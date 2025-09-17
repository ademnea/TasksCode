#!/usr/bin/env python3
from pydub import AudioSegment
from pydub.utils import make_chunks
import os
from tqdm import tqdm

def split_mp3(input_file, output_folder, chunk_length_ms=60000):
    """Split MP3 file into 1-minute MP3 chunks"""
    try:
        # Load MP3 file
        audio = AudioSegment.from_mp3(input_file)
    except Exception as e:
        print(f"❌ Error loading MP3 file {os.path.basename(input_file)}: {e}")
        return 0
    
    # Create output directory
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    os.makedirs(output_folder, exist_ok=True)
    
    # Split into chunks
    chunks = make_chunks(audio, chunk_length_ms)
    
    # Export each chunk as MP3
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(output_folder, f"{base_name}_chunk_{i+1:03d}.mp3")
        chunk.export(chunk_path, format="mp3", bitrate="192k")
    
    return len(chunks)

def process_folder(input_folder, output_root):
    """Process all MP3 files in a folder"""
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.mp3')]
    
    if not mp3_files:
        print("❌ No MP3 files found in input folder")
        return
    
    print(f"🔈 Found {len(mp3_files)} MP3 files to process")
    os.makedirs(output_root, exist_ok=True)
    
    total_chunks = 0
    for mp3_file in tqdm(mp3_files, desc="Processing MP3 files"):
        input_path = os.path.join(input_folder, mp3_file)
        # Create subfolder for each file's chunks
        output_subfolder = os.path.join(output_root, os.path.splitext(mp3_file)[0])
        chunks_created = split_mp3(input_path, output_subfolder)
        total_chunks += chunks_created
        tqdm.write(f"✔️ Created {chunks_created} chunks from {mp3_file}")
    
    print(f"\n🎉 Successfully created {total_chunks} MP3 chunks from {len(mp3_files)} files")

if __name__ == "__main__":
    # Configuration
    INPUT_FOLDER = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/audios/full_audio/unhealthy"  # Folder containing audio files
    OUTPUT_ROOT = "/home/ltgwgeorge/Desktop/IoT-RA/data_collection/audios/final_audio/unhealthy"  # Root folder for all chunk outputs
    
    # Run the processor
    process_folder(INPUT_FOLDER, OUTPUT_ROOT)