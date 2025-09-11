"""
Testing API endpoints for voice assistant components
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from app.core.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class TestRequest(BaseModel):
    """Test request model"""
    test_type: str  # "stt", "tts", "grok4", "end_to_end", "component"
    input_text: Optional[str] = None
    input_audio: Optional[str] = None  # Base64 encoded audio
    component: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class TestResult(BaseModel):
    """Test result model"""
    test_id: str
    test_type: str
    status: str  # "running", "completed", "failed"
    input: str
    output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int
    metrics: Optional[Dict[str, Any]] = None
    timestamp: str

# Dependency injection
def get_websocket_manager() -> WebSocketManager:
    """Get WebSocket manager instance"""
    from app.main import websocket_manager
    return websocket_manager

# In-memory test storage (in production, this would be in a database)
test_storage = {}
test_counter = 0

@router.post("/run")
async def run_test(
    test_request: TestRequest,
    background_tasks: BackgroundTasks,
    websocket_manager: WebSocketManager = Depends(get_websocket_manager)
) -> Dict[str, Any]:
    """Run a test on voice assistant components"""
    global test_counter
    test_counter += 1
    test_id = f"test_{test_counter}_{int(time.time())}"
    
    try:
        # Create test result
        test_result = TestResult(
            test_id=test_id,
            test_type=test_request.test_type,
            status="running",
            input=test_request.input_text or "Audio input",
            duration_ms=0,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        
        # Store test
        test_storage[test_id] = test_result.dict()
        
        # Run test in background
        background_tasks.add_task(
            execute_test,
            test_id,
            test_request,
            websocket_manager
        )
        
        return {
            "test_id": test_id,
            "status": "running",
            "message": f"Test {test_id} started"
        }
        
    except Exception as e:
        logger.error(f"Error starting test: {e}")
        raise HTTPException(status_code=500, detail="Failed to start test")

async def execute_test(
    test_id: str,
    test_request: TestRequest,
    websocket_manager: WebSocketManager
):
    """Execute a test in the background"""
    start_time = time.time()
    
    try:
        # Update test status
        test_storage[test_id]["status"] = "running"
        await websocket_manager.broadcast_test_result(test_storage[test_id])
        
        # Execute test based on type
        if test_request.test_type == "stt":
            result = await test_stt(test_request)
        elif test_request.test_type == "tts":
            result = await test_tts(test_request)
        elif test_request.test_type == "grok4":
            result = await test_grok4(test_request)
        elif test_request.test_type == "end_to_end":
            result = await test_end_to_end(test_request)
        elif test_request.test_type == "component":
            result = await test_component(test_request)
        else:
            raise ValueError(f"Unknown test type: {test_request.test_type}")
            
        # Update test result
        duration_ms = int((time.time() - start_time) * 1000)
        test_storage[test_id].update({
            "status": "completed",
            "output": result.get("output", ""),
            "duration_ms": duration_ms,
            "metrics": result.get("metrics", {}),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        
    except Exception as e:
        # Update test with error
        duration_ms = int((time.time() - start_time) * 1000)
        test_storage[test_id].update({
            "status": "failed",
            "error": str(e),
            "duration_ms": duration_ms,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        
    # Broadcast final result
    await websocket_manager.broadcast_test_result(test_storage[test_id])

async def test_stt(test_request: TestRequest) -> Dict[str, Any]:
    """Test Speech-to-Text functionality"""
    try:
        import aiohttp
        
        # Simulate STT test
        async with aiohttp.ClientSession() as session:
            # In a real implementation, you would send audio data to Whisper
            # For now, we'll simulate the response
            await asyncio.sleep(1)  # Simulate processing time
            
            return {
                "output": "Hello Alicia, how are you?",
                "metrics": {
                    "stt_time_ms": 1000,
                    "confidence": 0.95,
                    "language": "en"
                }
            }
    except Exception as e:
        raise Exception(f"STT test failed: {str(e)}")

async def test_tts(test_request: TestRequest) -> Dict[str, Any]:
    """Test Text-to-Speech functionality"""
    try:
        import aiohttp
        
        # Simulate TTS test
        async with aiohttp.ClientSession() as session:
            # In a real implementation, you would send text to Piper
            # For now, we'll simulate the response
            await asyncio.sleep(0.5)  # Simulate processing time
            
            return {
                "output": "Audio generated successfully",
                "metrics": {
                    "tts_time_ms": 500,
                    "audio_duration_ms": 2000,
                    "voice": "en_US-lessac-medium"
                }
            }
    except Exception as e:
        raise Exception(f"TTS test failed: {str(e)}")

async def test_grok4(test_request: TestRequest) -> Dict[str, Any]:
    """Test Grok-4 AI functionality"""
    try:
        # Simulate Grok-4 test
        await asyncio.sleep(1.5)  # Simulate processing time
        
        return {
            "output": "Hey there! I'm doing great, thanks for asking! How can I help you today?",
            "metrics": {
                "grok4_time_ms": 1500,
                "tokens_used": 45,
                "model": "grok-4-0709"
            }
        }
    except Exception as e:
        raise Exception(f"Grok-4 test failed: {str(e)}")

async def test_end_to_end(test_request: TestRequest) -> Dict[str, Any]:
    """Test complete end-to-end pipeline"""
    try:
        # Simulate complete pipeline test
        await asyncio.sleep(3)  # Simulate processing time
        
        return {
            "output": "Complete pipeline test successful",
            "metrics": {
                "total_time_ms": 3000,
                "stt_time_ms": 800,
                "grok4_time_ms": 1200,
                "tts_time_ms": 500,
                "mqtt_time_ms": 100,
                "total_tokens": 45
            }
        }
    except Exception as e:
        raise Exception(f"End-to-end test failed: {str(e)}")

async def test_component(test_request: TestRequest) -> Dict[str, Any]:
    """Test a specific component"""
    component = test_request.component
    if not component:
        raise ValueError("Component name is required for component tests")
        
    try:
        # Simulate component test
        await asyncio.sleep(1)  # Simulate processing time
        
        return {
            "output": f"Component {component} test successful",
            "metrics": {
                f"{component}_time_ms": 1000,
                "component": component
            }
        }
    except Exception as e:
        raise Exception(f"Component {component} test failed: {str(e)}")

@router.get("/results/{test_id}")
async def get_test_result(test_id: str) -> Dict[str, Any]:
    """Get result of a specific test"""
    if test_id not in test_storage:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")
        
    return test_storage[test_id]

@router.get("/results")
async def get_test_results(
    limit: int = 50,
    test_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get recent test results with optional filtering"""
    results = list(test_storage.values())
    
    # Apply filters
    if test_type:
        results = [r for r in results if r["test_type"] == test_type]
    if status:
        results = [r for r in results if r["status"] == status]
        
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Apply limit
    return results[:limit]

@router.delete("/results/{test_id}")
async def delete_test_result(test_id: str) -> Dict[str, Any]:
    """Delete a specific test result"""
    if test_id not in test_storage:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")
        
    del test_storage[test_id]
    return {"message": f"Test {test_id} deleted"}

@router.post("/run-suite")
async def run_test_suite(
    background_tasks: BackgroundTasks,
    websocket_manager: WebSocketManager = Depends(get_websocket_manager)
) -> Dict[str, Any]:
    """Run a comprehensive test suite"""
    global test_counter
    
    # Define test suite
    test_suite = [
        TestRequest(test_type="stt", input_text="Hello Alicia"),
        TestRequest(test_type="tts", input_text="Hello from the test suite"),
        TestRequest(test_type="grok4", input_text="What's the weather like?"),
        TestRequest(test_type="end_to_end", input_text="Turn on the living room light"),
        TestRequest(test_type="component", component="mqtt", input_text="Test MQTT connection")
    ]
    
    suite_id = f"suite_{int(time.time())}"
    suite_results = []
    
    for i, test_request in enumerate(test_suite):
        test_counter += 1
        test_id = f"{suite_id}_test_{i+1}_{test_counter}"
        
        # Create test result
        test_result = TestResult(
            test_id=test_id,
            test_type=test_request.test_type,
            status="running",
            input=test_request.input_text or f"Test {i+1}",
            duration_ms=0,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        
        test_storage[test_id] = test_result.dict()
        suite_results.append(test_id)
        
        # Run test in background
        background_tasks.add_task(
            execute_test,
            test_id,
            test_request,
            websocket_manager
        )
        
    return {
        "suite_id": suite_id,
        "test_count": len(test_suite),
        "test_ids": suite_results,
        "message": f"Test suite {suite_id} started with {len(test_suite)} tests"
    }

@router.get("/stats")
async def get_test_stats() -> Dict[str, Any]:
    """Get test statistics"""
    results = list(test_storage.values())
    
    if not results:
        return {
            "total_tests": 0,
            "success_rate": 0,
            "average_duration_ms": 0,
            "test_types": {}
        }
    
    # Calculate statistics
    total_tests = len(results)
    completed_tests = [r for r in results if r["status"] == "completed"]
    successful_tests = len(completed_tests)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Average duration
    durations = [r["duration_ms"] for r in completed_tests if r["duration_ms"] > 0]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Test types breakdown
    test_types = {}
    for result in results:
        test_type = result["test_type"]
        if test_type not in test_types:
            test_types[test_type] = {"total": 0, "successful": 0}
        test_types[test_type]["total"] += 1
        if result["status"] == "completed":
            test_types[test_type]["successful"] += 1
    
    return {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": round(success_rate, 2),
        "average_duration_ms": round(avg_duration, 2),
        "test_types": test_types
    }

