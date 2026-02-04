import pandas as pd
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import functions
try:
    from risk_analyser import load_data, analyze_k_anonymity, QUASI_IDENTIFIERS
except ImportError:
    print("❌ Error: risk_analyzer.py not found")
    sys.exit(1)

# Anonymisation logic
# 1. Age -> Binning
# 2. Country -> US vs Non-US
# 3. Marital Status -> Married vs Single
# 4. Race -> White vs Other
# 5. Sex -> Person

def generalize_age_group(age):
    age = int(age)
    
    if age < 30:
        return "<30"
    elif age < 50:
        return "30-49"
    elif age < 70:
        return "50-69"
    else:
        return "70+"

def anonymize_dataset(df):
    """
    Apply the generalisation transformations to the dataset.
    """
    # Create a copy
    df_anon = df.copy()

    print("\n[*] Applying AGE generalization (e.g. 27 -> <30)...")
    df_anon['age'] = df_anon['age'].apply(generalize_age_group)
    
    print("[*] Applying NATIVE-COUNTRY generalization (US vs Non-US)...")
    df_anon['native-country'] = df_anon['native-country'].apply(
        lambda x: "US" if str(x).strip() == "United-States" else "Non-US"
    )
    print("[*] Applying MARITAL-STATUS generalization (Married vs Single)...")
    df_anon['marital-status'] = df_anon['marital-status'].apply(
        lambda x: "Married" if str(x).strip().startswith("Married") else "Single"
    )
    
    print("[*] Applying RACE generalization (White vs Other)...")
    df_anon['race'] = df_anon['race'].apply(
        lambda x: "White" if str(x).strip() == "White" else "Other"
    )
    
    print("[*] Applying SEX generalisation (neutralise field)...")
    df_anon['sex'] = "Person"

    return df_anon

# Main
if __name__ == "__main__":
    print("--- ANONYMIZER ENGINE ---")

    # 1. Load data
    df = load_data()
    
    if df is not None:
        # 2. Apply anonymisation
        df_safe = anonymize_dataset(df)
        
        # 3. Verify if k value has increased
        print("\n--- VERIFY RESULTS ---")
        k_new, _, risk_count = analyze_k_anonymity(df_safe, QUASI_IDENTIFIERS)
        
        print(f"\n✅ NEW k VALUE: {k_new}")
        
        if k_new > 1:
            print(f"🎉 Good job! You got rid of the unique records.")
        else:
            print(f"⚠️ Attention: k is still 1. There are still {risk_count} unique profiles.")
        
        # df_safe.to_csv("../data/adult_anonymized.csv", index=False)