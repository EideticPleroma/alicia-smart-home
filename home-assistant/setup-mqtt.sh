#!/bin/bash

# MQTT Setup Script for Home Assistant
# This script configures MQTT integration via HA REST API
# Designed to run automatically after HA container starts

set -e  # Exit on any error

# Configuration
HA_URL="http://localhost:8123"
HA_API_PASSWORD="${HA_API_PASSWORD:-alicia_ha_api_2024}"
MQTT_HOST="${MQTT_HOST:-172.19.0.2}"
MQTT_PORT="${MQTT_PORT:-1883}"
MQTT_USERNAME="${MQTT_USERNAME:-alicia}"
MQTT_PASSWORD="${MQTT_PASSWORD:-alicia_ha_mqtt_2024}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Wait for Home Assistant to be ready
wait_for_ha() {
    log "Waiting for Home Assistant to be ready..."
    local max_attempts=60
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "${HA_URL}/api/" > /dev/null 2>&1; then
            log "Home Assistant is ready!"
            return 0
        fi

        log "Attempt $attempt/$max_attempts: HA not ready yet, waiting..."
        sleep 5
        ((attempt++))
    done

    error "Home Assistant failed to start within expected time"
    return 1
}

# Check if MQTT integration is already configured
check_mqtt_configured() {
    log "Checking if MQTT integration is already configured..."

    # Get list of config entries
    local response
    response=$(curl -s "${HA_URL}/api/config/config_entries")

    if echo "$response" | grep -q '"domain": "mqtt"'; then
        log "MQTT integration is already configured"
        return 0
    else
        log "MQTT integration not found, will configure it"
        return 1
    fi
}

# Configure MQTT integration via HA API
configure_mqtt() {
    log "Configuring MQTT integration..."

    # Step 1: Initialize MQTT config flow
    local flow_response
    flow_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{}' \
        "${HA_URL}/api/config/config_entries/flow")

    # Extract flow ID from response
    local flow_id
    flow_id=$(echo "$flow_response" | grep -o '"flow_id": "[^"]*' | cut -d'"' -f4)

    if [ -z "$flow_id" ]; then
        error "Failed to initialize MQTT config flow"
        echo "Response: $flow_response"
        return 1
    fi

    log "Initialized config flow with ID: $flow_id"

    # Step 2: Configure MQTT with broker details
    local config_data
    config_data=$(cat <<EOF
{
  "flow_id": "$flow_id",
  "handler": "mqtt",
  "data": {
    "broker": "$MQTT_HOST",
    "port": $MQTT_PORT,
    "username": "$MQTT_USERNAME",
    "password": "$MQTT_PASSWORD"
  }
}
EOF
)

    local config_response
    config_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$config_data" \
        "${HA_URL}/api/config/config_entries/flow")

    if echo "$config_response" | grep -q '"type": "create_entry"'; then
        log "MQTT integration configured successfully!"

        # Step 3: Configure MQTT discovery settings
        log "Configuring MQTT discovery settings..."
        local entry_id
        entry_id=$(echo "$config_response" | grep -o '"entry_id": "[^"]*' | cut -d'"' -f4)

        if [ -n "$entry_id" ]; then
            # Update MQTT options to enable discovery
            local options_data
            options_data=$(cat <<EOF
{
  "discovery": true,
  "discovery_prefix": "homeassistant"
}
EOF
)

            local options_response
            options_response=$(curl -s -X POST \
                -H "Content-Type: application/json" \
                -d "$options_data" \
                "${HA_URL}/api/config/config_entries/options/$entry_id")

            if echo "$options_response" | grep -q '"type": "update_options"'; then
                log "MQTT discovery settings configured successfully!"
            else
                warn "Failed to configure MQTT discovery settings"
                echo "Options response: $options_response"
            fi
        else
            warn "Could not extract entry_id for MQTT discovery configuration"
        fi

        return 0
    else
        error "Failed to configure MQTT integration"
        echo "Response: $config_response"
        return 1
    fi
}

# Main execution
main() {
    log "Starting MQTT setup for Home Assistant..."

    # Wait for HA to be ready
    if ! wait_for_ha; then
        error "Failed to connect to Home Assistant"
        exit 1
    fi

    # Check if MQTT is already configured
    if check_mqtt_configured; then
        log "MQTT setup complete (already configured)"
        exit 0
    fi

    # Configure MQTT
    if configure_mqtt; then
        log "MQTT setup completed successfully!"
        log "Home Assistant will now auto-discover MQTT devices"
    else
        error "MQTT setup failed"
        exit 1
    fi
}

# Run main function
main "$@"
