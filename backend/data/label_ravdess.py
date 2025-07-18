import zipfile
import csv
import os
import re

# Define emotion mapping based on the filename pattern
emotion_map = {
    '01': 'Neutral',
    '02': 'Calm',
    '03': 'Happy',
    '04': 'Sad',
    '05': 'Angry',
    '06': 'Fearful',
    '07': 'Disgust',
    '08': 'Surprised'
}

# Paths
zip_path = "ravdess_dataset.zip"       # ZIP file location
extract_dir = "ravdess_extracted"      # Extraction folder
csv_file = "labeled_ravdess.csv"       # Output CSV file

# Extract ZIP
print("Extracting ZIP file...")
try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Files extracted to '{extract_dir}'.")
except FileNotFoundError:
    print(f"Error: ZIP file '{zip_path}' not found.")
    exit(1)
except zipfile.BadZipFile:
    print(f"Error: '{zip_path}' is not a valid ZIP file.")
    exit(1)

# Regular expression for file naming
pattern = re.compile(r"(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})\.wav", re.IGNORECASE)

# Collect labeled data
print("Labeling files based on actor folders...")
data = []

for actor_folder in os.listdir(extract_dir):
    actor_path = os.path.join(extract_dir, actor_folder)

    if os.path.isdir(actor_path):  # Ensure it's a folder
        for file in os.listdir(actor_path):
            if file.lower().endswith(".wav"):
                match = pattern.match(file)
                if match:
                    emotion_code = match.group(3)  # Extract emotion code
                    emotion_label = emotion_map.get(emotion_code, "Unknown")

                    # Store absolute paths to prevent missing files
                    absolute_path = os.path.abspath(os.path.join(actor_path, file))

                    # Check if file actually exists before adding to CSV
                    if os.path.exists(absolute_path):
                        data.append([absolute_path, emotion_label])
                    else:
                        print(f"Warning: File not found -> {absolute_path}")
                else:
                    print(f"Skipping file '{file}' (Invalid filename pattern)")

# Write to CSV
print("Saving labeled data to CSV...")
try:
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filepath", "emotion"])
        writer.writerows(data)
    print(f"Labeled CSV file saved as '{csv_file}'.")
except IOError as e:
    print(f"Error writing CSV: {e}")

# Final verification
print(f"Total labeled files: {len(data)}")
if len(data) == 0:
    print("⚠️ No valid files were labeled! Check your dataset extraction.")
