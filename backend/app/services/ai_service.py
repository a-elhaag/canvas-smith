import asyncio
import base64
import logging
from typing import Optional, Dict, Any, List
from io import BytesIO

import aiohttp
from fastapi import HTTPException

from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class AIService:
    """Service for Azure OpenAI-powered code generation and chat assistance."""
    
    def __init__(self):
        self.api_key = settings.azure_openai_api_key
        self.endpoint = settings.azure_openai_endpoint
        self.deployment_name = settings.azure_openai_deployment_name
        self.api_version = settings.azure_openai_api_version
        self.timeout = settings.ai_timeout
        self.max_retries = settings.ai_max_retries
        self.max_tokens = settings.ai_max_tokens
    
    def _validate_configuration(self):
        """Validate that Azure OpenAI service is properly configured."""
        if not self.api_key:
            raise HTTPException(
                status_code=500, 
                detail="Azure OpenAI API key not configured."
            )
        
        if not self.endpoint:
            raise HTTPException(
                status_code=500,
                detail="Azure OpenAI endpoint not configured."
            )
        
        if not self.deployment_name:
            raise HTTPException(
                status_code=500,
                detail="Azure OpenAI deployment name not configured."
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for Azure OpenAI API requests."""
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"{settings.app_name}/{settings.app_version}"
        }
    
    def _get_chat_endpoint(self) -> str:
        """Get the Azure OpenAI chat completions endpoint."""
        return f"{self.endpoint.rstrip('/')}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
    
    async def _make_ai_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make an HTTP request to the AI service with retry logic."""
        headers = self._get_headers()
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(endpoint, json=payload, headers=headers) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:  # Rate limit
                            if attempt < self.max_retries - 1:
                                wait_time = 2 ** attempt  # Exponential backoff
                                logger.warning(f"Rate limited, retrying in {wait_time}s (attempt {attempt + 1})")
                                await asyncio.sleep(wait_time)
                                continue
                        
                        # Handle other HTTP errors
                        error_text = await response.text()
                        logger.error(f"AI API error: {response.status} - {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"AI service error: {error_text}"
                        )
            
            except aiohttp.ClientTimeout:
                logger.error(f"AI API timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    raise HTTPException(
                        status_code=504,
                        detail="AI service timeout. Please try again."
                    )
            
            except aiohttp.ClientError as e:
                logger.error(f"AI API connection error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Unable to connect to AI service. Please try again later."
                    )
            
            # Wait before retry
            if attempt < self.max_retries - 1:
                await asyncio.sleep(1)
        
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable after multiple attempts."
        )
    
    async def generate_code_from_image(
        self, 
        image_data: bytes, 
        image_format: str = "png",
        framework: str = "html",
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code from a hand-drawn website sketch using Azure OpenAI.
        
        Args:
            image_data: Binary image data
            image_format: Image format (png, jpg, webp)
            framework: Target framework (html, react, vue, etc.)
            additional_instructions: Optional additional instructions for the AI
        
        Returns:
            Dictionary containing generated code and metadata
        """
        self._validate_configuration()
        
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create system prompt for code generation
            system_prompt = f"""You are an expert web developer and UI/UX designer. Your task is to analyze hand-drawn website sketches and convert them into clean, functional {framework} code.

Guidelines:
1. Analyze the sketch carefully and identify UI components, layout structure, and content areas
2. Generate clean, semantic, and accessible code
3. Use modern CSS practices (Flexbox/Grid, responsive design)
4. Include placeholder content where text/images are indicated
5. Ensure the code is production-ready and follows best practices
6. Make the design responsive and mobile-friendly

Output only the code without explanations or markdown formatting."""

            user_prompt = f"""Convert this hand-drawn website sketch into {framework} code. 

Framework: {framework}
Additional instructions: {additional_instructions or 'Make it responsive and modern'}

Please analyze the sketch and create complete, functional code that represents the drawn design."""

            # Prepare Azure OpenAI payload
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_completion_tokens": self.max_tokens
            }
            
            logger.info(f"Generating {framework} code from image (size: {len(image_data)} bytes)")
            
            # Make request to Azure OpenAI
            endpoint = self._get_chat_endpoint()
            response = await self._make_ai_request(endpoint, payload)
            
            # Debug: Log the full response structure
            logger.info(f"Raw Azure OpenAI response keys: {list(response.keys())}")
            logger.info(f"Response choices count: {len(response.get('choices', []))}")
            
            # Extract the generated code
            choices = response.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                logger.info(f"Message keys: {list(message.keys())}")
                generated_code = message.get("content", "")
                logger.info(f"Generated code length: {len(generated_code) if generated_code else 'None/0'}")
                logger.info(f"Generated code preview: {generated_code[:100] if generated_code else 'EMPTY'}")
            else:
                generated_code = ""
                logger.warning("No choices found in Azure OpenAI response!")
            
            # Additional debug: check if code is in a different field
            if not generated_code and response:
                logger.warning("Generated code is empty, checking alternative response fields...")
                logger.info(f"Full response structure: {response}")
            
            # Prepare response in expected format
            result = {
                "code": generated_code,
                "model": f"azure-openai-{self.deployment_name}",
                "confidence": 0.95,  # Azure OpenAI typically has high confidence
                "metadata": {
                    "framework": framework,
                    "image_size_bytes": len(image_data),
                    "image_format": image_format,
                    "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                    "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response.get("usage", {}).get("completion_tokens", 0)
                }
            }
            
            logger.info(f"Final result code length: {len(result.get('code', ''))}")
            return result
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate code: {str(e)}"
            )
    
    async def chat_assistance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide chat assistance for code modifications and questions using Azure OpenAI.
        
        Args:
            message: User's message/question
            context: Optional context (previous code, project info, etc.)
            conversation_id: Optional conversation ID for continuity
        
        Returns:
            Dictionary containing AI response and metadata
        """
        self._validate_configuration()
        
        try:
            # Create system prompt for chat assistance
            system_prompt = """You are an expert web developer and coding assistant. You help users with:
1. Modifying and improving generated code
2. Debugging and fixing issues
3. Adding new features and functionality
4. Optimizing performance and accessibility
5. Converting between different frameworks
6. Providing best practices and recommendations

Always provide clear, practical advice with code examples when appropriate. Format code blocks with proper syntax highlighting."""

            # Build messages array
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add context if provided
            if context:
                context_message = "Here's the current context:\n"
                if context.get("code"):
                    context_message += f"Current code:\n```{context.get('framework', 'html')}\n{context['code']}\n```\n"
                if context.get("framework"):
                    context_message += f"Framework: {context['framework']}\n"
                if context.get("additional_info"):
                    context_message += f"Additional info: {context['additional_info']}\n"
                
                messages.append({"role": "user", "content": context_message})
            
            # Add the current user message
            messages.append({"role": "user", "content": message})
            
            # Prepare Azure OpenAI payload
            payload = {
                "messages": messages,
                "max_completion_tokens": min(self.max_tokens, 1500)  # Limit for chat responses
            }
            
            logger.info(f"Processing chat message (context: {bool(context)}, conv_id: {conversation_id})")
            
            # Make request to Azure OpenAI
            endpoint = self._get_chat_endpoint()
            response = await self._make_ai_request(endpoint, payload)
            
            # Extract the response
            ai_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Prepare response in expected format
            result = {
                "response": ai_response,
                "conversation_id": conversation_id,
                "model": f"azure-openai-{self.deployment_name}",
                "confidence": 0.95,
                "metadata": {
                    "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                    "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response.get("usage", {}).get("completion_tokens", 0),
                    "has_context": bool(context)
                }
            }
            
            logger.info("Chat assistance completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Chat assistance failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process chat message: {str(e)}"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Azure OpenAI service is available with detailed status."""
        result = {
            "healthy": False,
            "error": None,
            "endpoint": None,
            "status_code": None,
            "response_time_ms": None
        }
        
        try:
            self._validate_configuration()
            
            endpoint = self._get_chat_endpoint()
            result["endpoint"] = endpoint
            
            # Simple test message to check Azure OpenAI availability
            test_payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, this is a health check. Please respond with 'OK'."}
                ],
                "max_completion_tokens": 10
            }
            
            import time
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.post(
                    endpoint, 
                    json=test_payload, 
                    headers=self._get_headers()
                ) as response:
                    end_time = time.time()
                    result["response_time_ms"] = int((end_time - start_time) * 1000)
                    result["status_code"] = response.status
                    
                    if response.status == 200:
                        result["healthy"] = True
                        logger.info("Azure OpenAI health check passed")
                    else:
                        response_text = await response.text()
                        result["error"] = f"HTTP {response.status}: {response_text}"
                        logger.warning(f"Azure OpenAI health check failed: {result['error']}")
                    
                    return result
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Azure OpenAI health check failed: {str(e)}")
            return result


# Create global AI service instance
ai_service = AIService()
