import urllib.request
import os

DATA_DIR = "data"
BASE_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/"
FILES = ["adult.data", "adult.names"]

def download_file(filename):
    url = BASE_URL + filename
    save_path = os.path.join(DATA_DIR, filename)
    
    print(f"[*] Starting download of: {filename}...")
    try:
        urllib.request.urlretrieve(url, save_path)
        print(f"[OK] Saved in: {save_path}")
    except Exception as e:
        print(f"[!] Error during the download of {filename}: {e}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        print(f"[!] Creating folder {DATA_DIR}...")
        os.makedirs(DATA_DIR)
        
    print("--- AUTOMATED DATASET DOWNLOADER ---")
    for f in FILES:
        download_file(f)
    print("\n[v] Setup completed! the files are in the 'data' folder.")