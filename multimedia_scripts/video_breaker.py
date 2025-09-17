#!/usr/bin/env python3
import cv2
import os
from tqdm import tqdm

# === Configuration ===
input_folder = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/GEORGELUKAANYA/video/day/full_healthy"           # Folder with original videos
output_root = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/GEORGELUKAANYA/video/day/final_healthy"       # Root folder to save 1-min chunks
chunk_duration_sec = 60                # Chunk length in seconds
supported_exts = ('.mp4', '.avi', '.mov', '.mkv')

# === Ensure output root exists ===
os.makedirs(output_root, exist_ok=True)

# === Loop through all video files ===
video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_exts)]

if not video_files:
    print("No video files found in the input folder!")
    exit()

print(f"Found {len(video_files)} video files to process")

for video_file in video_files:
    video_path = os.path.join(input_folder, video_file)
    video_name = os.path.splitext(video_file)[0]
    output_folder = os.path.join(output_root, video_name)
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_per_chunk = fps * chunk_duration_sec
    total_chunks = (total_frames + frames_per_chunk - 1) // frames_per_chunk  # Ceiling division

    print(f"\n📂 Processing '{video_file}' ({fps} fps, {total_frames} frames, ~{total_chunks} chunks)")

    # Create progress bar for the entire video processing
    with tqdm(total=total_frames, desc=f"Processing {video_file}", unit='frame') as pbar:
        chunk_index = 0
        frame_index = 0

        while cap.isOpened():
            chunk_path = os.path.join(output_folder, f"{video_name}_chunk_{chunk_index:03d}.mp4")
            out = cv2.VideoWriter(chunk_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

            written = 0
            while written < frames_per_chunk:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                written += 1
                frame_index += 1
                pbar.update(1)  # Update progress bar for each frame

            out.release()
            if written > 0:
                tqdm.write(f"✅ Saved: {chunk_path}")  # Use tqdm.write to avoid progress bar interference
            else:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)  # remove empty file

            chunk_index += 1

            if frame_index >= total_frames:
                break

    cap.release()
    print(f"✔️ Finished splitting: {video_file}\n")

print("🎉 All videos processed.")