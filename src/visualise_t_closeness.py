import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# --- SETUP PATHS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from risk_analyser import QUASI_IDENTIFIERS, COLUMNS
except ImportError:
    sys.exit("❌ Error: risk_analyser.py not found.")

# --- CONFIGURATION ---
INPUT_PATH = os.path.join(current_dir, "../data/adult_anonymized.csv")
OUTPUT_CHART_PATH = os.path.join(current_dir, "../data/t_closeness_analysis.png")
SENSITIVE_ATTR = "income"
THRESHOLDS_TO_TEST = [0.15, 0.20, 0.25, 0.30]

def calculate_t_values(df, sensitive_col):
    global_dist = df[sensitive_col].value_counts(normalize=True).sort_index()
    groups = df.groupby(QUASI_IDENTIFIERS)
    
    t_list = []
    group_sizes = []
    worst_t = -1

    for name, group in groups:
        local_dist = group[sensitive_col].value_counts(normalize=True)
        local_dist = local_dist.reindex(global_dist.index, fill_value=0.0)
        
        # Variational Distance Formula
        t = 0.5 * np.sum(np.abs(local_dist - global_dist))
        
        t_list.append(t)
        group_sizes.append(len(group))
        if t > worst_t: worst_t = t

    return t_list, group_sizes, global_dist, worst_t

if __name__ == "__main__":
    print("\n🚀 --- T-CLOSENESS VISUALIZER & AUDITOR ---")

    # 1. LOAD DATA
    if not os.path.exists(INPUT_PATH):
        sys.exit(f"❌ Error: {INPUT_PATH} not found.")
    
    df = pd.read_csv(INPUT_PATH, names=COLUMNS, skipinitialspace=True)
    total_rows = len(df)
    
    # 2. CALCULATE METRICS
    print("⚙️  Calculating t-closeness for all groups...")
    t_values, sizes, glob_d, max_t = calculate_t_values(df, SENSITIVE_ATTR)
    avg_t = np.mean(t_values)
    
    print(f"\n📊 CURRENT STATUS:")
    print(f"   Max t-value: {max_t:.4f} (Worst Case)")
    print(f"   Avg t-value: {avg_t:.4f}")

    # 3. VISUALIZATION
    print(f"🎨 Generating distribution chart...")
    
    sns.set_theme(style="white") 
    fig, ax = plt.subplots(figsize=(12, 7))
    
    plot_df = pd.DataFrame({'t-value': t_values})

    # Main Histogram
    sns.histplot(
        data=plot_df, 
        x='t-value', 
        bins=30, 
        kde=True, 
        color='#3498db',       
        edgecolor=None,        
        alpha=0.85,            
        line_kws={'linewidth': 2},
        zorder=3
    )

    # Max Risk Line
    plt.axvline(max_t, color='#c0392b', linestyle='--', linewidth=2.5, zorder=4,
                label=f'Worst Group Risk (t={max_t:.3f})')
    
    # Risk Zones
    plt.axvspan(0, 0.2, color='#27ae60', alpha=0.3, zorder=1, label='Safe Zone (t < 0.2)')
    plt.axvspan(0.2, 0.3, color='#f1c40f', alpha=0.3, zorder=1, label='Moderate Risk (0.2-0.3)')
    plt.axvspan(0.3, 1.0, color='#e74c3c', alpha=0.1, zorder=0, label='High Risk (t > 0.3)')

    # Labels
    plt.title(f'T-Closeness Audit: Risk Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('t-value (Divergence Level)', fontsize=12, fontweight='bold')
    plt.ylabel('Frequency (Number of Groups)', fontsize=12, fontweight='bold')
    plt.xlim(0, max(0.4, max_t + 0.1))
    
    # FULL BLACK BORDER (BOX STYLE)
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_color('black')
        ax.spines[spine].set_linewidth(1.2)

    plt.legend(loc='upper right', frameon=True, framealpha=0.9, shadow=True, edgecolor='black')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_CHART_PATH, dpi=300)
    print(f"✅ Chart saved to: {OUTPUT_CHART_PATH}")

    # 4. FEASIBILITY CHECK
    print("\n⚖️  FEASIBILITY CHECK (Can we tighten privacy?)")
    print(f"{'Target t':<10} | {'Violating Groups':<18} | {'Rows to Drop':<12} | {'Data Loss %':<12} | {'Verdict'}")
    print("-" * 75)

    df_check = pd.DataFrame({'t': t_values, 'size': sizes})
    recommendation = "Maintain current state."

    for threshold in THRESHOLDS_TO_TEST:
        violators = df_check[df_check['t'] > threshold]
        rows_lost = violators['size'].sum()
        loss_pct = (rows_lost / total_rows) * 100
        
        if loss_pct == 0: verdict = "✅ Already Met"
        elif loss_pct < 5: 
            verdict = "🟢 Easy"
            recommendation = f"Tighten to t <= {threshold}"
        elif loss_pct < 15: verdict = "🟡 Feasible"
        else: verdict = "❌ Too Costly"

        print(f"t <= {threshold:<5} | {len(violators):<18} | {rows_lost:<12} | {loss_pct:6.2f}%      | {verdict}")

    print("-" * 75)
    print(f"💡 FINAL RECOMMENDATION: {recommendation}")