import pandas as pd
import os

# CONFIGURATION
# Define where the file is with respect to this cript
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/adult.data")

# Define the names of the columns
COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education-num", 
    "marital-status", "occupation", "relationship", "race", "sex", 
    "capital-gain", "capital-loss", "hours-per-week", "native-country", "income"
]

# Define the quasi-identifiers (QI)
QUASI_IDENTIFIERS = ["age", "sex", "race", "native-country", "marital-status"]

def load_data():
    """CLoad the dataset managing spaces and column names."""
    if not os.path.exists(DATA_PATH):
        print(f"❌ ERROR: File not found in {DATA_PATH}")
        print("   Did you execute 'setup_data.py' in order to download it?")
        return None
    
    df = pd.read_csv(DATA_PATH, names=COLUMNS, skipinitialspace=True)
    return df

def analyze_k_anonymity(df, qi_list):
    """
    Group the identical rows based on the QIs and find the smallest group.
    """
    print(f"\n[*] QI analysis in progress: {qi_list}")
    
    # 1. Group and count
    # Create a column 'count' that tells how many people are in each gruop
    groups = df.groupby(qi_list).size().reset_index(name='group_size')
    
    # 2. Find the value of k (minimum size found)
    k_val = groups['group_size'].min()
    
    # 3. Extra stats
    total_records = len(df)
    
    # Count how many rows violate an arbitrary k value
    rows_at_risk_1 = groups[groups['group_size'] == 1]['group_size'].count()
    
    return k_val, groups, rows_at_risk_1

if __name__ == "__main__":
    print("--- RISK ANALYZER ENGINE ---")
    
    # 1. Loading
    df = load_data()
    
    if df is not None:
        # 2. Analysis
        k, grouped_df, risk_count = analyze_k_anonymity(df, QUASI_IDENTIFIERS)
        
        # 3. Report
        print(f"\n✅ ANALYSIS COMPLETED")
        print(f"------------------------------------------------")
        print(f"👉 Current k-anonymity: {k}")
        print(f"------------------------------------------------")
        
        if k == 1:
            print("⚠️  CRITICAL RISK: Unique records exist in the dataset.")
            print(f"   There are {risk_count} unique combinations that identify single peoples.")
            print("   These peoples are re-identifiable with 100% probability!")
        
        # 4. Show a "victim" example
        print("\n🔍 Examlple of a vulnerable record:")
        unique_people = grouped_df[grouped_df['group_size'] == k].head(1)
        print(unique_people.to_string(index=False))