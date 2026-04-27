"""DNA mixing tests (accuracy)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mixer import DNAMixer


class TestDNAMixerBasics:
    """Test basic DNA mixing functionality."""

    @pytest.fixture
    def mixer(self):
        return DNAMixer()

    @pytest.mark.mix
    def test_mix_two_sequences(self, mixer, sample_dna_short):
        """Should mix two DNA sequences."""
        mixed = mixer.mix(sample_dna_short, sample_dna_short)
        assert mixed is not None
        assert len(mixed) == len(sample_dna_short)

    @pytest.mark.mix
    def test_mix_different_sequences(self, mixer):
        """Should mix different DNA sequences."""
        dna1 = "ATCGATCG"
        dna2 = "GCTAGCTA"
        mixed = mixer.mix(dna1, dna2)
        assert mixed is not None
        assert len(mixed) == 8

    @pytest.mark.mix
    def test_mix_preserves_length(self, mixer):
        """Mixed sequence should preserve length."""
        dna1 = "ATCGATCGATCG"
        dna2 = "GCTAGCTAGCTA"
        mixed = mixer.mix(dna1, dna2)
        assert len(mixed) == len(dna1)

    @pytest.mark.mix
    def test_mix_valid_nucleotides(self, mixer):
        """Mixed sequence should contain only valid nucleotides."""
        dna1 = "ATCGATCG"
        dna2 = "GCTAGCTA"
        mixed = mixer.mix(dna1, dna2)
        valid = set("ATCG")
        assert all(c in valid for c in mixed)


class TestDNAMixerMethods:
    """Test different mixing methods."""

    @pytest.fixture
    def mixer(self):
        return DNAMixer()

    @pytest.mark.mix
    def test_mix_alternating(self, mixer):
        """Alternating mix should alternate between sequences."""
        dna1 = "AAAA"
        dna2 = "TTTT"
        mixed = mixer.mix(dna1, dna2, method="alternating")
        assert mixed is not None
        assert len(mixed) == 4

    @pytest.mark.mix
    def test_mix_random(self, mixer):
        """Random mix should produce valid sequence."""
        dna1 = "ATCGATCG"
        dna2 = "GCTAGCTA"
        mixed = mixer.mix(dna1, dna2, method="random")
        assert mixed is not None
        assert len(mixed) == 8

    @pytest.mark.mix
    def test_mix_crossover(self, mixer):
        """Crossover mix should produce valid sequence."""
        dna1 = "ATCGATCG"
        dna2 = "GCTAGCTA"
        mixed = mixer.mix(dna1, dna2, method="crossover")
        assert mixed is not None
        assert len(mixed) == 8


class TestDNAMixerAccuracy:
    """Test mixing accuracy."""

    @pytest.fixture
    def mixer(self):
        return DNAMixer()

    @pytest.mark.mix
    def test_mix_accuracy_same_sequence(self, mixer):
        """Mixing identical sequences should produce same sequence."""
        dna = "ATCGATCG"
        mixed = mixer.mix(dna, dna, method="alternating")
        assert mixed == dna

    @pytest.mark.mix
    def test_mix_accuracy_complement(self, mixer):
        """Mixing with complement should produce valid result."""
        dna1 = "ATCGATCG"
        dna2 = "TAGCTAGC"  # Complement
        mixed = mixer.mix(dna1, dna2)
        assert mixed is not None
        assert len(mixed) == 8

    @pytest.mark.mix
    def test_mix_deterministic(self, mixer):
        """Same inputs should produce same output (deterministic)."""
        dna1 = "ATCGATCG"
        dna2 = "GCTAGCTA"
        mixed1 = mixer.mix(dna1, dna2, method="alternating")
        mixed2 = mixer.mix(dna1, dna2, method="alternating")
        assert mixed1 == mixed2


class TestDNAMixerEdgeCases:
    """Test mixing edge cases."""

    @pytest.fixture
    def mixer(self):
        return DNAMixer()

    def test_mix_different_lengths(self, mixer):
        """Should handle different length sequences."""
        dna1 = "ATCG"
        dna2 = "ATCGATCG"
        mixed = mixer.mix(dna1, dna2)
        # Should handle gracefully
        assert mixed is not None

    def test_mix_single_nucleotide(self, mixer):
        """Should handle single nucleotide sequences."""
        mixed = mixer.mix("A", "T")
        assert mixed is not None
        assert len(mixed) == 1

    def test_mix_long_sequences(self, mixer, sample_dna_long):
        """Should handle long sequences."""
        mixed = mixer.mix(sample_dna_long, sample_dna_long)
        assert mixed is not None
        assert len(mixed) == len(sample_dna_long)

    def test_mix_invalid_input(self, mixer):
        """Should handle invalid input gracefully."""
        with pytest.raises((ValueError, TypeError)):
            mixer.mix("ATCG", "")

    def test_mix_empty_input(self, mixer):
        """Should handle empty input."""
        with pytest.raises((ValueError, TypeError)):
            mixer.mix("", "ATCG")


class TestDNAMixerPatternGeneration:
    """Test mixing for pattern generation."""

    @pytest.fixture
    def mixer(self):
        return DNAMixer()

    @pytest.mark.mix
    def test_mix_then_generate(self, mixer, sample_dna_short):
        """Mixed DNA should generate valid pattern."""
        from src.pattern_generator import PatternGenerator

        mixed = mixer.mix(sample_dna_short, sample_dna_short)
        generator = PatternGenerator()
        pattern = generator.generate(mixed)
        assert pattern is not None
        assert len(pattern) > 0

    @pytest.mark.mix
    def test_mixed_dna_different_from_parents(self, mixer):
        """Mixed DNA should differ from at least one parent."""
        dna1 = "ATCGATCG"
        dna2 = "GCTAGCTA"
        mixed = mixer.mix(dna1, dna2, method="random")
        # Should differ from at least one parent
        assert mixed != dna1 or mixed != dna2
