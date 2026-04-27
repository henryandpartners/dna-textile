"""
Complexity — manages pattern difficulty levels and constraints.

Phase 2: Loads complexity definitions from complexity_levels.json and provides
validation for community-complexity compatibility.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


_BASE_DIR = Path(__file__).resolve().parent.parent
_COMPLEXITY_FILE = _BASE_DIR / "complexity_levels.json"

_COMPLEXITY_DATA: Optional[Dict[str, Any]] = None


def _load_complexity_data() -> Dict[str, Any]:
    """Load complexity level data from JSON."""
    global _COMPLEXITY_DATA
    if _COMPLEXITY_DATA is not None:
        return _COMPLEXITY_DATA

    if not _COMPLEXITY_FILE.exists():
        _COMPLEXITY_DATA = {
            "levels": {},
            "default_level": "intermediate",
            "community_complexity_ranges": {},
        }
        return _COMPLEXITY_DATA

    with open(_COMPLEXITY_FILE, "r", encoding="utf-8") as f:
        _COMPLEXITY_DATA = json.load(f)

    return _COMPLEXITY_DATA


def get_level(level_name: str) -> Optional[Dict[str, Any]]:
    """Get complexity level definition."""
    data = _load_complexity_data()
    return data.get("levels", {}).get(level_name)


def get_constraints(level_name: str) -> Optional[Dict[str, Any]]:
    """Get constraints for a complexity level."""
    level = get_level(level_name)
    if level:
        return level.get("constraints")
    return None


def get_default_level() -> str:
    """Get the default complexity level."""
    data = _load_complexity_data()
    return data.get("default_level", "intermediate")


def get_community_complexity_range(community: str) -> List[str]:
    """Get allowed complexity levels for a community."""
    data = _load_complexity_data()
    key = community.lower().replace(" ", "_")
    ranges = data.get("community_complexity_ranges", {})
    if key in ranges:
        return ranges[key]
    # Check if any level is allowed
    levels = data.get("levels", {})
    for level_name, level_data in levels.items():
        if key in level_data.get("suitable_communities", []):
            return [level_name]
    return ["beginner", "intermediate", "expert"]


def is_complexity_allowed(community: str, level: str) -> bool:
    """Check if a complexity level is allowed for a community."""
    allowed = get_community_complexity_range(community)
    return level in allowed


def get_all_levels() -> List[str]:
    """List all available complexity levels."""
    data = _load_complexity_data()
    return list(data.get("levels", {}).keys())


def get_level_info(level_name: str) -> Dict[str, Any]:
    """Get detailed info about a complexity level."""
    level = get_level(level_name)
    if level:
        return {
            "name": level.get("name", level_name),
            "description": level.get("description", ""),
            "constraints": level.get("constraints", {}),
            "characteristics": level.get("characteristics", []),
            "estimated_weaving_time_hours": level.get("estimated_weaving_time_hours", ""),
            "skill_level": level.get("skill_level", ""),
        }
    return {}


def validate_complexity(community: str, level: str) -> Tuple[bool, List[str]]:
    """Validate complexity level for a community. Returns (is_valid, errors)."""
    errors = []
    levels = get_all_levels()
    if level not in levels:
        errors.append(f"Unknown complexity level: {level}. Available: {', '.join(levels)}")
    if not is_complexity_allowed(community, level):
        allowed = get_community_complexity_range(community)
        errors.append(
            f"Complexity '{level}' not allowed for {community}. "
            f"Allowed: {', '.join(allowed)}"
        )
    return (len(errors) == 0, errors)


def get_motif_complexity_cap(level: str) -> str:
    """Get the maximum motif complexity allowed at a level."""
    constraints = get_constraints(level)
    if constraints:
        return constraints.get("motif_complexity_cap", level)
    return level


def get_max_motif_size(level: str) -> int:
    """Get maximum motif grid size for a complexity level."""
    constraints = get_constraints(level)
    if constraints:
        return constraints.get("max_motif_size", 5)
    return 5


def get_max_colors(level: str) -> int:
    """Get maximum number of colors for a complexity level."""
    constraints = get_constraints(level)
    if constraints:
        return constraints.get("max_colors", 5)
    return 5


def get_max_pattern_density(level: str) -> float:
    """Get maximum pattern density for a complexity level."""
    constraints = get_constraints(level)
    if constraints:
        return constraints.get("max_pattern_density", 0.6)
    return 0.6
