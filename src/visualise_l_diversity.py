import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from risk_analyser import QUASI_IDENTIFIERS, COLUMNS

# --- CONFIGURATION ---
PATH_INTERMEDIATE = os.path.join(current_dir, "../data/adult_anonymized_intermediate.csv")
PATH_FINAL = os.path.join(current_dir, "../data/adult_anonymized.csv")
OUTPUT_PATH = os.path.join(current_dir, "../data/l_diversity_chart.png")
SENSITIVE = "income"

def get_distribution(path, stage_label):
    if not os.path.exists(path):
        return pd.DataFrame()
    
    df = pd.read_csv(path, names=COLUMNS, skipinitialspace=True)
    groups = df.groupby(QUASI_IDENTIFIERS)
    l_vals = [g[SENSITIVE].nunique() for _, g in groups]
    
    counts = pd.Series(l_vals).value_counts().sort_index()
    return pd.DataFrame({'l_value': counts.index, 'count': counts.values, 'Stage': stage_label})

if __name__ == "__main__":
    print("--- VISUALIZING L-DIVERSITY DISTRIBUTION ---")
    
    # 1. Load Data
    df_before = get_distribution(PATH_INTERMEDIATE, "Before (Risk)")
    df_after = get_distribution(PATH_FINAL, "After (Safe)")
    
    if df_before.empty or df_after.empty:
        sys.exit("Error: Missing data. Run anonymizer.py first.")

    combined = pd.concat([df_before, df_after])
    combined['l_value'] = combined['l_value'].astype(int)

    # 2. Setup Plot
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Calculate limits
    num_categories = combined['l_value'].nunique()
    max_idx = num_categories - 1
    y_limit = combined['count'].max() * 1.3
    ax.set_ylim(0, y_limit)

    # 3. Background Zones
    # Danger Zone (l=1 covers index 0, so -0.5 to 0.5)
    ax.axvspan(-0.5, 0.5, color='#e74c3c', alpha=0.1, zorder=0) 
    
    # Safe Zone (l>=2 covers index 1 onwards)
    safe_start = 0.5
    safe_end = max_idx + 0.5
    ax.axvspan(safe_start, safe_end, color='#27ae60', alpha=0.1, zorder=0)
    
    # Threshold Line
    ax.axvline(x=0.5, color='gray', linestyle='--', linewidth=2, alpha=0.7, zorder=1)

    # 4. Main Bar Plot
    palette = {"Before (Risk)": "#c0392b", "After (Safe)": "#2980b9"}
    sns.barplot(data=combined, x='l_value', y='count', hue='Stage', palette=palette, 
                alpha=1, zorder=3, edgecolor='white', width=0.6)

    # 5. Zone Labels
    ax.text(0, y_limit * 0.94, "DANGER ZONE\n(Attribute Disclosure)", 
            ha='center', va='top', fontsize=11, fontweight='bold', color='#c0392b',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))

    safe_center = (safe_start + safe_end) / 2
    ax.text(safe_center, y_limit * 0.94, "SAFE ZONE\n(Privacy Preserved)", 
            ha='center', va='top', fontsize=11, fontweight='bold', color='#27ae60',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))

    # 6. Bar Annotations
    for p in ax.patches:
        height = p.get_height()
        x = p.get_x()
        w = p.get_width()
        center_x = x + w / 2.
        
        # Check if we are in the Danger Zone (l=1)
        is_danger_zone = (-0.5 < center_x < 0.5)
        
        # Standard Label: Only show number if > 1 to avoid noise
        if height > 1:
            ax.text(center_x, height + (y_limit * 0.01), f'{int(height)}', 
                    ha="center", va="bottom", fontsize=11, fontweight='bold', color="#333333", zorder=5)
        
    # 7. Final Formatting
    current_labels = [int(float(l.get_text())) for l in ax.get_xticklabels()]
    new_labels = []
    for val in current_labels:
        if val == 1: new_labels.append("l=1\n(Critical Risk)")
        elif val == 2: new_labels.append(f"l={val}\n(Min Safe)")
        else: new_labels.append(f"l={val}")
    
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(new_labels, fontsize=11, fontweight='bold')
    
    ax.set_title("L-Diversity Analysis: Risk Elimination", fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("Number of Groups", fontsize=12, fontweight='bold')

    plt.legend(title="Dataset Version", loc='upper left', bbox_to_anchor=(0.02, 0.85), 
               fontsize=10, title_fontsize=11, framealpha=0.9, edgecolor='#ccc')

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=300)
    print(f"Chart saved to: {OUTPUT_PATH}")