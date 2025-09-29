import os
from datetime import datetime

import uvicorn
# Import AI routes
from app.api.routes.ai import router as ai_router
# Import settings
from app.core.config import settings
# Import middleware
from app.middleware.metrics_middleware import MetricsMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for Canvas Smith application - Convert sketches to code with AI",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug,
)

# Configure CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add metrics middleware for production monitoring
app.add_middleware(MetricsMiddleware)

# Include AI routes
app.include_router(ai_router)


# Response models
class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str


class StatusResponse(BaseModel):
    backend_status: str
    message: str
    timestamp: str


if settings.serve_frontend and os.path.isdir(settings.static_dir):
    # Mount static assets (e.g. /assets/*, CSS, JS) from Vite build
    # Expect Vite output copied to /app/static by Docker multi-stage build
    # Typical Vite structure: index.html + assets/ directory
    # We only mount the assets folder explicitly if it exists to avoid 404 noise
    assets_path = os.path.join(settings.static_dir, "assets")
    if os.path.isdir(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():  # type: ignore
        """Serve the built frontend index.html if present, otherwise fallback JSON."""
        index_file = os.path.join(settings.static_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file, media_type="text/html")
        return JSONResponse(
            {
                "status": "success",
                "message": "Canvas Smith Backend is working (no built frontend found).",
                "timestamp": datetime.now().isoformat(),
                "version": settings.app_version,
            }
        )

else:
    # Fallback original JSON root if we are not serving the frontend
    @app.get("/", response_model=HealthResponse)
    async def root():  # type: ignore
        return HealthResponse(
            status="success",
            message="Canvas Smith Backend is working! 🎨",
            timestamp=datetime.now().isoformat(),
            version=settings.app_version,
        )
# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        message="Backend is healthy and running",
        timestamp=datetime.now().isoformat(),
        version=settings.app_version,
    )


# API status endpoint
@app.get("/api/status", response_model=StatusResponse)
async def api_status():
    """API status endpoint that the frontend can call."""
    return StatusResponse(
        backend_status="connected",
        message="Backend is working and connected! ✅",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/api/info")
async def api_info():
    """Get API information and deployment mode."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Backend API for Canvas Smith application",
        "serve_frontend": settings.serve_frontend,
        "static_dir_present": os.path.isdir(settings.static_dir),
        "endpoints": {
            "root": "/",
            "health": "/health",
            "status": "/api/status",
            "info": "/api/info",
            "docs": "/docs",
        },
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.reload, 
        log_level=settings.log_level.lower()
    )
