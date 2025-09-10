Feature: Sonos Edge Cases and Boundary Testing
  As a smart home system
  I want to handle edge cases and boundary conditions
  So that the system works reliably in all scenarios

  Background:
    Given the MQTT broker is running
    And the Sonos MQTT bridge is connected
    And at least one Sonos speaker is available

  Scenario: Handle maximum volume level (100)
    When I set the volume to 100
    Then the speaker volume should be 100
    And the volume change should be confirmed via MQTT
    And no audio distortion should occur

  Scenario: Handle minimum volume level (0)
    When I set the volume to 0
    Then the speaker volume should be 0
    And the speaker should be muted
    And the volume change should be confirmed via MQTT

  Scenario: Handle very long TTS messages
    Given a TTS message longer than 1000 characters
    When the message is sent to a speaker
    Then the message should be processed successfully
    And playback should complete without interruption
    And memory usage should remain stable

  Scenario: Handle special characters in TTS messages
    When I send a TTS message with "special chars: @#$%^&*()_+-=[]{}|;:,.<>?"
    Then the message should be processed correctly
    And special characters should be handled appropriately
    And the message should play without errors

  Scenario: Handle Unicode characters in TTS messages
    When I send a TTS message with "Unicode: ñáéíóú 中文 🚀 🎵"
    Then Unicode characters should be processed
    And the message should play correctly
    And encoding should be preserved

  Scenario: Handle empty TTS messages
    When I send an empty TTS message
    Then the request should be rejected
    And an appropriate error should be logged
    And no audio should be played

  Scenario: Handle multiple speakers with same base name
    Given speakers "living_room" and "living_room_2" exist
    When I send commands using partial names
    Then the correct speaker should be identified
    And commands should be routed accurately
    And no speaker confusion should occur

  Scenario: Handle rapid successive volume changes
    When I send 10 volume commands in rapid succession
    Then all commands should be processed
    And the final volume should be the last requested value
    And no commands should be lost

  Scenario: Handle maximum group size (10 speakers)
    Given 10 speakers are available
    When I create a group with all 10 speakers
    Then the group should be created successfully
    And all speakers should be synchronized
    And group status should be published

  Scenario: Handle zero-volume TTS announcements
    When I send a TTS message with volume 0
    Then the announcement should be silent
    And the original volume should be restored
    And no audio artifacts should remain

  Scenario: Handle extremely short TTS messages
    When I send a TTS message "Hi"
    Then the message should play completely
    And volume transitions should be smooth
    And no clipping should occur

  Scenario: Handle speaker name with spaces and special chars
    Given a speaker named "Living Room (Main)"
    When I send commands using the full name
    Then the speaker should respond correctly
    And name parsing should handle special characters
    And MQTT topics should be formatted properly

  Scenario: Handle concurrent TTS requests to same speaker
    Given a TTS message is currently playing
    When a second TTS request arrives
    Then the second request should be queued
    And the first message should complete
    And the queued message should play after

  Scenario: Handle volume changes during TTS playback
    Given TTS is playing at volume 50
    When I change volume to 30 during playback
    Then TTS should continue at new volume
    And volume change should take effect immediately
    And original volume should be restored after TTS

  Scenario: Handle playback commands during group operations
    Given speakers are being grouped
    When playback commands are sent during grouping
    Then commands should be queued
    And grouping should complete first
    And queued commands should execute after

  Scenario: Handle speaker disconnection during group playback
    Given a group is playing music
    When one speaker disconnects from the network
    Then the group should continue with remaining speakers
    And disconnection should be logged
    And group status should be updated

  Scenario: Handle invalid speaker IP addresses
    Given a speaker has an invalid IP configuration
    When commands are sent to the speaker
    Then network errors should be handled gracefully
    And alternative connection methods should be attempted
    And the speaker should be marked for rediscovery

  Scenario: Handle MQTT message size limits
    When an MQTT message exceeds size limits
    Then the message should be rejected
    And an appropriate error should be published
    And the system should continue functioning

  Scenario: Handle rapid speaker discovery and loss
    Given speakers are being discovered
    When speakers rapidly connect and disconnect
    Then the discovery process should be stable
    And speaker lists should be updated accurately
    And no memory leaks should occur

  Scenario: Handle timezone and timestamp accuracy
    When status messages are published
    Then timestamps should be accurate
    And timezone information should be included
    And timestamps should be consistent across messages
