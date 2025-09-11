"""
Health monitoring API endpoints
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta

from app.core.health_monitor import HealthMonitor
from app.core.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
def get_health_monitor() -> HealthMonitor:
    """Get health monitor instance"""
    from app.main import health_monitor
    return health_monitor

def get_websocket_manager() -> WebSocketManager:
    """Get WebSocket manager instance"""
    from app.main import websocket_manager
    return websocket_manager

@router.get("/")
async def get_health_status(
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get current health status of all services"""
    try:
        return await health_monitor.get_health_status()
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health status")

@router.get("/services")
async def get_services_status(
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get detailed status of all services"""
    try:
        health_data = await health_monitor.get_health_status()
        return {
            "services": health_data["services"],
            "summary": health_data["summary"],
            "timestamp": health_data["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error getting services status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get services status")

@router.get("/services/{service_name}")
async def get_service_status(
    service_name: str,
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get status of a specific service"""
    try:
        health_data = await health_monitor.get_health_status()
        
        if service_name not in health_data["services"]:
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
            
        return {
            "service": service_name,
            "status": health_data["services"][service_name],
            "timestamp": health_data["timestamp"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service status for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service status")

@router.get("/metrics")
async def get_metrics_history(
    hours: int = 24,
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> List[Dict[str, Any]]:
    """Get metrics history for the specified number of hours"""
    try:
        return await health_monitor.get_metrics_history(hours)
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics history")

@router.get("/metrics/{service_name}")
async def get_service_metrics(
    service_name: str,
    hours: int = 24,
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> List[Dict[str, Any]]:
    """Get metrics for a specific service"""
    try:
        return await health_monitor.get_service_metrics(service_name, hours)
    except Exception as e:
        logger.error(f"Error getting service metrics for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service metrics")

@router.post("/refresh")
async def refresh_health_status(
    health_monitor: HealthMonitor = Depends(get_health_monitor),
    websocket_manager: WebSocketManager = Depends(get_websocket_manager)
) -> Dict[str, Any]:
    """Manually refresh health status and broadcast update"""
    try:
        health_data = await health_monitor.get_health_status()
        await websocket_manager.broadcast_health_update(health_data)
        
        return {
            "message": "Health status refreshed",
            "timestamp": health_data["timestamp"],
            "overall_status": health_data["overall_status"]
        }
    except Exception as e:
        logger.error(f"Error refreshing health status: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh health status")

@router.get("/summary")
async def get_health_summary(
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get a summary of system health"""
    try:
        health_data = await health_monitor.get_health_status()
        
        # Calculate uptime for each service
        summary = {
            "overall_status": health_data["overall_status"],
            "timestamp": health_data["timestamp"],
            "services_summary": {},
            "recommendations": []
        }
        
        for service_name, service_data in health_data["services"].items():
            summary["services_summary"][service_name] = {
                "status": service_data["status"],
                "response_time_ms": service_data.get("response_time_ms", 0),
                "last_check": service_data["last_check"]
            }
            
        # Add recommendations based on status
        if health_data["overall_status"] == "critical":
            summary["recommendations"].append("All services are down. Check system infrastructure.")
        elif health_data["overall_status"] == "degraded":
            summary["recommendations"].append("Some services are experiencing issues. Review service logs.")
            
        return summary
        
    except Exception as e:
        logger.error(f"Error getting health summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health summary")
