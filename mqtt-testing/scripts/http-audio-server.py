#!/usr/bin/env python3
"""
Internal HTTP Audio Server for Sonos Bridge
Serves audio files from /tmp/audio directory
"""

import http.server
import socketserver
import os
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/tmp/audio", **kwargs)

    def end_headers(self):
        # Add CORS headers for Sonos compatibility
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_audio_server(port=8080):
    """Start the internal HTTP audio server"""
    try:
        os.makedirs("/tmp/audio", exist_ok=True)

        with socketserver.TCPServer(("", port), AudioHTTPRequestHandler) as httpd:
            logger.info(f"Audio server started on port {port}")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start audio server: {e}")

if __name__ == "__main__":
    start_audio_server()
