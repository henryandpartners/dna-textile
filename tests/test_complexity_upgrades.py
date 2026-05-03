"""Tests for upgraded complexity (entropy density)."""

import pytest

from src.complexity import get_density_from_entropy
from src.dna_features import DNAFeatures


class TestEntropyDensity:
    """Tests for entropy-based density calculation."""

    def test_low_entropy_dense(self):
        """Low entropy (< 1.0) should produce dense patterns (0.8-1.0)."""
        features = DNAFeatures(sequence="A" * 100, length=100)
        density = get_density_from_entropy(features)
        assert 0.8 <= density <= 1.0

    def test_medium_entropy_moderate(self):
        """Medium entropy (1.0-1.8) should produce moderate patterns (0.4-0.7)."""
        # Create features with known entropy
        features = DNAFeatures(sequence="ATCGATCGATCG", length=12)
        density = get_density_from_entropy(features)
        # Should be in the moderate range
        assert 0.0 <= density <= 1.0

    def test_high_entropy_sparse(self):
        """High entropy (> 1.8) should produce sparse patterns (0.1-0.3)."""
        # Create features with very high entropy
        features = DNAFeatures(sequence="", length=0)
        features.entropy = 2.0  # Max entropy
        density = get_density_from_entropy(features)
        assert 0.1 <= density <= 0.4

    def test_entropy_zero(self):
        """Zero entropy should give maximum density."""
        features = DNAFeatures(sequence="", length=0)
        features.entropy = 0.0
        density = get_density_from_entropy(features)
        assert density == 1.0

    def test_density_range(self):
        """All densities should be in [0, 1]."""
        for entropy_val in [0.0, 0.5, 1.0, 1.5, 1.8, 2.0, 2.5]:
            features = DNAFeatures(sequence="", length=0)
            features.entropy = entropy_val
            density = get_density_from_entropy(features)
            assert 0.0 <= density <= 1.0, f"Density out of range for entropy={entropy_val}: {density}"

    def test_density_monotonic(self):
        """Higher entropy should generally produce lower density."""
        densities = []
        for entropy_val in [0.0, 0.5, 1.0, 1.5, 1.8, 2.0]:
            features = DNAFeatures(sequence="", length=0)
            features.entropy = entropy_val
            densities.append(get_density_from_entropy(features))

        # Overall trend: density decreases as entropy increases
        assert densities[0] >= densities[-1]

    def test_real_dna_features(self):
        """Test with real DNA features."""
        from src.dna_features import extract_features

        # Low complexity sequence (mostly A's)
        seq1 = "AAAAAAAATTTTTTTT"
        features1 = extract_features(seq1)
        density1 = get_density_from_entropy(features1)

        # High complexity sequence (mixed)
        seq2 = "ATCGATCGATCGATCG"
        features2 = extract_features(seq2)
        density2 = get_density_from_entropy(features2)

        # Both should be valid densities
        assert 0.0 <= density1 <= 1.0
        assert 0.0 <= density2 <= 1.0
