from preprocess import load_sm40_dataset
from model import build_model
from sklearn.model_selection import train_test_split
import os
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import classification_report, confusion_matrix

MODEL_DIR = os.path.dirname(__file__)
BEST_MODEL_PATH = os.path.join(MODEL_DIR, "stress_model_best.keras")
FINAL_MODEL_PATH = os.path.join(MODEL_DIR, "stress_model.keras")

print("Loading dataset...")
X, y = load_sm40_dataset()

# (samples, channels, time) → (samples, time, channels)
X = X.transpose(0, 2, 1)

print(f"Dataset shape: {X.shape}")
print(f"Labels distribution: Relaxed={sum(y==0)}, Stressed={sum(y==1)}")

print("\nBuilding model...")
model = build_model((X.shape[1], X.shape[2]))

optimizer = Adam(learning_rate=0.001)
model.compile(
    optimizer=optimizer,
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

callbacks = [
    EarlyStopping(
        monitor="val_loss",
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=5,
        verbose=1
    ),
    ModelCheckpoint(
        BEST_MODEL_PATH,
        save_best_only=True,
        monitor="val_loss",
        verbose=1
    )
]

EPOCHS = 50

print(f"\n🚀 Training — epochs={EPOCHS}...")
history = model.fit(
    X_train,
    y_train,
    epochs=EPOCHS,
    batch_size=16,
    validation_split=0.2,
    callbacks=callbacks,
    verbose=2
)

print("\n📊 Evaluating on test set...")
test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")

y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()

print("\n📈 Classification Report:")
print(classification_report(y_test, y_pred, target_names=["Relaxed", "Stressed"]))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

model.save(FINAL_MODEL_PATH)
print(f"\n✅ Models saved:")
print(f"   {BEST_MODEL_PATH}")
print(f"   {FINAL_MODEL_PATH}")
