"""Procedural Motif Generator — 21 motif types + 6 symbol types.

Phase 3: All motifs generated procedurally from DNA features.
Each motif type is a function that draws onto a numpy grid.

Motifs: diamond, cross, butterfly, naga, lotus, spiral, triangle,
        circle, star, leaf, wave, zigzag, hook, eye, tooth, bird,
        fish, mountain, cloud, flame, tree
Symbols: mandala, totem, clan_shield, spirit_mask, guardian_figure,
         ancestral_pattern
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


# ── Type aliases ──────────────────────────────────────────

DrawFunc = Callable[[np.ndarray, int, int, int, Tuple[int, int, int]], None]

# ── Drawing Helpers ───────────────────────────────────────

def _in_bounds(grid: np.ndarray, y: int, x: int) -> bool:
    h, w = grid.shape[:2]
    return 0 <= y < h and 0 <= x < w


def _set(grid: np.ndarray, y: int, x: int, color: Tuple[int, int, int]) -> None:
    if _in_bounds(grid, y, x):
        grid[y, x] = color


# ── 21 Motif Types ───────────────────────────────────────

def draw_diamond(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Solid diamond shape."""
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            if abs(dx) + abs(dy) <= size:
                _set(grid, cy + dy, cx + dx, color)


def draw_cross(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Greek cross (equal arms)."""
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            if abs(dx) <= 1 or abs(dy) <= 1:
                _set(grid, cy + dy, cx + dx, color)


def draw_butterfly(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Butterfly wing pattern."""
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            # Two wing lobes
            left_dist = (dx + size // 2) ** 2 / (size * size) + dy ** 2 / (size * size * 0.6)
            right_dist = (dx - size // 2) ** 2 / (size * size) + dy ** 2 / (size * size * 0.6)
            body = abs(dx) <= 1 and abs(dy) <= size
            if left_dist <= 1 or right_dist <= 1 or body:
                _set(grid, cy + dy, cx + dx, color)


def draw_naga(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Serpentine Naga shape."""
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            # Wavy body
            wave = int(size * 0.4 * math.sin(dy * math.pi / max(size, 1)))
            body_dist = abs(dx - wave)
            if body_dist <= max(1, size // 4):
                _set(grid, cy + dy, cx + dx, color)
            # Head at top
            if dy == -size and abs(dx) <= max(1, size // 3):
                _set(grid, cy + dy, cx + dx, color)


def draw_lotus(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Lotus flower with petals."""
    num_petals = 6
    for angle_idx in range(num_petals):
        angle = angle_idx * 2 * math.pi / num_petals
        for t in range(1, size + 1):
            px = int(t * math.cos(angle))
            py = int(t * math.sin(angle))
            _set(grid, cy + py, cx + px, color)
            # Petal width
            for w in range(1, max(1, size // 4)):
                perp_angle = angle + math.pi / 2
                wx = int(w * math.cos(perp_angle))
                wy = int(w * math.sin(perp_angle))
                _set(grid, cy + py + wy, cx + px + wx, color)
    # Center
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx*dx + dy*dy <= 4:
                _set(grid, cy + dy, cx + dx, color)


def draw_spiral(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Archimedean spiral."""
    for t in range(size * 4):
        angle = t * 0.3
        r = t * size / (size * 4)
        px = int(r * math.cos(angle))
        py = int(r * math.sin(angle))
        _set(grid, cy + py, cx + px, color)
        # Thickness
        for w in range(-1, 2):
            perp_angle = angle + math.pi / 2
            wx = int(w * math.cos(perp_angle))
            wy = int(w * math.sin(perp_angle))
            _set(grid, cy + py + wy, cx + px + wx, color)


def draw_triangle(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Filled triangle pointing up."""
    for dy in range(-size, 1):
        width_at_y = int((size + dy) * size / max(size, 1))
        for dx in range(-width_at_y, width_at_y + 1):
            _set(grid, cy + dy, cx + dx, color)


def draw_circle(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Filled circle."""
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            if dx*dx + dy*dy <= size*size:
                _set(grid, cy + dy, cx + dx, color)


def draw_star(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """5-pointed star."""
    points = 5
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            angle = math.atan2(dy, dx)
            dist = math.sqrt(dx*dx + dy*dy)
            # Star boundary
            star_r = size * (0.5 + 0.5 * math.cos(points * angle))
            if dist <= star_r:
                _set(grid, cy + dy, cx + dx, color)


def draw_leaf(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Leaf shape."""
    for dy in range(-size, size + 1):
        width = int(size * math.sqrt(1 - (dy / max(size, 1)) ** 2) * 0.8)
        for dx in range(-width, width + 1):
            _set(grid, cy + dy, cx + dx, color)
    # Center vein
    for dy in range(-size, size + 1):
        _set(grid, cy + dy, cx, color)


def draw_wave(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Wavy line pattern."""
    for dx in range(-size * 2, size * 2 + 1):
        wave_y = int(size * 0.4 * math.sin(dx * math.pi / max(size, 1)))
        for dy in range(-2, 3):
            _set(grid, cy + wave_y + dy, cx + dx, color)


def draw_zigzag(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Zigzag line pattern."""
    segments = max(2, size // 2)
    seg_width = size * 2 // max(segments, 1)
    for seg in range(segments):
        x_start = cx - size + seg * seg_width
        y_base = cy + (size if seg % 2 == 0 else -size)
        x_end = x_start + seg_width
        for x in range(x_start, min(x_end, cx + size + 1)):
            t = (x - x_start) / max(seg_width, 1)
            y = int(y_base + (cy - y_base) * t)
            for dy in range(-1, 2):
                _set(grid, y + dy, x, color)


def draw_hook(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Hook/crochet hook shape."""
    # Vertical stem
    for dy in range(-size, size // 2):
        _set(grid, cy + dy, cx, color)
    # Hook curve at top
    for angle in range(90, 270):
        rad = angle * math.pi / 180
        px = int(size * 0.5 * math.cos(rad))
        py = int(size * 0.5 * math.sin(rad))
        _set(grid, cy - size + py, cx + px, color)


def draw_eye(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Eye motif (almond shape with pupil)."""
    for dy in range(-size, size + 1):
        for dx in range(-size * 2, size * 2 + 1):
            # Almond shape
            x_norm = dx / max(size * 2, 1)
            y_norm = dy / max(size, 1)
            if x_norm * x_norm + y_norm * y_norm - abs(x_norm) * 0.5 <= 1:
                _set(grid, cy + dy, cx + dx, color)
    # Pupil
    for dy in range(-max(1, size // 4), max(1, size // 4) + 1):
        for dx in range(-max(1, size // 4), max(1, size // 4) + 1):
            if dx*dx + dy*dy <= (size // 4) ** 2:
                _set(grid, cy + dy, cx + dx, color)


def draw_tooth(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Tooth/garlic shape (pointed oval)."""
    for dy in range(-size, size + 1):
        width = int(size * (1 - abs(dy) / max(size, 1)) * 0.7)
        for dx in range(-width, width + 1):
            _set(grid, cy + dy, cx + dx, color)


def draw_bird(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Bird silhouette."""
    # Body
    for dy in range(-size // 2, size // 2 + 1):
        for dx in range(-size, size + 1):
            if (dx*dx) / (size * size) + (dy*dy) / ((size // 2) ** 2) <= 1:
                _set(grid, cy + dy, cx + dx, color)
    # Wings
    for dy in range(-size, -size // 2):
        for dx in range(-size * 2, -size):
            if dx*dx + dy*dy <= size * size * 2:
                _set(grid, cy + dy, cx + dx, color)
        for dx in range(size, size * 2):
            if dx*dx + dy*dy <= size * size * 2:
                _set(grid, cy + dy, cx + dx, color)
    # Head
    for dy in range(-size // 2 - 2, -size // 2 + 2):
        for dx in range(-2, 2):
            if dx*dx + dy*dy <= 4:
                _set(grid, cy + dy, cx + dx + size, color)


def draw_fish(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Fish shape."""
    for dy in range(-size // 2, size // 2 + 1):
        for dx in range(-size, size):
            # Body ellipse
            body = (dx*dx) / (size * size) + (dy*dy) / ((size // 2) ** 2)
            # Tail triangle
            tail = dx > size * 0.5 and abs(dy) < (dx - size * 0.5) * 0.5
            if body <= 1 or tail:
                _set(grid, cy + dy, cx + dx, color)


def draw_mountain(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Mountain peak."""
    for dy in range(-size, 1):
        width = int((size + dy) * size / max(size, 1))
        for dx in range(-width, width + 1):
            _set(grid, cy + dy, cx + dx, color)
    # Snow cap
    for dy in range(-size, -size + max(2, size // 4)):
        width = int((size + dy) * size / max(size, 1)) * 0.3
        for dx in range(-int(width), int(width) + 1):
            _set(grid, cy + dy, cx + dx, color)


def draw_cloud(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Cloud shape (overlapping circles)."""
    centers = [
        (0, 0),
        (-size // 2, size // 4),
        (size // 2, size // 4),
        (-size // 3, -size // 3),
        (size // 3, -size // 3),
    ]
    for cdy, cdx in centers:
        r = max(2, size // 2)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if (dx - cdx) ** 2 + (dy - cdy) ** 2 <= r * r:
                    _set(grid, cy + dy, cx + dx, color)


def draw_flame(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Flame shape."""
    for dy in range(-size, size // 2 + 1):
        # Flame gets narrower toward top
        if dy < 0:
            width = int(size * (1 + dy / max(size, 1)) * 0.6)
        else:
            width = int(size * 0.6 * (1 - dy / max(size, 1)))
        width = max(1, width)
        for dx in range(-width, width + 1):
            _set(grid, cy + dy, cx + dx, color)


def draw_tree(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Tree with trunk and canopy."""
    # Trunk
    trunk_width = max(1, size // 6)
    for dy in range(0, size):
        for dx in range(-trunk_width, trunk_width + 1):
            _set(grid, cy + dy, cx + dx, color)
    # Canopy (triangle)
    for dy in range(-size, 0):
        width = int((size + dy) * size / max(size, 1))
        for dx in range(-width, width + 1):
            _set(grid, cy + dy, cx + dx, color)


# ── Motif Registry ───────────────────────────────────────

MOTIF_FUNCTIONS: Dict[str, DrawFunc] = {
    "diamond": draw_diamond,
    "cross": draw_cross,
    "butterfly": draw_butterfly,
    "naga": draw_naga,
    "lotus": draw_lotus,
    "spiral": draw_spiral,
    "triangle": draw_triangle,
    "circle": draw_circle,
    "star": draw_star,
    "leaf": draw_leaf,
    "wave": draw_wave,
    "zigzag": draw_zigzag,
    "hook": draw_hook,
    "eye": draw_eye,
    "tooth": draw_tooth,
    "bird": draw_bird,
    "fish": draw_fish,
    "mountain": draw_mountain,
    "cloud": draw_cloud,
    "flame": draw_flame,
    "tree": draw_tree,
}


# ── 6 Symbol Types ───────────────────────────────────────

def draw_mandala(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int],
                 layers: int = 4, segments: int = 8) -> None:
    """Circular mandala with concentric pattern layers."""
    for layer in range(1, layers + 1):
        r = int(layer * size / layers)
        for seg in range(segments):
            angle = seg * 2 * math.pi / segments
            for t in range(max(1, size // layers)):
                px = int((r + t) * math.cos(angle))
                py = int((r + t) * math.sin(angle))
                _set(grid, cy + py, cx + px, color)
                # Radial lines
                for w in range(-1, 2):
                    perp = angle + math.pi / 2
                    _set(grid, cy + py + int(w * math.cos(perp)),
                         cx + px + int(w * math.sin(perp)), color)
    # Center circle
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx*dx + dy*dy <= 4:
                _set(grid, cy + dy, cx + dx, color)


def draw_totem(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int],
               faces: int = 3) -> None:
    """Totem pole with stacked face motifs."""
    face_height = size // max(faces, 1)
    for f in range(faces):
        fy = cy - size + f * face_height + face_height // 2
        # Face circle
        for dy in range(-face_height // 2, face_height // 2 + 1):
            for dx in range(-face_height // 2, face_height // 2 + 1):
                if dx*dx + dy*dy <= (face_height // 2) ** 2:
                    _set(grid, fy + dy, cx + dx, color)
        # Eyes
        eye_y = fy - face_height // 6
        for ex in [-face_height // 5, face_height // 5]:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    _set(grid, eye_y + dy, cx + ex + dx, color)


def draw_clan_shield(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Shield shape with internal pattern."""
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            # Shield outline
            if dy < 0:
                width = size
            else:
                width = int(size * (1 - dy / max(size * 1.5, 1)))
            if abs(dx) <= width:
                _set(grid, cy + dy, cx + dx, color)
    # Internal cross
    for dx in range(-max(1, size // 4), max(1, size // 4) + 1):
        for dy in range(-size, size + 1):
            if abs(dx) <= max(1, size // 6):
                _set(grid, cy + dy, cx + dx, color)


def draw_spirit_mask(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Spirit mask with exaggerated features."""
    # Oval face
    for dy in range(-size, size + 1):
        for dx in range(-size, size + 1):
            if (dx*dx) / (size * size) + (dy*dy) / ((size * 1.2) ** 2) <= 1:
                _set(grid, cy + dy, cx + dx, color)
    # Large eyes
    for ey_offset in [-size // 4, size // 4]:
        for dy in range(-size // 4, size // 4 + 1):
            for dx in range(-size // 3, size // 3 + 1):
                if (dx*dx) / ((size // 3) ** 2) + (dy*dy) / ((size // 4) ** 2) <= 1:
                    _set(grid, cy + dy, cx + dx + ey_offset, color)
    # Mouth
    for dx in range(-size // 3, size // 3 + 1):
        for dy in range(-1, 2):
            _set(grid, cy + size // 2 + dy, cx + dx, color)


def draw_guardian_figure(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int]) -> None:
    """Guardian figure (stylized human with arms out)."""
    # Head
    head_r = max(2, size // 4)
    for dy in range(-head_r, head_r + 1):
        for dx in range(-head_r, head_r + 1):
            if dx*dx + dy*dy <= head_r * head_r:
                _set(grid, cy - size + dy, cx + dx, color)
    # Body
    for dy in range(-size + head_r, size // 2):
        for dx in range(-max(1, size // 6), max(1, size // 6) + 1):
            _set(grid, cy + dy, cx + dx, color)
    # Arms
    arm_y = cy - size // 2
    for dx in range(-size, size + 1):
        for dy in range(-2, 3):
            _set(grid, arm_y + dy, cx + dx, color)
    # Legs
    for dy in range(size // 2, size + 1):
        for leg_offset in [-max(1, size // 8), max(1, size // 8)]:
            for dx in range(-max(1, size // 10), max(1, size // 10) + 1):
                _set(grid, cy + dy, cx + dx + leg_offset, color)


def draw_ancestral_pattern(grid: np.ndarray, cy: int, cx: int, size: int, color: Tuple[int, int, int],
                           generations: int = 3) -> None:
    """Ancestral pattern: nested geometric shapes."""
    for gen in range(generations, 0, -1):
        r = int(gen * size / generations)
        # Diamond
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if abs(dx) + abs(dy) <= r:
                    _set(grid, cy + dy, cx + dx, color)
        # Inner circle
        inner_r = max(1, r // 3)
        for dy in range(-inner_r, inner_r + 1):
            for dx in range(-inner_r, inner_r + 1):
                if dx*dx + dy*dy <= inner_r * inner_r:
                    _set(grid, cy + dy, cx + dx, color)


# ── Symbol Registry ───────────────────────────────────────

SYMBOL_FUNCTIONS: Dict[str, Callable] = {
    "mandala": draw_mandala,
    "totem": draw_totem,
    "clan_shield": draw_clan_shield,
    "spirit_mask": draw_spirit_mask,
    "guardian_figure": draw_guardian_figure,
    "ancestral_pattern": draw_ancestral_pattern,
}


# ── DNA-Driven Selection ─────────────────────────────────

def select_motif_from_dna(features: Dict[str, Any], seed: int = 0) -> str:
    """Select a motif type based on DNA features deterministically."""
    random.seed(seed)
    base = features.get("base_composition", {})
    if not base:
        return random.choice(list(MOTIF_FUNCTIONS.keys()))

    # Use dominant base to narrow selection
    dominant = max(base, key=base.get)
    base_motifs = {
        "A": ["diamond", "cross", "triangle", "star", "mountain"],
        "T": ["spiral", "wave", "cloud", "flame", "leaf"],
        "G": ["lotus", "tree", "bird", "fish", "eye"],
        "C": ["naga", "butterfly", "hook", "tooth", "zigzag"],
    }
    pool = base_motifs.get(dominant, list(MOTIF_FUNCTIONS.keys()))

    # Further refine by GC content
    gc = features.get("gc_content", 0.5)
    idx = int(gc * len(pool)) % len(pool)
    return pool[idx]


def select_symbol_from_dna(features: Dict[str, Any], seed: int = 0) -> str:
    """Select a symbol type based on DNA features deterministically."""
    random.seed(seed)
    entropy = features.get("shannon_entropy", 1.5)
    if entropy >= 1.8:
        return "mandala"
    elif entropy >= 1.6:
        return "totem"
    elif entropy >= 1.4:
        return "guardian_figure"
    elif entropy >= 1.2:
        return "spirit_mask"
    elif entropy >= 1.0:
        return "clan_shield"
    else:
        return "ancestral_pattern"


def get_motif_size(features: Dict[str, Any]) -> int:
    """Determine motif size from sequence length and complexity."""
    length = features.get("length", 100)
    entropy = features.get("shannon_entropy", 1.5)
    # Longer sequences get larger motifs
    base_size = max(3, min(int(length / 30), 15))
    # Higher entropy → slightly larger
    size_mod = int(entropy)
    return base_size + size_mod


# ── Grid Placement ───────────────────────────────────────

def place_motif(
    grid: np.ndarray,
    motif_type: str,
    cy: int,
    cx: int,
    size: int,
    color: Tuple[int, int, int],
) -> None:
    """Draw a motif onto the grid at the specified position."""
    func = MOTIF_FUNCTIONS.get(motif_type)
    if func is None:
        return
    func(grid, cy, cx, size, color)


def place_symbol(
    grid: np.ndarray,
    symbol_type: str,
    cy: int,
    cx: int,
    size: int,
    color: Tuple[int, int, int],
) -> None:
    """Draw a symbol onto the grid at the specified position."""
    func = SYMBOL_FUNCTIONS.get(symbol_type)
    if func is None:
        return
    # Some symbols need extra params
    import inspect
    sig = inspect.signature(func)
    if symbol_type == "mandala":
        func(grid, cy, cx, size, color, layers=4, segments=8)
    elif symbol_type == "totem":
        func(grid, cy, cx, size, color, faces=3)
    else:
        func(grid, cy, cx, size, color)


def generate_motif_grid(
    motif_type: str,
    size: int,
    color: Tuple[int, int, int],
) -> np.ndarray:
    """Generate a standalone motif grid (for export/preview)."""
    grid = np.zeros((size * 3, size * 3, 3), dtype=np.uint8)
    cy, cx = size * 3 // 2, size * 3 // 2
    place_motif(grid, motif_type, cy, cx, size, color)
    return grid


def generate_symbol_grid(
    symbol_type: str,
    size: int,
    color: Tuple[int, int, int],
) -> np.ndarray:
    """Generate a standalone symbol grid (for export/preview)."""
    grid = np.zeros((size * 3, size * 3, 3), dtype=np.uint8)
    cy, cx = size * 3 // 2, size * 3 // 2
    place_symbol(grid, symbol_type, cy, cx, size, color)
    return grid
