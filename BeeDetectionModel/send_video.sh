#!/bin/bash

# File paths
START_TIME_FILE=/var/www/html/ademnea_website/public/bee-detection-model-video-monitoring/start_time.txt
LAST_RUN_FILE=/var/www/html/ademnea_website/public/bee-detection-model-video-monitoring/last_run.txt
PROCESSED_LOG=/var/www/html/ademnea_website/public/bee-detection-model-video-monitoring/processed.log
VIDEO_DIR=/var/www/html/ademnea_website/public/hivevideo
RUNPOD_ENDPOINT=https://api.runpod.ai/v2/qhs9hw3wderytz/run
API_KEY_FILE=/home/hivemonitor/.runpod_api_key

# Load API key
if [ ! -f "$API_KEY_FILE" ]; then
    echo "Error: API key file $API_KEY_FILE not found!"
    exit 1
fi
API_KEY=$(cat "$API_KEY_FILE")

# Set start time if not already set (only on first run)
if [ ! -f "$START_TIME_FILE" ]; then
    date -Iseconds > "$START_TIME_FILE"
fi
START_TIME=$(cat "$START_TIME_FILE")

# Get last run time (default to start time if not set)
LAST_RUN=$(cat "$LAST_RUN_FILE" 2>/dev/null || echo "$START_TIME")

# Find new videos since last run, but only after start time
NEW_VIDEOS=$(find "$VIDEO_DIR" -type f -newermt "$START_TIME" -newermt "$LAST_RUN" -name '*.mp4')

# Filter unprocessed videos
PROCESSED=$(cat "$PROCESSED_LOG" 2>/dev/null)
VIDEOS=()
for VIDEO in $NEW_VIDEOS; do
    if ! grep -Fx "$VIDEO" <<< "$PROCESSED"; then
        VIDEOS+=($(basename "$VIDEO"))
    fi
done

# Create JSON payload wrapped in "input" object
if [ ${#VIDEOS[@]} -gt 0 ]; then
    PAYLOAD=$(jq -n --argjson videos "$(printf '%s\n' "${VIDEOS[@]}" | jq -R . | jq -s .)" \
        '{"input": {"videos": $videos, "timestamp": "'$(date -Iseconds)'"}}')
    # Send to RunPod with API key
    curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" -d "$PAYLOAD" "$RUNPOD_ENDPOINT"
    # Update processed log with full paths
    for VIDEO in "${VIDEOS[@]}"; do
        echo "$VIDEO_DIR/$VIDEO" >> "$PROCESSED_LOG"
    done
fi

# Update last run time
date -Iseconds > "$LAST_RUN_FILE"