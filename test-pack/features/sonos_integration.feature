Feature: Sonos Speaker Integration
  As a smart home user
  I want to control Sonos speakers through MQTT
  So that I can play announcements and control audio playback

  Background:
    Given the MQTT broker is running
    And the Sonos MQTT bridge is connected
    And at least one Sonos speaker is available

  Scenario: Discover Sonos speakers on network
    When the bridge scans for Sonos speakers
    Then all available speakers should be discovered
    And speaker information should be published to MQTT

  Scenario: Send TTS announcement to speaker
    Given a speaker named "living_room_sonos" is available
    When I send a TTS message "Hello from Alicia" to the speaker
    Then the speaker should play the announcement
    And a completion status should be published

  Scenario: Control speaker volume
    Given a speaker named "living_room_sonos" is available
    When I set the volume to 50
    Then the speaker volume should be 50
    And the volume change should be confirmed via MQTT

  Scenario: Play/pause music playback
    Given a speaker named "living_room_sonos" is available
    And music is playing on the speaker
    When I send a pause command
    Then the speaker should pause playback
    And the playback state should update to "PAUSED"

  Scenario: Create multi-room audio group
    Given speakers "living_room_sonos" and "kitchen_sonos" are available
    When I create a group with living room as master
    Then both speakers should be in the same group
    And group status should be published to MQTT

  Scenario: Monitor speaker status
    Given a speaker named "living_room_sonos" is available
    When the speaker status is requested
    Then the current status should be published
    Including volume, playback state, and track information

  Scenario: Handle speaker disconnection
    Given a speaker named "living_room_sonos" is available
    When the speaker becomes unreachable
    Then an error status should be published
    And the bridge should attempt reconnection

  Scenario: Process voice assistant TTS request
    Given the voice assistant is active
    When a TTS request is received via MQTT
    Then the message should be forwarded to the appropriate speaker
    And playback confirmation should be sent back
