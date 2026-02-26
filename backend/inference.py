import os
import tensorflow as tf
import numpy as np
from model import AttentionSum

MODEL_PATH = os.path.join(os.path.dirname(__file__), "stress_model_best.keras")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run `train.py` to create it.")

tf.keras.config.enable_unsafe_deserialization()
model = tf.keras.models.load_model(MODEL_PATH)

def predict_stress(eeg_csv):
    eeg = np.array(eeg_csv, dtype=np.float32)

    # Ensure shape (channels, time)
    if eeg.shape[0] > eeg.shape[1]:
        eeg = eeg.T

    # Apply SAME normalization as training: per-sample z-score
    mean = np.mean(eeg)
    std = np.std(eeg)
    if std > 0:
        eeg = (eeg - mean) / std

    # Reshape for model input (1, time, channels)
    eeg = eeg.T.reshape(1, eeg.shape[1], eeg.shape[0])

    # Model prediction
    model_score = float(model.predict(eeg, verbose=0)[0][0])
    return model_score
