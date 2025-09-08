---
tags: #architecture-diagram #system-diagram #alicia-project #high-level-design #data-flow #mermaid-diagram #voice-processing #mqtt-communication #iot-integration
---

# Alicia High Level Architecture Diagram

This diagram shows the complete data flow for the Alicia smart home system, from voice input to device control.

## System Flow Overview:
1. **Voice Input** → USB Microphone captures audio
2. **Speech Processing** → Whisper converts voice to text
3. **Message Routing** → MQTT broker distributes messages
4. **AI Processing** → Home Assistant processes commands
5. **API Integration** → Grok API provides intelligent responses
6. **Voice Output** → Text-to-Speech via Sonos speakers
7. **Device Control** → IoT devices (ESP32, bulbs, etc.) receive commands

## Key Components:
- **USB Mic**: Audio input device
- **Whisper**: Speech-to-text processing
- **MQTT**: Message broker for device communication
- **HA Core**: Home Assistant automation platform
- **Grok API**: AI language model for responses
- **Sonos**: Audio output and voice synthesis
- **IoT Devices**: Smart home devices (sensors, bulbs, etc.)

```mermaid
graph LR
    subgraph Inbound
        A[USB Mic] -->|Voice| B{Whisper}
    end
    subgraph Processing
        B -->|Text| C{MQTT}
        C -->|Text| D{HA Core}
        D -->|Query| E{Grok API}
        E -->|Response| D
    end
    subgraph Outbound
        D -->|TTS| F[Sonos]
    end
    G[IoT e.g., ESP32] -->|Instructions| C
    C -->|Commands| D
    D -->|Actions| G
