#!/usr/bin/env python3
"""CLI entry point — DNA Textile Pattern Generator.

Phase 3: Full 5-layer pipeline with tribe-specific weaving engines,
procedural motifs, and cultural rules.

Usage:
    python -m src.main "ATGC..." -c karen
    python -m src.main "ATGC..." -c hmong --symbol --motif-placement grid
    python -m src.main "ATGC..." -c akha --output pattern.png
    python -m src.main examples/karen_sample.fasta -c karen --pipeline
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
from src import dna_features
from src import weaving_engine
from src import motif_generator
from src import pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DNA Textile Pattern Generator (Phase 3 — 5-Layer Pipeline)"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="examples/karen_sample.fasta",
        help="FASTA file or DNA string",
    )
    # ── Phase 2 options (legacy) ──────────────────────────
    parser.add_argument(
        "--type", "-t",
        choices=["stripe", "grid", "spiral", "random"],
        default="grid",
        help="Pattern type for Phase 2 generator (default: grid)",
    )
    parser.add_argument(
        "--size", "-s",
        type=int,
        default=200,
        help="Grid size NxN (default: 200)",
    )
    parser.add_argument(
        "--community", "-c",
        default="generic",
        help="Community: " + ", ".join(list_communities()),
    )
    parser.add_argument(
        "--motif", "-m",
        default=None,
        help="Motif name to overlay (Phase 2) or motif type (Phase 3)",
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
        help="Run cultural sensitivity check",
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory or file path (default: output/)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--mix",
        nargs="+",
        metavar="FASTA",
        help="Mix multiple FASTA files",
    )

    # ── Phase 3 options ──────────────────────────────────
    parser.add_argument(
        "--pipeline", "-p",
        action="store_true",
        help="Use Phase 3 pipeline (5-layer composition)",
    )
    parser.add_argument(
        "--no-structure",
        action="store_true",
        help="Skip structure layer (Phase 3)",
    )
    parser.add_argument(
        "--no-detail",
        action="store_true",
        help="Skip detail layer (Phase 3)",
    )
    parser.add_argument(
        "--no-motifs",
        action="store_true",
        help="Skip motif layer (Phase 3)",
    )
    parser.add_argument(
        "--symbol",
        action="store_true",
        help="Include symbol layer (Phase 3)",
    )
    parser.add_argument(
        "--motif-placement",
        choices=["grid", "scatter", "dna"],
        default="grid",
        help="Motif placement strategy (Phase 3, default: grid)",
    )
    parser.add_argument(
        "--motif-count",
        type=int,
        default=6,
        help="Number of motifs to place (Phase 3, default: 6)",
    )
    parser.add_argument(
        "--symbol-count",
        type=int,
        default=1,
        help="Number of symbols to place (Phase 3, default: 1)",
    )
    parser.add_argument(
        "--no-cultural-rules",
        action="store_true",
        help="Skip cultural rules application (Phase 3)",
    )

    # ── List commands ────────────────────────────────────
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
        "--list-engines",
        action="store_true",
        help="List available weaving engines (Phase 3)",
    )
    parser.add_argument(
        "--list-motif-types",
        action="store_true",
        help="List procedural motif types (Phase 3)",
    )
    parser.add_argument(
        "--list-symbol-types",
        action="store_true",
        help="List symbol types (Phase 3)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show community textile info",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze DNA features and show report",
    )

    args = parser.parse_args()

    # ── List commands ────────────────────────────────────

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

    if args.list_engines:
        print("Available weaving engines (Phase 3):")
        for key in weaving_engine.list_engines():
            print(f"  {key}")
        return

    if args.list_motif_types:
        print("Procedural motif types (Phase 3):")
        for name in sorted(motif_generator.MOTIF_FUNCTIONS.keys()):
            print(f"  {name}")
        return

    if args.list_symbol_types:
        print("Symbol types (Phase 3):")
        for name in sorted(motif_generator.SYMBOL_FUNCTIONS.keys()):
            print(f"  {name}")
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

    # ── Sensitivity check ────────────────────────────────

    if args.sensitivity_check:
        patterns_to_check = []
        if args.motif:
            patterns_to_check.append(args.motif)
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

    # ── DNA analysis ─────────────────────────────────────

    if args.analyze:
        input_path = Path(args.input)
        if input_path.exists() and input_path.suffix in (".fasta", ".fa"):
            entries = parse_fasta(input_path)
            header, seq = entries[0]
            print(f"Sequence: {header} ({len(seq)} bp)")
        else:
            seq = parse_string(args.input)
            print(f"Sequence: {len(seq)} bp")

        features = dna_features.extract_features(seq)
        print(f"\n── DNA Feature Analysis ──")
        print(f"  Length: {features['length']} bp")
        print(f"  GC Content: {features['gc_content']:.2%}")
        print(f"  Shannon Entropy: {features['shannon_entropy']:.4f} bits")
        print(f"  Base Composition: A={features['base_composition']['A']:.2%} "
              f"T={features['base_composition']['T']:.2%} "
              f"G={features['base_composition']['G']:.2%} "
              f"C={features['base_composition']['C']:.2%}")
        print(f"  Palindromes: {features['palindrome_count']}")
        print(f"  Homopolymers (≥3): {features['homopolymer_stats']['total_runs']}")
        print(f"  Tandem Repeats: {features['repeat_count']}")
        print(f"  Microsatellites: {len(features['microsatellites'])}")
        codons = features['codons']
        print(f"  Codons (frame 0): {codons['total_codons']} total, "
              f"{codons['start_codons']} ATG, {codons['stop_codons']} stop")
        top_3mers = dna_features.dominant_kmers(seq, k=3, top_n=5)
        print(f"  Top 3-mers: {', '.join(f'{km}({c})' for km, c in top_3mers)}")
        top_4mers = dna_features.dominant_kmers(seq, k=4, top_n=5)
        print(f"  Top 4-mers: {', '.join(f'{km}({c})' for km, c in top_4mers)}")

        # DNA-driven selections
        motif = motif_generator.select_motif_from_dna(features)
        symbol = motif_generator.select_symbol_from_dna(features)
        complexity = dna_features.entropy_to_complexity(features['shannon_entropy'])
        print(f"\n── DNA-Driven Pattern Selection ──")
        print(f"  Suggested motif: {motif}")
        print(f"  Suggested symbol: {symbol}")
        print(f"  Suggested complexity: {complexity}")
        return

    # ── Determine complexity ─────────────────────────────

    complexity = args.complexity
    if complexity is None:
        complexity = cx.get_default_level()
        allowed = cx.get_community_complexity_range(args.community)
        if complexity not in allowed:
            complexity = allowed[0] if allowed else "beginner"

    is_valid, errors = cx.validate_complexity(args.community, complexity)
    if not is_valid:
        print(f"Warning: {', '.join(errors)}")

    # ── Phase 3 Pipeline ─────────────────────────────────

    if args.pipeline:
        _run_phase3_pipeline(args, complexity)
        return

    # ── Phase 2 Generator (legacy) ───────────────────────

    _run_phase2_generator(args, complexity)


def _run_phase3_pipeline(args: argparse.Namespace, complexity: str) -> None:
    """Run the Phase 3 5-layer pipeline."""
    # Load sequence
    input_path = Path(args.input)
    if input_path.exists() and input_path.suffix in (".fasta", ".fa"):
        entries = parse_fasta(input_path)
        header, seq = entries[0]
        name = Path(input_path.stem)
    else:
        seq = parse_string(args.input)
        name = Path("input")

    # Determine output path
    out = args.output
    if out.endswith((".png", ".jpg", ".bmp")):
        output_path = out
        out_dir = str(Path(out).parent)
    else:
        out_dir = out
        output_path = None

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Build config
    config = pipeline.PipelineConfig(
        community=args.community,
        grid_size=args.size,
        complexity=complexity,
        seed=args.seed,
        motif_placement=args.motif_placement,
        include_symbols=args.symbol,
        include_motifs=not args.no_motifs,
        include_detail=not args.no_detail,
        include_structure=not args.no_structure,
        motif_count=args.motif_count,
        symbol_count=args.symbol_count,
        output_path=output_path,
        apply_cultural_rules=not args.no_cultural_rules,
    )

    # Run pipeline
    result = pipeline.run_pipeline(seq, config)

    # Export
    if not output_path:
        png_path = export_png(result.grid, f"{out_dir}/{name}_phase3_{args.size}x{args.size}.png")
        jac_path = export_jac(result.grid, f"{out_dir}/{name}_phase3_{args.size}x{args.size}.jac")
        txt_path = export_txt(result.grid, f"{out_dir}/{name}_phase3_{args.size}x{args.size}.txt")
    else:
        png_path = Path(output_path).resolve()
        jac_path = export_jac(result.grid, f"{png_path.stem}.jac")
        txt_path = export_txt(result.grid, f"{png_path.stem}.txt")

    # Print summary
    print(f"Phase 3 Pipeline — 5-Layer Composition")
    print(f"  Sequence: {len(seq)} bp")
    print(f"  GC Content: {result.features['gc_content']:.2%}")
    print(f"  Entropy: {result.features['shannon_entropy']:.4f}")
    print(f"  Community: {args.community}")
    print(f"  Grid: {args.size}×{args.size}")
    print(f"  Complexity: {complexity}")
    print(f"  Seed: {args.seed}")
    print(f"  Motif placement: {args.motif_placement}")
    print(f"  Symbols: {'yes' if args.symbol else 'no'}")
    print(f"  Layers: {list(result.layers.keys())}")
    print(f"  PNG: {png_path}")
    print(f"  JAC: {jac_path}")
    print(f"  TXT: {txt_path}")


def _run_phase2_generator(args: argparse.Namespace, complexity: str) -> None:
    """Run the Phase 2 pattern generator (legacy)."""
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

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

    # Apply cultural rules
    rule = get_community_rules(args.community)
    grid = apply_cultural_rules(grid, rule=rule)

    # Export
    base = out_dir / f"{name}_{args.type}_{args.size}x{args.size}"

    png_path = export_png(grid, f"{base}.png")
    jac_path = export_jac(grid, f"{base}.jac")
    txt_path = export_txt(grid, f"{base}.txt")

    print(f"Phase 2 Generator — {args.size}×{args.size} {args.type}")
    print(f"Community: {rule.name} ({rule.border_style} border)")
    print(f"Complexity: {complexity}")
    if args.motif:
        print(f"Motif: {args.motif}")
    print(f"  PNG: {png_path}")
    print(f"  JAC: {jac_path}")
    print(f"  TXT: {txt_path}")


if __name__ == "__main__":
    main()
