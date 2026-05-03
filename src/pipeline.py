"""
Pipeline — orchestrates the full DNA → textile pattern generation.

Phase 3: Multi-layer pipeline that combines:
1. DNA feature extraction
2. Tribe-specific weaving engine
3. Motif & symbol generation
4. Hierarchical composition
5. Cultural rule application
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .dna_features import DNAFeatures, extract_features
from .weaving_engine import WeavingEngine, get_engine
from .motif_generator import MotifGenerator
from .cultural_rules import apply_cultural_rules, get_community_rules
from .complexity import get_max_colors, get_motif_complexity_cap, get_density_from_entropy


@dataclass
class PipelineConfig:
    """Configuration for the generation pipeline."""
    grid_size: int = 100
    community: str = "generic"
    complexity: str = "intermediate"
    seed: Optional[int] = None
    include_motif: bool = True
    include_symbol: bool = False
    motif_size: int = 20
    symbol_size: int = 40
    motif_placement: str = "center"  # center, grid, scatter, border
    motif_count: int = 1
    motif_types: List[str] = field(default_factory=list)  # empty = auto
    symbol_type: str = "auto"
    layer_opacity: Dict[str, float] = field(default_factory=lambda: {
        "background": 1.0,
        "structure": 0.8,
        "detail": 0.5,
        "motif": 0.7,
        "symbol": 0.6,
        "border": 1.0,
    })
    # Entropy-based density mode
    density_mode: str = "entropy"  # "entropy" or "fixed"
    # Output format: "grid" (default), "costume", "costume_preview", "sewing_pattern"
    output_format: str = "grid"
    # Garment name for costume output
    garment_name: str = "default"
    # Pattern algorithm type (stripe, voronoi, fractal_koch, etc.)
    pattern_type: str = "stripe"
    # Stitch aspect ratio (width:height)
    stitch_ratio: float = 1.0
    # Sewing pattern options
    garment_size: str = "M"
    seam_allowance_cm: float = 1.0
    fabric_width_cm: float = 150.0


class Pipeline:
    """Full DNA → textile pattern generation pipeline."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.rng = random.Random(config.seed)

        # Initialize components
        self.engine = get_engine(config.community, config.grid_size)
        self.motif_gen = MotifGenerator(config.community, seed=config.seed)
        self.rules = get_community_rules(config.community)

    def run(self, sequence: str):
        """
        Run the full pipeline on a DNA sequence.

        Returns:
            For output_format="grid": np.ndarray (H×W×3 uint8)
            For output_format="costume": Dict[str, np.ndarray]
            For output_format="costume_preview": np.ndarray (composite preview)
            For output_format="sewing_pattern": dict (sewing pattern package)
        """
        features = extract_features(sequence)
        pattern_type = self.config.pattern_type

        # Use PatternGenerator for algorithm-driven patterns
        if pattern_type in ("stripe", "grid", "spiral", "random",
                            "cellular_automata", "lace",
                            "codon_tile", "phase_shift",
                            "fractal_koch", "voronoi", "wave_interference",
                            "perlin_noise", "l_system", "fourier_pattern",
                            "diffusion", "mosaic"):
            from .pattern_generator import PatternGenerator
            gen = PatternGenerator(
                grid_size=self.config.grid_size,
                community=self.config.community,
                complexity=self.config.complexity,
                seed=self.config.seed,
                stitch_ratio=self.config.stitch_ratio,
            )
            result = gen.generate_grid(sequence, pattern_type=pattern_type)
        else:
            # Use WeavingEngine (tribe-specific)
            params = self.engine.generate_params(features)
            layers = {}
            layers["background"] = self.engine.render_background(params, features)
            layers["structure"] = self.engine.render_structure(params, features)
            layers["detail"] = self.engine.render_detail(params, features)
            if self.config.include_motif:
                layers["motif"] = self._render_motif_layer(features, params)
            if self.config.include_symbol:
                layers["symbol"] = self._render_symbol_layer(features, params)
            result = self._composite_layers(layers, features)
            result = apply_cultural_rules(result, rule=self.rules)
            result = self._apply_complexity(result, features)

        # Handle output formats
        fmt = self.config.output_format
        if fmt == "costume":
            return self._render_costume(result, features)
        elif fmt == "costume_preview":
            return self._render_costume_preview(result, features)
        elif fmt == "sewing_pattern":
            return self._render_sewing_pattern(result, features)
        return result

    def _render_costume(
        self, pattern_grid: np.ndarray, features: DNAFeatures
    ) -> Dict[str, np.ndarray]:
        """Render pattern onto garment regions."""
        from .costume_mapper import CostumeMapper
        mapper = CostumeMapper(self.config.community, seed=self.config.seed)
        return mapper.map_pattern_to_garment(
            pattern_grid,
            garment_name=self.config.garment_name,
            features=features,
        )

    def _render_costume_preview(
        self, pattern_grid: np.ndarray, features: DNAFeatures
    ) -> np.ndarray:
        """Render costume preview (all regions in a flat layout)."""
        from .costume_mapper import CostumeMapper
        mapper = CostumeMapper(self.config.community, seed=self.config.seed)
        return mapper.generate_costume_preview(
            pattern_grid,
            features,
            garment_name=self.config.garment_name,
        )

    def _render_sewing_pattern(
        self, pattern_grid: np.ndarray, features: DNAFeatures
    ) -> dict:
        """Generate printable sewing pattern package."""
        from .printable_patterns import export_sewing_pattern
        out_dir = f"output/sewing_{self.config.community}_{self.config.garment_name}"
        return export_sewing_pattern(
            pattern_grid=pattern_grid,
            community=self.config.community,
            garment_name=self.config.garment_name,
            features=features,
            output_dir=out_dir,
            size=self.config.garment_size,
            seam_allowance_cm=self.config.seam_allowance_cm,
            fabric_width_cm=self.config.fabric_width_cm,
        )

    def _render_motif_layer(self, features: DNAFeatures, params) -> np.ndarray:
        """Render the motif layer."""
        grid = np.zeros((self.config.grid_size, self.config.grid_size, 3), dtype=np.uint8)

        motif_size = self.config.motif_size
        placement = self.config.motif_placement
        motif_types = self.config.motif_types or ["auto"]

        if placement == "center":
            # Single motif in center
            motif_type = motif_types[0] if motif_types else "auto"
            motif = self.motif_gen.generate_motif(features, motif_type, motif_size)
            cy = (self.config.grid_size - motif_size) // 2
            cx = (self.config.grid_size - motif_size) // 2
            grid[cy:cy + motif_size, cx:cx + motif_size] = motif

        elif placement == "grid":
            # Grid of motifs
            count = self.config.motif_count or 4
            grid_dim = int(np.ceil(np.sqrt(count)))
            spacing = self.config.grid_size // grid_dim

            for row in range(grid_dim):
                for col in range(grid_dim):
                    if row * grid_dim + col >= count:
                        break
                    motif_type = motif_types[(row * grid_dim + col) % len(motif_types)]
                    motif = self.motif_gen.generate_motif(features, motif_type, spacing - 2)
                    y = row * spacing + 1
                    x = col * spacing + 1
                    mh, mw = motif.shape[:2]
                    grid[y:y + mh, x:x + mw] = motif

        elif placement == "scatter":
            # Random scatter of motifs
            count = self.config.motif_count or 6
            for i in range(count):
                motif_type = motif_types[i % len(motif_types)]
                motif = self.motif_gen.generate_motif(features, motif_type, motif_size)
                y = self.rng.randint(0, self.config.grid_size - motif_size)
                x = self.rng.randint(0, self.config.grid_size - motif_size)
                mh, mw = motif.shape[:2]
                grid[y:y + mh, x:x + mw] = motif

        elif placement == "border":
            # Motifs along the border
            motif_count = self.config.motif_count or 8
            perimeter = self.config.grid_size * 2 + (self.config.grid_size - 2) * 2
            spacing = perimeter // motif_count

            pos = 0
            for i in range(motif_count):
                motif_type = motif_types[i % len(motif_types)]
                motif = self.motif_gen.generate_motif(features, motif_type, motif_size // 2)
                mh, mw = motif.shape[:2]

                # Position along perimeter
                side = pos // self.config.grid_size
                offset = pos % self.config.grid_size

                if side == 0:  # top
                    y, x = 0, offset
                elif side == 1:  # right
                    y, x = offset, self.config.grid_size - 1
                elif side == 2:  # bottom
                    y, x = self.config.grid_size - 1, self.config.grid_size - 1 - offset
                else:  # left
                    y, x = self.config.grid_size - 1 - offset, 0

                if 0 <= y < self.config.grid_size and 0 <= x < self.config.grid_size:
                    grid[y:y + mh, x:x + mw] = motif

                pos += spacing

        return grid

    def _render_symbol_layer(self, features: DNAFeatures, params) -> np.ndarray:
        """Render the symbol layer."""
        grid = np.zeros((self.config.grid_size, self.config.grid_size, 3), dtype=np.uint8)

        symbol_size = min(self.config.symbol_size, self.config.grid_size // 2)
        symbol_type = self.config.symbol_type

        symbol = self.motif_gen.generate_symbol(features, symbol_type, symbol_size)

        cy = (self.config.grid_size - symbol_size) // 2
        cx = (self.config.grid_size - symbol_size) // 2
        grid[cy:cy + symbol_size, cx:cx + symbol_size] = symbol

        return grid

    def _composite_layers(self, layers: Dict[str, np.ndarray], features: Optional[DNAFeatures] = None) -> np.ndarray:
        """Composite layers hierarchically — each level builds on the previous."""
        config = self.config
        opacity = config.layer_opacity
        gs = config.grid_size

        # Level 1: Background (texture + base color)
        result = layers.get("background", np.zeros(
            (gs, gs, 3), dtype=np.uint8
        )).copy()

        # Level 2: Structure (large-scale patterns, scale 20-50px)
        if "structure" in layers:
            result = self._blend(
                result, layers["structure"],
                opacity.get("structure", 0.8), "over"
            )

        # Level 3: Detail (medium patterns, scale 5-15px)
        if "detail" in layers:
            result = self._blend(
                result, layers["detail"],
                opacity.get("detail", 0.5), "over"
            )

        # Level 4: Motif (small patterns, scale 10-25px)
        if "motif" in layers:
            result = self._blend(
                result, layers["motif"],
                opacity.get("motif", 0.7), "over"
            )

        # Level 5: Symbol (if enabled)
        if "symbol" in layers:
            result = self._blend(
                result, layers["symbol"],
                opacity.get("symbol", 0.6), "over"
            )

        # Level 6: Micro-detail (DNA-driven pixel noise, scale 1-3px)
        if features is not None:
            micro = self._render_micro_detail(features, gs)
            micro_opacity = 0.15
            result = self._blend(result, micro, micro_opacity, "over")

        return result

    def _render_micro_detail(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Render DNA-driven pixel noise at 1-3px scale."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        seq = features.sequence
        if not seq:
            return grid

        for y in range(size):
            for x in range(size):
                idx = (y * size + x) % len(seq)
                base = seq[idx]
                # Micro-pattern: 1-3px dots based on base
                base_val = {"A": 1, "T": 2, "G": 3, "C": 4}.get(base, 0)
                if base_val > 0:
                    # Create small dots at sub-pixel scale
                    for dy in range(min(base_val, 3)):
                        for dx in range(min(base_val, 3)):
                            py, px = y + dy, x + dx
                            if 0 <= py < size and 0 <= px < size:
                                # Subtle noise color from base
                                color = {
                                    "A": (255, 200, 200),
                                    "T": (200, 200, 255),
                                    "G": (200, 255, 200),
                                    "C": (255, 255, 200),
                                }.get(base, (128, 128, 128))
                                grid[py, px] = color
        return grid

    def _blend(self, base: np.ndarray, overlay: np.ndarray, opacity: float, mode: str) -> np.ndarray:
        """Alpha blend two layers."""
        if opacity >= 1.0:
            return overlay.copy()
        if opacity <= 0.0:
            return base.copy()

        blended = base.astype(np.float32) * (1 - opacity) + overlay.astype(np.float32) * opacity
        return np.clip(blended, 0, 255).astype(np.uint8)

    def _apply_complexity(self, grid: np.ndarray, features: DNAFeatures) -> np.ndarray:
        """Apply complexity constraints."""
        from .color_palette import apply_palette_to_grid, get_all_colors

        max_colors = get_max_colors(self.config.complexity)
        palette = get_all_colors(self.config.community)

        if palette and len(palette) <= max_colors:
            grid = apply_palette_to_grid(grid, self.config.community)

        return grid


def generate_pattern(
    sequence: str,
    community: str = "generic",
    grid_size: int = 100,
    complexity: str = "intermediate",
    seed: Optional[int] = None,
    include_motif: bool = True,
    include_symbol: bool = False,
    motif_placement: str = "center",
    motif_types: Optional[List[str]] = None,
) -> np.ndarray:
    """
    Convenience function to generate a pattern.

    Args:
        sequence: Cleaned DNA string
        community: Tribe/community name
        grid_size: Output grid dimension
        complexity: Pattern complexity
        seed: Random seed
        include_motif: Whether to include motif layer
        include_symbol: Whether to include symbol layer
        motif_placement: Where to place motifs
        motif_types: List of motif types to use

    Returns:
        Pattern grid (H×W×3 uint8)
    """
    config = PipelineConfig(
        grid_size=grid_size,
        community=community,
        complexity=complexity,
        seed=seed,
        include_motif=include_motif,
        include_symbol=include_symbol,
        motif_placement=motif_placement,
        motif_types=motif_types or [],
    )
    pipeline = Pipeline(config)
    return pipeline.run(sequence)
