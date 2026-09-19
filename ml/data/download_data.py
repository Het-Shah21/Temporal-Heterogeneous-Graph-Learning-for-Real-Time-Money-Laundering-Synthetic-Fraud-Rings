import os
import subprocess

def download_ibm_aml():
    raw_dir = os.path.join(os.path.dirname(__file__), 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    print("Downloading IBM AML dataset via Kaggle API...")
    print("Ensure you have Kaggle API configured (~/.kaggle/kaggle.json).")
    try:
        subprocess.run([
            'kaggle', 'datasets', 'download', '-d', 
            'ealtman2019/ibm-transactions-for-anti-money-laundering-aml',
            '-p', raw_dir, '--unzip'
        ], check=True)
        print(f"Dataset downloaded successfully to {raw_dir}")
    except Exception as e:
        print(f"Failed to download using API. Error: {e}")
        print("Please download manually from: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml")

if __name__ == "__main__":
    download_ibm_aml()
