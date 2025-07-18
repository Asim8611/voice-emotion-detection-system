from flask import Flask, request, jsonify
import pickle
import librosa
import numpy as np
import os
from pymongo import MongoClient
from pydub import AudioSegment  # Added for conversion
from config import MONGO_URI
from flask_cors import CORS

# Explicitly set ffmpeg path
AudioSegment.ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"  # Adjust the path if needed

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["emotion_db"]
emotion_collection = db["emotions"]

# Load pre-trained ML model
MODEL_PATH = "model/emotion_model.pkl"
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

def convert_to_wav(file_path):
    """ Convert any audio file to WAV format """
    audio = AudioSegment.from_file(file_path)  # Pass the actual audio file path here
    wav_path = os.path.splitext(file_path)[0] + ".wav"
    audio.export(wav_path, format="wav")
    return wav_path

def extract_features(file_path):
    y, sr = librosa.load(file_path, duration=2.5, offset=0.6)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return np.mean(mfccs.T, axis=0)

@app.route("/predict", methods=["POST"])
def predict():
    audio_file = request.files["audio"]
    file_path = os.path.join("data/audio_samples", "temp" + os.path.splitext(audio_file.filename)[1])
    audio_file.save(file_path)

    # Convert to WAV if needed
    if not file_path.endswith(".wav"):
        file_path = convert_to_wav(file_path)

    # Extract features and predict emotion
    features = extract_features(file_path).reshape(1, -1)
    prediction = model.predict(features)[0]

    # Save result to database
    emotion_collection.insert_one({"emotion": prediction})

    os.remove(file_path)  # Cleanup
    print(prediction)
    return jsonify({"emotion": prediction})

@app.route("/emotions", methods=["GET"])
def get_emotions():
    emotions = list(emotion_collection.find({}, {"_id": 0}))
    return jsonify(emotions)

if __name__ == "__main__":
    app.run(debug=True)
