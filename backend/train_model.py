import os
import librosa
import numpy as np
import pickle
import pandas as pd
from imblearn.over_sampling import SMOTE  # Handle class imbalance
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Paths
CSV_PATH = os.path.join("data/", "labeled_ravdess.csv")  # CSV with file paths and emotion labels
MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "emotion_model.pkl")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Load CSV file
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Error: CSV file not found at {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Ensure CSV contains required columns
if 'filepath' not in df.columns or 'emotion' not in df.columns:
    raise ValueError("CSV file must contain 'filepath' and 'emotion' columns!")

print("CSV Data Preview:")
print(df.head())

# Check if all files exist
valid_files = []
for _, row in df.iterrows():
    if os.path.exists(row['filepath']):
        valid_files.append(row)
    else:
        print(f"Missing file: {row['filepath']}")

df = pd.DataFrame(valid_files)  # Use only valid files

print(f"Total valid audio files: {len(df)}")

if df.empty:
    raise ValueError("Error: No valid audio data available for training!")

# Function to extract MFCC features
def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, duration=2.5, offset=0.6)

        # Ensure n_fft is not larger than the signal length
        n_fft = min(1024, len(y))

        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40, n_fft=n_fft)
        return np.mean(mfccs.T, axis=0)
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Load features and labels
features = []
labels = []

for index, row in df.iterrows():
    file_path = row['filepath']
    emotion_label = row['emotion']
    feature_vector = extract_features(file_path)

    if feature_vector is not None:
        features.append(feature_vector)
        labels.append(emotion_label)

# Convert lists to NumPy arrays
X = np.array(features)
y = np.array(labels)

# Check if we have valid data
if X.shape[0] == 0:
    raise ValueError("Error: No valid features extracted!")

# Apply SMOTE to handle class imbalance
smote = SMOTE(random_state=42)
X, y = smote.fit_resample(X, y)

# Split dataset into training (80%) and testing (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a more optimized RandomForest model
model = RandomForestClassifier(n_estimators=300, max_depth=50, min_samples_split=5, random_state=42)
model.fit(X_train, y_train)

# Evaluate model accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"🔥 Model Accuracy: {accuracy * 100:.2f}% 🔥")

# Save the trained model
with open(MODEL_PATH, "wb") as file:
    pickle.dump(model, file)

print(f"✅ Model saved to {MODEL_PATH}")