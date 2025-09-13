"""
Alicia Bus Architecture - Multi-Language Support Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Multi-language support service that handles internationalization,
language detection, translation, and localization for the Alicia system.
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
from dotenv import load_dotenv

from service_wrapper import BusServiceWrapper, BusServiceAPI

# Load environment variables
load_dotenv()


class MultiLanguageSupport(BusServiceWrapper):
    """
    Multi-Language Support service for the Alicia bus architecture.

    Provides comprehensive internationalization and localization:
    - Language detection and identification
    - Text translation and localization
    - Cultural adaptation and formatting
    - Multi-language voice synthesis support
    - Dynamic language switching

    Features:
    - Real-time language detection
    - High-quality translation services
    - Cultural context awareness
    - Voice synthesis language support
    - Localization resource management
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": "multi_language",
            "password": "alicia_language_2024"
        }

        super().__init__("multi_language", mqtt_config)

        # Language Configuration
        self.default_language = os.getenv("DEFAULT_LANGUAGE", "en")
        self.supported_languages = os.getenv("SUPPORTED_LANGUAGES", "en,es,fr,de,it,pt,zh,ja,ko").split(",")
        self.translation_cache_ttl = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
        self.max_translation_length = int(os.getenv("MAX_TRANSLATION_LENGTH", "5000"))

        # Language resources
        self.language_resources: Dict[str, Dict[str, Any]] = {}
        self.translation_cache: Dict[str, Dict[str, Any]] = {}
        self.language_models: Dict[str, Any] = {}

        # Translation services
        self.translation_providers = {
            "google": self._translate_with_google,
            "microsoft": self._translate_with_microsoft,
            "deepl": self._translate_with_deepl,
            "openai": self._translate_with_openai
        }

        # Load language resources
        self._load_language_resources()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_language_endpoints()

        # Service capabilities
        self.capabilities = [
            "language_detection",
            "text_translation",
            "cultural_adaptation",
            "localization_support",
            "voice_language_synthesis"
        ]

        self.version = "1.0.0"

        # Start background tasks
        asyncio.create_task(self._cleanup_expired_cache())

        self.logger.info("Multi-Language Support initialized")

    def _load_language_resources(self):
        """Load language resources and configurations."""
        try:
            # Load supported languages configuration
            for lang_code in self.supported_languages:
                self.language_resources[lang_code] = {
                    "code": lang_code,
                    "name": self._get_language_name(lang_code),
                    "direction": self._get_text_direction(lang_code),
                    "voice_synthesis": self._get_voice_synthesis_support(lang_code),
                    "date_formats": self._get_date_formats(lang_code),
                    "number_formats": self._get_number_formats(lang_code),
                    "currency_formats": self._get_currency_formats(lang_code),
                    "cultural_notes": self._get_cultural_notes(lang_code)
                }

            self.logger.info(f"Loaded resources for {len(self.supported_languages)} languages")

        except Exception as e:
            self.logger.error(f"Error loading language resources: {e}")

    def _get_language_name(self, lang_code: str) -> str:
        """Get full language name from code."""
        language_names = {
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "zh": "中文",
            "ja": "日本語",
            "ko": "한국어"
        }
        return language_names.get(lang_code, lang_code)

    def _get_text_direction(self, lang_code: str) -> str:
        """Get text direction for language."""
        rtl_languages = ["ar", "he", "fa", "ur"]
        return "rtl" if lang_code in rtl_languages else "ltr"

    def _get_voice_synthesis_support(self, lang_code: str) -> Dict[str, Any]:
        """Get voice synthesis support for language."""
        voice_support = {
            "en": {"engines": ["piper", "google", "azure"], "voices": ["male", "female"]},
            "es": {"engines": ["piper", "google", "azure"], "voices": ["male", "female"]},
            "fr": {"engines": ["piper", "google", "azure"], "voices": ["male", "female"]},
            "de": {"engines": ["piper", "google", "azure"], "voices": ["male", "female"]},
            "it": {"engines": ["piper", "google"], "voices": ["male", "female"]},
            "pt": {"engines": ["piper", "google"], "voices": ["male", "female"]},
            "zh": {"engines": ["google", "azure"], "voices": ["male", "female"]},
            "ja": {"engines": ["google", "azure"], "voices": ["male", "female"]},
            "ko": {"engines": ["google", "azure"], "voices": ["male", "female"]}
        }
        return voice_support.get(lang_code, {"engines": ["google"], "voices": ["female"]})

    def _get_date_formats(self, lang_code: str) -> Dict[str, str]:
        """Get date formats for language."""
        date_formats = {
            "en": {"short": "MM/DD/YYYY", "long": "MMMM DD, YYYY", "time": "HH:MM AM/PM"},
            "es": {"short": "DD/MM/YYYY", "long": "DD de MMMM de YYYY", "time": "HH:MM"},
            "fr": {"short": "DD/MM/YYYY", "long": "DD MMMM YYYY", "time": "HH:MM"},
            "de": {"short": "DD.MM.YYYY", "long": "DD. MMMM YYYY", "time": "HH:MM"},
            "it": {"short": "DD/MM/YYYY", "long": "DD MMMM YYYY", "time": "HH:MM"},
            "pt": {"short": "DD/MM/YYYY", "long": "DD de MMMM de YYYY", "time": "HH:MM"},
            "zh": {"short": "YYYY-MM-DD", "long": "YYYY年MM月DD日", "time": "HH:MM"},
            "ja": {"short": "YYYY/MM/DD", "long": "YYYY年MM月DD日", "time": "HH:MM"},
            "ko": {"short": "YYYY-MM-DD", "long": "YYYY년 MM월 DD일", "time": "HH:MM"}
        }
        return date_formats.get(lang_code, date_formats["en"])

    def _get_number_formats(self, lang_code: str) -> Dict[str, str]:
        """Get number formats for language."""
        number_formats = {
            "en": {"decimal": ".", "thousands": ",", "currency": "$"},
            "es": {"decimal": ",", "thousands": ".", "currency": "€"},
            "fr": {"decimal": ",", "thousands": " ", "currency": "€"},
            "de": {"decimal": ",", "thousands": ".", "currency": "€"},
            "it": {"decimal": ",", "thousands": ".", "currency": "€"},
            "pt": {"decimal": ",", "thousands": ".", "currency": "€"},
            "zh": {"decimal": ".", "thousands": ",", "currency": "¥"},
            "ja": {"decimal": ".", "thousands": ",", "currency": "¥"},
            "ko": {"decimal": ".", "thousands": ",", "currency": "₩"}
        }
        return number_formats.get(lang_code, number_formats["en"])

    def _get_currency_formats(self, lang_code: str) -> Dict[str, str]:
        """Get currency formats for language."""
        currency_formats = {
            "en": {"symbol": "$", "position": "before", "space": False},
            "es": {"symbol": "€", "position": "after", "space": True},
            "fr": {"symbol": "€", "position": "after", "space": True},
            "de": {"symbol": "€", "position": "after", "space": True},
            "it": {"symbol": "€", "position": "after", "space": True},
            "pt": {"symbol": "€", "position": "after", "space": True},
            "zh": {"symbol": "¥", "position": "before", "space": False},
            "ja": {"symbol": "¥", "position": "before", "space": False},
            "ko": {"symbol": "₩", "position": "before", "space": False}
        }
        return currency_formats.get(lang_code, currency_formats["en"])

    def _get_cultural_notes(self, lang_code: str) -> Dict[str, str]:
        """Get cultural notes for language."""
        cultural_notes = {
            "en": {"greeting": "Hello", "farewell": "Goodbye", "politeness": "Please and thank you are important"},
            "es": {"greeting": "Hola", "farewell": "Adiós", "politeness": "Formal address is common"},
            "fr": {"greeting": "Bonjour", "farewell": "Au revoir", "politeness": "Formal language is preferred"},
            "de": {"greeting": "Guten Tag", "farewell": "Auf Wiedersehen", "politeness": "Direct but polite communication"},
            "it": {"greeting": "Ciao", "farewell": "Arrivederci", "politeness": "Warm and expressive"},
            "pt": {"greeting": "Olá", "farewell": "Adeus", "politeness": "Friendly and welcoming"},
            "zh": {"greeting": "你好", "farewell": "再见", "politeness": "Respect for hierarchy is important"},
            "ja": {"greeting": "こんにちは", "farewell": "さようなら", "politeness": "Honorific language is essential"},
            "ko": {"greeting": "안녕하세요", "farewell": "안녕히 가세요", "politeness": "Respect for elders is important"}
        }
        return cultural_notes.get(lang_code, cultural_notes["en"])

    def _setup_language_endpoints(self):
        """Setup FastAPI endpoints for language support."""

        @self.api.app.post("/detect")
        async def detect_language(request: Dict[str, Any]):
            """Detect language of input text."""
            try:
                text = request.get("text")

                if not text:
                    raise HTTPException(status_code=400, detail="Text is required")

                # Detect language
                detection_result = await self._detect_language(text)

                return {
                    "text": text,
                    "detected_language": detection_result,
                    "confidence": detection_result.get("confidence", 0.0)
                }

            except Exception as e:
                self.logger.error(f"Language detection error: {e}")
                raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

        @self.api.app.post("/translate")
        async def translate_text(request: Dict[str, Any]):
            """Translate text between languages."""
            try:
                text = request.get("text")
                source_lang = request.get("source_lang", "auto")
                target_lang = request.get("target_lang")
                provider = request.get("provider", "google")

                if not text or not target_lang:
                    raise HTTPException(status_code=400, detail="Text and target language are required")

                # Translate text
                translation_result = await self._translate_text(text, source_lang, target_lang, provider)

                return {
                    "original_text": text,
                    "translated_text": translation_result["text"],
                    "source_language": translation_result["source_lang"],
                    "target_language": target_lang,
                    "provider": provider,
                    "confidence": translation_result.get("confidence", 0.0)
                }

            except Exception as e:
                self.logger.error(f"Translation error: {e}")
                raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

        @self.api.app.get("/languages")
        async def list_languages():
            """List supported languages."""
            languages_list = []
            for lang_code, lang_info in self.language_resources.items():
                languages_list.append({
                    "code": lang_code,
                    "name": lang_info.get("name"),
                    "direction": lang_info.get("direction"),
                    "voice_synthesis": lang_info.get("voice_synthesis"),
                    "date_formats": lang_info.get("date_formats"),
                    "cultural_notes": lang_info.get("cultural_notes")
                })

            return {"languages": languages_list, "count": len(languages_list)}

        @self.api.app.get("/languages/{lang_code}")
        async def get_language_info(lang_code: str):
            """Get detailed language information."""
            if lang_code not in self.language_resources:
                raise HTTPException(status_code=404, detail="Language not supported")

            return self.language_resources[lang_code]

        @self.api.app.post("/localize")
        async def localize_content(request: Dict[str, Any]):
            """Localize content for specific language."""
            try:
                content = request.get("content")
                target_lang = request.get("target_lang")

                if not content or not target_lang:
                    raise HTTPException(status_code=400, detail="Content and target language are required")

                # Localize content
                localized_content = await self._localize_content(content, target_lang)

                return {
                    "original_content": content,
                    "localized_content": localized_content,
                    "target_language": target_lang
                }

            except Exception as e:
                self.logger.error(f"Localization error: {e}")
                raise HTTPException(status_code=500, detail=f"Localization failed: {str(e)}")

        @self.api.app.get("/health")
        async def health_check():
            """Multi-language support health check."""
            return {
                "service": "multi_language",
                "status": "healthy" if self.is_connected else "unhealthy",
                "supported_languages": len(self.supported_languages),
                "cache_size": len(self.translation_cache),
                "uptime": time.time() - self.start_time
            }

    def subscribe_to_topics(self):
        """Subscribe to language-related MQTT topics."""
        topics = [
            "alicia/language/detect",
            "alicia/language/translate",
            "alicia/language/localize",
            "alicia/voice/stt/request",
            "alicia/voice/tts/request",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

        self.logger.info("Subscribed to language topics")

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming MQTT messages."""
        try:
            if topic == "alicia/language/detect":
                self._handle_language_detection(message)
            elif topic == "alicia/language/translate":
                self._handle_translation_request(message)
            elif topic == "alicia/language/localize":
                self._handle_localization_request(message)
            elif topic == "alicia/voice/stt/request":
                self._handle_stt_request(message)
            elif topic == "alicia/voice/tts/request":
                self._handle_tts_request(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing language message: {e}")

    def _handle_language_detection(self, message: Dict[str, Any]):
        """Handle language detection requests."""
        try:
            payload = message.get("payload", {})
            text = payload.get("text")
            request_id = payload.get("request_id")

            if text:
                asyncio.create_task(self._process_language_detection(text, request_id))

        except Exception as e:
            self.logger.error(f"Error handling language detection: {e}")

    def _handle_translation_request(self, message: Dict[str, Any]):
        """Handle translation requests."""
        try:
            payload = message.get("payload", {})
            text = payload.get("text")
            source_lang = payload.get("source_lang", "auto")
            target_lang = payload.get("target_lang")
            provider = payload.get("provider", "google")
            request_id = payload.get("request_id")

            if text and target_lang:
                asyncio.create_task(self._process_translation(text, source_lang, target_lang, provider, request_id))

        except Exception as e:
            self.logger.error(f"Error handling translation request: {e}")

    def _handle_localization_request(self, message: Dict[str, Any]):
        """Handle localization requests."""
        try:
            payload = message.get("payload", {})
            content = payload.get("content")
            target_lang = payload.get("target_lang")
            request_id = payload.get("request_id")

            if content and target_lang:
                asyncio.create_task(self._process_localization(content, target_lang, request_id))

        except Exception as e:
            self.logger.error(f"Error handling localization request: {e}")

    def _handle_stt_request(self, message: Dict[str, Any]):
        """Handle STT requests for language detection."""
        try:
            payload = message.get("payload", {})
            transcription = payload.get("transcription", "")
            session_id = payload.get("session_id", "")

            if transcription:
                # Detect language of transcription
                asyncio.create_task(self._detect_transcription_language(transcription, session_id))

        except Exception as e:
            self.logger.error(f"Error handling STT request: {e}")

    def _handle_tts_request(self, message: Dict[str, Any]):
        """Handle TTS requests for language support."""
        try:
            payload = message.get("payload", {})
            text = payload.get("text", "")
            language = payload.get("language", self.default_language)
            session_id = payload.get("session_id", "")

            if text:
                # Validate language support for TTS
                asyncio.create_task(self._validate_tts_language(text, language, session_id))

        except Exception as e:
            self.logger.error(f"Error handling TTS request: {e}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    async def _detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of input text."""
        try:
            # Simple language detection (could be enhanced with ML models)
            # For now, use basic heuristics and common words

            text_lower = text.lower()

            # Language detection patterns
            language_patterns = {
                "es": ["el", "la", "los", "las", "qué", "cómo", "cuándo", "dónde"],
                "fr": ["le", "la", "les", "du", "de", "à", "et", "est"],
                "de": ["der", "die", "das", "und", "ist", "mit", "auf"],
                "it": ["il", "la", "i", "le", "e", "è", "di", "a"],
                "pt": ["o", "a", "os", "as", "e", "é", "de", "do"],
                "zh": ["的", "是", "在", "有", "和", "我", "你", "他"],
                "ja": ["は", "の", "が", "を", "に", "で", "と", "も"],
                "ko": ["은", "는", "이", "가", "을", "를", "에", "에서"]
            }

            # Count matches for each language
            scores = {}
            for lang, patterns in language_patterns.items():
                score = sum(1 for pattern in patterns if pattern in text_lower)
                if score > 0:
                    scores[lang] = score

            # Default to English if no patterns match
            if not scores:
                detected_lang = "en"
                confidence = 0.5
            else:
                detected_lang = max(scores, key=scores.get)
                max_score = scores[detected_lang]
                confidence = min(max_score / 5.0, 1.0)  # Normalize confidence

            return {
                "language": detected_lang,
                "confidence": confidence,
                "detected_at": time.time()
            }

        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return {
                "language": self.default_language,
                "confidence": 0.0,
                "error": str(e)
            }

    async def _translate_text(self, text: str, source_lang: str, target_lang: str,
                            provider: str = "google") -> Dict[str, Any]:
        """Translate text between languages."""
        try:
            # Check cache first
            cache_key = f"{text}:{source_lang}:{target_lang}:{provider}"
            if cache_key in self.translation_cache:
                cached_result = self.translation_cache[cache_key]
                if time.time() - cached_result["cached_at"] < self.translation_cache_ttl:
                    return cached_result

            # Validate languages
            if target_lang not in self.supported_languages:
                raise Exception(f"Target language {target_lang} not supported")

            # Detect source language if auto
            if source_lang == "auto":
                detection = await self._detect_language(text)
                source_lang = detection["language"]

            # Get translation provider
            if provider not in self.translation_providers:
                provider = "google"

            # Perform translation
            translation_result = await self.translation_providers[provider](
                text, source_lang, target_lang
            )

            # Cache result
            result = {
                "text": translation_result,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "provider": provider,
                "confidence": 0.9,  # Placeholder
                "cached_at": time.time()
            }

            self.translation_cache[cache_key] = result

            return result

        except Exception as e:
            self.logger.error(f"Error translating text: {e}")
            return {
                "text": text,  # Return original text on error
                "source_lang": source_lang,
                "target_lang": target_lang,
                "error": str(e)
            }

    async def _translate_with_google(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using Google Translate API."""
        try:
            # Placeholder - would integrate with Google Translate API
            self.logger.info(f"Google translation: {source_lang} -> {target_lang}")
            return f"[Translated to {target_lang}]: {text}"
        except Exception as e:
            self.logger.error(f"Google translation error: {e}")
            raise

    async def _translate_with_microsoft(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using Microsoft Translator API."""
        try:
            # Placeholder - would integrate with Microsoft Translator API
            self.logger.info(f"Microsoft translation: {source_lang} -> {target_lang}")
            return f"[Translated to {target_lang}]: {text}"
        except Exception as e:
            self.logger.error(f"Microsoft translation error: {e}")
            raise

    async def _translate_with_deepl(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using DeepL API."""
        try:
            # Placeholder - would integrate with DeepL API
            self.logger.info(f"DeepL translation: {source_lang} -> {target_lang}")
            return f"[Translated to {target_lang}]: {text}"
        except Exception as e:
            self.logger.error(f"DeepL translation error: {e}")
            raise

    async def _translate_with_openai(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using OpenAI API."""
        try:
            # Placeholder - would integrate with OpenAI API
            self.logger.info(f"OpenAI translation: {source_lang} -> {target_lang}")
            return f"[Translated to {target_lang}]: {text}"
        except Exception as e:
            self.logger.error(f"OpenAI translation error: {e}")
            raise

    async def _localize_content(self, content: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """Localize content for specific language."""
        try:
            if target_lang not in self.language_resources:
                raise Exception(f"Language {target_lang} not supported")

            lang_info = self.language_resources[target_lang]
            localized_content = {}

            # Localize text content
            for key, value in content.items():
                if isinstance(value, str):
                    # Translate text content
                    translation = await self._translate_text(value, "auto", target_lang)
                    localized_content[key] = translation["text"]
                elif isinstance(value, dict):
                    # Recursively localize nested content
                    localized_content[key] = await self._localize_content(value, target_lang)
                else:
                    localized_content[key] = value

            # Add language-specific formatting
            localized_content["_language"] = target_lang
            localized_content["_formatting"] = {
                "date_format": lang_info["date_formats"],
                "number_format": lang_info["number_formats"],
                "currency_format": lang_info["currency_formats"]
            }

            return localized_content

        except Exception as e:
            self.logger.error(f"Error localizing content: {e}")
            return content

    async def _process_language_detection(self, text: str, request_id: str = None):
        """Process language detection request."""
        try:
            detection_result = await self._detect_language(text)

            # Publish detection result
            detection_message = {
                "message_id": f"lang_detect_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "request_id": request_id,
                    "text": text,
                    "detected_language": detection_result["language"],
                    "confidence": detection_result["confidence"]
                }
            }

            self.publish_message("alicia/language/detection/complete", detection_message)

        except Exception as e:
            self.logger.error(f"Error processing language detection: {e}")

    async def _process_translation(self, text: str, source_lang: str, target_lang: str,
                                 provider: str, request_id: str = None):
        """Process translation request."""
        try:
            translation_result = await self._translate_text(text, source_lang, target_lang, provider)

            # Publish translation result
            translation_message = {
                "message_id": f"translation_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "request_id": request_id,
                    "original_text": text,
                    "translated_text": translation_result["text"],
                    "source_language": translation_result["source_lang"],
                    "target_language": target_lang,
                    "provider": provider
                }
            }

            self.publish_message("alicia/language/translation/complete", translation_message)

        except Exception as e:
            self.logger.error(f"Error processing translation: {e}")

    async def _process_localization(self, content: Dict[str, Any], target_lang: str, request_id: str = None):
        """Process localization request."""
        try:
            localized_content = await self._localize_content(content, target_lang)

            # Publish localization result
            localization_message = {
                "message_id": f"localization_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "broadcast",
                "message_type": "event",
                "payload": {
                    "request_id": request_id,
                    "original_content": content,
                    "localized_content": localized_content,
                    "target_language": target_lang
                }
            }

            self.publish_message("alicia/language/localization/complete", localization_message)

        except Exception as e:
            self.logger.error(f"Error processing localization: {e}")

    async def _detect_transcription_language(self, transcription: str, session_id: str):
        """Detect language of voice transcription."""
        try:
            detection_result = await self._detect_language(transcription)

            # Publish language detection for voice session
            voice_lang_message = {
                "message_id": f"voice_lang_{session_id}_{uuid.uuid4().hex[:8]}",
                "timestamp": time.time(),
                "source": self.service_name,
                "destination": "voice_router",
                "message_type": "language_detection",
                "payload": {
                    "session_id": session_id,
                    "transcription": transcription,
                    "detected_language": detection_result["language"],
                    "confidence": detection_result["confidence"]
                }
            }

            self.publish_message("alicia/voice/language/detected", voice_lang_message)

        except Exception as e:
            self.logger.error(f"Error detecting transcription language: {e}")

    async def _validate_tts_language(self, text: str, language: str, session_id: str):
        """Validate language support for TTS."""
        try:
            if language not in self.language_resources:
                # Fallback to default language
                fallback_lang = self.default_language
                self.logger.warning(f"Language {language} not supported for TTS, using {fallback_lang}")

                # Publish language validation result
                validation_message = {
                    "message_id": f"tts_lang_{session_id}_{uuid.uuid4().hex[:8]}",
                    "timestamp": time.time(),
                    "source": self.service_name,
                    "destination": "tts_service",
                    "message_type": "language_validation",
                    "payload": {
                        "session_id": session_id,
                        "requested_language": language,
                        "validated_language": fallback_lang,
                        "voice_synthesis": self.language_resources[fallback_lang]["voice_synthesis"]
                    }
                }

                self.publish_message("alicia/voice/tts/language/validated", validation_message)

        except Exception as e:
            self.logger.error(f"Error validating TTS language: {e}")

    async def _cleanup_expired_cache(self):
        """Cleanup expired translation cache."""
        while True:
            try:
                current_time = time.time()

                # Find expired cache entries
                expired_keys = []
                for key, cache_entry in self.translation_cache.items():
                    if current_time - cache_entry.get("cached_at", 0) > self.translation_cache_ttl:
                        expired_keys.append(key)

                # Remove expired entries
                for key in expired_keys:
                    del self.translation_cache[key]

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error cleaning up cache: {e}")
                await asyncio.sleep(300)


async def main():
    """Main entry point for Multi-Language Support service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create multi-language support
    multi_language = MultiLanguageSupport()

    # Start API server
    try:
        api = BusServiceAPI(multi_language)
        config = uvicorn.Config(api.app, host="0.0.0.0", port=8022)
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        multi_language.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
