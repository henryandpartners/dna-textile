"""Unit tests for Motif Library module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.motif_library import MotifLibrary


class TestMotifLibrary:
    """Test motif library management."""

    @pytest.fixture
    def library(self):
        return MotifLibrary()

    def test_load_motifs(self, library):
        """Should load motif library."""
        assert library is not None

    def test_get_motifs(self, library):
        """Should return motifs."""
        motifs = library.get_motifs()
        assert motifs is not None
        assert len(motifs) > 0

    def test_get_karen_motifs(self, library):
        """Should return Karen motifs."""
        motifs = library.get_motifs("Karen")
        assert motifs is not None

    def test_get_hmong_motifs(self, library):
        """Should return Hmong motifs."""
        motifs = library.get_motifs("Hmong")
        assert motifs is not None

    def test_get_lanna_motifs(self, library):
        """Should return Lanna motifs."""
        motifs = library.get_motifs("Lanna")
        assert motifs is not None

    def test_add_motif(self, library):
        """Should add motif to library."""
        motif = {"name": "test", "pattern": [[0, 1], [1, 0]]}
        library.add_motif(motif)
        motifs = library.get_motifs()
        assert any(m.get("name") == "test" for m in motifs)

    def test_search_motifs(self, library):
        """Should search motifs by keyword."""
        results = library.search("geometric")
        assert isinstance(results, list)

    def test_motif_structure(self, library):
        """Motifs should have expected structure."""
        motifs = library.get_motifs()
        for motif in motifs[:5]:  # Check first 5
            assert "name" in motif or "pattern" in motif
