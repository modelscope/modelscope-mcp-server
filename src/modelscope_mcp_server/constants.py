"""Global constants for ModelScope MCP Server."""

# ModelScope domains
DEFAULT_MODELSCOPE_DOMAIN = "https://modelscope.cn"
DEFAULT_MODELSCOPE_API_INFERENCE_DOMAIN = "https://api-inference.modelscope.cn"

# Default model IDs for content generation
DEFAULT_TEXT_TO_IMAGE_MODEL = "Qwen/Qwen-Image"
DEFAULT_IMAGE_TO_IMAGE_MODEL = "black-forest-labs/FLUX.1-Kontext-dev"

# Default timeout for requests
DEFAULT_API_TIMEOUT_SECONDS = 5
DEFAULT_IMAGE_GENERATION_TIMEOUT_SECONDS = 300

# Task polling interval (seconds)
DEFAULT_TASK_POLL_INTERVAL_SECONDS = 5

# Maximum number of polling attempts for async tasks
DEFAULT_MAX_POLL_ATTEMPTS = 60  # 60 attempts * 5 seconds = 5 minutes max
