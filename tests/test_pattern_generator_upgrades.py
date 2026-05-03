"""Tests for upgraded pattern_generator (codon_tile, phase_shift)."""

import numpy as np
import pytest

from src.pattern_generator import PatternGenerator


class TestCodonTilePattern:
    """Tests for codon-driven tile mapping."""

    def setup_method(self):
        self.gen = PatternGenerator(grid_size=50, community="Karen", seed=42)

    def test_codon_tile_pattern(self):
        """Test codon_tile pattern type."""
        grid = self.gen.generate_grid("ATCGATCGATCGATCG", pattern_type="codon_tile")
        assert grid.shape == (50, 50, 3)
        assert grid.dtype == np.uint8
        assert np.any(grid > 0)

    def test_codon_tile_different_sequences(self):
        """Test codon_tile with different sequences."""
        for seq in ["ATCG", "GGGG", "AAAA", "ATGCATGC"]:
            grid = self.gen.generate_grid(seq, pattern_type="codon_tile")
            assert grid.shape == (50, 50, 3)

    def test_tile_sequence_by_codon(self):
        """Test codon grouping."""
        codons = self.gen._tile_sequence_by_codon("ATCGATCG")
        assert codons == ["ATC", "GAT", "CGA"]

    def test_codon_padding(self):
        """Test codon padding for incomplete triplets."""
        codons = self.gen._tile_sequence_by_codon("AT")
        assert codons == ["ATA"]  # Padded with A

    def test_render_codon_tile(self):
        """Test single codon tile rendering."""
        tile = self.gen._render_codon_tile("ATCG", tile_size=5)
        assert tile.shape == (5, 5, 3)
        assert tile.dtype == np.uint8
        assert np.any(tile > 0)

    def test_render_codon_tile_all_patterns(self):
        """Test all pattern types from base2."""
        for base2, expected in [("A", "stripe"), ("T", "diamond"), ("G", "cross"), ("C", "dot")]:
            codon = f"A{base2}A"
            tile = self.gen._render_codon_tile(codon, tile_size=5)
            assert tile.shape == (5, 5, 3)

    def test_render_codon_tile_rotations(self):
        """Test rotation from base3."""
        for base3 in ["A", "T", "G", "C"]:
            codon = f"AAA{base3}"
            tile = self.gen._render_codon_tile(codon, tile_size=5)
            assert tile.shape == (5, 5, 3)


class TestPhaseShiftPattern:
    """Tests for phase-shifted patterns."""

    def setup_method(self):
        self.gen = PatternGenerator(grid_size=50, community="Karen", seed=42)

    def test_phase_shift_pattern(self):
        """Test phase_shift pattern type."""
        # Need a sequence with homopolymer runs
        seq = "ATCGAAAATCGGGGGATCGTTTTATCG"
        grid = self.gen.generate_grid(seq, pattern_type="phase_shift")
        assert grid.shape == (50, 50, 3)
        assert grid.dtype == np.uint8

    def test_phase_shift_no_homopolymers(self):
        """Test phase_shift with no homopolymer runs (should still work)."""
        seq = "ATCGATCGATCG"
        grid = self.gen.generate_grid(seq, pattern_type="phase_shift")
        assert grid.shape == (50, 50, 3)

    def test_detect_homopolymer_runs(self):
        """Test homopolymer run detection."""
        seq = "ATCGAAAAATCGGGGGATCG"
        runs = self.gen._detect_homopolymer_runs(seq)
        assert len(runs) >= 2
        # Check we found the AAAA and GGGGG runs
        bases = [r[0] for r in runs]
        assert "A" in bases
        assert "G" in bases

    def test_detect_homopolymer_no_runs(self):
        """Test homopolymer detection with no runs."""
        seq = "ATCGATCG"
        runs = self.gen._detect_homopolymer_runs(seq)
        assert len(runs) == 0

    def test_detect_homopolymer_minimum_length(self):
        """Test that runs < 3 are not detected."""
        seq = "ATCGAATCG"  # AA is only 2, should not be detected
        runs = self.gen._detect_homopolymer_runs(seq)
        assert len(runs) == 0

    def test_phase_shift_all_bases_transitions(self):
        """Test transition styles for all bases."""
        for base in ["A", "T", "G", "C"]:
            seq = f"ATCG{base * 5}ATCG"
            grid = self.gen.generate_grid(seq, pattern_type="phase_shift")
            assert grid.shape == (50, 50, 3)

    def test_phase_shift_empty_sequence(self):
        """Test phase_shift with empty sequence."""
        grid = self.gen.generate_grid("", pattern_type="phase_shift")
        assert grid.shape == (50, 50, 3)
