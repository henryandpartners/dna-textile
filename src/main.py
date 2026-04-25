#!/usr/bin/env python3
"""CLI entry point — generate sample patterns from example DNA.

Phase 2: Extended with --motif, --complexity, and --sensitivity-check flags.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dna_parser import parse_fasta, parse_string
from src.pattern_generator import PatternGenerator
from src.cultural_rules import apply_cultural_rules, get_community_rules, list_communities
from src.exporters import export_png, export_jac, export_txt
from src.mixer import mix_patterns
from src import motif_library as ml
from src import color_palette as cp
from src import border_style as bs
from src import complexity as cx
from src import sensitivity_checker as sc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DNA Textile Pattern Generator (Phase 2 — Cultural Rule Engine)"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="examples/karen_sample.fasta",
        help="FASTA file or DNA string",
    )
    parser.add_argument(
        "--type", "-t",
        choices=["stripe", "grid", "spiral", "random"],
        default="grid",
        help="Pattern type (default: grid)",
    )
    parser.add_argument(
        "--size", "-s",
        type=int,
        default=100,
        help="Grid size NxN (default: 100)",
    )
    parser.add_argument(
        "--community", "-c",
        default="generic",
        help="Community: " + ", ".join(list_communities()),
    )
    parser.add_argument(
        "--motif", "-m",
        default=None,
        help="Motif name to overlay (see --list-motifs)",
    )
    parser.add_argument(
        "--complexity",
        choices=["beginner", "intermediate", "expert"],
        default=None,
        help="Pattern complexity level",
    )
    parser.add_argument(
        "--sensitivity-check",
        action="store_true",
        help="Run cultural sensitivity check on selected motifs/patterns",
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--mix",
        nargs="+",
        metavar="FASTA",
        help="Mix multiple FASTA files",
    )
    parser.add_argument(
        "--list-communities",
        action="store_true",
        help="List all available communities",
    )
    parser.add_argument(
        "--list-motifs",
        action="store_true",
        help="List motifs for selected community",
    )
    parser.add_argument(
        "--list-palettes",
        action="store_true",
        help="List available color palettes",
    )
    parser.add_argument(
        "--list-borders",
        action="store_true",
        help="List available border styles",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show community textile info",
    )
    args = parser.parse_args()

    # ── List commands ──────────────────────────────────────

    if args.list_communities:
        print("Available communities:")
        for name in list_communities():
            rule = get_community_rules(name)
            print(f"  {name}: {rule.region} ({rule.language_family})")
        return

    if args.list_motifs:
        motifs = ml.get_motifs(args.community)
        if not motifs:
            print(f"No motifs found for: {args.community}")
        else:
            print(f"Motifs for {args.community}:")
            for m in motifs:
                print(f"  {m['name']} ({m['type']}, {m['complexity']})")
        return

    if args.list_palettes:
        print("Available palettes:")
        for name in cp.list_available_palettes():
            palette = cp.get_community_palette(name)
            if palette:
                colors = palette.get("primary", [])
                print(f"  {name}: {', '.join(colors)}")
        return

    if args.list_borders:
        print("Available border styles:")
        for style in bs.get_all_border_styles():
            print(f"  {style}")
        return

    if args.info:
        from src.cultural_rules import get_community_info
        info = get_community_info(args.community)
        print(f"Community: {info['name']}")
        print(f"  Native name: {info['native_name']}")
        print(f"  Language family: {info['language_family']}")
        print(f"  Region: {info['region']}")
        print(f"  Weaving technique: {info['weaving_technique']}")
        print(f"  Complexity range: {', '.join(info['complexity_range'])}")
        print(f"  Sacred motifs: {', '.join(info['sacred_motifs'])}")
        print(f"  Taboo patterns: {', '.join(info['taboo_patterns'])}")
        print(f"\nTextile history:")
        print(f"  {info['textile_history']}")
        print(f"\nCultural significance:")
        print(f"  {info['cultural_significance']}")
        return

    # ── Sensitivity check ──────────────────────────────────

    if args.sensitivity_check:
        patterns_to_check = []
        if args.motif:
            patterns_to_check.append(args.motif)

        # Also check community taboo patterns
        taboo = sc.get_taboo_patterns(args.community)
        patterns_to_check.extend(taboo)

        if not patterns_to_check:
            print(f"No patterns to check for {args.community}")
        else:
            is_valid, report = sc.validate_sensitivity(
                args.community,
                motifs=[args.motif] if args.motif else None,
            )
            print(report.summary())
            if not is_valid:
                print("\n⚠️  Cultural sensitivity issues detected!")
                if report.approval_needed:
                    print("   Community approval is required.")
                workflow = sc.get_approval_workflow()
                if workflow:
                    print("\nApproval workflow:")
                    for step in workflow:
                        print(f"   {step['step']}. {step['name']}: {step['description']}")
                sys.exit(1)
            else:
                print("\n✓ Pattern set passes cultural sensitivity check.")
        return

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Determine complexity ───────────────────────────────

    complexity = args.complexity
    if complexity is None:
        complexity = cx.get_default_level()
        # Check community range
        allowed = cx.get_community_complexity_range(args.community)
        if complexity not in allowed:
            complexity = allowed[0] if allowed else "beginner"

    # Validate complexity
    is_valid, errors = cx.validate_complexity(args.community, complexity)
    if not is_valid:
        print(f"Warning: {', '.join(errors)}")

    # ── Generate ────────────────────────────────────────────

    if args.mix:
        all_seqs = []
        for f in args.mix:
            entries = parse_fasta(f)
            all_seqs.extend(seq for _, seq in entries)
        gen = PatternGenerator(
            grid_size=args.size,
            community=args.community,
            complexity=complexity,
        )
        grid = gen.generate_grid(
            all_seqs[0] if all_seqs else "ATGC",
            pattern_type=args.type,
            seed=args.seed,
        )
        name = "mixed"
    else:
        input_path = Path(args.input)
        if input_path.exists() and input_path.suffix in (".fasta", ".fa"):
            entries = parse_fasta(input_path)
            header, seq = entries[0]
            name = Path(input_path.stem)
        else:
            seq = parse_string(args.input)
            name = "input"

        gen = PatternGenerator(
            grid_size=args.size,
            community=args.community,
            complexity=complexity,
        )
        grid = gen.generate_grid(
            seq,
            pattern_type=args.type,
            seed=args.seed,
            motif=args.motif,
        )

    # ── Apply cultural rules ────────────────────────────────

    rule = get_community_rules(args.community)
    grid = apply_cultural_rules(grid, rule=rule)

    # ── Export ───────────────────────────────────────────────

    base = out_dir / f"{name}_{args.type}_{args.size}x{args.size}"

    png_path = export_png(grid, f"{base}.png")
    jac_path = export_jac(grid, f"{base}.jac")
    txt_path = export_txt(grid, f"{base}.txt")

    print(f"Pattern: {args.size}×{args.size} {args.type}")
    print(f"Community: {rule.name} ({rule.border_style} border)")
    print(f"Complexity: {complexity}")
    if args.motif:
        print(f"Motif: {args.motif}")
    print(f"  PNG: {png_path}")
    print(f"  JAC: {jac_path}")
    print(f"  TXT: {txt_path}")


if __name__ == "__main__":
    main()
