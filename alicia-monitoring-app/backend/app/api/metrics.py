"""
Metrics and analytics API endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query

from app.core.health_monitor import HealthMonitor

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
def get_health_monitor() -> HealthMonitor:
    """Get health monitor instance"""
    from app.main import health_monitor
    return health_monitor

@router.get("/overview")
async def get_metrics_overview(
    hours: int = Query(24, description="Number of hours to look back"),
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get overview of system metrics"""
    try:
        # Get metrics history
        history = await health_monitor.get_metrics_history(hours)
        
        if not history:
            return {
                "message": "No metrics data available",
                "period_hours": hours,
                "data_points": 0
            }
        
        # Calculate overview metrics
        total_checks = len(history)
        healthy_checks = sum(1 for h in history if h["overall_status"] == "healthy")
        degraded_checks = sum(1 for h in history if h["overall_status"] == "degraded")
        critical_checks = sum(1 for h in history if h["overall_status"] == "critical")
        
        # Calculate uptime percentage
        uptime_percentage = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Calculate average response times for each service
        service_metrics = {}
        for service_name in health_monitor.services.keys():
            service_history = await health_monitor.get_service_metrics(service_name, hours)
            if service_history:
                response_times = [h["response_time_ms"] for h in service_history if h["response_time_ms"] > 0]
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                
                service_metrics[service_name] = {
                    "average_response_time_ms": round(avg_response_time, 2),
                    "total_checks": len(service_history),
                    "successful_checks": sum(1 for h in service_history if h["status"] == "healthy")
                }
        
        return {
            "period_hours": hours,
            "data_points": total_checks,
            "uptime_percentage": round(uptime_percentage, 2),
            "status_breakdown": {
                "healthy": healthy_checks,
                "degraded": degraded_checks,
                "critical": critical_checks
            },
            "service_metrics": service_metrics,
            "last_updated": history[-1]["timestamp"] if history else None
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics overview")

@router.get("/services/{service_name}")
async def get_service_metrics(
    service_name: str,
    hours: int = Query(24, description="Number of hours to look back"),
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get detailed metrics for a specific service"""
    try:
        if service_name not in health_monitor.services:
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
        
        # Get service metrics
        service_history = await health_monitor.get_service_metrics(service_name, hours)
        
        if not service_history:
            return {
                "service": service_name,
                "message": "No metrics data available",
                "period_hours": hours,
                "data_points": 0
            }
        
        # Calculate detailed metrics
        response_times = [h["response_time_ms"] for h in service_history if h["response_time_ms"] > 0]
        statuses = [h["status"] for h in service_history]
        
        # Response time statistics
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        # Status statistics
        status_counts = {}
        for status in statuses:
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Success rate
        successful_checks = status_counts.get("healthy", 0)
        success_rate = (successful_checks / len(service_history)) * 100 if service_history else 0
        
        # Recent trend (last 10 data points)
        recent_trend = service_history[-10:] if len(service_history) >= 10 else service_history
        recent_success_rate = (sum(1 for h in recent_trend if h["status"] == "healthy") / len(recent_trend)) * 100 if recent_trend else 0
        
        return {
            "service": service_name,
            "period_hours": hours,
            "data_points": len(service_history),
            "response_time_stats": {
                "average_ms": round(avg_response_time, 2),
                "min_ms": min_response_time,
                "max_ms": max_response_time
            },
            "status_breakdown": status_counts,
            "success_rate_percentage": round(success_rate, 2),
            "recent_success_rate_percentage": round(recent_success_rate, 2),
            "first_check": service_history[0]["timestamp"] if service_history else None,
            "last_check": service_history[-1]["timestamp"] if service_history else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service metrics for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service metrics")

@router.get("/performance")
async def get_performance_metrics(
    hours: int = Query(24, description="Number of hours to look back"),
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get performance metrics across all services"""
    try:
        # Get metrics for all services
        all_metrics = {}
        for service_name in health_monitor.services.keys():
            service_history = await health_monitor.get_service_metrics(service_name, hours)
            if service_history:
                response_times = [h["response_time_ms"] for h in service_history if h["response_time_ms"] > 0]
                if response_times:
                    all_metrics[service_name] = {
                        "average_response_time_ms": round(sum(response_times) / len(response_times), 2),
                        "min_response_time_ms": min(response_times),
                        "max_response_time_ms": max(response_times),
                        "total_checks": len(service_history),
                        "successful_checks": sum(1 for h in service_history if h["status"] == "healthy")
                    }
        
        # Calculate system-wide performance metrics
        all_response_times = []
        total_checks = 0
        total_successful = 0
        
        for service_metrics in all_metrics.values():
            all_response_times.extend([
                service_metrics["average_response_time_ms"]
            ] * service_metrics["total_checks"])
            total_checks += service_metrics["total_checks"]
            total_successful += service_metrics["successful_checks"]
        
        # System-wide statistics
        if all_response_times:
            system_avg_response_time = sum(all_response_times) / len(all_response_times)
        else:
            system_avg_response_time = 0
        
        system_success_rate = (total_successful / total_checks) * 100 if total_checks > 0 else 0
        
        # Find slowest and fastest services
        if all_metrics:
            slowest_service = max(all_metrics.items(), key=lambda x: x[1]["average_response_time_ms"])
            fastest_service = min(all_metrics.items(), key=lambda x: x[1]["average_response_time_ms"])
        else:
            slowest_service = fastest_service = None
        
        return {
            "period_hours": hours,
            "system_metrics": {
                "average_response_time_ms": round(system_avg_response_time, 2),
                "total_checks": total_checks,
                "success_rate_percentage": round(system_success_rate, 2)
            },
            "service_metrics": all_metrics,
            "performance_insights": {
                "slowest_service": {
                    "name": slowest_service[0],
                    "avg_response_time_ms": slowest_service[1]["average_response_time_ms"]
                } if slowest_service else None,
                "fastest_service": {
                    "name": fastest_service[0],
                    "avg_response_time_ms": fastest_service[1]["average_response_time_ms"]
                } if fastest_service else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@router.get("/alerts")
async def get_alert_metrics(
    hours: int = Query(24, description="Number of hours to look back"),
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Get alert and error metrics"""
    try:
        # Get metrics history
        history = await health_monitor.get_metrics_history(hours)
        
        if not history:
            return {
                "message": "No metrics data available",
                "period_hours": hours,
                "alerts": []
            }
        
        alerts = []
        
        # Analyze history for alerts
        for i, metric in enumerate(history):
            timestamp = metric["timestamp"]
            
            # Check for critical status
            if metric["overall_status"] == "critical":
                alerts.append({
                    "timestamp": timestamp,
                    "type": "critical",
                    "message": "All services are down",
                    "severity": "high"
                })
            
            # Check for degraded status
            elif metric["overall_status"] == "degraded":
                unhealthy_services = [
                    name for name, service_data in metric["services"].items()
                    if service_data["status"] not in ["healthy"]
                ]
                alerts.append({
                    "timestamp": timestamp,
                    "type": "degraded",
                    "message": f"Services experiencing issues: {', '.join(unhealthy_services)}",
                    "severity": "medium",
                    "affected_services": unhealthy_services
                })
            
            # Check for individual service issues
            for service_name, service_data in metric["services"].items():
                if service_data["status"] == "timeout":
                    alerts.append({
                        "timestamp": timestamp,
                        "type": "timeout",
                        "message": f"Service {service_name} timed out",
                        "severity": "medium",
                        "service": service_name
                    })
                elif service_data["status"] == "error":
                    alerts.append({
                        "timestamp": timestamp,
                        "type": "error",
                        "message": f"Service {service_name} error: {service_data.get('error', 'Unknown error')}",
                        "severity": "high",
                        "service": service_name
                    })
        
        # Sort alerts by timestamp (newest first)
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Count alerts by type
        alert_counts = {}
        for alert in alerts:
            alert_type = alert["type"]
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        return {
            "period_hours": hours,
            "total_alerts": len(alerts),
            "alert_counts": alert_counts,
            "recent_alerts": alerts[:10],  # Last 10 alerts
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error getting alert metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert metrics")

@router.get("/export")
async def export_metrics(
    hours: int = Query(24, description="Number of hours to look back"),
    format: str = Query("json", description="Export format: json or csv"),
    health_monitor: HealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Export metrics data in various formats"""
    try:
        # Get metrics history
        history = await health_monitor.get_metrics_history(hours)
        
        if not history:
            raise HTTPException(status_code=404, detail="No metrics data available for export")
        
        if format.lower() == "json":
            return {
                "format": "json",
                "data": history,
                "exported_at": datetime.now().isoformat(),
                "period_hours": hours
            }
        elif format.lower() == "csv":
            # Convert to CSV format
            csv_data = []
            for metric in history:
                for service_name, service_data in metric["services"].items():
                    csv_data.append({
                        "timestamp": metric["timestamp"],
                        "service": service_name,
                        "status": service_data["status"],
                        "response_time_ms": service_data.get("response_time_ms", 0),
                        "overall_status": metric["overall_status"]
                    })
            
            return {
                "format": "csv",
                "data": csv_data,
                "exported_at": datetime.now().isoformat(),
                "period_hours": hours
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'csv'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to export metrics")

