# Single-stage build for Canvas Smith
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV SERVE_FRONTEND=true
ENV STATIC_DIR=static

# Set working directory
WORKDIR /app

# Install system dependencies (including Node.js for frontend build)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@latest \
    && rm -rf /var/lib/apt/lists/*

# Copy and install backend dependencies first (for better layer caching)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend source and build
COPY frontend/ ./frontend/
WORKDIR /app/frontend
ENV CI=true
RUN pnpm install --frozen-lockfile
RUN pnpm run build

# Switch back to app directory and copy backend source
WORKDIR /app
COPY backend/ ./

# Move built frontend to static directory
RUN cp -r frontend/dist/* ./static/ 2>/dev/null || mkdir -p ./static

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose the port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)" || exit 1

# Start command - backend will serve both API and frontend
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]