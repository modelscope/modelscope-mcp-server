"""
Tests for demo.py script functionality.
"""

import sys

import pytest

from demo import main


class TestDemo:
    """Test demo script main function."""

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_main_execution(self, mocker):
        """Test that main function can execute without errors in real environment."""
        mocker.patch.object(sys, "argv", ["demo.py", "--full"])
        await main()
        print("✅ Demo executed successfully!")
