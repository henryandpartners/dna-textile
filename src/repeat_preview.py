"""Pattern repeat preview — detect repeating units and generate tiled previews.

Useful for knitting machine planning: shows the smallest repeating unit
isolated, plus a tiled preview of multiple repeats.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def detect_repeat_unit(grid: np.ndarray, max_repeat: int = 50) -> Tuple[int, int]:
    """
    Detect the repeating unit size in a pattern grid.

    Uses autocorrelation to find the smallest repeating unit in both
    horizontal and vertical directions.

    Args:
        grid:       Color grid (H×W×3 uint8).
        max_repeat: Maximum repeat size to search for.

    Returns:
        Tuple of (repeat_width, repeat_height).
    """
    h, w = grid.shape[:2]
    max_repeat = min(max_repeat, h, w)

    # Convert to grayscale for correlation
    gray = np.mean(grid.astype(np.float64), axis=2)

    # Find horizontal repeat
    best_w = 1
    best_corr_w = 0.0
    for rw in range(1, max_repeat + 1):
        if rw * 2 > w:
            break
        # Compare first repeat unit with second
        unit1 = gray[:, :rw]
        unit2 = gray[:, rw:rw * 2]
        if unit1.shape == unit2.shape:
            corr = np.corrcoef(unit1.flatten(), unit2.flatten())[0, 1]
            if corr > best_corr_w:
                best_corr_w = corr
                best_w = rw

    # Find vertical repeat
    best_h = 1
    best_corr_h = 0.0
    for rh in range(1, max_repeat + 1):
        if rh * 2 > h:
            break
        unit1 = gray[:rh, :]
        unit2 = gray[rh:rh * 2, :]
        if unit1.shape == unit2.shape:
            corr = np.corrcoef(unit1.flatten(), unit2.flatten())[0, 1]
            if corr > best_corr_h:
                best_corr_h = corr
                best_h = rh

    # Only accept repeats with strong correlation
    if best_corr_w < 0.7:
        best_w = w
    if best_corr_h < 0.7:
        best_h = h

    return best_w, best_h


def export_repeat_isolated(
    grid: np.ndarray,
    output_path: str | Path,
    repeat_w: Optional[int] = None,
    repeat_h: Optional[int] = None,
    cell_size: int = 10,
) -> Path:
    """
    Export a single isolated repeat unit.

    Args:
        grid:       Color grid (H×W×3 uint8).
        output_path: Destination PNG file path.
        repeat_w:   Repeat width (auto-detected if None).
        repeat_h:   Repeat height (auto-detected if None).
        cell_size:  Pixel size per cell in output.

    Returns:
        Resolved Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if repeat_w is None or repeat_h is None:
        repeat_w, repeat_h = detect_repeat_unit(grid)

    # Extract repeat unit
    unit = grid[:repeat_h, :repeat_w, :]

    # Scale up for visibility
    img = Image.fromarray(unit, mode="RGB")
    new_w = repeat_w * cell_size
    new_h = repeat_h * cell_size
    img = img.resize((new_w, new_h), Image.NEAREST)

    # Add label
    try:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except (IOError, OSError):
            font = ImageFont.load_default()
        label = f"Repeat unit: {repeat_w}×{repeat_h}"
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.rectangle([0, 0, tw + 8, 18], fill=(255, 255, 255))
        draw.text((4, 2), label, fill=(0, 0, 0), font=font)
    except Exception:
        pass

    img.save(path)
    return path.resolve()


def export_repeat_tiled(
    grid: np.ndarray,
    output_path: str | Path,
    repeats_x: int = 3,
    repeats_y: int = 3,
    repeat_w: Optional[int] = None,
    repeat_h: Optional[int] = None,
    cell_size: int = 8,
) -> Path:
    """
    Export a tiled preview showing multiple repeats.

    Args:
        grid:       Color grid (H×W×3 uint8).
        output_path: Destination PNG file path.
        repeats_x:  Number of horizontal repeats.
        repeats_y:  Number of vertical repeats.
        repeat_w:   Repeat width (auto-detected if None).
        repeat_h:   Repeat height (auto-detected if None).
        cell_size:  Pixel size per cell in output.

    Returns:
        Resolved Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if repeat_w is None or repeat_h is None:
        repeat_w, repeat_h = detect_repeat_unit(grid)

    # Extract repeat unit
    unit = grid[:repeat_h, :repeat_w, :]

    # Create tiled image
    tile_w = repeat_w * cell_size
    tile_h = repeat_h * cell_size
    img_w = tile_w * repeats_x
    img_h = tile_h * repeats_y

    img = Image.new("RGB", (img_w, img_h), (255, 255, 255))

    for ry in range(repeats_y):
        for rx in range(repeats_x):
            unit_img = Image.fromarray(unit, mode="RGB")
            unit_img = unit_img.resize((tile_w, tile_h), Image.NEAREST)
            img.paste(unit_img, (rx * tile_w, ry * tile_h))

    # Draw repeat boundary lines
    try:
        draw = ImageDraw.Draw(img)
        for rx in range(repeats_x + 1):
            x = rx * tile_w
            draw.line([(x, 0), (x, img_h)], fill=(255, 0, 0), width=2)
        for ry in range(repeats_y + 1):
            y = ry * tile_h
            draw.line([(0, y), (img_w, y)], fill=(255, 0, 0), width=2)
    except Exception:
        pass

    # Add label
    try:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except (IOError, OSError):
            font = ImageFont.load_default()
        label = f"Tiled preview: {repeats_x}×{repeats_y} repeats ({repeat_w}×{repeat_h} unit)"
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.rectangle([0, 0, tw + 8, 18], fill=(255, 255, 255))
        draw.text((4, 2), label, fill=(0, 0, 0), font=font)
    except Exception:
        pass

    img.save(path)
    return path.resolve()


def export_repeat_analysis(
    grid: np.ndarray,
    output_dir: str | Path,
    prefix: str = "repeat",
) -> dict:
    """
    Generate full repeat analysis: isolated unit + tiled preview.

    Args:
        grid:      Color grid (H×W×3 uint8).
        output_dir: Directory for output files.
        prefix:    Filename prefix.

    Returns:
        Dict with paths and repeat dimensions.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    repeat_w, repeat_h = detect_repeat_unit(grid)

    isolated_path = export_repeat_isolated(
        grid, out / f"{prefix}_isolated.png",
        repeat_w=repeat_w, repeat_h=repeat_h,
    )

    tiled_path = export_repeat_tiled(
        grid, out / f"{prefix}_tiled.png",
        repeat_w=repeat_w, repeat_h=repeat_h,
    )

    return {
        "repeat_width": repeat_w,
        "repeat_height": repeat_h,
        "isolated_path": str(isolated_path),
        "tiled_path": str(tiled_path),
    }
