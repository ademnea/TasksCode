#!/usr/bin/env python3
import os
import subprocess
from tqdm import tqdm

# === Configuration ===
input_folder = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/GEORGELUKAANYA/video/day/full_healthy"
output_root = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/GEORGELUKAANYA/audio/day/final_healthy"
supported_exts = ('.mp4', '.avi', '.mov', '.mkv')

# === Ensure output folder exists ===
os.makedirs(output_root, exist_ok=True)

# === Get video files ===
video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_exts)]

if not video_files:
    print("No video files found in the input folder!")
    exit()

print(f"🎬 Found {len(video_files)} video files to extract audio from")

# === Extract audio using FFmpeg ===
for video_file in tqdm(video_files, desc="Extracting audio"):
    video_path = os.path.join(input_folder, video_file)
    audio_name = os.path.splitext(video_file)[0] + ".wav"
    audio_path = os.path.join(output_root, audio_name)

    # FFmpeg command to extract audio
    command = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i", video_path,
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "44100",          # Sample rate
        "-ac", "2",              # Stereo
        audio_path
    ]

    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        tqdm.write(f"✅ Saved audio: {audio_path}")
    except subprocess.CalledProcessError:
        tqdm.write(f"❌ Failed to extract audio from: {video_path}")

print("🎉 All audio extracted successfully.")
