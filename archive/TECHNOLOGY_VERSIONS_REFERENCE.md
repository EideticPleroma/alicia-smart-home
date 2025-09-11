# Technology Versions Reference - Alicia Bus Architecture

## Overview
This document provides the latest stable versions of all technologies used in the Alicia bus architecture migration. All versions are current as of January 2025 and represent the most stable, production-ready releases.

## Core Infrastructure

### Containerization & Orchestration
| Technology | Version | Docker Image | Notes |
|------------|---------|--------------|-------|
| **Docker** | 24.0.7+ | `docker:24.0.7` | Latest stable Docker Engine |
| **Docker Compose** | 2.21.0+ | `docker/compose:2.21.0` | Latest stable Compose |
| **Docker MCP** | Latest | `ghcr.io/quantgeekdev/docker-mcp:latest` | Model Context Protocol for Docker |

### Programming Languages
| Language | Version | Package Manager | Notes |
|----------|---------|-----------------|-------|
| **Python** | 3.11.7+ | pip 23.3.1+ | Latest stable 3.11.x series |
| **Node.js** | 20.10.0+ | npm 10.2.3+ | LTS version |
| **TypeScript** | 5.3.0+ | npm | Latest stable |

## Message Bus & Communication

### MQTT & Message Brokers
| Technology | Version | Docker Image | Notes |
|------------|---------|--------------|-------|
| **Eclipse Mosquitto** | 2.0.18+ | `eclipse-mosquitto:2.0.18` | Latest stable 2.0.x |
| **MQTT Protocol** | 5.0 | N/A | Latest MQTT standard |
| **Paho MQTT (Python)** | 1.6.1+ | pip install paho-mqtt | Latest stable |
| **Paho MQTT (JavaScript)** | 1.0.15+ | npm install mqtt | Latest stable |

### WebSockets & Real-time Communication
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **WebSocket** | RFC 6455 | Built-in | WebSocket standard |
| **Socket.IO** | 4.7.4+ | npm install socket.io | Latest stable |

## Voice Processing & AI

### Speech-to-Text
| Technology | Version | Docker Image | Notes |
|------------|---------|--------------|-------|
| **OpenAI Whisper** | 20231117+ | `openai/whisper:latest` | Latest OpenAI Whisper |
| **Wyoming Whisper** | 1.5.0+ | `rhasspy/wyoming-whisper:1.5.0` | Rhasspy Wyoming protocol |
| **Whisper.cpp** | 1.5.4+ | `ghcr.io/ggerganov/whisper.cpp:latest` | C++ implementation |

### Text-to-Speech
| Technology | Version | Docker Image | Notes |
|------------|---------|--------------|-------|
| **Piper TTS** | 1.2.0+ | `rhasspy/piper:1.2.0` | Latest stable Piper |
| **Wyoming Piper** | 1.5.0+ | `rhasspy/wyoming-piper:1.5.0` | Wyoming protocol wrapper |
| **eSpeak** | 1.48.15+ | `espeak:latest` | Fallback TTS |

### AI & Machine Learning
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **OpenAI API** | 1.3.0+ | pip install openai | Latest Python client |
| **Transformers** | 4.36.0+ | pip install transformers | Hugging Face library |
| **PyTorch** | 2.1.0+ | pip install torch | Latest stable |
| **NumPy** | 1.24.4+ | pip install numpy | Latest stable |
| **SciPy** | 1.11.4+ | pip install scipy | Latest stable |

### Wyoming Protocol
| Component | Version | Docker Image | Notes |
|-----------|---------|--------------|-------|
| **Wyoming Core** | 1.5.0+ | `rhasspy/wyoming:1.5.0` | Core Wyoming protocol |
| **Wyoming Whisper** | 1.5.0+ | `rhasspy/wyoming-whisper:1.5.0` | STT service |
| **Wyoming Piper** | 1.5.0+ | `rhasspy/wyoming-piper:1.5.0` | TTS service |
| **Wyoming Wake** | 1.5.0+ | `rhasspy/wyoming-wake:1.5.0` | Wake word detection |

## Web Frameworks & APIs

### Backend Frameworks
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **FastAPI** | 0.104.1+ | pip install fastapi | Latest stable |
| **Uvicorn** | 0.24.0+ | pip install uvicorn | ASGI server |
| **Pydantic** | 2.5.0+ | pip install pydantic | Data validation |
| **SQLAlchemy** | 2.0.23+ | pip install sqlalchemy | ORM |
| **Alembic** | 1.13.0+ | pip install alembic | Database migrations |

### Frontend Frameworks
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **React** | 18.2.0+ | npm install react | Latest stable |
| **TypeScript** | 5.3.0+ | npm install typescript | Type system |
| **Vite** | 5.0.0+ | npm install vite | Build tool |
| **Material-UI** | 5.15.0+ | npm install @mui/material | UI components |

### HTTP Clients & Libraries
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **Requests** | 2.31.0+ | pip install requests | HTTP library |
| **httpx** | 0.25.2+ | pip install httpx | Async HTTP client |
| **aiohttp** | 3.9.1+ | pip install aiohttp | Async HTTP server/client |

## Databases & Storage

### Relational Databases
| Technology | Version | Docker Image | Notes |
|------------|---------|--------------|-------|
| **PostgreSQL** | 16.1+ | `postgres:16.1` | Latest stable |
| **pgvector** | 0.5.1+ | Extension | Vector similarity search |
| **psycopg2** | 2.9.9+ | pip install psycopg2-binary | PostgreSQL adapter |

### NoSQL & Caching
| Technology | Version | Docker Image | Notes |
|------------|---------|--------------|-------|
| **Redis** | 7.2.0+ | `redis:7.2.0` | Latest stable |
| **InfluxDB** | 2.7.0+ | `influxdb:2.7.0` | Time series database |
| **MongoDB** | 7.0.5+ | `mongo:7.0.5` | Document database |

## Security & Authentication

### Encryption & Security
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **Cryptography** | 41.0.8+ | pip install cryptography | Python crypto library |
| **PyJWT** | 2.8.0+ | pip install PyJWT | JWT implementation |
| **OpenSSL** | 3.0.12+ | System | Latest stable |
| **TLS** | 1.3 | Built-in | Latest TLS standard |

### Authentication & Authorization
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **OAuth2** | 1.6.1+ | pip install authlib | OAuth2 implementation |
| **Passlib** | 1.7.4+ | pip install passlib | Password hashing |
| **python-jose** | 3.3.0+ | pip install python-jose | JWT handling |

## Monitoring & Observability

### Metrics & Monitoring
| Technology | Version | Docker Image | Notes |
|------------|---------|--------------|-------|
| **Prometheus** | 2.47.0+ | `prom/prometheus:latest` | Metrics collection |
| **Grafana** | 10.2.0+ | `grafana/grafana:latest` | Visualization |
| **Node Exporter** | 1.6.1+ | `prom/node-exporter:latest` | System metrics |
| **cAdvisor** | 0.47.0+ | `gcr.io/cadvisor/cadvisor:latest` | Container metrics |

### Logging & Tracing
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **Loguru** | 0.7.2+ | pip install loguru | Python logging |
| **structlog** | 23.2.0+ | pip install structlog | Structured logging |
| **Jaeger** | 1.51.0+ | `jaegertracing/all-in-one:latest` | Distributed tracing |

## Home Automation & IoT

### Home Assistant
| Component | Version | Docker Image | Notes |
|-----------|---------|--------------|-------|
| **Home Assistant Core** | 2024.1.0+ | `ghcr.io/home-assistant/home-assistant:stable` | Latest stable |
| **Home Assistant OS** | 11.0+ | N/A | Latest OS version |
| **Supervisor** | 2024.01.0+ | N/A | Latest supervisor |

### IoT & Device Integration
| Technology | Version | Notes |
|------------|---------|-------|
| **Sonos API** | Latest | Sonos Control API |
| **ESP32** | ESP-IDF 5.1+ | Latest stable ESP-IDF |
| **Arduino** | 2.3.2+ | Latest Arduino IDE |
| **MicroPython** | 1.22.0+ | Latest stable |

## Audio & Media Processing

### Audio Libraries
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **PyAudio** | 0.2.11+ | pip install pyaudio | Audio I/O |
| **librosa** | 0.10.1+ | pip install librosa | Audio analysis |
| **soundfile** | 0.12.1+ | pip install soundfile | Audio file I/O |
| **webrtcvad** | 2.0.10+ | pip install webrtcvad | Voice activity detection |

### Media Processing
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **FFmpeg** | 6.1+ | System | Latest stable |
| **GStreamer** | 1.22.7+ | System | Latest stable |
| **OpenCV** | 4.8.1+ | pip install opencv-python | Computer vision |

## Development Tools

### Code Quality & Testing
| Technology | Version | Package | Notes |
|------------|---------|---------|-------|
| **pytest** | 7.4.3+ | pip install pytest | Testing framework |
| **black** | 23.11.0+ | pip install black | Code formatting |
| **flake8** | 6.1.0+ | pip install flake8 | Linting |
| **mypy** | 1.7.1+ | pip install mypy | Type checking |

### Build Tools & CI/CD
| Technology | Version | Notes |
|------------|---------|-------|
| **Git** | 2.43.0+ | Latest stable |
| **GitHub Actions** | Latest | CI/CD platform |
| **Docker Buildx** | 0.12.0+ | Multi-platform builds |

## Operating Systems

### Supported OS Versions
| OS | Version | Notes |
|----|---------|-------|
| **Ubuntu** | 22.04 LTS+ | Recommended for production |
| **Debian** | 12+ | Latest stable |
| **CentOS** | 9+ | Latest stable |
| **Windows** | 11+ | Development only |
| **macOS** | 14+ | Development only |

## Version Compatibility Matrix

### Python 3.11 Compatibility
| Package | Min Version | Max Version | Notes |
|---------|-------------|-------------|-------|
| FastAPI | 0.104.0+ | Latest | Full compatibility |
| Pydantic | 2.5.0+ | Latest | Full compatibility |
| SQLAlchemy | 2.0.20+ | Latest | Full compatibility |
| PyTorch | 2.1.0+ | Latest | Full compatibility |

### Node.js 20 LTS Compatibility
| Package | Min Version | Max Version | Notes |
|---------|-------------|-------------|-------|
| React | 18.2.0+ | Latest | Full compatibility |
| TypeScript | 5.0.0+ | Latest | Full compatibility |
| Vite | 5.0.0+ | Latest | Full compatibility |

## Docker Image Tags Strategy

### Stable Tags
- `latest` - Latest stable release
- `1.2.0` - Specific version
- `1.2` - Latest patch in minor version
- `1` - Latest minor in major version

### Development Tags
- `dev` - Development builds
- `beta` - Beta releases
- `rc` - Release candidates

## Security Considerations

### Vulnerability Management
- All versions listed are free of known critical vulnerabilities
- Regular security updates recommended
- Use `docker scan` to check for vulnerabilities
- Monitor security advisories for all components

### Version Pinning
- Pin major versions for stability
- Use semantic versioning
- Regular dependency updates
- Automated security scanning

## Update Schedule

### Critical Updates
- Security patches: Immediate
- Bug fixes: Within 1 week
- Feature updates: Monthly
- Major versions: Quarterly

### Testing Requirements
- All updates must pass integration tests
- Performance benchmarks must be maintained
- Security scans must pass
- Documentation must be updated

## Migration Notes

### Breaking Changes
- Python 3.11+ required for all services
- FastAPI 0.104+ requires Pydantic 2.5+
- PostgreSQL 16+ requires updated connection strings
- MQTT 5.0 features require client updates

### Compatibility
- All versions are tested together
- Backward compatibility maintained where possible
- Migration guides available for major updates
- Rollback procedures documented

This reference ensures Cline has access to the latest stable versions of all technologies, preventing the use of outdated implementations and ensuring optimal performance and security.
