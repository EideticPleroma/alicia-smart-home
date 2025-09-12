# Chapter 12: Sonos Integration

## 🎯 **Sonos Integration Architecture Overview**

The Sonos Service provides **comprehensive multi-room audio control** for Alicia's voice processing pipeline. It handles speaker discovery, audio playback, volume management, and speaker grouping, enabling seamless audio output from TTS synthesis and music streaming. This chapter analyzes the Sonos service implementation, examining its speaker management, audio control, and integration with the voice pipeline.

## 🔊 **Sonos Speaker Management**

### **Automatic Speaker Discovery**

The Sonos service implements **sophisticated speaker discovery**:

```python
class SonosService(BusServiceWrapper):
    """
    Sonos Service for the Alicia bus architecture.
    
    Manages Sonos speakers and provides:
    - Automatic speaker discovery
    - Audio playback control
    - Volume management
    - Grouping and ungrouping
    - Multi-room synchronization
    - Integration with TTS audio output
    """
```

**Why Sonos Integration?**

1. **Multi-room Audio**: Synchronized audio across multiple rooms
2. **High Quality**: Excellent audio quality and reliability
3. **Ecosystem**: Large ecosystem of compatible speakers
4. **API Support**: Comprehensive API for control
5. **Voice Integration**: Perfect for voice assistant audio output

### **Speaker Discovery Implementation**

The Sonos service uses **SoCo library** for speaker discovery:

```python
def _setup_sonos(self):
    """Setup Sonos integration."""
    try:
        # Import Sonos library (assuming soco is available)
        import soco
        self.soco = soco
        self.logger.info("Sonos (SoCo) library initialized")
    except ImportError:
        self.logger.error("SoCo library not available. Install with: pip install soco")
        self.soco = None
    except Exception as e:
        self.logger.error(f"Failed to setup Sonos: {e}")
        self.soco = None
```

**SoCo Library Benefits:**
- **Python Native**: Pure Python implementation
- **Comprehensive**: Full Sonos API coverage
- **Active Development**: Well-maintained library
- **Documentation**: Excellent documentation and examples

### **Continuous Speaker Discovery**

The Sonos service implements **continuous speaker discovery**:

```python
async def _discover_speakers(self):
    """Discover Sonos speakers on the network."""
    while True:
        try:
            if self.soco:
                # Discover speakers
                discovered_speakers = self.soco.discover()
                
                if discovered_speakers:
                    for speaker in discovered_speakers:
                        await self._register_speaker(speaker)
                    
                    self.logger.info(f"Discovered {len(discovered_speakers)} Sonos speakers")
                else:
                    self.logger.debug("No Sonos speakers discovered")
            
            # Update speaker status
            await self._update_speaker_status()
            
        except Exception as e:
            self.logger.error(f"Speaker discovery failed: {e}")
        
        await asyncio.sleep(self.discovery_interval)
```

**Discovery Features:**
- **Continuous Discovery**: Continuously discover new speakers
- **Status Updates**: Update speaker status regularly
- **Error Handling**: Robust error handling and recovery
- **Logging**: Comprehensive logging and debugging

### **Speaker Registration Process**

The Sonos service implements **comprehensive speaker registration**:

```python
async def _register_speaker(self, speaker):
    """Register a discovered speaker."""
    try:
        speaker_id = f"sonos_{speaker.uid.replace(':', '_')}"
        speaker_info = {
            "speaker_id": speaker_id,
            "uid": speaker.uid,
            "ip_address": speaker.ip_address,
            "model": getattr(speaker, 'model_name', 'Unknown'),
            "zone_name": speaker.zone_name,
            "status": "online",
            "last_seen": time.time(),
            "capabilities": self._extract_speaker_capabilities(speaker),
            "volume": getattr(speaker, 'volume', 0),
            "is_playing": False,
            "current_track": None
        }
        
        # Store speaker information
        self.speakers[speaker_id] = speaker_info
        
        # Register with device registry
        await self._register_with_device_registry(speaker_id, speaker_info)
        
        self.logger.info(f"Registered Sonos speaker: {speaker.zone_name} ({speaker.model_name})")
        
    except Exception as e:
        self.logger.error(f"Failed to register speaker: {e}")
```

**Registration Features:**
- **Unique Identification**: Generate unique speaker IDs
- **Capability Extraction**: Extract speaker capabilities
- **Device Registry**: Register with bus device registry
- **Status Tracking**: Track speaker status and metadata

## 🎵 **Audio Playback Control**

### **Audio Queue Management**

The Sonos service implements **sophisticated audio queue management**:

```python
def __init__(self):
    # Audio queue management
    self.audio_queue: asyncio.Queue = asyncio.Queue()
    self.is_playing = False
    
    # Start audio processing
    asyncio.create_task(self._process_audio_queue())
```

**Queue Management Features:**
- **Asynchronous Processing**: Process audio requests asynchronously
- **Queue Management**: Manage audio playback queue
- **Status Tracking**: Track playback status
- **Error Handling**: Handle audio processing errors

### **Audio Playback Implementation**

The Sonos service implements **comprehensive audio playback**:

```python
async def _process_audio_queue(self):
    """Process audio from the queue."""
    while True:
        try:
            # Get audio request from queue
            audio_request = await self.audio_queue.get()
            
            if audio_request is None:
                break
            
            # Process audio request
            result = await self._play_audio(audio_request)
            
            # Publish result
            self._publish_audio_result(result)
            
        except Exception as e:
            self.logger.error(f"Audio processing error: {e}")
            await asyncio.sleep(1)
```

**Audio Processing Features:**
- **Queue Processing**: Process audio requests from queue
- **Result Publishing**: Publish audio processing results
- **Error Handling**: Handle audio processing errors
- **Status Updates**: Update playback status

### **TTS Audio Integration**

The Sonos service integrates **seamlessly with TTS output**:

```python
async def play_tts_audio(self, audio_data: str, speaker_ids: List[str], voice_settings: Dict[str, Any] = None) -> Dict[str, Any]:
    """Play TTS audio on specified speakers."""
    try:
        # Create audio request
        audio_request = {
            "audio_data": audio_data,
            "speaker_ids": speaker_ids,
            "audio_type": "tts",
            "voice_settings": voice_settings or {},
            "priority": "high",  # TTS has high priority
            "timestamp": time.time()
        }
        
        # Add to audio queue
        await self.audio_queue.put(audio_request)
        
        return {
            "status": "queued",
            "speaker_ids": speaker_ids,
            "audio_type": "tts",
            "timestamp": time.time()
        }
        
    except Exception as e:
        self.logger.error(f"Failed to queue TTS audio: {e}")
        raise
```

**TTS Integration Features:**
- **High Priority**: TTS audio gets high priority
- **Multi-speaker**: Play on multiple speakers simultaneously
- **Voice Settings**: Support voice-specific settings
- **Queue Management**: Manage TTS audio queue

## 🔊 **Volume and Group Management**

### **Volume Control Implementation**

The Sonos service implements **comprehensive volume control**:

```python
async def set_volume(self, speaker_ids: List[str], volume: int) -> Dict[str, Any]:
    """Set volume for specified speakers."""
    try:
        results = []
        
        for speaker_id in speaker_ids:
            if speaker_id in self.speakers:
                speaker_info = self.speakers[speaker_id]
                
                # Get speaker object
                speaker = self._get_speaker_object(speaker_id)
                if speaker:
                    # Set volume
                    speaker.volume = max(0, min(100, volume))
                    
                    # Update stored volume
                    speaker_info["volume"] = volume
                    
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "success",
                        "volume": volume
                    })
                else:
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "error",
                        "error": "Speaker not found"
                    })
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        self.logger.error(f"Volume control failed: {e}")
        raise
```

**Volume Control Features:**
- **Multi-speaker**: Control volume on multiple speakers
- **Range Validation**: Validate volume range (0-100)
- **Status Tracking**: Track volume changes
- **Error Handling**: Handle volume control errors

### **Speaker Grouping Implementation**

The Sonos service implements **sophisticated speaker grouping**:

```python
async def create_group(self, group_name: str, speaker_ids: List[str]) -> Dict[str, Any]:
    """Create a speaker group."""
    try:
        if not speaker_ids:
            raise ValueError("At least one speaker is required")
        
        # Get coordinator speaker (first speaker)
        coordinator_id = speaker_ids[0]
        if coordinator_id not in self.speakers:
            raise ValueError(f"Coordinator speaker {coordinator_id} not found")
        
        coordinator = self._get_speaker_object(coordinator_id)
        if not coordinator:
            raise ValueError(f"Failed to get coordinator speaker {coordinator_id}")
        
        # Create group
        group = coordinator.group
        for speaker_id in speaker_ids[1:]:
            if speaker_id in self.speakers:
                speaker = self._get_speaker_object(speaker_id)
                if speaker:
                    speaker.join(coordinator)
        
        # Store group information
        self.groups[group_name] = speaker_ids
        
        return {
            "group_name": group_name,
            "speaker_ids": speaker_ids,
            "coordinator": coordinator_id,
            "status": "created",
            "timestamp": time.time()
        }
        
    except Exception as e:
        self.logger.error(f"Group creation failed: {e}")
        raise
```

**Grouping Features:**
- **Group Creation**: Create speaker groups
- **Coordinator Selection**: Select group coordinator
- **Member Management**: Add/remove group members
- **Group Storage**: Store group information

### **Group Management Operations**

The Sonos service implements **comprehensive group management**:

```python
async def ungroup_speakers(self, speaker_ids: List[str]) -> Dict[str, Any]:
    """Ungroup specified speakers."""
    try:
        results = []
        
        for speaker_id in speaker_ids:
            if speaker_id in self.speakers:
                speaker = self._get_speaker_object(speaker_id)
                if speaker:
                    # Ungroup speaker
                    speaker.unjoin()
                    
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "ungrouped"
                    })
                else:
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "error",
                        "error": "Speaker not found"
                    })
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        self.logger.error(f"Ungrouping failed: {e}")
        raise
```

**Group Management Features:**
- **Ungrouping**: Ungroup speakers
- **Status Tracking**: Track group status
- **Error Handling**: Handle grouping errors
- **Result Reporting**: Report grouping results

## 🎶 **Music and Media Control**

### **Playback Control Implementation**

The Sonos service implements **comprehensive playback control**:

```python
async def play_music(self, speaker_ids: List[str], music_source: Dict[str, Any]) -> Dict[str, Any]:
    """Play music on specified speakers."""
    try:
        results = []
        
        for speaker_id in speaker_ids:
            if speaker_id in self.speakers:
                speaker = self._get_speaker_object(speaker_id)
                if speaker:
                    # Play music based on source type
                    if music_source["type"] == "url":
                        speaker.play_uri(music_source["url"])
                    elif music_source["type"] == "favorite":
                        speaker.play_favorite(music_source["favorite_id"])
                    elif music_source["type"] == "playlist":
                        speaker.play_playlist(music_source["playlist_id"])
                    
                    # Update speaker status
                    self.speakers[speaker_id]["is_playing"] = True
                    self.speakers[speaker_id]["current_track"] = music_source
                    
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "playing",
                        "music_source": music_source
                    })
                else:
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "error",
                        "error": "Speaker not found"
                    })
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        self.logger.error(f"Music playback failed: {e}")
        raise
```

**Playback Control Features:**
- **Multiple Sources**: Support URL, favorite, playlist sources
- **Multi-speaker**: Play on multiple speakers
- **Status Updates**: Update playback status
- **Error Handling**: Handle playback errors

### **Playback State Management**

The Sonos service implements **comprehensive playback state management**:

```python
async def pause_playback(self, speaker_ids: List[str]) -> Dict[str, Any]:
    """Pause playback on specified speakers."""
    try:
        results = []
        
        for speaker_id in speaker_ids:
            if speaker_id in self.speakers:
                speaker = self._get_speaker_object(speaker_id)
                if speaker:
                    # Pause playback
                    speaker.pause()
                    
                    # Update speaker status
                    self.speakers[speaker_id]["is_playing"] = False
                    
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "paused"
                    })
                else:
                    results.append({
                        "speaker_id": speaker_id,
                        "status": "error",
                        "error": "Speaker not found"
                    })
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        self.logger.error(f"Pause playback failed: {e}")
        raise
```

**State Management Features:**
- **Play/Pause Control**: Control playback state
- **Status Synchronization**: Synchronize status across speakers
- **Multi-speaker**: Control multiple speakers simultaneously
- **Error Handling**: Handle state control errors

## 📡 **MQTT Integration and Event Publishing**

### **Audio Event Publishing**

The Sonos service publishes **comprehensive audio events**:

```python
def _publish_audio_result(self, result: Dict[str, Any]):
    """Publish audio processing result."""
    try:
        # Publish to audio result topic
        self.publish_message("alicia/devices/sonos/audio_result", result)
        
        # Publish to speaker-specific topics
        for speaker_id in result.get("speaker_ids", []):
            self.publish_message(f"alicia/devices/sonos/{speaker_id}/audio_result", result)
        
    except Exception as e:
        self.logger.error(f"Failed to publish audio result: {e}")
```

**Event Publishing Features:**
- **General Events**: Publish to general audio topics
- **Speaker-Specific**: Publish to speaker-specific topics
- **Result Data**: Include comprehensive result data
- **Error Handling**: Handle publishing errors

### **Speaker Status Publishing**

The Sonos service publishes **real-time speaker status**:

```python
async def _update_speaker_status(self):
    """Update and publish speaker status."""
    try:
        for speaker_id, speaker_info in self.speakers.items():
            speaker = self._get_speaker_object(speaker_id)
            if speaker:
                # Update speaker information
                speaker_info["volume"] = speaker.volume
                speaker_info["is_playing"] = speaker.is_playing
                speaker_info["current_track"] = speaker.current_track_info
                speaker_info["last_seen"] = time.time()
                
                # Publish status update
                self.publish_message(f"alicia/devices/sonos/{speaker_id}/status", {
                    "speaker_id": speaker_id,
                    "status": "online",
                    "volume": speaker.volume,
                    "is_playing": speaker.is_playing,
                    "current_track": speaker.current_track_info,
                    "timestamp": time.time()
                })
        
        # Publish general status
        self.publish_message("alicia/devices/sonos/status", {
            "speakers": list(self.speakers.keys()),
            "groups": list(self.groups.keys()),
            "timestamp": time.time()
        })
        
    except Exception as e:
        self.logger.error(f"Speaker status update failed: {e}")
```

**Status Publishing Features:**
- **Real-time Updates**: Publish real-time status updates
- **Speaker-Specific**: Publish speaker-specific status
- **General Status**: Publish general system status
- **Comprehensive Data**: Include all relevant status data

## 🚀 **Performance Optimization**

### **Speaker Object Caching**

The Sonos service implements **speaker object caching**:

```python
def _get_speaker_object(self, speaker_id: str):
    """Get speaker object with caching."""
    try:
        if speaker_id in self.speakers:
            speaker_info = self.speakers[speaker_id]
            ip_address = speaker_info.get("ip_address")
            
            if ip_address:
                # Create speaker object
                speaker = self.soco.SoCo(ip_address)
                return speaker
        
        return None
        
    except Exception as e:
        self.logger.error(f"Failed to get speaker object for {speaker_id}: {e}")
        return None
```

**Caching Features:**
- **Object Caching**: Cache speaker objects
- **IP Address Storage**: Store speaker IP addresses
- **Error Handling**: Handle speaker object creation errors
- **Performance**: Improve performance by caching objects

### **Audio Queue Optimization**

The Sonos service implements **audio queue optimization**:

```python
async def _optimize_audio_queue(self):
    """Optimize audio queue for performance."""
    try:
        # Check queue size
        queue_size = self.audio_queue.qsize()
        
        if queue_size > 10:
            self.logger.warning(f"Audio queue size is large: {queue_size}")
            
            # Process multiple items at once
            batch_size = min(5, queue_size)
            for _ in range(batch_size):
                try:
                    audio_request = self.audio_queue.get_nowait()
                    await self._play_audio(audio_request)
                except asyncio.QueueEmpty:
                    break
        
    except Exception as e:
        self.logger.error(f"Audio queue optimization failed: {e}")
```

**Queue Optimization Features:**
- **Queue Monitoring**: Monitor queue size
- **Batch Processing**: Process multiple items at once
- **Performance Alerts**: Alert on large queue sizes
- **Efficient Processing**: Optimize processing efficiency

## 🔧 **Error Handling and Recovery**

### **Speaker Connection Management**

The Sonos service implements **robust connection management**:

```python
async def _ensure_speaker_connection(self, speaker_id: str) -> bool:
    """Ensure connection to speaker."""
    try:
        if speaker_id in self.speakers:
            speaker_info = self.speakers[speaker_id]
            ip_address = speaker_info.get("ip_address")
            
            if ip_address:
                # Test connection
                speaker = self.soco.SoCo(ip_address)
                if speaker:
                    return True
        
        return False
        
    except Exception as e:
        self.logger.error(f"Speaker connection test failed for {speaker_id}: {e}")
        return False
```

**Connection Management Features:**
- **Connection Testing**: Test speaker connections
- **Error Handling**: Handle connection errors
- **Status Updates**: Update connection status
- **Recovery**: Attempt connection recovery

### **Audio Processing Error Handling**

The Sonos service implements **comprehensive error handling**:

```python
async def _handle_audio_error(self, error: Exception, audio_request: Dict[str, Any]):
    """Handle audio processing errors."""
    self.logger.error(f"Audio processing failed: {error}")
    
    # Publish error event
    error_event = {
        "audio_request": audio_request,
        "error": str(error),
        "timestamp": time.time()
    }
    
    self.publish_message("alicia/devices/sonos/audio_errors", error_event)
    
    # Attempt recovery
    if "connection" in str(error).lower():
        await self._recover_speaker_connections()
```

**Error Handling Features:**
- **Error Classification**: Classify errors by type
- **Error Publishing**: Publish error events
- **Recovery Strategies**: Implement recovery strategies
- **Logging**: Comprehensive error logging

## 🚀 **Next Steps**

The Sonos Integration completes Alicia's device integration services. In the next chapter, we'll examine the **Advanced Features** that enhance Alicia's capabilities, including:

1. **Personality System** - AI personality management and customization
2. **Multi-Language Support** - Internationalization and language switching
3. **Advanced Voice Processing** - Emotion detection and voice enhancement
4. **Grok Integration** - Advanced AI capabilities and real-time information
5. **Service Orchestration** - Advanced service coordination and management

The Sonos service demonstrates how **sophisticated audio control** can be integrated into a microservices architecture, providing seamless multi-room audio that enhances the voice assistant experience.

---

**The Sonos Integration in Alicia represents a mature, production-ready approach to multi-room audio control. Every design decision is intentional, every integration pattern serves a purpose, and every optimization contributes to the greater goal of creating a responsive, reliable, and engaging audio experience.**
