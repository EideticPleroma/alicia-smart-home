Feature: Sonos Integration Testing
  As a smart home system
  I want to ensure seamless integration between components
  So that all services work together reliably

  Background:
    Given the MQTT broker is running
    And the Sonos MQTT bridge is connected
    And Home Assistant is running
    And at least one Sonos speaker is available

  Scenario: Home Assistant entity discovery
    Given Home Assistant is configured for Sonos
    When the bridge discovers speakers
    Then Home Assistant should create media player entities
    And entity states should match speaker status
    And entities should be controllable from HA interface

  Scenario: Voice assistant TTS integration
    Given the voice processing pipeline is active
    When a voice command triggers TTS
    Then the TTS request should be forwarded to MQTT
    And the appropriate speaker should receive the message
    And playback confirmation should return to voice assistant

  Scenario: MQTT topic consistency across services
    Given multiple services are connected to MQTT
    When status messages are published
    Then all services should receive consistent topic formats
    And message payloads should be parseable by all consumers
    And no topic conflicts should occur

  Scenario: Docker container communication
    Given services are running in Docker containers
    When MQTT messages are exchanged
    Then network isolation should not affect communication
    And container logs should show successful message processing
    And cross-container timing should be synchronized

  Scenario: Home Assistant automation triggers
    Given Home Assistant automations are configured
    When speaker events occur
    Then automations should trigger appropriately
    And automation actions should execute on speakers
    And automation logs should show successful execution

  Scenario: Status synchronization between services
    Given multiple services monitor speaker status
    When speaker state changes
    Then all services should receive status updates
    And status information should be consistent across services
    And no stale status information should persist

  Scenario: Error propagation across services
    Given an error occurs in the MQTT bridge
    When the error is published
    Then Home Assistant should receive the error
    And voice assistant should be notified if applicable
    And error information should be preserved across services

  Scenario: Configuration synchronization
    Given configuration changes in one service
    When the configuration is updated
    Then other services should receive configuration updates
    And services should adapt to new configuration
    And no service restarts should be required

  Scenario: Service health monitoring
    Given all services are running
    When health checks are performed
    Then MQTT connectivity should be verified
    And service responsiveness should be confirmed
    And health status should be published to monitoring

  Scenario: Cross-service command validation
    Given commands originate from different services
    When commands are validated
    Then authorization should be checked per service
    And command parameters should be validated consistently
    And invalid commands should be rejected uniformly

  Scenario: Data persistence across service restarts
    Given services have persistent data
    When services are restarted
    Then configuration should be restored
    And speaker states should be rediscovered
    And ongoing operations should resume appropriately

  Scenario: Time synchronization between services
    Given services run on different hosts
    When timestamped events occur
    Then event timing should be synchronized
    And event ordering should be preserved
    And time-based automations should work correctly

  Scenario: Resource sharing between services
    Given services share MQTT broker resources
    When high load occurs
    Then resource allocation should be fair
    And no service should be starved of resources
    And broker performance should remain stable

  Scenario: Service dependency management
    Given services have startup dependencies
    When the system starts
    Then services should start in correct order
    And dependency checks should pass
    And circular dependencies should be detected

  Scenario: Message routing and filtering
    Given multiple message types exist
    When messages are published
    Then correct services should receive relevant messages
    And irrelevant messages should be filtered out
    And message routing should be efficient

  Scenario: Backup and recovery integration
    Given backup systems are configured
    When data needs to be backed up
    Then speaker configurations should be included
    And automation configurations should be preserved
    And recovery procedures should restore all services

  Scenario: Update coordination between services
    Given service updates are available
    When updates are applied
    Then services should coordinate update timing
    And no service disruption should occur during updates
    And rollback procedures should be available

  Scenario: Multi-zone audio synchronization
    Given speakers are in different rooms
    When synchronized playback is requested
    Then audio timing should be coordinated
    And network latency should be compensated
    And synchronization should be maintained

  Scenario: Energy monitoring integration
    Given energy monitoring is enabled
    When speakers are active
    Then power consumption should be tracked
    And energy data should be published to MQTT
    And energy-efficient modes should be available

  Scenario: Security event integration
    Given security systems are integrated
    When security events occur
    Then speakers can be used for alerts
    And audio can be muted during security events
    And security status should affect speaker behavior

  Scenario: Weather integration for audio
    Given weather services are connected
    When weather conditions change
    Then indoor speakers can adjust volume
    And outdoor speakers can be weather-protected
    And weather-appropriate audio can be selected
