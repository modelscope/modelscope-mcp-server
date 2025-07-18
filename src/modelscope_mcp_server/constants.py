"""Global constants for ModelScope MCP Server."""

# ModelScope domains
MODELSCOPE_DOMAIN = "https://modelscope.cn"
MODELSCOPE_API_INFERENCE_DOMAIN = "https://api-inference.modelscope.cn"

# ModelScope API endpoints
MODELSCOPE_API_ENDPOINT = f"{MODELSCOPE_DOMAIN}/api/v1"
MODELSCOPE_OPENAPI_ENDPOINT = f"{MODELSCOPE_DOMAIN}/openapi/v1"
MODELSCOPE_API_INFERENCE_ENDPOINT = f"{MODELSCOPE_API_INFERENCE_DOMAIN}/v1"

# Default model IDs for content generation
DEFAULT_TEXT_TO_IMAGE_MODEL = "MusePublic/489_ckpt_FLUX_1"
DEFAULT_IMAGE_TO_IMAGE_MODEL = "black-forest-labs/FLUX.1-Kontext-dev"
