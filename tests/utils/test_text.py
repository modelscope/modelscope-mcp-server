import pytest

from modelscope_mcp_server.utils.text import truncate_for_log


def test_returns_empty_string_for_none_input():
    # None input should return empty string
    assert truncate_for_log(None) == ""


@pytest.mark.parametrize("max_chars", [0, -1])
def test_zero_or_negative_max_chars_returns_marker(max_chars: int):
    text = "abcdef"
    out = truncate_for_log(text, max_chars=max_chars)
    assert out == "[truncated display=0 total=6]"


def test_within_limit_returns_original():
    text = "hello"
    out = truncate_for_log(text, max_chars=10)
    assert out == text


def test_truncates_and_appends_marker():
    text = "x" * 100
    out = truncate_for_log(text, max_chars=10)
    assert out == "{}\n... [truncated display=10 total=100]".format("x" * 10)


def test_unicode_handling_and_marker():
    text = "你好世界" * 30  # length 120
    max_chars = 5
    out = truncate_for_log(text, max_chars=max_chars)
    assert out.startswith(text[:max_chars])
    assert out.endswith(f"... [truncated display={max_chars} total={len(text)}]")


def test_empty_string_input():
    out = truncate_for_log("")
    assert out == ""
