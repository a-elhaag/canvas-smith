import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...monitoring.metrics import metrics_collector
from ...services.ai_service import ai_service
from ...utils.image_processing import process_image_for_ai, validate_image

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ai", tags=["AI Services"])


# Request/Response Models
class TokenUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class ComponentAnalysis(BaseModel):
    """Analysis of the generated component."""
    component_type: str
    has_script_setup: bool
    has_typescript: bool
    interactive_elements: Dict[str, int]
    animations: Dict[str, int]
    styling: Dict[str, bool]
    vue_features: Dict[str, bool]


class CodeGenerationResponse(BaseModel):
    """Response model for Vue.js code generation."""
    success: bool
    generated_code: str
    finish_reason: str
    token_usage: TokenUsage
    component_analysis: ComponentAnalysis
    metadata: Dict[str, Any]
    timestamp: str
    processing_time_ms: int


class ChatRequest(BaseModel):
    """Request model for chat assistance."""
    message: str = Field(..., description="User's message or question")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context (code, project info, etc.)")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for continuity")


class ChatResponse(BaseModel):
    """Response model for chat assistance."""
    success: bool
    response: str
    conversation_id: Optional[str]
    metadata: Dict[str, Any]
    timestamp: str


class HealthResponse(BaseModel):
    """Response model for AI service health check."""
    ai_service_status: str
    endpoints_configured: bool
    timestamp: str


# Endpoints
@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code_from_sketch(
    image: UploadFile = File(..., description="Hand-drawn website sketch image (supports JPG, PNG, WebP, GIF, BMP, TIFF)")
):
    """
    Generate functional Vue.js code from a hand-drawn website sketch.
    
    Simply upload an image of a hand-drawn website sketch and get a complete Vue.js component
    with predicted functionality, animations, and interactive elements.
    
    **Features:**
    - **Smart Component Prediction**: AI predicts what buttons and elements should do
    - **Animations & Transitions**: Includes smooth animations and hover effects
    - **Interactive Elements**: Adds click handlers, form submissions, navigation
    - **Vue.js 3**: Always generates Vue.js components with Composition API
    - **Token Tracking**: Returns detailed token usage and cost estimation
    - **All Image Formats**: Supports JPG, PNG, WebP, GIF, BMP, TIFF
    
    **Parameters:**
    - **image**: Image file containing the website sketch (JPG, PNG, WebP, GIF, BMP, TIFF)
    
    **Returns:**
    Complete Vue.js component code with token usage, component analysis, and metadata.
    """
    start_time = datetime.now()
    
    try:
        # Validate the uploaded image (now supports all image types)
        image_data = await validate_image(image)
        
        # Process image for AI service
        processed_data, image_format = await process_image_for_ai(image_data, image.content_type)
        
        # Generate Vue.js code using AI service (no framework parameter needed)
        result = await ai_service.generate_code_from_image(
            image_data=processed_data,
            image_format=image_format
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Extract token usage information
        token_usage = result.get("token_usage", {})
        component_analysis = result.get("metadata", {}).get("component_prediction", {})
        
        logger.info(f"Vue.js code generation completed - Tokens: {token_usage.get('total_tokens', 0)}")
        
        # Record metrics (always Vue.js)
        metrics_collector.record_ai_generation(
            framework="vue",
            tokens_used=token_usage.get('total_tokens', 0),
            cost_usd=token_usage.get('estimated_cost_usd', 0.0),
            processing_time_ms=processing_time,
            has_animations=result.get("metadata", {}).get("has_animations", False),
            success=True
        )
        
        return CodeGenerationResponse(
            success=True,
            generated_code=result.get("code", ""),
            finish_reason=result.get("finish_reason", "unknown"),
            token_usage=TokenUsage(
                prompt_tokens=token_usage.get("prompt_tokens", 0),
                completion_tokens=token_usage.get("completion_tokens", 0),
                total_tokens=token_usage.get("total_tokens", 0),
                estimated_cost_usd=token_usage.get("estimated_cost_usd", 0.0)
            ),
            component_analysis=ComponentAnalysis(
                component_type=component_analysis.get("component_type", "vue"),
                has_script_setup=component_analysis.get("has_script_setup", False),
                has_typescript=component_analysis.get("has_typescript", False),
                interactive_elements=component_analysis.get("interactive_elements", {}),
                animations=component_analysis.get("animations", {}),
                styling=component_analysis.get("styling", {}),
                vue_features=component_analysis.get("vue_features", {})
            ),
            metadata={
                "framework": "vue",
                "image_size_bytes": len(processed_data),
                "image_format": image_format,
                "ai_model": result.get("model", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "has_animations": result.get("metadata", {}).get("has_animations", False),
                "has_hover_effects": result.get("metadata", {}).get("has_hover_effects", False),
                "generation_parameters": result.get("metadata", {}).get("generation_parameters", {})
            },
            timestamp=datetime.now().isoformat(),
            processing_time_ms=int(processing_time)
        )
        
    except HTTPException:
        # Record failed generation
        metrics_collector.record_ai_generation(
            framework="vue",
            tokens_used=0,
            cost_usd=0.0,
            processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            has_animations=False,
            success=False
        )
        raise
    except Exception as e:
        # Record failed generation
        metrics_collector.record_ai_generation(
            framework="vue",
            tokens_used=0,
            cost_usd=0.0,
            processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            has_animations=False,
            success=False
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Vue.js code: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_assistance(request: ChatRequest):
    """
    Get AI chat assistance for code modifications and questions.
    
    Ask questions about your generated code, request modifications, or get help with web development.
    
    - **message**: Your message or question
    - **context**: Optional context like previous code or project information
    - **conversation_id**: Optional conversation ID to maintain context across multiple messages
    """
    try:
        # Process chat request using AI service
        result = await ai_service.chat_assistance(
            message=request.message,
            context=request.context,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            success=True,
            response=result.get("response", ""),
            conversation_id=result.get("conversation_id", request.conversation_id),
            metadata={
                "ai_model": result.get("model", "unknown"),
                "tokens_used": result.get("tokens_used", 0),
                "confidence": result.get("confidence", 0.0),
                **result.get("metadata", {})
            },
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/health")
async def check_ai_health():
    """
    Check the health status of AI services.
    
    Returns the current status of AI service connectivity and configuration.
    """
    try:
        # Check if AI service is available
        health_result = await ai_service.health_check()
        
        # Check if Azure OpenAI is configured
        endpoints_configured = bool(
            ai_service.api_key and 
            ai_service.endpoint and 
            ai_service.deployment_name
        )
        
        return JSONResponse({
            "ai_service_status": "healthy" if health_result["healthy"] else "unhealthy",
            "endpoints_configured": endpoints_configured,
            "timestamp": datetime.now().isoformat(),
            "details": {
                "endpoint": health_result.get("endpoint", "unknown"),
                "status_code": health_result.get("status_code"),
                "response_time_ms": health_result.get("response_time_ms"),
                "error": health_result.get("error"),
                "deployment_name": ai_service.deployment_name,
                "api_version": ai_service.api_version
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "ai_service_status": "error", 
            "endpoints_configured": False,
            "timestamp": datetime.now().isoformat(),
            "details": {
                "error": str(e)
            }
        }, status_code=500)


@router.get("/config-check")
async def check_ai_configuration():
    """
    Check Azure OpenAI configuration without making API calls.
    
    Returns configuration status and validation.
    """
    config_status = {
        "api_key_configured": bool(ai_service.api_key),
        "endpoint_configured": bool(ai_service.endpoint), 
        "deployment_configured": bool(ai_service.deployment_name),
        "api_version": ai_service.api_version,
        "endpoint": ai_service.endpoint if ai_service.endpoint else None,
        "deployment_name": ai_service.deployment_name if ai_service.deployment_name else None,
        "chat_endpoint_url": None
    }
    
    try:
        if config_status["endpoint_configured"] and config_status["deployment_configured"]:
            config_status["chat_endpoint_url"] = ai_service._get_chat_endpoint()
        
        all_configured = (
            config_status["api_key_configured"] and 
            config_status["endpoint_configured"] and 
            config_status["deployment_configured"]
        )
        
        return JSONResponse({
            "configuration_valid": all_configured,
            "timestamp": datetime.now().isoformat(),
            **config_status
        })
    except Exception as e:
        return JSONResponse({
            "configuration_valid": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            **config_status
        }, status_code=500)


@router.get("/supported-frameworks")
async def get_supported_frameworks():
    """
    Get information about the supported framework.
    
    Canvas Smith generates Vue.js 3 components exclusively for optimal quality and consistency.
    """
    return JSONResponse({
        "framework": {
            "id": "vue",
            "name": "Vue.js 3",
            "description": "Vue.js components with Composition API, animations, and TypeScript support",
            "features": [
                "composition_api",
                "script_setup_syntax", 
                "animations_and_transitions",
                "hover_effects",
                "reactive_data",
                "component_prediction",
                "tailwind_css_support",
                "typescript_integration"
            ]
        },
        "why_vue_only": [
            "Optimized AI prompts for Vue.js generate higher quality code",
            "Consistent output format and structure",
            "Better animation and interaction integration", 
            "Enhanced component intelligence and prediction",
            "Streamlined development workflow"
        ],
        "capabilities": {
            "smart_component_prediction": "AI predicts button functionality and interactions",
            "automatic_animations": "Smooth transitions and hover effects included",
            "responsive_design": "Mobile-first responsive components",
            "modern_syntax": "Vue 3 Composition API with <script setup>",
            "styling": "Tailwind CSS classes with custom CSS animations"
        },
        "timestamp": datetime.now().isoformat()
    })


@router.get("/metrics")
async def get_metrics(hours: int = 24):
    """
    Get production metrics and analytics.
    
    Returns comprehensive metrics including:
    - Request statistics and performance
    - AI generation analytics
    - Token usage and cost tracking
    - Error rates and health status
    
    Args:
        hours: Number of hours to include in metrics (default: 24)
    """
    try:
        metrics = metrics_collector.get_summary(hours=hours)
        return JSONResponse({
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)


@router.get("/health-detailed")
async def get_detailed_health():
    """
    Get detailed health status with metrics.
    
    Returns comprehensive health information including:
    - AI service connectivity
    - Recent error rates
    - Performance metrics
    - System status
    """
    try:
        # Get AI service health
        ai_health = await ai_service.health_check()
        
        # Get system metrics health
        metrics_health = metrics_collector.get_health_status()
        
        # Get configuration status
        config_status = {
            "api_key_configured": bool(ai_service.api_key),
            "endpoint_configured": bool(ai_service.endpoint),
            "deployment_configured": bool(ai_service.deployment_name)
        }
        
        overall_healthy = (
            ai_health.get("healthy", False) and
            metrics_health.get("status") != "unhealthy" and
            all(config_status.values())
        )
        
        return JSONResponse({
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "ai_service": ai_health,
            "metrics": metrics_health,
            "configuration": config_status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse({
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)


# Note: Error handlers are configured in main.py for the main app
