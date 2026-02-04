import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# --- SETUP PATH & IMPORTS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from risk_analyser import load_data, analyze_k_anonymity, QUASI_IDENTIFIERS
except ImportError:
    print("❌ Error: risk_analyser.py not found in the current directory.")
    sys.exit(1)

# --- TRANSFORMATION LOGIC ---

def age_weak(x):
    """Simulates weak generalization (e.g., 37 -> 3*)."""
    return str(x)[:1] + "*"

def age_strong(age):
    """Simulates strong binning (e.g., 27 -> <30)."""
    age = int(age)
    if age < 30: return "<30"
    elif age < 50: return "30-49"
    elif age < 70: return "50-69"
    else: return "70+"

def get_stats(df, qi_list):
    """Wrapper to extract k-value and risk count."""
    k, _, risk_count_1 = analyze_k_anonymity(df, qi_list)
    return risk_count_1, k

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("--- GENERATING ANONYMIZATION PROGRESS REPORT ---")
    
    df = load_data()
    if df is None: sys.exit(1)
    
    history = []

    # Step 1: Baseline
    print("1. Analyzing Baseline...")
    df_current = df.astype(str)
    uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
    history.append({"Step": "1. Raw Data", "Uniques": uniques, "k": k})

    # Step 2: Weak Age
    print("2. Applying Weak Age Generalization...")
    df_current = df_current.copy()
    df_current['age'] = df['age'].apply(age_weak) 
    uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
    history.append({"Step": "2. Age (Weak)", "Uniques": uniques, "k": k})

    # Step 3: Native Country
    print("3. Generalizing Country...")
    df_current = df_current.copy()
    df_current['native-country'] = df_current['native-country'].apply(
        lambda x: "US" if str(x).strip() == "United-States" else "Non-US"
    )
    uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
    history.append({"Step": "3. + Country", "Uniques": uniques, "k": k})

    # Step 4: Marital Status
    print("4. Generalizing Marital Status...")
    df_current = df_current.copy()
    df_current['marital-status'] = df_current['marital-status'].apply(
        lambda x: "Married" if str(x).strip().startswith("Married") else "Single"
    )
    uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
    history.append({"Step": "4. + Marital", "Uniques": uniques, "k": k})

    # Step 5: Race
    print("5. Generalizing Race...")
    df_current = df_current.copy()
    df_current['race'] = df_current['race'].apply(
        lambda x: "White" if str(x).strip() == "White" else "Other"
    )
    uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
    history.append({"Step": "5. + Race", "Uniques": uniques, "k": k})

    # Step 6: Strong Age (Binning)
    print("6. Applying Strong Age Binning...")
    df_current = df_current.copy()
    # Re-apply logic to original numeric age column
    df_current['age'] = df['age'].apply(age_strong)
    uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
    history.append({"Step": "6. Age (Bin)", "Uniques": uniques, "k": k})

    # Step 7: Sex (Final Masking)
    print("7. Masking Sex...")
    df_current = df_current.copy()
    df_current['sex'] = "Person"
    uniques, k = get_stats(df_current, QUASI_IDENTIFIERS)
    history.append({"Step": "7. + Sex", "Uniques": uniques, "k": k})

    # --- PLOTTING ---
    print("\nGenerating Chart...")
    
    steps = [x['Step'] for x in history]
    values_uniques = [x['Uniques'] for x in history]
    values_k = [x['k'] for x in history]

    # Style
    sns.set_theme(style="white")
    fig, ax1 = plt.subplots(figsize=(14, 9))
    ax1.grid(axis='y', linestyle='--', alpha=0.5, color='gray', zorder=0)

    # Left Axis: Risk (Bars)
    palette = sns.color_palette("Reds_r", n_colors=len(steps))
    bars = ax1.bar(steps, values_uniques, color=palette, alpha=0.9, zorder=2, width=0.6)
    
    # Increased fontsize for Axis Title (16) and Ticks (14)
    ax1.set_ylabel('Number of Unique Records (Risk)', fontsize=16, fontweight='bold', color='#c0392b', labelpad=15)
    ax1.tick_params(axis='y', labelsize=14, colors='#c0392b') 
    ax1.tick_params(axis='x', labelsize=14) 
    ax1.set_ylim(0, max(values_uniques) * 1.15)

    # Bar Labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + (max(values_uniques)*0.01),
                f'{int(height)}', ha='center', va='bottom', fontsize=14, fontweight='bold', color='#444444')

    # Right Axis: Safety (Line)
    ax2 = ax1.twinx()
    ax2.plot(steps, values_k, color='#2980b9', marker='o', linestyle='-', linewidth=4, markersize=12, zorder=3)
    
    # Increased fontsize for Axis Title (16) and Ticks (14)
    ax2.set_ylabel('k-Anonymity Score (Safety)', fontsize=16, fontweight='bold', color='#2980b9', labelpad=15)
    ax2.tick_params(axis='y', labelsize=14, colors='#2980b9')
    ax2.set_ylim(0, max(values_k) * 1.25)
    
    # Line Labels
    for i, v in enumerate(values_k):
        ax2.text(i, v + (max(values_k)*0.05), f'k={v}', 
                 ha='center', va='bottom', fontsize=14, fontweight='bold', color='#2980b9', 
                 bbox=dict(facecolor='white', edgecolor='#2980b9', boxstyle='round,pad=0.3', alpha=0.9))

    # Titles & Layout
    plt.suptitle('Privacy vs Utility: Anonymization Progress', fontsize=22, fontweight='bold', y=0.96)
    ax1.set_title('Reducing unique records (Red) while increasing k-anonymity (Blue)', fontsize=16, color='gray', pad=20)
    
    fig.autofmt_xdate(rotation=30, ha='right')
    
    # Adjusted rect to ensure titles fit with larger fonts
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    # Save Output
    output_path = os.path.join(current_dir, "../data/anonymization_pro_chart.png")
    plt.savefig(output_path, dpi=300)
    print(f"✅ Chart saved to: {output_path}")