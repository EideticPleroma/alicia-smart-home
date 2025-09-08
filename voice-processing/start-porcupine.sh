#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y python3 python3-pip fastapi uvicorn

# Install Python packages
pip3 install fastapi uvicorn

# Create the Python application
cat > /app/porcupine_app.py << 'EOF'
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/listen")
async def listen_for_wake_word():
    return {"wake_word_detected": False, "message": "Wake word detection disabled - using simple trigger"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10400)
EOF

# Run the application
python3 /app/porcupine_app.py
