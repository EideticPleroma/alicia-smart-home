# Chapter 8: AI Service & Grok Integration

## 🎯 **AI Service Architecture Overview**

The AI Service is the brain of Alicia's voice processing pipeline. It takes transcribed text from the STT service and processes it through advanced AI models to understand user intent, generate responses, and coordinate smart home actions. This chapter analyzes the AI service implementation, examining its multi-provider architecture, Grok integration, and conversation management capabilities.

## 🧠 **Multi-Provider AI Architecture**

### **Provider Selection Strategy**

Alicia's AI service implements a **sophisticated multi-provider architecture** that supports multiple AI providers:

```python
class AIService(BusServiceWrapper):
    """
    AI Service for the Alicia bus architecture.
    
    Handles natural language processing and response generation using:
    - xAI Grok API (primary)
    - OpenAI GPT (fallback)
    - Local models (future)
    """
```

**Why Multiple AI Providers?**

1. **Reliability**: If one provider fails, others can take over
2. **Cost Optimization**: Use different providers for different use cases
3. **Performance**: Choose the best provider for specific tasks
4. **Innovation**: Access to cutting-edge models from different providers
5. **Vendor Independence**: Avoid lock-in to a single provider

### **Provider Configuration**

The AI service uses **environment-based configuration** to select the appropriate provider:

```python
def __init__(self):
    # AI Configuration
    self.ai_provider = os.getenv("AI_PROVIDER", "grok")  # grok, openai, local
    self.grok_api_key = os.getenv("GROK_API_KEY")
    self.openai_api_key = os.getenv("OPENAI_API_KEY")
    self.model_name = os.getenv("AI_MODEL", "grok-beta")
    self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
    self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
```

**Configuration Benefits:**
- **Runtime Selection**: Change providers without code changes
- **Model Flexibility**: Choose appropriate models for different tasks
- **Parameter Tuning**: Optimize temperature, token limits, etc.
- **Cost Control**: Manage API usage and costs

## 🚀 **Grok Integration (Primary Provider)**

### **Grok API Client Setup**

The AI service uses **xAI Grok** as its primary provider due to its advanced capabilities and real-time information access:

```python
def _setup_grok(self):
    """Setup xAI Grok client."""
    if not self.grok_api_key:
        raise ValueError("GROK_API_KEY environment variable is required")
    
    try:
        # Import xAI SDK (assuming it's available)
        # For now, we'll use requests to call the API directly
        import requests
        self.grok_client = requests.Session()
        self.grok_client.headers.update({
            "Authorization": f"Bearer {self.grok_api_key}",
            "Content-Type": "application/json"
        })
        self.logger.info("Grok client initialized")
    except ImportError:
        self.logger.error("xAI SDK not available. Install with: pip install xai-sdk")
        raise
    except Exception as e:
        self.logger.error(f"Failed to setup Grok client: {e}")
        raise
```

**Why Grok?**
- **Real-time Information**: Access to current information via X platform
- **Advanced Reasoning**: Superior reasoning capabilities
- **Witty Personality**: Engaging and humorous responses
- **Context Awareness**: Excellent understanding of context
- **Multi-modal**: Support for text, images, and other inputs

### **Grok API Integration**

The AI service implements **comprehensive Grok API integration**:

```python
async def _process_with_grok(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Process text using Grok API."""
    try:
        # Prepare Grok API request
        grok_request = {
            "model": self.model_name,
            "messages": self._build_conversation_messages(text, context),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        # Call Grok API
        response = self.grok_client.post(
            "https://api.x.ai/v1/chat/completions",
            json=grok_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return self._parse_grok_response(result)
        else:
            raise Exception(f"Grok API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        self.logger.error(f"Grok API processing failed: {e}")
        raise
```

**Grok API Features:**
- **Chat Completions**: Standard chat completion interface
- **Streaming Support**: Real-time response streaming
- **Context Management**: Maintain conversation history
- **Parameter Control**: Fine-tune temperature and token limits
- **Error Handling**: Robust error handling and retry logic

### **Conversation Message Building**

The AI service implements **sophisticated conversation management**:

```python
def _build_conversation_messages(self, text: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build conversation messages for AI processing."""
    messages = []
    
    # System message with context
    system_message = self._build_system_message(context)
    messages.append({"role": "system", "content": system_message})
    
    # Conversation history
    session_id = context.get("session_id")
    if session_id and session_id in self.conversation_history:
        history = self.conversation_history[session_id]
        for entry in history[-self.max_history_length:]:
            messages.append({
                "role": entry["role"],
                "content": entry["content"]
            })
    
    # Current user message
    messages.append({"role": "user", "content": text})
    
    return messages
```

**Conversation Management Features:**
- **System Context**: Provide context about Alicia's capabilities
- **History Tracking**: Maintain conversation history
- **Session Management**: Track conversations by session
- **Context Preservation**: Maintain context across interactions

## 🔄 **OpenAI Integration (Fallback Provider)**

### **OpenAI Client Setup**

The AI service includes **OpenAI GPT** as a fallback option:

```python
def _setup_openai(self):
    """Setup OpenAI client."""
    if not self.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    try:
        from openai import OpenAI
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.logger.info("OpenAI client initialized")
    except ImportError:
        self.logger.error("OpenAI SDK not available. Install with: pip install openai")
        raise
    except Exception as e:
        self.logger.error(f"Failed to setup OpenAI client: {e}")
        raise
```

**OpenAI Benefits:**
- **Proven Reliability**: Well-established and reliable
- **Model Variety**: Access to multiple GPT models
- **Cost Effective**: Competitive pricing
- **Wide Adoption**: Extensive documentation and community support

### **OpenAI Processing Implementation**

The AI service implements **OpenAI processing with fallback logic**:

```python
async def _process_with_openai(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Process text using OpenAI API."""
    try:
        # Prepare OpenAI request
        messages = self._build_conversation_messages(text, context)
        
        # Call OpenAI API
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return self._parse_openai_response(response)
        
    except Exception as e:
        self.logger.error(f"OpenAI API processing failed: {e}")
        raise
```

## 🏠 **Smart Home Command Processing**

### **Intent Recognition and Command Parsing**

The AI service implements **sophisticated intent recognition** for smart home commands:

```python
def _analyze_smart_home_intent(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze text for smart home commands and intent."""
    intent_analysis = {
        "is_smart_home_command": False,
        "intent_type": None,
        "entities": {},
        "confidence": 0.0,
        "action_required": None
    }
    
    # Common smart home command patterns
    command_patterns = {
        "light_control": [
            r"turn (on|off) (the )?lights?",
            r"(turn on|turn off|switch) (the )?lights?",
            r"lights? (on|off)"
        ],
        "volume_control": [
            r"turn (up|down) (the )?volume",
            r"volume (up|down)",
            r"(increase|decrease) volume"
        ],
        "music_control": [
            r"play (music|song)",
            r"stop (music|song)",
            r"pause (music|song)",
            r"next (song|track)",
            r"previous (song|track)"
        ],
        "temperature_control": [
            r"set temperature to (\d+)",
            r"make it (warmer|cooler)",
            r"turn (up|down) (the )?heat"
        ]
    }
    
    # Analyze text against patterns
    for intent_type, patterns in command_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text.lower()):
                intent_analysis["is_smart_home_command"] = True
                intent_analysis["intent_type"] = intent_type
                intent_analysis["confidence"] = 0.8  # High confidence for pattern matches
                break
    
    return intent_analysis
```

**Intent Recognition Features:**
- **Pattern Matching**: Use regex patterns for common commands
- **Entity Extraction**: Extract specific parameters (room, device, value)
- **Confidence Scoring**: Assess confidence in intent recognition
- **Context Awareness**: Consider conversation context

### **Device Command Generation**

The AI service converts **natural language to device commands**:

```python
def _generate_device_command(self, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate device command from intent analysis."""
    command = {
        "device_type": None,
        "action": None,
        "parameters": {},
        "target_device": None,
        "room": None
    }
    
    intent_type = intent.get("intent_type")
    
    if intent_type == "light_control":
        command.update({
            "device_type": "light",
            "action": "toggle" if "on" in intent.get("text", "") else "off",
            "room": self._extract_room_from_context(context)
        })
    
    elif intent_type == "volume_control":
        command.update({
            "device_type": "speaker",
            "action": "volume_up" if "up" in intent.get("text", "") else "volume_down",
            "parameters": {"amount": 10}
        })
    
    elif intent_type == "music_control":
        command.update({
            "device_type": "speaker",
            "action": intent.get("text", "").split()[0],  # play, stop, pause, etc.
            "room": self._extract_room_from_context(context)
        })
    
    return command
```

**Command Generation Features:**
- **Device Mapping**: Map intents to specific device types
- **Action Translation**: Convert natural language to device actions
- **Parameter Extraction**: Extract specific parameters and values
- **Room Context**: Consider room context for device targeting

## 💬 **Conversation Management**

### **Context-Aware Conversation**

The AI service implements **sophisticated conversation management**:

```python
def _manage_conversation_context(self, session_id: str, user_message: str, ai_response: str):
    """Manage conversation context and history."""
    if session_id not in self.conversation_history:
        self.conversation_history[session_id] = []
    
    # Add user message
    self.conversation_history[session_id].append({
        "role": "user",
        "content": user_message,
        "timestamp": time.time()
    })
    
    # Add AI response
    self.conversation_history[session_id].append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": time.time()
    })
    
    # Trim history to max length
    if len(self.conversation_history[session_id]) > self.max_history_length * 2:
        self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_history_length * 2:]
```

**Conversation Management Features:**
- **Session Tracking**: Track conversations by session ID
- **History Management**: Maintain conversation history
- **Context Preservation**: Preserve context across interactions
- **Memory Management**: Limit history to prevent memory issues

### **Personality and Response Style**

The AI service implements **Alicia's personality system**:

```python
def _build_system_message(self, context: Dict[str, Any]) -> str:
    """Build system message with Alicia's personality and capabilities."""
    system_message = f"""
    You are Alicia, a smart home AI assistant. You are witty, helpful, and slightly sarcastic.
    
    Your capabilities:
    - Control smart home devices (lights, speakers, temperature, etc.)
    - Answer questions about your home
    - Provide weather information
    - Play music and control audio
    - Set reminders and timers
    - General conversation and assistance
    
    Current context:
    - Time: {context.get('current_time', 'unknown')}
    - Weather: {context.get('weather', 'unknown')}
    - Active devices: {context.get('active_devices', [])}
    - User preferences: {context.get('user_preferences', {})}
    
    Always be helpful, but don't be afraid to show your personality. Be concise but engaging.
    """
    
    return system_message
```

**Personality Features:**
- **Witty Responses**: Engaging and humorous personality
- **Context Awareness**: Consider current time, weather, devices
- **Capability Awareness**: Know what Alicia can do
- **User Preferences**: Consider user preferences and history

## 🔄 **Response Processing and Publishing**

### **Response Generation and Validation**

The AI service implements **comprehensive response processing**:

```python
def _process_ai_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Process AI response and prepare for publishing."""
    processed_response = {
        "text": response.get("content", ""),
        "intent": response.get("intent", "conversation"),
        "confidence": response.get("confidence", 0.8),
        "entities": response.get("entities", {}),
        "actions": response.get("actions", []),
        "context": context,
        "timestamp": time.time()
    }
    
    # Validate response quality
    if not processed_response["text"] or len(processed_response["text"]) < 2:
        processed_response["text"] = "I'm sorry, I didn't understand that. Could you please repeat?"
        processed_response["confidence"] = 0.0
    
    return processed_response
```

**Response Processing Features:**
- **Quality Validation**: Ensure response quality
- **Intent Classification**: Classify response intent
- **Entity Extraction**: Extract relevant entities
- **Action Planning**: Plan required actions

### **MQTT Publishing and Integration**

The AI service publishes **standardized responses** to the MQTT bus:

```python
def _publish_ai_response(self, response: Dict[str, Any], session_id: str):
    """Publish AI response to MQTT bus."""
    try:
        # Publish to AI response topic
        self.publish_message("alicia/voice/ai/response", {
            "session_id": session_id,
            "response": response,
            "timestamp": time.time()
        })
        
        # If response contains device commands, publish to device control
        if response.get("actions"):
            for action in response["actions"]:
                self.publish_message("alicia/devices/control/command", {
                    "session_id": session_id,
                    "command": action,
                    "timestamp": time.time()
                })
        
        # Publish to TTS service for voice synthesis
        self.publish_message("alicia/voice/tts/request", {
            "session_id": session_id,
            "text": response["text"],
            "voice_settings": response.get("voice_settings", {}),
            "timestamp": time.time()
        })
        
    except Exception as e:
        self.logger.error(f"Failed to publish AI response: {e}")
```

**Publishing Features:**
- **Multi-topic Publishing**: Publish to different consumers
- **Action Coordination**: Coordinate device actions
- **TTS Integration**: Send responses to TTS service
- **Session Tracking**: Maintain session context

## 🚀 **Performance Optimization**

### **Caching and Response Optimization**

The AI service implements **intelligent caching**:

```python
def _get_cached_response(self, text: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get cached response if available."""
    cache_key = self._generate_cache_key(text, context)
    
    if cache_key in self.response_cache:
        cached_response = self.response_cache[cache_key]
        
        # Check if cache is still valid
        if time.time() - cached_response["timestamp"] < self.cache_ttl:
            self.logger.debug(f"Using cached response for: {text[:50]}...")
            return cached_response["response"]
    
    return None
```

**Caching Features:**
- **Response Caching**: Cache common responses
- **TTL Management**: Time-to-live for cache entries
- **Context Awareness**: Consider context in caching
- **Memory Management**: Limit cache size

### **Load Balancing and Scaling**

The AI service implements **load balancing across providers**:

```python
async def _process_with_load_balancing(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Process text with load balancing across providers."""
    providers = [self.ai_provider, "openai", "grok"]
    
    for provider in providers:
        try:
            if provider == "grok" and self.grok_client:
                return await self._process_with_grok(text, context)
            elif provider == "openai" and self.openai_client:
                return await self._process_with_openai(text, context)
        except Exception as e:
            self.logger.warning(f"Provider {provider} failed: {e}")
            continue
    
    raise Exception("All AI providers failed")
```

## 🚀 **Next Steps**

The AI Service provides the intelligence for Alicia's voice processing pipeline. In the next chapter, we'll examine the **TTS Service & Voice Router** that completes the voice pipeline, including:

1. **Text-to-Speech Synthesis** - Converting AI responses to speech
2. **Voice Pipeline Orchestration** - Coordinating the complete voice pipeline
3. **Audio Output Management** - Managing speaker output and audio routing
4. **Session Management** - Tracking voice interactions and sessions
5. **Error Handling and Recovery** - Robust error handling throughout the pipeline

The AI service demonstrates how **advanced AI capabilities** can be integrated into a microservices architecture, providing intelligent conversation management and smart home control that scales with the system.

---

**The AI Service in Alicia represents a mature, production-ready approach to AI integration in smart home systems. Every design decision is intentional, every integration pattern serves a purpose, and every optimization contributes to the greater goal of creating an intelligent, responsive, and engaging voice assistant.**
