import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Basic App Settings
    app_name: str = Field(default="Canvas Smith API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str = Field(env="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = Field(env="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: str = Field(env="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    
    # AI Service Settings
    ai_timeout: int = Field(default=120, env="AI_TIMEOUT")
    ai_max_retries: int = Field(default=3, env="AI_MAX_RETRIES")
    ai_max_tokens: int = Field(default=6000, env="AI_MAX_TOKENS")  # Increased for complex components
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./canvas_smith.db", env="DATABASE_URL")
    db_echo: bool = Field(default=False, env="DB_ECHO")
    db_pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    
    # Security Settings
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    
    # Azure Blob Storage (Optional)
    azure_storage_connection_string: Optional[str] = Field(default=None, env="AZURE_STORAGE_CONNECTION_STRING")
    blob_container_images: str = Field(default="canvas-images", env="BLOB_CONTAINER_IMAGES")
    blob_container_projects: str = Field(default="canvas-projects", env="BLOB_CONTAINER_PROJECTS")
    blob_container_exports: str = Field(default="canvas-exports", env="BLOB_CONTAINER_EXPORTS")
    
    # Image Processing Settings
    max_image_size: int = Field(default=10*1024*1024, env="MAX_IMAGE_SIZE")  # 10MB
    allowed_image_types: str = Field(
        default="image/jpeg,image/jpg,image/png,image/webp,image/gif,image/bmp,image/tiff", 
        env="ALLOWED_IMAGE_TYPES"
    )
    max_image_width: int = Field(default=2048, env="MAX_IMAGE_WIDTH")
    max_image_height: int = Field(default=2048, env="MAX_IMAGE_HEIGHT")
    
    # CORS Settings
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://localhost:4173",
        env="CORS_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Frontend Settings
    serve_frontend: bool = Field(default=True, env="SERVE_FRONTEND")
    static_dir: str = Field(default="static", env="STATIC_DIR")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    show_error_details: bool = Field(default=True, env="SHOW_ERROR_DETAILS")
    
    # Cache Settings (Redis optional)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Monitoring (Optional)
    appinsights_connection_string: Optional[str] = Field(default=None, env="APPINSIGHTS_CONNECTION_STRING")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def get_cors_origins_list(self) -> List[str]:
        """Convert CORS origins from string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    def get_allowed_image_types_list(self) -> List[str]:
        """Convert allowed image types from string to list."""
        return [mime_type.strip() for mime_type in self.allowed_image_types.split(",") if mime_type.strip()]


# Create global settings instance
settings = Settings()
