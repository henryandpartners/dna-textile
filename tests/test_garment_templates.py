"""Unit tests for Garment Templates module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.garment_templates import (
    get_garment_templates,
    get_garment_template,
    list_garments,
    list_all_garments,
    GarmentTemplate,
    BodyRegion,
)


class TestGarmentTemplatesLoading:
    """Test garment template loading."""

    def test_get_karen_templates(self):
        """Should return Karen garment templates."""
        templates = get_garment_templates("Karen")
        assert templates is not None
        assert len(templates) > 0

    def test_get_hmong_templates(self):
        """Should return Hmong garment templates."""
        templates = get_garment_templates("Hmong")
        assert templates is not None
        assert len(templates) > 0

    def test_get_unknown_templates(self):
        """Unknown community should return empty list."""
        templates = get_garment_templates("Unknown")
        assert templates == []

    def test_get_specific_template(self):
        """Should get a specific garment template."""
        template = get_garment_template("Karen", "longyi")
        assert template is not None
        assert template.garment_name == "longyi"

    def test_list_garments(self):
        """Should list garment names for a community."""
        garments = list_garments("Karen")
        assert isinstance(garments, list)
        assert len(garments) > 0

    def test_list_all_garments(self):
        """Should list all garments across all communities."""
        all_garments = list_all_garments()
        assert isinstance(all_garments, dict)
        assert len(all_garments) > 0


class TestGarmentTemplateStructure:
    """Test garment template data structure."""

    def test_template_has_regions(self):
        """Templates should have body regions."""
        templates = get_garment_templates("Hmong")
        for t in templates:
            assert len(t.regions) > 0

    def test_region_has_uv_coords(self):
        """Body regions should have UV coordinates."""
        templates = get_garment_templates("Karen")
        for t in templates:
            for region in t.regions:
                assert len(region.uv_coords) == 4
                assert all(0.0 <= v <= 1.0 for v in region.uv_coords)

    def test_region_has_pattern_zone(self):
        """Body regions should have a pattern zone."""
        templates = get_garment_templates("Lisu")
        for t in templates:
            for region in t.regions:
                assert region.pattern_zone in ("general", "border", "center", "hem", "sleeve")

    def test_template_dimensions(self):
        """Templates should have valid dimensions."""
        template = get_garment_template("Akha", "headdress")
        assert template.total_width > 0
        assert template.total_height > 0


class TestGarmentTemplateCommunities:
    """Test garment templates for different communities."""

    @pytest.mark.parametrize("community", [
        "Karen", "Hmong", "Thai Lue", "Tai Dam", "Lisu",
        "Mien", "Akha", "Lahu", "Palaung", "Khamu",
        "Lua", "Mlabri", "Mani", "Moklen", "Urak Lawoi",
    ])
    def test_community_has_templates(self, community):
        """Each supported community should have templates."""
        templates = get_garment_templates(community)
        assert len(templates) > 0, f"No templates for {community}"
