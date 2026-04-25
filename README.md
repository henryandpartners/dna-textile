# DNA Textile Pattern Generator — Phase 2

## Cultural Rule Engine Expansion

Generates textile patterns from DNA sequences, applying community-specific cultural rules from **15+ Thai indigenous communities**.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate a pattern with Karen cultural rules
python -m src.main examples/karen_sample.fasta -c karen -t grid

# List all communities
python -m src.main --list-communities

# List motifs for Hmong
python -m src.main --list-motifs -c hmong

# Check cultural sensitivity
python -m src.main -c karen -m spirit_band --sensitivity-check

# Show community info
python -m src.main -c "thai lue" --info
```

---

## Communities (15+)

| Community | Language Family | Region | Complexity |
|-----------|----------------|--------|------------|
| Karen (Kayah) | Sino-Tibetan | Western/Northern Thailand | Beginner–Intermediate |
| Hmong | Hmong-Mien | Northern Thailand | Intermediate–Expert |
| Akha | Sino-Tibetan | Northern highlands | Intermediate–Expert |
| Lahu | Sino-Tibetan | Northern/Western Thailand | Beginner–Intermediate |
| Lisu | Sino-Tibetan | Northern Thailand | Intermediate–Expert |
| Mien (Yao) | Hmong-Mien | Northern Thailand | Intermediate–Expert |
| Palaung (Ta-ang) | Austroasiatic | Northern border regions | Beginner–Intermediate |
| Khamu | Austroasiatic | Northern border (Laos) | Beginner |
| Lua (Lawaa) | Austroasiatic | Northern/Central Thailand | Beginner–Intermediate |
| Mlabri (Phi Tong Luang) | Austroasiatic | Forest nomads | Beginner |
| Mani (Maniq) | Austroasiatic | Southern Thailand | Beginner |
| Moklen (Chao Lay) | Austroasiatic | Southern coast | Beginner |
| Urak Lawoi | Austronesian | Southern islands | Beginner |
| Thai Lue | Tai-Kadai | Northern Thailand | Intermediate–Expert |
| Tai Dam (Black Tai) | Tai-Kadai | Northern/Central Thailand | Intermediate–Expert |

---

## Features

### Motif Library (100+ motifs)
- **Geometric**: diamonds, stripes, crosses, waves
- **Animal**: butterflies, nagas, elephants, fish
- **Plant**: lotus, bamboo, rice, flowers
- **Spiritual**: ancestor marks, spirit gates, sacred symbols

### Color Palettes
Traditional colors per community with cultural meanings:
- Primary, secondary, and accent color groups
- Hex and RGB formats
- Cultural significance annotations

### Border Styles
Three categories with multiple techniques:
- **Woven**: solid, double, striped
- **Embroidered**: zigzag, cross-stitch, chain-stitch, counted-thread
- **Printed**: batik, ikat-edge, block-print, tie-dye

### Complexity Levels
- **Beginner**: Simple patterns, 2-3 colors, small motifs
- **Intermediate**: Moderate complexity, 3-5 colors, multiple motif types
- **Expert**: Intricate patterns, 5-8 colors, narrative compositions

### Cultural Sensitivity
- **Taboo patterns**: Automatically detected and blocked
- **Sacred motifs**: Require community approval workflow
- **Attribution**: Mandatory community credit on all outputs

---

## CLI Reference

```
python -m src.main [OPTIONS] [input]

Positional:
  input                 FASTA file or DNA string (default: examples/karen_sample.fasta)

Options:
  -t, --type            Pattern type: stripe, grid, spiral, random (default: grid)
  -s, --size            Grid size NxN (default: 100)
  -c, --community       Community name (default: generic)
  -m, --motif           Motif name to overlay
  --complexity          Complexity: beginner, intermediate, expert
  --sensitivity-check   Run cultural sensitivity validation
  -o, --output          Output directory (default: output/)
  --seed                Random seed
  --mix FASTA [FASTA...]  Mix multiple sequences

Info commands:
  --list-communities    List all communities
  --list-motifs         List motifs for community
  --list-palettes       List color palettes
  --list-borders        List border styles
  --info                Show community textile info
```

---

## File Structure

```
dna-textile/
├── src/
│   ├── cultural_rules.py      # Rule engine (15+ communities)
│   ├── motif_library.py       # Motif management (100+ motifs)
│   ├── color_palette.py       # Color rules per community
│   ├── border_style.py        # Woven/embroidered/printed borders
│   ├── complexity.py          # Beginner/intermediate/expert levels
│   ├── sensitivity_checker.py # Taboo/sacred motif validation
│   ├── pattern_generator.py   # DNA → grid with cultural rules
│   ├── main.py                # CLI entry point
│   ├── dna_parser.py          # FASTA parser
│   ├── exporters.py           # PNG/JAC/TXT export
│   └── mixer.py               # Multi-sequence blending
├── cultural_rules/            # 15 community JSON rule files
├── motif_library/             # 15 community motif JSON files
├── color_palettes.json        # Traditional colors
├── border_styles.json         # Border techniques
├── complexity_levels.json     # Difficulty constraints
├── cultural_sensitivity.json  # Taboos, sacred motifs, workflow
├── tests/
│   ├── test_generator.py      # Phase 1 tests
│   └── test_cultural_rules.py # Phase 2 tests
├── examples/                  # Sample FASTA files
├── output/                    # Generated patterns
└── README.md
```

---

## Cultural Sensitivity

⚠️ **Important**: These rules are based on academic research and should be validated with community representatives before commercial use.

### Approval Workflow
1. **Identify** — Determine which motifs are sacred/restricted
2. **Consult** — Contact community representatives
3. **Request** — Submit formal usage permission request
4. **Agree** — Negotiate terms and benefit sharing
5. **Document** — Record approval in writing
6. **Implement** — Use pattern with all conditions met

### Sacred Motifs Require Approval
- Karen: spirit_band, ancestor_diamond, clan_stripe
- Hmong: snail_path, flower_carpet, spirit_gate
- Akha: spirit_gate, silver_circle, ancestor_eye
- Thai Lue: naga_serpent, mount_meru, lotus_buddha, celestial_dance, lai_kham
- Tai Dam: soul_butterfly, silver_thread, clan_diamond, spirit_bridge, kingdom_mark

### Taboo Patterns
Certain patterns are culturally inappropriate for specific communities. The `--sensitivity-check` flag validates your pattern selection.

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run Phase 2 tests only
python -m pytest tests/test_cultural_rules.py -v
```

---

## License & Attribution

This project encodes cultural knowledge for educational and preservation purposes. All generated patterns must include community attribution. Commercial use requires explicit community consent per Thailand's Protection and Promotion of the Thai Traditional Wisdom Act.

---

*Phase 1: DNA → Pattern mapping | Phase 2: Cultural rule engine expansion*
