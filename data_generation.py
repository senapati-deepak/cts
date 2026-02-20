import pandas as pd
import numpy as np
from scipy import stats


def generate_assignment_data():
    np.random.seed(42)
    num_users = 1000
    # --- TASK 1 & 2: Network Logs & Churn Labels ---
    tower_logs = pd.DataFrame({
        'user_id': [f"CUST_{i:03}" for i in range(num_users)],
        'signal_strength': np.random.uniform(-110, -60, num_users),
        'dropped_calls': np.random.poisson(0.8, num_users),
        'latency': np.random.uniform(20, 200, num_users),
        'avg_data_gb': np.random.uniform(10, 150, num_users),
        'label': np.random.choice([0, 1], num_users, p=[0.97, 0.03])
    })

    # --- TASK 2: Support Transcripts (Mock Text) ---
    complaint_keywords = ["dropped", "slow", "terrible",
                          "expensive", "cancel", "frustrated"]
    neutral_keywords = ["question", "billing", "update", "plan", "okay"]
    transcripts = []
    for i in range(num_users):
        user_id = f"CUST_{i:03}"
        is_complainer = tower_logs.iloc[i]['label'] == 1
        for _ in range(2):  # 2 transcripts per user
            words = np.random.choice(complaint_keywords if is_complainer else neutral_keywords, 3)
            txt = f"Customer says: The service is {words[0]} and {words[1]}. I want a {words[2]}."
            transcripts.append({
                "user_id": user_id,
                "text_transcript": txt
            })
    transcripts_df = pd.DataFrame(transcripts)

    # --- TASK 3: Fiber Routes & Sensors ---
    routes_df = pd.DataFrame({
        'route_id': [f'R_{i:02}' for i in range(20)],
        'start_hub': np.random.choice(['Hub_A', 'Hub_C', 'Hub_E'], 20),
        'end_hub': np.random.choice(['Hub_B', 'Hub_D', 'Hub_F'], 20),
        'physical_km': np.random.uniform(2, 50, 20)
    })
    sensors_df = pd.DataFrame({
        'route_id': [f'R_{i:02}' for i in range(20)],
        'congestion_score': np.random.randint(0, 100, 20),
        'last_updated': pd.Timestamp.now()
    })

    # --- TASK 4: Model Drift History ---
    # Champion (Production) vs Challenger (Staging)
    model_history = pd.DataFrame({
        'prod_response_len': np.random.normal(45, 10, 500),
        'staging_response_len': np.random.normal(52, 12, 500)
    })

    # Save files
    tower_logs.to_csv('tower_logs.csv', index=False)
    transcripts_df.to_csv('transcripts.csv', index=False)
    routes_df.to_csv('fiber_routes.csv', index=False)
    sensors_df.to_csv('traffic_sensors.csv', index=False)
    model_history.to_csv('model_history.csv', index=False)
    print("Assignment data generated successfully!")

if __name__ == "__main__":
    generate_assignment_data()
