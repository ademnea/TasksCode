#!/usr/bin/env python3
from pydub import AudioSegment
import os
from tqdm import tqdm

def combine_mp3_chunks(input_folder, output_folder, group_size=10):
    """Combine every N MP3 chunks from a single flat folder"""
    
    # Get sorted list of MP3 files in the folder
    mp3_files = sorted([
        f for f in os.listdir(input_folder)
        if f.lower().endswith('.mp3') and os.path.isfile(os.path.join(input_folder, f))
    ])

    if not mp3_files:
        print(f"❌ No MP3 files found in {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    total_combined = 0
    group = []
    group_index = 1
    output_base = os.path.basename(os.path.normpath(input_folder))

    for i, file in enumerate(tqdm(mp3_files, desc="Combining")):
        file_path = os.path.join(input_folder, file)
        try:
            group.append(AudioSegment.from_mp3(file_path))
        except Exception as e:
            print(f"⚠️ Skipping {file}: {e}")
            continue

        # Combine and export every N files or at the end
        if len(group) == group_size or i == len(mp3_files) - 1:
            combined = sum(group)
            output_file = f"{output_base}_combined_{group_index:03d}.mp3"
            output_path = os.path.join(output_folder, output_file)
            combined.export(output_path, format="mp3", bitrate="192k")
            tqdm.write(f"🎵 Saved {output_path}")
            total_combined += 1
            group = []
            group_index += 1

    print(f"\n✅ Done! Combined into {total_combined} MP3 files.")

if __name__ == "__main__":
    # === Configuration ===
    INPUT_FOLDER = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/GEORGELUKAANYA/audio/unhealthy"  # Folder with .mp3 files
    OUTPUT_FOLDER = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/GEORGELUKAANYA/audio/combined_unhealthy"  # Save location
    CHUNKS_PER_COMBINED_FILE = 10  # 10 files → 10 minutes

    combine_mp3_chunks(INPUT_FOLDER, OUTPUT_FOLDER, CHUNKS_PER_COMBINED_FILE)
