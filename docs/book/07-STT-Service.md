# Chapter 7: STT Service Implementation

## 🎯 **Speech-to-Text Architecture Overview**

The STT (Speech-to-Text) Service is the first component in Alicia's voice processing pipeline. It converts audio input into text that can be processed by the AI service. This chapter analyzes the STT service implementation, examining its multi-engine architecture, audio processing pipeline, and integration with the broader voice system.

## 🏗️ **Multi-Engine Architecture**

### **Engine Selection Strategy**

Alicia's STT service implements a **multi-engine architecture** that supports multiple speech-to-text providers:

```python
class STTService(BusServiceWrapper):
    """
    STT Service for the Alicia bus architecture.
    
    Handles speech-to-text processing with multiple engine support:
    - OpenAI Whisper (primary)
    - Google Speech-to-Text (fallback)
    - Azure Speech Services (enterprise)
    """
```

**Why Multiple Engines?**

1. **Reliability**: If one engine fails, others can take over
2. **Performance**: Different engines excel at different use cases
3. **Cost Optimization**: Use cheaper engines for simple tasks
4. **Language Support**: Different engines support different languages
5. **Quality**: Choose the best engine for specific audio characteristics

### **Engine Configuration**

The STT service uses **environment-based configuration** to select the appropriate engine:

```python
def __init__(self):
    # STT Configuration
    self.stt_engine = os.getenv("STT_ENGINE", "whisper")  # whisper, google, azure
    self.model_size = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
    self.language = os.getenv("STT_LANGUAGE", "en")  # auto for auto-detection
    self.max_audio_length = int(os.getenv("MAX_AUDIO_LENGTH", "30"))  # seconds
    self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
```

**Configuration Benefits:**
- **Runtime Selection**: Change engines without code changes
- **Model Optimization**: Choose appropriate model size for performance
- **Language Flexibility**: Support multiple languages
- **Quality Control**: Set confidence thresholds for accuracy

## 🎤 **Whisper Integration (Primary Engine)**

### **Whisper Model Loading**

The STT service uses **OpenAI Whisper** as its primary engine due to its excellent accuracy and open-source nature:

```python
def _setup_whisper(self):
    """Setup OpenAI Whisper model."""
    try:
        import whisper
        self.logger.info(f"Loading Whisper model: {self.model_size}")
        self.whisper_model = whisper.load_model(self.model_size)
        self.logger.info("Whisper model loaded successfully")
    except ImportError:
        self.logger.error("Whisper not installed. Install with: pip install openai-whisper")
        raise
    except Exception as e:
        self.logger.error(f"Failed to load Whisper model: {e}")
        raise
```

**Whisper Model Sizes:**
- **tiny**: Fastest, lowest accuracy (~39 MB)
- **base**: Good balance of speed and accuracy (~74 MB)
- **small**: Better accuracy, slower (~244 MB)
- **medium**: High accuracy, slower (~769 MB)
- **large**: Highest accuracy, slowest (~1550 MB)

**Why Whisper?**
- **Open Source**: No API costs or rate limits
- **High Accuracy**: State-of-the-art speech recognition
- **Multi-language**: Supports 99+ languages
- **Offline Processing**: No internet connection required
- **Customizable**: Can be fine-tuned for specific use cases

### **Audio Processing Pipeline**

The STT service implements a **sophisticated audio processing pipeline**:

```python
async def _process_audio_queue(self):
    """Process audio from the queue."""
    while True:
        try:
            # Get audio from queue
            audio_request = await self.processing_queue.get()
            
            if audio_request is None:
                break
            
            # Process audio
            result = await self._transcribe_audio(audio_request)
            
            # Publish result
            self._publish_transcription_result(result)
            
        except Exception as e:
            self.logger.error(f"Audio processing error: {e}")
            await asyncio.sleep(1)
```

**Audio Processing Steps:**

1. **Queue Management**: Audio requests are queued for processing
2. **Format Validation**: Ensure audio is in supported format
3. **Preprocessing**: Normalize audio levels and remove noise
4. **Transcription**: Convert audio to text using selected engine
5. **Post-processing**: Apply confidence scoring and filtering
6. **Result Publishing**: Send transcription to MQTT bus

### **Audio Format Handling**

The STT service supports **multiple audio formats** with automatic conversion:

```python
def _preprocess_audio(self, audio_data: str, format: str = "wav") -> np.ndarray:
    """Preprocess audio data for transcription."""
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        # Load audio using librosa or similar
        import librosa
        audio_array, sample_rate = librosa.load(temp_file_path, sr=16000)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return audio_array, sample_rate
        
    except Exception as e:
        self.logger.error(f"Audio preprocessing failed: {e}")
        raise
```

**Supported Audio Formats:**
- **WAV**: Uncompressed, high quality
- **MP3**: Compressed, smaller file size
- **FLAC**: Lossless compression
- **OGG**: Open source compressed format
- **M4A**: Apple's compressed format

**Audio Processing Features:**
- **Sample Rate Conversion**: Convert to 16kHz for Whisper
- **Mono Conversion**: Convert stereo to mono
- **Noise Reduction**: Basic noise filtering
- **Volume Normalization**: Ensure consistent audio levels

## 🔄 **Fallback Engine Support**

### **Google Speech-to-Text Integration**

The STT service includes **Google Cloud Speech-to-Text** as a fallback option:

```python
def _setup_google(self):
    """Setup Google Speech-to-Text client."""
    try:
        from google.cloud import speech
        self.google_client = speech.SpeechClient()
        self.logger.info("Google Speech client initialized")
    except ImportError:
        self.logger.warning("Google Cloud Speech not available")
    except Exception as e:
        self.logger.error(f"Failed to setup Google Speech: {e}")
```

**Google Speech Benefits:**
- **Cloud Processing**: Offloads processing to Google's servers
- **High Accuracy**: Excellent recognition quality
- **Real-time Streaming**: Supports streaming audio
- **Language Detection**: Automatic language identification
- **Custom Models**: Can be trained on specific vocabularies

### **Azure Speech Services Integration**

The STT service also supports **Azure Speech Services** for enterprise deployments:

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
- **Batch Processing**: Process large audio files
- **Multi-language**: Support for 100+ languages
- **Integration**: Easy integration with Microsoft services

## 📊 **Quality Assessment and Confidence Scoring**

### **Confidence Threshold Implementation**

The STT service implements **confidence-based quality control**:

```python
def _assess_transcription_quality(self, transcription: str, confidence: float) -> Dict[str, Any]:
    """Assess the quality of a transcription."""
    quality_score = confidence
    
    # Adjust quality based on transcription characteristics
    if len(transcription) < 3:
        quality_score *= 0.5  # Very short transcriptions are less reliable
    
    if transcription.count(" ") < 1:
        quality_score *= 0.7  # Single words are less reliable
    
    # Check for common transcription errors
    error_indicators = ["[inaudible]", "[unclear]", "???"]
    if any(indicator in transcription.lower() for indicator in error_indicators):
        quality_score *= 0.3
    
    return {
        "quality_score": quality_score,
        "confidence": confidence,
        "is_high_quality": quality_score > self.confidence_threshold,
        "transcription": transcription
    }
```

**Quality Assessment Factors:**
- **Confidence Score**: Engine-provided confidence level
- **Transcription Length**: Longer transcriptions are generally more reliable
- **Word Count**: Multi-word transcriptions are more reliable
- **Error Indicators**: Detect common transcription errors
- **Audio Quality**: Consider source audio characteristics

### **Result Filtering and Validation**

The STT service implements **intelligent result filtering**:

```python
def _filter_transcription_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Filter transcription results based on quality criteria."""
    quality = result.get("quality", {})
    
    # Reject low-quality transcriptions
    if not quality.get("is_high_quality", False):
        self.logger.warning(f"Low quality transcription rejected: {result.get('transcription', '')}")
        return None
    
    # Reject empty or very short transcriptions
    transcription = result.get("transcription", "").strip()
    if len(transcription) < 2:
        self.logger.warning("Empty or very short transcription rejected")
        return None
    
    # Reject transcriptions with too many errors
    if quality.get("quality_score", 0) < 0.3:
        self.logger.warning("Transcription with too many errors rejected")
        return None
    
    return result
```

## 🔄 **Asynchronous Processing Architecture**

### **Queue-Based Processing**

The STT service uses **asynchronous queue processing** for scalability:

```python
def __init__(self):
    # Processing queue
    self.processing_queue = asyncio.Queue()
    self.is_processing = False
    
    # Start processing loop
    asyncio.create_task(self._process_audio_queue())
```

**Queue Processing Benefits:**
- **Scalability**: Handle multiple audio requests concurrently
- **Resource Management**: Control processing load
- **Fault Tolerance**: Isolate processing errors
- **Performance**: Optimize resource utilization

### **Session Management**

The STT service implements **session-based processing** for voice interactions:

```python
def _create_processing_session(self, audio_request: Dict[str, Any]) -> str:
    """Create a new processing session."""
    session_id = str(uuid.uuid4())
    
    session_data = {
        "session_id": session_id,
        "created_at": time.time(),
        "audio_request": audio_request,
        "status": "processing",
        "steps_completed": [],
        "result": None
    }
    
    self.active_sessions[session_id] = session_data
    return session_id
```

**Session Management Features:**
- **Unique Identifiers**: Each session has a unique ID
- **Status Tracking**: Track processing status
- **Step Logging**: Log completed processing steps
- **Result Storage**: Store final transcription results
- **Cleanup**: Automatic session cleanup

## 📡 **MQTT Integration and Message Publishing**

### **Transcription Result Publishing**

The STT service publishes **standardized transcription results**:

```python
def _publish_transcription_result(self, result: Dict[str, Any]):
    """Publish transcription result to MQTT bus."""
    try:
        # Create standardized message
        message = {
            "request_id": result.get("request_id"),
            "session_id": result.get("session_id"),
            "transcription": result.get("transcription"),
            "confidence": result.get("confidence"),
            "quality": result.get("quality"),
            "language": result.get("language"),
            "processing_time": result.get("processing_time"),
            "engine_used": result.get("engine_used"),
            "timestamp": time.time()
        }
        
        # Publish to STT response topic
        self.publish_message("alicia/voice/stt/response", message)
        
        # Publish to AI service for processing
        self.publish_message("alicia/voice/ai/request", {
            "text": result.get("transcription"),
            "session_id": result.get("session_id"),
            "context": result.get("context", {})
        })
        
    except Exception as e:
        self.logger.error(f"Failed to publish transcription result: {e}")
```

**Message Publishing Features:**
- **Standardized Format**: Consistent message structure
- **Multiple Topics**: Publish to different consumers
- **Context Preservation**: Maintain session context
- **Error Handling**: Graceful error handling

### **Health Monitoring Integration**

The STT service integrates with **Alicia's health monitoring system**:

```python
def publish_health_status(self):
    """Publish current health status."""
    health_status = {
        "service_name": self.service_name,
        "status": "healthy" if self.is_processing else "unhealthy",
        "uptime": time.time() - self.start_time,
        "messages_processed": self.message_count,
        "errors": self.error_count,
        "active_sessions": len(self.active_sessions),
        "queue_size": self.processing_queue.qsize(),
        "engine_status": {
            "whisper": self.whisper_model is not None,
            "google": self.google_client is not None,
            "azure": self.azure_client is not None
        },
        "timestamp": time.time()
    }
    
    self.publish_message(
        f"alicia/system/health/{self.service_name}",
        health_status
    )
```

## 🚀 **Performance Optimization**

### **Model Loading Optimization**

The STT service implements **efficient model loading**:

```python
def _setup_whisper(self):
    """Setup OpenAI Whisper model with optimization."""
    try:
        import whisper
        
        # Load model with optimization
        self.whisper_model = whisper.load_model(
            self.model_size,
            device="cpu",  # Use CPU for consistency
            download_root="/app/models"  # Cache models
        )
        
        # Pre-warm the model
        self._prewarm_model()
        
        self.logger.info("Whisper model loaded and optimized")
    except Exception as e:
        self.logger.error(f"Failed to load Whisper model: {e}")
        raise
```

**Optimization Techniques:**
- **Model Caching**: Cache models to avoid re-downloading
- **Pre-warming**: Initialize model before first use
- **Device Selection**: Choose appropriate compute device
- **Memory Management**: Optimize memory usage

### **Audio Processing Optimization**

The STT service implements **efficient audio processing**:

```python
def _optimize_audio_for_transcription(self, audio_array: np.ndarray) -> np.ndarray:
    """Optimize audio for transcription."""
    # Normalize audio
    audio_array = audio_array / np.max(np.abs(audio_array))
    
    # Apply noise reduction (basic)
    audio_array = self._apply_noise_reduction(audio_array)
    
    # Trim silence
    audio_array = self._trim_silence(audio_array)
    
    return audio_array
```

**Audio Optimization Features:**
- **Normalization**: Ensure consistent audio levels
- **Noise Reduction**: Remove background noise
- **Silence Trimming**: Remove leading/trailing silence
- **Format Optimization**: Convert to optimal format

## 🔧 **Error Handling and Recovery**

### **Engine Fallback Implementation**

The STT service implements **automatic engine fallback**:

```python
async def _transcribe_with_fallback(self, audio_data: str, format: str = "wav") -> Dict[str, Any]:
    """Transcribe audio with automatic fallback."""
    engines = [self.stt_engine, "google", "azure"]
    
    for engine in engines:
        try:
            if engine == "whisper" and self.whisper_model:
                return await self._transcribe_with_whisper(audio_data, format)
            elif engine == "google" and self.google_client:
                return await self._transcribe_with_google(audio_data, format)
            elif engine == "azure" and self.azure_client:
                return await self._transcribe_with_azure(audio_data, format)
        except Exception as e:
            self.logger.warning(f"Engine {engine} failed: {e}")
            continue
    
    raise Exception("All STT engines failed")
```

**Fallback Benefits:**
- **High Availability**: System continues working if one engine fails
- **Quality Assurance**: Use best available engine
- **Cost Optimization**: Use cheaper engines when appropriate
- **Load Distribution**: Distribute load across engines

### **Error Recovery and Retry Logic**

The STT service implements **sophisticated error recovery**:

```python
async def _transcribe_audio_with_retry(self, audio_request: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    """Transcribe audio with retry logic."""
    for attempt in range(max_retries):
        try:
            result = await self._transcribe_audio(audio_request)
            return result
        except Exception as e:
            self.logger.warning(f"Transcription attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise Exception(f"Transcription failed after {max_retries} attempts: {e}")
```

## 🚀 **Next Steps**

The STT Service provides the foundation for Alicia's voice processing pipeline. In the next chapter, we'll examine the **AI Service & Grok Integration** that processes the transcribed text, including:

1. **Natural Language Processing** - Understanding user intent and commands
2. **Grok API Integration** - Advanced AI conversation management
3. **Context Management** - Maintaining conversation history and context
4. **Smart Home Command Processing** - Converting natural language to device commands
5. **Response Generation** - Creating appropriate responses for TTS synthesis

The STT service demonstrates how **sophisticated audio processing** can be integrated into a microservices architecture, providing reliable, high-quality speech-to-text conversion that scales with the system.

---

**The STT Service in Alicia represents a mature, production-ready approach to speech-to-text processing. Every design decision is intentional, every optimization serves a purpose, and every integration pattern contributes to the greater goal of creating a reliable, scalable, and maintainable voice processing pipeline.**
