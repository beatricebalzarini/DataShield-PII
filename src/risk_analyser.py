import pandas as pd
import os
import sys

# CONFIGURATION
# Relative path to the raw file
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/adult.data")

COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education-num", 
    "marital-status", "occupation", "relationship", "race", "sex", 
    "capital-gain", "capital-loss", "hours-per-week", "native-country", "income"
]

# Quasi-Identifiers
QUASI_IDENTIFIERS = ["age", "sex", "race", "native-country", "marital-status"]

def load_data():
    """Loads the raw dataset handling spaces."""
    if not os.path.exists(DATA_PATH):
        print(f"❌ ERROR: File not found in {DATA_PATH}")
        return None
    
    # Reads the original raw file
    df = pd.read_csv(DATA_PATH, names=COLUMNS, skipinitialspace=True)
    return df

def analyze_k_anonymity(df, qi_list):
    """Calculates k-anonymity and counts rows at risk."""
    groups = df.groupby(qi_list).size().reset_index(name='group_size')
    k_val = groups['group_size'].min()
    rows_at_risk_1 = groups[groups['group_size'] == 1]['group_size'].count()
    return k_val, groups, rows_at_risk_1

if __name__ == "__main__":
    print("\n🕵️  --- RISK ANALYZER ENGINE ---")
    df = load_data()
    if df is not None:
        print(f"[*] Loaded dataset with {len(df)} rows.")
        k, grouped_df, risk_count = analyze_k_anonymity(df, QUASI_IDENTIFIERS)
        
        print(f"\n📊 RISK REPORT:")
        print(f"   Current k-anonymity: {k}")
        
        if k == 1:
            print(f"⚠️  CRITICAL RISK: {risk_count} unique records found.")
            print("   These individuals are re-identifiable with 100% probability.")
        else:
            print(f"✅ DATA IS SAFE (k={k})")