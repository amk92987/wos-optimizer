"""
Reusable OpenAI API client for code review.

Reads OPENAI_API_KEY from environment variables, masks the key in logs,
uses gpt-4o-mini by default for cost efficiency, and includes retry logic
with exponential backoff.
"""

import json
import logging
import os
import time
from typing import Any, Optional

from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.2  # Low temperature for consistent, analytical reviews
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1.0  # seconds


def _mask_key(key: str) -> str:
    """Mask an API key, showing only the last 4 characters."""
    if not key or len(key) < 8:
        return "****"
    return f"****{key[-4:]}"


class OpenAIReviewClient:
    """
    OpenAI API client for code review requests.

    Handles authentication, retries, and structured JSON responses.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client: Optional[OpenAI] = None
        self._api_key: Optional[str] = None

    def _ensure_client(self) -> OpenAI:
        """Lazily initialize the OpenAI client, reading the key from env."""
        if self._client is not None:
            return self._client

        self._api_key = os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is not set.\n"
                "Set it with:\n"
                "  Windows:  set OPENAI_API_KEY=sk-...\n"
                "  Unix:     export OPENAI_API_KEY=sk-...\n"
                "The key is never logged or stored by this tool."
            )

        masked = _mask_key(self._api_key)
        logger.info("OpenAI client initialized (key: %s, model: %s)", masked, self.model)

        self._client = OpenAI(api_key=self._api_key)
        return self._client

    def chat(
        self,
        system_message: str,
        user_message: str,
        response_format: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Send a chat completion request and return the parsed JSON response.

        Args:
            system_message: The system prompt defining the reviewer role.
            user_message: The user prompt with code/diff and review request.
            response_format: Optional response format spec (e.g., {"type": "json_object"}).

        Returns:
            Parsed JSON dict from the model response.

        Raises:
            EnvironmentError: If OPENAI_API_KEY is not set.
            RuntimeError: If all retries are exhausted.
        """
        client = self._ensure_client()

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        return self._send_with_retry(kwargs)

    def chat_multi_turn(
        self,
        system_message: str,
        conversation: list[dict[str, str]],
        response_format: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Send a multi-turn conversation and return the parsed JSON response.

        Args:
            system_message: The system prompt.
            conversation: List of {"role": "user"|"assistant", "content": "..."} messages.
            response_format: Optional response format spec.

        Returns:
            Parsed JSON dict from the model response.
        """
        client = self._ensure_client()

        messages = [{"role": "system", "content": system_message}]
        messages.extend(conversation)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        return self._send_with_retry(kwargs)

    def _send_with_retry(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Send request with exponential backoff retry logic.

        Retries on connection errors and rate limits. Does not retry on
        authentication or other client errors.
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content

                if not content:
                    logger.warning("Empty response from OpenAI (attempt %d/%d)", attempt, MAX_RETRIES)
                    last_error = RuntimeError("Empty response from OpenAI")
                    continue

                # Try to parse as JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, wrap the raw text in a structured response
                    logger.warning(
                        "Response was not valid JSON (attempt %d/%d), wrapping raw text",
                        attempt, MAX_RETRIES,
                    )
                    return {
                        "summary": content,
                        "top_concerns": [],
                        "recommended_changes": [],
                        "follow_up_questions": [],
                        "confidence": "low",
                        "_raw_response": True,
                    }

            except RateLimitError as e:
                delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Rate limited (attempt %d/%d), retrying in %.1fs",
                    attempt, MAX_RETRIES, delay,
                )
                last_error = e
                time.sleep(delay)

            except APIConnectionError as e:
                delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Connection error (attempt %d/%d), retrying in %.1fs",
                    attempt, MAX_RETRIES, delay,
                )
                last_error = e
                time.sleep(delay)

            except APIStatusError as e:
                # Don't retry on auth errors (401) or bad request (400)
                if e.status_code in (401, 403):
                    masked = _mask_key(self._api_key or "")
                    raise RuntimeError(
                        f"OpenAI authentication failed (key: {masked}). "
                        "Check that your OPENAI_API_KEY is valid and has sufficient permissions."
                    ) from e
                if e.status_code == 400:
                    raise RuntimeError(
                        f"Bad request to OpenAI API: {e.message}"
                    ) from e

                # Retry on server errors (5xx)
                delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "API error %d (attempt %d/%d), retrying in %.1fs",
                    e.status_code, attempt, MAX_RETRIES, delay,
                )
                last_error = e
                time.sleep(delay)

        raise RuntimeError(
            f"OpenAI request failed after {MAX_RETRIES} attempts. Last error: {last_error}"
        )

    @property
    def masked_key(self) -> str:
        """Return the masked API key for display purposes."""
        key = self._api_key or os.environ.get("OPENAI_API_KEY", "")
        return _mask_key(key)
