"""
Printable Patterns — generates real-world printable sewing patterns from DNA textile output.

Converts costume mapper output into sewing pattern pieces with seam allowances,
grain lines, notch marks, cutting layouts, and assembly instructions.
Outputs SVG files suitable for printing at any scale.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


# ── Size Chart (cm) ─────────────────────────────────────────

SIZE_CHART: Dict[str, Dict[str, float]] = {
    "S": {"bust": 86, "waist": 66, "hip": 92, "height": 160},
    "M": {"bust": 92, "waist": 72, "hip": 98, "height": 165},
    "L": {"bust": 98, "waist": 78, "hip": 104, "height": 170},
    "XL": {"bust": 104, "waist": 84, "hip": 110, "height": 175},
}

# Paper sizes in mm
PAPER_SIZES: Dict[str, Tuple[float, float]] = {
    "A4": (210, 297),
    "A3": (297, 420),
}


@dataclass
class PatternPiece:
    """A single sewing pattern piece."""
    name: str
    piece_id: str
    vertices: List[Tuple[float, float]]
    seam_allowance_cm: float
    grain_direction: Tuple[float, float] = (0.0, 1.0)
    notches: List[Tuple[float, float, str]] = field(default_factory=list)
    match_marks: List[Tuple[float, float, str]] = field(default_factory=list)
    cut_on_fold: bool = False
    quantity: int = 2
    notes: str = ""


@dataclass
class CuttingLayout:
    """Fabric cutting layout."""
    pieces: List[PatternPiece]
    fabric_width_cm: float
    fabric_length_cm: float
    piece_positions: List[Dict] = field(default_factory=list)


@dataclass
class MeasurementTable:
    """Measurement table for a garment."""
    size: str
    measurements: Dict[str, float]
    scale_factor: float


class PrintablePatternGenerator:
    """Generate printable sewing patterns from DNA textile pattern grids."""

    def __init__(
        self,
        grid_size: int = 100,
        pixels_per_cm: float = 2.0,
    ):
        """
        Args:
            grid_size: Original pattern grid size (N×N pixels).
            pixels_per_cm: Conversion factor from pixels to centimeters.
        """
        self.grid_size = grid_size
        self.pixels_per_cm = pixels_per_cm

    def pixels_to_cm(self, pixels: float) -> float:
        """Convert pixels to centimeters."""
        return pixels / self.pixels_per_cm

    def cm_to_pixels(self, cm: float) -> float:
        """Convert centimeters to pixels."""
        return cm * self.pixels_per_cm

    # ── Pattern Piece Generation ─────────────────────────────

    def generate_pattern_pieces(
        self,
        pattern_grid: np.ndarray,
        community: str,
        garment_name: str,
        seam_allowance_cm: float = 1.0,
        size: str = "M",
    ) -> List[PatternPiece]:
        """
        Generate sewing pattern pieces from a pattern grid.

        Args:
            pattern_grid: DNA pattern grid (H×W×3 uint8).
            community: Target community.
            garment_name: Garment type.
            seam_allowance_cm: Seam allowance width.
            size: Garment size (S, M, L, XL).

        Returns:
            List of PatternPiece objects.
        """
        h, w = pattern_grid.shape[:2]
        size_data = SIZE_CHART.get(size, SIZE_CHART["M"])
        scale = self._get_size_scale(size)
        garment_lower = garment_name.lower()

        if "skirt" in garment_lower or "longyi" in garment_lower or "sinh" in garment_lower:
            pieces = self._skirt_pieces(w, h, scale, seam_allowance_cm, size_data)
        elif "jacket" in garment_lower or "blouse" in garment_lower:
            pieces = self._jacket_pieces(w, h, scale, seam_allowance_cm, size_data)
        elif "wrap" in garment_lower or "cloth" in garment_lower or "bark" in garment_lower:
            pieces = self._wrap_pieces(w, h, scale, seam_allowance_cm, size_data)
        elif "tunic" in garment_lower:
            pieces = self._tunic_pieces(w, h, scale, seam_allowance_cm, size_data)
        elif "trouser" in garment_lower:
            pieces = self._trouser_pieces(w, h, scale, seam_allowance_cm, size_data)
        elif "headdress" in garment_lower:
            pieces = self._headdress_pieces(w, h, scale, seam_allowance_cm, size_data)
        elif "apron" in garment_lower:
            pieces = self._apron_pieces(w, h, scale, seam_allowance_cm, size_data)
        elif "sabai" in garment_lower:
            pieces = self._shawl_pieces(w, h, scale, seam_allowance_cm, size_data)
        else:
            pieces = self._default_pieces(w, h, scale, seam_allowance_cm, size_data)

        self._add_dna_details(pieces, pattern_grid, community)
        return pieces

    def _get_size_scale(self, size: str) -> float:
        scales = {"S": 0.9, "M": 1.0, "L": 1.1, "XL": 1.2}
        return scales.get(size, 1.0)

    def _skirt_pieces(self, w, h, scale, sa, sd):
        hip_cm = sd["hip"]
        length_cm = self.pixels_to_cm(h) * scale
        half_hip = hip_cm / 4 + 2
        return [
            PatternPiece("Skirt Front", "A",
                self._trapezoid(0, 0, half_hip, half_hip + 2, length_cm),
                sa, grain_direction=(1.0, 0.0), cut_on_fold=True, quantity=1,
                notes="Cut 1 on fold at center front"),
            PatternPiece("Skirt Back", "B",
                self._trapezoid(0, 0, half_hip, half_hip + 2, length_cm),
                sa, grain_direction=(1.0, 0.0), quantity=2,
                notes="Cut 2, match notches at side seams"),
            PatternPiece("Waistband", "C",
                self._rect(0, 0, hip_cm / 2 + 3, 5),
                sa, grain_direction=(1.0, 0.0), quantity=2,
                notes="Cut 2, interfacing recommended"),
        ]

    def _jacket_pieces(self, w, h, scale, sa, sd):
        bust = sd["bust"]
        length = self.pixels_to_cm(h) * scale
        half_bust = bust / 4 + 3
        sleeve_w = bust / 6 + 2
        return [
            PatternPiece("Front Left", "A",
                self._jacket_front(0, 0, half_bust, length),
                sa, grain_direction=(0.0, 1.0), quantity=1,
                notes="Cut 1, mirror for right front"),
            PatternPiece("Back", "B",
                self._rect(0, 0, half_bust * 2 - 2, length),
                sa, grain_direction=(0.0, 1.0), cut_on_fold=True, quantity=1,
                notes="Cut 1 on fold at center back"),
            PatternPiece("Sleeve", "C",
                self._sleeve(0, 0, sleeve_w, length * 0.6),
                sa, grain_direction=(0.0, 1.0), quantity=2,
                notes="Cut 2, match notches at cap"),
            PatternPiece("Collar", "D",
                self._collar(0, 0, bust / 3, 6),
                sa, grain_direction=(0.0, 1.0), quantity=2,
                notes="Cut 2 (outer + interfacing)"),
        ]

    def _wrap_pieces(self, w, h, scale, sa, sd):
        wc = self.pixels_to_cm(w) * scale
        lc = self.pixels_to_cm(h) * scale
        return [PatternPiece("Main Body", "A",
            self._rect(0, 0, wc, lc), sa, grain_direction=(0.0, 1.0),
            quantity=1, notes="Cut 1, finish edges with hem")]

    def _tunic_pieces(self, w, h, scale, sa, sd):
        bust = sd["bust"]
        length = self.pixels_to_cm(h) * scale
        half_bust = bust / 4 + 4
        sleeve_w = bust / 5 + 2
        return [
            PatternPiece("Tunic Front", "A",
                self._trapezoid(0, 0, half_bust - 1, half_bust + 2, length),
                sa, grain_direction=(0.0, 1.0), cut_on_fold=True, quantity=1,
                notes="Cut 1 on fold, add neckline facing"),
            PatternPiece("Tunic Back", "B",
                self._trapezoid(0, 0, half_bust - 1, half_bust + 2, length),
                sa, grain_direction=(0.0, 1.0), cut_on_fold=True, quantity=1,
                notes="Cut 1 on fold"),
            PatternPiece("Sleeve", "C",
                self._sleeve(0, 0, sleeve_w, length * 0.5),
                sa, grain_direction=(0.0, 1.0), quantity=2, notes="Cut 2"),
        ]

    def _trouser_pieces(self, w, h, scale, sa, sd):
        hip = sd["hip"]
        length = self.pixels_to_cm(h) * scale
        half_hip = hip / 4 + 2
        rise = sd["height"] * 0.15
        knee_w = half_hip * 0.6
        hem_w = half_hip * 0.45
        return [
            PatternPiece("Front Left Leg", "A",
                self._leg(0, 0, half_hip, knee_w, hem_w, length, rise),
                sa, grain_direction=(0.0, 1.0), quantity=1,
                notes="Cut 1, mirror for right leg"),
            PatternPiece("Back Left Leg", "B",
                self._leg(0, 0, half_hip + 2, knee_w + 1, hem_w + 1, length, rise + 3),
                sa, grain_direction=(0.0, 1.0), quantity=1,
                notes="Cut 1, mirror for right leg"),
            PatternPiece("Waistband", "C",
                self._rect(0, 0, hip / 2 + 3, 5),
                sa, grain_direction=(1.0, 0.0), quantity=2,
                notes="Cut 2, with elastic casing"),
        ]

    def _headdress_pieces(self, w, h, scale, sa, sd):
        hw = sd["bust"] * 0.55
        return [
            PatternPiece("Headband", "A", self._rect(0, 0, hw, 15 * scale),
                sa, grain_direction=(1.0, 0.0), quantity=2,
                notes="Cut 2, add interfacing"),
            PatternPiece("Cap Crown", "B",
                self._ellipse(0, 0, hw * 0.5, 20 * scale),
                sa, grain_direction=(0.0, 1.0), quantity=1,
                notes="Cut 1, gather to headband"),
            PatternPiece("Decoration Panel", "C",
                self._rect(0, 0, hw * 0.6, 30 * scale),
                sa, grain_direction=(0.0, 1.0), quantity=1,
                notes="Cut 1, add silver coins/beads"),
        ]

    def _apron_pieces(self, w, h, scale, sa, sd):
        wc = self.pixels_to_cm(w) * scale * 0.8
        lc = self.pixels_to_cm(h) * scale * 0.7
        return [
            PatternPiece("Apron Body", "A",
                self._trapezoid(0, 0, wc * 0.8, wc, lc),
                sa, grain_direction=(0.0, 1.0), cut_on_fold=True, quantity=1,
                notes="Cut 1 on fold at top"),
            PatternPiece("Waist Tie", "B",
                self._rect(0, 0, sd["hip"] + 20, 6),
                sa, grain_direction=(1.0, 0.0), quantity=2,
                notes="Cut 2, fold and stitch"),
        ]

    def _shawl_pieces(self, w, h, scale, sa, sd):
        wc = self.pixels_to_cm(w) * scale
        lc = self.pixels_to_cm(h) * scale
        return [
            PatternPiece("Shawl Body", "A",
                self._rect(0, 0, wc, lc),
                sa, grain_direction=(0.0, 1.0), quantity=1,
                notes="Cut 1, finish edges with narrow hem"),
            PatternPiece("Fringe", "B",
                self._rect(0, 0, wc, 8),
                0, grain_direction=(1.0, 0.0), quantity=1,
                notes="Cut 1, create fringe by pulling threads"),
        ]

    def _default_pieces(self, w, h, scale, sa, sd):
        wc = self.pixels_to_cm(w) * scale
        lc = self.pixels_to_cm(h) * scale
        return [PatternPiece("Main Panel", "A",
            self._rect(0, 0, wc, lc), sa, grain_direction=(0.0, 1.0),
            quantity=2, notes="Cut 2")]

    # ── Vertex generators ────────────────────────────────────

    def _rect(self, x, y, w, h):
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

    def _trapezoid(self, x, y, top_w, bot_w, h):
        dx = (bot_w - top_w) / 2
        return [(x + dx, y), (x + bot_w - dx, y), (x + bot_w, y + h), (x, y + h)]

    def _jacket_front(self, x, y, w, h):
        neck_w = w * 0.35
        armhole_d = h * 0.4
        return [(x, y), (x + neck_w, y), (x + w, y + armhole_d),
                (x + w, y + h), (x, y + h)]

    def _sleeve(self, x, y, w, h):
        cap_h = h * 0.15
        return [(x + w / 2, y), (x + w, y + cap_h), (x + w * 1.1, y + h * 0.3),
                (x + w * 0.95, y + h), (x + w * 0.05, y + h),
                (x - w * 0.1, y + h * 0.3), (x, y + cap_h)]

    def _collar(self, x, y, w, h):
        return [(x, y), (x + w, y), (x + w + 2, y + h), (x - 2, y + h)]

    def _leg(self, x, y, top_w, knee_w, hem_w, length, rise):
        knee_y = y + rise + (length - rise) * 0.55
        return [(x + top_w * 0.15, y), (x + top_w, y + rise * 0.3),
                (x + top_w, y + rise), (x + knee_w, knee_y),
                (x + hem_w, y + length), (x, y + length),
                (x - knee_w * 0.1, knee_y), (x, y + rise),
                (x - top_w * 0.05, y + rise * 0.5)]

    def _ellipse(self, cx, cy, rx, ry, seg=12):
        return [(cx + rx * math.cos(2 * math.pi * i / seg),
                 cy + ry * math.sin(2 * math.pi * i / seg))
                for i in range(seg)]

    # ── DNA-driven details ───────────────────────────────────

    def _add_dna_details(self, pieces, pattern_grid, community):
        if pattern_grid.size == 0:
            return
        for i, piece in enumerate(pieces):
            if not piece.vertices:
                continue
            nv = len(piece.vertices)
            for j in range(0, nv, max(1, nv // 4)):
                v1 = piece.vertices[j % nv]
                v2 = piece.vertices[(j + 1) % nv]
                piece.notches.append(((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2,
                                      chr(65 + (i * 3 + j) % 26)))
            cx = sum(v[0] for v in piece.vertices) / nv
            cy = sum(v[1] for v in piece.vertices) / nv
            piece.match_marks.append((cx, cy, piece.piece_id))
            cn = self._community_notes(community, piece.piece_id)
            if cn:
                piece.notes += f" | {cn}"

    def _community_notes(self, community, piece_id):
        notes = {
            "hmong": {"A": "Hmong reverse appliqué: layer 5 fabric colors, cut away top layers to reveal underlying colors",
                      "B": "Hmong reverse appliqué: use 3-5 layered colors for geometric patterns"},
            "karen": {"A": "Karen backstrap loom technique: maintain consistent tension",
                      "C": "Karen waistband: use traditional twill weave structure"},
            "lisu": {"A": "Lisu color-block: use contrasting fabric panels",
                     "D": "Lisu collar: add embroidered trim with cross-stitch"},
            "akha": {"A": "Akha headdress: attach silver coins and beads after assembly",
                     "B": "Akha cap: use indigo-dyed fabric as base"},
            "thai_lue": {"A": "Thai Lue jok technique: supplementary weft patterning"},
            "tai_dam": {"A": "Tai Dam: use indigo-dyed fabric, resist-dye patterns"},
            "mien": {"A": "Mien: add cross-stitch embroidery, red thread accents"},
        }
        cl = community.lower().replace(" ", "_")
        return notes.get(cl, {}).get(piece_id, "")

    # ── Measurement System ───────────────────────────────────

    def calculate_measurements(
        self, pattern_grid, size="M", garment_name="default"
    ) -> MeasurementTable:
        """
        Calculate real-world dimensions from pattern grid.

        Args:
            pattern_grid: DNA pattern grid.
            size: Garment size (S, M, L, XL).
            garment_name: Garment type.

        Returns:
            MeasurementTable with dimensions and conversion factors.
        """
        h, w = pattern_grid.shape[:2]
        sd = SIZE_CHART.get(size, SIZE_CHART["M"])
        scale = self._get_size_scale(size)
        gcw = self.pixels_to_cm(w) * scale
        gch = self.pixels_to_cm(h) * scale
        gl = garment_name.lower()

        m: Dict[str, float] = {"grid_width_cm": round(gcw, 1), "grid_height_cm": round(gch, 1)}
        if "skirt" in gl or "longyi" in gl or "sinh" in gl:
            m.update({"hip_circumference": sd["hip"], "waist_circumference": sd["waist"],
                      "skirt_length": round(gch * 0.9, 1), "waistband_width": 5.0})
        elif "jacket" in gl or "blouse" in gl:
            m.update({"bust_circumference": sd["bust"], "jacket_length": round(gch * 0.85, 1),
                      "shoulder_width": round(sd["bust"] * 0.22, 1), "sleeve_length": round(gch * 0.5, 1)})
        else:
            m.update({"width": round(gcw, 1), "length": round(gch, 1)})

        return MeasurementTable(size=size, measurements=m, scale_factor=self.pixels_per_cm)

    # ── Cutting Layout ───────────────────────────────────────

    def generate_cutting_layout(
        self, pieces, fabric_width_cm=150.0
    ) -> CuttingLayout:
        """
        Arrange pattern pieces on fabric width.

        Args:
            pieces: List of pattern pieces.
            fabric_width_cm: Fabric roll width.

        Returns:
            CuttingLayout with piece positions.
        """
        sorted_pieces = sorted(pieces, key=lambda p: self._piece_h(p), reverse=True)
        positions = []
        cy = 0.0
        row_h = 0.0
        cx = 0.0

        for piece in sorted_pieces:
            pw = self._piece_w(piece)
            ph = self._piece_h(piece)
            if cx + pw > fabric_width_cm:
                cx = 0.0
                cy += row_h + 2
                row_h = 0.0
            positions.append({"piece_id": piece.piece_id, "piece_name": piece.name,
                              "x": round(cx, 1), "y": round(cy, 1),
                              "rotation": 0, "flipped": False,
                              "width": round(pw, 1), "height": round(ph, 1)})
            cx += pw + 1
            row_h = max(row_h, ph)

        return CuttingLayout(pieces=pieces, fabric_width_cm=fabric_width_cm,
                             fabric_length_cm=round(cy + row_h + 5, 1),
                             piece_positions=positions)

    def _piece_w(self, p):
        if not p.vertices: return 0
        return max(v[0] for v in p.vertices) - min(v[0] for v in p.vertices) + p.seam_allowance_cm * 2

    def _piece_h(self, p):
        if not p.vertices: return 0
        return max(v[1] for v in p.vertices) - min(v[1] for v in p.vertices) + p.seam_allowance_cm * 2

    # ── SVG Export ───────────────────────────────────────────

    def export_sewing_pattern(
        self,
        pattern_grid: np.ndarray,
        community: str,
        garment_name: str,
        features: object,
        output_dir: str,
        size: str = "M",
        seam_allowance_cm: float = 1.0,
        fabric_width_cm: float = 150.0,
        dpi: int = 150,
    ) -> dict:
        """
        Generate complete printable sewing pattern package.

        Args:
            pattern_grid: DNA pattern grid (H×W×3 uint8).
            community: Target community.
            garment_name: Garment type.
            features: DNA features object.
            output_dir: Directory to save output files.
            size: Garment size (S, M, L, XL).
            seam_allowance_cm: Seam allowance width.
            fabric_width_cm: Fabric roll width.
            dpi: Print resolution.

        Returns:
            Dict with pieces, layout, measurements, instructions, summary.
        """
        os.makedirs(output_dir, exist_ok=True)

        pieces = self.generate_pattern_pieces(
            pattern_grid, community, garment_name, seam_allowance_cm, size)
        measurements = self.calculate_measurements(pattern_grid, size, garment_name)
        layout = self.generate_cutting_layout(pieces, fabric_width_cm)

        # Piece SVGs
        piece_files = []
        for piece in pieces:
            path = os.path.join(output_dir, f"piece_{piece.piece_id}.svg")
            with open(path, "w") as f:
                f.write(self._piece_svg(piece, seam_allowance_cm))
            piece_files.append(path)

        # Layout SVG
        layout_path = os.path.join(output_dir, "cutting_layout.svg")
        with open(layout_path, "w") as f:
            f.write(self._layout_svg(layout, fabric_width_cm))

        # Measurements
        mt = self._measurement_table(measurements, pieces)
        mp = os.path.join(output_dir, "measurements.txt")
        with open(mp, "w") as f:
            f.write(mt)

        # Instructions
        inst = self.generate_assembly_instructions(pieces, community, garment_name, measurements)
        ip = os.path.join(output_dir, "assembly_instructions.txt")
        with open(ip, "w") as f:
            f.write(inst)

        # Summary
        total_pieces = sum(p.quantity for p in pieces)
        summary = {
            "garment": garment_name, "community": community, "size": size,
            "fabric_needed_meters": round(layout.fabric_length_cm / 100, 2),
            "fabric_width_cm": fabric_width_cm,
            "piece_count": len(pieces), "total_pieces_to_cut": total_pieces,
            "seam_allowance_cm": seam_allowance_cm,
            "pattern_grid_pixels": f"{pattern_grid.shape[1]}x{pattern_grid.shape[0]}",
            "scale_cm_per_pixel": round(1.0 / self.pixels_per_cm, 3),
        }

        return {"pieces": piece_files, "layout": layout_path,
                "measurements": mt, "instructions": inst, "summary": summary}

    def _piece_svg(self, piece, sa):
        if not piece.vertices:
            return '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><text x="100" y="100" text-anchor="middle">Empty piece</text></svg>'

        xs = [v[0] for v in piece.vertices]
        ys = [v[1] for v in piece.vertices]
        mn_x, mx_x = min(xs), max(xs)
        mn_y, mx_y = min(ys), max(ys)
        margin = max(sa + 1, 2)
        w = mx_x - mn_x + margin * 2
        h = mx_y - mn_y + margin * 2
        ox, oy = mn_x - margin, mn_y - margin
        sw = max(w * 10, 200)
        sh = max(h * 10, 200)

        def pt(v):
            return f"{(v[0] - ox) * 10:.1f},{(v[1] - oy) * 10:.1f}"

        def pts_list(vs):
            return " ".join(pt(v) for v in vs)

        # Offset vertices outward for cut line
        cut_vs = self._offset_polygon(piece.vertices, sa)

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{sw}" height="{sh}" viewBox="0 0 {sw} {sh}">',
            f'  <title>{piece.name} - {piece.piece_id}</title>',
            '  <style>',
            '    .cut-line { fill: none; stroke: #000; stroke-width: 2; }',
            '    .stitch-line { fill: none; stroke: #666; stroke-width: 1; stroke-dasharray: 4,3; }',
            '    .grain-line { stroke: #0066cc; stroke-width: 1.5; }',
            '    .notch { fill: #ff3333; }',
            '    .match-mark { fill: #009900; }',
            '    .fold-line { stroke: #cc6600; stroke-width: 2; stroke-dasharray: 8,4; }',
            '    .label { font-family: Arial, sans-serif; font-size: 12px; fill: #333; }',
            '    .piece-id { font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #0066cc; }',
            '  </style>',
            '',
            f'  <!-- Scale: 1cm = 10px -->',
            f'  <polygon class="cut-line" points="{pts_list(cut_vs)}" />',
            f'  <polygon class="stitch-line" points="{pts_list(piece.vertices)}" />',
        ]

        # Grain line
        cx = sum(v[0] for v in piece.vertices) / len(piece.vertices)
        cy = sum(v[1] for v in piece.vertices) / len(piece.vertices)
        gx, gy = piece.grain_direction
        gl = min(w, h) * 0.4
        lines.append(f'  <line class="grain-line" x1="{(cx - gx * gl - ox) * 10:.1f}" y1="{(cy - gy * gl - oy) * 10:.1f}" x2="{(cx + gx * gl - ox) * 10:.1f}" y2="{(cy + gy * gl - oy) * 10:.1f}" />')
        # Arrow
        lines.append(f'  <polygon points="{(cx + gx * gl - ox) * 10:.1f},{(cy + gy * gl - oy) * 10:.1f} {(cx + gx * (gl - 0.5) - ox) * 10:.1f},{(cy + gy * (gl - 0.3) - oy) * 10:.1f} {(cx + gx * (gl - 0.5) - ox) * 10:.1f},{(cy + gy * (gl + 0.3) - oy) * 10:.1f}" fill="#0066cc" />')

        # Notches
        for nx, ny, nl in piece.notches:
            lines.append(f'  <polygon class="notch" points="{(nx - ox) * 10:.1f},{(ny - 0.15 - oy) * 10:.1f} {(nx - 0.15 - ox) * 10:.1f},{(ny + 0.15 - oy) * 10:.1f} {(nx + 0.15 - ox) * 10:.1f},{(ny + 0.15 - oy) * 10:.1f}" />')
            lines.append(f'  <text class="label" x="{(nx - ox) * 10:.1f}" y="{(ny - 0.3 - oy) * 10:.1f}" text-anchor="middle">{nl}</text>')

        # Match marks
        for mx, my, ml in piece.match_marks:
            lines.append(f'  <circle class="match-mark" cx="{(mx - ox) * 10:.1f}" cy="{(my - oy) * 10:.1f}" r="3" />')
            lines.append(f'  <text class="label" x="{(mx - ox) * 10:.1f}" y="{(my + 0.5 - oy) * 10:.1f}" text-anchor="middle">{ml}</text>')

        # Cut-on-fold indicator
        if piece.cut_on_fold:
            fold_x = min(xs)
            lines.append(f'  <line class="fold-line" x1="{(fold_x - ox) * 10:.1f}" y1="{(mn_y - oy) * 10:.1f}" x2="{(fold_x - ox) * 10:.1f}" y2="{(mx_y - oy) * 10:.1f}" />')
            lines.append(f'  <text class="label" x="{(fold_x - ox) * 10:.1f}" y="{(mn_y - 0.5 - oy) * 10:.1f}" text-anchor="middle" fill="#cc6600">FOLD</text>')

        # Labels
        lines.append(f'  <text class="piece-id" x="{sw / 2:.1f}" y="20" text-anchor="middle">{piece.piece_id} — {piece.name}</text>')
        lines.append(f'  <text class="label" x="{sw / 2:.1f}" y="38" text-anchor="middle">Cut {piece.quantity}x{", on fold" if piece.cut_on_fold else ""}</text>')
        if piece.notes:
            lines.append(f'  <text class="label" x="10" y="{sh - 10}">{piece.notes[:80]}</text>')

        lines.append('</svg>')
        return "\n".join(lines)

    def _offset_polygon(self, vertices, offset):
        """Offset polygon vertices outward by given amount."""
        if len(vertices) < 3:
            return vertices
        result = []
        n = len(vertices)
        for i in range(n):
            prev = vertices[(i - 1) % n]
            curr = vertices[i]
            next_v = vertices[(i + 1) % n]
            # Edge vectors
            e1 = (curr[0] - prev[0], curr[1] - prev[1])
            e2 = (next_v[0] - curr[0], next_v[1] - curr[1])
            # Normalize
            l1 = math.sqrt(e1[0] ** 2 + e1[1] ** 2) or 1
            l2 = math.sqrt(e2[0] ** 2 + e2[1] ** 2) or 1
            # Outward normals
            n1 = (e1[1] / l1, -e1[0] / l1)
            n2 = (e2[1] / l2, -e2[0] / l2)
            # Average normal
            avg = (n1[0] + n2[0], n1[1] + n2[1])
            la = math.sqrt(avg[0] ** 2 + avg[1] ** 2) or 1
            result.append((curr[0] + avg[0] / la * offset,
                           curr[1] + avg[1] / la * offset))
        return result

    def _layout_svg(self, layout, fabric_w):
        scale = 5  # 5px per cm
        sw = fabric_w * scale + 40
        sh = layout.fabric_length_cm * scale + 60

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{sw}" height="{sh}" viewBox="0 0 {sw} {sh}">',
            '  <title>Cutting Layout</title>',
            '  <style>',
            '    .fabric { fill: #f5f0e8; stroke: #333; stroke-width: 2; }',
            '    .piece { fill: rgba(108,140,255,0.2); stroke: #0066cc; stroke-width: 1.5; }',
            '    .label { font-family: Arial, sans-serif; font-size: 10px; fill: #333; }',
            '    .title { font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #0066cc; }',
            '    .grain { stroke: #009900; stroke-width: 1; }',
            '  </style>',
            '',
            f'  <text class="title" x="{sw / 2}" y="20" text-anchor="middle">Cutting Layout — {layout.fabric_width_cm}cm fabric × {layout.fabric_length_cm}cm</text>',
            '',
            f'  <rect class="fabric" x="20" y="30" width="{fabric_w * scale}" height="{layout.fabric_length_cm * scale}" />',
            '',
        ]

        for pos in layout.piece_positions:
            px = 20 + pos["x"] * scale
            py = 30 + pos["y"] * scale
            pw = pos["width"] * scale
            ph = pos["height"] * scale
            lines.append(f'  <rect class="piece" x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" />')
            lines.append(f'  <text class="label" x="{px + pw / 2:.1f}" y="{py + ph / 2:.1f}" text-anchor="middle">{pos["piece_id"]}</text>')

        lines.append('</svg>')
        return "\n".join(lines)

    def _measurement_table(self, mt, pieces):
        lines = [
            "=" * 60,
            f"  MEASUREMENT TABLE — Size {mt.size}",
            "=" * 60,
            "",
            f"  Scale: {mt.scale_factor} pixels = 1 cm",
            "",
            "  Garment Measurements:",
            "  " + "-" * 40,
        ]
        for name, value in sorted(mt.measurements.items()):
            if isinstance(value, float):
                lines.append(f"    {name:<30s} {value:>8.1f} cm")
            else:
                lines.append(f"    {name:<30s} {value}")
        lines.extend([
            "",
            "  Pattern Pieces:",
            "  " + "-" * 40,
        ])
        for p in pieces:
            lines.append(f"    {p.piece_id}: {p.name} (cut {p.quantity}x)")
        lines.extend(["", "=" * 60])
        return "\n".join(lines)

    # ── Assembly Instructions ────────────────────────────────

    def generate_assembly_instructions(
        self,
        pieces: List[PatternPiece],
        community: str,
        garment_name: str,
        measurements: MeasurementTable,
    ) -> str:
        """
        Generate step-by-step sewing assembly instructions.

        Args:
            pieces: List of pattern pieces.
            community: Target community.
            garment_name: Garment type.
            measurements: Measurement table.

        Returns:
            Text string with assembly instructions.
        """
        lines = [
            "=" * 60,
            f"  ASSEMBLY INSTRUCTIONS",
            f"  {garment_name.title()} — {community.title()} Tradition",
            f"  Size: {measurements.size}",
            "=" * 60,
            "",
            "  MATERIALS:",
            f"    - Fabric: {measurements.measurements.get('grid_width_cm', 50):.0f}cm × {measurements.measurements.get('grid_height_cm', 100):.0f}cm",
            f"    - Thread: matching color",
            f"    - Seam allowance: {pieces[0].seam_allowance_cm if pieces else 1.0}cm",
            "",
            "  PIECES:",
        ]
        for p in pieces:
            fold = " (cut on fold)" if p.cut_on_fold else ""
            lines.append(f"    {p.piece_id}: {p.name} — Cut {p.quantity}x{fold}")

        lines.extend(["", "  INSTRUCTIONS:", ""])

        # Generate garment-specific steps
        gl = garment_name.lower()
        if "skirt" in gl or "longyi" in gl or "sinh" in gl:
            steps = self._skirt_steps(pieces)
        elif "jacket" in gl or "blouse" in gl:
            steps = self._jacket_steps(pieces)
        elif "wrap" in gl or "cloth" in gl:
            steps = self._wrap_steps(pieces)
        elif "tunic" in gl:
            steps = self._tunic_steps(pieces)
        elif "trouser" in gl:
            steps = self._trouser_steps(pieces)
        else:
            steps = self._default_steps(pieces)

        for i, step in enumerate(steps, 1):
            lines.append(f"  Step {i}: {step}")

        lines.extend([
            "",
            "  FINISHING:",
            "    1. Press all seams flat",
            "    2. Try on garment and adjust fit if needed",
            "    3. Add any decorative elements (embroidery, beads, etc.)",
            "    4. Final press and inspect",
            "",
            "=" * 60,
        ])
        return "\n".join(lines)

    def _skirt_steps(self, pieces):
        return [
            "Cut all pieces according to cutting layout. Transfer all notches and match marks.",
            "If using interfacing, apply to waistband pieces (piece C).",
            "With right sides together, sew front skirt (A) side seam. Press seam open.",
            "With right sides together, sew back skirt (B) side seams, leaving gap for closure if needed. Press seams open.",
            "Match notches and pin front to back at side seams. Sew together. Press.",
            "Finish hem edge: fold up seam allowance twice and stitch.",
            "Fold waistband (C) in half lengthwise, wrong sides together. Press.",
            "Pin waistband to top edge of skirt, matching notches. Sew with seam allowance.",
            "Finish raw edge of waistband. Topstitch if desired.",
            "Add closure (zipper, buttons, or elastic) as needed.",
        ]

    def _jacket_steps(self, pieces):
        return [
            "Cut all pieces. Transfer notches and match marks. Apply interfacing to collar and front edges if needed.",
            "Sew shoulder seams: join front (A) to back (B) at shoulders. Press open.",
            "Prepare collar: sew outer collar to under collar, trim and turn. Press.",
            "Attach collar to neckline, matching notches. Press.",
            "Sew underarm seams of sleeves (C). Press.",
            "Pin sleeves to armholes, matching notches at cap and underarm. Ease in fullness. Sew.",
            "Sew side seams of jacket body, continuing down sleeve seams. Press.",
            "Finish hem: fold up and stitch.",
            "Finish sleeve cuffs: fold and stitch, or add cuff bands.",
            "Add closures (buttons, frog fasteners) as appropriate for the style.",
        ]

    def _wrap_steps(self, pieces):
        return [
            "Cut main body (A) according to layout.",
            "Finish all edges with narrow hem or bias binding.",
            "If desired, add decorative stitching or embroidery along edges.",
            "Press finished edges. Garment is ready to wear as a wrap.",
        ]

    def _tunic_steps(self, pieces):
        return [
            "Cut all pieces. Apply interfacing to neckline if needed.",
            "Sew shoulder seams: join front (A) to back (B). Press open.",
            "Finish neckline: apply facing or bias binding.",
            "Sew underarm seams of sleeves (C). Press.",
            "Attach sleeves to armholes, matching notches. Press.",
            "Sew side seams from hem to underarm. Press.",
            "Finish hem and sleeve cuffs.",
        ]

    def _trouser_steps(self, pieces):
        return [
            "Cut all pieces. Transfer notches and match marks.",
            "Sew front crotch curve (A): sew from front waist, through crotch, to other front waist. Press.",
            "Sew back crotch curve (B) similarly. Press.",
            "Pin front to back at crotch, matching seams. Sew inner leg seams. Press.",
            "Sew outer leg seams from hem to waist. Press.",
            "Finish hem: fold up and stitch.",
            "Prepare waistband (C): sew short ends, turn. Apply elastic if needed.",
            "Attach waistband to top of trousers. Finish raw edge inside.",
        ]

    def _default_steps(self, pieces):
        return [
            f"Cut all {len(pieces)} pieces according to cutting layout.",
            "Transfer all notches and match marks to fabric.",
            "Sew pieces together following the match marks (A to A, B to B, etc.).",
            "Press all seams open or to one side as appropriate.",
            "Finish raw edges with hem or bias binding.",
            "Try on and adjust fit if needed.",
        ]


# ── Convenience function ─────────────────────────────────────

def export_sewing_pattern(
    pattern_grid: np.ndarray,
    community: str,
    garment_name: str,
    features: object,
    output_dir: str,
    size: str = "M",
    seam_allowance_cm: float = 1.0,
    fabric_width_cm: float = 150.0,
    dpi: int = 150,
) -> dict:
    """
    Generate complete printable sewing pattern package.

    Convenience wrapper around PrintablePatternGenerator.export_sewing_pattern.

    Args:
        pattern_grid: DNA pattern grid (H×W×3 uint8).
        community: Target community.
        garment_name: Garment type.
        features: DNA features object.
        output_dir: Directory to save output files.
        size: Garment size (S, M, L, XL).
        seam_allowance_cm: Seam allowance width.
        fabric_width_cm: Fabric roll width.
        dpi: Print resolution.

    Returns:
        Dict with pieces (SVG files), layout, measurements, instructions, summary.
    """
    gen = PrintablePatternGenerator()
    return gen.export_sewing_pattern(
        pattern_grid, community, garment_name, features,
        output_dir, size, seam_allowance_cm, fabric_width_cm, dpi,
    )
