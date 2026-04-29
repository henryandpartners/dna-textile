"""Pipeline — orchestrates the full 5-layer DNA textile composition.

Phase 3: DNA → Feature Extraction → Tribe Weaving Engine → 5-Layer Composition → Cultural Rules → Pattern

Layers:
1. Background  - Base color + texture from DNA
2. Structure   - Tribe-specific (stripes/patches/resist/beads/blocks)
3. Detail      - Embroidery stitches, silver threads, supplementary weft
4. Motifs      - Procedurally generated motifs placed on grid
5. Symbols     - Cultural compositions (mandalas, totems, etc.)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from . import color_palette as cp
from . import complexity as cx
from . import cultural_rules
from . import dna_features
from . import exporters
from . import motif_generator as mg
from . import weaving_engine as we


# ── Pipeline Config ───────────────────────────────────────

@dataclass
class PipelineConfig:
    """Configuration for the pipeline run."""
    community: str = "generic"
    grid_size: int = 200
    complexity: str = "intermediate"
    seed: int = 42
    motif_placement: str = "grid"  # "grid", "scatter", "dna"
    include_symbols: bool = False
    include_motifs: bool = True
    include_detail: bool = True
    include_structure: bool = True
    motif_count: int = 6
    symbol_count: int = 1
    output_path: Optional[str] = None
    apply_cultural_rules: bool = True


# ── Pipeline Result ───────────────────────────────────────

@dataclass
class PipelineResult:
    """Result from a pipeline run."""
    grid: np.ndarray
    features: Dict[str, Any]
    community: str
    layers: Dict[str, np.ndarray] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Main Pipeline ─────────────────────────────────────────

def run_pipeline(
    sequence: str,
    config: Optional[PipelineConfig] = None,
) -> PipelineResult:
    """Run the full 5-layer DNA textile pipeline.

    Args:
        sequence: Cleaned DNA string (uppercase ATGC).
        config: Pipeline configuration.

    Returns:
        PipelineResult with final grid and metadata.
    """
    if config is None:
        config = PipelineConfig()

    random.seed(config.seed)
    size = config.grid_size

    # ── Step 1: Extract DNA Features ──────────────────────
    features = dna_features.extract_features(sequence)

    # ── Step 2: Select Tribe Weaving Engine ───────────────
    palette = cp.get_all_colors(config.community)
    if not palette:
        palette = [(0, 0, 0), (128, 128, 128), (255, 255, 255)]
    engine = we.get_engine(config.community, palette)

    layers: Dict[str, np.ndarray] = {}

    # ── Step 3: Background Layer ──────────────────────────
    bg_layer = engine.generate_background(features, size, seed=config.seed)
    grid = bg_layer.grid.copy()
    layers["background"] = grid.copy()

    # ── Step 4: Structure Layer ───────────────────────────
    if config.include_structure:
        struct_layer = engine.generate_structure(features, size, seed=config.seed)
        grid = we._blend(grid, struct_layer.grid)
        layers["structure"] = struct_layer.grid.copy()

    # ── Step 5: Detail Layer ──────────────────────────────
    if config.include_detail:
        detail_layer = engine.generate_detail(features, size, seed=config.seed)
        grid = we._blend(grid, detail_layer.grid)
        layers["detail"] = detail_layer.grid.copy()

    # ── Step 6: Motif Layer ───────────────────────────────
    if config.include_motifs:
        motif_layer = _generate_motif_layer(features, config, engine, size)
        grid = we._blend(grid, motif_layer.grid)
        layers["motifs"] = motif_layer.grid.copy()

    # ── Step 7: Symbol Layer ──────────────────────────────
    if config.include_symbols:
        symbol_layer = _generate_symbol_layer(features, config, engine, size)
        grid = we._blend(grid, symbol_layer.grid)
        layers["symbols"] = symbol_layer.grid.copy()

    # ── Step 8: Apply Cultural Rules ──────────────────────
    if config.apply_cultural_rules:
        rule = cultural_rules.get_community_rules(config.community)
        grid = cultural_rules.apply_cultural_rules(grid, rule=rule)

    # ── Step 9: Export ────────────────────────────────────
    metadata = {
        "sequence_length": len(sequence),
        "gc_content": features["gc_content"],
        "shannon_entropy": features["shannon_entropy"],
        "community": config.community,
        "grid_size": size,
        "complexity": config.complexity,
        "seed": config.seed,
        "motif_placement": config.motif_placement,
    }

    if config.output_path:
        exporters.export_png(grid, config.output_path)

    return PipelineResult(
        grid=grid,
        features=features,
        community=config.community,
        layers=layers,
        metadata=metadata,
    )


# ── Motif Layer Generation ───────────────────────────────

def _generate_motif_layer(
    features: Dict[str, Any],
    config: PipelineConfig,
    engine: we.WeavingEngine,
    size: int,
) -> we.LayerSpec:
    """Generate the motif layer with procedurally placed motifs."""
    grid = np.zeros((size, size, 3), dtype=np.uint8)
    palette = engine.palette

    motif_type = mg.select_motif_from_dna(features, seed=config.seed)
    motif_size = mg.get_motif_size(features)

    # Determine motif color from DNA
    base = dna_features.select_dna_base(features)
    color_idx = {"A": 0, "T": 2, "G": 1, "C": 3}.get(base, 0)
    motif_color = we._pick_color(palette, color_idx)

    if config.motif_placement == "grid":
        # Place motifs on a regular grid
        spacing = max(motif_size * 3, size // max(int(np.sqrt(config.motif_count)), 1))
        count = 0
        for r in range(spacing, size - spacing, spacing):
            for c in range(spacing, size - spacing, spacing):
                if count >= config.motif_count:
                    break
                mg.place_motif(grid, motif_type, r, c, motif_size, motif_color)
                count += 1
            if count >= config.motif_count:
                break

    elif config.motif_placement == "scatter":
        # Random scatter placement
        random.seed(config.seed + 100)
        for _ in range(config.motif_count):
            r = random.randint(motif_size * 2, size - motif_size * 2)
            c = random.randint(motif_size * 2, size - motif_size * 2)
            color = we._pick_color(palette, random.randint(0, len(palette) - 1))
            m_type = random.choice(list(mg.MOTIF_FUNCTIONS.keys()))
            mg.place_motif(grid, m_type, r, c, motif_size, color)

    elif config.motif_placement == "dna":
        # Place motifs at positions determined by DNA features
        # Use homopolymer positions, repeat positions, etc.
        positions = []
        for hp in features.get("homopolymers", []):
            pos = hp["start"]
            r = (pos % size) * size // max(len(features.get("homopolymers", [{}]) or [{}]), 1)
            c = (pos // size) * size // max(len(features.get("homopolymers", [{}]) or [{}]), 1)
            positions.append((min(r, size - motif_size), min(c, size - motif_size)))
        for rep in features.get("tandem_repeats", []):
            pos = rep["start"]
            r = (pos % size)
            c = (pos // size) % size
            positions.append((min(r, size - motif_size), min(c, size - motif_size)))

        # Fallback to grid if not enough DNA-derived positions
        if len(positions) < config.motif_count:
            spacing = max(motif_size * 3, size // max(int(np.sqrt(config.motif_count)), 1))
            for r in range(spacing, size - spacing, spacing):
                for c in range(spacing, size - spacing, spacing):
                    positions.append((r, c))
                    if len(positions) >= config.motif_count:
                        break
                if len(positions) >= config.motif_count:
                    break

        for i, (r, c) in enumerate(positions[:config.motif_count]):
            color = we._pick_color(palette, i % len(palette))
            mg.place_motif(grid, motif_type, r, c, motif_size, color)

    return we.LayerSpec("motifs", grid, metadata={"motif_type": motif_type})


# ── Symbol Layer Generation ──────────────────────────────

def _generate_symbol_layer(
    features: Dict[str, Any],
    config: PipelineConfig,
    engine: we.WeavingEngine,
    size: int,
) -> we.LayerSpec:
    """Generate the symbol layer with cultural compositions."""
    grid = np.zeros((size, size, 3), dtype=np.uint8)
    palette = engine.palette

    symbol_type = mg.select_symbol_from_dna(features, seed=config.seed)
    symbol_size = mg.get_motif_size(features)
    symbol_color = we._pick_color(palette, 6)  # accent color

    if config.symbol_count == 1:
        # Center the symbol
        mg.place_symbol(grid, symbol_type, size // 2, size // 2, symbol_size * 2, symbol_color)
    else:
        # Place multiple symbols at corners and center
        positions = [
            (size // 4, size // 4),
            (size * 3 // 4, size // 4),
            (size // 2, size // 2),
            (size // 4, size * 3 // 4),
            (size * 3 // 4, size * 3 // 4),
        ]
        for i, (r, c) in enumerate(positions[:config.symbol_count]):
            color = we._pick_color(palette, i % len(palette))
            mg.place_symbol(grid, symbol_type, r, c, symbol_size, color)

    return we.LayerSpec("symbols", grid, metadata={"symbol_type": symbol_type})


# ── Convenience Functions ─────────────────────────────────

def generate_pattern(
    sequence: str,
    community: str = "generic",
    grid_size: int = 200,
    seed: int = 42,
    output_path: Optional[str] = None,
    **kwargs: Any,
) -> np.ndarray:
    """Quick function to generate a pattern from DNA.

    Args:
        sequence: Cleaned DNA string.
        community: Tribe/community name.
        grid_size: Output image size.
        seed: Random seed.
        output_path: Optional PNG output path.
        **kwargs: Additional PipelineConfig options.

    Returns:
        Final pattern grid (H×W×3 uint8).
    """
    config = PipelineConfig(
        community=community,
        grid_size=grid_size,
        seed=seed,
        output_path=output_path,
        **kwargs,
    )
    result = run_pipeline(sequence, config)
    return result.grid


def generate_batch(
    sequences: List[str],
    community: str = "generic",
    grid_size: int = 200,
    output_dir: str = "output",
    **kwargs: Any,
) -> List[PipelineResult]:
    """Generate patterns for multiple sequences.

    Args:
        sequences: List of DNA strings.
        community: Tribe/community name.
        grid_size: Output image size.
        output_dir: Directory for PNG outputs.
        **kwargs: Additional PipelineConfig options.

    Returns:
        List of PipelineResult objects.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for i, seq in enumerate(sequences):
        output_path = str(out / f"pattern_{i:03d}.png")
        config = PipelineConfig(
            community=community,
            grid_size=grid_size,
            seed=42 + i,
            output_path=output_path,
            **kwargs,
        )
        result = run_pipeline(seq, config)
        results.append(result)
    return results
