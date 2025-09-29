"""
Enhanced validation utilities for Canvas Smith backend.
"""
import re
from typing import List, Optional

from fastapi import HTTPException


def validate_framework(framework: str) -> str:
    """Validate and normalize framework name."""
    allowed_frameworks = {
        "html", "react", "vue", "angular", 
        "tailwind", "bootstrap", "svelte", "nextjs"
    }
    
    framework_lower = framework.lower().strip()
    if framework_lower not in allowed_frameworks:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported framework '{framework}'. Allowed: {', '.join(allowed_frameworks)}"
        )
    
    return framework_lower

def validate_instructions(instructions: Optional[str]) -> Optional[str]:
    """Validate and sanitize additional instructions."""
    if not instructions:
        return None
    
    # Basic length check
    if len(instructions) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Additional instructions too long (max 1000 characters)"
        )
    
    # Remove potentially harmful content
    # This is a basic example - in production you'd want more sophisticated filtering
    harmful_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
    ]
    
    cleaned = instructions
    for pattern in harmful_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    return cleaned.strip()

def validate_conversation_id(conv_id: Optional[str]) -> Optional[str]:
    """Validate conversation ID format."""
    if not conv_id:
        return None
    
    # Simple UUID-like pattern validation
    if not re.match(r'^[a-f0-9-]{8,36}$', conv_id.lower()):
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID format"
        )
    
    return conv_id.lower()