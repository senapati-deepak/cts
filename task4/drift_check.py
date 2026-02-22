import sys

import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


# --- Model Drift Detection (K-S Test) ---
def detect_model_drift(csv_path='../data/model_history.csv'):
    
    df = pd.read_csv(csv_path)
    
    prod_lengths = df['prod_response_len']
    staging_lengths = df['staging_response_len']
    
    ks_stat, p_value = stats.ks_2samp(prod_lengths, staging_lengths)
    
    print("--- MLOps Drift Detection Report ---")
    print(f"K-S Statistic: {ks_stat:.4f}")
    print(f"P-Value:       {p_value:.4e}\n")
    
    if p_value < 0.05:
        print("Status: 🔴 [ALERT] Statistically significant drift detected (p < 0.05).")
        print("Action: Staging model behaves differently than Production.")
        sys.exit(1)
    else:
        print("Status: 🟢 [OK] No significant drift detected.")
        print("Action: Staging model behavior is consistent with Production.")
        
    plt.figure(figsize=(8, 4))
    sns.kdeplot(prod_lengths, label='Production', fill=True, color='blue')
    sns.kdeplot(staging_lengths, label='Staging', fill=True, color='orange')
    plt.title('Response Length Distribution: Prod vs Staging')
    plt.xlabel('Response Length (Characters/Tokens)')
    plt.ylabel('Density')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    detect_model_drift()