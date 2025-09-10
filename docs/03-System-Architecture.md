---
tags: #architecture-diagram #system-diagram #alicia-project #high-level-design #data-flow #mermaid-diagram #voice-processing #mqtt-communication #iot-integration
---

# Alicia High Level Architecture Diagram

This diagram shows the complete data flow for the Alicia smart home system, from voice input to device control.

## System Flow Overview:
1. **Voice Input** → USB Microphone captures audio with wake word detection
2. **Speech Processing** → Whisper STT converts voice to text with confidence scoring
3. **Context Management** → ConversationContext maintains session state and device status
4. **AI Processing** → GrokHandler processes commands through Grok-4 API with rate limiting
5. **Personality Enhancement** → PersonalityManager adds wit, sarcasm, and contextual responses
6. **Voice Output** → Piper TTS generates natural speech with HTTP audio server
7. **Audio Delivery** → MQTT bridge delivers audio to Sonos speakers
8. **Device Control** → IoT devices (ESP32, bulbs, etc.) receive commands via MQTT

## Key Components:
- **USB Microphone**: Audio input with 16kHz sampling
- **Porcupine**: Wake word detection engine
- **Whisper STT**: OpenAI speech-to-text with 99+ languages
- **GrokHandler**: Grok-4 API client with context management
- **PersonalityManager**: Witty response generation and conversation flow
- **Piper TTS**: Neural text-to-speech synthesis
- **HTTP Audio Server**: Audio file serving for Sonos integration
- **MQTT Broker**: Secure message routing with authentication
- **Home Assistant**: Smart home automation platform
- **PostgreSQL**: Database with pgvector for AI model storage
- **IoT Devices**: ESP32 sensors, TP-Link bulbs, Sonos speakers

```mermaid
graph TB
    subgraph "🎤 Input Processing"
        A[USB Microphone<br/>16kHz] -->|Audio| B{Porcupine<br/>Wake Word}
        B -->|Voice Command| C[Audio Buffer<br/>WAV]
    end

    subgraph "📝 Speech Processing"
        C -->|Raw Audio| D[Whisper STT<br/>OpenAI API]
        D -->|Text + Confidence| E[Text Command]
    end

    subgraph "🧠 AI & Personality"
        E -->|Text| F[Context Manager<br/>Session State]
        F -->|Context| G[GrokHandler<br/>Grok-4 API]
        G -->|AI Response| H[PersonalityManager<br/>Witty Enhancement]
        H -->|Enhanced Response| I[Response Text]
    end

    subgraph "🔊 Audio Generation"
        I -->|Text| J[Piper TTS<br/>Neural Synthesis]
        J -->|WAV/MP3| K[Audio File]
    end

    subgraph "📡 Delivery"
        K -->|HTTP URL| L[HTTP Audio Server<br/>Port 8080]
        L -->|MQTT Command| M[MQTT Bridge<br/>Sonos Integration]
        M -->|Audio Stream| N[Sonos Speakers]
    end

    subgraph "🏠 Smart Home"
        O[Home Assistant] -->|Device Status| F
        F -->|Commands| O
        O -->|Actions| P[IoT Devices<br/>ESP32, Bulbs]
    end

    subgraph "💾 Data Storage"
        Q[PostgreSQL<br/>pgvector] -->|Embeddings| G
        G -->|Context| Q
    end

    F -.-> R[Performance<br/>Monitoring]
    G -.-> R
    J -.-> R
