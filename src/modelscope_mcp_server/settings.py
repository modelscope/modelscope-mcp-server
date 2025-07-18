"""Global settings management for ModelScope MCP Server."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_IMAGE_TO_IMAGE_MODEL,
    DEFAULT_TEXT_TO_IMAGE_MODEL,
    MODELSCOPE_API_ENDPOINT,
    MODELSCOPE_API_INFERENCE_ENDPOINT,
    MODELSCOPE_OPENAPI_ENDPOINT,
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

    # ModelScope API settings
    api_token: str | None = Field(
        default=None, description="ModelScope API token for authentication"
    )
    api_base_url: str = Field(
        default=MODELSCOPE_API_ENDPOINT,
        description="Base URL for ModelScope API",
    )
    openapi_base_url: str = Field(
        default=MODELSCOPE_OPENAPI_ENDPOINT,
        description="Base URL for ModelScope OpenAPI",
    )
    api_inference_base_url: str = Field(
        default=MODELSCOPE_API_INFERENCE_ENDPOINT,
        description="Base URL for ModelScope API Inference",
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
        masked_token = (
            self.api_token[:-8] + "********"
            if self.api_token and len(self.api_token) > 4
            else "Not configured"
        )
        print(f"  • Token: {masked_token}")
        print(f"  • Base URL: {self.api_base_url}")
        print(f"  • OpenAPI URL: {self.openapi_base_url}")
        print(f"  • Inference URL: {self.api_inference_base_url}")
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
