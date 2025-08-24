"""Utility helpers for working with text strings."""

from __future__ import annotations


def truncate_for_log(text: str | None, max_chars: int = 2000) -> str:
    """Truncate a string for log readability.

    If the input exceeds max_chars, returns the prefix plus a trailing marker
    indicating truncation with the display and total lengths.

    Args:
        text: The input string to truncate.
        max_chars: Maximum number of characters to display.

    Returns:
        The original text if within limit; otherwise a truncated string followed
        by a newline and an annotation showing the display and total lengths.

    """
    if text is None:
        return ""

    if max_chars <= 0:
        total_len = len(text)
        return f"[truncated display=0 total={total_len}]"

    total_len = len(text)
    if total_len <= max_chars:
        return text

    displayed = text[:max_chars]
    return f"{displayed}\n... [truncated display={max_chars} total={total_len}]"
