import os
import json
import csv
import paramiko
from datetime import datetime
from ultralytics import YOLO
from dotenv import load_dotenv
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Verify critical variables
REMOTE_HOST = os.getenv('REMOTE_HOST')
REMOTE_USER = os.getenv('REMOTE_USER')
REMOTE_PASS = os.getenv('REMOTE_PASS')
SSH_KEY_PATH = os.getenv('SSH_KEY_PATH')
REMOTE_VIDEO_PATH = os.getenv('REMOTE_VIDEO_PATH')
REMOTE_OUTPUT_PATH = os.getenv('REMOTE_OUTPUT_PATH')

for var, name in [(REMOTE_HOST, 'REMOTE_HOST'), (REMOTE_USER, 'REMOTE_USER'), 
                  (REMOTE_VIDEO_PATH, 'REMOTE_VIDEO_PATH'), (REMOTE_OUTPUT_PATH, 'REMOTE_OUTPUT_PATH')]:
    if not var:
        logger.error(f"{name} environment variable not set!")
        sys.exit(1)

# Configuration - Container-local paths
MODEL_PATH = "/app/best.pt"
LOCAL_VIDEO_DIR = "/tmp/videos"
LOCAL_OUTPUT_DIR = "/tmp/output"
PROCESSED_LOG = "/app/processed.log"
LAST_RUN_FILE = "/app/last_run.txt"

# Initialize YOLO model
logger.info("Loading YOLO model from %s", MODEL_PATH)
try:
    model = YOLO(MODEL_PATH)
    model.fuse()
except Exception as e:
    logger.error("Failed to load YOLO model: %s", str(e))
    sys.exit(1)

def ssh_command(command):
    """Execute SSH command on remote server."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.info("Executing SSH command: %s", command)
        if SSH_KEY_PATH and os.path.exists(SSH_KEY_PATH):
            logger.info("Using SSH key authentication")
            client.connect(
                hostname=REMOTE_HOST,
                username=REMOTE_USER,
                key_filename=SSH_KEY_PATH,
                timeout=10
            )
        else:
            logger.warning("Falling back to password-based authentication")
            if not REMOTE_PASS:
                logger.error("REMOTE_PASS not set for password authentication")
                sys.exit(1)
            client.connect(
                hostname=REMOTE_HOST,
                username=REMOTE_USER,
                password=REMOTE_PASS,
                timeout=10
            )
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            logger.error("SSH command error: %s", error)
        logger.info("SSH command output: %s", output)
        return output
    except Exception as e:
        logger.error("SSH Error: %s", str(e))
        raise
    finally:
        client.close()

def scp_download(remote_path, local_path):
    """Download file via SCP."""
    logger.info("Downloading from %s to %s", remote_path, local_path)
    if SSH_KEY_PATH and os.path.exists(SSH_KEY_PATH):
        command = f"scp -i {SSH_KEY_PATH} {REMOTE_USER}@{REMOTE_HOST}:{remote_path} {local_path}"
    else:
        if not REMOTE_PASS:
            logger.error("REMOTE_PASS not set for password authentication")
            sys.exit(1)
        command = f"SSHPASS={REMOTE_PASS} sshpass -e scp {REMOTE_USER}@{REMOTE_HOST}:{remote_path} {local_path}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("SCP download error: %s", str(e))
        raise

def scp_upload(content, remote_path):
    """Upload content via SCP."""
    local_temp = "/tmp/temp_result.json"
    logger.info("Uploading to %s", remote_path)
    try:
        with open(local_temp, "w") as f:
            f.write(content)
        if SSH_KEY_PATH and os.path.exists(SSH_KEY_PATH):
            command = f"scp -i {SSH_KEY_PATH} {local_temp} {REMOTE_USER}@{REMOTE_HOST}:{remote_path}"
        else:
            if not REMOTE_PASS:
                logger.error("REMOTE_PASS not set for password authentication")
                sys.exit(1)
            command = f"SSHPASS={REMOTE_PASS} sshpass -e scp {local_temp} {REMOTE_USER}@{REMOTE_HOST}:{remote_path}"
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("SCP upload error: %s", str(e))
        raise
    finally:
        if os.path.exists(local_temp):
            os.remove(local_temp)

def process_video(video_name):
    """Process a single video and upload results."""
    try:
        logger.info("Processing video: %s", video_name)
        remote_path = os.path.join(REMOTE_VIDEO_PATH, video_name)
        local_path = os.path.join(LOCAL_VIDEO_DIR, video_name)

        # Download video
        logger.info("Downloading %s to %s", remote_path, local_path)
        scp_download(remote_path, local_path)

        # Process with YOLO
        logger.info("Running YOLO model on %s", local_path)
        results = model.track(local_path, stream=True, persist=True)
        bee_ids = {int(box.id[0]) for r in results for box in r.boxes if box.id is not None}

        # Prepare output
        timestamp = datetime.now().isoformat()
        result = {
            "video": video_name,
            "timestamp": timestamp,
            "bee_count": len(bee_ids),
            "bee_ids": list(bee_ids)
        }
        logger.info("YOLO results: %s", result)

        # Save results locally to CSV
        os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)
        csv_path = f"{LOCAL_OUTPUT_DIR}/results.csv"
        with open(csv_path, "a") as f:
            writer = csv.writer(f)
            writer.writerow([result["video"], timestamp, result["bee_count"], ",".join(map(str, bee_ids))])

        # Upload to remote server
        logger.info("Uploading results to %s", REMOTE_OUTPUT_PATH)
        ssh_command(f"mkdir -p {REMOTE_OUTPUT_PATH}")
        scp_upload(json.dumps(result), f"{REMOTE_OUTPUT_PATH}/results.json")

        # Update logs
        with open(PROCESSED_LOG, "a") as f:
            f.write(f"{remote_path}\n")
        logger.info("Video %s processed successfully", video_name)

    except Exception as e:
        logger.error("Error processing video %s: %s", video_name, str(e))
        raise
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

def main():
    """Main function to handle JSON payload."""
    # Initialize files
    for f in [PROCESSED_LOG, LAST_RUN_FILE]:
        if not os.path.exists(f):
            open(f, 'w').close()

    # Read JSON payload from stdin
    try:
        payload = json.load(sys.stdin)
        logger.info("Received payload: %s", payload)
        # Extract data from "input" key
        input_data = payload.get("input", {})
        if not input_data:
            logger.error("No 'input' key in payload")
            sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON payload: %s", str(e))
        logger.info("For local testing, provide a JSON payload via stdin, e.g.:")
        logger.info('echo \'{"input": {"videos": ["sample.mp4"], "timestamp": "2025-06-26T09:12:00Z"}}\' | python main.py')
        sys.exit(0)

    # Process videos in the payload
    videos = input_data.get("videos", [])
    if not videos:
        logger.warning("No videos in payload")
        return

    for video in videos:
        process_video(video)

    # Update last run time
    with open(LAST_RUN_FILE, "w") as f:
        f.write(datetime.now().isoformat())

if __name__ == "__main__":
    main()