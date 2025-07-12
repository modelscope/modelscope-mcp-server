"""Global settings management for ModelScope MCP Server."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global settings for ModelScope MCP Server."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MODELSCOPE_",
        case_sensitive=False,
        extra="ignore",
    )

    # ModelScope API settings
    api_key: str | None = Field(
        default=None, description="ModelScope API key for authentication"
    )

    api_inference_base_url: str = Field(
        default="https://api-inference.modelscope.cn/v1",
        description="Base URL for ModelScope API Inference",
    )

    # Default model settings
    default_image_generation_model: str = Field(
        default="MusePublic/489_ckpt_FLUX_1",
        description="Default model for image generation",
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str | None) -> str | None:
        """Validate API key format."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v

    @property
    def images_endpoint(self) -> str:
        """Get the full images generation endpoint URL."""
        return f"{self.api_inference_base_url}/images/generations"

    def is_api_key_configured(self) -> bool:
        """Check if API key is configured."""
        return self.api_key is not None and len(self.api_key) > 0


# Global settings instance
settings = Settings()
