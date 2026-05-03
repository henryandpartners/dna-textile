"""
Garment Templates — tribe-specific garment definitions for costume mapping.

Each tribe has culturally appropriate garment templates with body regions,
UV coordinates, and pattern zone assignments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class BodyRegion:
    """A body region within a garment template."""
    name: str
    """Human-readable region name (e.g., 'skirt_body', 'jacket_front')."""

    # UV coordinates: (u_min, v_min, u_max, v_max) in 0-1 range
    uv_coords: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)

    # Pattern zone: which DNA features drive this region
    pattern_zone: str = "general"
    """Zone type: general, border, center, hem, sleeve, etc."""

    # Priority: lower number = higher priority for feature assignment
    priority: int = 5

    # Output dimensions in pixels (for costume mode)
    width: int = 100
    height: int = 100

    # Warp type for mapping flat patterns to curved surfaces
    warp_type: str = "flat"
    """Warp type: flat, cylindrical, conical, drape."""


@dataclass
class GarmentTemplate:
    """A complete garment template for a specific tribe."""
    tribe: str
    """Tribe/community name."""

    garment_name: str
    """Name of the garment (e.g., 'longyi', 'sinh')."""

    # Output dimensions
    total_width: int = 200
    total_height: int = 300

    # Body regions
    regions: List[BodyRegion] = field(default_factory=list)

    # Color adjustment per region (hue shift, saturation multiplier)
    region_color_adjust: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    """region_name → (hue_shift_deg, saturation_mult)"""

    # Description
    description: str = ""


# ── Karen Garments ──────────────────────────────────────────

def _karen_longyi() -> GarmentTemplate:
    """Karen traditional longyi (wrap skirt)."""
    return GarmentTemplate(
        tribe="Karen",
        garment_name="longyi",
        total_width=200,
        total_height=250,
        regions=[
            BodyRegion("skirt_body", (0.0, 0.0, 1.0, 0.7), "general", 1, 200, 175, "cylindrical"),
            BodyRegion("skirt_hem", (0.0, 0.7, 1.0, 1.0), "hem", 2, 200, 75, "flat"),
            BodyRegion("waistband", (0.0, 0.0, 1.0, 0.05), "border", 3, 200, 12, "flat"),
        ],
        region_color_adjust={
            "skirt_body": (0.0, 1.0),
            "skirt_hem": (10.0, 1.1),
            "waistband": (-5.0, 1.2),
        },
        description="Karen wrap skirt with horizontal stripe bands and decorative hem.",
    )


def _karen_body_cloth() -> GarmentTemplate:
    """Karen body cloth / shawl."""
    return GarmentTemplate(
        tribe="Karen",
        garment_name="body_cloth",
        total_width=180,
        total_height=200,
        regions=[
            BodyRegion("cloth_center", (0.1, 0.0, 0.9, 1.0), "center", 1, 144, 200, "flat"),
            BodyRegion("cloth_border_l", (0.0, 0.0, 0.1, 1.0), "border", 2, 18, 200, "flat"),
            BodyRegion("cloth_border_r", (0.9, 0.0, 1.0, 1.0), "border", 2, 18, 200, "flat"),
        ],
        region_color_adjust={},
        description="Karen shoulder cloth with striped borders.",
    )


# ── Hmong Garments ──────────────────────────────────────────

def _hmong_jacket() -> GarmentTemplate:
    """Hmong pau kuam (reverse appliqué jacket)."""
    return GarmentTemplate(
        tribe="Hmong",
        garment_name="jacket",
        total_width=200,
        total_height=280,
        regions=[
            BodyRegion("front_panel", (0.2, 0.0, 0.8, 0.6), "center", 1, 120, 168, "flat"),
            BodyRegion("back_panel", (0.2, 0.6, 0.8, 1.0), "general", 2, 120, 112, "flat"),
            BodyRegion("sleeve_l", (0.0, 0.0, 0.2, 0.5), "sleeve", 3, 40, 140, "cylindrical"),
            BodyRegion("sleeve_r", (0.8, 0.0, 1.0, 0.5), "sleeve", 3, 40, 140, "cylindrical"),
            BodyRegion("collar", (0.3, 0.0, 0.7, 0.1), "border", 4, 80, 28, "flat"),
        ],
        region_color_adjust={
            "front_panel": (0.0, 1.0),
            "sleeve_l": (15.0, 0.9),
            "sleeve_r": (15.0, 0.9),
        },
        description="Hmong reverse appliqué jacket with embroidered panels.",
    )


def _hmong_skirt() -> GarmentTemplate:
    """Hmong pleated skirt."""
    return GarmentTemplate(
        tribe="Hmong",
        garment_name="skirt",
        total_width=220,
        total_height=260,
        regions=[
            BodyRegion("skirt_body", (0.0, 0.0, 1.0, 0.75), "general", 1, 220, 195, "cylindrical"),
            BodyRegion("skirt_border", (0.0, 0.75, 1.0, 1.0), "hem", 2, 220, 65, "flat"),
            BodyRegion("waistband", (0.0, 0.0, 1.0, 0.05), "border", 3, 220, 13, "flat"),
        ],
        region_color_adjust={},
        description="Hmong pleated skirt with embroidered hem band.",
    )


def _hmong_apron() -> GarmentTemplate:
    """Hmong front/rear apron."""
    return GarmentTemplate(
        tribe="Hmong",
        garment_name="apron",
        total_width=120,
        total_height=200,
        regions=[
            BodyRegion("apron_body", (0.0, 0.0, 1.0, 0.8), "center", 1, 120, 160, "flat"),
            BodyRegion("apron_border", (0.0, 0.8, 1.0, 1.0), "hem", 2, 120, 40, "flat"),
        ],
        region_color_adjust={},
        description="Hmong decorative apron worn over skirt.",
    )


# ── Thai Lue Garments ──────────────────────────────────────

def _thai_lue_sinh() -> GarmentTemplate:
    """Thai Lue sinh (tube skirt)."""
    return GarmentTemplate(
        tribe="Thai Lue",
        garment_name="sinh",
        total_width=200,
        total_height=280,
        regions=[
            BodyRegion("sinh_hem", (0.0, 0.7, 1.0, 1.0), "hem", 1, 200, 84, "flat"),
            BodyRegion("sinh_body", (0.0, 0.1, 1.0, 0.7), "general", 2, 200, 168, "cylindrical"),
            BodyRegion("sinh_headband", (0.0, 0.0, 1.0, 0.1), "border", 3, 200, 28, "flat"),
        ],
        region_color_adjust={
            "sinh_hem": (5.0, 1.1),
            "sinh_headband": (-10.0, 1.2),
        },
        description="Thai Lue tube skirt with jok pattern bands.",
    )


def _thai_lue_sabai() -> GarmentTemplate:
    """Thai Lue sabai (shawl)."""
    return GarmentTemplate(
        tribe="Thai Lue",
        garment_name="sabai",
        total_width=160,
        total_height=220,
        regions=[
            BodyRegion("sabai_body", (0.0, 0.0, 1.0, 0.8), "general", 1, 160, 176, "flat"),
            BodyRegion("sabai_fringe", (0.0, 0.8, 1.0, 1.0), "hem", 2, 160, 44, "flat"),
        ],
        region_color_adjust={},
        description="Thai Lue silk shawl with decorative fringe.",
    )


# ── Tai Dam Garments ───────────────────────────────────────

def _tai_dam_blouse() -> GarmentTemplate:
    """Tai Dam indigo blouse."""
    return GarmentTemplate(
        tribe="Tai Dam",
        garment_name="blouse",
        total_width=180,
        total_height=240,
        regions=[
            BodyRegion("blouse_front", (0.2, 0.0, 0.8, 0.5), "center", 1, 108, 120, "flat"),
            BodyRegion("blouse_back", (0.2, 0.5, 0.8, 1.0), "general", 2, 108, 120, "flat"),
            BodyRegion("sleeve_l", (0.0, 0.0, 0.2, 0.5), "sleeve", 3, 36, 120, "cylindrical"),
            BodyRegion("sleeve_r", (0.8, 0.0, 1.0, 0.5), "sleeve", 3, 36, 120, "cylindrical"),
        ],
        region_color_adjust={},
        description="Tai Dam indigo-dyed blouse with silver accents.",
    )


def _tai_dam_skirt() -> GarmentTemplate:
    """Tai Dam woven tube skirt."""
    return GarmentTemplate(
        tribe="Tai Dam",
        garment_name="tube_skirt",
        total_width=200,
        total_height=260,
        regions=[
            BodyRegion("skirt_body", (0.0, 0.0, 1.0, 0.8), "general", 1, 200, 208, "cylindrical"),
            BodyRegion("skirt_hem", (0.0, 0.8, 1.0, 1.0), "hem", 2, 200, 52, "flat"),
        ],
        region_color_adjust={},
        description="Tai Dam indigo tube skirt with woven patterns.",
    )


# ── Lisu Garments ──────────────────────────────────────────

def _lisu_blouse() -> GarmentTemplate:
    """Lisu embroidered blouse."""
    return GarmentTemplate(
        tribe="Lisu",
        garment_name="blouse",
        total_width=200,
        total_height=260,
        regions=[
            BodyRegion("blouse_body", (0.15, 0.0, 0.85, 0.6), "center", 1, 140, 156, "flat"),
            BodyRegion("yoke", (0.15, 0.0, 0.85, 0.15), "border", 2, 140, 39, "flat"),
            BodyRegion("sleeve_l", (0.0, 0.0, 0.15, 0.5), "sleeve", 3, 30, 130, "cylindrical"),
            BodyRegion("sleeve_r", (0.85, 0.0, 1.0, 0.5), "sleeve", 3, 30, 130, "cylindrical"),
            BodyRegion("hem_band", (0.15, 0.85, 0.85, 1.0), "hem", 4, 140, 39, "flat"),
        ],
        region_color_adjust={
            "yoke": (20.0, 1.2),
            "hem_band": (10.0, 1.1),
        },
        description="Lisu color-block blouse with embroidered yoke and hem.",
    )


# ── Mien Garments ──────────────────────────────────────────

def _mien_tunic() -> GarmentTemplate:
    """Mien long tunic."""
    return GarmentTemplate(
        tribe="Mien",
        garment_name="tunic",
        total_width=180,
        total_height=300,
        regions=[
            BodyRegion("tunic_body", (0.15, 0.0, 0.85, 0.7), "general", 1, 126, 210, "flat"),
            BodyRegion("tunic_border", (0.0, 0.0, 0.15, 0.7), "border", 2, 27, 210, "flat"),
            BodyRegion("sleeve_l", (0.0, 0.0, 0.15, 0.4), "sleeve", 3, 27, 120, "cylindrical"),
            BodyRegion("sleeve_r", (0.85, 0.0, 1.0, 0.4), "sleeve", 3, 27, 120, "cylindrical"),
        ],
        region_color_adjust={},
        description="Mien long tunic with cross-stitch embroidery.",
    )


def _mien_trousers() -> GarmentTemplate:
    """Mien traditional trousers."""
    return GarmentTemplate(
        tribe="Mien",
        garment_name="trousers",
        total_width=160,
        total_height=280,
        regions=[
            BodyRegion("leg_l", (0.0, 0.1, 0.45, 0.9), "general", 1, 72, 224, "cylindrical"),
            BodyRegion("leg_r", (0.55, 0.1, 1.0, 0.9), "general", 1, 72, 224, "cylindrical"),
            BodyRegion("waistband", (0.0, 0.0, 1.0, 0.1), "border", 2, 160, 28, "flat"),
        ],
        region_color_adjust={},
        description="Mien indigo trousers with embroidered cuffs.",
    )


# ── Akha Garments ──────────────────────────────────────────

def _akha_headdress() -> GarmentTemplate:
    """Akha elaborate headdress."""
    return GarmentTemplate(
        tribe="Akha",
        garment_name="headdress",
        total_width=200,
        total_height=180,
        regions=[
            BodyRegion("cap_base", (0.2, 0.3, 0.8, 0.7), "center", 1, 120, 72, "conical"),
            BodyRegion("silver_front", (0.2, 0.0, 0.8, 0.3), "border", 2, 120, 54, "flat"),
            BodyRegion("coin_row", (0.1, 0.7, 0.9, 0.85), "border", 3, 160, 27, "flat"),
            BodyRegion("pennants", (0.0, 0.85, 1.0, 1.0), "hem", 4, 200, 27, "drape"),
        ],
        region_color_adjust={
            "silver_front": (0.0, 1.3),
            "coin_row": (0.0, 1.2),
        },
        description="Akha headdress with silver coins, beads, and pendants.",
    )


def _akha_jacket() -> GarmentTemplate:
    """Akha woven jacket."""
    return GarmentTemplate(
        tribe="Akha",
        garment_name="jacket",
        total_width=180,
        total_height=240,
        regions=[
            BodyRegion("jacket_body", (0.15, 0.0, 0.85, 0.6), "general", 1, 126, 144, "flat"),
            BodyRegion("sleeve_l", (0.0, 0.0, 0.15, 0.5), "sleeve", 2, 27, 120, "cylindrical"),
            BodyRegion("sleeve_r", (0.85, 0.0, 1.0, 0.5), "sleeve", 2, 27, 120, "cylindrical"),
        ],
        region_color_adjust={},
        description="Akha dark jacket with silver decorations.",
    )


# ── Lahu Garments ──────────────────────────────────────────

def _lahu_jacket() -> GarmentTemplate:
    """Lahu striped jacket."""
    return GarmentTemplate(
        tribe="Lahu",
        garment_name="jacket",
        total_width=180,
        total_height=240,
        regions=[
            BodyRegion("jacket_body", (0.15, 0.0, 0.85, 0.6), "general", 1, 126, 144, "flat"),
            BodyRegion("sleeve_l", (0.0, 0.0, 0.15, 0.5), "sleeve", 2, 27, 120, "cylindrical"),
            BodyRegion("sleeve_r", (0.85, 0.0, 1.0, 0.5), "sleeve", 2, 27, 120, "cylindrical"),
            BodyRegion("hem_stripes", (0.15, 0.8, 0.85, 1.0), "hem", 3, 126, 48, "flat"),
        ],
        region_color_adjust={},
        description="Lahu black jacket with colorful stripe bands.",
    )


# ── Palaung Garments ───────────────────────────────────────

def _palaung_wrap_skirt() -> GarmentTemplate:
    """Palaung woven wrap skirt."""
    return GarmentTemplate(
        tribe="Palaung",
        garment_name="wrap_skirt",
        total_width=200,
        total_height=250,
        regions=[
            BodyRegion("skirt_body", (0.0, 0.0, 1.0, 0.75), "general", 1, 200, 188, "cylindrical"),
            BodyRegion("skirt_hem", (0.0, 0.75, 1.0, 1.0), "hem", 2, 200, 62, "flat"),
        ],
        region_color_adjust={},
        description="Palaung woven skirt with bold stripe patterns.",
    )


# ── Khamu Garments ─────────────────────────────────────────

def _khamu_wrap() -> GarmentTemplate:
    """Khamu simple wrap garment."""
    return GarmentTemplate(
        tribe="Khamu",
        garment_name="wrap",
        total_width=180,
        total_height=220,
        regions=[
            BodyRegion("wrap_body", (0.0, 0.0, 1.0, 0.85), "general", 1, 180, 187, "cylindrical"),
            BodyRegion("wrap_hem", (0.0, 0.85, 1.0, 1.0), "hem", 2, 180, 33, "flat"),
        ],
        region_color_adjust={},
        description="Khamu simple woven wrap.",
    )


# ── Lua Garments ───────────────────────────────────────────

def _lua_skirt() -> GarmentTemplate:
    """Lua traditional skirt."""
    return GarmentTemplate(
        tribe="Lua",
        garment_name="skirt",
        total_width=200,
        total_height=260,
        regions=[
            BodyRegion("skirt_body", (0.0, 0.0, 1.0, 0.7), "general", 1, 200, 182, "cylindrical"),
            BodyRegion("skirt_hem", (0.0, 0.7, 1.0, 1.0), "hem", 2, 200, 78, "flat"),
        ],
        region_color_adjust={},
        description="Lua earth-tone traditional skirt.",
    )


# ── Mlabri Garments ────────────────────────────────────────

def _mlabri_bark_cloth() -> GarmentTemplate:
    """Mlabri bark cloth wrap."""
    return GarmentTemplate(
        tribe="Mlabri",
        garment_name="bark_cloth",
        total_width=160,
        total_height=200,
        regions=[
            BodyRegion("cloth_body", (0.0, 0.0, 1.0, 1.0), "general", 1, 160, 200, "drape"),
        ],
        region_color_adjust={},
        description="Mlabri bark cloth wrap — natural fiber texture.",
    )


# ── Mani Garments ──────────────────────────────────────────

def _mani_wrap() -> GarmentTemplate:
    """Mani minimal wrap."""
    return GarmentTemplate(
        tribe="Mani",
        garment_name="wrap",
        total_width=140,
        total_height=180,
        regions=[
            BodyRegion("wrap_body", (0.0, 0.0, 1.0, 1.0), "general", 1, 140, 180, "drape"),
        ],
        region_color_adjust={},
        description="Mani minimal wrap — simple natural fiber.",
    )


# ── Moklen Garments ────────────────────────────────────────

def _moklen_sea_cloth() -> GarmentTemplate:
    """Moklen sea cloth."""
    return GarmentTemplate(
        tribe="Moklen",
        garment_name="sea_cloth",
        total_width=160,
        total_height=200,
        regions=[
            BodyRegion("cloth_body", (0.0, 0.0, 1.0, 1.0), "general", 1, 160, 200, "drape"),
        ],
        region_color_adjust={},
        description="Moklen sea-inspired coastal cloth.",
    )


# ── Urak Lawoi Garments ────────────────────────────────────

def _urak_lawai_wrap() -> GarmentTemplate:
    """Urak Lawoi coastal wrap."""
    return GarmentTemplate(
        tribe="Urak Lawoi",
        garment_name="coastal_wrap",
        total_width=160,
        total_height=200,
        regions=[
            BodyRegion("wrap_body", (0.0, 0.0, 1.0, 1.0), "general", 1, 160, 200, "drape"),
        ],
        region_color_adjust={},
        description="Urak Lawoi coastal wrap with ocean motifs.",
    )


# ── Template Registry ──────────────────────────────────────

GARMENT_REGISTRY: Dict[str, List[GarmentTemplate]] = {
    "karen": [_karen_longyi(), _karen_body_cloth()],
    "hmong": [_hmong_jacket(), _hmong_skirt(), _hmong_apron()],
    "thai_lue": [_thai_lue_sinh(), _thai_lue_sabai()],
    "tai_dam": [_tai_dam_blouse(), _tai_dam_skirt()],
    "lisu": [_lisu_blouse()],
    "mien": [_mien_tunic(), _mien_trousers()],
    "akha": [_akha_headdress(), _akha_jacket()],
    "lahu": [_lahu_jacket()],
    "palaung": [_palaung_wrap_skirt()],
    "khamu": [_khamu_wrap()],
    "lua": [_lua_skirt()],
    "mlabri": [_mlabri_bark_cloth()],
    "mani": [_mani_wrap()],
    "moklen": [_moklen_sea_cloth()],
    "urak_lawoi": [_urak_lawai_wrap()],
}


def get_garment_templates(community: str) -> List[GarmentTemplate]:
    """
    Get all garment templates for a community.

    Args:
        community: Tribe/community name.

    Returns:
        List of GarmentTemplate objects, or empty list if not found.
    """
    key = community.lower().replace(" ", "_").replace("-", "_")
    result = GARMENT_REGISTRY.get(key)
    if result is not None:
        return result
    # Handle common spelling variants
    aliases = {
        "urak_lawoi": "urak_lawai",
        "uraklawoi": "urak_lawai",
    }
    alias_key = aliases.get(key)
    if alias_key:
        result = GARMENT_REGISTRY.get(alias_key)
        if result is not None:
            return result
    # Fallback: try matching by partial name
    for registry_key, templates in GARMENT_REGISTRY.items():
        if community.lower().replace(" ", "_") in registry_key or registry_key in community.lower().replace(" ", "_"):
            return templates
    return []


def get_garment_template(community: str, garment_name: str) -> Optional[GarmentTemplate]:
    """
    Get a specific garment template for a community.

    Args:
        community: Tribe/community name.
        garment_name: Name of the garment (e.g., 'longyi', 'sinh').

    Returns:
        GarmentTemplate or None.
    """
    templates = get_garment_templates(community)
    for t in templates:
        if t.garment_name.lower() == garment_name.lower():
            return t
    # Return first template as default
    return templates[0] if templates else None


def list_garments(community: str) -> List[str]:
    """List all garment names for a community."""
    templates = get_garment_templates(community)
    return [t.garment_name for t in templates]


def list_all_garments() -> Dict[str, List[str]]:
    """List all garments across all communities."""
    return {k: [t.garment_name for t in v] for k, v in GARMENT_REGISTRY.items()}
