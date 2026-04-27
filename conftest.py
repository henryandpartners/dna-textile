"""Shared pytest fixtures for DNA Textile tests."""

import json
import sys
from pathlib import Path

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Sample DNA sequences for testing
SAMPLE_DNA_SHORT = "ATCGATCGATCGATCGATCG"
SAMPLE_DNA_MEDIUM = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
SAMPLE_DNA_LONG = "ATCG" * 100  # 400 bp


@pytest.fixture
def sample_dna_short():
    """Short DNA sequence (20 bp)."""
    return SAMPLE_DNA_SHORT


@pytest.fixture
def sample_dna_medium():
    """Medium DNA sequence (40 bp)."""
    return SAMPLE_DNA_MEDIUM


@pytest.fixture
def sample_dna_long():
    """Long DNA sequence (400 bp)."""
    return SAMPLE_DNA_LONG


@pytest.fixture
def all_community_names():
    """List of all 15+ community names."""
    return [
        "Karen", "Hmong", "Lisu", "Akha", "Lahu",
        "Mlabri", "Mien", "Kuy", "Khmer", "Mon",
        "Phu Thai", "Isan", "Lanna", "Southern", "Tai Dam",
    ]


@pytest.fixture
def sample_colors():
    """Sample color palette for testing."""
    return [
        (139, 69, 19),    # Brown
        (34, 139, 34),    # Green
        (255, 215, 0),    # Gold
        (128, 0, 128),    # Purple
        (220, 20, 60),    # Crimson
    ]


@pytest.fixture
def sample_pattern():
    """Sample pattern grid for testing."""
    return [
        [0, 1, 2, 1, 0],
        [1, 3, 4, 3, 1],
        [2, 4, 0, 4, 2],
        [1, 3, 4, 3, 1],
        [0, 1, 2, 1, 0],
    ]


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Temporary output directory for export tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
