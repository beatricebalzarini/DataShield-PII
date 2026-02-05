import pandas as pd
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from risk_analyser import load_data, analyze_k_anonymity, QUASI_IDENTIFIERS
except ImportError:
    sys.exit("❌ Error: risk_analyser.py not found")

# CONFIGURATION
SENSITIVE_ATTRIBUTE = "income"
# Intermediate file (Generalized but NOT suppressed - risky l-diversity)
INTERMEDIATE_PATH = os.path.join(current_dir, "../data/adult_anonymized_intermediate.csv")
# Final file (Generalized AND Suppressed - safe)
FINAL_PATH = os.path.join(current_dir, "../data/adult_anonymized.csv")

# --- GENERALIZATION LOGIC ---
def generalize_age_group(age):
    age = int(age)
    if age < 30: return "<30"
    elif age < 50: return "30-49"
    elif age < 70: return "50-69"
    else: return "70+"

def anonymize_dataset(df):
    df_anon = df.copy()
    print("   🔹 Generalizing Age...")
    df_anon['age'] = df_anon['age'].apply(generalize_age_group)
    print("   🔹 Generalizing Native Country...")
    df_anon['native-country'] = df_anon['native-country'].apply(lambda x: "US" if str(x).strip() == "United-States" else "Non-US")
    print("   🔹 Generalizing Marital Status...")
    df_anon['marital-status'] = df_anon['marital-status'].apply(lambda x: "Married" if str(x).strip().startswith("Married") else "Single")
    print("   🔹 Generalizing Race...")
    df_anon['race'] = df_anon['race'].apply(lambda x: "White" if str(x).strip() == "White" else "Other")
    print("   🔹 Masking Sex...")
    df_anon['sex'] = "Person"
    return df_anon

def enforce_l_diversity(df, qi_list, sensitive_col, min_l=2):
    print(f"\n[*] Enforcing l-diversity (Suppressing groups with l < {min_l})...")
    initial_count = len(df)
    
    # Calculate l-score for each group
    df['l_score'] = df.groupby(qi_list)[sensitive_col].transform('nunique')
    
    # Keep only those with l >= min_l
    df_safe = df[df['l_score'] >= min_l].copy()
    df_safe = df_safe.drop(columns=['l_score'])
    
    dropped = initial_count - len(df_safe)
    print(f"   ✂️  SUPPRESSION: Dropped {dropped} rows ({dropped/initial_count:.1%}).")
    return df_safe

if __name__ == "__main__":
    print("\n🎭 --- ANONYMIZER ENGINE ---")
    df = load_data()
    if df is not None:
        df = df.astype(str)

        # 1. GENERALIZATION
        print("[*] Applying Generalization Hierarchies:")
        df_gen = anonymize_dataset(df)
        
        # 2. SAVE INTERMEDIATE
        df_gen.to_csv(INTERMEDIATE_PATH, index=False, header=False)
        print(f"💾 Saved intermediate file (Pre-Suppression): {INTERMEDIATE_PATH}")

        # 3. SUPPRESSION
        df_final = enforce_l_diversity(df_gen, QUASI_IDENTIFIERS, SENSITIVE_ATTRIBUTE, min_l=2)
        
        # 4. FINAL CHECK & SAVE
        k_final, _, _ = analyze_k_anonymity(df_final, QUASI_IDENTIFIERS)
        print(f"✅ FINAL k-anonymity: {k_final}")
        
        df_final.to_csv(FINAL_PATH, index=False, header=False)
        print(f"💾 Saved final anonymized file: {FINAL_PATH}")