# import os
# import numpy as np
# import pandas as pd
# from sklearn.preprocessing import StandardScaler

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR = os.path.join(BASE_DIR, "data", "SM40")


# def detect_task(folder_name):
#     name = folder_name.lower()
#     if "relax" in name:
#         return 0
#     if "stroop" in name:
#         return 1
#     if "arithmetic" in name:
#         return 1
#     if "mirror" in name:
#         return 1
#     return None


# def load_sm40_dataset():
#     X, y = [], []

#     if not os.path.exists(DATA_DIR):
#         raise FileNotFoundError(f"Dataset folder not found: {DATA_DIR}")

#     for task_folder in os.listdir(DATA_DIR):
#         task_folder_path = os.path.join(DATA_DIR, task_folder)

#         if not os.path.isdir(task_folder_path):
#             continue

#         label = detect_task(task_folder)
#         if label is None:
#             continue

#         print(f"✔ Task folder: {task_folder} → label {label}")

#         # 🔴 INNER FOLDER (THIS WAS THE MISSING PART)
#         for inner in os.listdir(task_folder_path):
#             inner_path = os.path.join(task_folder_path, inner)

#             if not os.path.isdir(inner_path):
#                 continue

#             print(f"   ↳ Reading inner folder: {inner}")

#             for file in os.listdir(inner_path):
#                 if not file.lower().endswith(".csv"):
#                     continue

#                 file_path = os.path.join(inner_path, file)

#                 try:
#                     # Read CSV (comma or semicolon)
#                     try:
#                         df = pd.read_csv(file_path)
#                     except:
#                         df = pd.read_csv(file_path, sep=";")

#                     # Keep only numeric EEG columns
#                     df = df.select_dtypes(include=[np.number])

#                     if df.empty:
#                         print(f"⚠ Empty EEG after cleaning: {file}")
#                         continue

#                     eeg = df.values

#                     # Ensure (channels, time)
#                     if eeg.shape[0] > eeg.shape[1]:
#                         eeg = eeg.T

#                     X.append(eeg)
#                     y.append(label)

#                 except Exception as e:
#                     print(f"⚠ Failed to read {file}: {e}")

#     if len(X) == 0:
#         raise RuntimeError("❌ No EEG CSV files loaded. Dataset structure mismatch.")

#     X = np.array(X, dtype=np.float32)
#     y = np.array(y, dtype=np.int32)

#     # Normalize per sample
#     scaler = StandardScaler()
#     X = scaler.fit_transform(
#         X.reshape(X.shape[0], -1)
#     ).reshape(X.shape)

#     print(f"\n✅ Loaded {len(X)} EEG samples")
#     print(f"✅ EEG tensor shape: {X.shape} (samples, channels, time)")

#     return X, y
import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "SM40")


def detect_task(folder_name):
    name = folder_name.lower()
    if "relax" in name:
        return 0
    if "stroop" in name:
        return 1
    if "arithmetic" in name:
        return 1
    if "mirror" in name:
        return 1
    return None


def load_sm40_dataset():
    X, y = [], []

    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Dataset folder not found: {DATA_DIR}")

    for task_folder in os.listdir(DATA_DIR):
        task_folder_path = os.path.join(DATA_DIR, task_folder)

        if not os.path.isdir(task_folder_path):
            continue

        label = detect_task(task_folder)
        if label is None:
            continue

        print(f"✔ Task folder: {task_folder} → label {label}")

        for inner in os.listdir(task_folder_path):
            inner_path = os.path.join(task_folder_path, inner)

            if not os.path.isdir(inner_path):
                continue

            print(f"   ↳ Reading inner folder: {inner}")

            for file in os.listdir(inner_path):
                if not file.lower().endswith(".csv"):
                    continue

                file_path = os.path.join(inner_path, file)

                try:
                    try:
                        df = pd.read_csv(file_path)
                    except:
                        df = pd.read_csv(file_path, sep=";")

                    # Keep only EEG channels (32)
                    df = df.select_dtypes(include=[np.number]).iloc[:, :32]

                    if df.empty:
                        print(f"⚠ Empty EEG after cleaning: {file}")
                        continue

                    eeg = df.values

                    # Ensure (channels, time)
                    if eeg.shape[0] > eeg.shape[1]:
                        eeg = eeg.T

                    # Per-sample normalization
                    mean = np.mean(eeg)
                    std = np.std(eeg)
                    if std > 0:
                        eeg = (eeg - mean) / std

                    X.append(eeg)
                    y.append(label)

                except Exception as e:
                    print(f"⚠ Failed to read {file}: {e}")

    if len(X) == 0:
        raise RuntimeError("❌ No EEG CSV files loaded. Dataset structure mismatch.")

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    print(f"\n✅ Loaded {len(X)} EEG samples")
    print(f"✅ Shape: {X.shape}")

    return X, y
