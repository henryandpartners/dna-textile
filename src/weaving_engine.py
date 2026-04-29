"""Tribe Weaving Engine — 7 tribe-specific textile technique engines.

Phase 3: Each engine implements actual weaving/embroidery techniques:
- Karen (Kayah): Supplementary weft stripes, diamond/cross motifs
- Hmong: Patchwork embroidery, X-stitch/square/dot/line stitches
- Thai Lue: Jok supplementary weft, gold thread patterns
- Tai Dam: Indigo reserve dyeing, resist patterns
- Lisu: Vertical stripe blocks, bead patterns
- Mien: Cross-stitch embroidery, silver thread accents
- Akha: Beadwork patterns, silver coin motifs

Each engine takes DNA features + palette and returns layer specifications.
"""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ── Layer Spec ─────────────────────────────────────────────

@dataclass
class LayerSpec:
    """Specification for a single weaving layer."""
    layer_name: str
    grid: np.ndarray  # (H, W, 3) uint8
    alpha: np.ndarray | None = None  # optional alpha mask (H, W) uint8
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Helper: pick color from palette by index ──────────────

def _pick_color(palette: List[Tuple[int, int, int]], index: int) -> Tuple[int, int, int]:
    if not palette:
        return (0, 0, 0)
    return palette[index % len(palette)]


def _blend(base: np.ndarray, overlay: np.ndarray, alpha: Optional[np.ndarray] = None) -> np.ndarray:
    """Alpha-blend overlay onto base."""
    if overlay.shape != base.shape:
        return base
    if alpha is None:
        # Use luminance of overlay as alpha
        lum = 0.299 * overlay[:, :, 0].astype(np.float32) + \
              0.587 * overlay[:, :, 1].astype(np.float32) + \
              0.114 * overlay[:, :, 2].astype(np.float32)
        alpha = (lum / 255.0).astype(np.float32)
    a = alpha[:, :, np.newaxis].astype(np.float32)
    result = base.astype(np.float32) * (1 - a) + overlay.astype(np.float32) * a
    return np.clip(result, 0, 255).astype(np.uint8)


# ── Base Engine ────────────────────────────────────────────

class WeavingEngine(ABC):
    """Abstract base for tribe-specific weaving engines."""

    def __init__(self, name: str, palette: List[Tuple[int, int, int]]):
        self.name = name
        self.palette = palette

    @abstractmethod
    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        """Generate background layer."""
        ...

    @abstractmethod
    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        """Generate structure layer (stripes/patches/resist/etc)."""
        ...

    @abstractmethod
    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        """Generate detail layer (stitches/threads/etc)."""
        ...

    def _empty_layer(self, size: int) -> LayerSpec:
        return LayerSpec(
            layer_name="empty",
            grid=np.zeros((size, size, 3), dtype=np.uint8),
        )


# ── Karen (Kayah) Engine ──────────────────────────────────

class KarenEngine(WeavingEngine):
    """Supplementary weft stripes with diamond/cross motifs.

    Traditional technique: extra weft threads create geometric patterns
    on a dark background.
    """

    def __init__(self, palette: List[Tuple[int, int, int]]):
        super().__init__("Karen (Kayah)", palette)

    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed)
        # Dark base (black or deep red)
        bg_color = _pick_color(self.palette, 0)
        grid = np.full((size, size, 3), bg_color, dtype=np.uint8)
        # Subtle texture from DNA
        gc = features.get("gc_content", 0.5)
        texture_color = _pick_color(self.palette, 1)
        for r in range(size):
            for c in range(size):
                if random.random() < gc * 0.3:
                    grid[r, c] = texture_color
        return LayerSpec("karen_background", grid, metadata={"technique": "supplementary_weft"})

    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 1)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Horizontal supplementary weft stripes
        stripe_colors = [self.palette[i % len(self.palette)] for i in range(4)]
        stripe_height = max(2, size // 20)
        base = features.get("base_composition", {})
        dominant = max(base, key=base.get) if base else "A"
        # A→red stripes, T→white, G→brown, C→gold
        color_map = {"A": 0, "T": 1, "G": 2, "C": 3}
        stripe_idx = color_map.get(dominant, 0)
        y = 0
        while y < size:
            h = stripe_height + random.randint(-2, 2)
            h = max(1, min(h, size - y))
            color = stripe_colors[stripe_idx % len(stripe_colors)]
            grid[y:y+h, :, :] = color
            stripe_idx += 1
            y += h + random.randint(1, 3)
        return LayerSpec("karen_structure", grid, metadata={"technique": "supplementary_weft_stripes"})

    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 2)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Diamond and cross motifs
        motif_color = _pick_color(self.palette, 6)  # gold accent
        diamond_color = _pick_color(self.palette, 7)  # silver
        spacing = max(8, size // 12)
        for r in range(spacing, size - spacing, spacing):
            for c in range(spacing, size - spacing, spacing):
                if random.random() < 0.4:
                    self._draw_diamond(grid, r, c, 3, motif_color)
                elif random.random() < 0.3:
                    self._draw_cross(grid, r, c, 2, diamond_color)
        return LayerSpec("karen_detail", grid, metadata={"technique": "diamond_cross_motifs"})

    @staticmethod
    def _draw_diamond(grid: np.ndarray, cy: int, cx: int, radius: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if abs(dx) + abs(dy) <= radius:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color

    @staticmethod
    def _draw_cross(grid: np.ndarray, cy: int, cx: int, arm: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for i in range(-arm, arm + 1):
            for j in range(-arm, arm + 1):
                if abs(i) <= 1 or abs(j) <= 1:
                    ny, nx = cy + i, cx + j
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color


# ── Hmong Engine ──────────────────────────────────────────

class HmongEngine(WeavingEngine):
    """Patchwork embroidery with X-stitch, square, dot, and line stitches.

    Traditional technique: reverse appliqué and embroidery on indigo cloth.
    """

    def __init__(self, palette: List[Tuple[int, int, int]]):
        super().__init__("Hmong", palette)

    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed)
        # Indigo background
        bg_color = _pick_color(self.palette, 0)
        grid = np.full((size, size, 3), bg_color, dtype=np.uint8)
        # Patchwork blocks
        block_size = max(4, size // 16)
        for r in range(0, size, block_size):
            for c in range(0, size, block_size):
                if random.random() < 0.15:
                    color = _pick_color(self.palette, random.randint(1, len(self.palette) - 1))
                    end_r = min(r + block_size, size)
                    end_c = min(c + block_size, size)
                    grid[r:end_r, c:end_c] = color
        return LayerSpec("hmong_background", grid, metadata={"technique": "patchwork_indigo"})

    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 1)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Geometric bands from DNA features
        gc = features.get("gc_content", 0.5)
        band_count = max(3, int(gc * 12))
        band_height = max(2, size // (band_count * 2))
        for i in range(band_count):
            y = (i * 2 + 1) * band_height
            color = _pick_color(self.palette, (i + 1) % len(self.palette))
            if y + band_height <= size:
                grid[y:y+band_height, :, :] = color
        return LayerSpec("hmong_structure", grid, metadata={"technique": "embroidery_bands"})

    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 2)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # X-stitches scattered across the pattern
        stitch_color = _pick_color(self.palette, 3)  # red
        spacing = max(6, size // 16)
        for r in range(spacing, size - spacing, spacing):
            for c in range(spacing, size - spacing, spacing):
                if random.random() < 0.5:
                    self._draw_x_stitch(grid, r, c, 2, stitch_color)
                elif random.random() < 0.3:
                    self._draw_square_stitch(grid, r, c, 2, _pick_color(self.palette, 4))
        return LayerSpec("hmong_detail", grid, metadata={"technique": "x_stitch_embroidery"})

    @staticmethod
    def _draw_x_stitch(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if abs(dx) == abs(dy):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color

    @staticmethod
    def _draw_square_stitch(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if abs(dy) == size or abs(dx) == size:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color


# ── Thai Lue Engine ───────────────────────────────────────

class ThaiLueEngine(WeavingEngine):
    """Jok supplementary weft with gold thread patterns.

    Traditional technique: discontinuous supplementary weft creating
    elaborate geometric and figurative motifs on indigo ground.
    """

    def __init__(self, palette: List[Tuple[int, int, int]]):
        super().__init__("Thai Lue", palette)

    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed)
        # Navy/indigo background
        bg_color = _pick_color(self.palette, 1)
        grid = np.full((size, size, 3), bg_color, dtype=np.uint8)
        # Subtle warp texture
        for c in range(size):
            shade = random.randint(-15, 15)
            r = max(0, min(255, bg_color[0] + shade))
            g = max(0, min(255, bg_color[1] + shade))
            b = max(0, min(255, bg_color[2] + shade))
            grid[:, c] = (r, g, b)
        return LayerSpec("thai_lue_background", grid, metadata={"technique": "indigo_ground"})

    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 1)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Jok supplementary weft bands
        gc = features.get("gc_content", 0.5)
        band_positions = [int(size * gc * 0.5), int(size * 0.5), int(size * (0.5 + gc * 0.5))]
        band_height = max(3, size // 15)
        for pos in band_positions:
            if 0 <= pos < size:
                color = _pick_color(self.palette, 2)  # gold
                end = min(pos + band_height, size)
                grid[pos:end, :, :] = color
                # Secondary band
                if pos - band_height > 0:
                    grid[pos - band_height:pos, :, :] = _pick_color(self.palette, 0)  # deep red
        return LayerSpec("thai_lue_structure", grid, metadata={"technique": "jok_supplementary_weft"})

    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 2)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Gold thread patterns and temple motifs
        gold = _pick_color(self.palette, 2)
        silver = _pick_color(self.palette, 8)
        spacing = max(8, size // 14)
        for r in range(spacing, size - spacing, spacing):
            for c in range(spacing, size - spacing, spacing):
                if random.random() < 0.35:
                    self._draw_lai_kham(grid, r, c, 3, gold)
                elif random.random() < 0.25:
                    self._draw_small_diamond(grid, r, c, 2, silver)
        return LayerSpec("thai_lue_detail", grid, metadata={"technique": "gold_thread_lai_kham"})

    @staticmethod
    def _draw_lai_kham(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
        """Draw a small Lai Kham (gold pattern) motif."""
        h, w = grid.shape[:2]
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                dist = math.sqrt(dx*dx + dy*dy)
                if size - 1 <= dist <= size + 0.5:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color

    @staticmethod
    def _draw_small_diamond(grid: np.ndarray, cy: int, cx: int, radius: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if abs(dx) + abs(dy) <= radius:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color


# ── Tai Dam Engine ────────────────────────────────────────

class TaiDamEngine(WeavingEngine):
    """Indigo reserve dyeing with resist patterns.

    Traditional technique: black cloth with resist-dyed patterns,
    silver thread accents.
    """

    def __init__(self, palette: List[Tuple[int, int, int]]):
        super().__init__("Tai Dam", palette)

    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed)
        # Black background (identity color)
        bg_color = _pick_color(self.palette, 0)
        grid = np.full((size, size, 3), bg_color, dtype=np.uint8)
        # Subtle variation from entropy
        entropy = features.get("shannon_entropy", 1.5)
        variation = int(entropy * 8)
        for r in range(0, size, 2):
            for c in range(0, size, 2):
                shade = random.randint(-variation, variation)
                grid[r, c] = tuple(max(0, min(255, bg_color[i] + shade)) for i in range(3))
        return LayerSpec("tai_dam_background", grid, metadata={"technique": "indigo_reserve"})

    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 1)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Resist pattern: geometric blocks
        gc = features.get("gc_content", 0.5)
        block_size = max(4, int(size * 0.08))
        for r in range(0, size, block_size):
            for c in range(0, size, block_size):
                if random.random() < gc:
                    color = _pick_color(self.palette, random.choice([1, 2, 3]))  # silver, gold, red
                    end_r = min(r + block_size, size)
                    end_c = min(c + block_size, size)
                    grid[r:end_r, c:end_c] = color
        return LayerSpec("tai_dam_structure", grid, metadata={"technique": "resist_patterns"})

    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 2)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Silver thread accents in geometric lines
        silver = _pick_color(self.palette, 1)
        spacing = max(6, size // 16)
        for r in range(spacing, size - spacing, spacing):
            # Horizontal silver lines
            for c in range(0, size, 3):
                if random.random() < 0.6:
                    grid[r, c:c+2] = silver
        for c in range(spacing, size - spacing, spacing):
            # Vertical silver lines
            for r in range(0, size, 3):
                if random.random() < 0.4:
                    grid[r:r+2, c] = silver
        return LayerSpec("tai_dam_detail", grid, metadata={"technique": "silver_thread_accents"})


# ── Lisu Engine ───────────────────────────────────────────

class LisuEngine(WeavingEngine):
    """Vertical stripe blocks with bead patterns.

    Traditional technique: bold vertical color blocks with beadwork.
    """

    def __init__(self, palette: List[Tuple[int, int, int]]):
        super().__init__("Lisu", palette)

    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed)
        # Red base
        bg_color = _pick_color(self.palette, 0)
        grid = np.full((size, size, 3), bg_color, dtype=np.uint8)
        return LayerSpec("lisu_background", grid, metadata={"technique": "vertical_stripes"})

    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 1)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Vertical stripe blocks
        gc = features.get("gc_content", 0.5)
        num_blocks = max(3, int(gc * 10))
        block_width = max(2, size // num_blocks)
        for i in range(num_blocks):
            x = i * block_width
            color = _pick_color(self.palette, (i + 1) % len(self.palette))
            end_x = min(x + block_width, size)
            grid[:, x:end_x] = color
        return LayerSpec("lisu_structure", grid, metadata={"technique": "vertical_stripe_blocks"})

    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 2)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Bead patterns: small circles in rows
        bead_colors = [
            _pick_color(self.palette, 4),  # blue
            _pick_color(self.palette, 5),  # purple
            _pick_color(self.palette, 7),  # white
            _pick_color(self.palette, 8),  # hot pink
        ]
        spacing = max(6, size // 16)
        for r in range(spacing, size - spacing, spacing):
            for c in range(spacing, size - spacing, spacing):
                if random.random() < 0.5:
                    color = bead_colors[random.randint(0, len(bead_colors) - 1)]
                    self._draw_bead(grid, r, c, 2, color)
        return LayerSpec("lisu_detail", grid, metadata={"technique": "bead_patterns"})

    @staticmethod
    def _draw_bead(grid: np.ndarray, cy: int, cx: int, radius: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color


# ── Mien Engine ───────────────────────────────────────────

class MienEngine(WeavingEngine):
    """Cross-stitch embroidery with silver thread accents.

    Traditional technique: detailed cross-stitch on indigo cloth
    with silver ornament accents.
    """

    def __init__(self, palette: List[Tuple[int, int, int]]):
        super().__init__("Mien", palette)

    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed)
        # Deep red background
        bg_color = _pick_color(self.palette, 0)
        grid = np.full((size, size, 3), bg_color, dtype=np.uint8)
        return LayerSpec("mien_background", grid, metadata={"technique": "cross_stitch_base"})

    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 1)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Horizontal bands from DNA base composition
        base = features.get("base_composition", {})
        gc = features.get("gc_content", 0.5)
        num_bands = max(4, int(gc * 15))
        band_height = max(2, size // num_bands)
        for i in range(num_bands):
            y = i * band_height
            color_idx = i % len(self.palette)
            color = _pick_color(self.palette, color_idx)
            end_y = min(y + band_height, size)
            grid[y:end_y, :, :] = color
        return LayerSpec("mien_structure", grid, metadata={"technique": "embroidery_bands"})

    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 2)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Cross-stitch patterns
        stitch_color = _pick_color(self.palette, 2)  # white
        silver = _pick_color(self.palette, 4)  # silver
        spacing = max(5, size // 18)
        for r in range(spacing, size - spacing, spacing):
            for c in range(spacing, size - spacing, spacing):
                if random.random() < 0.45:
                    self._draw_cross_stitch(grid, r, c, 2, stitch_color)
                elif random.random() < 0.2:
                    self._draw_silver_line(grid, r, c, 3, silver)
        return LayerSpec("mien_detail", grid, metadata={"technique": "cross_stitch_silver"})

    @staticmethod
    def _draw_cross_stitch(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if abs(dx) == abs(dy) and dx != 0:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color
        # Center dot
        if 0 <= cy < h and 0 <= cx < w:
            grid[cy, cx] = color

    @staticmethod
    def _draw_silver_line(grid: np.ndarray, cy: int, cx: int, length: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dx in range(-length, length + 1):
            nx = cx + dx
            if 0 <= cy < h and 0 <= nx < w:
                grid[cy, nx] = color


# ── Akha Engine ───────────────────────────────────────────

class AkhaEngine(WeavingEngine):
    """Beadwork patterns with silver coin motifs.

    Traditional technique: dense beadwork on black cloth with
    silver coin decorations.
    """

    def __init__(self, palette: List[Tuple[int, int, int]]):
        super().__init__("Akha", palette)

    def generate_background(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed)
        # Black background
        bg_color = _pick_color(self.palette, 0)
        grid = np.full((size, size, 3), bg_color, dtype=np.uint8)
        return LayerSpec("akha_background", grid, metadata={"technique": "beadwork_base"})

    def generate_structure(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 1)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Horizontal beadwork bands
        gc = features.get("gc_content", 0.5)
        num_bands = max(4, int(gc * 12))
        band_height = max(3, size // num_bands)
        for i in range(num_bands):
            y = i * band_height
            # Alternate red and silver
            color = _pick_color(self.palette, 1 if i % 2 == 0 else 2)
            end_y = min(y + band_height, size)
            grid[y:end_y, :, :] = color
        return LayerSpec("akha_structure", grid, metadata={"technique": "beadwork_bands"})

    def generate_detail(self, features: Dict[str, Any], size: int, seed: int = 0) -> LayerSpec:
        random.seed(seed + 2)
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        # Beadwork dots and silver coin motifs
        bead_colors = [
            _pick_color(self.palette, 3),  # red
            _pick_color(self.palette, 4),  # gold
            _pick_color(self.palette, 5),  # white
            _pick_color(self.palette, 6),  # purple
        ]
        silver = _pick_color(self.palette, 2)
        spacing = max(6, size // 14)
        for r in range(spacing, size - spacing, spacing):
            for c in range(spacing, size - spacing, spacing):
                if random.random() < 0.5:
                    color = bead_colors[random.randint(0, len(bead_colors) - 1)]
                    self._draw_bead(grid, r, c, 2, color)
                elif random.random() < 0.15:
                    self._draw_silver_coin(grid, r, c, 3, silver)
        return LayerSpec("akha_detail", grid, metadata={"technique": "beadwork_silver_coins"})

    @staticmethod
    def _draw_bead(grid: np.ndarray, cy: int, cx: int, radius: int, color: Tuple[int, int, int]) -> None:
        h, w = grid.shape[:2]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color

    @staticmethod
    def _draw_silver_coin(grid: np.ndarray, cy: int, cx: int, radius: int, color: Tuple[int, int, int]) -> None:
        """Draw a silver coin motif (circle with center hole)."""
        h, w = grid.shape[:2]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                dist_sq = dx*dx + dy*dy
                if (radius - 1) * (radius - 1) <= dist_sq <= radius * radius:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        grid[ny, nx] = color


# ── Engine Registry ───────────────────────────────────────

_ENGINES: Dict[str, type] = {
    "karen": KarenEngine,
    "karen_kayah": KarenEngine,
    "hmong": HmongEngine,
    "thai_lue": ThaiLueEngine,
    "tai_dam": TaiDamEngine,
    "lisu": LisuEngine,
    "mien": MienEngine,
    "akha": AkhaEngine,
}


def get_engine(community: str, palette: List[Tuple[int, int, int]]) -> WeavingEngine:
    """Get the appropriate weaving engine for a community."""
    key = community.lower().replace(" ", "_")
    engine_cls = _ENGINES.get(key)
    if engine_cls is None:
        # Default to Karen-style supplementary weft
        engine_cls = KarenEngine
    return engine_cls(palette)


def list_engines() -> List[str]:
    """List all available weaving engine community keys."""
    return list(_ENGINES.keys())
