"""ModelScope HTTP client for unified API requests."""

import json
import logging as std_logging
import time
from typing import Any

import requests
from fastmcp.utilities import logging

from modelscope_mcp_server.utils.metadata import get_server_version

from .settings import settings

logger = logging.get_logger(__name__)


class ModelScopeClient:
    """Unified client for ModelScope API requests."""

    def __init__(self, timeout: int = settings.default_api_timeout_seconds):
        """Initialize the ModelScope client.

        Args:
            timeout: Default timeout for requests in seconds

        """
        self.timeout = timeout
        self._session = requests.Session()

    def _get_default_headers(self) -> dict[str, str]:
        """Get default headers for all requests."""
        headers = {
            "User-Agent": f"modelscope-mcp-server/{get_server_version()}",
        }

        if settings.is_api_token_configured():
            headers["Authorization"] = f"Bearer {settings.api_token}"
            # TODO: Remove this once all API endpoints support Bearer token
            headers["Cookie"] = f"m_session_id={settings.api_token}"

        return headers

    def _prepare_request_headers(
        self, kwargs: dict, additional_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        """Prepare headers for a request and log them if DEBUG is enabled.

        Args:
            kwargs: Request kwargs, may contain 'headers' key that will be popped
            additional_headers: Additional headers to add to defaults

        Returns:
            Final headers dict to use for the request

        """
        headers = self._get_default_headers()
        if additional_headers:
            headers.update(additional_headers)
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Log request headers if DEBUG level is enabled
        if logger.isEnabledFor(std_logging.DEBUG):
            headers_str = "\n".join([f"  {key}: {value}" for key, value in headers.items()])
            logger.debug(f"Request headers:\n{headers_str}")

        return headers

    def _handle_response(self, response: requests.Response, start_time: float) -> dict[str, Any]:
        """Handle common response processing."""
        # Log response basic info
        elapsed_time = time.time() - start_time
        content_length = len(response.content) if response.content else 0
        logger.info(
            f"Response: {response.status_code} {response.reason}, size: {content_length} bytes, "
            f"elapsed: {elapsed_time:.3f}s"
        )

        # Log response headers if DEBUG level is enabled
        if logger.isEnabledFor(std_logging.DEBUG):
            headers_str = "\n".join([f"  {key}: {value}" for key, value in response.headers.items()])
            logger.debug(f"Response headers:\n{headers_str}")

        try:
            response_json = response.json()
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}") from e

        # Log JSON body if DEBUG level is enabled
        if logger.isEnabledFor(std_logging.DEBUG):
            formatted_json = json.dumps(response_json, indent=2, ensure_ascii=False)
            logger.debug(f"Response body:\n{formatted_json}")

        # Raise an exception if the response is not successful
        response.raise_for_status()

        # If 'success = false' (case-insensitive), raise an exception
        if isinstance(response_json, dict):
            for key in response_json:
                if key.lower() == "success" and response_json[key] is False:
                    raise RuntimeError(f"Server returned error: {response_json}")

        return response_json

    def get(
        self, url: str, params: dict[str, Any] | None = None, timeout: int | None = None, **kwargs
    ) -> dict[str, Any]:
        """Perform GET request.

        Args:
            url: The URL to request
            params: Query parameters
            timeout: Request timeout in seconds
            **kwargs: Additional arguments passed to requests.get

        Returns:
            Parsed JSON response

        Raises:
            TimeoutError: If request times out
            Exception: For other request errors

        """
        logger.info(f"Sending GET request to {url} with params: {params}")
        start_time = time.time()
        try:
            headers = self._prepare_request_headers(kwargs)

            response = self._session.get(url, params=params, timeout=timeout or self.timeout, headers=headers, **kwargs)
            return self._handle_response(response, start_time)
        except requests.exceptions.Timeout as e:
            raise TimeoutError("Request timeout - please try again later") from e

    def post(
        self,
        url: str,
        json_data: dict[str, Any] | None = None,
        timeout: int | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Perform POST request.

        Args:
            url: The URL to request
            json_data: JSON data to send (will be serialized)
            timeout: Request timeout in seconds
            **kwargs: Additional arguments passed to requests.post

        Returns:
            Parsed JSON response

        Raises:
            TimeoutError: If request times out
            Exception: For other request errors

        """
        return self._request_with_data("POST", url, json_data, timeout, **kwargs)

    def put(
        self, url: str, json_data: dict[str, Any] | None = None, timeout: int | None = None, **kwargs
    ) -> dict[str, Any]:
        """Perform PUT request.

        Args:
            url: The URL to request
            json_data: JSON data to send
            timeout: Request timeout in seconds
            **kwargs: Additional arguments passed to requests.put

        Returns:
            Parsed JSON response

        Raises:
            TimeoutError: If request times out
            Exception: For other request errors

        """
        return self._request_with_data("PUT", url, json_data, timeout, **kwargs)

    def _request_with_data(
        self,
        method: str,
        url: str,
        json_data: dict[str, Any] | None = None,
        timeout: int | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Perform HTTP request with JSON data."""
        logger.info(f"Sending {method} request to {url} with data: {json_data}")
        start_time = time.time()
        try:
            headers = self._prepare_request_headers(kwargs, {"Content-Type": "application/json"})

            response = self._session.request(
                method,
                url,
                data=json.dumps(json_data, ensure_ascii=False).encode("utf-8") if json_data else None,
                timeout=timeout or self.timeout,
                headers=headers,
                **kwargs,
            )
            return self._handle_response(response, start_time)
        except requests.exceptions.Timeout as e:
            raise TimeoutError("Request timeout - please try again later") from e

    def close(self):
        """Close the session."""
        self._session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client instance with default settings
default_client = ModelScopeClient()
