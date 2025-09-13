"""
Alicia Bus Architecture - Security Gateway Service
Python 3.11.7+, FastAPI 0.104.1+, Paho MQTT 1.6.1+

Centralized security service that handles:
- Device authentication and authorization
- Message encryption/decryption
- Certificate management
- Security event logging
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import paho.mqtt.client as mqtt

from service_wrapper import BusServiceWrapper, BusServiceAPI


class SecurityGateway(BusServiceWrapper):
    """
    Security Gateway service for the Alicia bus architecture.

    Handles all security-related operations:
    - Device certificate validation
    - Message encryption/decryption
    - Access token management
    - Security event logging
    """

    def __init__(self):
        # MQTT configuration
        mqtt_config = {
            "host": os.getenv("MQTT_BROKER", "alicia_bus_core"),
            "port": int(os.getenv("MQTT_PORT", "1883")),
            "username": os.getenv("MQTT_USERNAME", "security_gateway"),
            "password": os.getenv("MQTT_PASSWORD", "alicia_security_2024")
        }

        super().__init__("security_gateway", mqtt_config)

        # Security configuration
        self.encryption_key_path = os.getenv("ENCRYPTION_KEY_PATH", "/app/keys")
        self.certificate_path = os.getenv("CERTIFICATE_PATH", "/app/certs")

        # In-memory stores (in production, use database)
        self.device_certificates: Dict[str, Dict[str, Any]] = {}
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        self.security_events: list = []

        # Setup encryption
        self._setup_encryption()

        # Setup API
        self.api = BusServiceAPI(self)
        self._setup_security_endpoints()

        # Service capabilities
        self.capabilities = [
            "device_authentication",
            "message_encryption",
            "certificate_management",
            "access_control",
            "security_monitoring"
        ]

        self.version = "1.0.0"

        self.logger.info("Security Gateway initialized")

    def _setup_encryption(self):
        """Setup encryption keys and certificates."""
        try:
            # Create directories if they don't exist
            os.makedirs(self.encryption_key_path, exist_ok=True)
            os.makedirs(self.certificate_path, exist_ok=True)

            # Generate or load encryption key
            key_path = os.path.join(self.encryption_key_path, "encryption_key.pem")
            if os.path.exists(key_path):
                with open(key_path, "rb") as f:
                    self.encryption_key = serialization.load_pem_private_key(
                        f.read(), password=None
                    )
            else:
                # Generate new key
                self.encryption_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                # Save key
                pem = self.encryption_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                with open(key_path, "wb") as f:
                    f.write(pem)

            self.logger.info("Encryption setup complete")

        except Exception as e:
            self.logger.error(f"Failed to setup encryption: {e}")
            raise

    def _setup_security_endpoints(self):
        """Setup FastAPI security endpoints."""
        security_scheme = HTTPBearer()

        @self.api.app.post("/auth/device")
        async def authenticate_device(certificate_pem: str):
            """Authenticate device using certificate."""
            try:
                result = self.authenticate_device(certificate_pem)
                if result["success"]:
                    return {
                        "access_token": result["token"],
                        "token_type": "bearer",
                        "expires_in": 3600
                    }
                else:
                    raise HTTPException(status_code=401, detail=result["error"])
            except Exception as e:
                self.logger.error(f"Device authentication error: {e}")
                raise HTTPException(status_code=500, detail="Authentication failed")

        @self.api.app.post("/auth/validate")
        async def validate_token(credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
            """Validate access token."""
            try:
                token = credentials.credentials
                result = self.validate_token(token)
                return result
            except Exception as e:
                self.logger.error(f"Token validation error: {e}")
                raise HTTPException(status_code=401, detail="Invalid token")

        @self.api.app.post("/encrypt")
        async def encrypt_message(message: Dict[str, Any]):
            """Encrypt message for secure transmission."""
            try:
                encrypted = self.encrypt_message(message)
                return {"encrypted_message": encrypted}
            except Exception as e:
                self.logger.error(f"Message encryption error: {e}")
                raise HTTPException(status_code=500, detail="Encryption failed")

        @self.api.app.post("/decrypt")
        async def decrypt_message(encrypted_message: str):
            """Decrypt received message."""
            try:
                decrypted = self.decrypt_message(encrypted_message)
                return {"message": decrypted}
            except Exception as e:
                self.logger.error(f"Message decryption error: {e}")
                raise HTTPException(status_code=500, detail="Decryption failed")

        @self.api.app.get("/certificates")
        async def list_certificates():
            """List registered device certificates."""
            return {"certificates": list(self.device_certificates.keys())}

        @self.api.app.get("/events")
        async def get_security_events(limit: int = 100):
            """Get recent security events."""
            return {"events": self.security_events[-limit:]}

    def subscribe_to_topics(self):
        """Subscribe to security-related topics."""
        topics = [
            "alicia/system/security/auth",
            "alicia/system/security/encrypt",
            "alicia/system/security/validate",
            "alicia/system/discovery/register",
            "alicia/system/health/check"
        ]

        for topic in topics:
            self.mqtt_client.subscribe(topic)

    def process_message(self, topic: str, message: Dict[str, Any]):
        """Process incoming security messages."""
        try:
            if topic == "alicia/system/security/auth":
                self._handle_auth_request(message)
            elif topic == "alicia/system/security/encrypt":
                self._handle_encrypt_request(message)
            elif topic == "alicia/system/security/validate":
                self._handle_validate_request(message)
            elif topic == "alicia/system/discovery/register":
                self._handle_device_registration(message)
            elif topic == "alicia/system/health/check":
                self._handle_health_check(message)

        except Exception as e:
            self.logger.error(f"Error processing security message: {e}")
            self._log_security_event("message_processing_error", {
                "topic": topic,
                "error": str(e),
                "timestamp": time.time()
            })

    def authenticate_device(self, certificate_pem: str) -> Dict[str, Any]:
        """
        Authenticate device using certificate.

        Args:
            certificate_pem: PEM-encoded device certificate

        Returns:
            Authentication result with token or error
        """
        try:
            # Parse certificate
            cert = x509.load_pem_x509_certificate(certificate_pem.encode())

            # Validate certificate (simplified - in production use full CA validation)
            if self._validate_certificate(cert):
                device_id = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

                # Generate access token
                token_data = {
                    "device_id": device_id,
                    "exp": time.time() + 3600,  # 1 hour
                    "iat": time.time(),
                    "iss": "alicia-security-gateway"
                }

                token = jwt.encode(token_data, "alicia_secret_key_2024", algorithm="HS256")

                # Store token
                self.active_tokens[token] = {
                    "device_id": device_id,
                    "issued_at": time.time(),
                    "expires_at": token_data["exp"]
                }

                # Store certificate
                self.device_certificates[device_id] = {
                    "certificate": certificate_pem,
                    "registered_at": time.time(),
                    "last_seen": time.time()
                }

                self._log_security_event("device_authenticated", {
                    "device_id": device_id,
                    "timestamp": time.time()
                })

                return {
                    "success": True,
                    "token": token,
                    "device_id": device_id
                }
            else:
                self._log_security_event("device_authentication_failed", {
                    "certificate_subject": cert.subject.rfc4514_string(),
                    "timestamp": time.time()
                })
                return {
                    "success": False,
                    "error": "Invalid certificate"
                }

        except Exception as e:
            self.logger.error(f"Device authentication failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate access token."""
        try:
            # Decode token
            payload = jwt.decode(token, "alicia_secret_key_2024", algorithms=["HS256"])

            # Check if token is in active tokens
            if token in self.active_tokens:
                token_info = self.active_tokens[token]

                # Check expiration
                if time.time() > token_info["expires_at"]:
                    del self.active_tokens[token]
                    return {"valid": False, "error": "Token expired"}

                return {
                    "valid": True,
                    "device_id": payload["device_id"],
                    "expires_at": payload["exp"]
                }
            else:
                return {"valid": False, "error": "Token not found"}

        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}

    def encrypt_message(self, message: Dict[str, Any]) -> str:
        """Encrypt message for secure transmission."""
        try:
            # Convert message to JSON string
            message_json = json.dumps(message)

            # In a real implementation, use proper encryption
            # For now, return base64 encoded (simplified)
            import base64
            encrypted = base64.b64encode(message_json.encode()).decode()

            self._log_security_event("message_encrypted", {
                "message_id": message.get("message_id", "unknown"),
                "timestamp": time.time()
            })

            return encrypted

        except Exception as e:
            self.logger.error(f"Message encryption failed: {e}")
            raise

    def decrypt_message(self, encrypted_message: str) -> Dict[str, Any]:
        """Decrypt received message."""
        try:
            # In a real implementation, use proper decryption
            # For now, decode base64 (simplified)
            import base64
            decrypted_json = base64.b64decode(encrypted_message.encode()).decode()
            message = json.loads(decrypted_json)

            self._log_security_event("message_decrypted", {
                "message_id": message.get("message_id", "unknown"),
                "timestamp": time.time()
            })

            return message

        except Exception as e:
            self.logger.error(f"Message decryption failed: {e}")
            raise

    def _validate_certificate(self, cert: x509.Certificate) -> bool:
        """Validate device certificate (simplified)."""
        try:
            # Check if certificate is not expired
            now = time.time()
            if now < cert.not_valid_before.timestamp() or now > cert.not_valid_after.timestamp():
                return False

            # Check subject (simplified validation)
            subject = cert.subject
            if not subject.get_attributes_for_oid(NameOID.COMMON_NAME):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Certificate validation failed: {e}")
            return False

    def _handle_auth_request(self, message: Dict[str, Any]):
        """Handle authentication request."""
        certificate = message.get("payload", {}).get("certificate")
        if certificate:
            result = self.authenticate_device(certificate)

            # Send response
            response = {
                "message_id": f"auth_response_{message.get('message_id', 'unknown')}",
                "destination": message.get("source"),
                "message_type": "response",
                "payload": result
            }

            self.publish_message("alicia/system/security/auth_response", response)

    def _handle_encrypt_request(self, message: Dict[str, Any]):
        """Handle encryption request."""
        payload = message.get("payload", {})
        if payload:
            encrypted = self.encrypt_message(payload)

            # Send response
            response = {
                "message_id": f"encrypt_response_{message.get('message_id', 'unknown')}",
                "destination": message.get("source"),
                "message_type": "response",
                "payload": {"encrypted_message": encrypted}
            }

            self.publish_message("alicia/system/security/encrypt_response", response)

    def _handle_validate_request(self, message: Dict[str, Any]):
        """Handle token validation request."""
        token = message.get("payload", {}).get("token")
        if token:
            result = self.validate_token(token)

            # Send response
            response = {
                "message_id": f"validate_response_{message.get('message_id', 'unknown')}",
                "destination": message.get("source"),
                "message_type": "response",
                "payload": result
            }

            self.publish_message("alicia/system/security/validate_response", response)

    def _handle_device_registration(self, message: Dict[str, Any]):
        """Handle device registration."""
        device_id = message.get("payload", {}).get("device_id")
        if device_id:
            self.logger.info(f"Device registered: {device_id}")

    def _handle_health_check(self, message: Dict[str, Any]):
        """Handle health check request."""
        self.publish_health_status()

    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        event = {
            "event_type": event_type,
            "timestamp": time.time(),
            "details": details
        }

        self.security_events.append(event)

        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]

        self.logger.info(f"Security event: {event_type}")


def main():
    """Main entry point for Security Gateway service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create security gateway
    security_gateway = SecurityGateway()

    # Start API server
    try:
        security_gateway.api.run_api(host="0.0.0.0", port=8009)
    except KeyboardInterrupt:
        security_gateway.shutdown()


if __name__ == "__main__":
    main()
