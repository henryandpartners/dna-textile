#!/usr/bin/env python3
"""Batch-generate DNA textile patterns for all 15 Thai indigenous communities.

Produces one pattern per (community × pattern_type × complexity) combination,
plus mixed-DNA patterns. Outputs PNG + JAC + TXT per pattern.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dna_parser import parse_string
from src.pattern_generator import PatternGenerator
from src.cultural_rules import apply_cultural_rules, get_community_rules
from src.exporters import export_png, export_jac, export_txt
from src import motif_library as ml

# ── Community definitions ──────────────────────────────────

COMMUNITIES = [
    "karen", "hmong", "akha", "lahu", "lisu",
    "mien", "palaung", "khamu", "lua", "mlabri",
    "mani", "moklen", "urak_lawoi", "thai_lue", "tai_dam",
]

PATTERN_TYPES = ["grid", "stripe", "spiral", "random"]
COMPLEXITY_LEVELS = ["beginner", "intermediate", "expert"]

# Community-specific DNA seeds (evocative sequences)
DNA_SEEDS = {
    "karen":       "ATGCGATCGATCGATGCGATCGATCGATGCGATCGATCGATGCGATCGATCG",
    "hmong":       "CGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA",
    "akha":        "TACGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATC",
    "lahu":        "GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT",
    "lisu":        "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATC",
    "mien":        "GATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGAT",
    "palaung":     "CATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGAT",
    "khamu":       "TGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC",
    "lua":         "AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC",
    "mlabri":      "CTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTA",
    "mani":        "GCTACGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA",
    "moklen":      "ATGCGATGCGATGCGATGCGATGCGATGCGATGCGATGCGATGCGATGCGA",
    "urak_lawoi":  "CGATGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT",
    "thai_lue":    "TACGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATC",
    "tai_dam":     "GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT",
}

# Mixed DNA seeds (combine 2-3 communities)
MIXED_SEEDS = {
    "karen_hmong":     "ATGCGATCGATCG" + "CGATCGATCGATC" * 5,
    "akha_lahu":       "TACGATCGATCGA" + "GCTAGCTAGCTAG" * 5,
    "lisu_mien":       "ATCGATCGATCGA" + "GATCGATCGATCG" * 5,
    "palaung_khamu":   "CATCGATCGATCG" + "TGCATGCATGCAT" * 5,
    "lua_mlabri":      "AGCTAGCTAGCTA" + "CTAGCTAGCTAGC" * 5,
    "mani_moklen":     "GCTACGATCGATC" + "ATGCGATGCGATG" * 5,
    "urak_lawoi_thai_lue": "CGATGCTAGCTAG" + "TACGATCGATCGA" * 5,
    "tai_dam_karen":   "GCTAGCTAGCTAG" + "ATGCGATCGATCG" * 5,
}


def generate_patterns(output_dir: Path) -> list[dict]:
    """Generate all patterns and return catalog entries."""
    output_dir.mkdir(parents=True, exist_ok=True)
    catalog: list[dict] = []
    seed_counter = 0

    # ── Single-community patterns ──────────────────────────
    for community in COMMUNITIES:
        dna = DNA_SEEDS[community]
        for ptype in PATTERN_TYPES:
            for complexity in COMPLEXITY_LEVELS:
                seed_counter += 1
                gen = PatternGenerator(
                    grid_size=100,
                    community=community,
                    complexity=complexity,
                )
                grid = gen.generate_grid(
                    dna,
                    pattern_type=ptype,
                    seed=seed_counter,
                )
                # Apply cultural rules
                rule = get_community_rules(community)
                grid = apply_cultural_rules(grid, rule=rule)

                base = f"{community}_{ptype}_{complexity}_100x100"
                png = export_png(grid, str(output_dir / f"{base}.png"))
                jac = export_jac(grid, str(output_dir / f"{base}.jac"))
                txt = export_txt(grid, str(output_dir / f"{base}.txt"))

                catalog.append({
                    "id": base,
                    "community": community,
                    "pattern_type": ptype,
                    "complexity": complexity,
                    "dna_source": "single",
                    "grid_size": 100,
                    "seed": seed_counter,
                    "files": {
                        "png": str(png),
                        "jac": str(jac),
                        "txt": str(txt),
                    },
                })

    # ── Mixed-DNA patterns ─────────────────────────────────
    for mix_name, dna in MIXED_SEEDS.items():
        for ptype in PATTERN_TYPES:
            for complexity in COMPLEXITY_LEVELS:
                seed_counter += 1
                gen = PatternGenerator(
                    grid_size=100,
                    community="mixed",
                    complexity=complexity,
                )
                grid = gen.generate_grid(
                    dna,
                    pattern_type=ptype,
                    seed=seed_counter,
                )

                base = f"mixed_{mix_name}_{ptype}_{complexity}_100x100"
                png = export_png(grid, str(output_dir / f"{base}.png"))
                jac = export_jac(grid, str(output_dir / f"{base}.jac"))
                txt = export_txt(grid, str(output_dir / f"{base}.txt"))

                catalog.append({
                    "id": base,
                    "community": mix_name,
                    "pattern_type": ptype,
                    "complexity": complexity,
                    "dna_source": "mixed",
                    "grid_size": 100,
                    "seed": seed_counter,
                    "files": {
                        "png": str(png),
                        "jac": str(jac),
                        "txt": str(txt),
                    },
                })

    return catalog


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "output"
    catalog = generate_patterns(out)
    print(f"Generated {len(catalog)} patterns → {out}")

    # Write catalog
    catalog_path = Path(__file__).resolve().parent / "pattern_catalog.json"
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"Catalog → {catalog_path}")
