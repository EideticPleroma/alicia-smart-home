# Chapter 9: TTS Service & Voice Router

## 🎯 **Voice Pipeline Orchestration Overview**

The TTS (Text-to-Speech) Service and Voice Router complete Alicia's voice processing pipeline. The TTS service converts AI responses into natural-sounding speech, while the Voice Router orchestrates the entire voice pipeline from audio input to speaker output. This chapter analyzes both services, examining their multi-engine architecture, pipeline coordination, and integration patterns.

## 🎤 **TTS Service Architecture**

### **Multi-Engine TTS Support**

The TTS service implements a **sophisticated multi-engine architecture** similar to the STT service:

```python
class TTSService(BusServiceWrapper):
    """
    TTS Service for the Alicia bus architecture.
    
    Handles text-to-speech synthesis with multiple engine support:
    - Piper TTS (primary)
    - Google Text-to-Speech (fallback)
    - Azure Speech Services (enterprise)
    """
```

**Why Multiple TTS Engines?**

1. **Voice Quality**: Different engines excel at different voice characteristics
2. **Language Support**: Different engines support different languages
3. **Cost Optimization**: Use appropriate engines for different use cases
4. **Reliability**: Fallback options ensure continuous operation
5. **Customization**: Different engines offer different customization options

### **TTS Configuration and Setup**

The TTS service uses **comprehensive configuration** for voice synthesis:

```python
def __init__(self):
    # TTS Configuration
    self.tts_engine = os.getenv("TTS_ENGINE", "piper")  # piper, google, azure
    self.voice_model = os.getenv("VOICE_MODEL", "en_US-lessac-medium")
    self.speaker_id = int(os.getenv("SPEAKER_ID", "0"))
    self.sample_rate = int(os.getenv("SAMPLE_RATE", "22050"))
    self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
```

**Configuration Benefits:**
- **Voice Selection**: Choose appropriate voice models
- **Quality Control**: Set sample rates and audio quality
- **Performance Tuning**: Optimize for different use cases
- **Language Support**: Support multiple languages and accents

## 🔊 **Piper TTS Integration (Primary Engine)**

### **Piper TTS Setup**

The TTS service uses **Piper TTS** as its primary engine due to its high quality and open-source nature:

```python
def _setup_piper(self):
    """Setup Piper TTS engine."""
    try:
        # Import Piper (assuming it's available)
        # For now, we'll use subprocess to call piper executable
        import subprocess
        self.piper_client = subprocess
        self.logger.info("Piper TTS client initialized")
    except ImportError:
        self.logger.error("Piper TTS not available. Install with: pip install piper-tts")
        raise
    except Exception as e:
        self.logger.error(f"Failed to setup Piper TTS: {e}")
        raise
```

**Why Piper TTS?**
- **Open Source**: No licensing costs or restrictions
- **High Quality**: Excellent voice synthesis quality
- **Offline Processing**: No internet connection required
- **Customizable**: Can be trained on custom voices
- **Lightweight**: Efficient resource usage

### **Piper TTS Processing**

The TTS service implements **comprehensive Piper TTS processing**:

```python
async def _synthesize_with_piper(self, text: str, voice_settings: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize speech using Piper TTS."""
    try:
        # Prepare Piper command
        piper_command = [
            "piper",
            "--model", f"/app/models/{self.voice_model}.onnx",
            "--config", f"/app/models/{self.voice_model}.onnx.json",
            "--output_file", "/tmp/output.wav"
        ]
        
        # Add voice settings
        if voice_settings.get("speed"):
            piper_command.extend(["--length_scale", str(voice_settings["speed"])])
        
        if voice_settings.get("pitch"):
            piper_command.extend(["--noise_scale", str(voice_settings["pitch"])])
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(text)
            temp_file_path = temp_file.name
        
        # Run Piper TTS
        result = subprocess.run(
            piper_command + [temp_file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Read generated audio
            with open("/tmp/output.wav", "rb") as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # Clean up temporary files
            os.unlink(temp_file_path)
            os.unlink("/tmp/output.wav")
            
            return {
                "audio_data": audio_data,
                "format": "wav",
                "sample_rate": self.sample_rate,
                "duration": self._calculate_audio_duration(audio_data),
                "engine_used": "piper"
            }
        else:
            raise Exception(f"Piper TTS failed: {result.stderr}")
            
    except Exception as e:
        self.logger.error(f"Piper TTS synthesis failed: {e}")
        raise
```

**Piper TTS Features:**
- **Model-based Synthesis**: Use pre-trained voice models
- **Voice Customization**: Adjust speed, pitch, and other parameters
- **Format Support**: Generate audio in multiple formats
- **Quality Control**: High-quality voice synthesis

## 🔄 **Fallback TTS Engines**

### **Google Text-to-Speech Integration**

The TTS service includes **Google Cloud Text-to-Speech** as a fallback option:

```python
def _setup_google(self):
    """Setup Google Text-to-Speech client."""
    try:
        from google.cloud import texttospeech
        self.google_client = texttospeech.TextToSpeechClient()
        self.logger.info("Google TTS client initialized")
    except ImportError:
        self.logger.warning("Google Cloud TTS not available")
    except Exception as e:
        self.logger.error(f"Failed to setup Google TTS: {e}")
```

**Google TTS Benefits:**
- **Cloud Processing**: Offloads processing to Google's servers
- **High Quality**: Excellent voice synthesis quality
- **Language Support**: Support for 100+ languages
- **Voice Variety**: Multiple voice options
- **Real-time Streaming**: Support for streaming audio

### **Azure Speech Services Integration**

The TTS service also supports **Azure Speech Services** for enterprise deployments:

```python
def _setup_azure(self):
    """Setup Azure Speech Services client."""
    try:
        import azure.cognitiveservices.speech as speechsdk
        speech_key = os.getenv("AZURE_SPEECH_KEY")
        service_region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        if speech_key:
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
            self.azure_client = speech_config
            self.logger.info("Azure Speech client initialized")
        else:
            self.logger.warning("Azure Speech key not configured")
    except ImportError:
        self.logger.warning("Azure Speech SDK not available")
    except Exception as e:
        self.logger.error(f"Failed to setup Azure Speech: {e}")
```

**Azure Speech Benefits:**
- **Enterprise Features**: Advanced security and compliance
- **Custom Voice**: Create custom voice models
- **Neural Voices**: High-quality neural voice synthesis
- **SSML Support**: Advanced speech markup language
- **Integration**: Easy integration with Microsoft services

## 🎛️ **Voice Router Architecture**

### **Pipeline Orchestration**

The Voice Router serves as the **central coordinator** for the entire voice pipeline:

```python
class VoiceRouter(BusServiceWrapper):
    """
    Voice Router service for the Alicia bus architecture.
    
    Orchestrates the complete voice pipeline:
    1. Receives voice commands
    2. Routes to STT service for transcription
    3. Routes transcription to AI service for processing
    4. Routes AI response to TTS service for synthesis
    5. Routes synthesized audio to speaker services
    """
```

**Pipeline Steps:**
1. **Audio Input**: Receive audio from microphones or other sources
2. **STT Processing**: Convert audio to text using STT service
3. **AI Processing**: Process text using AI service
4. **TTS Synthesis**: Convert AI response to speech using TTS service
5. **Audio Output**: Send synthesized audio to speakers

### **Session Management**

The Voice Router implements **comprehensive session management**:

```python
def __init__(self):
    # Voice Router Configuration
    self.max_sessions = int(os.getenv("MAX_SESSIONS", "10"))
    self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "300"))  # 5 minutes
    self.pipeline_timeout = int(os.getenv("PIPELINE_TIMEOUT", "30"))  # 30 seconds
    
    # Session management
    self.active_sessions: Dict[str, Dict[str, Any]] = {}
    self.session_cleanup_task = None
```

**Session Management Features:**
- **Session Tracking**: Track active voice sessions
- **Timeout Management**: Automatic session cleanup
- **Resource Limits**: Limit concurrent sessions
- **State Persistence**: Maintain session state across interactions

### **Pipeline Coordination**

The Voice Router implements **sophisticated pipeline coordination**:

```python
async def _process_voice_pipeline(self, audio_data: str, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Process voice through the complete pipeline."""
    try:
        # Create session
        session = self._create_session(session_id, audio_data, context)
        
        # Step 1: STT Processing
        stt_result = await self._process_stt(audio_data, session_id)
        if not stt_result:
            raise Exception("STT processing failed")
        
        # Step 2: AI Processing
        ai_result = await self._process_ai(stt_result["transcription"], session_id, context)
        if not ai_result:
            raise Exception("AI processing failed")
        
        # Step 3: TTS Processing
        tts_result = await self._process_tts(ai_result["text"], session_id, ai_result.get("voice_settings", {}))
        if not tts_result:
            raise Exception("TTS processing failed")
        
        # Step 4: Audio Output
        audio_result = await self._process_audio_output(tts_result["audio_data"], session_id)
        
        # Update session
        session["status"] = "completed"
        session["result"] = {
            "transcription": stt_result["transcription"],
            "ai_response": ai_result["text"],
            "audio_output": audio_result
        }
        
        return session["result"]
        
    except Exception as e:
        self.logger.error(f"Voice pipeline processing failed: {e}")
        # Update session with error
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "error"
            self.active_sessions[session_id]["error"] = str(e)
        raise
```

**Pipeline Coordination Features:**
- **Sequential Processing**: Process steps in correct order
- **Error Handling**: Handle failures at each step
- **State Tracking**: Track progress through pipeline
- **Result Aggregation**: Combine results from all steps

## 🔄 **Asynchronous Processing Architecture**

### **Queue-Based Processing**

The TTS service uses **asynchronous queue processing** for scalability:

```python
def __init__(self):
    # Processing queue
    self.processing_queue = asyncio.Queue()
    self.is_processing = False
    
    # Start processing loop
    asyncio.create_task(self._process_synthesis_queue())
```

**Queue Processing Benefits:**
- **Scalability**: Handle multiple synthesis requests concurrently
- **Resource Management**: Control processing load
- **Fault Tolerance**: Isolate processing errors
- **Performance**: Optimize resource utilization

### **Processing Queue Implementation**

The TTS service implements **efficient queue processing**:

```python
async def _process_synthesis_queue(self):
    """Process synthesis requests from the queue."""
    while True:
        try:
            # Get request from queue
            synthesis_request = await self.processing_queue.get()
            
            if synthesis_request is None:
                break
            
            # Process synthesis
            result = await self._synthesize_text(synthesis_request)
            
            # Publish result
            self._publish_synthesis_result(result)
            
        except Exception as e:
            self.logger.error(f"Synthesis processing error: {e}")
            await asyncio.sleep(1)
```

**Queue Processing Features:**
- **Continuous Processing**: Process requests continuously
- **Error Isolation**: Isolate errors to prevent queue blocking
- **Resource Optimization**: Optimize resource usage
- **Result Publishing**: Publish results to MQTT bus

## 📡 **MQTT Integration and Message Flow**

### **Voice Pipeline Message Flow**

The Voice Router coordinates **message flow** through the entire pipeline:

```python
def _setup_router_endpoints(self):
    """Setup FastAPI endpoints for voice router."""
    
    @self.api.app.post("/process-voice")
    async def process_voice_command(request: Dict[str, Any]):
        """Process a voice command through the complete pipeline."""
        try:
            audio_data = request.get("audio_data")
            session_id = request.get("session_id", str(uuid.uuid4()))
            context = request.get("context", {})
            
            if not audio_data:
                raise HTTPException(status_code=400, detail="Audio data is required")
            
            # Start voice processing pipeline
            result = await self._process_voice_pipeline(audio_data, session_id, context)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Voice processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")
```

**Message Flow Pattern:**
1. **Voice Input** → Voice Router
2. **STT Request** → STT Service
3. **STT Response** → Voice Router
4. **AI Request** → AI Service
5. **AI Response** → Voice Router
6. **TTS Request** → TTS Service
7. **TTS Response** → Voice Router
8. **Audio Output** → Speaker Services

### **Service Communication**

The Voice Router implements **sophisticated service communication**:

```python
async def _process_stt(self, audio_data: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Process audio through STT service."""
    try:
        # Create STT request
        stt_request = {
            "audio_data": audio_data,
            "session_id": session_id,
            "format": "wav",
            "language": "en-US"
        }
        
        # Publish STT request
        self.publish_message("alicia/voice/stt/request", stt_request)
        
        # Wait for STT response
        response = await self._wait_for_response("alicia/voice/stt/response", session_id, timeout=30)
        
        return response
        
    except Exception as e:
        self.logger.error(f"STT processing failed: {e}")
        return None
```

**Service Communication Features:**
- **Request Publishing**: Publish requests to appropriate services
- **Response Waiting**: Wait for responses with timeout
- **Error Handling**: Handle communication errors
- **Timeout Management**: Prevent hanging requests

## 🎵 **Audio Output Management**

### **Speaker Integration**

The Voice Router coordinates **audio output** to various speaker services:

```python
async def _process_audio_output(self, audio_data: str, session_id: str) -> Dict[str, Any]:
    """Process audio output to speakers."""
    try:
        # Determine target speakers
        target_speakers = self._determine_target_speakers(session_id)
        
        # Send audio to each speaker
        results = []
        for speaker in target_speakers:
            result = await self._send_audio_to_speaker(audio_data, speaker, session_id)
            results.append(result)
        
        return {
            "speakers_used": target_speakers,
            "results": results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        self.logger.error(f"Audio output processing failed: {e}")
        raise
```

**Audio Output Features:**
- **Multi-speaker Support**: Send audio to multiple speakers
- **Speaker Selection**: Choose appropriate speakers
- **Volume Control**: Control volume per speaker
- **Synchronization**: Synchronize audio across speakers

### **Sonos Integration**

The Voice Router integrates with **Sonos speakers** for high-quality audio:

```python
async def _send_audio_to_sonos(self, audio_data: str, speaker: str, session_id: str) -> Dict[str, Any]:
    """Send audio to Sonos speaker."""
    try:
        # Create Sonos audio request
        sonos_request = {
            "speaker_id": speaker,
            "audio_data": audio_data,
            "format": "wav",
            "volume": 50,
            "session_id": session_id
        }
        
        # Publish to Sonos service
        self.publish_message("alicia/devices/sonos/play_audio", sonos_request)
        
        # Wait for confirmation
        response = await self._wait_for_response("alicia/devices/sonos/audio_played", session_id, timeout=10)
        
        return response
        
    except Exception as e:
        self.logger.error(f"Sonos audio output failed: {e}")
        raise
```

**Sonos Integration Features:**
- **Multi-room Audio**: Play audio across multiple rooms
- **Volume Control**: Control volume per speaker
- **Audio Quality**: High-quality audio playback
- **Synchronization**: Synchronized playback across speakers

## 🚀 **Performance Optimization**

### **Pipeline Optimization**

The Voice Router implements **pipeline optimization** techniques:

```python
def _optimize_pipeline_performance(self, session_id: str) -> Dict[str, Any]:
    """Optimize pipeline performance for a session."""
    session = self.active_sessions.get(session_id)
    if not session:
        return {}
    
    # Analyze session performance
    performance_metrics = {
        "stt_latency": session.get("stt_latency", 0),
        "ai_latency": session.get("ai_latency", 0),
        "tts_latency": session.get("tts_latency", 0),
        "total_latency": session.get("total_latency", 0)
    }
    
    # Apply optimizations based on metrics
    optimizations = []
    
    if performance_metrics["stt_latency"] > 5.0:
        optimizations.append("Consider using faster STT model")
    
    if performance_metrics["ai_latency"] > 10.0:
        optimizations.append("Consider using faster AI model")
    
    if performance_metrics["tts_latency"] > 3.0:
        optimizations.append("Consider using faster TTS model")
    
    return {
        "metrics": performance_metrics,
        "optimizations": optimizations
    }
```

**Optimization Features:**
- **Latency Monitoring**: Track latency at each step
- **Performance Analysis**: Analyze performance bottlenecks
- **Optimization Suggestions**: Suggest performance improvements
- **Adaptive Processing**: Adapt processing based on performance

### **Caching and Response Optimization**

The TTS service implements **intelligent caching**:

```python
def _get_cached_audio(self, text: str, voice_settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get cached audio if available."""
    cache_key = self._generate_audio_cache_key(text, voice_settings)
    
    if cache_key in self.audio_cache:
        cached_audio = self.audio_cache[cache_key]
        
        # Check if cache is still valid
        if time.time() - cached_audio["timestamp"] < self.audio_cache_ttl:
            self.logger.debug(f"Using cached audio for: {text[:50]}...")
            return cached_audio["audio"]
    
    return None
```

**Caching Features:**
- **Audio Caching**: Cache generated audio
- **TTL Management**: Time-to-live for cache entries
- **Voice Settings**: Consider voice settings in caching
- **Memory Management**: Limit cache size

## 🔧 **Error Handling and Recovery**

### **Pipeline Error Handling**

The Voice Router implements **comprehensive error handling**:

```python
async def _handle_pipeline_error(self, error: Exception, session_id: str, step: str):
    """Handle pipeline errors gracefully."""
    self.logger.error(f"Pipeline error in {step}: {error}")
    
    # Update session with error
    if session_id in self.active_sessions:
        self.active_sessions[session_id]["status"] = "error"
        self.active_sessions[session_id]["error"] = str(error)
        self.active_sessions[session_id]["error_step"] = step
    
    # Attempt recovery based on error type
    if "timeout" in str(error).lower():
        await self._retry_pipeline_step(session_id, step)
    elif "connection" in str(error).lower():
        await self._reconnect_services()
    else:
        await self._fallback_processing(session_id, step)
```

**Error Handling Features:**
- **Error Classification**: Classify errors by type
- **Recovery Strategies**: Different recovery strategies for different errors
- **Fallback Processing**: Use alternative processing methods
- **Service Reconnection**: Reconnect to failed services

### **Service Health Monitoring**

The Voice Router monitors **service health** throughout the pipeline:

```python
def _monitor_service_health(self, service_name: str) -> bool:
    """Monitor health of a specific service."""
    try:
        # Check service health via MQTT
        health_topic = f"alicia/system/health/{service_name}"
        
        # Publish health check request
        self.publish_message("alicia/system/health/check", {
            "service_name": service_name,
            "timestamp": time.time()
        })
        
        # Wait for health response
        response = self._wait_for_response(health_topic, timeout=5)
        
        return response.get("status") == "healthy"
        
    except Exception as e:
        self.logger.error(f"Health check failed for {service_name}: {e}")
        return False
```

**Health Monitoring Features:**
- **Service Health Checks**: Check health of all services
- **Automatic Recovery**: Automatically recover from service failures
- **Health Reporting**: Report service health status
- **Load Balancing**: Distribute load across healthy services

## 🚀 **Next Steps**

The TTS Service and Voice Router complete Alicia's voice processing pipeline. In the next chapter, we'll examine the **Device Integration Services** that handle smart home device control, including:

1. **Device Manager & Control Services** - Centralized device management
2. **Home Assistant Bridge** - Integration with Home Assistant
3. **Sonos Integration** - Multi-room audio control
4. **Device Discovery** - Automatic device discovery and registration
5. **Device State Management** - Real-time device state tracking

The voice pipeline demonstrates how **sophisticated audio processing** can be orchestrated through a microservices architecture, providing seamless voice interaction that scales with the system.

---

**The TTS Service and Voice Router in Alicia represent a mature, production-ready approach to voice pipeline orchestration. Every design decision is intentional, every integration pattern serves a purpose, and every optimization contributes to the greater goal of creating a responsive, reliable, and engaging voice assistant.**
