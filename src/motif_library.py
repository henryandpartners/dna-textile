"""
Motif Library — manages community-specific textile motifs.

Phase 2: Loads motifs from JSON files in motif_library/ directory.
Each community has its own motif file with culturally appropriate patterns.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


_BASE_DIR = Path(__file__).resolve().parent.parent
_MOTIF_DIR = _BASE_DIR / "motif_library"

# In-memory cache
_MOTIFS: Dict[str, List[Dict[str, Any]]] = {}
_LOADED = False


def _load_motifs() -> None:
    """Load all motif libraries from JSON files."""
    global _MOTIFS, _LOADED
    if _LOADED:
        return

    _MOTIFS = {}

    if not _MOTIF_DIR.exists():
        return

    for json_file in sorted(_MOTIF_DIR.glob("*_motifs.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            community = data.get("community", json_file.stem.replace("_motifs", ""))
            community_key = community.lower().replace(" ", "_")
            motifs = data.get("motifs", [])
            _MOTIFS[community_key] = motifs
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load {json_file}: {e}")

    _LOADED = True


def get_motifs(community: str) -> List[Dict[str, Any]]:
    """Get all motifs for a community."""
    _load_motifs()
    key = community.lower().replace(" ", "_")
    return _MOTIFS.get(key, [])


def get_motif_by_name(community: str, motif_name: str) -> Optional[Dict[str, Any]]:
    """Get a specific motif by name."""
    motifs = get_motifs(community)
    for motif in motifs:
        if motif.get("name") == motif_name:
            return motif
    return None


def get_motifs_by_type(community: str, motif_type: str) -> List[Dict[str, Any]]:
    """Get motifs filtered by type (geometric, animal, plant, spiritual)."""
    motifs = get_motifs(community)
    return [m for m in motifs if m.get("type") == motif_type]


def get_motifs_by_complexity(community: str, complexity: str) -> List[Dict[str, Any]]:
    """Get motifs filtered by complexity level."""
    motifs = get_motifs(community)
    return [m for m in motifs if m.get("complexity") == complexity]


def get_all_motif_names(community: str) -> List[str]:
    """Get list of all motif names for a community."""
    motifs = get_motifs(community)
    return [m.get("name", "") for m in motifs]


def get_motif_grid(community: str, motif_name: str) -> Optional[List[List[int]]]:
    """Get the 2D grid representation of a motif."""
    motif = get_motif_by_name(community, motif_name)
    if motif:
        return motif.get("grid")
    return None


def motif_to_numpy(community: str, motif_name: str, value: int = 1) -> Optional[np.ndarray]:
    """Convert a motif's grid to a numpy array."""
    grid = get_motif_grid(community, motif_name)
    if grid is not None:
        return np.array(grid, dtype=np.uint8) * value
    return None


def list_communities_with_motifs() -> List[str]:
    """List all communities that have motif libraries."""
    _load_motifs()
    return list(_MOTIFS.keys())


def count_total_motifs() -> int:
    """Count total number of motifs across all communities."""
    _load_motifs()
    return sum(len(m) for m in _MOTIFS.values())


def count_motifs_by_type() -> Dict[str, int]:
    """Count motifs by type across all communities."""
    _load_motifs()
    counts: Dict[str, int] = {}
    for motifs in _MOTIFS.values():
        for motif in motifs:
            mtype = motif.get("type", "unknown")
            counts[mtype] = counts.get(mtype, 0) + 1
    return counts


def search_motifs(query: str) -> List[Dict[str, Any]]:
    """Search motifs across all communities by name or description."""
    _load_motifs()
    results = []
    query_lower = query.lower()
    for community, motifs in _MOTIFS.items():
        for motif in motifs:
            name = motif.get("name", "").lower()
            desc = motif.get("description", "").lower()
            if query_lower in name or query_lower in desc:
                result = dict(motif)
                result["community"] = community
                results.append(result)
    return results


def validate_motif(motif: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a motif definition. Returns (is_valid, list_of_errors)."""
    errors = []
    if "name" not in motif:
        errors.append("Missing 'name' field")
    if "type" not in motif:
        errors.append("Missing 'type' field")
    elif motif["type"] not in ("geometric", "animal", "plant", "spiritual"):
        errors.append(f"Invalid motif type: {motif['type']}")
    if "grid" not in motif:
        errors.append("Missing 'grid' field")
    elif not isinstance(motif["grid"], list):
        errors.append("'grid' must be a 2D list")
    else:
        # Check grid is rectangular
        row_lengths = [len(row) for row in motif["grid"] if isinstance(row, list)]
        if row_lengths and len(set(row_lengths)) > 1:
            errors.append("Grid rows have inconsistent lengths")
    if "complexity" not in motif:
        errors.append("Missing 'complexity' field")
    elif motif["complexity"] not in ("beginner", "intermediate", "expert"):
        errors.append(f"Invalid complexity: {motif['complexity']}")
    return (len(errors) == 0, errors)


def validate_all_motifs() -> Dict[str, List[str]]:
    """Validate all motifs. Returns dict of community -> list of errors."""
    _load_motifs()
    results: Dict[str, List[str]] = {}
    for community, motifs in _MOTIFS.items():
        errors = []
        for motif in motifs:
            is_valid, motif_errors = validate_motif(motif)
            if not is_valid:
                errors.append(f"{motif.get('name', 'unknown')}: {'; '.join(motif_errors)}")
        if errors:
            results[community] = errors
    return results


class MotifLibrary:
    """Thin wrapper for motif library functions."""

    def __init__(self, community: str = "generic"):
        self.community = community
        self._custom_motifs: List[Dict[str, Any]] = []

    def get_motifs(self, community: Optional[str] = None) -> List[Dict[str, Any]]:
        c = community or self.community
        motifs = get_motifs(c)
        # If no motifs found for this community, aggregate from all communities
        if not motifs:
            all_motifs: List[Dict[str, Any]] = []
            for comm in list_communities_with_motifs():
                all_motifs.extend(get_motifs(comm))
            motifs = all_motifs
        # Include custom motifs
        return motifs + list(self._custom_motifs)

    def search(self, query: str) -> List[Dict[str, Any]]:
        return search_motifs(query)

    def add_motif(self, motif: Dict[str, Any]) -> None:
        self._custom_motifs.append(motif)
