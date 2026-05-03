"""Unit tests for Pattern Warper module."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pattern_warp import PatternWarper


class TestPatternWarper:
    """Test pattern warping functionality."""

    @pytest.fixture
    def warper(self):
        return PatternWarper()

    @pytest.fixture
    def sample_grid(self):
        """Generate a sample pattern grid."""
        return np.random.randint(0, 256, (30, 30, 3), dtype=np.uint8)

    def test_flat_warp(self, warper, sample_grid):
        """Flat warp should resize to target shape."""
        result = warper.warp_to_region(sample_grid, region_shape=(60, 60), warp_type="flat")
        assert result.shape == (60, 60, 3)
        assert result.dtype == np.uint8

    def test_cylindrical_warp(self, warper, sample_grid):
        """Cylindrical warp should produce valid output."""
        result = warper.warp_to_region(
            sample_grid, region_shape=(40, 40), warp_type="cylindrical"
        )
        assert result.shape == (40, 40, 3)

    def test_conical_warp(self, warper, sample_grid):
        """Conical warp should produce valid output."""
        result = warper.warp_to_region(
            sample_grid, region_shape=(50, 50), warp_type="conical"
        )
        assert result.shape == (50, 50, 3)

    def test_drape_warp(self, warper, sample_grid):
        """Drape warp should produce valid output."""
        result = warper.warp_to_region(
            sample_grid, region_shape=(40, 40), warp_type="drape"
        )
        assert result.shape == (40, 40, 3)

    def test_warp_preserves_channels(self, warper, sample_grid):
        """Warp should preserve 3 color channels."""
        for warp_type in ["flat", "cylindrical", "conical", "drape"]:
            result = warper.warp_to_region(sample_grid, region_shape=(25, 25), warp_type=warp_type)
            assert result.shape[2] == 3

    def test_warp_different_sizes(self, warper, sample_grid):
        """Should handle different target sizes."""
        for size in [(10, 10), (50, 30), (100, 100)]:
            result = warper.warp_to_region(sample_grid, region_shape=size, warp_type="flat")
            assert result.shape[:2] == size

    def test_cylindrical_curvature(self, warper, sample_grid):
        """Different curvature values should produce different results."""
        r1 = warper.apply_cylindrical_warp(sample_grid, curvature=0.0)
        r2 = warper.apply_cylindrical_warp(sample_grid, curvature=1.0)
        # Results should differ
        assert not np.array_equal(r1, r2)

    def test_conical_angle(self, warper, sample_grid):
        """Different angles should produce different results."""
        r1 = warper.apply_conical_warp(sample_grid, angle=0)
        r2 = warper.apply_conical_warp(sample_grid, angle=90)
        assert not np.array_equal(r1, r2)

    def test_drape_directions(self, warper, sample_grid):
        """Different gravity directions should work."""
        for direction in ["down", "up", "left", "right"]:
            result = warper.apply_drape_warp(sample_grid, gravity_direction=direction)
            assert result is not None
            assert result.ndim == 3

    def test_invalid_warp_type(self, warper, sample_grid):
        """Invalid warp type should raise ValueError."""
        with pytest.raises(ValueError):
            warper.warp_to_region(sample_grid, region_shape=(30, 30), warp_type="invalid")
