# DNA Textile Pattern Generator — Phase 3

## Multi-Layer Pipeline with Tribe-Specific Weaving Engines

Generates textile patterns from DNA sequences using a **multi-layer hierarchical pipeline** with **tribe-specific weaving engines**, **procedural motif generation**, and **cultural symbol creation** from **15+ Thai indigenous communities**.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate a pattern with Karen weaving engine
python -m src.main examples/karen_sample.fasta -c karen

# Generate with motifs and symbols
python -m src.main "ATGCATGC..." -c hmong --symbol --motif-placement grid --motif-count 9

# Analyze DNA features
python -m src.main "ATGC..." --analyze

# List all communities
python -m src.main --list-communities

# List motifs for Hmong
python -m src.main --list-motifs -c hmong

# Check cultural sensitivity
python -m src.main -c karen --sensitivity-check
```

---

## Architecture: Multi-Layer Pipeline

```
DNA Sequence
    │
    ▼
┌─────────────────────┐
│  DNA Feature Extract│  ← GC content, k-mers, palindromes,
│                     │    homopolymers, repeats, codons, entropy
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Tribe Weaving Engine│  ← Karen/Hmong/ThaiLue/TaiDam/Lisu/Mien/Akha
│                     │    Each tribe has unique weaving logic
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Layer 1: Background│  ← Base color, texture
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Layer 2: Structure │  ← Stripes/blocks/patches/resist/beads
│                     │    (tribe-specific patterns from DNA)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Layer 3: Detail    │  ← Embroidery stitches, silver threads,
│                     │    supplementary weft, diamond patterns
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Layer 4: Motifs    │  ← Procedurally generated from DNA
│                     │    (diamonds, butterflies, nagas, lotus, etc.)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Layer 5: Symbols   │  ← Cultural symbols (mandalas, totems,
│                     │    clan shields, spirit masks, etc.)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Cultural Rules     │  ← Border styles, taboo checks,
│                     │    palette enforcement
└─────────┬───────────┘
          │
          ▼
   Final Pattern (PNG/JAC/TXT)
```

---

## DNA Feature Extraction

Extracts semantic features from DNA to drive pattern generation:

| Feature | Description | Pattern Impact |
|---------|-------------|----------------|
| **GC Content** | % of G+C bases | Color complexity, motif type |
| **k-mer Frequencies** | Di/tri/tetra-nucleotide counts | Motif selection, color mapping |
| **Homopolymer Runs** | Consecutive same bases (AAA, TTT...) | Bold bands, circular motifs |
| **Palindromes** | DNA complement palindromes | Symmetric patterns, resist shapes |
| **Tandem Repeats** | Repeated motifs (ATATAT...) | Rhythm, repeat density |
| **Codons** | Triplet reading frames | Color assignment, motif variation |
| **Shannon Entropy** | Base distribution randomness | Pattern randomness vs structure |

### Derived Scores

- **Complexity Score** (0-1): Drives color count & motif density
- **Symmetry Score** (0-1): Drives symmetry preference
- **Rhythm Score** (0-1): Drives repeat density vs randomness

---

## Tribe-Specific Weaving Engines

Each tribe has a custom weaving engine that implements its actual textile technique:

| Engine | Technique | Structure | Detail |
|--------|-----------|-----------|--------|
| **Karen** | Weft-faced stripes | Horizontal bands | Diamonds/crosses embroidery |
| **Hmong** | Reverse appliqué (pau kuam) | Layered patches | Cross-stitch embroidery |
| **Thai Lue** | Supplementary weft (jin/jok) | Jok blocks | Gold supplementary threads |
| **Tai Dam** | Indigo reserve dyeing | Resist patterns | Silver thread patterns |
| **Lisu** | Color-block weaving | Vertical blocks | Horizontal accent lines |
| **Mien** | Cross-stitch embroidery | Counted stitch grid | Gold cross-stitches |
| **Akha** | Beaded weaving | Bead grid | Silver coin circles |
| **Generic** | Fallback for others | Grid pattern | Dot patterns |

### How DNA Drives Each Tribe

**Karen**: DNA chunks → horizontal stripe colors, base → diamond/cross detail
**Hmong**: DNA → patch colors/shapes, base → stitch type (X/square/dot/line)
**Thai Lue**: DNA GC content → jok block presence, base → supplementary thread pattern
**Tai Dam**: DNA palindromes → resist diamond shapes, homopolymers → circular motifs
**Lisu**: DNA GC → vertical block colors, base → horizontal accent lines
**Mien**: DNA base → cross-stitch color, A bases → gold accents
**Akha**: DNA base → bead color, homopolymers → silver coin circles

---

## Motif Generation (21 Types)

Procedurally generated from DNA features:

### Geometric
- `diamond` — Nested diamonds with DNA-driven colors
- `triangle` — Layered triangles
- `zigzag` — DNA-driven wave patterns
- `wave` — Multi-layer interference waves
- `spiral` — Golden angle spiral

### Animal
- `butterfly` — Symmetric wings with DNA spots
- `naga` — Sinusoidal serpent with scales
- `elephant` — Body/head/trunk/legs
- `fish` — Body/tail/eye
- `bird` — Body/wings/head/beak

### Plant
- `lotus` — Petals with DNA-driven colors
- `bamboo` — Stalks/nodes/leaves
- `rice` — Stem/grain heads/awns
- `flower` — Petals with center
- `tree` — Trunk/canopy (Tree of Life)

### Spiritual
- `spirit_gate` — Pillars/lintel/roof
- `sun` — Disk with rays
- `moon` — Crescent shape
- `sacred_geometry` — Concentric circles + star

### Clan Marks
- `clan_mark` — Unique pattern from DNA hash
- `ancestor_mark` — Stylized human figure

---

## Symbol Generation (6 Types)

Larger cultural compositions:

| Symbol | Description |
|--------|-------------|
| `totem` | Stacked faces on a pole |
| `mandala` | Radial symmetry with DNA-driven layers |
| `clan_shield` | Shield shape with DNA colors + inner symbol |
| `spirit_mask` | Face with eyes/mouth/forehead patterns |
| `cosmic_diagram` | Worlds/axes/markers from DNA |
| `story_panel` | Narrative scenes from DNA sequence |

---

## CLI Reference

```
python -m src.main [OPTIONS] [input]

Positional:
  input                 FASTA file or DNA string

Options:
  -s, --size            Grid size NxN (default: 100)
  -c, --community       Community name (default: generic)
  --complexity          beginner, intermediate, expert
  --seed                Random seed
  -o, --output          Output directory

Motif Settings:
  --no-motif            Disable motif layer
  --motif-placement     center, grid, scatter, border
  --motif-count         Number of motifs (default: 1)
  --motif-types         Motif types (default: auto from DNA)
  --motif-size          Motif grid size (default: 20)

Symbol Settings:
  --symbol              Enable symbol layer
  --symbol-type         auto, totem, mandala, clan_shield, spirit_mask,
                        cosmic_diagram, story_panel
  --symbol-size         Symbol grid size (default: 40)

Layer Opacity:
  --opacity-structure   Structure layer opacity (default: 0.8)
  --opacity-detail      Detail layer opacity (default: 0.5)
  --opacity-motif       Motif layer opacity (default: 0.7)
  --opacity-symbol      Symbol layer opacity (default: 0.6)

Info Commands:
  --list-communities    List all communities
  --list-motifs         List motifs for community
  --list-palettes       List color palettes
  --list-borders        List border styles
  --list-engines        List weaving engines
  --info                Show community textile info
  --analyze             Analyze DNA features
  --sensitivity-check   Run cultural sensitivity check
  --mix FASTA [FASTA...]  Mix multiple sequences
```

---

## Examples

```bash
# Karen pattern with grid of 9 motifs
python -m src.main "ATGC..." -c karen --motif-placement grid --motif-count 9

# Hmong pattern with scattered motifs and mandala symbol
python -m src.main "ATGC..." -c hmong --symbol --motif-placement scatter --motif-count 6

# Thai Lue with center motif
python -m src.main "ATGC..." -c thai_lue --motif-placement center

# Tai Dam with clan_shield symbol
python -m src.main "ATGC..." -c tai_dam --symbol --symbol-type clan_shield

# Analyze DNA before generating
python -m src.main "ATGC..." --analyze

# Generate with specific motif types
python -m src.main "ATGC..." -c karen --motif-types diamond lotus butterfly

# Mix multiple DNA sequences
python -m src.main --mix sample1.fasta sample2.fasta -c hmong
```

---

## File Structure

```
dna-textile/
├── src/
│   ├── dna_features.py         # DNA feature extraction (NEW)
│   ├── weaving_engine.py       # Tribe-specific weaving engines (NEW)
│   ├── motif_generator.py      # Motif & symbol generation (NEW)
│   ├── pipeline.py             # Multi-layer pipeline orchestrator (NEW)
│   ├── cultural_rules.py       # Rule engine (15+ communities)
│   ├── motif_library.py        # Motif management (100+ motifs)
│   ├── color_palette.py        # Color rules per community
│   ├── border_style.py         # Woven/embroidered/printed borders
│   ├── complexity.py           # Beginner/intermediate/expert levels
│   ├── sensitivity_checker.py  # Taboo/sacred motif validation
│   ├── pattern_generator.py    # Phase 1 generator (legacy)
│   ├── main.py                 # CLI entry point
│   ├── dna_parser.py           # FASTA parser
│   ├── exporters.py            # PNG/JAC/TXT export
│   └── mixer.py                # Multi-sequence blending
├── cultural_rules/             # 15 community JSON rule files
├── motif_library/              # 15 community motif JSON files
├── color_palettes.json         # Traditional colors
├── border_styles.json          # Border techniques
├── complexity_levels.json      # Difficulty constraints
├── cultural_sensitivity.json   # Taboos, sacred motifs, workflow
├── tests/
├── examples/                   # Sample FASTA files
├── output/                     # Generated patterns
└── README.md
```

---

## Communities (15+)

| Community | Engine | Language Family | Region |
|-----------|--------|----------------|--------|
| Karen (Kayah) | ✓ | Sino-Tibetan | Western/Northern Thailand |
| Hmong | ✓ | Hmong-Mien | Northern Thailand |
| Akha | ✓ | Sino-Tibetan | Northern highlands |
| Lahu | | Austroasiatic | Northern/Western Thailand |
| Lisu | ✓ | Sino-Tibetan | Northern Thailand |
| Mien (Yao) | ✓ | Hmong-Mien | Northern Thailand |
| Palaung (Ta-ang) | | Austroasiatic | Northern border regions |
| Khamu | | Austroasiatic | Northern border (Laos) |
| Lua (Lawaa) | | Austroasiatic | Northern/Central Thailand |
| Mlabri (Phi Tong Luang) | | Austroasiatic | Forest nomads |
| Mani (Maniq) | | Austroasiatic | Southern Thailand |
| Moklen (Chao Lay) | | Austroasiatic | Southern coast |
| Urak Lawoi | | Austronesian | Southern islands |
| Thai Lue | ✓ | Tai-Kadai | Northern Thailand |
| Tai Dam (Black Tai) | ✓ | Tai-Kadai | Northern/Central Thailand |

✓ = Has custom weaving engine

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/test_generator.py -v
```

---

## License & Attribution

This project encodes cultural knowledge for educational and preservation purposes. All generated patterns must include community attribution. Commercial use requires explicit community consent per Thailand's Protection and Promotion of the Thai Traditional Wisdom Act.

---

*Phase 1: DNA → Pattern mapping | Phase 2: Cultural rule engine | Phase 3: Multi-layer pipeline with tribe-specific weaving engines*
