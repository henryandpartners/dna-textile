"""Unit tests for Costume Mapper module."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.costume_mapper import CostumeMapper
from src.dna_features import DNAFeatures


class TestCostumeMapper:
    """Test costume mapping functionality."""

    @pytest.fixture
    def mapper(self):
        return CostumeMapper("Karen")

    @pytest.fixture
    def pattern_grid(self):
        """Generate a sample pattern grid."""
        return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    @pytest.fixture
    def features(self):
        return DNAFeatures(sequence="ATCGATCGATCGATCG", length=16)

    def test_map_pattern_to_garment(self, mapper, pattern_grid):
        """Should map pattern to garment regions."""
        result = mapper.map_pattern_to_garment(pattern_grid)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_map_returns_region_patterns(self, mapper, pattern_grid):
        """Each region should have a pattern grid."""
        result = mapper.map_pattern_to_garment(pattern_grid)
        for name, grid in result.items():
            assert isinstance(grid, np.ndarray)
            assert grid.ndim == 3
            assert grid.shape[2] == 3

    def test_generate_costume_output(self, mapper, pattern_grid, features):
        """Should generate full costume output."""
        output = mapper.generate_costume_output(pattern_grid, features)
        assert isinstance(output, dict)
        assert len(output) > 0

    def test_generate_costume_preview(self, mapper, pattern_grid, features):
        """Should generate a composite preview."""
        preview = mapper.generate_costume_preview(pattern_grid, features)
        assert isinstance(preview, np.ndarray)
        assert preview.ndim == 3
        assert preview.shape[2] == 3

    def test_list_available_garments(self, mapper):
        """Should list available garment names."""
        garments = mapper.list_available_garments()
        assert isinstance(garments, list)
        assert len(garments) > 0

    def test_different_communities(self):
        """Should work with different communities."""
        for community in ["Karen", "Hmong", "Lisu"]:
            mapper = CostumeMapper(community)
            grid = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
            result = mapper.map_pattern_to_garment(grid)
            assert len(result) > 0

    def test_specific_garment(self, mapper, pattern_grid):
        """Should map to a specific garment by name."""
        result = mapper.map_pattern_to_garment(pattern_grid, garment_name="longyi")
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_region_pattern(self, mapper, pattern_grid):
        """Should extract a pattern for a specific region."""
        templates = mapper._templates
        if templates:
            region = templates[0].regions[0]
            region_pattern = mapper.get_region_pattern(pattern_grid, region)
            assert isinstance(region_pattern, np.ndarray)
            assert region_pattern.ndim == 3
