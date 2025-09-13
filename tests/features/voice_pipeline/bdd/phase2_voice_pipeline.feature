# Phase 2: Voice Processing Pipeline Testing
# Testing complete voice processing workflow

Feature: Voice Processing Pipeline
  As a user
  I want to interact with Alicia using voice commands
  So that I can control my smart home naturally

  Background:
    Given the MQTT broker is running
    And the voice processing services are deployed
    And all voice services are healthy

  Scenario: Speech-to-Text Processing
    Given the STT Service is running
    When I send an audio file to the STT service
    Then it should transcribe the audio to text
    And the transcription should be accurate
    And the result should be published to MQTT
    And the service should respond within 2 seconds

  Scenario: AI Processing
    Given the AI Service is running
    When I send a text message to the AI service
    Then it should process the natural language
    And it should generate an appropriate response
    And it should maintain conversation context
    And the response should be published to MQTT

  Scenario: Text-to-Speech Processing
    Given the TTS Service is running
    When I send text to the TTS service
    Then it should generate audio output
    And the audio should be clear and natural
    And the audio should be published to MQTT
    And the service should respond within 2 seconds

  Scenario: Voice Router Orchestration
    Given the Voice Router is running
    When I send a voice command through the router
    Then it should coordinate the STT, AI, and TTS services
    And it should handle the complete voice pipeline
    And it should manage service dependencies
    And it should provide status updates via MQTT

  Scenario: End-to-End Voice Command
    Given all voice services are running
    When I say "Turn on the living room lights"
    Then the audio should be transcribed to text
    And the AI should understand the command
    And the AI should generate a response
    And the response should be converted to speech
    And the complete pipeline should complete within 5 seconds

  Scenario: Voice Service Health Monitoring
    Given all voice services are running
    When I check the health of voice services
    Then all services should report healthy status
    And response times should be within limits
    And error rates should be low
    And services should be processing requests

  Scenario: Voice Service Error Handling
    Given all voice services are running
    When a voice service encounters an error
    Then it should log the error appropriately
    And it should attempt recovery
    And other services should continue functioning
    And the error should be reported to monitoring

  Scenario: Voice Service Load Balancing
    Given multiple instances of voice services are running
    When I send multiple voice commands
    Then the load should be distributed evenly
    And all instances should be utilized
    And response times should remain consistent
    And no service should be overloaded

  Scenario: Voice Service Configuration
    Given the voice services are running
    When I check service configurations
    Then services should load configurations correctly
    And API keys should be properly configured
    And model settings should be applied
    And language settings should be respected

  Scenario: Voice Service MQTT Communication
    Given all voice services are running
    When services communicate via MQTT
    Then messages should be delivered reliably
    And services should respond to requests
    And message routing should be correct
    And error handling should work properly




