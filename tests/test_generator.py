"""Tests for DNA Textile Pattern Generator."""

import sys
from pathlib import Path

import numpy as np

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dna_parser import parse_string, parse_fasta, DNASparseError
from src.pattern_generator import PatternGenerator, DEFAULT_COLOR_MAP
from src.cultural_rules import apply_cultural_rules, get_community_rules
from src.mixer import mix_patterns, mix_sequences
from src.exporters import export_png, export_jac, export_txt


def test_parse_string():
    seq = parse_string("ATGCATGC")
    assert seq == "ATGCATGC"
    print("✓ parse_string")


def test_parse_string_invalid():
    try:
        parse_string("ATXGC")
        assert False, "Should have raised"
    except DNASparseError:
        pass
    print("✓ parse_string invalid chars")


def test_pattern_grid():
    gen = PatternGenerator(grid_size=10)
    grid = gen.generate_grid("ATGCATGCATGC", pattern_type="grid")
    assert grid.shape == (10, 10, 3)
    assert grid.dtype == np.uint8
    # Check a known cell
    assert tuple(grid[0, 0]) == DEFAULT_COLOR_MAP["A"]
    print("✓ pattern_grid")


def test_pattern_stripe():
    gen = PatternGenerator(grid_size=10)
    grid = gen.generate_grid("ATGC", pattern_type="stripe")
    assert grid.shape == (10, 10, 3)
    # Each row should be uniform
    for r in range(10):
        assert np.all(grid[r, 0] == grid[r, 5])
    print("✓ pattern_stripe")


def test_pattern_spiral():
    gen = PatternGenerator(grid_size=10)
    grid = gen.generate_grid("ATGCATGCATGC", pattern_type="spiral")
    assert grid.shape == (10, 10, 3)
    print("✓ pattern_spiral")


def test_pattern_random():
    gen = PatternGenerator(grid_size=10)
    grid1 = gen.generate_grid("ATGCATGCATGC", pattern_type="random", seed=42)
    grid2 = gen.generate_grid("ATGCATGCATGC", pattern_type="random", seed=42)
    assert np.array_equal(grid1, grid2)  # deterministic with seed
    print("✓ pattern_random (deterministic)")


def test_cultural_rules():
    gen = PatternGenerator(grid_size=20)
    grid = gen.generate_grid("ATGC" * 25, pattern_type="grid")
    rule = get_community_rules("karen")
    result = apply_cultural_rules(grid.copy(), rule=rule)
    # Top border should be brown
    assert tuple(result[0, 5]) == (139, 69, 19)
    print("✓ cultural_rules (karen border)")


def test_mix_patterns():
    seq1 = "ATGCATGCATGC"
    seq2 = "GCTAGCTAGCTA"
    blended = mix_patterns([seq1, seq2], weights=[0.5, 0.5], grid_size=10)
    assert blended.shape == (10, 10, 3)
    assert blended.dtype == np.uint8
    print("✓ mix_patterns")


def test_mix_sequences():
    seq1 = "ATGCATGC"
    seq2 = "GCTAGCTA"
    blended = mix_sequences([seq1, seq2], weights=[0.5, 0.5])
    assert len(blended) == 8
    print("✓ mix_sequences")


def test_export_png(tmp_path=None):
    """Test PNG export (writes to /tmp if no tmp_path)."""
    gen = PatternGenerator(grid_size=16)
    grid = gen.generate_grid("ATGC" * 64, pattern_type="grid")

    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.gettempdir())

    out = tmp_path / "test_pattern.png"
    result = export_png(grid, out)
    assert result.exists()
    print(f"✓ export_png → {result}")


def test_export_jac(tmp_path=None):
    gen = PatternGenerator(grid_size=8)
    grid = gen.generate_grid("ATGCATGCATGC", pattern_type="grid")

    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.gettempdir())

    out = tmp_path / "test_pattern.jac"
    result = export_jac(grid, out)
    assert result.exists()
    print(f"✓ export_jac → {result}")


def test_export_txt(tmp_path=None):
    gen = PatternGenerator(grid_size=8)
    grid = gen.generate_grid("ATGCATGCATGC", pattern_type="grid")

    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.gettempdir())

    out = tmp_path / "test_pattern.txt"
    result = export_txt(grid, out)
    assert result.exists()
    print(f"✓ export_txt → {result}")


def run_all():
    print("Running tests...\n")
    test_parse_string()
    test_parse_string_invalid()
    test_pattern_grid()
    test_pattern_stripe()
    test_pattern_spiral()
    test_pattern_random()
    test_cultural_rules()
    test_mix_patterns()
    test_mix_sequences()
    test_export_png()
    test_export_jac()
    test_export_txt()
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all()
