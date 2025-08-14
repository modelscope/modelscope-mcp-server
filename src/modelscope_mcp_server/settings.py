"""Global settings management for ModelScope MCP Server."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_API_TIMEOUT_SECONDS,
    DEFAULT_IMAGE_GENERATION_TIMEOUT_SECONDS,
    DEFAULT_IMAGE_TO_IMAGE_MODEL,
    DEFAULT_MAX_POLL_ATTEMPTS,
    DEFAULT_MODELSCOPE_API_INFERENCE_DOMAIN,
    DEFAULT_MODELSCOPE_DOMAIN,
    DEFAULT_TASK_POLL_INTERVAL_SECONDS,
    DEFAULT_TEXT_TO_IMAGE_MODEL,
)


class Settings(BaseSettings):
    """Global settings for ModelScope MCP Server."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MODELSCOPE_",
        case_sensitive=False,
        extra="ignore",
    )

    # Authentication settings
    api_token: str | None = Field(default=None, description="ModelScope API token for authentication")

    # Domain settings
    main_domain: str = Field(
        default=DEFAULT_MODELSCOPE_DOMAIN,
        description="ModelScope website domain",
    )
    api_inference_domain: str = Field(
        default=DEFAULT_MODELSCOPE_API_INFERENCE_DOMAIN,
        description="ModelScope API inference domain",
    )

    # Default model settings
    default_text_to_image_model: str = Field(
        default=DEFAULT_TEXT_TO_IMAGE_MODEL,
        description="Default model for text-to-image generation",
    )
    default_image_to_image_model: str = Field(
        default=DEFAULT_IMAGE_TO_IMAGE_MODEL,
        description="Default model for image-to-image generation",
    )

    # Default timeout settings
    default_api_timeout_seconds: int = Field(
        default=DEFAULT_API_TIMEOUT_SECONDS,
        description="Default timeout for API requests",
    )
    default_image_generation_timeout_seconds: int = Field(
        default=DEFAULT_IMAGE_GENERATION_TIMEOUT_SECONDS,
        description="Default timeout for image generation requests",
    )

    # Task polling
    task_poll_interval_seconds: int = Field(
        default=DEFAULT_TASK_POLL_INTERVAL_SECONDS,
        description="Polling interval in seconds when waiting for async tasks",
    )
    max_poll_attempts: int = Field(
        default=DEFAULT_MAX_POLL_ATTEMPTS,
        description="Maximum number of polling attempts for async tasks",
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("api_token")
    @classmethod
    def validate_api_token(cls, v: str | None) -> str | None:
        """Validate API token format."""
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

    def is_api_token_configured(self) -> bool:
        """Check if API token is configured."""
        return self.api_token is not None and len(self.api_token) > 0

    def show_settings(self) -> None:
        """Display current configuration settings in a formatted way."""
        print("=" * 60)
        print("📋 Global Settings")
        print("=" * 60)

        # API Configuration
        print("🔑 API Configuration:")
        token_status = "Configured" if self.api_token else "Not configured"
        print(f"  • Token: {token_status}")
        print(f"  • Main Domain: {self.main_domain}")
        print(f"  • API Inference Domain: {self.api_inference_domain}")
        print()

        # Default Models
        print("🤖 Default Models:")
        print(f"  • Text-to-Image: {self.default_text_to_image_model}")
        print(f"  • Image-to-Image: {self.default_image_to_image_model}")
        print()

        # System Settings
        print("⚙️ System Settings:")
        print(f"  • Log Level: {self.log_level}")
        print("=" * 60)
        print()


# Global settings instance
settings = Settings()
