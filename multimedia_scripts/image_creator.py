#!/usr/bin/env python3
import os
import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image  # For alternative saving method

def extract_frames(video_folder, output_folder, frame_interval=5, quality=100, use_pillow=False):
    """
    Extract high-quality frames from videos with perfect color accuracy.
    
    Args:
        video_folder: Path to folder containing video files
        output_folder: Path to save extracted frames
        frame_interval: Extract every nth frame (default: 5 for 30fps→6fps)
        quality: JPEG quality (1-100, default: 100)
        use_pillow: If True, uses PIL for saving (best quality)
    """
    os.makedirs(output_folder, exist_ok=True)

    video_files = [f for f in os.listdir(video_folder)
                   if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv'))]

    if not video_files:
        print(f"❌ No video files found in {video_folder}")
        return

    print(f"🔍 Found {len(video_files)} video files to process")

    for video_file in video_files:
        video_path = os.path.join(video_folder, video_file)
        video_name = os.path.splitext(video_file)[0]
        output_subfolder = os.path.join(output_folder, video_name)

        os.makedirs(output_subfolder, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Failed to open: {video_file}")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"\n📹 Processing: {video_file} ({width}x{height}, {fps:.1f}fps)")
        print(f"⚙️  Extracting 1 frame every {frame_interval} frames")
        print(f"🖼️  Output quality: {quality} {'(using Pillow)' if use_pillow else '(using OpenCV)'}")

        frame_count = 0
        saved_count = 0

        with tqdm(total=total_frames, desc=f"Extracting {video_file}", unit='frame') as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    frame_filename = os.path.join(
                        output_subfolder,
                        f"{video_name}_frame_{frame_count:06d}.jpg"
                    )

                    if use_pillow:
                        Image.fromarray(rgb_frame).save(
                            frame_filename,
                            format='JPEG',
                            quality=quality,
                            subsampling=0,         # No chroma subsampling
                            optimize=True,         # Better compression
                            progressive=True       # For better web rendering
                        )
                    else:
                        cv2.imwrite(
                            frame_filename,
                            cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR),
                            [cv2.IMWRITE_JPEG_QUALITY, quality,
                             cv2.IMWRITE_JPEG_OPTIMIZE, 1,
                             cv2.IMWRITE_JPEG_SUBSAMPLE, 0]
                        )

                    saved_count += 1

                frame_count += 1
                pbar.update(1)

        cap.release()
        print(f"✅ Saved {saved_count} frames to {output_subfolder}")

    print("\n🎉 Frame extraction completed successfully!")

if __name__ == "__main__":
    # ===== Configuration =====
    VIDEO_FOLDER = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/GEORGELUKAANYA/video/night/full_healthy"
    OUTPUT_FOLDER = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/images/night/healthy"

    # Extraction parameters
    FRAME_INTERVAL = 29       # Extract every 29th frame (30fps → 1fps)
    JPEG_QUALITY = 100       # Use max JPEG quality
    USE_PILLOW = True        # Pillow gives better color preservation

    extract_frames(
        video_folder=VIDEO_FOLDER,
        output_folder=OUTPUT_FOLDER,
        frame_interval=FRAME_INTERVAL,
        quality=JPEG_QUALITY,
        use_pillow=USE_PILLOW
    )
