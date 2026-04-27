"""Unit tests for Color Palette module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.color_palette import ColorPalette


class TestColorPaletteLoading:
    """Test color palette loading."""

    @pytest.fixture
    def palette(self):
        return ColorPalette()

    def test_load_palette(self, palette):
        """Should load color palette."""
        assert palette is not None

    def test_get_colors(self, palette):
        """Should return colors."""
        colors = palette.get_colors("default")
        assert colors is not None
        assert len(colors) > 0

    def test_get_karen_colors(self, palette):
        """Should return Karen-specific colors."""
        colors = palette.get_colors("Karen")
        assert colors is not None

    def test_get_hmong_colors(self, palette):
        """Should return Hmong-specific colors."""
        colors = palette.get_colors("Hmong")
        assert colors is not None

    def test_get_lanna_colors(self, palette):
        """Should return Lanna-specific colors."""
        colors = palette.get_colors("Lanna")
        assert colors is not None


class TestColorPaletteOperations:
    """Test color palette operations."""

    @pytest.fixture
    def palette(self):
        return ColorPalette()

    def test_color_is_tuple(self, palette):
        """Colors should be tuples."""
        colors = palette.get_colors("default")
        for color in colors:
            assert isinstance(color, tuple)
            assert len(color) == 3  # RGB

    def test_color_values_valid(self, palette):
        """Color values should be 0-255."""
        colors = palette.get_colors("default")
        for r, g, b in colors:
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255

    def test_get_all_palettes(self, palette):
        """Should return all available palettes."""
        palettes = palette.get_all_palettes()
        assert len(palettes) > 0

    def test_community_palette_exists(self, palette, all_community_names):
        """Each community should have a palette."""
        for community in all_community_names:
            colors = palette.get_colors(community)
            assert colors is not None
            assert len(colors) > 0


class TestColorPaletteCustom:
    """Test custom color palette creation."""

    @pytest.fixture
    def palette(self):
        return ColorPalette()

    def test_custom_colors(self, palette):
        """Should create custom palette."""
        custom = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        palette.set_custom_palette("custom", custom)
        colors = palette.get_colors("custom")
        assert colors == custom

    def test_add_color(self, palette):
        """Should add color to palette."""
        initial = len(palette.get_colors("default"))
        palette.add_color("default", (128, 128, 128))
        assert len(palette.get_colors("default")) == initial + 1
