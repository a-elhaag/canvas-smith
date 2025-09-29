import time
from typing import Dict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_window: int = 100, window_seconds: int = 3600):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.clients: Dict[str, Dict] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = time.time()
        
        if client_id not in self.clients:
            self.clients[client_id] = {"requests": 1, "window_start": now}
            return True
        
        client_data = self.clients[client_id]
        
        # Reset window if expired
        if now - client_data["window_start"] > self.window_seconds:
            client_data["requests"] = 1
            client_data["window_start"] = now
            return True
        
        # Check if within limits
        if client_data["requests"] < self.requests_per_window:
            client_data["requests"] += 1
            return True
        
        return False

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for FastAPI."""
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/api/status"]:
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    
    # You would implement rate limiter instance here
    # For now, just proceed
    return await call_next(request)