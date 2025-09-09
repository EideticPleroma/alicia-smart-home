#!/bin/bash

# Install system dependencies
apt-get update && apt-get install -y python3 python3-pip ffmpeg

# Install Python packages
pip3 install openai-whisper fastapi uvicorn python-multipart

# Create the Python application file
cat > /app/whisper_app.py << 'PYTHON_EOF'
from fastapi import FastAPI, UploadFile
import whisper
import uvicorn

app = FastAPI()
model = whisper.load_model("medium")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile):
    audio_data = await file.read()
    with open("/tmp/audio.wav", "wb") as f:
        f.write(audio_data)
    result = model.transcribe("/tmp/audio.wav", language=None)  # Detect language automatically
    return {"text": result["text"], "language": result["language"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
PYTHON_EOF

# Make sure the file is executable and run the application
chmod +x /app/whisper_app.py
python3 /app/whisper_app.py
