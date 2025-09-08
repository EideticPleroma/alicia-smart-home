#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y python3 python3-pip ffmpeg

# Install Python packages
pip3 install openai-whisper fastapi uvicorn

# Create the Python application
cat > /app/whisper_app.py << 'EOF'
from fastapi import FastAPI, UploadFile
import whisper
import uvicorn

app = FastAPI()
model = whisper.load_model("base")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile):
    audio_data = await file.read()
    with open("/tmp/audio.wav", "wb") as f:
        f.write(audio_data)
    result = model.transcribe("/tmp/audio.wav")
    return {"text": result["text"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
EOF

# Run the application
python3 /app/whisper_app.py
