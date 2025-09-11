#!/usr/bin/env python3
"""
Alicia Monitoring App - FastAPI Backend
Main application entry point for the monitoring and development tool
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from app.api import health, config, testing, metrics
from app.core.health_monitor import HealthMonitor
from app.core.websocket_manager import WebSocketManager
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global instances
health_monitor = HealthMonitor()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Alicia Monitoring App...")
    
    # Initialize health monitor
    await health_monitor.initialize()
    
    # Start background tasks
    asyncio.create_task(health_monitor.monitor_loop())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Alicia Monitoring App...")
    await health_monitor.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Alicia Monitoring App",
    description="Monitoring and development tool for Alicia Voice Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(testing.router, prefix="/api/testing", tags=["testing"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Alicia Monitoring App API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "alicia-monitoring-app"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(1)
            health_data = await health_monitor.get_health_status()
            await websocket_manager.broadcast(health_data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.get("/ws-test")
async def websocket_test():
    """WebSocket test page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>Alicia Monitoring WebSocket Test</h1>
        <div id="messages"></div>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                messages.innerHTML += '<p>' + event.data + '</p>';
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
