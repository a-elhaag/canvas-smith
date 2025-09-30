import asyncio
import base64
import logging
from typing import Any, Dict, List, Optional

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
            "api-key": self.api_key.get_secret_value() if hasattr(self.api_key, "get_secret_value") else str(self.api_key),
            "Content-Type": "application/json",
            "User-Agent": f"{settings.app_name}/{settings.app_version}"
        }
    
    def _get_chat_endpoint(self) -> str:
        """Get the Azure OpenAI chat completions endpoint."""
        endpoint_base = str(self.endpoint).rstrip("/")
        return f"{endpoint_base}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
    
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
            
            except Exception as e:
                logger.error(f"Unexpected error during AI request: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="AI service unavailable after multiple attempts."
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
        user_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate functional Vue.js code from a hand-drawn website sketch using Azure OpenAI.
        
        Args:
            image_data: Binary image data
            image_format: Image format (png, jpg, webp)
        
        Returns:
            Dictionary containing generated Vue.js code, token usage, and metadata
        """
        self._validate_configuration()
        
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create comprehensive system prompt for Vue.js code generation
            system_prompt = """You are an expert Vue.js developer and UI/UX designer specializing in creating interactive, animated web components from sketches.

CORE MISSION: Transform hand-drawn sketches into fully functional Vue.js components with:
1. **Smart Component Prediction**: Analyze the sketch to predict component functionality
2. **Interactive Elements**: Add appropriate click handlers, form submissions, navigation
3. **Smooth Animations**: Implement Vue transitions and CSS animations
4. **Hover Effects**: Add engaging hover states for interactive elements
5. **Motion Design**: Use CSS transforms, transitions, and Vue animations

TECHNICAL REQUIREMENTS:
- Framework: Vue.js 3 with Composition API
- Use <script setup> syntax with TypeScript where beneficial
- Implement responsive design with Tailwind CSS or modern CSS
- Add smooth transitions between states
- Include loading states and micro-interactions
- Predict button functionality based on visual context

COMPONENT INTELLIGENCE:
- **Buttons**: Predict actions (submit, navigate, toggle, etc.) based on placement and context
- **Forms**: Add validation, submission handling, and success states
- **Cards**: Include hover animations, click interactions
- **Navigation**: Implement active states, smooth scrolling
- **Images**: Add lazy loading, hover zoom effects
- **Lists**: Include item animations, filtering capabilities

ANIMATION GUIDELINES:
- Use Vue <Transition> components for state changes
- Implement CSS transforms for hover effects
- Add spring-like animations for user interactions
- Include entrance animations for page elements
- Use appropriate easing functions (cubic-bezier)

OUTPUT FORMAT:
Return ONLY the complete Vue.js component code with:
- Single File Component (.vue) structure
- Reactive data and methods using Composition API
- CSS with animations and transitions
- TypeScript where appropriate
- Comprehensive functionality prediction

Do not include explanations, markdown formatting, or code blocks - just the raw Vue component code."""

            effective_user_prompt = user_prompt.strip() if user_prompt else "Analyze this hand-drawn website sketch and create a complete, functional Vue.js component. Focus on predicting what each UI element should do and produce production-ready Vue.js code."

            detailed_prompt = f"""{effective_user_prompt}

ANALYSIS REQUIREMENTS:
1. **Visual Elements**: Identify all UI components, layout structure, and content areas
2. **Functional Prediction**: Determine what each button/element should do based on context
3. **User Flow**: Predict the intended user interactions and navigation
4. **Component Behavior**: Add appropriate reactive data and methods

IMPLEMENTATION REQUIREMENTS:
- Create a modern, interactive Vue.js component with animations and hover effects
- Add predicted functionality for interactive elements and connect actions to appropriate handlers
- Implement responsive design principles and accessibility best practices
- Use modern Vue.js patterns and best practices with Composition API

Create a production-ready component that brings this sketch to life with engaging interactions and animations."""

            # Prepare Azure OpenAI payload with enhanced parameters
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": detailed_prompt},
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
                "max_completion_tokens": self.max_tokens,
                # Remove temperature for GPT-4 compatibility (use default)
                # "temperature": 0.7,  # Some models don't support custom temperature
                "top_p": 0.95,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            logger.info(f"Generating Vue.js code from image (size: {len(image_data)} bytes)")
            
            # Make request to Azure OpenAI
            endpoint = self._get_chat_endpoint()
            response = await self._make_ai_request(endpoint, payload)
            
            # Extract the generated code and token usage
            choices = response.get("choices", [])
            usage = response.get("usage", {})
            
            if choices:
                message = choices[0].get("message", {})
                generated_code = message.get("content", "")
                finish_reason = choices[0].get("finish_reason", "unknown")
                
                # Log different finish reasons for monitoring
                if finish_reason == "length":
                    logger.warning(f"Code generation hit token limit - consider increasing AI_MAX_TOKENS (current: {self.max_tokens})")
                elif finish_reason == "stop":
                    logger.info(f"Code generation completed successfully")
                else:
                    logger.info(f"Code generation finished with reason: {finish_reason}")
                    
                logger.info(f"Generated code length: {len(generated_code)} chars, Finish reason: {finish_reason}")
            else:
                generated_code = ""
                finish_reason = "no_choices"
                logger.warning("No choices found in Azure OpenAI response!")
            
            # Extract detailed token usage
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
            
            # Prepare comprehensive response
            result = {
                "code": generated_code,
                "model": f"azure-openai-{self.deployment_name}",
                "confidence": 0.95,
                "finish_reason": finish_reason,
                "token_usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost_usd": self._estimate_cost(prompt_tokens, completion_tokens)
                },
                "metadata": {
                    "framework": "vue",
                    "image_size_bytes": len(image_data),
                    "image_format": image_format,
                    "user_prompt": effective_user_prompt,
                    "has_animations": "transition" in generated_code.lower() or "animation" in generated_code.lower(),
                    "has_hover_effects": "hover:" in generated_code.lower() or ":hover" in generated_code.lower(),
                    "component_prediction": self._analyze_generated_component(generated_code),
                    "generation_parameters": {
                        "temperature": "default",  # Using model default
                        "max_tokens": self.max_tokens,
                        "model_version": self.api_version,
                        "top_p": 0.95
                    }
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate code: {str(e)}"
            )
    
    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate the cost of the API call based on token usage.
        
        Note: This is an approximate calculation based on typical Azure OpenAI pricing.
        Actual costs may vary based on your specific pricing tier and region.
        """
        # Approximate pricing (as of 2024) - update based on your actual pricing
        prompt_cost_per_1k = 0.03  # $0.03 per 1K prompt tokens
        completion_cost_per_1k = 0.06  # $0.06 per 1K completion tokens
        
        prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_1k
        completion_cost = (completion_tokens / 1000) * completion_cost_per_1k
        
        return round(prompt_cost + completion_cost, 6)
    
    def _analyze_generated_component(self, code: str) -> Dict[str, Any]:
        """
        Analyze the generated component to extract insights about its functionality.
        """
        if not code:
            return {"error": "No code to analyze"}
        
        code_lower = code.lower()
        
        analysis = {
            "component_type": "vue" if "<template>" in code_lower else "unknown",
            "has_script_setup": "<script setup" in code_lower,
            "has_typescript": "typescript" in code_lower or "lang=\"ts\"" in code_lower,
            "interactive_elements": {
                "buttons": code_lower.count("button") + code_lower.count("@click"),
                "forms": code_lower.count("form") + code_lower.count("@submit"),
                "inputs": code_lower.count("input") + code_lower.count("v-model"),
                "links": code_lower.count("router-link") + code_lower.count("href")
            },
            "animations": {
                "vue_transitions": code_lower.count("<transition") + code_lower.count("transition-"),
                "css_animations": code_lower.count("@keyframes") + code_lower.count("animation:"),
                "hover_effects": code_lower.count("hover:") + code_lower.count(":hover")
            },
            "styling": {
                "tailwind_classes": "class=" in code and any(tw in code_lower for tw in ["bg-", "text-", "p-", "m-", "flex", "grid"]),
                "custom_css": "<style" in code_lower,
                "scoped_styles": "scoped" in code_lower
            },
            "vue_features": {
                "reactive_data": "ref(" in code or "reactive(" in code,
                "computed_properties": "computed(" in code,
                "watchers": "watch(" in code,
                "lifecycle_hooks": any(hook in code for hook in ["onMounted", "onUpdated", "onUnmounted"])
            }
        }
        
        return analysis
    
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

