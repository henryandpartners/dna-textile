"""
Pattern Warper — warp flat patterns onto curved garment surfaces.

Uses numpy array operations for UV coordinate transformations to simulate
how fabric wraps around body parts (cylindrical, conical, drape effects).
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np


class PatternWarper:
    """Warp flat 2D patterns to simulate curved garment surfaces."""

    def warp_to_region(
        self,
        grid: np.ndarray,
        region_shape: Tuple[int, int],
        warp_type: str = "flat",
        **kwargs,
    ) -> np.ndarray:
        """
        Warp a pattern grid to fit a body region shape.

        Args:
            grid: Input pattern grid (H×W×3 uint8).
            region_shape: Target (height, width) for output.
            warp_type: One of "flat", "cylindrical", "conical", "drape".
            **kwargs: Warp-specific parameters.

        Returns:
            Warped grid of shape region_shape + (3,).
        """
        h, w = region_shape
        src_h, src_w = grid.shape[:2]

        if warp_type == "flat":
            return self._warp_flat(grid, h, w)
        elif warp_type == "cylindrical":
            curvature = kwargs.get("curvature", 0.5)
            return self.apply_cylindrical_warp(grid, curvature, h, w)
        elif warp_type == "conical":
            angle = kwargs.get("angle", 45)
            return self.apply_conical_warp(grid, angle, h, w)
        elif warp_type == "drape":
            gravity = kwargs.get("gravity_direction", "down")
            return self.apply_drape_warp(grid, gravity, h, w)
        else:
            raise ValueError(f"Unknown warp_type: {warp_type!r}")

    def _warp_flat(self, grid: np.ndarray, h: int, w: int) -> np.ndarray:
        """Resize grid to target shape using bilinear interpolation."""
        src_h, src_w = grid.shape[:2]
        result = np.zeros((h, w, 3), dtype=np.uint8)

        for dy in range(h):
            for dx in range(w):
                # Map target coords to source coords
                sy = dy * src_h / h
                sx = dx * src_w / w

                # Bilinear interpolation
                y0 = int(sy)
                x0 = int(sx)
                y1 = min(y0 + 1, src_h - 1)
                x1 = min(x0 + 1, src_w - 1)

                fy = sy - y0
                fx = sx - x0

                for c in range(3):
                    v00 = grid[y0, x0, c]
                    v10 = grid[y1, x0, c]
                    v01 = grid[y0, x1, c]
                    v11 = grid[y1, x1, c]

                    v0 = v00 * (1 - fx) + v01 * fx
                    v1 = v10 * (1 - fx) + v11 * fx
                    result[dy, dx, c] = int(v0 * (1 - fy) + v1 * fy)

        return result

    def apply_cylindrical_warp(
        self,
        grid: np.ndarray,
        curvature: float = 0.5,
        target_h: Optional[int] = None,
        target_w: Optional[int] = None,
    ) -> np.ndarray:
        """
        Simulate fabric wrapped around a cylindrical body part.

        Horizontal compression at edges (like fabric curving away from viewer).

        Args:
            grid: Input pattern grid (H×W×3 uint8).
            curvature: 0-1, how much edge compression (0 = flat, 1 = full cylinder).
            target_h: Output height (default: same as input).
            target_w: Output width (default: same as input).

        Returns:
            Warped grid.
        """
        src_h, src_w = grid.shape[:2]
        h = target_h or src_h
        w = target_w or src_w
        result = np.zeros((h, w, 3), dtype=np.uint8)

        curvature = max(0.0, min(1.0, curvature))

        for dy in range(h):
            for dx in range(w):
                # Map target to source with cylindrical distortion
                # Center of cylinder is at x=0.5, edges compress
                nx = dx / max(w - 1, 1)  # normalized x: 0-1

                # Cylindrical mapping: cos-based compression at edges
                angle = nx * math.pi  # 0 to pi
                compressed_x = 0.5 + (math.cos(angle) * curvature * 0.3 + (1 - curvature) * (nx - 0.5))
                compressed_x = max(0.0, min(1.0, compressed_x))

                ny = dy / max(h - 1, 1)

                # Map back to source coords
                sx = compressed_x * src_w
                sy = ny * src_h

                # Clamp and sample
                sx = max(0, min(src_w - 1, sx))
                sy = max(0, min(src_h - 1, sy))

                sx0 = int(sx)
                sy0 = int(sy)
                sx1 = min(sx0 + 1, src_w - 1)
                sy1 = min(sy0 + 1, src_h - 1)

                fx = sx - sx0
                fy = sy - sy0

                for c in range(3):
                    v00 = grid[sy0, sx0, c]
                    v10 = grid[sy1, sx0, c]
                    v01 = grid[sy0, sx1, c]
                    v11 = grid[sy1, sx1, c]
                    v0 = v00 * (1 - fx) + v01 * fx
                    v1 = v10 * (1 - fx) + v11 * fx
                    result[dy, dx, c] = int(v0 * (1 - fy) + v1 * fy)

        return result

    def apply_conical_warp(
        self,
        grid: np.ndarray,
        angle: float = 45,
        target_h: Optional[int] = None,
        target_w: Optional[int] = None,
    ) -> np.ndarray:
        """
        Simulate a conical shape (for skirts, hats, headdresses).

        Radial expansion from center — top narrower, bottom wider.

        Args:
            grid: Input pattern grid (H×W×3 uint8).
            angle: Cone angle in degrees (0 = cylinder, 90 = flat disk).
            target_h: Output height.
            target_w: Output width.

        Returns:
            Warped grid.
        """
        src_h, src_w = grid.shape[:2]
        h = target_h or src_h
        w = target_w or src_w
        result = np.zeros((h, w, 3), dtype=np.uint8)

        angle_rad = math.radians(max(0, min(90, angle)))
        expansion_factor = 1.0 + math.tan(angle_rad) * 0.5

        for dy in range(h):
            # Vertical position affects horizontal scale
            progress = dy / max(h - 1, 1)
            # Top is narrow, bottom is wide
            h_scale = 1.0 + (expansion_factor - 1.0) * progress

            for dx in range(w):
                # Map to source with conical scaling
                nx = (dx / max(w - 1, 1) - 0.5) / h_scale + 0.5
                ny = dy / max(h - 1, 1)

                sx = max(0.0, min(1.0, nx)) * (src_w - 1)
                sy = ny * (src_h - 1)

                sx0 = int(sx)
                sy0 = int(sy)
                sx1 = min(sx0 + 1, src_w - 1)
                sy1 = min(sy0 + 1, src_h - 1)

                fx = sx - sx0
                fy = sy - sy0

                for c in range(3):
                    v00 = grid[sy0, sx0, c]
                    v10 = grid[sy1, sx0, c]
                    v01 = grid[sy0, sx1, c]
                    v11 = grid[sy1, sx1, c]
                    v0 = v00 * (1 - fx) + v01 * fx
                    v1 = v10 * (1 - fx) + v11 * fx
                    result[dy, dx, c] = int(v0 * (1 - fy) + v1 * fy)

        return result

    def apply_drape_warp(
        self,
        grid: np.ndarray,
        gravity_direction: str = "down",
        target_h: Optional[int] = None,
        target_w: Optional[int] = None,
    ) -> np.ndarray:
        """
        Simulate fabric hanging under gravity.

        Vertical stretch + horizontal compression.

        Args:
            grid: Input pattern grid (H×W×3 uint8).
            gravity_direction: "down", "left", "right", or "up".
            target_h: Output height.
            target_w: Output width.

        Returns:
            Warped grid.
        """
        src_h, src_w = grid.shape[:2]
        h = target_h or int(src_h * 1.2)  # Default: 20% vertical stretch
        w = target_w or int(src_w * 0.9)  # Default: 10% horizontal compression
        result = np.zeros((h, w, 3), dtype=np.uint8)

        # Direction vectors
        dir_map = {
            "down": (0, 1),
            "up": (0, -1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        dx_dir, dy_dir = dir_map.get(gravity_direction, (0, 1))

        for dy in range(h):
            for dx in range(w):
                # Gravity causes progressive distortion
                progress = (dy * dy_dir + dx * dx_dir) / max(h + w, 1)

                # Vertical stretch factor increases with gravity direction
                stretch = 1.0 + progress * 0.3
                squeeze = 1.0 - progress * 0.15

                # Map to source
                nx = (dx / max(w - 1, 1) - 0.5) / squeeze + 0.5
                ny = (dy / max(h - 1, 1) - 0.5) / stretch + 0.5

                sx = max(0.0, min(1.0, nx)) * (src_w - 1)
                sy = max(0.0, min(1.0, ny)) * (src_h - 1)

                sx0 = int(sx)
                sy0 = int(sy)
                sx1 = min(sx0 + 1, src_w - 1)
                sy1 = min(sy0 + 1, src_h - 1)

                fx = sx - sx0
                fy = sy - sy0

                for c in range(3):
                    v00 = grid[sy0, sx0, c]
                    v10 = grid[sy1, sx0, c]
                    v01 = grid[sy0, sx1, c]
                    v11 = grid[sy1, sx1, c]
                    v0 = v00 * (1 - fx) + v01 * fx
                    v1 = v10 * (1 - fx) + v11 * fx
                    result[dy, dx, c] = int(v0 * (1 - fy) + v1 * fy)

        return result
