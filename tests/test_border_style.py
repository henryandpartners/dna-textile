"""Unit tests for Border Style module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.border_style import BorderStyle


class TestBorderStyle:
    """Test border style management."""

    @pytest.fixture
    def border(self):
        return BorderStyle()

    def test_get_border_styles(self, border):
        """Should return border styles."""
        styles = border.get_styles()
        assert styles is not None
        assert len(styles) > 0

    def test_get_default_border(self, border):
        """Should return default border style."""
        style = border.get_style("default")
        assert style is not None

    def test_get_karen_border(self, border):
        """Should return Karen border style."""
        style = border.get_style("Karen")
        assert style is not None

    def test_get_hmong_border(self, border):
        """Should return Hmong border style."""
        style = border.get_style("Hmong")
        assert style is not None

    def test_apply_border(self, border, sample_pattern):
        """Should apply border to pattern."""
        bordered = border.apply(sample_pattern, "default")
        assert bordered is not None
        assert len(bordered) >= len(sample_pattern)

    def test_border_preserves_pattern(self, border, sample_pattern):
        """Border should not modify original pattern."""
        original = [row[:] for row in sample_pattern]
        border.apply(sample_pattern, "default")
        assert sample_pattern == original
