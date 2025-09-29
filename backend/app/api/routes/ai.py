from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...services.ai_service import ai_service
from ...utils.image_processing import validate_image, process_image_for_ai

# Create router
router = APIRouter(prefix="/api/ai", tags=["AI Services"])


# Request/Response Models
class CodeGenerationRequest(BaseModel):
    """Request model for code generation (when not using file upload)."""
    framework: str = Field(default="html", description="Target framework (html, react, vue, etc.)")
    additional_instructions: Optional[str] = Field(None, description="Additional instructions for the AI")


class CodeGenerationResponse(BaseModel):
    """Response model for code generation."""
    success: bool
    generated_code: str
    framework: str
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
    image: UploadFile = File(..., description="Hand-drawn website sketch image"),
    framework: str = Form(default="html", description="Target framework"),
    additional_instructions: Optional[str] = Form(None, description="Additional instructions")
):
    """
    Generate code from a hand-drawn website sketch.
    
    Upload an image of a hand-drawn website sketch and get generated code in your preferred framework.
    
    - **image**: Image file (PNG, JPEG, WebP) containing the website sketch
    - **framework**: Target framework (html, react, vue, etc.)
    - **additional_instructions**: Optional additional instructions for the AI
    """
    start_time = datetime.now()
    
    try:
        # Validate the uploaded image
        image_data = await validate_image(image)
        
        # Process image for AI service
        processed_data, image_format = await process_image_for_ai(image_data, image.content_type)
        
        # Generate code using AI service
        result = await ai_service.generate_code_from_image(
            image_data=processed_data,
            image_format=image_format,
            framework=framework,
            additional_instructions=additional_instructions
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return CodeGenerationResponse(
            success=True,
            generated_code=result.get("code", ""),
            framework=framework,
            metadata={
                "image_size_bytes": len(processed_data),
                "image_format": image_format,
                "ai_model": result.get("model", "unknown"),
                "confidence": result.get("confidence", 0.0),
                **result.get("metadata", {})
            },
            timestamp=datetime.now().isoformat(),
            processing_time_ms=int(processing_time)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate code: {str(e)}"
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
    Get list of supported frameworks for code generation.
    
    Returns the frameworks that the AI service can generate code for.
    """
    return JSONResponse({
        "frameworks": [
            {
                "id": "html",
                "name": "HTML/CSS",
                "description": "Pure HTML with inline or embedded CSS"
            },
            {
                "id": "react",
                "name": "React",
                "description": "React components with JSX and CSS"
            },
            {
                "id": "vue",
                "name": "Vue.js",
                "description": "Vue.js single file components"
            },
            {
                "id": "angular",
                "name": "Angular",
                "description": "Angular components with TypeScript"
            },
            {
                "id": "tailwind",
                "name": "HTML + Tailwind CSS",
                "description": "HTML with Tailwind CSS utility classes"
            },
            {
                "id": "bootstrap",
                "name": "HTML + Bootstrap",
                "description": "HTML with Bootstrap framework"
            }
        ],
        "default": "html",
        "timestamp": datetime.now().isoformat()
    })


# Note: Error handlers are configured in main.py for the main app
