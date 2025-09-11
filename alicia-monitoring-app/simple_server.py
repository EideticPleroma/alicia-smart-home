#!/usr/bin/env python3
"""
Simple FastAPI server for testing the Alicia Monitoring App
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(title="Alicia Monitoring App", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/health/")
async def get_health_status():
    """Mock health status for testing"""
    return {
        "timestamp": "2024-01-15T10:30:00Z",
        "services": {
            "whisper": {
                "status": "healthy",
                "response_time_ms": 1200,
                "last_check": "2024-01-15T10:30:00Z"
            },
            "piper": {
                "status": "healthy", 
                "response_time_ms": 800,
                "last_check": "2024-01-15T10:30:00Z"
            },
            "alicia_assistant": {
                "status": "healthy",
                "response_time_ms": 500,
                "last_check": "2024-01-15T10:30:00Z"
            },
            "mqtt": {
                "status": "healthy",
                "response_time_ms": 100,
                "last_check": "2024-01-15T10:30:00Z"
            },
            "homeassistant": {
                "status": "healthy",
                "response_time_ms": 300,
                "last_check": "2024-01-15T10:30:00Z"
            }
        },
        "overall_status": "healthy",
        "summary": {
            "total_services": 5,
            "healthy_services": 5,
            "unhealthy_services": 0,
            "error_services": 0
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Alicia Monitoring App Backend...")
    print("📍 Backend will be available at: http://localhost:8002")
    print("📚 API Documentation: http://localhost:8002/docs")
    print("🔍 Health Check: http://localhost:8002/health")
    print("🌐 Mock Health Data: http://localhost:8002/api/health/")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
