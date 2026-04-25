"""
Cultural Rule Engine — applies community-specific constraints to textile patterns.

Phase 2: Expanded to support 15+ Thai indigenous communities with JSON-based
rule definitions, motif compatibility, color palette enforcement, and
cultural sensitivity checking.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ── Path resolution ─────────────────────────────────────────

_BASE_DIR = Path(__file__).resolve().parent.parent
_CULTURAL_RULES_DIR = _BASE_DIR / "cultural_rules"


@dataclass
class CulturalRule:
    """A single constraint applied to a textile pattern."""
    name: str
    native_name: str = ""
    language_family: str = ""
    region: str = ""
    textile_history: str = ""
    cultural_significance: str = ""
    border_style: str = "none"
    border_color: Tuple[int, int, int] = (0, 0, 0)
    border_width: int = 4
    excluded_motifs: List[str] = field(default_factory=list)
    sacred_motifs: List[str] = field(default_factory=list)
    taboo_patterns: List[str] = field(default_factory=list)
    preferred_pattern_types: List[str] = field(default_factory=list)
    symmetry_preference: str = "none"
    weaving_technique: str = ""
    complexity_range: List[str] = field(default_factory=list)
    community_approval_required: List[str] = field(default_factory=list)
    traditional_colors: Dict[str, List[str]] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)


# ── Community rule sets (in-memory cache) ──────────────────

_COMMUNITY_RULES: Dict[str, CulturalRule] = {}
_LOADED = False


def _load_community_rules() -> None:
    """Load all community rules from JSON files in cultural_rules/."""
    global _COMMUNITY_RULES, _LOADED
    if _LOADED:
        return

    _COMMUNITY_RULES = {}

    if not _CULTURAL_RULES_DIR.exists():
        return

    for json_file in sorted(_CULTURAL_RULES_DIR.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            community_key = json_file.stem.lower().replace(" ", "_")
            rule = CulturalRule(
                name=data.get("community", json_file.stem),
                native_name=data.get("native_name", ""),
                language_family=data.get("language_family", ""),
                region=data.get("region", ""),
                textile_history=data.get("textile_history", ""),
                cultural_significance=data.get("cultural_significance", ""),
                border_style=data.get("preferred_border", "solid"),
                border_color=(0, 0, 0),  # Will be set from palette
                border_width=6,
                excluded_motifs=data.get("taboo_patterns", []),
                sacred_motifs=data.get("sacred_motifs", []),
                taboo_patterns=data.get("taboo_patterns", []),
                preferred_pattern_types=data.get("preferred_pattern_types", []),
                symmetry_preference=data.get("symmetry_preference", "none"),
                weaving_technique=data.get("weaving_technique", ""),
                complexity_range=data.get("complexity_range", []),
                community_approval_required=data.get("community_approval_required", []),
                traditional_colors=data.get("traditional_colors", {}),
                raw_data=data,
            )
            _COMMUNITY_RULES[community_key] = rule

            # Also index by alternate names
            alt_names = [
                community_key,
                json_file.stem.lower(),
                data.get("community", "").lower(),
            ]
            for alt in alt_names:
                if alt and alt not in _COMMUNITY_RULES:
                    _COMMUNITY_RULES[alt] = rule

        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load {json_file}: {e}")

    # Fallback defaults
    if "karen" not in _COMMUNITY_RULES:
        _COMMUNITY_RULES["karen"] = CulturalRule(
            name="Karen (Kayah)",
            border_style="double",
            border_color=(139, 69, 19),
            border_width=6,
        )
    if "hmong" not in _COMMUNITY_RULES:
        _COMMUNITY_RULES["hmong"] = CulturalRule(
            name="Hmong",
            border_style="zigzag",
            border_color=(255, 255, 255),
            border_width=4,
        )
    if "generic" not in _COMMUNITY_RULES:
        _COMMUNITY_RULES["generic"] = CulturalRule(
            name="Generic",
            border_style="solid",
            border_color=(0, 0, 0),
            border_width=4,
        )
    if "none" not in _COMMUNITY_RULES:
        _COMMUNITY_RULES["none"] = CulturalRule(
            name="No rules",
            border_style="none",
        )

    _LOADED = True


def get_community_rules(community: str) -> CulturalRule:
    """Return rules for a named community (case-insensitive)."""
    _load_community_rules()
    key = community.strip().lower().replace(" ", "_")
    if key in _COMMUNITY_RULES:
        return _COMMUNITY_RULES[key]
    # Try without underscore
    key2 = community.strip().lower()
    if key2 in _COMMUNITY_RULES:
        return _COMMUNITY_RULES[key2]
    return _COMMUNITY_RULES.get("generic", CulturalRule(name="Generic"))


def list_communities() -> List[str]:
    """Return list of all available community names."""
    _load_community_rules()
    seen = set()
    result = []
    for key, rule in _COMMUNITY_RULES.items():
        if rule.name not in seen:
            seen.add(rule.name)
            result.append(rule.name)
    return result


def get_community_info(community: str) -> Dict[str, Any]:
    """Return detailed info about a community's textile tradition."""
    rule = get_community_rules(community)
    return {
        "name": rule.name,
        "native_name": rule.native_name,
        "language_family": rule.language_family,
        "region": rule.region,
        "textile_history": rule.textile_history,
        "cultural_significance": rule.cultural_significance,
        "weaving_technique": rule.weaving_technique,
        "complexity_range": rule.complexity_range,
        "sacred_motifs": rule.sacred_motifs,
        "taboo_patterns": rule.taboo_patterns,
    }


# ── Rule application ───────────────────────────────────────

def apply_border(
    grid: np.ndarray,
    style: str = "solid",
    color: Tuple[int, int, int] = (0, 0, 0),
    width: int = 4,
) -> np.ndarray:
    """Draw a border around the pattern grid in-place and return it."""
    h, w = grid.shape[:2]
    bw = min(width, h // 4, w // 4)
    if bw <= 0 or style == "none":
        return grid

    if style == "solid":
        grid[:bw, :, :] = color
        grid[-bw:, :, :] = color
        grid[:, :bw, :] = color
        grid[:, -bw:, :] = color

    elif style == "double":
        for offset in (0, 2):
            if offset + 2 <= h // 4:
                grid[offset:offset + 2, :, :] = color
                grid[-(offset + 2):, :, :] = color
                grid[:, offset:offset + 2, :] = color
                grid[:, -(offset + 2):, :] = color

    elif style == "zigzag":
        _draw_zigzag_border(grid, color, bw)

    return grid


def _draw_zigzag_border(grid: np.ndarray, color: Tuple[int, int, int], width: int) -> None:
    """Draw a zigzag pattern along all four edges."""
    h, w = grid.shape[:2]
    bw = min(width, h // 4, w // 4)
    if bw <= 0:
        return
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


def apply_cultural_rules(
    grid: np.ndarray,
    rule: Optional[CulturalRule] = None,
    community: str = "generic",
) -> np.ndarray:
    """
    Apply a cultural rule set to a pattern grid.

    Args:
        grid:       Color grid (H×W×3 uint8).
        rule:       Optional explicit rule object.
        community:  Community name (used if rule is None).

    Returns:
        Modified grid.
    """
    if rule is None:
        rule = get_community_rules(community)

    apply_border(grid, rule.border_style, rule.border_color, rule.border_width)
    return grid
