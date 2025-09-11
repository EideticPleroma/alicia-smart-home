# Grok Integration Guide for Alicia Voice Assistant

## Overview

This guide explains how to integrate Grok (xAI's language model) with your Alicia voice assistant system, including context management and prompt generation layers.

## Architecture

```
Voice Input → STT (Whisper) → Context Manager → Prompt Generator → Grok API → Response Processor → TTS (Piper) → Sonos
```

### Key Components

1. **GrokHandler**: Main API client with OpenAI compatibility
2. **ConversationContext**: Manages conversation history and device states
3. **PromptGenerator**: Creates contextual prompts for Grok
4. **Context Integration**: Seamlessly integrates with existing voice pipeline

## Setup Instructions

### 1. Get Grok API Key

1. Visit [x.ai](https://x.ai/api) and sign up
2. Generate an API key from your dashboard
3. Set environment variable:
   ```bash
   export XAI_API_KEY="your-api-key-here"
   ```

### 2. Install Dependencies

```bash
cd voice-processing
pip install -r requirements.txt
```

### 3. Enable Grok Integration

Update `voice-processing/config/assistant_config.yaml`:

```yaml
llm:
  enabled: true
  provider: "grok"
  api_key: "${XAI_API_KEY}"
  model: "grok-2-1212"
  endpoint: "https://api.x.ai/v1"
  temperature: 0.7
  max_tokens: 200
  context_length: 4000
  rate_limit: 1.0
```

### 4. Test Integration

```bash
# Set your API key
export XAI_API_KEY="your-key-here"

# Run comprehensive tests
python test_grok_integration.py
```

## Features

### Context Management

The system maintains rich context including:

- **Conversation History**: Recent user/assistant exchanges
- **Device States**: Current status of smart home devices
- **User Preferences**: Personalized settings and preferences
- **System Context**: Home Assistant states and sensor data

### Prompt Generation

Intelligent prompt generation that:

- **Builds System Prompts**: Defines Alicia's personality and capabilities
- **Includes Context**: Incorporates device states and conversation history
- **Manages Token Limits**: Automatically trims context to stay within limits
- **Optimizes for Voice**: Generates concise responses suitable for TTS

### Rate Limiting

Built-in rate limiting to respect API limits:

- **Configurable Intervals**: Default 1 second between requests
- **Queue Management**: Handles multiple simultaneous requests
- **Error Recovery**: Graceful fallback to basic processing

## Usage Examples

### Basic Voice Commands

```python
# Initialize handler
from grok_handler import create_grok_handler
grok = create_grok_handler()

# Process voice command
response = await grok.process_command("Turn on the kitchen light")
# Response: "I'll turn on the kitchen light for you."
```

### Context-Aware Conversations

```python
# First command
response1 = await grok.process_command("Turn on the kitchen light")
# Response: "I'll turn on the kitchen light for you."

# Follow-up command (uses context)
response2 = await grok.process_command("What's the temperature?")
# Response: "The current temperature is 22°C. The kitchen light is on."
```

### Device Context Integration

```python
# Update device states
device_context = {
    "kitchen_light": "on",
    "temperature": "22°C",
    "motion_detected": True
}
grok.update_device_context(device_context)

# Process command with context
response = await grok.process_command("What's the status?")
# Response: "The kitchen light is on, temperature is 22°C, and motion was detected."
```

## Configuration Options

### Grok Models

- **grok-2-1212**: Latest model with 128k context window
- **grok-2-vision-1212**: Multimodal model with image support

### Context Settings

```yaml
conversation:
  max_history: 50          # Maximum conversation history
  session_timeout: 300     # Session timeout in seconds
  response_timeout: 10     # Response timeout in seconds

llm:
  context_length: 4000     # Maximum context tokens
  temperature: 0.7         # Response creativity (0-1)
  max_tokens: 200          # Maximum response length
  rate_limit: 1.0          # Seconds between requests
```

## Integration with Existing Pipeline

### Voice Processing Flow

1. **STT Output**: Whisper converts speech to text
2. **Context Retrieval**: System gathers device states and conversation history
3. **Prompt Generation**: Creates contextual prompt for Grok
4. **Grok Processing**: Sends request to Grok API
5. **Response Processing**: Formats response for TTS
6. **TTS Output**: Piper converts response to speech
7. **Sonos Playback**: Audio plays through speakers

### MQTT Integration

The system publishes context updates via MQTT:

```json
{
  "topic": "alicia/context/update",
  "payload": {
    "session_id": "uuid",
    "device_context": {...},
    "conversation_length": 5,
    "timestamp": 1234567890
  }
}
```

## Error Handling

### API Errors

- **Rate Limiting**: Automatic retry with exponential backoff
- **Authentication**: Clear error messages for invalid API keys
- **Network Issues**: Graceful fallback to basic processing
- **Timeout**: Configurable timeout with fallback responses

### Fallback Strategy

If Grok processing fails:

1. Log the error
2. Fall back to basic command processing
3. Return helpful error message
4. Continue normal operation

## Monitoring and Debugging

### Logging

The system provides comprehensive logging:

```python
# Enable debug logging
import logging
logging.getLogger('grok_handler').setLevel(logging.DEBUG)
```

### Context Inspection

```python
# Get current context summary
context_summary = grok.get_context_summary()
print(json.dumps(context_summary, indent=2))
```

### Health Checks

```python
# Check Grok handler health
if hasattr(assistant, 'grok_handler'):
    context = grok.get_context_summary()
    print(f"Grok handler active: {context['session_id']}")
```

## Performance Considerations

### Token Management

- **Context Trimming**: Automatically removes old messages
- **Token Estimation**: Rough estimation (4 chars per token)
- **Model Limits**: Respects Grok's context window limits

### Rate Limiting

- **API Limits**: Respects xAI's rate limits
- **Queue Management**: Handles concurrent requests
- **Retry Logic**: Exponential backoff for failed requests

### Memory Usage

- **Context Storage**: In-memory conversation history
- **Session Management**: Automatic cleanup of old sessions
- **Device States**: Lightweight device context storage

## Security Considerations

### API Key Management

- **Environment Variables**: Store API keys securely
- **Docker Secrets**: Use Docker secrets for production
- **Key Rotation**: Regular API key rotation

### Data Privacy

- **Local Processing**: STT/TTS processed locally
- **Context Storage**: Conversation history stored locally
- **API Calls**: Only text sent to Grok API

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```bash
   export XAI_API_KEY="your-key-here"
   ```

2. **Rate Limiting Errors**
   - Increase `rate_limit` in config
   - Check API usage limits

3. **Context Too Long**
   - Reduce `context_length` in config
   - Check conversation history size

4. **Network Issues**
   - Check internet connectivity
   - Verify API endpoint accessibility

### Debug Commands

```bash
# Test basic connection
python -c "from grok_handler import create_grok_handler; print('OK')"

# Test with API key
python -c "import os; print('API Key:', 'SET' if os.getenv('XAI_API_KEY') else 'NOT SET')"

# Run full test suite
python test_grok_integration.py
```

## Next Steps

1. **Set up API key** and test basic integration
2. **Configure device context** integration with Home Assistant
3. **Customize prompts** for your specific use case
4. **Monitor performance** and adjust settings
5. **Scale up** for production use

## Support

For issues or questions:

1. Check the test suite output
2. Review logs for error messages
3. Verify API key and network connectivity
4. Test with simple commands first

The Grok integration is designed to be robust and fallback gracefully, ensuring your voice assistant continues working even if the LLM service is unavailable.
