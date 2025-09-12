"""
Alicia Bus Architecture - Advanced Voice Pipeline Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Advanced voice processing service that provides enhanced audio capabilities
with emotion detection, voice activity detection, noise reduction, and audio enhancement.
"""

import asyncio
import json
import logging
import os
import time
import uuid
from typing import Dict, Any, Optional, List

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
import uvicorn

from service_wrapper import BusServiceWrapper, BusServiceAPI


class AdvancedVoicePipeline(BusServiceWrapper):
    """
    Advanced Voice Pipeline service for the Alicia bus architecture.

    Provides advanced audio processing capabilities:
    - Voice activity detection (VAD)
    - Emotion recognition and analysis
    - Noise reduction and audio enhancement
    - Speaker diarization and identification
    - Audio quality assessment
    - Real-time audio preprocessing

    Features:
    - Real-time voice activity detection
    - Emotion analysis from speech patterns
    - Audio noise reduction algorithms
    - Speaker identification and diarization
    - Audio quality metrics and enhancement
    - Integration with voice pipeline
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "advanced_voice"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_voice_advanced_2024")
        }

        super().__init__("advanced_voice", mqtt_config)

        # Advanced Voice Configuration
        self.vad_sensitivity = float(os.getenv("VAD_SENSITIVITY", "0.5"))
        self.emotion_detection_enabled = os.getenv("EMOTION_DETECTION", "true").lower() == "true"
        self.noise_reduction_enabled = os.getenv("NOISE_REDUCTION", "true").lower() == "true"
        self.audio_quality_threshold = float(os.getenv("QUALITY_THRESHOLD", "0.7"))
        self.max_audio_length = int(os.getenv("MAX_AUDIO_LENGTH", "300"))  # seconds

        # Audio processing state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.audio_buffers: Dict[str, List[bytes]] = {}
        self.voice_activity_state: Dict[str, Dict[str, Any]] = {}
        self.emotion_analysis: Dict[str, Dict[str, Any]] = {}

        # Audio processing models (placeholders for actual ML models)
        self.vad_model = None
        self.emotion_model = None
        self.diarization_model = None

        # Setup audio processing
        self._setup_audio_processing()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_voice_endpoints()

        # Service capabilities
        self.capabilities = [
            "voice_activity_detection",
            "emotion_recognition",
            "noise_reduction",
            "audio_enhancement",
            "speaker_diarization",
            "audio_quality_assessment"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._process_audio_streams())
        asyncio.create_task(self._cleanup_expired_sessions())

        self.logger.info("Advanced Voice Pipeline initialized")

    def _setup_audio_processing(self):
        """Setup audio processing components."""
        try:
            # Initialize audio processing libraries (placeholders)
            # In real implementation, would load actual ML models
            self.logger.info("Audio processing components initialized")

        except Exception as e:
            self.logger.error(f"Error setting up audio processing: {e}")

    def _setup_voice_endpoints(self):
        """Setup FastAPI endpoints for advanced voice processing."""

        @self.api.app.post("/analyze-audio")
        async def analyze_audio(request: Dict[str, Any]):
            """Analyze audio for voice activity, emotion, and quality."""
            try:
                audio_data = request.get("audio_data")
                session_id = request.get("session_id")
                analysis_type = request.get("analysis_type", "full")  # vad, emotion, quality, full

                if not audio_data or not session_id:
                    raise HTTPException(status_code=400, detail="Audio data and session ID are required")

                # Analyze audio
                analysis_result = await self._analyze_audio(audio_data, session_id, analysis_type)

                return {
                    "session_id": session_id,
                    "analysis_type": analysis_type,
                    "analysis_result": analysis_result,
                    "timestamp": time.time()
                }

            except Exception as e:
                self.logger.error(f"Audio analysis error: {e}")
                raise HTTPException(status_code=500, detail=f"Audio analysis failed: {str(e)}")

        @self.api.app.post("/enhance-audio")
        async def enhance_audio(request: Dict[str, Any]):
            """Enhance audio quality with noise reduction."""
            try:
                audio_data = request.get("audio_data")
                session_id = request.get("session_id")
                enhancement_type = request.get("enhancement_type", "noise_reduction")

                if not audio_data or not session_id:
                    raise HTTPException(status_code=400, detail="Audio data and session ID are required")

                # Enhance audio
                enhanced_audio = await self._enhance_audio(audio_data, session_id, enhancement_type)

                return {
                    "session_id": session_id,
                    "enhancement_type": enhancement_type,
                    "enhanced_audio": enhanced_audio,
                    "original_length": len(audio_data),
                    "enhanced_length": len(enhanced_audio) if enhanced_audio else 0
                }

            except Exception as e:
                self.logger.error(f"Audio enhancement error: {e}")
                raise HTTPException(status_code=500, detail=f"Audio enhancement failed: {str(e)}")

        @self.api.app.post("/detect-speakers")
        async def detect_speakers(request: Dict[str, Any]):
            """Detect and identify speakers in audio."""
            try:
                audio_data = request.get("audio_data")
                session_id = request.get("session_id")
                num_speakers = request.get("num_speakers", "auto")

                if not audio_data or not session_id:
                    raise HTTPException(status_code=400, detail="Audio data and session ID are required")

                # Detect speakers
                speaker_result = await self._detect_speakers(audio_data, session_id, num_speakers)

                return {
                    "session_id": session_id,
                    "speaker_detection": speaker_result,
                    "num_speakers": num_speakers
                }

            except Exception as e:
                self.logger.error(f"Speaker detection error: {e}")
                raise HTTPException(status_code=500, detail=f"Speaker detection failed: {str(e)}")

        @self.api.app.get("/session/{session_id}/status")
        async def get_session_status(session_id: str):
            """Get status of audio processing session."""
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session_info = self.active_sessions[session_id]
            return {
                "session_id": session_id,
                "status": session_info.get("status"),
                "voice_activity": self.voice_activity_state.get(session_id, {}),
                "emotion_analysis": self.emotion_analysis.get(session_id, {}),
                "audio_buffer_size": len(self.audio_buffers.get(session_id, [])),
                "last_activity": session_info.get("last_activity")
            }

        @self.api.app.post("/session")
        async def create_session(request: Dict[str, Any]):
            """Create a new audio processing session."""
            try:
                session_config = request.get("config", {})
                session_id = f"voice_session_{uuid.uuid4().hex[:8]}"

                # Create session
                await self._create_audio_session(session_id, session_config)

                return {
                    "session_id": session_id,
                    "status": "created",
                    "config": session_config
                }

            except Exception as e:
                self.logger.error(f"Create session error: {e}")
                raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

        @self.api.app.get("/health")
        async def health_check():
            """Advanced voice pipeline health check."""
            return {
                "service": "advanced_voice",
                "status": "healthy" if self.is_connected else "unhealthy",
                "active_sessions": len(self.active_sessions),
                "vad_enabled": self.vad_sensitivity > 0,
                "emotion_detection": self.emotion_detection_enabled,
                "noise_reduction": self.noise_reduction_enabled,
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to voice-related MQTT topics."""
        topics = [
            "alicia/voice/stt/request",
            "alicia/voice/tts/request",
            "alicia/voice/audio/stream",
            "alicia/voice/session/start",
            "alicia/voice/session/end",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to advanced voice topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/voice/stt/request":
                self._handle_stt_request(message)
            elif topic == "alicia/voice/tts/request":
                self._handle_tts_request(message)
            elif topic == "alicia/voice/audio/stream":
                self._handle_audio_stream(message)
            elif topic == "alicia/voice/session/start":
                self._handle_session_start(message)
            elif topic == "alicia/voice/session/end":
                self._handle_session_end(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing voice message: {e}")

    def _handle_stt_request(self, message: Dict[str, Any]):
        """Handle STT requests for preprocessing."""
        try:
            payload = message.get("payload", {})
            audio_data = payload.get("audio_data")
            session_id = payload.get("session_id", "")

            if audio_data and session_id:
                # Preprocess audio for better STT
                asyncio.create_task(self._preprocess_audio_for_stt(audio_data, session_id))

        except Exception as e:
            self.logger.error(f"Error handling STT request: {e}")

    def _handle_tts_request(self, message: Dict[str, Any]):
        """Handle TTS requests for postprocessing."""
        try:
            payload = message.get("payload", {})
            text = payload.get("text", "")
            session_id = payload.get("session_id", "")

            if text and session_id:
                # Analyze text for emotion and style
                asyncio.create_task(self._analyze_text_for_tts(text, session_id))

        except Exception as e:
            self.logger.error(f"Error handling TTS request: {e}")

    def _handle_audio_stream(self, message: Dict[str, Any]):
        """Handle audio stream data."""
        try:
            payload = message.get("payload", {})
            audio_chunk = payload.get("audio_chunk")
            session_id = payload.get("session_id", "")
            sequence_number = payload.get("sequence_number", 0)

            if audio_chunk and session_id:
                # Process audio chunk
                asyncio.create_task(self._process_audio_chunk(audio_chunk, session_id, sequence_number))

        except Exception as e:
            self.logger.error(f"Error handling audio stream: {e}")

    def _handle_session_start(self, message: Dict[str, Any]):
        """Handle voice session start."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")
            session_config = payload.get("config", {})

            if session_id:
                # Initialize session
                asyncio.create_task(self._create_audio_session(session_id, session_config))

        except Exception as e:
            self.logger.error(f"Error handling session start: {e}")

    def _handle_session_end(self, message: Dict[str, Any]):
        """Handle voice session end."""
        try:
            payload = message.get("payload", {})
            session_id = payload.get("session_id", "")

            if session_id and session_id in self.active_sessions:
                # Cleanup session
                asyncio.create_task(self._cleanup_audio_session(session_id))

        except Exception as e:
            self.logger.error(f"Error handling session end: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _analyze_audio(self, audio_data: bytes, session_id: str,
                           analysis_type: str = "full") -> Dict[str, Any]:
        """Analyze audio for various characteristics."""
        try:
            analysis_result = {}

            # Voice Activity Detection
            if analysis_type in ["vad", "full"]:
                vad_result = await self._detect_voice_activity(audio_data, session_id)
                analysis_result["voice_activity"] = vad_result

            # Emotion Analysis
            if analysis_type in ["emotion", "full"] and self.emotion_detection_enabled:
                emotion_result = await self._analyze_emotion(audio_data, session_id)
                analysis_result["emotion"] = emotion_result

            # Audio Quality Assessment
            if analysis_type in ["quality", "full"]:
                quality_result = await self._assess_audio_quality(audio_data, session_id)
                analysis_result["quality"] = quality_result

            # Speaker Diarization
            if analysis_type in ["diarization", "full"]:
                diarization_result = await self._perform_speaker_diarization(audio_data, session_id)
                analysis_result["diarization"] = diarization_result

            return analysis_result

        except Exception as e:
            self.logger.error(f"Error analyzing audio: {e}")
            return {"error": str(e)}

    async def _detect_voice_activity(self, audio_data: bytes, session_id: str) -> Dict[str, Any]:
        """Detect voice activity in audio."""
        try:
            # Placeholder VAD implementation
            # In real implementation, would use WebRTC VAD or similar

            # Simple energy-based VAD simulation
            import audioop
            try:
                # Calculate RMS energy
                rms = audioop.rms(audio_data, 2)  # Assuming 16-bit audio
                is_speech = rms > (self.vad_sensitivity * 32767)  # Threshold based on sensitivity

                vad_result = {
                    "is_speech": is_speech,
                    "confidence": min(rms / 32767.0, 1.0),
                    "energy_level": rms,
                    "duration": len(audio_data) / (16000 * 2),  # Assuming 16kHz, 16-bit
                    "timestamp": time.time()
                }

                # Update voice activity state
                self.voice_activity_state[session_id] = vad_result

                return vad_result

            except Exception:
                # Fallback if audioop fails
                return {
                    "is_speech": True,  # Assume speech if analysis fails
                    "confidence": 0.5,
                    "energy_level": 0,
                    "duration": 0,
                    "timestamp": time.time()
                }

        except Exception as e:
            self.logger.error(f"Error detecting voice activity: {e}")
            return {"error": str(e)}

    async def _analyze_emotion(self, audio_data: bytes, session_id: str) -> Dict[str, Any]:
        """Analyze emotion from audio."""
        try:
            # Placeholder emotion analysis
            # In real implementation, would use emotion recognition models

            # Simulate emotion analysis based on audio characteristics
            emotions = ["neutral", "happy", "sad", "angry", "surprised", "fearful"]
            confidence_scores = {emotion: 0.1 for emotion in emotions}

            # Simple heuristic: higher energy might indicate stronger emotions
            try:
                import audioop
                rms = audioop.rms(audio_data, 2)
                energy_factor = min(rms / 16384.0, 1.0)  # Normalize

                # Distribute confidence based on energy
                confidence_scores["neutral"] = 0.4 + (energy_factor * 0.3)
                confidence_scores["happy"] = energy_factor * 0.6
                confidence_scores["angry"] = energy_factor * 0.5
                confidence_scores["surprised"] = energy_factor * 0.4

                # Normalize to sum to 1
                total = sum(confidence_scores.values())
                confidence_scores = {k: v/total for k, v in confidence_scores.items()}

            except Exception:
                pass

            # Determine primary emotion
            primary_emotion = max(confidence_scores, key=confidence_scores.get)

            emotion_result = {
                "primary_emotion": primary_emotion,
                "confidence_scores": confidence_scores,
                "intensity": confidence_scores[primary_emotion],
                "timestamp": time.time()
            }

            # Update emotion analysis state
            self.emotion_analysis[session_id] = emotion_result

            return emotion_result

        except Exception as e:
            self.logger.error(f"Error analyzing emotion: {e}")
            return {"error": str(e)}

    async def _assess_audio_quality(self, audio_data: bytes, session_id: str) -> Dict[str, Any]:
        """Assess audio quality metrics."""
        try:
            quality_metrics = {}

            try:
                import audioop
                # Calculate various audio quality metrics

                # Signal-to-noise ratio (simplified)
                rms = audioop.rms(audio_data, 2)
                quality_metrics["rms_level"] = rms
                quality_metrics["snr_estimate"] = min(rms / 1000.0, 1.0)  # Simplified SNR

                # Peak level
                peak = audioop.max(audio_data, 2)
                quality_metrics["peak_level"] = peak
                quality_metrics["peak_normalized"] = peak / 32767.0

                # Clipping detection
                quality_metrics["clipping"] = peak >= 32700  # Close to max value

            except Exception:
                quality_metrics["rms_level"] = 0
                quality_metrics["snr_estimate"] = 0.5
                quality_metrics["peak_level"] = 0
                quality_metrics["peak_normalized"] = 0
                quality_metrics["clipping"] = False

            # Overall quality score
            quality_score = 0.5  # Base score
            if quality_metrics.get("snr_estimate", 0) > 0.3:
                quality_score += 0.2
            if not quality_metrics.get("clipping", True):
                quality_score += 0.2
            if quality_metrics.get("peak_normalized", 0) > 0.1:
                quality_score += 0.1

            quality_metrics["overall_quality"] = min(quality_score, 1.0)
            quality_metrics["quality_threshold"] = self.audio_quality_threshold
            quality_metrics["meets_threshold"] = quality_metrics["overall_quality"] >= self.audio_quality_threshold
            quality_metrics["timestamp"] = time.time()

            return quality_metrics

        except Exception as e:
            self.logger.error(f"Error assessing audio quality: {e}")
            return {"error": str(e)}

    async def _perform_speaker_diarization(self, audio_data: bytes, session_id: str) -> Dict[str, Any]:
        """Perform speaker diarization."""
        try:
            # Placeholder speaker diarization
            # In real implementation, would use pyannote.audio or similar

            # Simulate speaker detection
            duration = len(audio_data) / (16000 * 2)  # Assuming 16kHz, 16-bit

            diarization_result = {
                "num_speakers": 1,  # Assume single speaker for simplicity
                "segments": [
                    {
                        "speaker": "speaker_1",
                        "start_time": 0.0,
                        "end_time": duration,
                        "duration": duration,
                        "confidence": 0.9
                    }
                ],
                "total_duration": duration,
                "timestamp": time.time()
            }

            return diarization_result

        except Exception as e:
            self.logger.error(f"Error performing speaker diarization: {e}")
            return {"error": str(e)}

    async def _enhance_audio(self, audio_data: bytes, session_id: str,
                           enhancement_type: str) -> Optional[bytes]:
        """Enhance audio quality."""
        try:
            if not self.noise_reduction_enabled:
                return audio_data

            # Placeholder audio enhancement
            # In real implementation, would use noise reduction algorithms

            if enhancement_type == "noise_reduction":
                # Simple noise reduction simulation
                # In practice, would use RNNoise, SpeexDSP, or similar
                self.logger.info(f"Applying noise reduction to audio for session {session_id}")

                # Return enhanced audio (unchanged for now)
                return audio_data

            elif enhancement_type == "volume_normalization":
                # Volume normalization
                try:
                    import audioop
                    # Find current max peak
                    max_peak = audioop.max(audio_data, 2)
                    if max_peak > 0:
                        # Calculate gain to reach 80% of max
                        target_peak = int(32767 * 0.8)
                        gain = target_peak / max_peak
                        if gain < 1.0:  # Only amplify, don't attenuate
                            enhanced_audio = audioop.mul(audio_data, 2, gain)
                            return enhanced_audio
                except Exception:
                    pass

            return audio_data

        except Exception as e:
            self.logger.error(f"Error enhancing audio: {e}")
            return audio_data

    async def _detect_speakers(self, audio_data: bytes, session_id: str,
                             num_speakers: str) -> Dict[str, Any]:
        """Detect speakers in audio."""
        try:
            # Enhanced speaker detection
            diarization_result = await self._perform_speaker_diarization(audio_data, session_id)

            # Speaker identification (placeholder)
            speaker_identification = {
                "identified_speakers": [],
                "unknown_segments": diarization_result.get("segments", [])
            }

            # Simulate speaker identification
            for segment in diarization_result.get("segments", []):
                speaker_id = segment["speaker"]
                speaker_identification["identified_speakers"].append({
                    "speaker_id": speaker_id,
                    "confidence": segment.get("confidence", 0.5),
                    "segment": segment
                })

            return {
                "diarization": diarization_result,
                "identification": speaker_identification,
                "num_speakers_detected": len(diarization_result.get("segments", []))
            }

        except Exception as e:
            self.logger.error(f"Error detecting speakers: {e}")
            return {"error": str(e)}

    async def _create_audio_session(self, session_id: str, config: Dict[str, Any]):
        """Create a new audio processing session."""
        try:
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "status": "active",
                "config": config,
                "created_at": time.time(),
                "last_activity": time.time(),
                "audio_chunks": 0,
                "total_audio_size": 0
            }

            self.audio_buffers[session_id] = []
            self.voice_activity_state[session_id] = {}
            self.emotion_analysis[session_id] = {}

            self.logger.info(f"Created audio session: {session_id}")

        except Exception as e:
            self.logger.error(f"Error creating audio session: {e}")
            raise

    async def _process_audio_chunk(self, audio_chunk: bytes, session_id: str, sequence_number: int):
        """Process incoming audio chunk."""
        try:
            if session_id not in self.active_sessions:
                # Create session if it doesn't exist
                await self._create_audio_session(session_id, {})

            # Add to buffer
            if session_id not in self.audio_buffers:
                self.audio_buffers[session_id] = []

            self.audio_buffers[session_id].append(audio_chunk)

            # Update session stats
            session_info = self.active_sessions[session_id]
            session_info["audio_chunks"] = session_info.get("audio_chunks", 0) + 1
            session_info["total_audio_size"] = session_info.get("total_audio_size", 0) + len(audio_chunk)
            session_info["last_activity"] = time.time()

            # Process chunk for real-time analysis
            await self._analyze_audio_chunk(audio_chunk, session_id, sequence_number)

        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")

    async def _analyze_audio_chunk(self, audio_chunk: bytes, session_id: str, sequence_number: int):
        """Analyze audio chunk in real-time."""
        try:
            # Perform real-time analysis
            analysis_result = await self._analyze_audio(audio_chunk, session_id, "vad")

            # Publish real-time analysis
            realtime_message = {
                "message_id": f"realtime_analysis_{session_id}_{sequence_number}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "voice_router",
                "message_type": "realtime_analysis",
                "payload": {
                    "session_id": session_id,
                    "sequence_number": sequence_number,
                    "analysis": analysis_result,
                    "chunk_size": len(audio_chunk)
                }
            }

            self.publish_message("alicia/voice/realtime/analysis", realtime_message)

        except Exception as e:
            self.logger.error(f"Error analyzing audio chunk: {e}")

    async def _preprocess_audio_for_stt(self, audio_data: bytes, session_id: str):
        """Preprocess audio for better STT performance."""
        try:
            # Enhance audio quality
            enhanced_audio = await self._enhance_audio(audio_data, session_id, "noise_reduction")

            # Analyze audio quality
            quality_analysis = await self._assess_audio_quality(enhanced_audio or audio_data, session_id)

            # Publish preprocessing results
            preprocess_message = {
                "message_id": f"preprocess_{session_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "stt_service",
                "message_type": "preprocessed_audio",
                "payload": {
                    "session_id": session_id,
                    "original_audio": audio_data,
                    "enhanced_audio": enhanced_audio,
                    "quality_analysis": quality_analysis,
                    "preprocessing_applied": ["noise_reduction", "quality_assessment"]
                }
            }

            self.publish_message("alicia/voice/stt/preprocessed", preprocess_message)

        except Exception as e:
            self.logger.error(f"Error preprocessing audio for STT: {e}")

    async def _analyze_text_for_tts(self, text: str, session_id: str):
        """Analyze text for TTS emotion and style."""
        try:
            # Simple text analysis for emotion cues
            emotion_cues = {
                "happy": ["happy", "excited", "great", "wonderful", "awesome"],
                "sad": ["sad", "sorry", "unfortunately", "disappointed"],
                "angry": ["angry", "frustrated", "annoyed", "terrible"],
                "surprised": ["wow", "amazing", "incredible", "unbelievable"]
            }

            text_lower = text.lower()
            detected_emotions = {}

            for emotion, cues in emotion_cues.items():
                matches = sum(1 for cue in cues if cue in text_lower)
                if matches > 0:
                    detected_emotions[emotion] = matches

            # Determine primary emotion
            primary_emotion = "neutral"
            if detected_emotions:
                primary_emotion = max(detected_emotions, key=detected_emotions.get)

            # Publish TTS analysis
            tts_analysis_message = {
                "message_id": f"tts_analysis_{session_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "tts_service",
                "message_type": "text_analysis",
                "payload": {
                    "session_id": session_id,
                    "text": text,
                    "detected_emotions": detected_emotions,
                    "primary_emotion": primary_emotion,
                    "suggested_style": self._get_tts_style_for_emotion(primary_emotion)
                }
            }

            self.publish_message("alicia/voice/tts/analysis", tts_analysis_message)

        except Exception as e:
            self.logger.error(f"Error analyzing text for TTS: {e}")

    def _get_tts_style_for_emotion(self, emotion: str) -> Dict[str, Any]:
        """Get TTS style parameters for emotion."""
        style_mapping = {
            "happy": {"speed": 1.1, "pitch": 1.1, "volume": 1.0},
            "sad": {"speed": 0.9, "pitch": 0.9, "volume": 0.8},
            "angry": {"speed": 1.2, "pitch": 1.2, "volume": 1.1},
            "surprised": {"speed": 1.0, "pitch": 1.3, "volume": 1.0},
            "neutral": {"speed": 1.0, "pitch": 1.0, "volume": 1.0}
        }

        return style_mapping.get(emotion, style_mapping["neutral"])

    async def _process_audio_streams(self):
        """Process audio streams continuously."""
        while True:
            try:
                # Process any pending audio analysis
                for session_id in list(self.active_sessions.keys()):
                    if session_id in self.audio_buffers and self.audio_buffers[session_id]:
                        # Combine recent audio chunks for analysis
                        recent_chunks = self.audio_buffers[session_id][-10:]  # Last 10 chunks
                        combined_audio = b''.join(recent_chunks)

                        if len(combined_audio) > 1000:  # Minimum size for analysis
                            # Perform periodic analysis
                            await self._analyze_audio(combined_audio, session_id, "full")

                await asyncio.sleep(1)  # Process every second

            except Exception as e:
                self.logger.error(f"Error processing audio streams: {e}")
                await asyncio.sleep(1)

    async def _cleanup_audio_session(self, session_id: str):
        """Cleanup audio processing session."""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            if session_id in self.audio_buffers:
                del self.audio_buffers[session_id]

            if session_id in self.voice_activity_state:
                del self.voice_activity_state[session_id]

            if session_id in self.emotion_analysis:
                del self.emotion_analysis[session_id]

            self.logger.info(f"Cleaned up audio session: {session_id}")

        except Exception as e:
            self.logger.error(f"Error cleaning up audio session: {e}")

    async def _cleanup_expired_sessions(self):
        """Cleanup expired audio sessions."""
        while True:
            try:
                current_time = time.time()
                session_timeout = 3600  # 1 hour

                # Find expired sessions
                expired_sessions = []
                for session_id, session_info in self.active_sessions.items():
                    last_activity = session_info.get("last_activity", 0)
                    if current_time - last_activity > session_timeout:
                        expired_sessions.append(session_id)

                # Cleanup expired sessions
                for session_id in expired_sessions:
                    await self._cleanup_audio_session(session_id)

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error cleaning up sessions: {e}")
                await asyncio.sleep(300)


def main():
    """Main entry point for Advanced Voice Pipeline service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(levelname)s - %(message)s'
    )

    # Create advanced voice pipeline
    advanced_voice = AdvancedVoicePipeline()

    # Start API server
    try:
        advanced_voice.api.run_api(host="0.0.0.0", port=8012)
    except KeyboardInterrupt:
        advanced_voice.shutdown()


if __name__ == "__main__":
    main()
