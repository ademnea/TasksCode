FROM python:3.9-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    openssh-client \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create temporary directories
RUN mkdir -p /tmp/videos /tmp/output

# Copy application files
COPY app/ .

# Set permissions
RUN chmod +x /app/main.py

# Set default environment variables
ENV YOLO_CONFIG_DIR=/tmp
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "main.py"]