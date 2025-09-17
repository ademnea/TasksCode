import os
import shutil
import re
import random
from datetime import datetime, timedelta

# Set your main folders
SOURCE_ROOT = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/videos/final_videos/new/GeorgeData/originals/videos"
DEST_ROOT = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/videos/final_videos/new/GeorgeData/originals/videos"

# Create destination root if it doesn't exist
os.makedirs(DEST_ROOT, exist_ok=True)

# Random datetime between 01/07/2025 and 04/07/2025
def random_date_between(start_date, end_date):
    delta_seconds = int((end_date - start_date).total_seconds())
    random_seconds = random.randint(0, delta_seconds)
    return start_date + timedelta(seconds=random_seconds)

# Randomize numbers in filename while preserving format
def randomize_filename(name):
    def replace_digits(match):
        digit_group = match.group()
        # Preserve leading zeros
        new_number = str(random.randint(0, 10**len(digit_group)-1)).zfill(len(digit_group))
        return new_number

    name_without_ext, ext = os.path.splitext(name)
    randomized = re.sub(r'\d+', replace_digits, name_without_ext)
    return randomized + ext

# Process all folders
def process_folders(source_root, dest_root):
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 4, 23, 59, 59)

    for folder_name in os.listdir(source_root):
        source_folder_path = os.path.join(source_root, folder_name)
        if not os.path.isdir(source_folder_path):
            continue

        dest_folder_path = os.path.join(dest_root, folder_name + "_copy")
        os.makedirs(dest_folder_path, exist_ok=True)

        for file_name in os.listdir(source_folder_path):
            if file_name.lower().endswith('.mp4'):
                original_path = os.path.join(source_folder_path, file_name)

                # Randomize filename (same format)
                new_name = randomize_filename(file_name)
                dest_file_path = os.path.join(dest_folder_path, new_name)

                # Copy video
                shutil.copy2(original_path, dest_file_path)

                # Assign random date between July 1–4
                random_date = random_date_between(start_date, end_date)
                mod_time = random_date.timestamp()
                os.utime(dest_file_path, (mod_time, mod_time))

                print(f"✔ {file_name} → {new_name} | Timestamp: {random_date.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                continue  # Skip .mp3 or others

process_folders(SOURCE_ROOT, DEST_ROOT)
