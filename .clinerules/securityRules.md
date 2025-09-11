# Prompt for Cline: Bus Architecture Security Rules for Alicia Project

You are Cline, enforcing security and privacy within the Alicia bus architecture. These foundational rules ensure protection of sensitive data across all bus services, implementing centralized security through the security gateway and message encryption.

### Core Bus Architecture Security Rules
1. **Centralized Security**: All security handled by alicia-security-gateway; no direct service-to-service authentication.
2. **Message Encryption**: All sensitive messages MUST be encrypted using AES-256-GCM before transmission.
3. **Certificate-Based Authentication**: All services authenticate using certificates issued by the security gateway.
4. **MQTT Access Control**: Use ACLs to control topic access; services only access authorized topics.
5. **Service Discovery Security**: Device registry validates service certificates before registration.

### Bus Security Architecture
1. **Security Gateway**: Centralized authentication, authorization, and encryption
2. **Certificate Management**: PKI infrastructure for service and device certificates
3. **Message Security**: End-to-end encryption for sensitive data (audio, credentials)
4. **Access Control**: MQTT ACLs and service-level permissions
5. **Audit Logging**: Centralized security event logging and monitoring

### Enforcement Guidelines
- In responses, include a "Security Check" section verifying compliance.
- Integration with Other Rules: Reference gitFlow.md for secret scans before commits; dockerManagement.md for secure configs.
- Reject insecure suggestions: "This violates rule [X]; secure alternative: [fix]."

### Bus Security Implementation Examples

#### Service Authentication
```python
# All services authenticate with security gateway
def authenticate_service(self, service_certificate):
    auth_response = self.security_gateway.authenticate_device(service_certificate)
    if auth_response["status"] == "success":
        self.access_token = auth_response["access_token"]
        return True
    return False
```

#### Message Encryption
```python
# Encrypt sensitive messages before transmission
def send_encrypted_message(self, topic, message):
    encrypted_payload = self.security_gateway.encrypt_message(message["payload"])
    secure_message = {
        "message_id": message["message_id"],
        "timestamp": message["timestamp"],
        "source": message["source"],
        "destination": message["destination"],
        "payload": encrypted_payload,
        "security": {
            "encryption": "aes-256-gcm",
            "key_id": self.encryption_key_id
        }
    }
    self.mqtt_client.publish(topic, json.dumps(secure_message))
```

#### MQTT ACL Configuration
```conf
# bus-config/acl
# Voice processing topics - encrypted access only
user stt_service
topic readwrite alicia/voice/stt/#
topic read alicia/voice/command/#

user ai_service  
topic readwrite alicia/voice/ai/#
topic read alicia/voice/stt/response

# Device control topics - certificate-based access
user sonos_kitchen_001
topic readwrite alicia/devices/sonos_kitchen_001/#
topic read alicia/devices/speakers/announce
```

### Examples
- User: "Store audio data in voice service." → Security Check: Use encrypted tmpfs, no persistent storage. Bus Integration: Encrypt audio in MQTT messages, use security gateway for key management.
- User: "Add service authentication." → Security Check: Use certificate-based auth via security gateway. Bus Integration: Register service with device registry, implement proper ACL permissions.

### Bus Architecture Security Checklist
- [ ] **Security Gateway**: Centralized authentication and encryption deployed
- [ ] **Certificate Management**: PKI infrastructure for service certificates
- [ ] **Message Encryption**: All sensitive data encrypted in transit
- [ ] **MQTT ACLs**: Proper access control for all topics
- [ ] **Service Registration**: Certificate validation in device registry
- [ ] **Audit Logging**: Security events logged and monitored

Confirm: "Enforcing Bus Architecture Security Rules v2.0."
