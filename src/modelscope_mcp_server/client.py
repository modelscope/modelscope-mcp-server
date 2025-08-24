"""ModelScope HTTP client with connection pooling."""

import asyncio
import json
import logging as std_logging
import time
import uuid
from typing import Any

import httpx
from fastmcp.utilities import logging

from modelscope_mcp_server.utils.metadata import get_server_version
from modelscope_mcp_server.utils.text import truncate_for_log

from .settings import settings

logger = logging.get_logger(__name__)

LOG_BODY_MAX_CHARS = 1024
REQUEST_ID_HEADER = "X-Request-ID"


class ModelScopeClient:
    """High-performance HTTP client with connection pooling.

    This client maintains a global connection pool that is shared across all requests,
    providing optimal performance for both single-user and high-concurrency scenarios.
    """

    # Class-level shared resources
    _global_client: httpx.AsyncClient | None = None
    _initialization_lock = asyncio.Lock()
    _shutdown_event = asyncio.Event()

    def __init__(self, timeout: int = settings.default_api_timeout_seconds) -> None:
        """Initialize the client configuration.

        Args:
            timeout: Default timeout for requests in seconds

        """
        self.timeout = timeout

    @classmethod
    async def _ensure_global_client(cls) -> httpx.AsyncClient:
        """Ensure the global client pool exists and is healthy.

        Uses double-checked locking pattern for thread-safe initialization.
        """
        if cls._global_client is None or cls._global_client.is_closed:
            async with cls._initialization_lock:
                # Double-check after acquiring lock
                if cls._global_client is None or cls._global_client.is_closed:
                    logger.info("Initializing global connection pool")

                    event_hooks = {
                        "request": [cls._log_request],
                        "response": [cls._log_response, cls._raise_on_error],
                    }

                    default_headers = {
                        "User-Agent": f"modelscope-mcp-server/{get_server_version()}",
                    }

                    if settings.is_api_token_configured():
                        default_headers["Authorization"] = f"Bearer {settings.api_token}"
                        # TODO: Remove this once all API endpoints support Bearer token
                        default_headers["Cookie"] = f"m_session_id={settings.api_token}"

                    cls._global_client = httpx.AsyncClient(
                        limits=httpx.Limits(
                            max_keepalive_connections=100,  # Keep 100 persistent connections
                            max_connections=200,  # Allow up to 200 concurrent connections
                            keepalive_expiry=30,  # Keep connections alive for 30 seconds
                        ),
                        timeout=httpx.Timeout(
                            connect=5.0,  # Connection timeout
                            read=30.0,  # Read timeout
                            write=30.0,  # Write timeout
                            pool=5.0,  # Pool acquisition timeout
                        ),
                        # Enable HTTP/2 for multiplexing
                        http2=True,
                        headers=default_headers,
                        event_hooks=event_hooks,
                        follow_redirects=True,
                        # Don't use system proxy settings
                        trust_env=False,
                    )

                    logger.info(
                        f"Global connection pool initialized: max_keepalive={100}, max_connections={200}, http2=True"
                    )

        return cls._global_client

    @staticmethod
    async def _log_request(request: httpx.Request) -> None:
        """Event hook for logging HTTP requests."""
        request_id = str(uuid.uuid4())[:8]
        request.headers[REQUEST_ID_HEADER] = request_id
        request.extensions["start_time"] = time.time()

        logger.info(
            f"[{request_id}] {request.method} {request.url} "
            f"(params: {dict(request.url.params) if request.url.params else None})"
        )

        if logger.isEnabledFor(std_logging.DEBUG):
            # Log headers (with sensitive data masked)
            safe_headers = {
                k: v if k.lower() not in ["authorization", "cookie"] else "******" for k, v in request.headers.items()
            }
            headers_str = "\n".join([f"  {key}: {value}" for key, value in safe_headers.items()])
            logger.debug(f"[{request_id}] Request headers:\n{headers_str}")

            # Log body if present
            if request.content:
                try:
                    body = request.content.decode("utf-8")
                    json_body = json.loads(body)
                    formatted_body = json.dumps(json_body, indent=2, ensure_ascii=False)
                    logger.debug(
                        f"[{request_id}] Request body:\n{truncate_for_log(formatted_body, LOG_BODY_MAX_CHARS)}"
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    raw = request.content.decode("utf-8", errors="replace")
                    logger.debug(f"[{request_id}] Request body: {truncate_for_log(raw, LOG_BODY_MAX_CHARS)}")

    @staticmethod
    async def _log_response(response: httpx.Response) -> None:
        """Event hook for logging HTTP responses."""
        request_id = response.request.headers.get(REQUEST_ID_HEADER, "unknown")

        start_time = response.request.extensions.get("start_time", time.time())
        elapsed_time = time.time() - start_time

        content_length = response.headers.get("content-length", "unknown")

        log_level = std_logging.INFO if response.is_success else std_logging.WARNING
        logger.log(
            log_level,
            f"[{request_id}] Response: {response.status_code} {response.reason_phrase}, "
            f"size: {content_length} bytes, elapsed: {elapsed_time:.3f}s",
        )

        if logger.isEnabledFor(std_logging.DEBUG):
            headers_str = "\n".join([f"  {key}: {value}" for key, value in response.headers.items()])
            logger.debug(f"[{request_id}] Response headers:\n{headers_str}")

            try:
                if not response.is_stream_consumed:
                    await response.aread()
                response_json = response.json()
                formatted_json = json.dumps(response_json, indent=2, ensure_ascii=False)
                logger.debug(f"[{request_id}] Response body:\n{truncate_for_log(formatted_json, LOG_BODY_MAX_CHARS)}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                logger.debug(f"[{request_id}] Response body: {truncate_for_log(response.text, LOG_BODY_MAX_CHARS)}")

    @staticmethod
    async def _raise_on_error(response: httpx.Response) -> None:
        """Event hook to check for API-specific errors."""
        request_id = response.request.headers.get(REQUEST_ID_HEADER, "unknown")

        if not response.is_stream_consumed:
            await response.aread()

        # Check for business error first: success=false
        try:
            response_json = response.json()
            if isinstance(response_json, dict):
                lowered = {str(k).lower(): v for k, v in response_json.items()}
                if lowered.get("success") is False:
                    error_msg = lowered.get("message", "Unknown error")
                    error_code = lowered.get("code", "UNKNOWN")
                    status = response.status_code
                    logger.error(
                        f"[{request_id}] HTTP {status} {response.reason_phrase} "
                        f"API error: code={error_code}, message={error_msg}"
                    )
                    if response.is_error:
                        raise httpx.HTTPStatusError(
                            f"[status={status}] API error [{error_code}]: {error_msg}",
                            request=response.request,
                            response=response,
                        )
                    else:
                        raise RuntimeError(f"[status={status}] API error [{error_code}]: {error_msg}")
        except json.JSONDecodeError:
            pass

        response.raise_for_status()

    async def get(
        self, url: str, params: dict[str, Any] | None = None, timeout: int | None = None, **kwargs
    ) -> dict[str, Any]:
        """Perform GET request using the global connection pool.

        Args:
            url: The URL to request
            params: Query parameters
            timeout: Request timeout in seconds (overrides default)
            **kwargs: Additional arguments passed to httpx

        Returns:
            Parsed JSON response

        Raises:
            TimeoutError: If request times out
            RuntimeError: For API errors
            httpx.HTTPStatusError: For HTTP errors

        """
        client = await self._ensure_global_client()

        try:
            response = await client.get(url, params=params, timeout=timeout or self.timeout, **kwargs)
            return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError("Request timeout - please try again later") from e

    async def post(
        self,
        url: str,
        json_data: dict[str, Any] | None = None,
        timeout: int | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Perform POST request using the global connection pool."""
        client = await self._ensure_global_client()

        try:
            response = await client.post(url, json=json_data, timeout=timeout or self.timeout, **kwargs)
            return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError("Request timeout - please try again later") from e

    async def put(
        self, url: str, json_data: dict[str, Any] | None = None, timeout: int | None = None, **kwargs
    ) -> dict[str, Any]:
        """Perform PUT request using the global connection pool."""
        client = await self._ensure_global_client()

        try:
            response = await client.put(url, json=json_data, timeout=timeout or self.timeout, **kwargs)
            return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError("Request timeout - please try again later") from e

    @classmethod
    async def close_global_pool(cls) -> None:
        """Close the global connection pool gracefully.

        Should be called during application shutdown.
        """
        if cls._global_client and not cls._global_client.is_closed:
            logger.info("Closing global connection pool")
            await cls._global_client.aclose()
            cls._global_client = None


def get_client() -> ModelScopeClient:
    """Get a ModelScope client instance.

    Returns a new client instance that uses the global connection pool.
    """
    return ModelScopeClient()
