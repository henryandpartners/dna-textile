"""Exporters — PNG image and Jacquard (.jac) weave file output."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image


def export_png(grid: np.ndarray, output_path: str | Path) -> Path:
    """
    Save a color grid as a PNG image.

    Args:
        grid:        np.ndarray of shape (H, W, 3) dtype uint8.
        output_path: Destination file path.

    Returns:
        Resolved Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(grid, mode="RGB")
    img.save(path)
    return path.resolve()


def _rgb_to_jac_code(rgb: Tuple[int, int, int]) -> str:
    """
    Map an RGB color to a Jacquard thread code.

    Simple mapping: assign each unique color an integer thread ID.
    For a real Jacquard file you'd use a machine-specific palette.
    """
    # Deterministic hash based on RGB
    return str((rgb[0] * 31 + rgb[1] * 17 + rgb[2]) % 256)


def export_jac(
    grid: np.ndarray,
    output_path: str | Path,
    threads_per_row: int = 1,
) -> Path:
    """
    Export a color grid as a Jacquard-style CSV weave file (.jac).

    Each row in the output represents one pick (weft row).
    Each column represents a warp thread.
    Values are thread color codes.

    Args:
        grid:            Color grid (H×W×3 uint8).
        output_path:     Destination .jac file path.
        threads_per_row: Number of picks to combine per output row
                         (1 = one row per grid row).

    Returns:
        Resolved Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    h, w = grid.shape[:2]

    # Build a color→thread_id lookup
    color_map: dict[Tuple[int, int, int], int] = {}
    next_id = 1

    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        # Header
        writer.writerow([
            "JACQUARD_EXPORT",
            f"WIDTH={w}",
            f"HEIGHT={h}",
            f"THREADS_PER_ROW={threads_per_row}",
        ])

        for r in range(h):
            row_codes = []
            for c in range(w):
                rgb_tuple = tuple(int(x) for x in grid[r, c])
                if rgb_tuple not in color_map:
                    color_map[rgb_tuple] = next_id
                    next_id += 1
                row_codes.append(str(color_map[rgb_tuple]))
            writer.writerow(row_codes)

        # Palette section
        writer.writerow([])
        writer.writerow(["# PALETTE"])
        for color, tid in sorted(color_map.items(), key=lambda x: x[1]):
            writer.writerow([f"T{tid}", f"RGB({color[0]},{color[1]},{color[2]})"])

    return path.resolve()


def export_txt(
    grid: np.ndarray,
    output_path: str | Path,
) -> Path:
    """
    Export a color grid as a plain-text weave map.

    Each cell is a single character: A/T/G/C → mapped by dominant RGB.
    Useful for quick inspection.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Reverse color map
    reverse_map = {
        (255, 0, 0): "A",
        (0, 0, 255): "T",
        (0, 255, 0): "G",
        (255, 255, 0): "C",
    }

    with path.open("w") as fh:
        for r in range(grid.shape[0]):
            line = ""
            for c in range(grid.shape[1]):
                rgb = tuple(int(x) for x in grid[r, c])
                line += reverse_map.get(rgb, "?")
            fh.write(line + "\n")

    return path.resolve()
