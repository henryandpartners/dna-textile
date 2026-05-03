"""Exporters — PNG image, Jacquard (.jac) weave file, and sewing pattern output."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from typing import Optional, Tuple

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


class Exporter:
    """Thin wrapper for exporter functions."""

    def __init__(self):
        pass

    def export_png(self, pattern: list, output_path: str, **kwargs) -> bool:
        try:
            arr = np.array(pattern, dtype=np.uint8)
            if arr.ndim == 2:
                # Convert indexed to RGB
                colors = kwargs.get("colors", None)
                if colors:
                    rgb = np.zeros((*arr.shape, 3), dtype=np.uint8)
                    for i, c in enumerate(colors):
                        rgb[arr == i] = c
                    arr = rgb
                else:
                    arr = np.stack([arr] * 3, axis=-1)
            export_png(arr, output_path)
            return True
        except Exception:
            return False

    def export_jac(self, pattern: list, output_path: str, **kwargs) -> bool:
        try:
            arr = np.array(pattern, dtype=np.uint8)
            if arr.ndim == 2:
                arr = np.stack([arr] * 3, axis=-1)
            export_jac(arr, output_path)
            return True
        except Exception:
            return False

    def export_txt(self, pattern: list, output_path: str, **kwargs) -> bool:
        try:
            arr = np.array(pattern, dtype=np.uint8)
            if arr.ndim == 2:
                arr = np.stack([arr] * 3, axis=-1)
            delimiter = kwargs.get("delimiter", "\t")
            metadata = kwargs.get("metadata", None)
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w") as fh:
                if metadata:
                    fh.write(json.dumps(metadata) + "\n")
                for r in range(arr.shape[0]):
                    row_vals = []
                    for c in range(arr.shape[1]):
                        row_vals.append(str(int(arr[r, c, 0])))
                    fh.write(delimiter.join(row_vals) + "\n")
            return True
        except Exception:
            return False


def export_punch_card(
    grid: np.ndarray,
    output_path: str | Path,
    stitch_ratio: float = 1.0,
    cell_size: int = 12,
    show_grid: bool = True,
    show_numbers: bool = True,
    repeat_size: Optional[int] = None,
) -> Path:
    """
    Export a color grid as a punch card chart PNG.

    Renders as a high-contrast black/white grid (like Rosie's generative
    knitting tool). Each cell represents one pixel on a knitting machine.
    Includes grid lines, row/column numbers, and repeat boundaries.

    Args:
        grid:        Color grid (H×W×3 uint8).
        output_path: Destination PNG file path.
        stitch_ratio: Aspect ratio for stitches (width:height). Default 1.0;
                      typical knitting ~0.85 (stitches wider than tall).
        cell_size:   Pixel size of each cell in the output image.
        show_grid:   Whether to draw grid lines between cells.
        show_numbers: Whether to show row/column numbers.
        repeat_size: If set, draw repeat boundary lines every N cells.

    Returns:
        Resolved Path to the written file.
    """
    from typing import Optional as _Opt
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    h, w = grid.shape[:2]

    # Apply stitch ratio: scale cell height
    cell_h = max(4, int(cell_size * stitch_ratio))
    cell_w = cell_size

    # Calculate image dimensions
    margin = 30 if show_numbers else 5
    img_w = margin * 2 + w * cell_w
    img_h = margin * 2 + h * cell_h

    # Create image (white background)
    img = Image.new("RGB", (img_w, img_h), (255, 255, 255))

    # Try to import ImageDraw
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        # Try to load a monospace font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 8)
        except (IOError, OSError):
            font = ImageFont.load_default()
    except ImportError:
        draw = None
        font = None

    # Convert grid to binary (dark vs light) for punch card
    # A cell is "punched" (black) if its luminance is below threshold
    def _luminance(rgb):
        return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

    for r in range(h):
        for c in range(w):
            rgb = tuple(int(x) for x in grid[r, c])
            lum = _luminance(rgb)
            # Threshold: dark cells become black (punched), light cells stay white
            color = (0, 0, 0) if lum < 128 else (255, 255, 255)

            x0 = margin + c * cell_w
            y0 = margin + r * cell_h
            x1 = x0 + cell_w - 1
            y1 = y0 + cell_h - 1

            if draw:
                draw.rectangle([x0, y0, x1, y1], fill=color)
            else:
                # Fallback: pixel-level drawing
                for dy in range(y0, min(y1 + 1, img_h)):
                    for dx in range(x0, min(x1 + 1, img_w)):
                        img.putpixel((dx, dy), color)

    # Draw grid lines
    if show_grid and draw:
        for r in range(h + 1):
            y = margin + r * cell_h
            draw.line([(margin, y), (margin + w * cell_w, y)], fill=(200, 200, 200), width=1)
        for c in range(w + 1):
            x = margin + c * cell_w
            draw.line([(x, margin), (x, margin + h * cell_h)], fill=(200, 200, 200), width=1)

    # Draw repeat boundaries
    if repeat_size and repeat_size > 0 and draw:
        for r in range(0, h + 1, repeat_size):
            y = margin + r * cell_h
            draw.line([(margin, y), (margin + w * cell_w, y)], fill=(255, 0, 0), width=2)
        for c in range(0, w + 1, repeat_size):
            x = margin + c * cell_w
            draw.line([(x, margin), (x, margin + h * cell_h)], fill=(255, 0, 0), width=2)

    # Draw row/column numbers
    if show_numbers and draw:
        for r in range(h):
            y = margin + r * cell_h + cell_h // 2 - 4
            text = str(r + 1)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((margin - tw - 4, y), text, fill=(0, 0, 0), font=font)
        for c in range(w):
            x = margin + c * cell_w + cell_w // 2 - 3
            text = str(c + 1)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((x, margin - 12), text, fill=(0, 0, 0), font=font)

    img.save(path)
    return path.resolve()


def export_punch_card_csv(
    grid: np.ndarray,
    output_path: str | Path,
    stitch_ratio: float = 1.0,
) -> Path:
    """
    Export a color grid as a CSV file for digital knitting machine loading.

    Each row in the CSV represents one row of the pattern.
    Each cell is 0 (light/no punch) or 1 (dark/punch).

    Args:
        grid:        Color grid (H×W×3 uint8).
        output_path: Destination CSV file path.
        stitch_ratio: Aspect ratio (stored as metadata in CSV header).

    Returns:
        Resolved Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    h, w = grid.shape[:2]

    def _luminance(rgb):
        return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        # Header with metadata
        writer.writerow(["# PUNCH_CARD_CSV"])
        writer.writerow([f"WIDTH={w}"])
        writer.writerow([f"HEIGHT={h}"])
        writer.writerow([f"STITCH_RATIO={stitch_ratio}"])
        writer.writerow(["# 0=light, 1=dark"])

        for r in range(h):
            row_vals = []
            for c in range(w):
                rgb = tuple(int(x) for x in grid[r, c])
                lum = _luminance(rgb)
                row_vals.append("1" if lum < 128 else "0")
            writer.writerow(row_vals)

    return path.resolve()


def export_lace_chart(
    grid: np.ndarray,
    output_path: str | Path,
    cell_size: int = 14,
    show_grid: bool = True,
    show_numbers: bool = True,
) -> Path:
    """
    Export a lace chart with eyelet symbols.

    Renders a lace pattern chart where holes are shown as circles (eyelets)
    and solid areas as filled squares. Suitable for hand-knitting lace charts.

    Args:
        grid:       Color grid (H×W×3 uint8). White cells = holes.
        output_path: Destination PNG file path.
        cell_size:  Pixel size of each cell.
        show_grid:  Whether to draw grid lines.
        show_numbers: Whether to show row/column numbers.

    Returns:
        Resolved Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    h, w = grid.shape[:2]
    margin = 30 if show_numbers else 5
    img_w = margin * 2 + w * cell_size
    img_h = margin * 2 + h * cell_size

    img = Image.new("RGB", (img_w, img_h), (255, 255, 255))

    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 8)
        except (IOError, OSError):
            font = ImageFont.load_default()
    except ImportError:
        draw = None
        font = None

    # Determine if a cell is a hole (white/light)
    def _is_hole(rgb):
        return rgb[0] > 200 and rgb[1] > 200 and rgb[2] > 200

    for r in range(h):
        for c in range(w):
            rgb = tuple(int(x) for x in grid[r, c])
            x0 = margin + c * cell_size
            y0 = margin + r * cell_size

            if draw:
                if _is_hole(rgb):
                    # Eyelet symbol: circle
                    radius = cell_size // 2 - 2
                    cx = x0 + cell_size // 2
                    cy = y0 + cell_size // 2
                    draw.ellipse(
                        [cx - radius, cy - radius, cx + radius, cy + radius],
                        outline=(0, 0, 0),
                        width=2,
                    )
                else:
                    # Solid: filled square
                    draw.rectangle(
                        [x0, y0, x0 + cell_size - 1, y0 + cell_size - 1],
                        fill=(60, 60, 60),
                    )

    # Grid lines
    if show_grid and draw:
        for r in range(h + 1):
            y = margin + r * cell_size
            draw.line([(margin, y), (margin + w * cell_size, y)], fill=(200, 200, 200), width=1)
        for c in range(w + 1):
            x = margin + c * cell_size
            draw.line([(x, margin), (x, margin + h * cell_size)], fill=(200, 200, 200), width=1)

    # Numbers
    if show_numbers and draw:
        for r in range(h):
            y = margin + r * cell_size + cell_size // 2 - 4
            text = str(r + 1)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((margin - tw - 4, y), text, fill=(0, 0, 0), font=font)
        for c in range(w):
            x = margin + c * cell_size + cell_size // 2 - 3
            text = str(c + 1)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((x, margin - 12), text, fill=(0, 0, 0), font=font)

    img.save(path)
    return path.resolve()


def export_sewing_pattern(
    sewing_data: dict,
    output_path: str | Path,
    community: str = "generic",
    garment_name: str = "default",
    size: str = "M",
    seam_allowance_cm: float = 1.0,
    fabric_width_cm: float = 150.0,
) -> Path:
    """
    Export sewing pattern package as a ZIP file.

    Args:
        sewing_data:       Dict from Pipeline with sewing pattern data.
        output_path:       Destination .zip file path.
        community:         Community name.
        garment_name:      Garment template name.
        size:              Garment size (S/M/L/XL).
        seam_allowance_cm: Seam allowance in cm.
        fabric_width_cm:   Fabric width in cm.

    Returns:
        Resolved Path to the written ZIP file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Pattern pieces SVGs
        pieces = sewing_data.get("pieces", [])
        for piece in pieces:
            piece_name = piece.get("name", "unknown")
            svg_content = piece.get("svg", "")
            if svg_content:
                zf.writestr(f"pieces/{piece_name}.svg", svg_content)

        # Cutting layout SVG
        layout_svg = sewing_data.get("layout_svg", "")
        if layout_svg:
            zf.writestr("cutting_layout.svg", layout_svg)

        # Measurements
        measurements = sewing_data.get("measurements", {})
        if measurements:
            zf.writestr("measurements.json", json.dumps(measurements, indent=2))

        # Assembly instructions
        instructions = sewing_data.get("instructions", "")
        if instructions:
            zf.writestr("assembly_instructions.txt", instructions)

        # Cutting instructions
        cutting_instr = sewing_data.get("cutting_instructions", "")
        if cutting_instr:
            zf.writestr("cutting_instructions.txt", cutting_instr)

        # Metadata
        metadata = {
            "community": community,
            "garment": garment_name,
            "size": size,
            "seam_allowance_cm": seam_allowance_cm,
            "fabric_width_cm": fabric_width_cm,
            "piece_count": len(pieces),
        }
        zf.writestr("metadata.json", json.dumps(metadata, indent=2))

    return path.resolve()
