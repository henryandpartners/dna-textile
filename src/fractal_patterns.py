"""
Fractal Patterns — recursive motif-within-motif pattern generation.

Generates self-similar patterns where each motif contains smaller versions
of itself, driven by DNA sub-sequences at each recursion level.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from .dna_features import DNAFeatures

# Maximum recursion depth to prevent infinite loops
MAX_FRACTAL_DEPTH = 3

# Motif types available at each recursion level
FRACTAL_MOTIF_TYPES = ["diamond", "triangle", "cross", "circle", "square"]


class FractalPatternGenerator:
    """Generate recursive motif-within-motif patterns from DNA features."""

    def __init__(self, community: str = "generic", seed: Optional[int] = None):
        """
        Args:
            community: Target community for color palette selection.
            seed: Optional RNG seed for reproducibility.
        """
        self.community = community
        self.rng = random.Random(seed)
        self._seed = seed or 0

    def generate_fractal_motif(
        self,
        features: DNAFeatures,
        motif_type: str = "auto",
        depth: int = 1,
        size: int = 50,
    ) -> np.ndarray:
        """
        Generate a fractal motif with recursive self-similarity.

        Args:
            features: Extracted DNA features.
            motif_type: Base motif type, or "auto" to select from DNA.
            depth: Recursion depth (0 = base motif only, max 3).
            size: Grid size for the output motif.

        Returns:
            np.ndarray of shape (size, size, 3) dtype uint8.
        """
        depth = min(max(0, depth), MAX_FRACTAL_DEPTH)

        if motif_type == "auto":
            motif_type = self._select_motif_type(features, depth)

        grid = np.zeros((size, size, 3), dtype=np.uint8)
        self._render_fractal(grid, features, motif_type, depth, size, 0, 0)
        return grid

    def _render_fractal(
        self,
        grid: np.ndarray,
        features: DNAFeatures,
        motif_type: str,
        depth: int,
        size: int,
        offset_y: int,
        offset_x: int,
    ) -> None:
        """Recursively render fractal motif into grid region."""
        if size < 3 or depth < 0:
            return

        colors = self._get_colors(features, depth)

        # Draw base motif at this level
        self._draw_motif(grid, motif_type, size, offset_y, offset_x, colors)

        # Recurse: place smaller motif in center
        if depth > 0:
            inner_size = max(3, size // 3)
            inner_offset_y = offset_y + (size - inner_size) // 2
            inner_offset_x = offset_x + (size - inner_size) // 2

            # Select next motif type from DNA sub-sequence
            inner_motif = self._select_motif_type(features, depth - 1)

            self._render_fractal(
                grid, features, inner_motif, depth - 1,
                inner_size, inner_offset_y, inner_offset_x,
            )

    def _draw_motif(
        self,
        grid: np.ndarray,
        motif_type: str,
        size: int,
        offset_y: int,
        offset_x: int,
        colors: List[Tuple[int, int, int]],
    ) -> None:
        """Draw a single motif shape into the grid at the given offset."""
        h, w = grid.shape[:2]
        cy, cx = size // 2, size // 2

        if motif_type == "diamond":
            half = size // 2
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    if abs(dy) + abs(dx) <= half:
                        py, px = offset_y + cy + dy, offset_x + cx + dx
                        if 0 <= py < h and 0 <= px < w:
                            dist = (abs(dy) + abs(dx)) / max(half, 1)
                            ci = min(int(dist * (len(colors) - 1)), len(colors) - 1)
                            grid[py, px] = colors[ci]

        elif motif_type == "triangle":
            for dy in range(size):
                progress = dy / max(size - 1, 1)
                half_w = int(cx * progress)
                for dx in range(-half_w, half_w + 1):
                    py, px = offset_y + dy, offset_x + cx + dx
                    if 0 <= py < h and 0 <= px < w:
                        ci = min(int(progress * (len(colors) - 1)), len(colors) - 1)
                        grid[py, px] = colors[ci]

        elif motif_type == "cross":
            arm_w = max(1, size // 6)
            for dy in range(size):
                for dx in range(size):
                    rel_y, rel_x = dy - cy, dx - cx
                    if abs(rel_x) <= arm_w or abs(rel_y) <= arm_w:
                        py, px = offset_y + dy, offset_x + dx
                        if 0 <= py < h and 0 <= px < w:
                            grid[py, px] = colors[0]

        elif motif_type == "circle":
            radius = size // 2 - 1
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dy * dy + dx * dx <= radius * radius:
                        py, px = offset_y + cy + dy, offset_x + cx + dx
                        if 0 <= py < h and 0 <= px < w:
                            dist = math.sqrt(dy * dy + dx * dx) / max(radius, 1)
                            ci = min(int(dist * (len(colors) - 1)), len(colors) - 1)
                            grid[py, px] = colors[ci]

        elif motif_type == "square":
            margin = size // 8
            for dy in range(margin, size - margin):
                for dx in range(margin, size - margin):
                    py, px = offset_y + dy, offset_x + dx
                    if 0 <= py < h and 0 <= px < w:
                        grid[py, px] = colors[0]

    def _select_motif_type(self, features: DNAFeatures, depth: int) -> str:
        """Select motif type based on DNA sub-sequence at this depth."""
        seq = features.sequence
        if not seq:
            return "diamond"

        # Use different parts of the sequence per depth level
        chunk_size = max(1, len(seq) // (MAX_FRACTAL_DEPTH + 1))
        start = depth * chunk_size
        end = start + chunk_size
        subseq = seq[start:end]

        if not subseq:
            return FRACTAL_MOTIF_TYPES[depth % len(FRACTAL_MOTIF_TYPES)]

        # Hash the sub-sequence to deterministically pick a motif
        h = sum(ord(c) for c in subseq) % len(FRACTAL_MOTIF_TYPES)
        return FRACTAL_MOTIF_TYPES[h]

    def _get_colors(
        self, features: DNAFeatures, depth: int
    ) -> List[Tuple[int, int, int]]:
        """Get color palette for a given recursion depth."""
        from .color_palette import get_all_colors

        palette = get_all_colors(self.community)
        if not palette:
            palette = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

        # Shift palette per depth level for visual variety
        offset = depth * 2
        count = min(3 + depth, len(palette))
        colors = []
        for i in range(count):
            idx = (offset + i) % len(palette)
            colors.append(palette[idx])
        return colors

    def generate_fractal_grid(
        self,
        features: DNAFeatures,
        grid_rows: int = 4,
        grid_cols: int = 4,
        tile_size: int = 30,
        depth: int = 1,
    ) -> np.ndarray:
        """
        Generate a grid of fractal motifs, each driven by a different DNA sub-sequence.

        Args:
            features: Extracted DNA features.
            grid_rows: Number of rows in the output grid.
            grid_cols: Number of columns in the output grid.
            tile_size: Size of each tile.
            depth: Recursion depth for each tile.

        Returns:
            np.ndarray of shape (total_h, total_w, 3) dtype uint8.
        """
        total_h = tile_size * grid_rows
        total_w = tile_size * grid_cols
        result = np.zeros((total_h, total_w, 3), dtype=np.uint8)

        seq = features.sequence
        chunk_size = max(1, len(seq) // (grid_rows * grid_cols))

        for row in range(grid_rows):
            for col in range(grid_cols):
                idx = row * grid_cols + col
                sub_start = idx * chunk_size
                sub_end = min(sub_start + chunk_size, len(seq))
                subseq = seq[sub_start:sub_end]

                # Create mini-features from sub-sequence
                sub_features = DNAFeatures(sequence=subseq, length=len(subseq))
                sub_features.gc_content = (subseq.count("G") + subseq.count("C")) / max(len(subseq), 1)
                sub_features.complexity_score = min(1.0, len(set(subseq)) / 4.0)

                motif_type = self._select_motif_type(sub_features, depth)
                motif = self.generate_fractal_motif(sub_features, motif_type, depth, tile_size)

                result[
                    row * tile_size:(row + 1) * tile_size,
                    col * tile_size:(col + 1) * tile_size
                ] = motif

        return result
