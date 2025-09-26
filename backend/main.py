"""
Canvas Smith Backend API
A simple FastAPI backend for the Canvas Smith application.
"""

import os
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="Canvas Smith API",
    description="Backend API for Canvas Smith application",
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


# Root endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint that confirms the backend is working."""
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


# API info endpoint
@app.get("/api/info")
async def api_info():
    """Get API information."""
    return {
        "name": "Canvas Smith API",
        "version": "1.0.0",
        "description": "Backend API for Canvas Smith application",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "status": "/api/status",
            "info": "/api/info",
            "docs": "/docs",
        },
        "frontend_connection": "ready",
        "timestamp": datetime.now().isoformat(),
    }

# Serve built frontend (static) if available
SERVE_FRONTEND = os.getenv("SERVE_FRONTEND", "false").lower() in {"1", "true", "yes"}
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
INDEX_FILE = os.path.join(STATIC_DIR, "index.html")

if SERVE_FRONTEND and os.path.isdir(STATIC_DIR):
    # Mount all static assets at root path except API paths
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    @app.get("/{full_path:path}")  # Fallback for SPA routing
    async def spa_fallback(full_path: str):  # noqa: D401
        if os.path.isfile(os.path.join(STATIC_DIR, full_path)):
            return FileResponse(os.path.join(STATIC_DIR, full_path))
        if os.path.exists(INDEX_FILE):
            return FileResponse(INDEX_FILE)
        return JSONResponse(status_code=404, content={"detail": "Not Found"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
