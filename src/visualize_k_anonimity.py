import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from risk_analyser import load_data, analyze_k_anonymity, QUASI_IDENTIFIERS

# --- TRANSFORMATION LOGIC ---
def age_strong(age):
    age = int(age)
    if age < 30: return "<30"
    elif age < 50: return "30-49"
    elif age < 70: return "50-69"
    else: return "70+"

def get_stats(df, qi_list):
    k, _, risk_count_1 = analyze_k_anonymity(df, qi_list)
    return risk_count_1, k

if __name__ == "__main__":
    print("--- VISUALIZING K-ANONYMITY PROCESS ---")
    df = load_data()
    if df is None: sys.exit(1)
    
    history = []
    df_current = df.astype(str)

    # --- PHASE 1: GENERALIZATION STEPS ---
    steps_config = [
        ("1. Raw", None, None), # Shortened labels for better fit
        ("2. Country", 'native-country', lambda x: "US" if x.strip() == "United-States" else "Non-US"),
        ("3. Marital", 'marital-status', lambda x: "Married" if x.strip().startswith("Married") else "Single"),
        ("4. Race", 'race', lambda x: "White" if x.strip() == "White" else "Other"),
        ("5. Age", 'age', age_strong),
        ("6. Sex", 'sex', lambda x: "Person")
    ]

    for label, col, func in steps_config:
        print(f"Running step: {label}...")
        if col and func:
            if col == 'age': 
                df_current[col] = df['age'].apply(func) 
            else:
                df_current[col] = df_current[col].apply(func)
        
        uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
        history.append({"Step": label, "Uniques": uniques, "k": k})

    # --- PHASE 2: SUPPRESSION ---
    print("7. Applying Suppression...")
    SENSITIVE = "income"
    df_current['l_score'] = df_current.groupby(QUASI_IDENTIFIERS)[SENSITIVE].transform('nunique')
    df_suppressed = df_current[df_current['l_score'] >= 2].copy()
    
    uniques, k = get_stats(df_suppressed, QUASI_IDENTIFIERS)
    history.append({"Step": "7. Suppression", "Uniques": uniques, "k": k})

    # --- PLOTTING ---
    steps = [x['Step'] for x in history]
    values_uniques = [x['Uniques'] for x in history]
    values_k = [x['k'] for x in history]

    sns.set_theme(style="white")
    fig, ax1 = plt.subplots(figsize=(14, 9)) # Increased height
    ax1.grid(axis='y', linestyle='--', alpha=0.5, color='gray', zorder=0)

    # --- AXIS 1: RISK (Red Bars) ---
    palette = sns.color_palette("Reds_r", n_colors=len(steps))
    bars = ax1.bar(steps, values_uniques, color=palette, alpha=0.8, zorder=2, width=0.5)
    
    ax1.set_ylabel('Unique Records (Risk)', fontsize=14, fontweight='bold', color='#c0392b')
    ax1.tick_params(axis='y', labelsize=12, colors='#c0392b')
    # Give plenty of headroom for the text
    ax1.set_ylim(0, max(values_uniques) * 1.2)

    # Label Bars (Placed slightly above the bar)
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height + (max(values_uniques)*0.02),
                    f'{int(height)}', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#444444')

    # --- AXIS 2: SAFETY (Blue Line) ---
    ax2 = ax1.twinx()
    ax2.plot(steps, values_k, color='#2980b9', marker='o', linestyle='-', linewidth=3, markersize=10, zorder=3)
    
    ax2.set_ylabel('K-Value (Safety)', fontsize=14, fontweight='bold', color='#2980b9')
    ax2.tick_params(axis='y', labelsize=12, colors='#2980b9')
    # Massive headroom for the K labels so they don't touch the bars
    ax2.set_ylim(0, max(values_k) * 1.5) 

    # Label Line points (Placed WAY above the point)
    for i, v in enumerate(values_k):
        # Offset calculation to push label up
        offset = max(values_k) * 0.08 
        ax2.text(i, v + offset, f'k={v}', 
                 ha='center', va='bottom', fontsize=12, fontweight='bold', color='#2980b9', 
                 bbox=dict(facecolor='white', edgecolor='#2980b9', boxstyle='round,pad=0.2', alpha=0.9))

    # Titles and Layout
    plt.title('Anonymization Process: Risk Reduction vs K-Anonymity Increase', fontsize=18, fontweight='bold', pad=20)
    
    # NO ROTATION for X labels
    ax1.set_xticklabels(steps, fontsize=11, fontweight='bold') 
    
    plt.tight_layout()
    
    out_path = os.path.join(current_dir, "../data/k_anonimity_chart.png")
    plt.savefig(out_path, dpi=300)
    print(f"✅ Chart saved to: {out_path}")