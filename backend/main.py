"""
Canvas Smith Backend API
A simple FastAPI backend for the Canvas Smith application.
"""

import os
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Create FastAPI app
SERVE_FRONTEND = os.getenv("SERVE_FRONTEND", "true").lower() in {"1", "true", "yes"}
STATIC_DIR = os.getenv("STATIC_DIR", "static")

app = FastAPI(
    title="Canvas Smith API",
    description="Backend API for Canvas Smith application (single-container deployment)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "http://localhost:4173",  # Vite preview
        "*",  # Allow all origins for development - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


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


if SERVE_FRONTEND and os.path.isdir(STATIC_DIR):
    # Mount static assets (e.g. /assets/*, CSS, JS) from Vite build
    # Expect Vite output copied to /app/static by Docker multi-stage build
    # Typical Vite structure: index.html + assets/ directory
    # We only mount the assets folder explicitly if it exists to avoid 404 noise
    assets_path = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():  # type: ignore
        """Serve the built frontend index.html if present, otherwise fallback JSON."""
        index_file = os.path.join(STATIC_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file, media_type="text/html")
        return JSONResponse(
            {
                "status": "success",
                "message": "Canvas Smith Backend is working (no built frontend found).",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
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
            version="1.0.0",
        )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        message="Backend is healthy and running",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
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
        "name": "Canvas Smith API",
        "version": "1.0.0",
        "description": "Backend API for Canvas Smith application",
        "serve_frontend": SERVE_FRONTEND,
        "static_dir_present": os.path.isdir(STATIC_DIR),
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
