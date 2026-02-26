import numpy as np
import pandas as pd
import requests
import json

# Test with a RELAXED sample
print("=" * 60)
print("TEST 1: RELAXED EEG Sample")
print("=" * 60)

relax_csv = r"C:\Users\Abdul\OneDrive\Desktop\college\resume\SOFTCOPY\brain2vec\brain2vec\data\SM40\Relax-20231211T181913Z-001\Relax\Relax_sub_1.csv"
df_relax = pd.read_csv(relax_csv)
df_relax = df_relax.select_dtypes(include=[np.number]).iloc[:, :32]

if df_relax.shape[1] < 32:
    missing = 32 - df_relax.shape[1]
    pad = pd.DataFrame(np.zeros((df_relax.shape[0], missing)), index=df_relax.index)
    df_relax = pd.concat([df_relax, pad], axis=1)

eeg_relax = df_relax.values.tolist()

response_relax = requests.post(
    "http://localhost:5000/predict",
    json={"eeg": eeg_relax},
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response_relax.status_code}")
print(f"Response:\n{json.dumps(response_relax.json(), indent=2)}")

# Test with a STRESS sample (Stroop)
print("\n" + "=" * 60)
print("TEST 2: STRESS EEG Sample (Stroop Test)")
print("=" * 60)

stress_csv = r"C:\Users\Abdul\OneDrive\Desktop\college\resume\SOFTCOPY\brain2vec\brain2vec\data\SM40\Stroop-20231211T181911Z-001\Stroop\Stroop_sub_1.csv"
df_stress = pd.read_csv(stress_csv)
df_stress = df_stress.select_dtypes(include=[np.number]).iloc[:, :32]

if df_stress.shape[1] < 32:
    missing = 32 - df_stress.shape[1]
    pad = pd.DataFrame(np.zeros((df_stress.shape[0], missing)), index=df_stress.index)
    df_stress = pd.concat([df_stress, pad], axis=1)

eeg_stress = df_stress.values.tolist()

response_stress = requests.post(
    "http://localhost:5000/predict",
    json={"eeg": eeg_stress},
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response_stress.status_code}")
print(f"Response:\n{json.dumps(response_stress.json(), indent=2)}")
