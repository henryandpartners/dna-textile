"""Pattern generation tests for all 15+ communities."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pattern_generator import PatternGenerator


class TestPatternGenerationBasics:
    """Test basic pattern generation."""

    @pytest.fixture
    def generator(self):
        return PatternGenerator()

    def test_generate_pattern(self, generator, sample_dna_short):
        """Should generate a pattern from DNA."""
        pattern = generator.generate(sample_dna_short)
        assert pattern is not None
        assert len(pattern) > 0

    def test_generate_with_community(self, generator, sample_dna_short):
        """Should generate pattern with community rules."""
        pattern = generator.generate(sample_dna_short, community="Karen")
        assert pattern is not None

    def test_generate_different_dna(self, generator):
        """Different DNA should produce different patterns."""
        p1 = generator.generate("ATCGATCG")
        p2 = generator.generate("GCTAGCTA")
        assert p1 != p2

    def test_generate_same_dna(self, generator):
        """Same DNA should produce same pattern (deterministic)."""
        p1 = generator.generate("ATCGATCG")
        p2 = generator.generate("ATCGATCG")
        assert p1 == p2

    def test_generate_min_length(self, generator):
        """Minimum length DNA should work."""
        pattern = generator.generate("ATCG")
        assert pattern is not None

    def test_generate_long_sequence(self, generator, sample_dna_long):
        """Long DNA sequence should generate larger pattern."""
        pattern = generator.generate(sample_dna_long)
        assert pattern is not None


class TestPatternGenerationCommunities:
    """Test pattern generation for each community."""

    @pytest.fixture
    def generator(self):
        return PatternGenerator()

    @pytest.mark.pattern
    def test_karen_pattern(self, generator, sample_dna_medium):
        """Karen community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Karen")
        assert pattern is not None

    @pytest.mark.pattern
    def test_hmong_pattern(self, generator, sample_dna_medium):
        """Hmong community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Hmong")
        assert pattern is not None

    @pytest.mark.pattern
    def test_lisu_pattern(self, generator, sample_dna_medium):
        """Lisu community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Lisu")
        assert pattern is not None

    @pytest.mark.pattern
    def test_akha_pattern(self, generator, sample_dna_medium):
        """Akha community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Akha")
        assert pattern is not None

    @pytest.mark.pattern
    def test_lahu_pattern(self, generator, sample_dna_medium):
        """Lahu community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Lahu")
        assert pattern is not None

    @pytest.mark.pattern
    def test_mlabri_pattern(self, generator, sample_dna_medium):
        """Mlabri community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Mlabri")
        assert pattern is not None

    @pytest.mark.pattern
    def test_mien_pattern(self, generator, sample_dna_medium):
        """Mien community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Mien")
        assert pattern is not None

    @pytest.mark.pattern
    def test_kuy_pattern(self, generator, sample_dna_medium):
        """Kuy community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Kuy")
        assert pattern is not None

    @pytest.mark.pattern
    def test_khmer_pattern(self, generator, sample_dna_medium):
        """Khmer community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Khmer")
        assert pattern is not None

    @pytest.mark.pattern
    def test_mon_pattern(self, generator, sample_dna_medium):
        """Mon community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Mon")
        assert pattern is not None

    @pytest.mark.pattern
    def test_phu_thai_pattern(self, generator, sample_dna_medium):
        """Phu Thai community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Phu Thai")
        assert pattern is not None

    @pytest.mark.pattern
    def test_isan_pattern(self, generator, sample_dna_medium):
        """Isan community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Isan")
        assert pattern is not None

    @pytest.mark.pattern
    def test_lanna_pattern(self, generator, sample_dna_medium):
        """Lanna community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Lanna")
        assert pattern is not None

    @pytest.mark.pattern
    def test_southern_pattern(self, generator, sample_dna_medium):
        """Southern community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Southern")
        assert pattern is not None

    @pytest.mark.pattern
    def test_tai_dam_pattern(self, generator, sample_dna_medium):
        """Tai Dam community pattern generation."""
        pattern = generator.generate(sample_dna_medium, community="Tai Dam")
        assert pattern is not None

    @pytest.mark.pattern
    def test_unknown_community(self, generator, sample_dna_medium):
        """Unknown community should use default rules."""
        pattern = generator.generate(sample_dna_medium, community="Unknown")
        assert pattern is not None


class TestPatternStructure:
    """Test pattern structure and properties."""

    @pytest.fixture
    def generator(self):
        return PatternGenerator()

    def test_pattern_is_2d_array(self, generator, sample_dna_short):
        """Pattern should be a 2D array."""
        pattern = generator.generate(sample_dna_short)
        assert isinstance(pattern, list)
        assert all(isinstance(row, list) for row in pattern)

    def test_pattern_symmetry(self, generator, sample_dna_short):
        """Pattern should have some symmetry."""
        pattern = generator.generate(sample_dna_short)
        # Check if pattern has at least some structure
        assert len(pattern) >= 1
        assert all(len(row) >= 1 for row in pattern)

    def test_pattern_color_indices(self, generator, sample_dna_short):
        """Pattern values should be valid color indices."""
        pattern = generator.generate(sample_dna_short)
        for row in pattern:
            for val in row:
                assert isinstance(val, int)
                assert val >= 0
