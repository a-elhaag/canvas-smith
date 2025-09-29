"""
Middleware for request tracking and metrics collection.
"""
import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..monitoring.metrics import metrics_collector

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and record metrics."""
        start_time = time.time()
        
        # Get request info
        method = request.method
        path = request.url.path
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Record metrics (skip health checks to reduce noise)
        if not path.startswith("/health"):
            metrics_collector.record_request(
                endpoint=path,
                method=method,
                status_code=response.status_code,
                response_time_ms=response_time_ms
            )
            
            # Log slow requests
            if response_time_ms > 5000:  # 5 seconds
                logger.warning(f"Slow request: {method} {path} took {response_time_ms:.0f}ms")
        
        return response