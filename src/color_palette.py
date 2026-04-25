"""
Color Palette — manages traditional color palettes per community.

Phase 2: Loads color definitions from color_palettes.json and provides
utilities for color conversion, palette selection, and DNA-to-color mapping.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


_BASE_DIR = Path(__file__).resolve().parent.parent
_PALETTE_FILE = _BASE_DIR / "color_palettes.json"

# In-memory cache
_PALETTE_DATA: Optional[Dict[str, Any]] = None


def _load_palettes() -> Dict[str, Any]:
    """Load color palette data from JSON."""
    global _PALETTE_DATA
    if _PALETTE_DATA is not None:
        return _PALETTE_DATA

    if not _PALETTE_FILE.exists():
        _PALETTE_DATA = {"palettes": {}, "global_defaults": {"dna_color_map": {}}}
        return _PALETTE_DATA

    with open(_PALETTE_FILE, "r", encoding="utf-8") as f:
        _PALETTE_DATA = json.load(f)

    return _PALETTE_DATA


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))  # type: ignore


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def get_community_palette(community: str) -> Optional[Dict[str, Any]]:
    """Get the full color palette for a community."""
    data = _load_palettes()
    key = community.lower().replace(" ", "_")
    return data.get("palettes", {}).get(key)


def get_primary_colors(community: str) -> List[Tuple[int, int, int]]:
    """Get primary colors for a community as RGB tuples."""
    palette = get_community_palette(community)
    if not palette:
        return [(0, 0, 0)]
    hex_colors = palette.get("primary", ["#000000"])
    return [hex_to_rgb(c) for c in hex_colors]


def get_secondary_colors(community: str) -> List[Tuple[int, int, int]]:
    """Get secondary colors for a community as RGB tuples."""
    palette = get_community_palette(community)
    if not palette:
        return [(128, 128, 128)]
    hex_colors = palette.get("secondary", ["#808080"])
    return [hex_to_rgb(c) for c in hex_colors]


def get_accent_colors(community: str) -> List[Tuple[int, int, int]]:
    """Get accent colors for a community as RGB tuples."""
    palette = get_community_palette(community)
    if not palette:
        return [(255, 255, 255)]
    hex_colors = palette.get("accent", ["#FFFFFF"])
    return [hex_to_rgb(c) for c in hex_colors]


def get_all_colors(community: str) -> List[Tuple[int, int, int]]:
    """Get all colors for a community."""
    palette = get_community_palette(community)
    if not palette:
        return [(0, 0, 0), (128, 128, 128), (255, 255, 255)]
    all_hex = (
        palette.get("primary", []) +
        palette.get("secondary", []) +
        palette.get("accent", [])
    )
    return [hex_to_rgb(c) for c in all_hex]


def get_color_info(community: str, color_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed info about a specific color in a community's palette."""
    palette = get_community_palette(community)
    if not palette:
        return None
    for color in palette.get("colors", []):
        if color.get("name") == color_name:
            return color
    return None


def get_dna_color_map() -> Dict[str, Tuple[int, int, int]]:
    """Get the default DNA nucleotide to RGB color mapping."""
    data = _load_palettes()
    dna_map = data.get("global_defaults", {}).get("dna_color_map", {})
    result = {}
    for base, info in dna_map.items():
        if isinstance(info, dict) and "rgb" in info:
            result[base] = tuple(info["rgb"])  # type: ignore
        elif isinstance(info, dict) and "hex" in info:
            result[base] = hex_to_rgb(info["hex"])
    return result


def apply_palette_to_grid(
    grid: np.ndarray,
    community: str,
    source_color_map: Optional[Dict[str, Tuple[int, int, int]]] = None,
) -> np.ndarray:
    """
    Remap grid colors to community palette.

    Args:
        grid: Input color grid (H×W×3 uint8).
        community: Target community for palette.
        source_color_map: Optional mapping of original colors to nucleotides.

    Returns:
        Remapped color grid.
    """
    palette_colors = get_all_colors(community)
    if not palette_colors:
        return grid

    result = grid.copy()
    h, w = grid.shape[:2]

    # Find closest palette color for each pixel
    palette_arr = np.array(palette_colors, dtype=np.float32)

    for r in range(h):
        for c in range(w):
            pixel = grid[r, c].astype(np.float32)
            distances = np.sqrt(np.sum((palette_arr - pixel) ** 2, axis=1))
            closest_idx = np.argmin(distances)
            result[r, c] = palette_colors[closest_idx]

    return result


def list_available_palettes() -> List[str]:
    """List all available community palettes."""
    data = _load_palettes()
    return list(data.get("palettes", {}).keys())


def validate_palette(community: str) -> Tuple[bool, List[str]]:
    """Validate a community's color palette. Returns (is_valid, errors)."""
    palette = get_community_palette(community)
    errors = []
    if palette is None:
        return False, [f"No palette found for community: {community}"]

    for color in palette.get("colors", []):
        if "hex" not in color:
            errors.append(f"Color missing 'hex': {color.get('name', 'unknown')}")
        if "rgb" not in color:
            errors.append(f"Color missing 'rgb': {color.get('name', 'unknown')}")
        if "name" not in color:
            errors.append("Color missing 'name'")
        if "meaning" not in color:
            errors.append(f"Color '{color.get('name', 'unknown')}' missing cultural meaning")

    return (len(errors) == 0, errors)
