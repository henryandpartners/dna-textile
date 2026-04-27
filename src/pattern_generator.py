"""Pattern generator — maps DNA nucleotides to a grid of colors.

Phase 2: Extended with motif overlay, complexity-aware generation,
and community-specific pattern constraints.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from . import color_palette as cp
from . import complexity as cx
from . import motif_library as ml


# Default color mapping (RGB tuples)
DEFAULT_COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
    "A": (255, 0, 0),
    "T": (0, 0, 255),
    "G": (0, 255, 0),
    "C": (255, 255, 0),
}


class PatternGenerator:
    """Convert a DNA sequence into a 2D color grid with cultural rules."""

    def __init__(
        self,
        grid_size: int = 100,
        color_map: Optional[Dict[str, Tuple[int, int, int]]] = None,
        community: str = "generic",
        complexity: str = "intermediate",
    ):
        """
        Args:
            grid_size:  Width and height of the output grid (N×N).
            color_map:  Optional custom nucleotide→RGB mapping.
            community:  Target community for cultural rules.
            complexity: Pattern complexity level.
        """
        self.grid_size = grid_size
        self.color_map = color_map or dict(DEFAULT_COLOR_MAP)
        self.community = community
        self.complexity = complexity

    # ── helpers ──────────────────────────────────────────────

    def _nucleotide_to_rgb(self, base: str) -> Tuple[int, int, int]:
        return self.color_map.get(base, (128, 128, 128))

    def _tile_sequence(self, sequence: str) -> List[str]:
        """Repeat / truncate the sequence to fill grid_size² cells."""
        total = self.grid_size * self.grid_size
        repeats = (total // max(len(sequence), 1)) + 1
        tiled = (sequence * repeats)[:total]
        return list(tiled)

    # ── pattern algorithms ───────────────────────────────────

    def generate_grid(
        self,
        sequence: str,
        pattern_type: str = "stripe",
        seed: Optional[int] = None,
        motif: Optional[str] = None,
        apply_complexity: bool = True,
    ) -> np.ndarray:
        """
        Generate a color grid from a DNA sequence.

        Args:
            sequence:  Cleaned DNA string (A/T/G/C only).
            pattern_type: One of 'stripe', 'grid', 'spiral', 'random'.
            seed:      Optional RNG seed.
            motif:     Optional motif name to overlay.
            apply_complexity: Whether to enforce complexity constraints.

        Returns:
            np.ndarray of shape (grid_size, grid_size, 3) dtype uint8.
        """
        if seed is not None:
            random.seed(seed)

        tiled = self._tile_sequence(sequence)
        grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)

        if pattern_type == "stripe":
            grid = self._pattern_stripe(tiled, grid)
        elif pattern_type == "grid":
            grid = self._pattern_grid(tiled, grid)
        elif pattern_type == "spiral":
            grid = self._pattern_spiral(tiled, grid)
        elif pattern_type == "random":
            grid = self._pattern_random(tiled, grid)
        else:
            raise ValueError(f"Unknown pattern_type: {pattern_type!r}")

        # Apply motif overlay
        if motif:
            grid = self._apply_motif(grid, motif)

        # Apply complexity constraints
        if apply_complexity:
            grid = self._apply_complexity_constraints(grid)

        return grid

    def _pattern_stripe(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        idx = 0
        for r in range(self.grid_size):
            base = tiled[idx]
            rgb = self._nucleotide_to_rgb(base)
            grid[r, :, :] = rgb
            idx += 1
        return grid

    def _pattern_grid(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        idx = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                grid[r, c] = self._nucleotide_to_rgb(tiled[idx])
                idx += 1
        return grid

    def _pattern_spiral(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        n = self.grid_size
        coords: List[Tuple[int, int]] = []
        top, bottom, left, right = 0, n - 1, 0, n - 1
        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                coords.append((top, c))
            top += 1
            for r in range(top, bottom + 1):
                coords.append((r, right))
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    coords.append((bottom, c))
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    coords.append((r, left))
                left += 1

        for i, (r, c) in enumerate(coords):
            if i < len(tiled):
                grid[r, c] = self._nucleotide_to_rgb(tiled[i])
        return grid

    def _pattern_random(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        shuffled = tiled[:]
        random.shuffle(shuffled)
        idx = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                grid[r, c] = self._nucleotide_to_rgb(shuffled[idx])
                idx += 1
        return grid

    # ── motif overlay ────────────────────────────────────────

    def _apply_motif(self, grid: np.ndarray, motif_name: str) -> np.ndarray:
        """Overlay a motif pattern onto the grid."""
        motif_grid = ml.get_motif_grid(self.community, motif_name)
        if motif_grid is None:
            return grid

        motif_arr = np.array(motif_grid, dtype=np.uint8)
        mh, mw = motif_arr.shape

        # Place motif in center of grid
        start_r = (self.grid_size - mh) // 2
        start_c = (self.grid_size - mw) // 2

        for r in range(mh):
            for c in range(mw):
                if motif_arr[r, c] > 0:
                    gr = start_r + r
                    gc = start_c + c
                    if 0 <= gr < self.grid_size and 0 <= gc < self.grid_size:
                        # Blend motif color with existing
                        existing = grid[gr, gc].astype(np.float32)
                        motif_color = np.array([255, 255, 255], dtype=np.float32)
                        blended = existing * 0.6 + motif_color * 0.4
                        grid[gr, gc] = blended.astype(np.uint8)

        return grid

    # ── complexity constraints ───────────────────────────────

    def _apply_complexity_constraints(self, grid: np.ndarray) -> np.ndarray:
        """Apply complexity-level constraints to the grid."""
        max_colors = cx.get_max_colors(self.complexity)
        palette_colors = cp.get_all_colors(self.community)

        # Limit to community palette colors
        if palette_colors and len(palette_colors) <= max_colors:
            grid = cp.apply_palette_to_grid(grid, self.community)

        return grid
