"""
Weaving Engine — tribe-specific pattern generation logic.

Phase 3: Each tribe has its own weaving engine that maps DNA features
to culturally appropriate pattern structures, colors, and motifs.

Tribes implement different weaving techniques:
- Karen: weft-faced stripes → horizontal bands
- Hmong: reverse appliqué (pau kuam) → layered patches + embroidery
- Thai Lue: supplementary weft (jin/jok) → pattern threads
- Tai Dam: indigo reserve dyeing → resist patterns
- Lisu: color-block weaving → bold geometric blocks
- Mien: cross-stitch embroidery → counted stitch grids
- Akha: beaded weaving → dot/mosaic patterns
- Lahu: striped with embroidery → bands + decorated panels
- Palaung: woven bands → horizontal stripe patterns
- Khamu: simple weave → basic geometric
- Lua: traditional weave → earth-tone patterns
- Mlabri: bark cloth → natural fiber textures
- Mani: minimal decoration → simple bands
- Moklen: sea-inspired → wave patterns
- Urak Lawoi: coastal weaving → ocean motifs
"""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .dna_features import DNAFeatures
from .color_palette import get_all_colors, get_primary_colors, get_secondary_colors, hex_to_rgb


@dataclass
class PatternLayer:
    """A single layer in the hierarchical pattern composition."""
    name: str
    grid: np.ndarray
    opacity: float = 1.0
    blend_mode: str = "over"  # over, multiply, screen, overlay


@dataclass
class WeavingParams:
    """Parameters produced by a weaving engine for pattern generation."""
    # Background
    bg_color: Tuple[int, int, int] = (0, 0, 0)
    bg_pattern: str = "solid"  # solid, gradient, noise, stripes

    # Structure layer
    structure_type: str = "none"  # none, stripes, grid, blocks, waves, diamonds
    structure_color: Tuple[int, int, int] = (128, 128, 128)
    structure_scale: int = 10  # pixel size of structural elements
    structure_opacity: float = 0.7

    # Detail layer
    detail_type: str = "none"  # none, dots, lines, crosses, zigzag
    detail_color: Tuple[int, int, int] = (255, 255, 255)
    detail_density: float = 0.3  # 0-1, fraction of cells with detail
    detail_scale: int = 4

    # Motif layer
    motif_names: List[str] = field(default_factory=list)
    motif_placement: str = "center"  # center, grid, scatter, border
    motif_scale: int = 1

    # Symbol layer
    symbol_type: str = "none"  # none, clan_mark, spirit_sign, totem
    symbol_placement: str = "center"
    symbol_scale: int = 1

    # Border
    border_style: str = "solid"
    border_color: Tuple[int, int, int] = (0, 0, 0)
    border_width: int = 6

    # Color palette
    palette_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    dominant_color: Tuple[int, int, int] = (0, 0, 0)
    accent_colors: List[Tuple[int, int, int]] = field(default_factory=list)

    # Derived
    complexity: float = 0.5
    symmetry: str = "none"  # none, horizontal, vertical, radial, both


class WeavingEngine(ABC):
    """Base class for tribe-specific weaving engines."""

    def __init__(self, community: str, grid_size: int = 100):
        self.community = community
        self.grid_size = grid_size
        self._palette = get_all_colors(community)
        self._primary = get_primary_colors(community)
        self._secondary = get_secondary_colors(community)

    @abstractmethod
    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        """Generate weaving parameters from DNA features."""
        pass

    @abstractmethod
    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        """Render the background layer."""
        pass

    @abstractmethod
    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        """Render the structural layer."""
        pass

    @abstractmethod
    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        """Render the detail layer."""
        pass

    def compose(self, features: DNAFeatures) -> np.ndarray:
        """Full composition pipeline for this tribe."""
        params = self.generate_params(features)
        bg = self.render_background(params, features)
        struct = self.render_structure(params, features)
        detail = self.render_detail(params, features)

        # Composite layers
        result = bg.copy()
        result = self._blend(result, struct, params.structure_opacity, params.blend_mode if hasattr(params, 'blend_mode') else 'over')
        result = self._blend(result, detail, 0.5, 'over')

        return result

    def _blend(self, base: np.ndarray, overlay: np.ndarray, opacity: float, mode: str) -> np.ndarray:
        """Blend two layers."""
        if mode == "multiply":
            blended = (base.astype(np.float32) * overlay.astype(np.float32) / 255.0)
        elif mode == "screen":
            blended = 255 - (255 - base.astype(np.float32)) * (255 - overlay.astype(np.float32)) / 255.0
        elif mode == "overlay":
            mask = base.astype(np.float32) < 128
            blended = np.where(mask,
                              2 * base * overlay / 255.0,
                              255 - 2 * (255 - base) * (255 - overlay) / 255.0)
        else:  # over (alpha blend)
            blended = base.astype(np.float32) * (1 - opacity) + overlay.astype(np.float32) * opacity

        return np.clip(blended, 0, 255).astype(np.uint8)

    def _select_colors(self, count: int, features: DNAFeatures) -> List[Tuple[int, int, int]]:
        """Select colors from palette based on DNA features."""
        if not self._palette:
            return [(0, 0, 0)] * count
        # Use GC content to bias color selection
        gc = features.gc_content
        indices = []
        for i in range(count):
            # Spread across palette, biased by GC
            pos = (i / max(count, 1)) * len(self._palette)
            pos += (gc - 0.5) * len(self._palette) * 0.3  # GC bias
            idx = int(pos) % len(self._palette)
            indices.append(idx)
        return [self._palette[i] for i in indices]


# ── Karen Engine ───────────────────────────────────────────

class KarenEngine(WeavingEngine):
    """
    Karen weaving: weft-faced stripes.
    Horizontal bands of color, each band driven by a chunk of DNA.
    Geometric motifs (diamonds, zigzags) embroidered on top.
    """

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = self._primary[0] if self._primary else (0, 0, 0)
        params.bg_pattern = "solid"

        # Structure: horizontal stripes — each stripe = chunk of sequence
        num_stripes = max(3, int(features.complexity_score * 12))
        params.structure_type = "stripes"
        params.structure_scale = max(3, self.grid_size // num_stripes)

        # Colors from DNA base frequencies
        color_count = min(4 + int(features.gc_content * 4), len(self._palette))
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = params.palette_colors[0]

        # Detail: geometric embroidery (diamonds, crosses)
        params.detail_type = "diamonds" if features.symmetry_score > 0.4 else "crosses"
        params.detail_density = 0.2 + features.rhythm_score * 0.4
        params.detail_scale = max(2, 6 - int(features.complexity_score * 3))

        # Motif: spirit diamonds, clan marks
        params.motif_placement = "grid"
        params.motif_scale = 1

        # Border: double red stripe
        params.border_style = "double"
        params.border_color = (139, 0, 0)
        params.border_width = 6

        params.complexity = features.complexity_score
        params.symmetry = "horizontal"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)
        # Subtle vertical texture (warp threads visible)
        texture = np.random.RandomState(42).randint(0, 15, (self.grid_size, self.grid_size))
        texture = np.stack([texture] * 3, axis=-1)
        grid = np.clip(grid.astype(np.int16) + texture - 7, 0, 255).astype(np.uint8)
        return grid

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        stripe_h = params.structure_scale
        colors = params.palette_colors
        seq = features.sequence

        # Each stripe gets a color based on DNA chunk
        chunk_size = max(1, len(seq) // (self.grid_size // max(stripe_h, 1)))
        stripe_idx = 0
        for r in range(0, self.grid_size, stripe_h):
            end_r = min(r + stripe_h, self.grid_size)
            # Color from DNA chunk
            chunk = seq[stripe_idx * chunk_size:(stripe_idx + 1) * chunk_size]
            if chunk:
                dominant = max(set(chunk), key=chunk.count)
                color_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[dominant] % len(colors)
            else:
                color_idx = stripe_idx % len(colors)
            grid[r:end_r, :, :] = colors[color_idx]
            stripe_idx += 1

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        alpha = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)

        detail_color = params.palette_colors[1] if len(params.palette_colors) > 1 else (255, 255, 255)
        scale = params.detail_scale
        density = params.detail_density

        seq = features.sequence

        if params.detail_type == "diamonds":
            for r in range(scale, self.grid_size - scale, scale * 2):
                for c in range(scale, self.grid_size - scale, scale * 2):
                    idx = (r * self.grid_size + c) % max(len(seq), 1)
                    if seq[idx] in "AG" and random.random() < density:
                        self._draw_diamond(grid, alpha, r, c, scale, detail_color)

        elif params.detail_type == "crosses":
            for r in range(scale, self.grid_size - scale, scale * 2):
                for c in range(scale, self.grid_size - scale, scale * 2):
                    idx = (r * self.grid_size + c) % max(len(seq), 1)
                    if seq[idx] in "TC" and random.random() < density:
                        self._draw_cross(grid, alpha, r, c, scale, detail_color)

        elif params.detail_type == "zigzag":
            for r in range(0, self.grid_size, scale * 4):
                for c in range(0, self.grid_size, scale):
                    phase = (c // scale) % 4
                    offset = scale if phase < 2 else -scale
                    pr, pc = r + offset, c
                    if 0 <= pr < self.grid_size:
                        grid[pr, pc] = detail_color
                        alpha[pr, pc] = 1.0

        return grid

    def _draw_diamond(self, grid, alpha, cy, cx, size, color):
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if abs(dy) + abs(dx) <= size:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                        grid[py, px] = color
                        alpha[py, px] = 1.0

    def _draw_cross(self, grid, alpha, cy, cx, size, color):
        for i in range(-size, size + 1):
            for j in range(-size // 2, size // 2 + 1):
                py1, px1 = cy + i, cx + j
                py2, px2 = cy + j, cx + i
                if 0 <= py1 < self.grid_size and 0 <= px1 < self.grid_size:
                    grid[py1, px1] = color
                    alpha[py1, px1] = 1.0
                if 0 <= py2 < self.grid_size and 0 <= px2 < self.grid_size:
                    grid[py2, px2] = color
                    alpha[py2, px2] = 1.0


# ── Hmong Engine ──────────────────────────────────────────

class HmongEngine(WeavingEngine):
    """
    Hmong weaving: reverse appliqué (pau kuam) + embroidery.
    Layered fabric patches with embroidered geometric symbols.
    Bright, contrasting colors.
    """

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = self._primary[0] if self._primary else (0, 0, 128)
        params.bg_pattern = "solid"

        # Structure: layered patches (like appliqué layers)
        params.structure_type = "patches"
        num_patches = max(2, int(features.complexity_score * 6))
        params.structure_scale = max(8, self.grid_size // num_patches)

        # Colors: bright, high contrast
        color_count = min(5 + int(features.complexity_score * 3), len(self._palette))
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = params.palette_colors[0]

        # Detail: embroidery stitches (cross-stitch, chain-stitch)
        params.detail_type = "stitches"
        params.detail_density = 0.3 + features.rhythm_score * 0.5
        params.detail_scale = max(2, 5 - int(features.complexity_score * 2))

        # Motif: flower carpet (tom qeej), snail patterns
        params.motif_placement = "scatter"
        params.motif_scale = 1

        # Border: zigzag (Hmong signature)
        params.border_style = "zigzag"
        params.border_color = (255, 255, 255)
        params.border_width = 4

        params.complexity = features.complexity_score
        params.symmetry = "both" if features.symmetry_score > 0.5 else "none"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        return np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        alpha = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        colors = params.palette_colors
        seq = features.sequence

        # Layered patches — like reverse appliqué
        patch_size = params.structure_scale
        patch_idx = 0
        for r in range(0, self.grid_size, patch_size):
            for c in range(0, self.grid_size, patch_size):
                # Each patch color from DNA
                chunk_start = patch_idx * 4 % len(seq)
                chunk = seq[chunk_start:chunk_start + 4]
                gc = chunk.count("G") + chunk.count("C")
                color_idx = gc % len(colors)
                color = colors[color_idx]

                # Patch shape varies: square, diamond, triangle
                shape_idx = hash(chunk) % 3
                end_r = min(r + patch_size, self.grid_size)
                end_c = min(c + patch_size, self.grid_size)

                if shape_idx == 0:  # Square
                    grid[r:end_r, c:end_c] = color
                    alpha[r:end_r, c:end_c] = 0.8
                elif shape_idx == 1:  # Diamond
                    cy, cx = (r + end_r) // 2, (c + end_c) // 2
                    half = patch_size // 2
                    for dy in range(-half, half + 1):
                        for dx in range(-half, half + 1):
                            if abs(dy) + abs(dx) <= half:
                                py, px = cy + dy, cx + dx
                                if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                                    grid[py, px] = color
                                    alpha[py, px] = 0.8
                else:  # Triangle
                    for dy in range(end_r - r):
                        width = int((dy + 1) / (end_r - r) * (end_c - c))
                        for dx in range(width):
                            py, px = r + dy, c + dx
                            if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                                grid[py, px] = color
                                alpha[py, px] = 0.8

                patch_idx += 1

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.detail_scale
        density = params.detail_density
        color = params.palette_colors[1] if len(params.palette_colors) > 1 else (255, 255, 255)

        # Cross-stitch embroidery pattern
        step = scale * 2
        for r in range(0, self.grid_size, step):
            for c in range(0, self.grid_size, step):
                idx = (r * self.grid_size + c) % len(seq)
                base = seq[idx]
                if random.random() < density:
                    if base == "A":
                        self._draw_x_stitch(grid, r, c, scale, color)
                    elif base == "T":
                        self._draw_square_stitch(grid, r, c, scale, color)
                    elif base == "G":
                        self._draw_dot_stitch(grid, r, c, scale, color)
                    else:  # C
                        self._draw_line_stitch(grid, r, c, scale, color)

        return grid

    def _draw_x_stitch(self, grid, r, c, size, color):
        for i in range(-size, size + 1):
            if 0 <= r + i < self.grid_size and 0 <= c + i < self.grid_size:
                grid[r + i, c + i] = color
            if 0 <= r + i < self.grid_size and 0 <= c - i < self.grid_size:
                grid[r + i, c - i] = color

    def _draw_square_stitch(self, grid, r, c, size, color):
        for i in range(-size, size + 1):
            for j in range(-size, size + 1):
                if abs(i) == size or abs(j) == size:
                    py, px = r + i, c + j
                    if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                        grid[py, px] = color

    def _draw_dot_stitch(self, grid, r, c, size, color):
        for dy in range(-size // 2, size // 2 + 1):
            for dx in range(-size // 2, size // 2 + 1):
                py, px = r + dy, c + dx
                if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                    grid[py, px] = color

    def _draw_line_stitch(self, grid, r, c, size, color):
        for i in range(-size, size + 1):
            if 0 <= r < self.grid_size and 0 <= c + i < self.grid_size:
                grid[r, c + i] = color


# ── Thai Lue Engine ───────────────────────────────────────

class ThaiLueEngine(WeavingEngine):
    """
    Thai Lue: supplementary weft (jin/jok) patterning.
    Buddhist motifs, naga serpents, lotus patterns.
    Rich colors with gold accents.
    """

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = (139, 0, 0)  # Deep red base
        params.bg_pattern = "stripes"

        # Structure: horizontal warp stripes with supplementary weft blocks
        params.structure_type = "jok_blocks"
        params.structure_scale = max(6, self.grid_size // 10)

        color_count = min(6 + int(features.gc_content * 4), len(self._palette))
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = (139, 0, 0)

        # Detail: supplementary weft threads
        params.detail_type = "supplementary_weft"
        params.detail_density = 0.4 + features.complexity_score * 0.4
        params.detail_scale = 3

        # Motif: naga, lotus, mount meru
        params.motif_placement = "center"
        params.motif_scale = 2

        # Border: gold lai kham pattern
        params.border_style = "solid"
        params.border_color = (255, 215, 0)
        params.border_width = 8

        params.complexity = features.complexity_score
        params.symmetry = "radial" if features.symmetry_score > 0.5 else "vertical"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)
        # Subtle horizontal stripe texture (warp threads)
        stripe_h = 2
        for r in range(0, self.grid_size, stripe_h * 2):
            end = min(r + stripe_h, self.grid_size)
            grid[r:end, :, :] = np.clip(
                np.array(params.bg_color) + 20, 0, 255
            ).astype(np.uint8)
        return grid

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        colors = params.palette_colors
        seq = features.sequence

        # Jok blocks: rectangular pattern areas (supplementary weft)
        block_h = params.structure_scale
        block_w = block_h * 2
        block_idx = 0

        for r in range(0, self.grid_size, block_h * 3):
            for c in range(0, self.grid_size, block_w * 2):
                # Block presence and color from DNA
                chunk_start = block_idx * 8 % len(seq)
                chunk = seq[chunk_start:chunk_start + 8]
                gc_content = (chunk.count("G") + chunk.count("C")) / max(len(chunk), 1)

                if gc_content > 0.3:  # Only some blocks appear
                    end_r = min(r + block_h, self.grid_size)
                    end_c = min(c + block_w, self.grid_size)
                    color_idx = int(gc_content * (len(colors) - 1))
                    color = colors[min(color_idx, len(colors) - 1)]
                    grid[r:end_r, c:end_c] = color
                block_idx += 1

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.detail_scale
        density = params.detail_density
        color = (255, 215, 0)  # Gold

        # Supplementary weft: horizontal threads with pattern
        for r in range(0, self.grid_size, scale * 2):
            for c in range(0, self.grid_size, scale):
                idx = (r * self.grid_size + c) % len(seq)
                if seq[idx] in "GC" and random.random() < density:
                    # Horizontal thread segment
                    for dx in range(scale):
                        px = c + dx
                        if 0 <= px < self.grid_size:
                            grid[r, px] = color
                    # Vertical connector
                    if random.random() < 0.3:
                        for dy in range(scale):
                            py = r + dy
                            if 0 <= py < self.grid_size:
                                grid[py, c] = color

        return grid


# ── Tai Dam Engine ────────────────────────────────────────

class TaiDamEngine(WeavingEngine):
    """
    Tai Dam (Black Tai): indigo reserve dyeing.
    Black base with silver/gold accents.
    Clan symbols and spirit motifs.
    """

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = (0, 0, 0)  # Black base
        params.bg_pattern = "solid"

        # Structure: resist pattern (like tie-dye but geometric)
        params.structure_type = "resist"
        params.structure_scale = max(5, self.grid_size // 15)

        color_count = min(4 + int(features.complexity_score * 3), len(self._palette))
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = (0, 0, 0)

        # Detail: silver thread patterns
        params.detail_type = "silver_threads"
        params.detail_density = 0.2 + features.rhythm_score * 0.4
        params.detail_scale = 3

        # Motif: clan diamonds, soul butterflies
        params.motif_placement = "grid"
        params.motif_scale = 1

        # Border: silver thread
        params.border_style = "solid"
        params.border_color = (192, 192, 192)
        params.border_width = 6

        params.complexity = features.complexity_score
        params.symmetry = "both"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)
        # Subtle texture
        noise = np.random.RandomState(123).randint(0, 10, (self.grid_size, self.grid_size))
        noise = np.stack([noise] * 3, axis=-1)
        return np.clip(grid.astype(np.int16) + noise - 5, 0, 255).astype(np.uint8)

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.structure_scale
        colors = params.palette_colors

        # Resist pattern: geometric shapes where dye was blocked
        # Based on DNA palindrome locations
        for motif_seq, start, length in features.palindromes[:8]:
            cy = (start * self.grid_size) % self.grid_size
            cx = (start * 7) % self.grid_size
            size = min(length, scale * 2)

            color_idx = start % len(colors)
            color = colors[color_idx]

            # Diamond resist shape
            for dy in range(-size, size + 1):
                for dx in range(-size, size + 1):
                    if abs(dy) + abs(dx) <= size:
                        py, px = cy + dy, cx + dx
                        if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                            grid[py, px] = color

        # Also add some circular resist patterns from homopolymers
        for base, start, length in features.homopolymer_runs[:5]:
            cy = (start * 3) % self.grid_size
            cx = (start * 11) % self.grid_size
            radius = min(length, scale)

            color_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[base] % len(colors)
            color = colors[color_idx]

            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dy * dy + dx * dx <= radius * radius:
                        py, px = cy + dy, cx + dx
                        if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                            grid[py, px] = color

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.detail_scale
        density = params.detail_density
        color = (192, 192, 192)  # Silver

        # Silver thread: fine linear patterns
        for r in range(0, self.grid_size, scale * 3):
            for c in range(0, self.grid_size, scale):
                idx = (r + c) % len(seq)
                if seq[idx] in "AT" and random.random() < density:
                    # Horizontal silver thread
                    for dx in range(scale):
                        px = c + dx
                        if 0 <= px < self.grid_size:
                            grid[r, px] = color
                    # Vertical cross
                    if random.random() < 0.4:
                        for dy in range(scale):
                            py = r + dy
                            if 0 <= py < self.grid_size:
                                grid[py, c] = color

        return grid


# ── Lisu Engine ───────────────────────────────────────────

class LisuEngine(WeavingEngine):
    """
    Lisu: bold color-block weaving.
    Vertical stripes with bright, saturated colors.
    """

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = (255, 0, 0)  # Red base
        params.bg_pattern = "solid"

        # Structure: vertical color blocks
        params.structure_type = "vblocks"
        num_blocks = max(3, int(features.complexity_score * 8))
        params.structure_scale = max(4, self.grid_size // num_blocks)

        color_count = min(6 + int(features.complexity_score * 3), len(self._palette))
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = params.palette_colors[0]

        # Detail: horizontal accent lines
        params.detail_type = "hlines"
        params.detail_density = 0.5
        params.detail_scale = 2

        # Border: multi-stripe
        params.border_style = "striped"
        params.border_color = (255, 140, 0)
        params.border_width = 8

        params.complexity = features.complexity_score
        params.symmetry = "vertical"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        return np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        colors = params.palette_colors
        seq = features.sequence
        block_w = params.structure_scale

        block_idx = 0
        for c in range(0, self.grid_size, block_w):
            end_c = min(c + block_w, self.grid_size)
            chunk_start = block_idx * 6 % len(seq)
            chunk = seq[chunk_start:chunk_start + 6]
            gc = (chunk.count("G") + chunk.count("C")) / max(len(chunk), 1)
            color_idx = int(gc * (len(colors) - 1))
            color = colors[min(color_idx, len(colors) - 1)]
            grid[:, c:end_c] = color
            block_idx += 1

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.detail_scale
        color = (255, 255, 255)

        # Horizontal accent lines at DNA-driven intervals
        for r in range(0, self.grid_size, scale * 4):
            idx = r % len(seq)
            if seq[idx] in "GC":
                for dy in range(scale):
                    pr = r + dy
                    if 0 <= pr < self.grid_size:
                        grid[pr, :] = color

        return grid


# ── Mien Engine ───────────────────────────────────────────

class MienEngine(WeavingEngine):
    """
    Mien (Yao): cross-stitch embroidery on dark fabric.
    Counted-stitch patterns with imperial motifs.
    """

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = (0, 0, 128)  # Indigo base
        params.bg_pattern = "solid"

        # Structure: counted stitch grid
        params.structure_type = "stitch_grid"
        params.structure_scale = max(3, 8 - int(features.complexity_score * 4))

        color_count = min(5 + int(features.gc_content * 3), len(self._palette))
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = (139, 0, 0)

        # Detail: cross-stitch patterns
        params.detail_type = "cross_stitch"
        params.detail_density = 0.4 + features.rhythm_score * 0.4
        params.detail_scale = params.structure_scale

        # Border: gold trim
        params.border_style = "solid"
        params.border_color = (255, 215, 0)
        params.border_width = 6

        params.complexity = features.complexity_score
        params.symmetry = "both"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        return np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.structure_scale
        colors = params.palette_colors

        # Counted stitch grid: each stitch = one DNA base
        for r in range(0, self.grid_size, scale * 2):
            for c in range(0, self.grid_size, scale * 2):
                idx = ((r // (scale * 2)) * (self.grid_size // (scale * 2)) +
                       c // (scale * 2)) % len(seq)
                base = seq[idx]
                color_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[base] % len(colors)
                color = colors[color_idx]

                # Draw cross stitch
                for dy in range(-scale // 2, scale // 2 + 1):
                    for dx in range(-scale // 2, scale // 2 + 1):
                        py, px = r + dy, c + dx
                        if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                            grid[py, px] = color

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.detail_scale
        density = params.detail_density
        color = (255, 215, 0)  # Gold

        # Additional gold cross-stitches
        for r in range(scale, self.grid_size - scale, scale * 3):
            for c in range(scale, self.grid_size - scale, scale * 3):
                idx = (r + c) % len(seq)
                if seq[idx] == "A" and random.random() < density:
                    for dy in range(-scale, scale + 1):
                        for dx in range(-scale, scale + 1):
                            if abs(dy) + abs(dx) <= scale:
                                py, px = r + dy, c + dx
                                if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                                    grid[py, px] = color

        return grid


# ── Akha Engine ───────────────────────────────────────────

class AkhaEngine(WeavingEngine):
    """
    Akha: beaded weaving with silver coins.
    Dark base with silver/gold dot patterns.
    """

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = (0, 0, 0)
        params.bg_pattern = "solid"

        # Structure: bead grid
        params.structure_type = "beads"
        params.structure_scale = max(2, 5 - int(features.complexity_score * 2))

        color_count = min(5 + int(features.complexity_score * 3), len(self._palette))
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = (0, 0, 0)

        # Detail: silver coin circles
        params.detail_type = "coin_circles"
        params.detail_density = 0.15 + features.rhythm_score * 0.3
        params.detail_scale = 4

        # Border: bead pattern
        params.border_style = "solid"
        params.border_color = (192, 192, 192)
        params.border_width = 6

        params.complexity = features.complexity_score
        params.symmetry = "both"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        return np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.structure_scale
        colors = params.palette_colors

        # Bead grid
        for r in range(0, self.grid_size, scale * 2):
            for c in range(0, self.grid_size, scale * 2):
                idx = ((r * self.grid_size + c) // (scale * 2)) % len(seq)
                base = seq[idx]
                color_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[base] % len(colors)
                color = colors[color_idx]

                # Circular bead
                for dy in range(-scale // 2, scale // 2 + 1):
                    for dx in range(-scale // 2, scale // 2 + 1):
                        if dy * dy + dx * dx <= (scale // 2) ** 2 + 1:
                            py, px = r + dy, c + dx
                            if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                                grid[py, px] = color

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        seq = features.sequence
        scale = params.detail_scale
        density = params.detail_density
        color = (192, 192, 192)  # Silver

        # Silver coin circles at DNA-driven positions
        for i, (base, start, length) in enumerate(features.homopolymer_runs[:10]):
            cy = (start * 5) % self.grid_size
            cx = (start * 13) % self.grid_size
            radius = min(length, scale)

            if random.random() < density:
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if dy * dy + dx * dx <= radius * radius:
                            py, px = cy + dy, cx + dx
                            if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                                grid[py, px] = color

        return grid


# ── Generic/Fallback Engine ───────────────────────────────

class GenericEngine(WeavingEngine):
    """Generic weaving engine for communities without specific logic."""

    def generate_params(self, features: DNAFeatures) -> WeavingParams:
        params = WeavingParams()
        params.bg_color = (0, 0, 0)
        params.bg_pattern = "solid"
        params.structure_type = "grid"
        params.structure_scale = max(4, self.grid_size // 10)

        color_count = min(4, len(self._palette)) if self._palette else 4
        params.palette_colors = self._select_colors(color_count, features)
        params.dominant_color = params.palette_colors[0] if params.palette_colors else (0, 0, 0)

        params.detail_type = "dots"
        params.detail_density = 0.3
        params.detail_scale = 3

        params.border_style = "solid"
        params.border_color = (128, 128, 128)
        params.border_width = 4

        params.complexity = features.complexity_score
        params.symmetry = "none"

        return params

    def render_background(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        return np.full((self.grid_size, self.grid_size, 3), params.bg_color, dtype=np.uint8)

    def render_structure(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        colors = params.palette_colors
        seq = features.sequence
        scale = params.structure_scale

        for r in range(0, self.grid_size, scale):
            for c in range(0, self.grid_size, scale):
                idx = ((r * self.grid_size + c) // scale) % len(seq)
                base = seq[idx]
                color_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[base] % len(colors)
                end_r = min(r + scale, self.grid_size)
                end_c = min(c + scale, self.grid_size)
                grid[end_r if end_r > r else r:end_r, end_c if end_c > c else c:end_c] = colors[color_idx]

        return grid

    def render_detail(self, params: WeavingParams, features: DNAFeatures) -> np.ndarray:
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        return grid


# ── Engine Registry ───────────────────────────────────────

ENGINE_REGISTRY: Dict[str, type] = {
    "karen": KarenEngine,
    "hmong": HmongEngine,
    "thai_lue": ThaiLueEngine,
    "tai_dam": TaiDamEngine,
    "lisu": LisuEngine,
    "mien": MienEngine,
    "akha": AkhaEngine,
}


def get_engine(community: str, grid_size: int = 100) -> WeavingEngine:
    """Get the appropriate weaving engine for a community."""
    key = community.lower().replace(" ", "_")
    engine_class = ENGINE_REGISTRY.get(key, GenericEngine)
    return engine_class(community, grid_size)


def list_engines() -> List[str]:
    """List all available weaving engines."""
    return list(ENGINE_REGISTRY.keys())
