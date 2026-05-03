"""Unit tests for Fractal Patterns module."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fractal_patterns import FractalPatternGenerator
from src.dna_features import DNAFeatures


class TestFractalPatternGenerator:
    """Test fractal pattern generation."""

    @pytest.fixture
    def generator(self):
        return FractalPatternGenerator()

    @pytest.fixture
    def features(self):
        return DNAFeatures(sequence="ATCGATCGATCGATCGATCG", length=20)

    def test_generate_fractal_motif(self, generator, features):
        """Should generate a fractal motif."""
        motif = generator.generate_fractal_motif(features, depth=1, size=50)
        assert motif is not None
        assert motif.shape == (50, 50, 3)
        assert motif.dtype == np.uint8

    def test_generate_fractal_motif_auto(self, generator, features):
        """Should auto-select motif type from DNA."""
        motif = generator.generate_fractal_motif(features, motif_type="auto", depth=1)
        assert motif is not None
        assert motif.shape[2] == 3

    def test_generate_fractal_motif_depth_zero(self, generator, features):
        """Depth 0 should produce a base motif."""
        motif = generator.generate_fractal_motif(features, depth=0, size=30)
        assert motif is not None
        assert motif.shape == (30, 30, 3)

    def test_generate_fractal_grid(self, generator, features):
        """Should generate a grid of fractal motifs."""
        grid = generator.generate_fractal_grid(features, grid_rows=2, grid_cols=2, tile_size=30)
        assert grid is not None
        assert grid.shape == (60, 60, 3)

    def test_generate_fractal_grid_different_sizes(self, generator, features):
        """Should handle different grid sizes."""
        grid = generator.generate_fractal_grid(features, grid_rows=3, grid_cols=4, tile_size=20)
        assert grid.shape == (60, 80, 3)

    def test_motif_types(self, generator, features):
        """Should support different motif types."""
        for motif_type in ["diamond", "triangle", "cross", "circle", "square"]:
            motif = generator.generate_fractal_motif(features, motif_type=motif_type, size=20)
            assert motif is not None
            assert motif.shape == (20, 20, 3)

    def test_deterministic_with_seed(self):
        """Same seed should produce same output."""
        features = DNAFeatures(sequence="ATCGATCG", length=8)
        gen1 = FractalPatternGenerator(seed=42)
        gen2 = FractalPatternGenerator(seed=42)
        m1 = gen1.generate_fractal_motif(features, size=20)
        m2 = gen2.generate_fractal_motif(features, size=20)
        assert np.array_equal(m1, m2)
