Feature: Sonos Error Handling and Resilience
  As a smart home system
  I want to handle errors gracefully
  So that the system remains stable and provides feedback

  Background:
    Given the MQTT broker is running
    And the Sonos MQTT bridge is connected
    And at least one Sonos speaker is available

  Scenario: Handle MQTT broker disconnection gracefully
    Given the MQTT broker connection is lost
    When the bridge attempts to reconnect
    Then the bridge should retry connection automatically
    And log reconnection attempts
    And continue processing when connection is restored

  Scenario: Handle speaker discovery failure
    Given the network discovery process fails
    When the bridge attempts to find speakers
    Then an error should be logged
    And the bridge should retry discovery periodically
    And notify the system of discovery failure

  Scenario: Handle invalid JSON payload
    When an invalid JSON message is received
    Then the message should be rejected
    And an error should be logged
    And the bridge should continue processing other messages

  Scenario: Handle speaker hardware failure
    Given a speaker becomes unresponsive
    When commands are sent to the failed speaker
    Then an error status should be published
    And the speaker should be marked as unavailable
    And alternative speakers should remain functional

  Scenario: Handle volume command with invalid value
    When a volume command with value 150 is sent
    Then the command should be rejected
    And an error should be logged
    And the speaker volume should remain unchanged

  Scenario: Handle TTS request for unknown speaker
    When a TTS request is sent for "unknown_speaker"
    Then the request should be rejected
    And an error status should be published
    And available speakers should be listed in the error

  Scenario: Handle group creation with invalid speakers
    When a group command includes non-existent speakers
    Then the command should be partially successful
    And valid speakers should be grouped
    And invalid speakers should be reported in error status

  Scenario: Handle network timeout during command execution
    Given a command is sent to a speaker
    When the network request times out
    Then the command should be retried
    And a timeout error should be logged
    And the system should remain stable

  Scenario: Handle concurrent command conflicts
    Given multiple volume commands are sent simultaneously
    When commands conflict with each other
    Then the last valid command should take precedence
    And previous commands should be logged
    And no system crashes should occur

  Scenario: Handle memory exhaustion gracefully
    Given the system is under memory pressure
    When large TTS messages are processed
    Then memory usage should be monitored
    And large messages should be rejected if needed
    And the system should recover automatically

  Scenario: Handle speaker firmware update interruption
    Given a speaker is updating firmware
    When commands are sent during update
    Then commands should be queued
    And update completion should be monitored
    And queued commands should execute after update

  Scenario: Handle MQTT topic authorization failure
    When a command is sent to unauthorized topic
    Then the message should be rejected
    And a security error should be logged
    And no unauthorized actions should be performed

  Scenario: Handle speaker name conflicts
    Given two speakers have similar names
    When commands use ambiguous names
    Then the command should request clarification
    And both speakers should be listed
    And no incorrect speaker should be controlled

  Scenario: Handle playback command during TTS
    Given TTS is currently playing
    When a playback command is received
    Then the TTS should complete first
    And the playback command should be queued
    And status should reflect the queue state

  Scenario: Handle group dissolution failure
    Given a speaker group exists
    When group dissolution fails
    Then partial dissolution should be attempted
    And remaining group members should be notified
    And error status should be published

  Scenario: Handle configuration file corruption
    Given the bridge configuration is corrupted
    When the bridge starts
    Then default configuration should be used
    And a configuration error should be logged
    And the system should continue with defaults
