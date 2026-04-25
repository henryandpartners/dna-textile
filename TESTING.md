# DNA Textile - Testing Guide

## Overview

Comprehensive test suite for the DNA Textile pattern generation system covering unit, pattern generation, cultural validation, export, and mixing tests.

## Test Structure

```
tests/
├── test_dna_parser.py          # DNA parsing unit tests
├── test_pattern_generator.py   # Pattern generation (all 15 communities)
├── test_cultural_rules.py      # Cultural rule validation
├── test_exporters.py           # Export format tests (PNG, JAC, TXT)
├── test_mixer.py               # DNA mixing accuracy tests
├── test_color_palette.py       # Color palette unit tests
├── test_complexity.py          # Complexity management tests
├── test_border_style.py        # Border style tests
├── test_motif_library.py       # Motif library tests
├── test_sensitivity_checker.py # Cultural sensitivity tests
├── test_generator.py           # Existing generator tests
└── test_cultural_rules.py      # Existing cultural rule tests
```

## Test Categories

| Category | Markers | Files | Purpose |
|----------|---------|-------|---------|
| Unit | `unit` | test_dna_parser, test_color_palette, test_complexity, test_border_style, test_motif_library, test_sensitivity_checker | Individual module testing |
| Pattern | `pattern` | test_pattern_generator | All 15 community patterns |
| Cultural | `cultural` | test_cultural_rules | Cultural rule validation |
| Export | `export` | test_exporters | PNG, JAC, TXT export |
| Mix | `mix` | test_mixer | DNA mixing accuracy |

## Running Tests

### All tests
```bash
cd dna-textile
pytest
```

### Specific category
```bash
pytest -m unit          # Unit tests only
pytest -m pattern       # Pattern generation tests
pytest -m cultural      # Cultural rule tests
pytest -m export        # Export format tests
pytest -m mix           # DNA mixing tests
```

### With coverage
```bash
pytest --cov=src --cov-report=html
```

### Parallel execution
```bash
pytest -n auto          # Use all CPU cores
```

### Benchmark mode
```bash
pytest --benchmark-only --benchmark-json=benchmark.json
```

## Test Configuration

- **pytest.ini**: Main configuration (coverage thresholds, markers)
- **conftest.py**: Shared fixtures (DNA sequences, colors, patterns, communities)
- **Coverage target**: 90%+

## CI/CD

GitHub Actions workflow runs on:
- Push to main/develop
- Pull requests to main/develop

Pipeline:
1. Install dependencies
2. Run unit tests
3. Run pattern generation tests
4. Run cultural rule tests
5. Run export format tests
6. Run DNA mixing tests
7. Generate coverage report
8. Upload to Codecov

## Fixtures

Available in `conftest.py`:
- `sample_dna_short`: 20bp DNA sequence
- `sample_dna_medium`: 40bp DNA sequence
- `sample_dna_long`: 400bp DNA sequence
- `all_community_names`: All 15+ community names
- `sample_colors`: Color palette for testing
- `sample_pattern`: 5x5 pattern grid
- `tmp_output_dir`: Temporary output directory

## Community Coverage

All 15 communities tested:
- Karen, Hmong, Lisu, Akha, Lahu
- Mlabri, Mien, Kuy, Khmer, Mon
- Phu Thai, Isan, Lanna, Southern, Tai Dam

## Export Formats

Tested formats:
- **PNG**: Image export with custom colors and cell sizes
- **JAC**: Embroidery format export
- **TXT**: Text/CSV export with metadata

## Adding Tests

1. Create test file: `tests/test_<module>.py`
2. Use pytest fixtures from `conftest.py`
3. Add appropriate markers: `@pytest.mark.pattern`, `@pytest.mark.cultural`, etc.
4. Run: `pytest tests/test_<module>.py -v`
