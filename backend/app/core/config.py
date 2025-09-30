from datetime import timedelta
from typing import Annotated, List, Literal, Optional

from pydantic import (AnyUrl, ByteSize, Field, NonNegativeInt, PositiveInt,
                      SecretStr)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive = True,   # safer in prod
        extra="ignore"
    )

    # Basic
    app_name: str = Field(default="Canvas Smith API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: PositiveInt = Field(default=8000, alias="PORT")
    reload: bool = Field(default=False, alias="RELOAD")  # set from env; don’t default to True

    # Azure OpenAI
    azure_openai_api_key: SecretStr = Field(alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: AnyUrl = Field(alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: str = Field(alias="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_api_version: str = Field(default="2024-02-01", alias="AZURE_OPENAI_API_VERSION")

    # AI
    ai_timeout: PositiveInt = Field(default=120, alias="AI_TIMEOUT")
    ai_max_retries: NonNegativeInt = Field(default=3, alias="AI_MAX_RETRIES")
    ai_max_tokens: PositiveInt = Field(default=6000, alias="AI_MAX_TOKENS")

    # Database
    database_url: str = Field(default="sqlite:///./canvas_smith.db", alias="DATABASE_URL")
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    db_pool_size: NonNegativeInt = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: NonNegativeInt = Field(default=10, alias="DB_MAX_OVERFLOW")

    # Security
    secret_key: Optional[SecretStr] = Field(default=None, alias="SECRET_KEY")  # require in prod

    # Azure Blob
    azure_storage_connection_string: Optional[SecretStr] = Field(default=None, alias="AZURE_STORAGE_CONNECTION_STRING")
    blob_container_images: str = Field(default="canvas-images", alias="BLOB_CONTAINER_IMAGES")
    blob_container_projects: str = Field(default="canvas-projects", alias="BLOB_CONTAINER_PROJECTS")
    blob_container_exports: str = Field(default="canvas-exports", alias="BLOB_CONTAINER_EXPORTS")

    # Images
    max_image_size: ByteSize = Field(default=ByteSize(10 * 1024 * 1024), alias="MAX_IMAGE_SIZE")
    allowed_image_types: List[str] = Field(
        default_factory=lambda: [
            "image/jpeg","image/jpg","image/png","image/webp","image/gif","image/bmp","image/tiff"
        ],
        alias="ALLOWED_IMAGE_TYPES"
    )
    max_image_width: PositiveInt = Field(default=2048, alias="MAX_IMAGE_WIDTH")
    max_image_height: PositiveInt = Field(default=2048, alias="MAX_IMAGE_HEIGHT")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173","http://localhost:3000","http://localhost:4173"],
        alias="CORS_ORIGINS"
    )

    # Rate limiting
    rate_limit_requests: PositiveInt = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: timedelta = Field(default=timedelta(hours=1), alias="RATE_LIMIT_WINDOW")

    # Frontend
    serve_frontend: bool = Field(default=False, alias="SERVE_FRONTEND")
    static_dir: str = Field(default="static", alias="STATIC_DIR")

    # Logging
    log_level: Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"] = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", alias="LOG_FORMAT")
    show_error_details: bool = Field(default=True, alias="SHOW_ERROR_DETAILS")

    # Cache
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    cache_ttl: timedelta = Field(default=timedelta(hours=1), alias="CACHE_TTL")

    # Monitoring
    appinsights_connection_string: Optional[SecretStr] = Field(default=None, alias="APPINSIGHTS_CONNECTION_STRING")
    sentry_dsn: Optional[SecretStr] = Field(default=None, alias="SENTRY_DSN")

    # Convenience
    @property
    def is_prod(self) -> bool:
        return not self.debug

    @property
    def should_reload(self) -> bool:
        # force off in prod unless explicitly enabled
        return self.reload and not self.is_prod

    def get_cors_origins_list(self) -> List[str]:
        """Return a copy of configured CORS origins."""
        return list(self.cors_origins)

    def get_allowed_image_types_list(self) -> List[str]:
        """Return a copy of allowed image MIME types."""
        return list(self.allowed_image_types)

settings = Settings()