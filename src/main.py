import subprocess
import sys
import os
import time

# Define the sequence of scripts to run
PIPELINE = [
    {
        "script": "risk_analyser.py",
        "title": "STEP 1: INITIAL RISK ASSESSMENT",
        "desc": "Analyzing the raw 'Adult' dataset to identify privacy violations (k=1)."
    },
    {
        "script": "anonymiser.py",
        "title": "STEP 2: ANONYMIZATION ENGINE",
        "desc": "Applying Generalization and Suppression to achieve k-anonymity and l-diversity."
    },
    {
        "script": "visualise_k_anonimity.py",
        "title": "STEP 3: VISUALIZING K-ANONYMITY",
        "desc": "Generating the chart showing the trade-off between Risk (unique rows) and Safety (k-value)."
    },
    {
        "script": "visualise_l_diversity.py",
        "title": "STEP 4: VISUALIZING L-DIVERSITY",
        "desc": "Comparing the distribution of sensitive attributes before and after anonymization."
    },
    {
        "script": "visualise_t_closeness.py",
        "title": "STEP 5: T-CLOSENESS AUDIT",
        "desc": "Calculating Variational Distance to ensure sensitive attributes follow global distribution."
    }
]

def run_script(script_name, description):
    """Executes a python script and handles output."""
    print(f"\n{'='*60}")
    print(f"📄 RUNNING: {script_name}")
    print(f"ℹ️  INFO:    {description}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Check if file exists
    if not os.path.exists(script_name):
        print(f"❌ ERROR: File '{script_name}' not found in current directory.")
        return False

    # Run the script
    try:
        # We use sys.executable to ensure we use the same python interpreter
        result = subprocess.run([sys.executable, script_name], check=True)
        
        elapsed = time.time() - start_time
        print(f"\n✅ SUCCESS: {script_name} completed in {elapsed:.2f}s.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FAILURE: {script_name} crashed with exit code {e.returncode}.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print("\n🔐 STARTING PRIVACY PRESERVATION PIPELINE 🔐")
    print("--------------------------------------------------")

    success_count = 0
    
    for step in PIPELINE:
        print(f"\n\n>>> {step['title']}")
        if run_script(step['script'], step['desc']):
            success_count += 1
        else:
            print("\n⛔ PIPELINE HALTED DUE TO ERROR.")
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY ({success_count}/{len(PIPELINE)} steps)")
    print(f"📊 Check the '../data/' folder for generated charts and CSVs.")
    print(f"{'='*60}\n")