"""
Border Style — manages border types (woven, embroidered, printed).

Phase 2: Loads border style definitions from border_styles.json and provides
rendering functions for each border technique.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


_BASE_DIR = Path(__file__).resolve().parent.parent
_BORDER_FILE = _BASE_DIR / "border_styles.json"

_BORDER_DATA: Optional[Dict[str, Any]] = None


def _load_border_data() -> Dict[str, Any]:
    """Load border style data from JSON."""
    global _BORDER_DATA
    if _BORDER_DATA is not None:
        return _BORDER_DATA

    if not _BORDER_FILE.exists():
        _BORDER_DATA = {"styles": {}, "community_defaults": {}}
        return _BORDER_DATA

    with open(_BORDER_FILE, "r", encoding="utf-8") as f:
        _BORDER_DATA = json.load(f)

    return _BORDER_DATA


def get_border_style(style_key: str) -> Optional[Dict[str, Any]]:
    """Get border style definition by key (e.g., 'woven.solid')."""
    data = _load_border_data()
    styles = data.get("styles", {})
    parts = style_key.split(".")
    if len(parts) == 2:
        category, technique = parts
        cat_data = styles.get(category, {})
        techniques = cat_data.get("techniques", {})
        return techniques.get(technique)
    return None


def get_community_default_border(community: str) -> str:
    """Get the default border style for a community."""
    data = _load_border_data()
    key = community.lower().replace(" ", "_")
    return data.get("community_defaults", {}).get(key, "woven.solid")


def get_border_categories() -> List[str]:
    """List all border style categories."""
    data = _load_border_data()
    return list(data.get("styles", {}).keys())


def get_techniques_in_category(category: str) -> List[str]:
    """List all techniques in a border category."""
    data = _load_border_data()
    cat_data = data.get("styles", {}).get(category, {})
    return list(cat_data.get("techniques", {}).keys())


def get_all_border_styles() -> List[str]:
    """List all available border styles as 'category.technique'."""
    data = _load_border_data()
    styles = []
    for category, cat_data in data.get("styles", {}).items():
        for technique in cat_data.get("techniques", {}):
            styles.append(f"{category}.{technique}")
    return styles


def render_border(
    grid: np.ndarray,
    style_key: str,
    color: Tuple[int, int, int] = (0, 0, 0),
    width: Optional[int] = None,
) -> np.ndarray:
    """
    Render a border on the grid.

    Args:
        grid: Input color grid (H×W×3 uint8).
        style_key: Border style (e.g., 'woven.solid', 'embroidered.zigzag').
        color: Border color.
        width: Border width (uses default from style if None).

    Returns:
        Grid with border applied.
    """
    style_def = get_border_style(style_key)
    if style_def is None:
        # Fallback to solid
        return _render_solid(grid, color, width or 6)

    if width is None:
        width = style_def.get("default_width", 6)

    technique = style_key.split(".")[-1]

    if technique == "solid":
        return _render_solid(grid, color, width)
    elif technique == "double":
        return _render_double(grid, color, width)
    elif technique == "zigzag":
        return _render_zigzag(grid, color, width)
    elif technique == "striped":
        return _render_striped(grid, color, width)
    elif technique == "raw_edge":
        return grid  # No border
    else:
        return _render_solid(grid, color, width)


def _render_solid(grid: np.ndarray, color: Tuple[int, int, int], width: int) -> np.ndarray:
    """Render a solid border."""
    h, w = grid.shape[:2]
    bw = min(width, h // 4, w // 4)
    if bw <= 0:
        return grid
    grid[:bw, :, :] = color
    grid[-bw:, :, :] = color
    grid[:, :bw, :] = color
    grid[:, -bw:, :] = color
    return grid


def _render_double(grid: np.ndarray, color: Tuple[int, int, int], width: int) -> np.ndarray:
    """Render a double border with gap."""
    h, w = grid.shape[:2]
    bw = min(width, h // 4, w // 4)
    if bw <= 0:
        return grid
    for offset in (0, max(2, bw // 2)):
        if offset + 2 <= h // 4:
            grid[offset:offset + 2, :, :] = color
            grid[-(offset + 2):, :, :] = color
            grid[:, offset:offset + 2, :] = color
            grid[:, -(offset + 2):, :] = color
    return grid


def _render_zigzag(grid: np.ndarray, color: Tuple[int, int, int], width: int) -> np.ndarray:
    """Render a zigzag border."""
    h, w = grid.shape[:2]
    bw = min(width, h // 4, w // 4)
    if bw <= 0:
        return grid
    step = max(2, bw)
    for r in range(h):
        for c in range(w):
            if r < bw and (c // step) % 2 == 0:
                grid[r, c] = color
            if r >= h - bw and (c // step) % 2 == 0:
                grid[r, c] = color
            if c < bw and (r // step) % 2 == 0:
                grid[r, c] = color
            if c >= w - bw and (r // step) % 2 == 0:
                grid[r, c] = color
    return grid


def _render_striped(grid: np.ndarray, color: Tuple[int, int, int], width: int) -> np.ndarray:
    """Render a striped border with alternating colors."""
    h, w = grid.shape[:2]
    bw = min(width, h // 4, w // 4)
    if bw <= 0:
        return grid
    stripe_h = max(1, bw // 3)
    for i in range(0, bw, stripe_h * 2):
        end = min(i + stripe_h, bw)
        grid[i:end, :, :] = color
        grid[:, i:end, :] = color
        if end < bw:
            grid[-(i + stripe_h):-(end) if end > 0 else -bw:, :, :] = color
            grid[:, -(i + stripe_h):-(end) if end > 0 else -bw:, :] = color
    return grid


def validate_border_style(style_key: str) -> Tuple[bool, List[str]]:
    """Validate a border style key. Returns (is_valid, errors)."""
    errors = []
    parts = style_key.split(".")
    if len(parts) != 2:
        return False, [f"Invalid style key format: {style_key} (expected 'category.technique')"]

    data = _load_border_data()
    styles = data.get("styles", {})
    if parts[0] not in styles:
        errors.append(f"Unknown category: {parts[0]}")
    else:
        techniques = styles[parts[0]].get("techniques", {})
        if parts[1] not in techniques:
            errors.append(f"Unknown technique '{parts[1]}' in category '{parts[0]}'")

    return (len(errors) == 0, errors)
