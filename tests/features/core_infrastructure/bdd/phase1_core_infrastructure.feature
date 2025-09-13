# Phase 1: Core Infrastructure Testing
# Testing foundational services and MQTT bus connectivity

Feature: Core Infrastructure Services
  As a system administrator
  I want to ensure core infrastructure services are working properly
  So that the Alicia Smart Home AI Assistant has a solid foundation

  Background:
    Given the MQTT broker is running
    And the core infrastructure services are deployed
    And all services are healthy

  Scenario: MQTT Broker Connectivity
    Given the MQTT broker is accessible
    When I connect to the MQTT broker
    Then I should be able to publish messages
    And I should be able to subscribe to topics
    And the connection should be stable

  Scenario: Security Gateway Service
    Given the Security Gateway service is running
    When I check the service health
    Then the service should be healthy
    And it should be registered with the device registry
    And it should be listening on MQTT topics
    And it should respond to authentication requests

  Scenario: Device Registry Service
    Given the Device Registry service is running
    When I check the service health
    Then the service should be healthy
    And it should maintain a list of registered services
    And it should respond to service discovery requests
    And it should track service capabilities

  Scenario: Discovery Service
    Given the Discovery Service is running
    When I check the service health
    Then the service should be healthy
    And it should discover new services automatically
    And it should register services with the device registry
    And it should handle service unregistration

  Scenario: Service Communication via MQTT
    Given all core services are running
    When services communicate via MQTT
    Then messages should be delivered reliably
    And services should respond to requests
    And error handling should work properly
    And message routing should be correct

  Scenario: Service Health Monitoring
    Given all core services are running
    When I check service health endpoints
    Then all services should report healthy status
    And health metrics should be available
    And service uptime should be tracked
    And error counts should be monitored

  Scenario: Service Registration and Discovery
    Given the Device Registry is running
    When a new service starts up
    Then it should register itself with the registry
    And other services should discover it
    And its capabilities should be recorded
    And it should appear in service listings

  Scenario: MQTT Topic Structure
    Given the MQTT broker is running
    When I examine the topic structure
    Then topics should follow the alicia/ namespace
    And service-specific topics should be organized
    And wildcard subscriptions should work
    And topic permissions should be enforced

  Scenario: Error Handling and Recovery
    Given all core services are running
    When a service encounters an error
    Then it should log the error appropriately
    And it should attempt recovery
    And other services should continue functioning
    And the error should be reported to monitoring

  Scenario: Configuration Management
    Given the core services are running
    When I check service configurations
    Then services should load configurations correctly
    And environment variables should be respected
    And default values should be used when needed
    And configuration changes should be applied




