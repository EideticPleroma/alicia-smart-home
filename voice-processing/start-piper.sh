#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y wget python3 python3-pip alsa-utils pulseaudio

# Download Piper
wget -O piper_amd64.tar.gz https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz

# Download voice model
wget -O en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -O en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Install Python packages
pip3 install fastapi uvicorn

# Create the Python application
cat > /app/piper_app.py << 'EOF'
from fastapi import FastAPI
import subprocess
import uvicorn

app = FastAPI()

@app.post("/synthesize")
async def synthesize_text(text: str):
    with open("/tmp/text.txt", "w") as f:
        f.write(text)
    subprocess.run(["./piper/piper", "--model", "en_US-lessac-medium.onnx", "--output_file", "/tmp/output.wav"], input=text.encode(), text=True)
    with open("/tmp/output.wav", "rb") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10200)
EOF

# Run the application
python3 /app/piper_app.py
