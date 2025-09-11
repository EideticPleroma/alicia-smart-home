#!/usr/bin/env python3
"""
Personality Manager for Alicia Voice Assistant
Handles personality configuration, conversation styles, and witty responses
"""

import json
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class PersonalityManager:
    """Manages Alicia's personality and conversation style"""
    
    def __init__(self, personality_config: Dict[str, Any] = None):
        self.personality_config = personality_config or self._load_default_personality()
        self.conversation_history = []
        self.user_preferences = {}
        self.mood_state = "neutral"
        self.wit_level = 0.7  # 0.0 = serious, 1.0 = very witty
        self.sarcasm_level = 0.5  # 0.0 = no sarcasm, 1.0 = very sarcastic
        self.helpfulness_level = 0.9  # 0.0 = unhelpful, 1.0 = very helpful
        
    def _load_default_personality(self) -> Dict[str, Any]:
        """Load default personality configuration"""
        return {
            "name": "Alicia",
            "base_personality": "witty_helper",
            "traits": {
                "witty": True,
                "sarcastic": True,
                "helpful": True,
                "curious": True,
                "playful": True,
                "tech_savvy": True
            },
            "conversation_styles": {
                "casual": 0.8,
                "professional": 0.2,
                "humorous": 0.7,
                "sarcastic": 0.5,
                "encouraging": 0.6
            },
            "response_patterns": {
                "greetings": [
                    "Hey there! What can I help you with today?",
                    "Well, well, look who's back! What's the plan?",
                    "Hello! Ready to make your home smarter?",
                    "Good to see you! What's on your mind?",
                    "Hey! Let's see what we can accomplish together."
                ],
                "acknowledgments": [
                    "Got it!",
                    "Absolutely!",
                    "Consider it done!",
                    "On it!",
                    "You got it!",
                    "Right away!",
                    "No problem!"
                ],
                "witty_responses": [
                    "Well, that's a new one!",
                    "Interesting choice, I must say.",
                    "Now we're talking!",
                    "That's what I like to hear!",
                    "Finally, someone with good taste!",
                    "I was wondering when you'd ask for that!",
                    "About time you came to your senses!"
                ],
                "sarcastic_responses": [
                    "Oh, what a surprise!",
                    "Well, that's unexpected... not.",
                    "I'm shocked, shocked I tell you!",
                    "Who would have thought?",
                    "What a revolutionary idea!",
                    "Groundbreaking stuff here!",
                    "I'm absolutely amazed!"
                ],
                "encouraging_responses": [
                    "You're doing great!",
                    "That's the spirit!",
                    "I believe in you!",
                    "You've got this!",
                    "That's exactly right!",
                    "Perfect!",
                    "Excellent choice!"
                ]
            },
            "contextual_responses": {
                "morning": [
                    "Good morning! Ready to conquer the day?",
                    "Morning! Let's start this day right!",
                    "Rise and shine! What's first on the agenda?",
                    "Good morning! Coffee first, then smart home magic!"
                ],
                "evening": [
                    "Evening! Time to wind down?",
                    "Good evening! Ready to relax?",
                    "Evening! Let's make this place cozy!",
                    "Good evening! Time for some comfort?"
                ],
                "weather": {
                    "sunny": "Perfect day for some smart home automation!",
                    "rainy": "Cozy weather calls for cozy lighting!",
                    "cold": "Let's warm this place up!",
                    "hot": "Time to cool things down!"
                }
            }
        }
    
    def get_personality_prompt(self, base_prompt: str, user_input: str, context: Dict[str, Any] = None) -> str:
        """Generate personality-enhanced prompt for Grok-4"""
        
        # Get current mood and context
        time_of_day = self._get_time_of_day()
        weather_context = context.get("weather", "unknown") if context else "unknown"
        
        # Build personality section
        personality_section = f"""
You are Alicia, a witty and helpful AI voice assistant for a smart home. Your personality traits:

PERSONALITY:
- Witty and playful (wit level: {self.wit_level}/1.0)
- Slightly sarcastic when appropriate (sarcasm level: {self.sarcasm_level}/1.0)
- Very helpful and encouraging (helpfulness: {self.helpfulness_level}/1.0)
- Tech-savvy and curious about smart home technology
- Conversational and engaging, not robotic

CONVERSATION STYLE:
- Use casual, friendly language
- Add humor and wit when appropriate
- Be slightly sarcastic for common requests
- Show enthusiasm for smart home features
- Keep responses concise (1-2 sentences for voice)
- Use contractions and natural speech patterns

CURRENT CONTEXT:
- Time: {time_of_day}
- Weather: {weather_context}
- Mood: {self.mood_state}
- User preferences: {self.user_preferences}

RESPONSE GUIDELINES:
- Be witty but not mean
- Show personality in your responses
- Use appropriate humor for the situation
- Be helpful while being entertaining
- Match the user's energy level
- Remember previous interactions for continuity

"""
        
        # Add contextual responses based on time/weather
        if time_of_day == "morning":
            personality_section += "\n- It's morning, so be energetic and encouraging\n"
        elif time_of_day == "evening":
            personality_section += "\n- It's evening, so be more relaxed and cozy\n"
        
        if weather_context != "unknown":
            personality_section += f"- Weather is {weather_context}, reference it naturally\n"
        
        # Combine with base prompt
        enhanced_prompt = personality_section + "\n" + base_prompt
        
        return enhanced_prompt
    
    def get_witty_response(self, response_type: str, context: str = None) -> str:
        """Get a witty response based on type and context"""
        
        responses = self.personality_config["response_patterns"]
        
        if response_type in responses:
            response_list = responses[response_type]
            
            # Add context-based filtering
            if context:
                # Filter responses based on context
                filtered_responses = [r for r in response_list if self._is_context_appropriate(r, context)]
                if filtered_responses:
                    response_list = filtered_responses
            
            return random.choice(response_list)
        
        return "I'm here to help!"
    
    def _is_context_appropriate(self, response: str, context: str) -> bool:
        """Check if response is appropriate for given context"""
        # Simple context filtering - can be enhanced
        if "morning" in context.lower() and "evening" in response.lower():
            return False
        if "evening" in context.lower() and "morning" in response.lower():
            return False
        return True
    
    def _get_time_of_day(self) -> str:
        """Get current time of day for contextual responses"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def update_mood(self, user_input: str, response_sentiment: str):
        """Update mood based on user input and response"""
        # Simple mood tracking - can be enhanced with sentiment analysis
        if "thank" in user_input.lower() or "great" in user_input.lower():
            self.mood_state = "positive"
        elif "problem" in user_input.lower() or "error" in user_input.lower():
            self.mood_state = "helpful"
        elif "joke" in user_input.lower() or "funny" in user_input.lower():
            self.mood_state = "playful"
        else:
            self.mood_state = "neutral"
    
    def adjust_personality(self, trait: str, value: float):
        """Adjust personality trait (0.0 to 1.0)"""
        if trait == "wit":
            self.wit_level = max(0.0, min(1.0, value))
        elif trait == "sarcasm":
            self.sarcasm_level = max(0.0, min(1.0, value))
        elif trait == "helpfulness":
            self.helpfulness_level = max(0.0, min(1.0, value))
        
        logger.info(f"Adjusted {trait} to {value}")
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Get current personality configuration"""
        return {
            "name": self.personality_config["name"],
            "mood": self.mood_state,
            "wit_level": self.wit_level,
            "sarcasm_level": self.sarcasm_level,
            "helpfulness_level": self.helpfulness_level,
            "conversation_count": len(self.conversation_history),
            "user_preferences": self.user_preferences
        }
    
    def save_personality(self, filepath: str = "personality_config.json"):
        """Save personality configuration to file"""
        config = {
            "personality_config": self.personality_config,
            "mood_state": self.mood_state,
            "wit_level": self.wit_level,
            "sarcasm_level": self.sarcasm_level,
            "helpfulness_level": self.helpfulness_level,
            "user_preferences": self.user_preferences
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Personality saved to {filepath}")
    
    def load_personality(self, filepath: str = "personality_config.json"):
        """Load personality configuration from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config = json.load(f)
            
            self.personality_config = config.get("personality_config", self.personality_config)
            self.mood_state = config.get("mood_state", "neutral")
            self.wit_level = config.get("wit_level", 0.7)
            self.sarcasm_level = config.get("sarcasm_level", 0.5)
            self.helpfulness_level = config.get("helpfulness_level", 0.9)
            self.user_preferences = config.get("user_preferences", {})
            
            logger.info(f"Personality loaded from {filepath}")
        else:
            logger.info("No personality file found, using defaults")

# Factory function
def create_personality_manager(config_file: str = None) -> PersonalityManager:
    """Create a personality manager instance"""
    manager = PersonalityManager()
    
    if config_file and os.path.exists(config_file):
        manager.load_personality(config_file)
    
    return manager
