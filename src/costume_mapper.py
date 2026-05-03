"""
Costume Mapper — map pattern zones to body regions on garment templates.

Divides pattern grids into regions matching garment body parts,
warps each region to fit, and applies tribe-specific color adjustments.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from .dna_features import DNAFeatures
from .garment_templates import BodyRegion, GarmentTemplate, get_garment_templates
from .pattern_warp import PatternWarper


class CostumeMapper:
    """Map DNA-driven patterns onto garment body regions."""

    def __init__(self, community: str, seed: Optional[int] = None):
        """
        Args:
            community: Target community/tribe.
            seed: Optional RNG seed.
        """
        self.community = community
        self._seed = seed or 0
        self.warper = PatternWarper()
        self._templates = get_garment_templates(community)

    def map_pattern_to_garment(
        self,
        pattern_grid: np.ndarray,
        garment_template: Optional[GarmentTemplate] = None,
        features: Optional[DNAFeatures] = None,
        garment_name: str = "default",
    ) -> Dict[str, np.ndarray]:
        """
        Map a flat pattern grid onto garment body regions.

        Args:
            pattern_grid: Full pattern grid (H×W×3 uint8).
            garment_template: Garment template to map onto.
                If None, uses first template for the community.
            features: DNA features for color adjustments.
            garment_name: Specific garment name to use if template is None.

        Returns:
            Dict mapping region_name → warped pattern grid (uint8).
        """
        if garment_template is None:
            garment_template = self._resolve_template(garment_name)
            if garment_template is None:
                raise ValueError(
                    f"No garment template found for {self.community}/{garment_name}"
                )

        result: Dict[str, np.ndarray] = {}

        for region in garment_template.regions:
            region_pattern = self.get_region_pattern(
                pattern_grid, region, features
            )
            result[region.name] = region_pattern

        return result

    def get_region_pattern(
        self,
        pattern_grid: np.ndarray,
        region: BodyRegion,
        features: Optional[DNAFeatures] = None,
    ) -> np.ndarray:
        """
        Extract and warp a sub-pattern for a specific body region.

        Args:
            pattern_grid: Full pattern grid (H×W×3 uint8).
            region: Body region definition.
            features: DNA features (unused here, but available for extensions).

        Returns:
            Warped pattern grid for this region.
        """
        src_h, src_w = pattern_grid.shape[:2]

        # Extract region from UV coords
        u_min, v_min, u_max, v_max = region.uv_coords

        px_min = int(u_min * src_w)
        px_max = int(u_max * src_w)
        py_min = int(v_min * src_h)
        py_max = int(v_max * src_h)

        # Clamp to source bounds
        px_min = max(0, px_min)
        px_max = min(src_w, px_max)
        py_min = max(0, py_min)
        py_max = min(src_h, py_max)

        # Extract sub-pattern
        sub_pattern = pattern_grid[py_min:py_max, px_min:px_max]

        # If sub_pattern is empty, create a minimal grid
        if sub_pattern.size == 0 or sub_pattern.shape[0] == 0 or sub_pattern.shape[1] == 0:
            sub_pattern = np.zeros((max(1, src_h // 4), max(1, src_w // 4), 3), dtype=np.uint8)

        # Warp to region shape
        warped = self.warper.warp_to_region(
            sub_pattern,
            region_shape=(region.height, region.width),
            warp_type=region.warp_type,
        )

        return warped

    def generate_costume_output(
        self,
        pattern_grid: np.ndarray,
        features: DNAFeatures,
        garment_name: str = "default",
    ) -> Dict[str, np.ndarray]:
        """
        Generate full costume output: dict of region_name → pattern.

        Convenience wrapper that resolves the template automatically.

        Args:
            pattern_grid: Full pattern grid.
            features: DNA features.
            garment_name: Garment to use.

        Returns:
            Dict mapping region_name → pattern grid.
        """
        template = self._resolve_template(garment_name)
        if template is None:
            raise ValueError(
                f"No garment template for {self.community}/{garment_name}"
            )
        return self.map_pattern_to_garment(pattern_grid, template, features)

    def generate_costume_preview(
        self,
        pattern_grid: np.ndarray,
        features: DNAFeatures,
        garment_name: str = "default",
        padding: int = 10,
        bg_color: Tuple[int, int, int] = (40, 40, 40),
    ) -> np.ndarray:
        """
        Generate a flat 2D preview of all garment regions laid out side by side.

        Useful for visualization before sewing/printing.

        Args:
            pattern_grid: Full pattern grid.
            features: DNA features.
            garment_name: Garment to preview.
            padding: Pixels between regions.
            bg_color: Background color for the preview canvas.

        Returns:
            Single composite grid with all regions laid out.
        """
        regions = self.generate_costume_output(pattern_grid, features, garment_name)

        if not regions:
            return np.zeros((100, 100, 3), dtype=np.uint8)

        # Calculate total preview size
        region_arrays = list(regions.values())
        total_w = sum(r.shape[1] for r in region_arrays) + padding * (len(region_arrays) + 1)
        max_h = max(r.shape[0] for r in region_arrays) + padding * 2

        preview = np.full((max_h, total_w, 3), bg_color, dtype=np.uint8)

        x_offset = padding
        for region_arr in region_arrays:
            rh, rw = region_arr.shape[:2]
            y_offset = padding + (max_h - padding * 2 - rh) // 2
            preview[y_offset:y_offset + rh, x_offset:x_offset + rw] = region_arr
            x_offset += rw + padding

        return preview

    def _resolve_template(self, garment_name: str) -> Optional[GarmentTemplate]:
        """Resolve a garment template by name from the community's templates."""
        for t in self._templates:
            if t.garment_name.lower() == garment_name.lower():
                return t
        return self._templates[0] if self._templates else None

    def list_available_garments(self) -> List[str]:
        """List all garment names available for this community."""
        return [t.garment_name for t in self._templates]
