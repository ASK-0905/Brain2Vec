# user-friendly, robust paths relative to this file
import numpy as np
import pandas as pd
from pathlib import Path
from inference import predict_stress

# 🔴 CHANGE THIS PATH TO ANY CSV YOU WANT TO TEST (relative to the repo)
CSV_PATH = Path(__file__).resolve().parent / '..' / 'data' / 'SM40' / 'Relax-20231211T181913Z-001' / 'Relax' / 'Relax_sub_1.csv'

CSV_PATH = str(CSV_PATH)
# Example for stress:
# CSV_PATH = r"..\data\SM40\Stroop-20231211T181911Z-001\Stroop\Stroop_sub_1.csv"

print("Loading EEG from:", CSV_PATH)

df = pd.read_csv(CSV_PATH)

# Keep only numeric EEG values and match training channel count (32)
df = df.select_dtypes(include=[np.number]).iloc[:, :32]

# If the CSV has fewer than 32 channels, pad with zeros to match training shape
if df.shape[1] < 32:
    missing = 32 - df.shape[1]
    pad = pd.DataFrame(np.zeros((df.shape[0], missing)), index=df.index)
    df = pd.concat([df, pad], axis=1)

if df.empty:
    raise ValueError("CSV has no numeric EEG data")

eeg = df.values

# Ensure (channels, time)
if eeg.shape[0] > eeg.shape[1]:
    eeg = eeg.T

score = predict_stress(eeg)

print("\n🔍 RESULT")
print("Stress score:", score)
print("Prediction:", "STRESSED" if score > 0.5 else "RELAXED")
