"""
WebSocket manager for real-time updates
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
            
    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast data to all connected WebSocket clients"""
        if not self.active_connections:
            return
            
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
                
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
            
    async def broadcast_health_update(self, health_data: Dict[str, Any]):
        """Broadcast health status update"""
        await self.broadcast({
            "type": "health_update",
            "data": health_data
        })
        
    async def broadcast_metrics_update(self, metrics_data: Dict[str, Any]):
        """Broadcast metrics update"""
        await self.broadcast({
            "type": "metrics_update",
            "data": metrics_data
        })
        
    async def broadcast_test_result(self, test_result: Dict[str, Any]):
        """Broadcast test result"""
        await self.broadcast({
            "type": "test_result",
            "data": test_result
        })
        
    async def broadcast_config_update(self, config_data: Dict[str, Any]):
        """Broadcast configuration update"""
        await self.broadcast({
            "type": "config_update",
            "data": config_data
        })
        
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)

