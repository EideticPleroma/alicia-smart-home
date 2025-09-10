#!/bin/bash

# Install system dependencies
apt-get update && apt-get install -y wget python3 python3-pip alsa-utils pulseaudio

# Download Piper
wget -O piper_amd64.tar.gz https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz

# Download voice models for multiple languages
# English - Primary British Voice
wget -O en_GB-jenny_dioco-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx
wget -O en_GB-jenny_dioco-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx.json

# English - Fallback American Voice
wget -O en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -O en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Spanish
wget -O es_ES-mls_10246-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/medium/es_ES-mls_10246-medium.onnx
wget -O es_ES-mls_10246-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/mls_10246/medium/es_ES-mls_10246-medium.onnx.json

# French
wget -O fr_FR-upmc-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx
wget -O fr_FR-upmc-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json

# German
wget -O de_DE-thorsten-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx
wget -O de_DE-thorsten-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json

# Italian
wget -O it_IT-riccardo-xw.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/riccardo/xw/it_IT-riccardo-xw.onnx
wget -O it_IT-riccardo-xw.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/riccardo/xw/it_IT-riccardo-xw.onnx.json

# Verify critical model downloads
echo "Validating model downloads..."

if [ ! -f "en_GB-jenny_dioco-medium.onnx" ]; then
    echo "❌ ERROR: Failed to download en_GB-jenny model"
    exit 1
fi

if [ ! -f "en_GB-jenny_dioco-medium.onnx.json" ]; then
    echo "❌ ERROR: Failed to download en_GB-jenny config"
    exit 1
fi

echo "✅ en_GB-jenny model validation passed"

# Install Python packages
pip3 install fastapi uvicorn

# Create the Python application file
cat > /app/piper_app.py << 'PYTHON_EOF'
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import uvicorn

class SynthesizeRequest(BaseModel):
    text: str
    language: str = "en"

app = FastAPI()

@app.post("/synthesize")
async def synthesize_text(request: SynthesizeRequest):
    text = request.text
    language = request.language

    # Map language codes to model files (en-gb-jenny as primary English voice)
    model_map = {
        "en": "en_GB-jenny_dioco-medium.onnx",  # Primary English voice
        "en_gb": "en_GB-jenny_dioco-medium.onnx",
        "en_us": "en_US-lessac-medium.onnx",    # Fallback
        "es": "es_ES-mls_10246-medium.onnx",
        "fr": "fr_FR-upmc-medium.onnx",
        "de": "de_DE-thorsten-medium.onnx",
        "it": "it_IT-riccardo-xw.onnx"
    }

    model = model_map.get(language, "en_US-lessac-medium.onnx")

    with open("/tmp/text.txt", "w") as f:
        f.write(text)
    subprocess.run(["./piper/piper", "--model", model, "--output_file", "/tmp/output.wav"], input=text, text=True)
    with open("/tmp/output.wav", "rb") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10200)
PYTHON_EOF

# Make sure the file is executable and run the application
chmod +x /app/piper_app.py
python3 /app/piper_app.py
