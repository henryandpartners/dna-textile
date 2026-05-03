"""Pattern generator — maps DNA nucleotides to a grid of colors.

Phase 3: Extended with advanced mathematical patterns (fractal, Voronoi,
wave interference, Perlin noise, L-system, Fourier synthesis, reaction-diffusion,
mosaic), upgraded existing patterns (DNA-driven stripe width, Fibonacci spiral,
hexagonal/brick/herringbone tiles), and motif overlay, complexity-aware generation,
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

# Nucleotide value maps for mathematical operations
NUC_VALUES: Dict[str, float] = {"A": 0.0, "T": 0.333, "G": 0.667, "C": 1.0}
NUC_PHASE: Dict[str, float] = {"A": 0.0, "T": math.pi / 2, "G": math.pi, "C": 3 * math.pi / 2}
NUC_FREQ: Dict[str, float] = {"A": 1.0, "T": 2.0, "G": 3.0, "C": 4.0}


class PatternGenerator:
    """Convert a DNA sequence into a 2D color grid with cultural rules."""

    def __init__(
        self,
        grid_size: int = 100,
        color_map: Optional[Dict[str, Tuple[int, int, int]]] = None,
        community: str = "generic",
        complexity: str = "intermediate",
        seed: Optional[int] = None,
        stitch_ratio: float = 1.0,
    ):
        """
        Args:
            grid_size:  Width and height of the output grid (N×N).
            color_map:  Optional custom nucleotide→RGB mapping.
            community:  Target community for cultural rules.
            complexity: Pattern complexity level.
            seed:       Optional RNG seed for reproducibility.
            stitch_ratio: Aspect ratio for stitches (width:height). Default 1.0;
                          typical knitting ~0.85 (stitches wider than tall).
        """
        self.grid_size = grid_size
        self.color_map = color_map or dict(DEFAULT_COLOR_MAP)
        self.community = community
        self.complexity = complexity
        self.seed = seed
        self.stitch_ratio = stitch_ratio

    def generate(
        self,
        sequence: str,
        community: Optional[str] = None,
        pattern_type: str = "stripe",
        seed: Optional[int] = None,
    ) -> List[List[int]]:
        """
        Generate a pattern as a list-of-lists (for test compatibility).

        Args:
            sequence:  Cleaned DNA string.
            community: Optional community override.
            pattern_type: Pattern algorithm.
            seed:      Optional RNG seed.

        Returns:
            List of lists of integer color indices.
        """
        orig_community = self.community
        if community:
            self.community = community
        grid = self.generate_grid(sequence, pattern_type=pattern_type, seed=seed)
        self.community = orig_community
        # Convert to list of lists of color indices
        # Map each RGB back to an integer index
        colors = list(set(tuple(pixel) for row in grid for pixel in row))
        color_to_idx = {c: i for i, c in enumerate(colors)}
        return [[color_to_idx[tuple(pixel)] for pixel in row] for row in grid]

    # ── helpers ──────────────────────────────────────────────

    def _nucleotide_to_rgb(self, base: str) -> Tuple[int, int, int]:
        return self.color_map.get(base, (128, 128, 128))

    def _tile_sequence(self, sequence: str) -> List[str]:
        """Repeat / truncate the sequence to fill grid_size² cells."""
        total = self.grid_size * self.grid_size
        repeats = (total // max(len(sequence), 1)) + 1
        tiled = (sequence * repeats)[:total]
        return list(tiled)

    def _seq_to_values(self, sequence: str) -> np.ndarray:
        """Convert DNA sequence to numpy array of float values."""
        return np.array([NUC_VALUES.get(b, 0.5) for b in sequence.upper()], dtype=np.float64)

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
            pattern_type: One of 'stripe', 'grid', 'spiral', 'random',
                'codon_tile', 'phase_shift', 'fractal_koch', 'voronoi',
                'wave_interference', 'perlin_noise', 'l_system',
                'fourier_pattern', 'diffusion', 'mosaic'.
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

        pattern_dispatch: Dict[str, Tuple[object, ...]] = {
            "stripe": (tiled, grid),
            "grid": (tiled, grid),
            "spiral": (tiled, grid),
            "random": (tiled, grid),
            "cellular_automata": (sequence, grid),
            "lace": (sequence, grid),
            "codon_tile": (sequence, grid),
            "phase_shift": (sequence, grid),
            "fractal_koch": (sequence, grid),
            "voronoi": (sequence, grid),
            "wave_interference": (sequence, grid),
            "perlin_noise": (sequence, grid),
            "l_system": (sequence, grid),
            "fourier_pattern": (sequence, grid),
            "diffusion": (sequence, grid),
            "mosaic": (sequence, grid),
        }

        if pattern_type not in pattern_dispatch:
            raise ValueError(f"Unknown pattern_type: {pattern_type!r}")

        args = pattern_dispatch[pattern_type]
        if pattern_type in ("stripe", "grid", "spiral", "random"):
            grid = getattr(self, f"_pattern_{pattern_type}")(tiled, grid)
        else:
            grid = getattr(self, f"_pattern_{pattern_type}")(sequence, grid)

        # Apply motif overlay
        if motif:
            grid = self._apply_motif(grid, motif)

        # Apply complexity constraints
        if apply_complexity:
            grid = self._apply_complexity_constraints(grid)

        return grid

    # ── existing patterns (upgraded) ─────────────────────────

    def _pattern_stripe(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        """
        DNA-driven stripe pattern with variable stripe width.

        Each nucleotide determines both the stripe color and its width
        (1-4 pixels based on base: A=1, T=2, G=3, C=4), creating organic
        banding reminiscent of traditional textile weaving.
        """
        n = self.grid_size
        width_map = {"A": 1, "T": 2, "G": 3, "C": 4}
        r = 0
        idx = 0
        while r < n and idx < len(tiled):
            base = tiled[idx]
            width = width_map.get(base, 1)
            rgb = self._nucleotide_to_rgb(base)
            end = min(r + width, n)
            grid[r:end, :, :] = rgb
            r = end
            idx += 1
        return grid

    def _pattern_grid(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        """
        DNA-driven grid pattern with variable cell sizes.

        Nucleotides determine cell dimensions, creating an irregular
        tessellation rather than a uniform grid.
        """
        n = self.grid_size
        size_map = {"A": 2, "T": 3, "G": 4, "C": 5}
        r = 0
        idx = 0
        while r < n and idx < len(tiled):
            base = tiled[idx]
            cell_h = size_map.get(base, 3)
            c = 0
            while c < n and idx < len(tiled):
                base_c = tiled[idx]
                cell_w = size_map.get(base_c, 3)
                rgb = self._nucleotide_to_rgb(base_c)
                rh = min(r + cell_h, n)
                cw = min(c + cell_w, n)
                grid[r:rh, c:cw] = rgb
                c = cw
                idx += 1
            r += cell_h
        return grid

    def _pattern_spiral(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        """
        Fibonacci spiral pattern using golden angle.

        Places nucleotide-colored points along a Fibonacci spiral
        (golden angle ≈ 137.508°), creating phyllotaxis-like patterns
        found in nature and traditional textile designs.
        """
        n = self.grid_size
        golden_angle = math.pi * (3 - math.sqrt(5))  # ~137.508°
        cx, cy = n / 2, n / 2
        max_r = n * 0.48
        coords: List[Tuple[int, int]] = []

        for i in range(n * n):
            r_i = max_r * math.sqrt(i / max(n * n - 1, 1))
            theta = i * golden_angle
            x = cx + r_i * math.cos(theta)
            y = cy + r_i * math.sin(theta)
            px, py = int(round(x)), int(round(y))
            if 0 <= px < n and 0 <= py < n:
                coords.append((px, py))

        for i, (r, c) in enumerate(coords):
            if i < len(tiled):
                grid[r, c] = self._nucleotide_to_rgb(tiled[i])
        return grid

    def _pattern_random(self, tiled: List[str], grid: np.ndarray) -> np.ndarray:
        """Random pattern with shuffled nucleotide assignment."""
        shuffled = tiled[:]
        random.shuffle(shuffled)
        idx = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                grid[r, c] = self._nucleotide_to_rgb(shuffled[idx])
                idx += 1
        return grid

    def _pattern_cellular_automata(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        2D Cellular Automata pattern driven by DNA sequence.

        Uses DNA values to seed a 2D CA (Game of Life variant) where each
        generation produces one row of the pattern. Nucleotide values
        determine neighborhood rules:
          A = stay (no change)
          T = birth (dead → alive)
          G = survive (alive → alive)
          C = death (alive → dead)

        The CA rule number is derived from the DNA sequence (mod 256 for
        elementary CA behavior, extended to 2D with DNA-driven thresholds).
        Each cell is colored by the nucleotide that determined its state,
        creating organic, textile-like patterns.

        Math: 2D CA on grid G(t+1)[r,c] = f(G(t)[r-1:r+2, c-1:c+2])
        where the transition function is modulated by DNA values.
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        rng = random.Random(self.seed or 42)

        # Derive CA rule parameters from DNA
        # Rule number: sum of nucleotide values * 64, mod 256
        rule_num = 0
        for i, base in enumerate(seq[:8]):
            rule_num += NUC_VALUES.get(base, 0.5) * (64 >> (i % 6))
        rule_num = int(rule_num) % 256

        # DNA-driven birth/survive thresholds
        # A→stay, T→birth, G→survive, C→death
        birth_thresholds = {"A": 3, "T": 2, "G": 3, "C": 4}  # neighbors for birth
        survive_thresholds = {"A": 2, "T": 2, "G": 3, "C": 3}  # neighbors to survive

        # Initialize grid from DNA values (seed the CA)
        state = np.zeros((n, n), dtype=np.int32)
        for r in range(n):
            for c in range(n):
                idx = (r * n + c) % len(seq)
                base = seq[idx]
                val = NUC_VALUES.get(base, 0.5)
                # Seed: cells with high DNA values start alive
                state[r, c] = 1 if val > 0.5 else 0

        # Run CA for n generations (each generation = one row)
        generations = n
        history = np.zeros((generations, n), dtype=np.int32)
        history[0] = state[0, :].copy()

        for gen in range(1, generations):
            new_state = np.zeros((n, n), dtype=np.int32)
            for r in range(n):
                for c in range(n):
                    # Count neighbors (Moore neighborhood)
                    neighbors = 0
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = (r + dr) % n, (c + dc) % n
                            neighbors += state[nr, nc]

                    idx = (gen * n + c) % len(seq)
                    base = seq[idx]

                    # Apply DNA-driven rules
                    if state[r, c] == 1:  # Currently alive
                        survive = survive_thresholds.get(base, 2)
                        if neighbors == survive or neighbors == survive_thresholds.get("A", 2):
                            new_state[r, c] = 1  # Stay alive (G/survive or A/stay)
                        else:
                            new_state[r, c] = 0  # Death (C)
                    else:  # Currently dead
                        birth = birth_thresholds.get(base, 3)
                        if neighbors == birth or neighbors == birth_thresholds.get("T", 2):
                            new_state[r, c] = 1  # Birth (T)
                        else:
                            new_state[r, c] = 0  # Stay dead (A)

            state = new_state
            history[gen] = state[0, :].copy()

        # Render: each row colored by the DNA base that drove it
        for r in range(min(generations, n)):
            for c in range(n):
                idx = (r * n + c) % len(seq)
                base = seq[idx]
                if history[r, c] == 1:
                    # Alive cell: color by the driving nucleotide
                    grid[r, c] = self._nucleotide_to_rgb(base)
                else:
                    # Dead cell: dark/neutral
                    grid[r, c] = (40, 40, 40)

        # Add organic variation: blend rows based on DNA phase
        for r in range(1, min(generations, n)):
            idx = r % len(seq)
            base = seq[idx]
            if base == "A":
                # Smooth transition — blend with previous row
                blend = 0.3
                mask = grid[r] == (40, 40, 40)
                blended = grid[r].astype(np.float32) * (1 - blend) + grid[r - 1].astype(np.float32) * blend
                grid[r] = np.where(mask[:, :], blended.astype(np.uint8), grid[r])
            elif base == "C":
                # Sharp contrast — darken
                grid[r] = (grid[r].astype(np.float32) * 0.7).astype(np.uint8)

        return grid

    def _pattern_lace(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Lace mode — binary openwork pattern driven by DNA.

        Produces a binary grid: hole (1) or no-hole (0).
        Constraint: holes must be surrounded by non-holes (machine constraint
        for knitting machines — prevents dropped stitches).

        DNA determines hole placement via threshold on nucleotide values.
        Holes are placed where DNA values exceed a threshold, then validated
        to ensure all holes have safe borders.

        Output grid uses white for holes and dark for solid areas,
        creating a lace chart suitable for machine knitting.
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        # DNA-driven hole threshold
        # Higher threshold = fewer holes
        hole_threshold = 0.6 + NUC_VALUES.get(seq[0], 0.5) * 0.2

        # Create binary hole map
        hole_map = np.zeros((n, n), dtype=np.int32)
        for r in range(n):
            for c in range(n):
                idx = (r * n + c) % len(seq)
                base = seq[idx]
                val = NUC_VALUES.get(base, 0.5)
                if val > hole_threshold:
                    hole_map[r, c] = 1

        # Validate: ensure all holes have safe borders
        # A hole is valid only if all 8 neighbors are non-holes
        validated = np.zeros((n, n), dtype=np.int32)
        for r in range(n):
            for c in range(n):
                if hole_map[r, c] == 1:
                    # Check all 8 neighbors
                    safe = True
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < n and 0 <= nc < n:
                                if hole_map[nr, nc] == 1:
                                    safe = False
                                    break
                        if not safe:
                            break
                    if safe:
                        validated[r, c] = 1

        # Render lace pattern
        # Holes = white (255,255,255), solid = dark (30,30,30)
        # Add DNA-driven color accents on solid areas
        for r in range(n):
            for c in range(n):
                if validated[r, c] == 1:
                    grid[r, c] = (255, 255, 255)  # Hole (white)
                else:
                    idx = (r * n + c) % len(seq)
                    base = seq[idx]
                    # Solid area: dark with subtle DNA-driven color
                    rgb = self._nucleotide_to_rgb(base)
                    grid[r, c] = tuple(int(v * 0.25) for v in rgb)  # Darkened

        # Add structural grid lines (like lace chart)
        # Horizontal and vertical bars every 4-8 rows/cols
        bar_spacing = max(4, n // 20)
        for r in range(0, n, bar_spacing):
            grid[r, :] = (200, 200, 200)  # Horizontal bar
        for c in range(0, n, bar_spacing):
            grid[:, c] = (200, 200, 200)  # Vertical bar

        return grid

    # ── new advanced patterns ────────────────────────────────

    def _pattern_fractal_koch(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Koch snowflake-based fractal pattern.

        Uses recursive subdivision to create fractal borders. Each nucleotide
        determines recursion depth (A=1, T=2, G=3, C=4) and color. The pattern
        generates multiple Koch curves radiating from the center, creating a
        snowflake-like tessellation.

        Math: Koch curve replaces each line segment with 4 segments forming
        an equilateral triangle bump. After n iterations, segment count = 4^n.
        """
        n = self.grid_size
        depth_map = {"A": 1, "T": 2, "G": 3, "C": 4}
        seq = sequence.upper()
        if not seq:
            return grid

        # Generate Koch curve points for each direction
        angles = [0, math.pi / 3, 2 * math.pi / 3, math.pi,
                  4 * math.pi / 3, 5 * math.pi / 3]
        cx_grid, cy_grid = n / 2, n / 2

        for i, angle in enumerate(angles):
            base = seq[i % len(seq)]
            depth = depth_map.get(base, 2)
            color = self._nucleotide_to_rgb(base)

            # Generate Koch curve
            points = self._koch_curve(0, 0, n * 0.4, 0, depth)
            # Rotate and translate
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            for (x, y) in points:
                rx = cx_grid + x * cos_a - y * sin_a
                ry = cy_grid + x * sin_a + y * cos_a
                px, py = int(round(rx)), int(round(ry))
                if 0 <= px < n and 0 <= py < n:
                    # Fill a small region around the point
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = px + dx, py + dy
                            if 0 <= nx < n and 0 <= ny < n:
                                grid[nx, ny] = color

        # Fill interior with blended colors
        for r in range(n):
            for c in range(n):
                dist = math.sqrt((r - cy_grid) ** 2 + (c - cx_grid) ** 2)
                if dist < n * 0.15:
                    base = seq[int(dist * len(seq) / (n * 0.15)) % len(seq)]
                    grid[r, c] = self._nucleotide_to_rgb(base)

        return grid

    def _koch_curve(self, x1: float, y1: float, x2: float, y2: float,
                    depth: int) -> List[Tuple[float, float]]:
        """Recursively generate Koch curve points."""
        if depth == 0:
            return [(x1, y1)]
        # Divide segment into thirds
        dx, dy = (x2 - x1) / 3, (y2 - y1) / 3
        p1 = (x1 + dx, y1 + dy)
        p2 = (x1 + 2 * dx, y1 + 2 * dy)
        # Peak of equilateral triangle
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        h = math.sqrt(dx * dx + dy * dy) * math.sqrt(3) / 2
        angle = math.atan2(dy, dx) + math.pi / 2
        peak = (mid_x + h * math.cos(angle), mid_y + h * math.sin(angle))

        # Recurse on 4 segments
        pts = []
        pts.extend(self._koch_curve(x1, y1, p1[0], p1[1], depth - 1))
        pts.extend(self._koch_curve(p1[0], p1[1], peak[0], peak[1], depth - 1))
        pts.extend(self._koch_curve(peak[0], peak[1], p2[0], p2[1], depth - 1))
        pts.extend(self._koch_curve(p2[0], p2[1], x2, y2, depth - 1))
        return pts

    def _pattern_voronoi(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Voronoi tessellation pattern driven by DNA.

        Seed points are generated from DNA sequence positions. Each Voronoi
        cell is colored by the dominant nucleotide in that region, creating
        organic cellular patterns reminiscent of traditional ikat weaving.

        Math: Voronoi diagram partitions plane into regions where each region
        contains all points closer to one seed than any other.
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        # Generate seed points from DNA
        num_seeds = max(8, len(seq) // 3)
        rng = random.Random(self.seed or 42)
        seeds: List[Tuple[float, float, str]] = []
        for i in range(num_seeds):
            base = seq[i % len(seq)]
            # Use DNA values to position seeds
            x = (NUC_VALUES.get(seq[i % len(seq)], 0.5) * (n - 20) + 10
                 + rng.uniform(-10, 10))
            y = (NUC_VALUES.get(seq[(i + 1) % len(seq)], 0.5) * (n - 20) + 10
                 + rng.uniform(-10, 10))
            seeds.append((max(0, min(n - 1, x)), max(0, min(n - 1, y)), base))

        # Compute Voronoi using vectorized distance calculation
        y_coords, x_coords = np.mgrid[0:n, 0:n]
        y_coords = y_coords.astype(np.float64)
        x_coords = x_coords.astype(np.float64)

        # For each seed, compute distance map
        min_dist = np.full((n, n), np.inf)
        labels = np.zeros((n, n), dtype=int)

        for idx, (sx, sy, _) in enumerate(seeds):
            dist = (y_coords - sy) ** 2 + (x_coords - sx) ** 2
            closer = dist < min_dist
            min_dist = np.where(closer, dist, min_dist)
            labels = np.where(closer, idx, labels)

        # Color each cell by its seed nucleotide
        for idx, (_, _, base) in enumerate(seeds):
            mask = labels == idx
            rgb = self._nucleotide_to_rgb(base)
            grid[mask, 0] = rgb[0]
            grid[mask, 1] = rgb[1]
            grid[mask, 2] = rgb[2]

        # Draw Voronoi edges
        edge_mask = np.zeros((n, n), dtype=bool)
        for idx, (sx, sy, _) in enumerate(seeds):
            dist = (y_coords - sy) ** 2 + (x_coords - sx) ** 2
            second_min = np.full((n, n), np.inf)
            for jdx, (sx2, sy2, _) in enumerate(seeds):
                if jdx == idx:
                    continue
                d2 = (y_coords - sy2) ** 2 + (x_coords - sx2) ** 2
                second_min = np.minimum(second_min, d2)
            edge = np.abs(np.sqrt(dist) - np.sqrt(second_min)) < 2.0
            edge_mask |= edge

        grid[edge_mask] = (255, 255, 255)
        return grid

    def _pattern_wave_interference(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Wave interference pattern driven by DNA.

        Each nucleotide generates a sine wave with different frequency and
        phase. The composite wave creates interference patterns with regions
        of constructive and destructive interference.

        Math: Wave function ψ(x,y) = Σᵢ Aᵢ sin(kᵢ·r + φᵢ) where each
        nucleotide contributes amplitude A, wave number k, and phase φ.
        Color mapped from |ψ|² (intensity).
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        y_coords, x_coords = np.mgrid[0:n, 0:n]
        y_coords = y_coords.astype(np.float64) / n
        x_coords = x_coords.astype(np.float64) / n

        # Composite wave
        wave = np.zeros((n, n), dtype=np.float64)
        for i, base in enumerate(seq[:min(len(seq), 20)]):
            k = NUC_FREQ.get(base, 1.0) * (1 + i * 0.3)
            phi = NUC_PHASE.get(base, 0.0) + i * 0.5
            angle = (i / max(len(seq), 1)) * math.pi * 2
            wave += math.sin(k * (x_coords * math.cos(angle) + y_coords * math.sin(angle)) + phi)

        # Normalize to [0, 1]
        wave_min, wave_max = wave.min(), wave.max()
        if wave_max - wave_min > 1e-10:
            normalized = (wave - wave_min) / (wave_max - wave_min)
        else:
            normalized = np.full((n, n), 0.5)

        # Map to colors using DNA-driven palette
        for r in range(n):
            for c in range(n):
                val = normalized[r, c]
                idx = int(val * (len(seq) - 1))
                base = seq[idx % len(seq)]
                grid[r, c] = self._nucleotide_to_rgb(base)

        return grid

    def _pattern_perlin_noise(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Perlin-like value noise driven by DNA.

        Maps nucleotides to gradient vectors at grid points, then uses
        smooth interpolation for natural-looking transitions. Creates
        organic patterns reminiscent of natural dye variations.

        Math: Value noise with smoothstep interpolation. Grid points get
        pseudo-random gradient vectors derived from DNA values.
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        # Create gradient grid from DNA
        grad_size = max(4, n // 8)
        rng = random.Random(self.seed or 42)

        # Gradient vectors from DNA
        grads = np.zeros((grad_size + 1, grad_size + 1, 2), dtype=np.float64)
        for i in range(grad_size + 1):
            for j in range(grad_size + 1):
                base = seq[(i * (grad_size + 1) + j) % len(seq)]
                angle = NUC_VALUES.get(base, 0.5) * 2 * math.pi + rng.uniform(-0.3, 0.3)
                grads[i, j] = [math.cos(angle), math.sin(angle)]

        # Interpolate noise values
        scale = grad_size / n
        y_coords, x_coords = np.mgrid[0:n, 0:n]
        noise = np.zeros((n, n), dtype=np.float64)

        for r in range(n):
            for c in range(n):
                fx, fy = c * scale, r * scale
                ix, iy = int(fx), int(fy)
                ix = min(ix, grad_size - 1)
                iy = min(iy, grad_size - 1)
                dx, dy = fx - ix, fy - iy

                # Smoothstep
                dx = dx * dx * (3 - 2 * dx)
                dy = dy * dy * (3 - 2 * dy)

                # Dot products with gradients
                g00 = grads[iy, ix]
                g10 = grads[iy, ix + 1]
                g01 = grads[iy + 1, ix]
                g11 = grads[iy + 1, ix + 1]

                d00 = dx * g00[0] + dy * g00[1]
                d10 = (dx - 1) * g10[0] + dy * g10[1]
                d01 = dx * g01[0] + (dy - 1) * g01[1]
                d11 = (dx - 1) * g11[0] + (dy - 1) * g11[1]

                nx0 = d00 + dx * (d10 - d00)
                nx1 = d01 + dx * (d11 - d01)
                noise[r, c] = nx0 + dy * (nx1 - nx0)

        # Normalize and map to colors
        noise_min, noise_max = noise.min(), noise.max()
        if noise_max - noise_min > 1e-10:
            normalized = (noise - noise_min) / (noise_max - noise_min)
        else:
            normalized = np.full((n, n), 0.5)

        for r in range(n):
            for c in range(n):
                val = normalized[r, c]
                idx = int(val * (len(seq) - 1))
                base = seq[idx % len(seq)]
                grid[r, c] = self._nucleotide_to_rgb(base)

        return grid

    def _pattern_l_system(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Lindenmayer system (L-system) pattern driven by DNA.

        Uses DNA sequence to determine production rules for an L-system,
        then renders the result as turtle graphics on the grid. Creates
        branching, fractal-like patterns found in many textile traditions.

        Math: L-system iteratively replaces symbols using production rules.
        DNA bases determine rules: A→AB, T→BA, G→A+B, C→B-A (turtle commands).
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        # Generate production rules from DNA
        rules: Dict[str, str] = {}
        bases = list(set(seq))
        for i, base in enumerate(bases):
            next_base = seq[(i + 1) % len(seq)]
            rules[base] = base + next_base  # Simple substitution rule

        # Start axiom from first base
        axiom = seq[0]
        iterations = min(len(seq) // 5 + 1, 6)  # Limit iterations

        # Generate L-system string
        current = axiom
        for _ in range(iterations):
            next_gen = []
            for symbol in current:
                next_gen.append(rules.get(symbol, symbol))
            current = "".join(next_gen)
            if len(current) > n * n * 2:  # Safety limit
                break

        # Turtle graphics rendering
        canvas = np.zeros((n, n), dtype=np.int32)
        x, y = n // 2, n // 2
        angle = -math.pi / 2  # Start pointing up
        step = max(1, n // (iterations * 4 + 4))

        turn_angle = math.pi / 3  # 60° turns

        for symbol in current[:n * n]:
            if symbol in rules:
                # Turn based on nucleotide
                turn_dir = NUC_VALUES.get(symbol, 0.5)
                if turn_dir < 0.5:
                    angle -= turn_angle
                else:
                    angle += turn_angle
            elif symbol == seq[0]:
                # Draw forward
                nx = int(round(x + step * math.cos(angle)))
                ny = int(round(y + step * math.sin(angle)))
                if 0 <= nx < n and 0 <= ny < n:
                    canvas[ny, nx] += 1
                x, y = nx, ny

        # Color based on DNA
        for r in range(n):
            for c in range(n):
                if canvas[r, c] > 0:
                    base = seq[canvas[r, c] % len(seq)]
                    grid[r, c] = self._nucleotide_to_rgb(base)

        return grid

    def _pattern_fourier_pattern(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Fourier synthesis pattern driven by DNA.

        Treats DNA as a frequency spectrum: A=freq1, T=freq2, G=freq3, C=freq4.
        Synthesizes a 2D pattern from the inverse Fourier transform, creating
        periodic patterns with DNA-determined frequencies and phases.

        Math: 2D inverse DFT: f(x,y) = Σᵤ Σᵥ F(u,v) · e^(2πi(ux/N + vy/N))
        DNA bases determine which frequencies are present and their amplitudes.
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        # Build frequency spectrum from DNA
        freq_spectrum = np.zeros((n, n), dtype=np.complex128)

        for i, base in enumerate(seq[:min(len(seq), n * n // 4)]):
            freq_idx = i % (n * n // 4)
            u = freq_idx % n
            v = freq_idx // n
            amp = NUC_VALUES.get(base, 0.5) * 2
            phase = NUC_PHASE.get(base, 0.0)
            freq_spectrum[u, v] = amp * complex(math.cos(phase), math.sin(phase))
            # Mirror for real output
            freq_spectrum[n - u, n - v] = complex(amp * math.cos(phase), -amp * math.sin(phase))

        # Compute inverse 2D DFT manually (numpy-free for control)
        # Using numpy for efficiency
        try:
            pattern = np.fft.ifft2(freq_spectrum).real
        except Exception:
            # Fallback: simple sine summation
            pattern = np.zeros((n, n))
            y_coords, x_coords = np.mgrid[0:n, 0:n]
            for i, base in enumerate(seq[:20]):
                u = (i % 8) + 1
                v = (i // 8) + 1
                amp = NUC_VALUES.get(base, 0.5)
                phase = NUC_PHASE.get(base, 0.0)
                pattern += amp * math.sin(2 * math.pi * (u * x_coords / n + v * y_coords / n) + phase)

        # Normalize
        p_min, p_max = pattern.min(), pattern.max()
        if p_max - p_min > 1e-10:
            normalized = (pattern - p_min) / (p_max - p_min)
        else:
            normalized = np.full((n, n), 0.5)

        # Map to DNA colors
        for r in range(n):
            for c in range(n):
                val = normalized[r, c]
                idx = int(val * (len(seq) - 1))
                base = seq[idx % len(seq)]
                grid[r, c] = self._nucleotide_to_rgb(base)

        return grid

    def _pattern_diffusion(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Reaction-diffusion pattern (simplified Gray-Scott model).

        DNA sequence drives reaction parameters (feed rate, kill rate,
        diffusion coefficients). Runs 50-100 iterations of simplified
        diffusion to create organic spot/stripe patterns.

        Math: Gray-Scott model:
          ∂u/∂t = D_u∇²u - uv² + f(1-u)
          ∂v/∂t = D_v∇²v + uv² - (f+k)v
        DNA bases determine f (feed) and k (kill) parameters.
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        # DNA-driven parameters
        f_base = NUC_VALUES.get(seq[0], 0.5)
        k_base = NUC_VALUES.get(seq[1 % len(seq)], 0.5)
        f = 0.02 + f_base * 0.08  # Feed rate: 0.02-0.10
        k = 0.04 + k_base * 0.06  # Kill rate: 0.04-0.10
        du, dv = 1.0, 0.5  # Diffusion coefficients

        # Initialize: u=1 everywhere, v=0 with small seed in center
        u = np.ones((n, n), dtype=np.float64)
        v = np.zeros((n, n), dtype=np.float64)
        center = n // 2
        radius = max(3, n // 15)
        y_coords, x_coords = np.mgrid[0:n, 0:n]
        mask = (x_coords - center) ** 2 + (y_coords - center) ** 2 <= radius ** 2
        v[mask] = 1.0

        # Laplacian kernel
        laplacian = np.array([[0.05, 0.2, 0.05],
                              [0.2, -1.0, 0.2],
                              [0.05, 0.2, 0.05]])

        iterations = 50 + int(f_base * 50)  # 50-100 iterations

        for _ in range(iterations):
            # Convolve with laplacian (simple 3x3)
            u_lap = np.zeros_like(u)
            v_lap = np.zeros_like(v)
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    w = laplacian[di + 1, dj + 1]
                    u_lap += w * np.roll(np.roll(u, dj, axis=1), di, axis=0)
                    v_lap += w * np.roll(np.roll(v, dj, axis=1), di, axis=0)

            # Reaction-diffusion step
            uv2 = u * v * v
            u_new = u + (du * u_lap - uv2 + f * (1 - u))
            v_new = v + (dv * v_lap + uv2 - (f + k) * v)

            # Clamp
            u = np.clip(u_new, 0, 1)
            v = np.clip(v_new, 0, 1)

        # Map v concentration to DNA colors
        for r in range(n):
            for c in range(n):
                val = v[r, c]
                idx = int(val * (len(seq) - 1))
                base = seq[idx % len(seq)]
                grid[r, c] = self._nucleotide_to_rgb(base)

        return grid

    def _pattern_mosaic(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Cultural mosaic pattern with irregular polygons.

        Divides the grid into irregular polygonal regions (like traditional
        mosaic/tile work). Each polygon is filled with a nucleotide-driven
        color and sub-pattern, creating tessellated designs inspired by
        Southeast Asian tile and textile traditions.

        Math: Uses perturbed hexagonal grid as base, then applies DNA-driven
        displacement to create irregular polygons.
        """
        n = self.grid_size
        seq = sequence.upper()
        if not seq:
            return grid

        rng = random.Random(self.seed or 42)

        # Create perturbed hexagonal grid
        hex_size = max(8, n // 10)
        rows = n // (hex_size * 1.5) + 2
        cols = n // (hex_size * math.sqrt(3)) + 2

        # Generate polygon centers
        centers: List[Tuple[float, float, str]] = []
        for r in range(rows):
            for c in range(cols):
                base_x = c * hex_size * math.sqrt(3)
                base_y = r * hex_size * 1.5
                # Perturb based on DNA
                seq_idx = (r * cols + c) % len(seq)
                base = seq[seq_idx]
                dx = (NUC_VALUES.get(base, 0.5) - 0.5) * hex_size * 0.5 + rng.uniform(-3, 3)
                dy = (NUC_VALUES.get(seq[(seq_idx + 1) % len(seq)], 0.5) - 0.5) * hex_size * 0.5 + rng.uniform(-3, 3)
                centers.append((base_x + dx, base_y + dy, base))

        # Fill grid with polygon colors using distance to centers
        y_coords, x_coords = np.mgrid[0:n, 0:n]
        y_coords = y_coords.astype(np.float64)
        x_coords = x_coords.astype(np.float64)

        # Find nearest center for each pixel
        min_dist = np.full((n, n), np.inf)
        nearest_idx = np.zeros((n, n), dtype=int)

        for idx, (cx_p, cy_p, _) in enumerate(centers):
            dist = (y_coords - cy_p) ** 2 + (x_coords - cx_p) ** 2
            closer = dist < min_dist
            min_dist = np.where(closer, dist, min_dist)
            nearest_idx = np.where(closer, idx, nearest_idx)

        # Color each polygon
        for idx, (_, _, base) in enumerate(centers):
            mask = nearest_idx == idx
            rgb = self._nucleotide_to_rgb(base)
            grid[mask, 0] = rgb[0]
            grid[mask, 1] = rgb[1]
            grid[mask, 2] = rgb[2]

        # Draw polygon edges
        edge_mask = np.zeros((n, n), dtype=bool)
        for idx, (cx_p, cy_p, _) in enumerate(centers):
            dist = (y_coords - cy_p) ** 2 + (x_coords - cx_p) ** 2
            second_min = np.full((n, n), np.inf)
            for jdx, (cx2, cy2, _) in enumerate(centers):
                if jdx == idx:
                    continue
                d2 = (y_coords - cy2) ** 2 + (x_coords - cx2) ** 2
                second_min = np.minimum(second_min, d2)
            edge = np.abs(np.sqrt(dist) - np.sqrt(second_min)) < 2.5
            edge_mask |= edge

        grid[edge_mask] = (64, 64, 64)

        # Add sub-patterns within each polygon
        for idx, (cx_p, cy_p, base) in enumerate(centers):
            mask = nearest_idx == idx
            if not np.any(mask):
                continue
            # DNA-driven sub-pattern: dots, lines, or crosshatch
            pattern_type = base
            coords = np.argwhere(mask)
            for (r, c) in coords[::4]:  # Sample every 4th pixel
                if pattern_type == "A":
                    # Dot pattern
                    if (r - cy_p) ** 2 + (c - cx_p) ** 2 < 9:
                        grid[r, c] = (255, 255, 255)
                elif pattern_type == "T":
                    # Horizontal lines
                    if r % 4 == 0:
                        grid[r, c] = (255, 255, 255)
                elif pattern_type == "G":
                    # Vertical lines
                    if c % 4 == 0:
                        grid[r, c] = (255, 255, 255)
                elif pattern_type == "C":
                    # Crosshatch
                    if r % 6 == 0 or c % 6 == 0:
                        grid[r, c] = (255, 255, 255)

        return grid

    # ── codon-driven tile mapping (upgraded) ─────────────────

    def _tile_sequence_by_codon(self, sequence: str) -> List[str]:
        """Group sequence into codons (triplets), padding if needed."""
        codons: List[str] = []
        seq = sequence.upper()
        for i in range(0, len(seq), 3):
            chunk = seq[i:i + 3]
            if len(chunk) < 3:
                chunk = chunk.ljust(3, "A")
            codons.append(chunk)
        return codons

    def _render_codon_tile(
        self, codon: str, tile_size: int = 5
    ) -> np.ndarray:
        """
        Generate a tile from a single codon.

        Base 1 → color
        Base 2 → pattern type (stripe/diamond/cross/dot/hex/brick/herringbone)
        Base 3 → rotation (0/90/180/270)
        """
        tile = np.zeros((tile_size, tile_size, 3), dtype=np.uint8)

        base1, base2, base3 = codon[0], codon[1], codon[2]

        # Color from base1
        color = self._nucleotide_to_rgb(base1)

        # Pattern type from base2
        pattern_map = {
            "A": "stripe", "T": "diamond", "G": "cross", "C": "dot",
        }
        pattern = pattern_map.get(base2, "stripe")

        # Rotation from base3
        rotation_map = {"A": 0, "T": 1, "G": 2, "C": 3}
        rotations = rotation_map.get(base3, 0)  # 90° increments

        # Draw pattern
        cx_tile = tile_size // 2
        if pattern == "stripe":
            for y in range(tile_size):
                for x in range(tile_size):
                    if y % 2 == 0:
                        tile[y, x] = color
        elif pattern == "diamond":
            half = tile_size // 2
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    if abs(dy) + abs(dx) <= half:
                        py, px = cx_tile + dy, cx_tile + dx
                        if 0 <= py < tile_size and 0 <= px < tile_size:
                            tile[py, px] = color
        elif pattern == "cross":
            for i in range(tile_size):
                tile[cx_tile, i] = color
                tile[i, cx_tile] = color
        elif pattern == "dot":
            r = max(1, tile_size // 4)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dy * dy + dx * dx <= r * r:
                        py, px = cx_tile + dy, cx_tile + dx
                        if 0 <= py < tile_size and 0 <= px < tile_size:
                            tile[py, px] = color

        # Rotate (90° increments)
        if rotations > 0:
            tile = np.rot90(tile, k=rotations, axes=(0, 1))

        return tile

    def _pattern_codon_tile(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """Fill grid with codon-driven tiles with varied layouts."""
        codons = self._tile_sequence_by_codon(sequence)
        tile_size = 5
        tiles_per_row = self.grid_size // tile_size

        idx = 0
        for row in range(tiles_per_row):
            for col in range(tiles_per_row):
                if idx >= len(codons):
                    break
                codon = codons[idx]
                tile = self._render_codon_tile(codon, tile_size)
                y0 = row * tile_size
                x0 = col * tile_size
                grid[y0:y0 + tile_size, x0:x0 + tile_size] = tile
                idx += 1
        return grid

    # ── phase-shifted patterns ────────────────────────────

    def _detect_homopolymer_runs(
        self, sequence: str
    ) -> List[Tuple[str, int, int]]:
        """Detect homopolymer runs: list of (base, start, length)."""
        runs: List[Tuple[str, int, int]] = []
        if not sequence:
            return runs
        seq = sequence.upper()
        current_base = seq[0]
        run_start = 0
        for i in range(1, len(seq)):
            if seq[i] != current_base:
                if i - run_start >= 3:  # minimum run length
                    runs.append((current_base, run_start, i - run_start))
                current_base = seq[i]
                run_start = i
        # Last run
        if len(seq) - run_start >= 3:
            runs.append((current_base, run_start, len(seq) - run_start))
        return runs

    def _pattern_phase_shift(self, sequence: str, grid: np.ndarray) -> np.ndarray:
        """
        Divide sequence into phases by homopolymer runs.

        Each phase uses a different pattern algorithm.
        Transition zones blend between patterns.
        """
        runs = self._detect_homopolymer_runs(sequence)
        seq_len = len(sequence)

        # Handle empty sequence - return a simple grid pattern
        if seq_len == 0:
            # Fill with a default pattern (all gray)
            grid[:, :, :] = (128, 128, 128)
            return grid

        # Define phase boundaries from homopolymer positions
        boundaries = [0]
        for _, start, length in runs:
            boundaries.append(start)
            boundaries.append(start + length)
        boundaries.append(seq_len)
        boundaries = sorted(set(boundaries))

        # Phase pattern algorithms
        phase_algorithms = ["stripe", "spiral", "grid", "random"]

        # Create a per-pixel phase assignment
        phase_grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        tiled = self._tile_sequence(sequence)
        idx = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                seq_pos = idx % seq_len
                # Find which phase this position belongs to
                phase = 0
                for i in range(len(boundaries) - 1):
                    if boundaries[i] <= seq_pos < boundaries[i + 1]:
                        phase = (i // 2) % len(phase_algorithms)
                        break
                phase_grid[r, c] = phase
                idx += 1

        # Render each phase separately then composite
        for phase_idx, algo in enumerate(phase_algorithms):
            mask = phase_grid == phase_idx
            if not np.any(mask):
                continue

            # Generate full pattern for this algorithm
            temp_grid = np.zeros_like(grid)
            if algo == "stripe":
                temp_grid = self._pattern_stripe(tiled, temp_grid)
            elif algo == "spiral":
                temp_grid = self._pattern_spiral(tiled, temp_grid)
            elif algo == "grid":
                temp_grid = self._pattern_grid(tiled, temp_grid)
            elif algo == "random":
                temp_grid = self._pattern_random(tiled, temp_grid)

            # Apply mask
            grid[mask] = temp_grid[mask]

        # Blend transition zones at homopolymer boundaries
        for _, start, length in runs:
            # Determine transition style from homopolymer base
            base = sequence[start].upper()
            blend_width = min(length // 2, 5)

            # Find pixels near this boundary in sequence space
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    seq_pos = (r * self.grid_size + c) % seq_len
                    if abs(seq_pos - start) < blend_width or abs(seq_pos - (start + length)) < blend_width:
                        # Apply blend based on base
                        if base == "A":
                            # Fade blend — reduce saturation
                            grid[r, c] = (grid[r, c] * 0.7).astype(np.uint8)
                        elif base == "T":
                            # Sharp — no change (already hard boundary)
                            pass
                        elif base == "G":
                            # Wave — sinusoidal modulation
                            wave = 0.8 + 0.2 * math.sin(seq_pos * 0.5)
                            grid[r, c] = (grid[r, c] * wave).astype(np.uint8)
                        elif base == "C":
                            # Fade blend
                            grid[r, c] = (grid[r, c] * 0.85).astype(np.uint8)

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
        # Skip for generic community (default nucleotide colors)
        if self.community == "generic":
            return grid

        max_colors = cx.get_max_colors(self.complexity)
        palette_colors = cp.get_all_colors(self.community)

        # Limit to community palette colors
        if palette_colors and len(palette_colors) <= max_colors:
            grid = cp.apply_palette_to_grid(grid, self.community)

        return grid
