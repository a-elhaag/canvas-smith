"""
Production monitoring and metrics for Canvas Smith backend.
"""
import logging
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and store application metrics for monitoring."""
    
    def __init__(self):
        self._metrics = defaultdict(list)
        self._counters = defaultdict(int)
        self._response_times = deque(maxlen=1000)  # Keep last 1000 response times
        self._errors = deque(maxlen=100)  # Keep last 100 errors
        self._lock = threading.Lock()
        
    def record_request(self, endpoint: str, method: str, status_code: int, response_time_ms: float):
        """Record API request metrics."""
        with self._lock:
            timestamp = datetime.now()
            
            # Record response time
            self._response_times.append({
                "timestamp": timestamp,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms
            })
            
            # Update counters
            self._counters[f"requests_total"] += 1
            self._counters[f"requests_{endpoint}"] += 1
            self._counters[f"status_{status_code}"] += 1
            
            # Record errors
            if status_code >= 400:
                self._errors.append({
                    "timestamp": timestamp,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "response_time_ms": response_time_ms
                })
    
    def record_ai_generation(self, 
                           framework: str, 
                           tokens_used: int, 
                           cost_usd: float, 
                           processing_time_ms: float,
                           has_animations: bool,
                           success: bool):
        """Record AI code generation metrics."""
        with self._lock:
            timestamp = datetime.now()
            
            self._metrics["ai_generations"].append({
                "timestamp": timestamp,
                "framework": framework,
                "tokens_used": tokens_used,
                "cost_usd": cost_usd,
                "processing_time_ms": processing_time_ms,
                "has_animations": has_animations,
                "success": success
            })
            
            # Update counters
            self._counters["ai_generations_total"] += 1
            self._counters[f"ai_generations_{framework}"] += 1
            self._counters["total_tokens_used"] += tokens_used
            
            if success:
                self._counters["ai_generations_successful"] += 1
            else:
                self._counters["ai_generations_failed"] += 1
    
    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours."""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter recent response times
            recent_responses = [
                r for r in self._response_times 
                if r["timestamp"] > cutoff_time
            ]
            
            # Filter recent AI generations
            recent_ai_gens = [
                g for g in self._metrics["ai_generations"]
                if g["timestamp"] > cutoff_time
            ]
            
            # Filter recent errors
            recent_errors = [
                e for e in self._errors
                if e["timestamp"] > cutoff_time
            ]
            
            # Calculate response time stats
            response_times = [r["response_time_ms"] for r in recent_responses]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Calculate AI generation stats
            total_tokens = sum(g["tokens_used"] for g in recent_ai_gens)
            total_cost = sum(g["cost_usd"] for g in recent_ai_gens)
            avg_ai_time = sum(g["processing_time_ms"] for g in recent_ai_gens) / len(recent_ai_gens) if recent_ai_gens else 0
            
            # Framework breakdown
            framework_counts = defaultdict(int)
            for g in recent_ai_gens:
                framework_counts[g["framework"]] += 1
            
            return {
                "timeframe_hours": hours,
                "summary": {
                    "total_requests": len(recent_responses),
                    "total_errors": len(recent_errors),
                    "error_rate": len(recent_errors) / len(recent_responses) if recent_responses else 0,
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "ai_generations": len(recent_ai_gens),
                    "total_tokens_used": total_tokens,
                    "total_cost_usd": round(total_cost, 4),
                    "avg_ai_processing_time_ms": round(avg_ai_time, 2)
                },
                "frameworks": dict(framework_counts),
                "recent_errors": [
                    {
                        "timestamp": e["timestamp"].isoformat(),
                        "endpoint": e["endpoint"],
                        "status_code": e["status_code"]
                    }
                    for e in list(recent_errors)[-10:]  # Last 10 errors
                ],
                "performance": {
                    "p50_response_time": self._percentile(response_times, 50) if response_times else 0,
                    "p95_response_time": self._percentile(response_times, 95) if response_times else 0,
                    "p99_response_time": self._percentile(response_times, 99) if response_times else 0
                }
            }
    
    def _percentile(self, data: list, percentile: int) -> float:
        """Calculate percentile value."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(minutes=5)  # Last 5 minutes
            
            recent_responses = [
                r for r in self._response_times 
                if r["timestamp"] > cutoff_time
            ]
            
            recent_errors = [
                e for e in self._errors
                if e["timestamp"] > cutoff_time
            ]
            
            error_rate = len(recent_errors) / len(recent_responses) if recent_responses else 0
            
            # Health determination
            if error_rate > 0.5:  # More than 50% errors
                health_status = "unhealthy"
            elif error_rate > 0.1:  # More than 10% errors
                health_status = "degraded"
            else:
                health_status = "healthy"
            
            return {
                "status": health_status,
                "error_rate_5min": round(error_rate, 3),
                "requests_5min": len(recent_responses),
                "errors_5min": len(recent_errors),
                "timestamp": datetime.now().isoformat()
            }


# Global metrics collector instance
metrics_collector = MetricsCollector()