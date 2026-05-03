"""
Motif & Symbol Generator — creates culturally appropriate motifs and symbols
from DNA features using procedural generation.

Phase 3: Replaces static motif library with dynamic generation driven by DNA.
Each motif is generated from DNA k-mers, palindromes, and structural features.

Motif types:
- Geometric: diamonds, triangles, zigzags, waves, spirals
- Animal: butterflies, nagas, elephants, fish, birds
- Plant: lotus, bamboo, rice, flowers, trees
- Spiritual: ancestor marks, spirit gates, sun/moon, sacred geometry
- Clan symbols: tribe-specific identity markers
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from .dna_features import DNAFeatures


class MotifGenerator:
    """Generate motifs and symbols from DNA features."""

    def __init__(self, community: str, seed: Optional[int] = None):
        self.community = community
        self.rng = random.Random(seed)
        self._seed = seed or 0

    def generate_motif(
        self,
        features: DNAFeatures,
        motif_type: str = "auto",
        size: int = 20,
    ) -> np.ndarray:
        """
        Generate a single motif from DNA features.

        Args:
            features: Extracted DNA features
            motif_type: Type of motif, or "auto" to select from DNA
            size: Grid size for the motif

        Returns:
            np.ndarray of shape (size, size, 3) with motif colors
        """
        if motif_type == "auto":
            motif_type = self._select_motif_type(features)

        generators = {
            "geometric": self._generate_diamond,  # alias
            "diamond": self._generate_diamond,
            "triangle": self._generate_triangle,
            "zigzag": self._generate_zigzag,
            "wave": self._generate_wave,
            "spiral": self._generate_spiral,
            "butterfly": self._generate_butterfly,
            "naga": self._generate_naga,
            "elephant": self._generate_elephant,
            "fish": self._generate_fish,
            "bird": self._generate_bird,
            "lotus": self._generate_lotus,
            "bamboo": self._generate_bamboo,
            "rice": self._generate_rice,
            "flower": self._generate_flower,
            "tree": self._generate_tree,
            "spirit_gate": self._generate_spirit_gate,
            "sun": self._generate_sun,
            "moon": self._generate_moon,
            "sacred_geometry": self._generate_sacred_geometry,
            "clan_mark": self._generate_clan_mark,
            "ancestor_mark": self._generate_ancestor_mark,
        }

        generator = generators.get(motif_type, self._generate_diamond)
        return generator(features, size)

    def generate_symbol(
        self,
        features: DNAFeatures,
        symbol_type: str = "auto",
        size: int = 40,
    ) -> np.ndarray:
        """
        Generate a cultural symbol from DNA features.

        Symbols are larger, more complex compositions.
        """
        if symbol_type == "auto":
            symbol_type = self._select_symbol_type(features)

        generators = {
            "totem": self._generate_totem,
            "mandala": self._generate_mandala,
            "clan_shield": self._generate_clan_shield,
            "spirit_mask": self._generate_spirit_mask,
            "cosmic_diagram": self._generate_cosmic_diagram,
            "story_panel": self._generate_story_panel,
        }

        generator = generators.get(symbol_type, self._generate_totem)
        return generator(features, size)

    def generate_pattern_tile(
        self,
        features: DNAFeatures,
        tile_size: int = 20,
        grid_rows: int = 5,
        grid_cols: int = 5,
    ) -> np.ndarray:
        """
        Generate a repeating pattern tile from DNA.

        Creates a grid of motifs that can tile seamlessly.
        """
        total_h = tile_size * grid_rows
        total_w = tile_size * grid_cols
        result = np.zeros((total_h, total_w, 3), dtype=np.uint8)

        seq = features.sequence
        motif_types = [
            "diamond", "triangle", "zigzag", "wave",
            "lotus", "flower", "butterfly", "spiral",
        ]

        for row in range(grid_rows):
            for col in range(grid_cols):
                idx = (row * grid_cols + col) % len(seq)
                base = seq[idx]
                # Map base to motif type
                base_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[base]
                motif_type = motif_types[base_idx % len(motif_types)]

                motif = self.generate_motif(features, motif_type, tile_size)
                result[
                    row * tile_size:(row + 1) * tile_size,
                    col * tile_size:(col + 1) * tile_size
                ] = motif

        return result

    # ── Auto-selection ────────────────────────────────────

    def _select_motif_type(self, features: DNAFeatures) -> str:
        """Select motif type based on DNA features."""
        # Use dominant trinucleotide to pick motif
        trinuc = features.dominant_trinuc
        if not trinuc:
            return "geometric"

        # Map trinucleotide patterns to motif categories
        gc = features.gc_content
        symmetry = features.symmetry_score

        if symmetry > 0.6:
            # High symmetry → geometric/spiritual
            if gc > 0.5:
                return "sacred_geometry"
            return "diamond"
        elif gc > 0.6:
            # High GC → plant motifs
            return self.rng.choice(["lotus", "bamboo", "flower", "tree"])
        elif gc < 0.35:
            # Low GC → animal motifs
            return self.rng.choice(["butterfly", "fish", "bird", "elephant"])
        else:
            # Medium GC → mixed
            return self.rng.choice(["zigzag", "wave", "spiral", "triangle"])

    def _select_symbol_type(self, features: DNAFeatures) -> str:
        """Select symbol type based on DNA features."""
        if features.symmetry_score > 0.6:
            return "mandala"
        elif len(features.palindromes) > 3:
            return "spirit_mask"
        elif features.gc_content > 0.55:
            return "cosmic_diagram"
        else:
            return "totem"

    # ── Geometric Motifs ─────────────────────────────────

    def _generate_diamond(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a diamond motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        cy, cx = size // 2, size // 2
        half = size // 2 - 1

        colors = self._get_motif_colors(features, 3)

        # Outer diamond
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                if abs(dy) + abs(dx) <= half:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        # Color based on distance from center
                        dist = (abs(dy) + abs(dx)) / half
                        color_idx = min(int(dist * (len(colors) - 1)), len(colors) - 1)
                        grid[py, px] = colors[color_idx]

        # Inner pattern from DNA
        seq = features.sequence
        inner_half = half // 2
        for dy in range(-inner_half, inner_half + 1):
            for dx in range(-inner_half, inner_half + 1):
                if abs(dy) + abs(dx) <= inner_half:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        idx = ((dy + inner_half) * (inner_half * 2 + 1) + dx + inner_half) % len(seq)
                        if seq[idx] in "GC":
                            grid[py, px] = colors[-1]  # Accent color

        return grid

    def _generate_triangle(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a triangle motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)

        cy = size // 3
        base_y = size - 1
        half_w = size // 2 - 1

        for y in range(cy, base_y + 1):
            progress = (y - cy) / max(base_y - cy, 1)
            width = int(progress * half_w)
            for dx in range(-width, width + 1):
                px = size // 2 + dx
                if 0 <= px < size:
                    color_idx = int(progress * (len(colors) - 1))
                    grid[y, px] = colors[min(color_idx, len(colors) - 1)]

        # Inner triangle from DNA
        inner_progress = 0.4
        inner_y = cy + int((base_y - cy) * inner_progress)
        inner_half = int(half_w * (1 - inner_progress))
        for y in range(inner_y, base_y + 1):
            progress = (y - inner_y) / max(base_y - inner_y, 1)
            width = int(progress * inner_half)
            for dx in range(-width, width + 1):
                px = size // 2 + dx
                if 0 <= px < size:
                    grid[y, px] = colors[0]

        return grid

    def _generate_zigzag(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a zigzag motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 2)
        seq = features.sequence

        amplitude = size // 4
        frequency = max(2, len(seq) // (size // 2))

        for x in range(size):
            phase = (x * frequency / size) % 1.0
            y = size // 2 + int(amplitude * math.sin(phase * math.pi * 2))

            # Draw zigzag line with thickness
            thickness = max(1, size // 20)
            for dy in range(-thickness, thickness + 1):
                py = y + dy
                if 0 <= py < size:
                    grid[py, x] = colors[0]

            # Second line (offset)
            y2 = size // 2 + int(amplitude * math.sin(phase * math.pi * 2 + math.pi / 2))
            for dy in range(-thickness // 2, thickness // 2 + 1):
                py = y2 + dy
                if 0 <= py < size:
                    grid[py, x] = colors[1]

        return grid

    def _generate_wave(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a wave motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)

        for y in range(size):
            for x in range(size):
                # Multiple wave layers from DNA
                wave1 = math.sin(x * 0.3 + y * 0.1) * 0.5
                wave2 = math.sin(x * 0.15 - y * 0.2) * 0.3
                wave3 = math.cos(x * 0.2 + y * 0.15) * 0.2

                # DNA drives wave phase
                idx = (x + y * size) % len(features.sequence)
                base_phase = {"A": 0, "T": 0.5, "G": 1.0, "C": 1.5}[features.sequence[idx]]

                value = wave1 + wave2 + wave3 + base_phase * 0.1
                color_idx = int((value + 1) / 2 * (len(colors) - 1))
                color_idx = max(0, min(color_idx, len(colors) - 1))
                grid[y, x] = colors[color_idx]

        return grid

    def _generate_spiral(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a spiral motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)
        cy, cx = size // 2, size // 2
        max_r = size // 2 - 1

        # Golden angle spiral
        golden_angle = math.pi * (3 - math.sqrt(5))

        seq = features.sequence
        for i in range(size * size):
            angle = i * golden_angle
            r = math.sqrt(i) / math.sqrt(size * size) * max_r
            x = cx + int(r * math.cos(angle))
            y = cy + int(r * math.sin(angle))

            if 0 <= y < size and 0 <= x < size:
                idx = i % len(seq)
                color_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[seq[idx]]
                grid[y, x] = colors[color_idx]

        return grid

    # ── Animal Motifs ────────────────────────────────────

    def _generate_butterfly(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a butterfly motif (Hmong-style)."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)
        cy, cx = size // 2, size // 2

        # Body
        body_w = max(1, size // 10)
        for dy in range(-size // 3, size // 3 + 1):
            for dx in range(-body_w, body_w + 1):
                py, px = cy + dy, cx + dx
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[0]

        # Wings (symmetric)
        wing_size = size // 3
        for side in [-1, 1]:
            for dy in range(-wing_size, wing_size + 1):
                for dx in range(wing_size):
                    # Wing shape: ellipse
                    nx = dx / wing_size
                    ny = dy / wing_size
                    if nx * nx + ny * ny < 1.0:
                        px = cx + side * (body_w + dx)
                        py = cy + dy
                        if 0 <= py < size and 0 <= px < size:
                            # Color from DNA
                            idx = int((nx + ny) * len(features.sequence) / 2) % len(features.sequence)
                            color_idx = {"A": 1, "T": 2, "G": 3, "C": 1}[features.sequence[idx]]
                            grid[py, px] = colors[color_idx]

        # Wing spots
        for _ in range(3):
            spot_x = cx + self.rng.choice([-1, 1]) * self.rng.randint(wing_size // 3, wing_size * 2 // 3)
            spot_y = cy + self.rng.randint(-wing_size // 2, wing_size // 2)
            spot_r = max(1, size // 12)
            for dy in range(-spot_r, spot_r + 1):
                for dx in range(-spot_r, spot_r + 1):
                    if dy * dy + dx * dx <= spot_r * spot_r:
                        py, px = spot_y + dy, spot_x + dx
                        if 0 <= py < size and 0 <= px < size:
                            grid[py, px] = colors[3]

        return grid

    def _generate_naga(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a naga serpent motif (Thai Lue style)."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)

        # Sinusoidal body
        body_w = max(2, size // 12)
        for x in range(size):
            y = size // 2 + int(size // 4 * math.sin(x * 0.15))
            for dy in range(-body_w, body_w + 1):
                py = y + dy
                if 0 <= py < size:
                    color_idx = int((dy + body_w) / (body_w * 2) * (len(colors) - 1))
                    grid[py, x] = colors[min(color_idx, len(colors) - 1)]

        # Head (top of grid)
        head_y = size // 2 + int(size // 4 * math.sin(0))
        head_r = body_w * 2
        for dy in range(-head_r, head_r + 1):
            for dx in range(-head_r, head_r + 1):
                if dy * dy + dx * dx <= head_r * head_r:
                    py, px = head_y + dy, dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[-1]

        # Scales pattern
        for x in range(0, size, 4):
            y = size // 2 + int(size // 4 * math.sin(x * 0.15))
            for dy in range(-body_w, body_w + 1):
                if abs(dy) % 2 == 0:
                    py = y + dy
                    if 0 <= py < size:
                        grid[py, x] = colors[2] if len(colors) > 2 else colors[0]

        return grid

    def _generate_elephant(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a simplified elephant motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 2)
        cy, cx = size // 2, size // 2

        # Body (ellipse)
        body_rx, body_ry = size // 4, size // 5
        for dy in range(-body_ry, body_ry + 1):
            for dx in range(-body_rx, body_rx + 1):
                if (dx / body_rx) ** 2 + (dy / body_ry) ** 2 < 1:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Head (circle)
        head_r = size // 6
        head_cy, head_cx = cy - body_ry - head_r // 2, cx + body_rx // 2
        for dy in range(-head_r, head_r + 1):
            for dx in range(-head_r, head_r + 1):
                if dy * dy + dx * dx <= head_r * head_r:
                    py, px = head_cy + dy, head_cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Trunk (curved line)
        for t in range(head_r * 2):
            tx = head_cx + head_r // 2
            ty = head_cy + t
            trunk_offset = int(3 * math.sin(t * 0.3))
            px = tx + trunk_offset
            if 0 <= ty < size and 0 <= px < size:
                grid[ty, px] = colors[0]

        # Legs
        leg_w = max(1, size // 15)
        leg_positions = [-body_rx // 2, -body_rx // 4, body_rx // 4, body_rx // 2]
        for lx in leg_positions:
            for dy in range(body_ry, body_ry + size // 4):
                for dx in range(-leg_w, leg_w + 1):
                    py, px = cy + dy, cx + lx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        return grid

    def _generate_fish(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a fish motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)
        cy, cx = size // 2, size // 2

        # Body
        body_rx, body_ry = size // 3, size // 5
        for dy in range(-body_ry, body_ry + 1):
            for dx in range(-body_rx, body_rx + 1):
                if (dx / body_rx) ** 2 + (dy / body_ry) ** 2 < 1:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Tail
        tail_x = cx - body_rx
        tail_w = size // 5
        for dy in range(-tail_w, tail_w + 1):
            progress = abs(dy) / tail_w
            tx = tail_x - int(tail_w * (1 - progress))
            for x in range(tx, tail_x + 1):
                if 0 <= x < size:
                    grid[cy + dy, x] = colors[1]

        # Eye
        eye_x = cx + body_rx // 2
        eye_r = max(1, size // 15)
        for dy in range(-eye_r, eye_r + 1):
            for dx in range(-eye_r, eye_r + 1):
                if dy * dy + dx * dx <= eye_r * eye_r:
                    py, px = cy + dy, eye_x + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[2]

        return grid

    def _generate_bird(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a bird motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)
        cy, cx = size // 2, size // 2

        # Body
        body_r = size // 5
        for dy in range(-body_r, body_r + 1):
            for dx in range(-body_r, body_r + 1):
                if dy * dy + dx * dx <= body_r * body_r:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Wings (spread)
        wing_span = size // 3
        for side in [-1, 1]:
            for w in range(wing_span):
                wing_y = cy + int(w * 0.3 * side)
                for dy in range(-max(1, wing_span // 6), max(1, wing_span // 6) + 1):
                    px = cx + side * (body_r + w)
                    py = wing_y + dy
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[1]

        # Head
        head_r = size // 8
        for dy in range(-head_r, head_r + 1):
            for dx in range(-head_r, head_r + 1):
                if dy * dy + dx * dx <= head_r * head_r:
                    py, px = cy - body_r - head_r // 2 + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Beak
        beak_y = cy - body_r - head_r
        for dx in range(head_r):
            px = cx + head_r + dx
            if 0 <= px < size:
                grid[beak_y, px] = colors[2]

        return grid

    # ── Plant Motifs ──────────────────────────────────────

    def _generate_lotus(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a lotus motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)
        cy, cx = size // 2, size // 2

        num_petals = 8
        petal_length = size // 3
        petal_width = size // 6

        for p in range(num_petals):
            angle = (p / num_petals) * math.pi * 2
            for dy in range(-petal_length, petal_length + 1):
                for dx in range(-petal_width, petal_width + 1):
                    # Petal shape
                    progress = abs(dy) / petal_length
                    max_dx = petal_width * (1 - progress * progress)
                    if abs(dx) <= max_dx:
                        # Rotate
                        rx = dx * math.cos(angle) - dy * math.sin(angle)
                        ry = dx * math.sin(angle) + dy * math.cos(angle)
                        px, py = int(cx + rx), int(cy + ry)
                        if 0 <= py < size and 0 <= px < size:
                            color_idx = int(progress * (len(colors) - 1))
                            grid[py, px] = colors[min(color_idx, len(colors) - 1)]

        # Center
        center_r = size // 8
        for dy in range(-center_r, center_r + 1):
            for dx in range(-center_r, center_r + 1):
                if dy * dy + dx * dx <= center_r * center_r:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[-1]

        return grid

    def _generate_bamboo(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a bamboo motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)

        # Stalks
        num_stalks = max(1, size // 15)
        for s in range(num_stalks):
            stalk_x = size // (num_stalks + 1) * (s + 1)
            stalk_w = max(1, size // 20)

            for y in range(size):
                # Slight curve
                curve = int(2 * math.sin(y * 0.1 + s))
                x = stalk_x + curve
                for dx in range(-stalk_w, stalk_w + 1):
                    px = x + dx
                    if 0 <= px < size:
                        grid[y, px] = colors[0]

                # Nodes
                if y % (size // 4) == 0:
                    for dx in range(-stalk_w - 1, stalk_w + 2):
                        px = x + dx
                        if 0 <= px < size:
                            grid[y, px] = colors[1]

        # Leaves
        for _ in range(max(3, size // 10)):
            leaf_y = self.rng.randint(size // 4, size * 3 // 4)
            leaf_x = self.rng.randint(size // 6, size * 5 // 6)
            leaf_len = max(3, size // 6)
            for l in range(leaf_len):
                lx = leaf_x + l
                ly = leaf_y + int(l * 0.3)
                if 0 <= ly < size and 0 <= lx < size:
                    grid[ly, lx] = colors[2]

        return grid

    def _generate_rice(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a rice/grain motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)
        cy, cx = size // 2, size // 2

        # Stem
        stem_w = max(1, size // 20)
        for y in range(size // 4, size):
            for dx in range(-stem_w, stem_w + 1):
                px = cx + dx
                if 0 <= px < size:
                    grid[y, px] = colors[0]

        # Grain heads
        num_heads = max(3, size // 8)
        for h in range(num_heads):
            head_y = size // 4 + h * (size // (num_heads + 1))
            head_r = max(2, size // 10)
            for dy in range(-head_r, head_r + 1):
                for dx in range(-head_r, head_r + 1):
                    if dy * dy + dx * dx <= head_r * head_r:
                        py, px = head_y + dy, cx + dx
                        if 0 <= py < size and 0 <= px < size:
                            grid[py, px] = colors[1]

            # Awns (thin extensions)
            for angle in [-0.3, 0, 0.3]:
                for a in range(head_r):
                    ax = cx + int(a * math.sin(angle))
                    ay = head_y - head_r - a
                    if 0 <= ay < size and 0 <= ax < size:
                        grid[ay, ax] = colors[2]

        return grid

    def _generate_flower(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a generic flower motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)
        cy, cx = size // 2, size // 2

        num_petals = 5 + int(features.gc_content * 3)
        petal_r = size // 3

        for p in range(num_petals):
            angle = (p / num_petals) * math.pi * 2
            for r in range(petal_r):
                for a in range(-3, 4):
                    pa = angle + a * 0.1
                    px = cx + int(r * math.cos(pa))
                    py = cy + int(r * math.sin(pa))
                    if 0 <= py < size and 0 <= px < size:
                        color_idx = int((r / petal_r) * (len(colors) - 2)) + 1
                        grid[py, px] = colors[min(color_idx, len(colors) - 1)]

        # Center
        center_r = size // 6
        for dy in range(-center_r, center_r + 1):
            for dx in range(-center_r, center_r + 1):
                if dy * dy + dx * dx <= center_r * center_r:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        return grid

    def _generate_tree(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a tree of life motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)
        cy, cx = size // 2, size // 2

        # Trunk
        trunk_w = max(2, size // 12)
        trunk_top = size // 4
        trunk_bot = size - size // 6
        for y in range(trunk_top, trunk_bot):
            taper = 1 - (y - trunk_top) / (trunk_bot - trunk_top) * 0.3
            w = int(trunk_w * taper)
            for dx in range(-w, w + 1):
                px = cx + dx
                if 0 <= px < size:
                    grid[y, px] = colors[0]

        # Canopy (multiple circles)
        canopy_centers = [
            (size // 4, cx, size // 5),
            (size // 3, cx - size // 5, size // 6),
            (size // 3, cx + size // 5, size // 6),
            (size // 5, cx - size // 6, size // 7),
            (size // 5, cx + size // 6, size // 7),
        ]
        for cy_c, cx_c, r in canopy_centers:
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dy * dy + dx * dx <= r * r:
                        py, px = cy_c + dy, cx_c + dx
                        if 0 <= py < size and 0 <= px < size:
                            grid[py, px] = colors[1]

        return grid

    # ── Spiritual Motifs ─────────────────────────────────

    def _generate_spirit_gate(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a spirit gate motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)

        # Pillars
        pillar_w = max(2, size // 10)
        pillar_x1 = size // 4
        pillar_x2 = size * 3 // 4

        for x in [pillar_x1, pillar_x2]:
            for dy in range(size // 4, size * 3 // 4):
                for dx in range(-pillar_w, pillar_w + 1):
                    px = x + dx
                    if 0 <= px < size:
                        grid[dy, px] = colors[0]

        # Lintel
        lintel_y = size // 4
        lintel_h = max(2, size // 10)
        for dy in range(lintel_h):
            for x in range(pillar_x1, pillar_x2 + 1):
                if 0 <= x < size:
                    grid[lintel_y + dy, x] = colors[1]

        # Roof decorations
        for x in range(pillar_x1, pillar_x2 + 1, max(2, size // 15)):
            for dy in range(-size // 8, 0):
                py = lintel_y + dy
                if 0 <= py < size:
                    grid[py, x] = colors[2]

        return grid

    def _generate_sun(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a sun motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)
        cy, cx = size // 2, size // 2

        # Sun disk
        disk_r = size // 4
        for dy in range(-disk_r, disk_r + 1):
            for dx in range(-disk_r, disk_r + 1):
                if dy * dy + dx * dx <= disk_r * disk_r:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Rays
        num_rays = 12
        ray_len = size // 4
        for r in range(num_rays):
            angle = (r / num_rays) * math.pi * 2
            for l in range(disk_r, disk_r + ray_len):
                rx = cx + int(l * math.cos(angle))
                ry = cy + int(l * math.sin(angle))
                if 0 <= ry < size and 0 <= rx < size:
                    grid[ry, rx] = colors[1]

        return grid

    def _generate_moon(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a moon/crescent motif."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 2)
        cy, cx = size // 2, size // 2
        outer_r = size // 3
        inner_r = size // 4

        for dy in range(-outer_r, outer_r + 1):
            for dx in range(-outer_r, outer_r + 1):
                dist_sq = dy * dy + dx * dx
                if outer_r * outer_r >= dist_sq >= inner_r * inner_r:
                    # Crescent shape: offset inner circle
                    inner_dist = dy * dy + (dx - inner_r // 2) ** 2
                    if inner_dist > inner_r * inner_r:
                        py, px = cy + dy, cx + dx
                        if 0 <= py < size and 0 <= px < size:
                            grid[py, px] = colors[0]

        return grid

    def _generate_sacred_geometry(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate sacred geometry pattern."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)
        cy, cx = size // 2, size // 2
        max_r = size // 2 - 2

        # Concentric circles with DNA-driven radii
        seq = features.sequence
        num_circles = 5 + int(features.complexity_score * 5)

        for c in range(num_circles):
            r = int((c + 1) / num_circles * max_r)
            color_idx = c % len(colors)

            for angle in range(360):
                rad = angle * math.pi / 180
                px = cx + int(r * math.cos(rad))
                py = cy + int(r * math.sin(rad))
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[color_idx]

        # Inner star pattern
        num_points = 6
        for p in range(num_points):
            angle = (p / num_points) * math.pi * 2 - math.pi / 2
            for l in range(0, max_r, 2):
                px = cx + int(l * math.cos(angle))
                py = cy + int(l * math.sin(angle))
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[-1]

        return grid

    # ── Clan/Spirit Marks ────────────────────────────────

    def _generate_clan_mark(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a clan mark from DNA sequence hash."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)

        # Deterministic from sequence
        h = hash(features.sequence) % (size * size)
        seed_val = h

        # Generate unique pattern from hash
        self.rng.seed(seed_val)

        # Central symbol
        sym_size = size // 3
        cy, cx = size // 2, size // 2

        # Diamond base
        for dy in range(-sym_size, sym_size + 1):
            for dx in range(-sym_size, sym_size + 1):
                if abs(dy) + abs(dx) <= sym_size:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Inner pattern from DNA bases
        seq = features.sequence
        for dy in range(-sym_size // 2, sym_size // 2 + 1):
            for dx in range(-sym_size // 2, sym_size // 2 + 1):
                if abs(dy) + abs(dx) <= sym_size // 2:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        idx = (dy + sym_size // 2) * (sym_size + 1) + dx + sym_size // 2
                        if idx < len(seq):
                            if seq[idx] in "GC":
                                grid[py, px] = colors[1]

        # Corner marks
        corners = [(size // 6, size // 6), (size * 5 // 6, size // 6),
                   (size // 6, size * 5 // 6), (size * 5 // 6, size * 5 // 6)]
        for cy_c, cx_c in corners:
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    py, px = cy_c + dy, cx_c + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[2]

        return grid

    def _generate_ancestor_mark(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate an ancestor mark."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 3)
        cy, cx = size // 2, size // 2

        # Vertical figure (simplified human)
        # Head
        head_r = size // 8
        for dy in range(-head_r, head_r + 1):
            for dx in range(-head_r, head_r + 1):
                if dy * dy + dx * dx <= head_r * head_r:
                    py, px = cy - size // 4 + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Body
        body_w = max(1, size // 12)
        for dy in range(-size // 6, size // 6):
            for dx in range(-body_w, body_w + 1):
                py, px = cy + dy, cx + dx
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[0]

        # Arms
        arm_w = size // 4
        for dx in range(-arm_w, arm_w + 1):
            py = cy - size // 8
            px = cx + dx
            if 0 <= py < size and 0 <= px < size:
                grid[py, px] = colors[1]

        # Legs
        for dx in range(-arm_w // 2, arm_w // 2 + 1, max(1, arm_w // 4)):
            for dy in range(size // 6):
                py = cy + size // 6 + dy
                px = cx + dx
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[0]

        return grid

    # ── Symbol Generators ────────────────────────────────

    def _generate_totem(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a totem pole symbol."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)

        # Pole base
        pole_w = size // 5
        for y in range(size):
            for dx in range(-pole_w, pole_w + 1):
                px = size // 2 + dx
                if 0 <= px < size:
                    grid[y, px] = colors[0]

        # Faces stacked vertically
        num_faces = 3 + int(features.complexity_score * 3)
        face_h = size // num_faces

        for f in range(num_faces):
            fy = f * face_h + face_h // 2
            # Eyes
            eye_r = max(1, size // 20)
            for dy in range(-eye_r, eye_r + 1):
                for dx in range(-eye_r, eye_r + 1):
                    if dy * dy + dx * dx <= eye_r * eye_r:
                        for side in [-1, 1]:
                            py, px = fy + dy, size // 2 + side * (pole_w // 3) + dx
                            if 0 <= py < size and 0 <= px < size:
                                grid[py, px] = colors[1]

            # Mouth
            mouth_y = fy + pole_w // 4
            for dx in range(-pole_w // 3, pole_w // 3 + 1):
                px = size // 2 + dx
                if 0 <= px < size:
                    grid[mouth_y, px] = colors[2]

        return grid

    def _generate_mandala(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a mandala symbol."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 5)
        cy, cx = size // 2, size // 2
        max_r = size // 2 - 2

        seq = features.sequence

        # Radial symmetry layers
        num_layers = 4 + int(features.complexity_score * 4)
        num_segments = 8

        for layer in range(num_layers):
            r_inner = int(layer / num_layers * max_r)
            r_outer = int((layer + 1) / num_layers * max_r)

            for segment in range(num_segments):
                angle_start = (segment / num_segments) * math.pi * 2
                angle_end = ((segment + 1) / num_segments) * math.pi * 2

                color_idx = (layer + segment) % len(colors)

                for r in range(r_inner, r_outer + 1):
                    for angle_int in range(int(angle_start * 180 / math.pi),
                                          int(angle_end * 180 / math.pi) + 1):
                        rad = angle_int * math.pi / 180
                        px = cx + int(r * math.cos(rad))
                        py = cy + int(r * math.sin(rad))
                        if 0 <= py < size and 0 <= px < size:
                            # DNA drives color variation
                            idx = (r + segment * 10 + layer * 20) % len(seq)
                            if seq[idx] in "GC" and layer % 2 == 0:
                                grid[py, px] = colors[(color_idx + 1) % len(colors)]
                            else:
                                grid[py, px] = colors[color_idx]

        # Center point
        center_r = max(2, size // 15)
        for dy in range(-center_r, center_r + 1):
            for dx in range(-center_r, center_r + 1):
                if dy * dy + dx * dx <= center_r * center_r:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[-1]

        return grid

    def _generate_clan_shield(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a clan shield symbol."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)
        cy, cx = size // 2, size // 2

        # Shield shape
        shield_h = size * 2 // 3
        shield_w = size // 2
        shield_top = size // 6

        for dy in range(shield_h):
            y = shield_top + dy
            # Width varies: wide at top, narrow at bottom
            progress = dy / shield_h
            if progress < 0.5:
                width = int(shield_w * (0.5 + progress))
            else:
                width = int(shield_w * (1.5 - progress))

            for dx in range(-width, width + 1):
                px = cx + dx
                if 0 <= px < size:
                    # Color from DNA
                    idx = (dy * width + dx) % len(features.sequence)
                    color_idx = {"A": 0, "T": 1, "G": 2, "C": 3}[features.sequence[idx]]
                    grid[y, px] = colors[color_idx]

        # Inner symbol
        inner_r = shield_w // 3
        for dy in range(-inner_r, inner_r + 1):
            for dx in range(-inner_r, inner_r + 1):
                if dy * dy + dx * dx <= inner_r * inner_r:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[-1]

        return grid

    def _generate_spirit_mask(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a spirit mask symbol."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)
        cy, cx = size // 2, size // 2

        # Face (oval)
        face_rx, face_ry = size // 3, size // 2
        for dy in range(-face_ry, face_ry + 1):
            for dx in range(-face_rx, face_rx + 1):
                if (dx / face_rx) ** 2 + (dy / face_ry) ** 2 < 1:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[0]

        # Eyes (almond shape)
        for side in [-1, 1]:
            eye_cx = cx + side * face_rx // 3
            eye_ry = face_ry // 5
            eye_rx = face_rx // 4
            for dy in range(-eye_ry, eye_ry + 1):
                for dx in range(-eye_rx, eye_rx + 1):
                    if (dx / eye_rx) ** 2 + (dy / eye_ry) ** 2 < 1:
                        py, px = (cy - face_ry // 4) + dy, eye_cx + dx
                        if 0 <= py < size and 0 <= px < size:
                            grid[py, px] = colors[1]

        # Mouth
        mouth_y = cy + face_ry // 4
        mouth_w = face_rx // 3
        for dx in range(-mouth_w, mouth_w + 1):
            for dy in range(-2, 3):
                px = cx + dx
                py = mouth_y + dy
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[2]

        # Forehead pattern
        for dy in range(-face_ry, -face_ry // 2):
            for dx in range(-face_rx // 2, face_rx // 2):
                if abs(dx) + abs(dy) < face_rx // 2:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        idx = (dy + face_ry) * face_rx + dx + face_rx
                        if idx < len(features.sequence) and features.sequence[idx] in "GC":
                            grid[py, px] = colors[3]

        return grid

    def _generate_cosmic_diagram(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a cosmic diagram symbol."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 5)
        cy, cx = size // 2, size // 2
        max_r = size // 2 - 2

        # Outer circle
        for angle in range(360):
            rad = angle * math.pi / 180
            px = cx + int(max_r * math.cos(rad))
            py = cy + int(max_r * math.sin(rad))
            if 0 <= py < size and 0 <= px < size:
                grid[py, px] = colors[0]

        # Inner circles (worlds)
        for r in [max_r * 2 // 3, max_r // 3]:
            for angle in range(360):
                rad = angle * math.pi / 180
                px = cx + int(r * math.cos(rad))
                py = cy + int(r * math.sin(rad))
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[1]

        # Cross axes
        for axis in range(4):
            angle = axis * math.pi / 2
            for r in range(0, max_r, 2):
                px = cx + int(r * math.cos(angle))
                py = cy + int(r * math.sin(angle))
                if 0 <= py < size and 0 <= px < size:
                    grid[py, px] = colors[2]

        # Center
        center_r = max(2, size // 12)
        for dy in range(-center_r, center_r + 1):
            for dx in range(-center_r, center_r + 1):
                if dy * dy + dx * dx <= center_r * center_r:
                    py, px = cy + dy, cx + dx
                    if 0 <= py < size and 0 <= px < size:
                        grid[py, px] = colors[-1]

        # DNA-driven markers
        seq = features.sequence
        for i, base in enumerate(seq[:12]):
            angle = (i / 12) * math.pi * 2
            r = max_r * 0.6
            px = cx + int(r * math.cos(angle))
            py = cy + int(r * math.sin(angle))
            if 0 <= py < size and 0 <= px < size:
                grid[py, px] = colors[3]

        return grid

    def _generate_story_panel(self, features: DNAFeatures, size: int) -> np.ndarray:
        """Generate a narrative story panel."""
        grid = np.zeros((size, size, 3), dtype=np.uint8)
        colors = self._get_motif_colors(features, 4)

        # Divide into scenes
        num_scenes = 3 + int(features.complexity_score * 3)
        scene_w = size // num_scenes

        seq = features.sequence
        scene_types = ["diamond", "wave", "spiral", "triangle", "lotus", "zigzag"]

        for s in range(num_scenes):
            scene_start = s * scene_w
            scene_end = min((s + 1) * scene_w, size)

            # Scene background
            bg_color = colors[s % len(colors)]
            grid[:, scene_start:scene_end] = bg_color

            # Scene motif
            motif_type = scene_types[s % len(scene_types)]
            motif = self.generate_motif(features, motif_type, scene_w)
            grid[:, scene_start:scene_end] = self._blend(
                grid[:, scene_start:scene_end],
                motif,
                0.6,
                "over"
            )

        return grid

    # ── Helpers ──────────────────────────────────────────

    def _get_motif_colors(self, features: DNAFeatures, count: int) -> List[Tuple[int, int, int]]:
        """Get colors for a motif based on DNA features."""
        from .color_palette import get_all_colors
        palette = get_all_colors(self.community)
        if not palette:
            palette = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 255, 255)]

        colors = []
        for i in range(count):
            # Use DNA to select colors
            idx = int(features.gc_content * (len(palette) - 1) * (i + 1) / count)
            idx = idx % len(palette)
            colors.append(palette[idx])
        return colors

    def _blend(self, base: np.ndarray, overlay: np.ndarray, opacity: float, mode: str) -> np.ndarray:
        """Blend two layers."""
        if mode == "multiply":
            blended = (base.astype(np.float32) * overlay.astype(np.float32) / 255.0)
        elif mode == "screen":
            blended = 255 - (255 - base.astype(np.float32)) * (255 - overlay.astype(np.float32)) / 255.0
        else:  # over
            blended = base.astype(np.float32) * (1 - opacity) + overlay.astype(np.float32) * opacity
        return np.clip(blended, 0, 255).astype(np.uint8)
