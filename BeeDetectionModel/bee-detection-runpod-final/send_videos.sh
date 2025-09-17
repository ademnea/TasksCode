#!/bin/bash

# Paths
START_TIME_FILE=/var/www/html/ademnea_website/public/bee-detection-model-video-monitoring/start_time.txt
LAST_RUN_FILE=/var/www/html/ademnea_website/public/bee-detection-model-video-monitoring/last_run.txt
PROCESSED_LOG=/var/www/html/ademnea_website/public/bee-detection-model-video-monitoring/processed.log
VIDEO_DIR=/var/www/html/ademnea_website/public/hivevideo

# RunPod Endpoint (corrected to actual structure!)
RUNPOD_ENDPOINT="https://api.runpod.ai/v2/{endpoint_id}/run"

# Add your actual RunPod API Key
API_KEY="your_runpod_api_key_here"

# Lock
LOCK_FILE="/tmp/bee_detection.lock"
exec 200>"$LOCK_FILE"
flock -n 200 || { echo "Script is already running"; exit 1; }

# Init START_TIME
if [ ! -f "$START_TIME_FILE" ]; then
    date -Iseconds > "$START_TIME_FILE"
fi
START_TIME=$(cat "$START_TIME_FILE")

# Get LAST_RUN
LAST_RUN=$(cat "$LAST_RUN_FILE" 2>/dev/null || echo "$START_TIME")

# Find New Videos
NEW_VIDEOS=$(find "$VIDEO_DIR" -type f -newermt "$LAST_RUN" -name '*.mp4')
PROCESSED=$(cat "$PROCESSED_LOG" 2>/dev/null)

# Filter Unprocessed Videos
VIDEOS=()
for VIDEO in $NEW_VIDEOS; do
    if ! grep -Fx "$VIDEO" <<< "$PROCESSED"; then
        VIDEOS+=("$(basename "$VIDEO")")
    fi
done

# Proceed if New Videos Found
if [ ${#VIDEOS[@]} -gt 0 ]; then
    PAYLOAD=$(jq -n \
        --arg timestamp "$(date -Iseconds)" \
        --argjson videos "$(printf '%s\n' "${VIDEOS[@]}" | jq -R . | jq -s .)" \
        '{input: {videos: $videos, timestamp: $timestamp}}')

    # RunPod Request
    RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/response.txt \
        -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer '"$API_KEY"'" \
        -d "$PAYLOAD" \
        "$RUNPOD_ENDPOINT")

    if [ "$RESPONSE" -ne 200 ]; then
        echo "Error: Push failed with status $RESPONSE"
        cat /tmp/response.txt
        exit 1
    else
        echo "Push succeeded! Job response:"
        cat /tmp/response.txt
    fi

    # Mark Videos as Processed
    for VIDEO in "${VIDEOS[@]}"; do
        echo "$VIDEO_DIR/$VIDEO" >> "$PROCESSED_LOG"
    done
fi

# Update LAST_RUN
date -Iseconds > "$LAST_RUN_FILE"
