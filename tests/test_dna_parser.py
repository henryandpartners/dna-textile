"""Unit tests for DNA Parser module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dna_parser import DNAParser


class TestDNAParserValidation:
    """Test DNA sequence validation."""

    @pytest.fixture
    def parser(self):
        return DNAParser()

    def test_valid_sequence(self, parser):
        """Valid DNA sequence should parse."""
        result = parser.parse("ATCGATCG")
        assert result is not None
        assert len(result) == 8

    def test_lowercase_input(self, parser):
        """Lowercase should be accepted and normalized."""
        result = parser.parse("atcgatcg")
        assert result is not None
        assert len(result) == 8

    def test_mixed_case(self, parser):
        """Mixed case should be accepted."""
        result = parser.parse("AtCgAtCg")
        assert result is not None
        assert len(result) == 8

    def test_empty_sequence(self, parser):
        """Empty sequence should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            parser.parse("")

    def test_invalid_character(self, parser):
        """Invalid characters should raise ValueError."""
        with pytest.raises(ValueError):
            parser.parse("ATXCG")

    def test_whitespace_handling(self, parser):
        """Whitespace should be stripped."""
        result = parser.parse("  ATCGATCG  ")
        assert result is not None
        assert len(result) == 8

    def test_newline_handling(self, parser):
        """Newlines should be stripped."""
        result = parser.parse("ATCG\nATCG")
        assert result is not None
        assert len(result) == 8


class TestDNAParserCounts:
    """Test nucleotide counting."""

    @pytest.fixture
    def parser(self):
        return DNAParser()

    def test_count_atcg(self, parser):
        """Should count A, T, C, G correctly."""
        counts = parser.count_nucleotides("AATTCCGG")
        assert counts["A"] == 2
        assert counts["T"] == 2
        assert counts["C"] == 2
        assert counts["G"] == 2

    def test_count_single_nucleotide(self, parser):
        """Single nucleotide sequence."""
        counts = parser.count_nucleotides("AAAA")
        assert counts["A"] == 4
        assert counts["T"] == 0
        assert counts["C"] == 0
        assert counts["G"] == 0

    def test_gc_content(self, parser):
        """GC content calculation."""
        gc = parser.gc_content("ATCGATCG")
        assert gc == 0.5  # 4 GC out of 8

    def test_gc_content_100(self, parser):
        """100% GC content."""
        gc = parser.gc_content("GCGCGC")
        assert gc == 1.0

    def test_gc_content_0(self, parser):
        """0% GC content."""
        gc = parser.gc_content("ATATAT")
        assert gc == 0.0


class TestDNAParserPatterns:
    """Test pattern detection in DNA sequences."""

    @pytest.fixture
    def parser(self):
        return DNAParser()

    def test_repeat_detection(self, parser):
        """Should detect repeating patterns."""
        repeats = parser.find_repeats("ATCGATCGATCG")
        assert len(repeats) > 0

    def test_no_repeats(self, parser):
        """Sequence with no repeats."""
        repeats = parser.find_repeats("ATCG")
        # Short sequence, may or may not have repeats
        assert isinstance(repeats, list)

    def test_codon_extraction(self, parser):
        """Should extract codons (triplets)."""
        codons = parser.extract_codons("ATCGATCGAT")
        assert len(codons) == 3  # ATC, GAT, CGA (last T incomplete)
        assert codons[0] == "ATC"
        assert codons[1] == "GAT"

    def test_codon_extraction_exact_multiple(self, parser):
        """Codon extraction with exact multiple of 3."""
        codons = parser.extract_codons("ATCGAT")
        assert len(codons) == 2
        assert codons == ["ATC", "GAT"]
