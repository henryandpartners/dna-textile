#!/usr/bin/env python3
"""CLI entry point — generate textile patterns from DNA.

Phase 3: Multi-layer pipeline with tribe-specific weaving engines,
motif/symbol generation, and hierarchical composition.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dna_parser import parse_fasta, parse_string
from src.pipeline import Pipeline, PipelineConfig, generate_pattern
from src.cultural_rules import get_community_rules, list_communities, get_community_info
from src.exporters import export_png, export_jac, export_txt, export_punch_card, export_punch_card_csv, export_lace_chart
from src.repeat_preview import export_repeat_analysis
from src.mixer import mix_patterns, mix_sequences
from src import motif_library as ml
from src import color_palette as cp
from src import border_style as bs
from src import complexity as cx
from src import sensitivity_checker as sc
from src import weaving_engine as we
from src import motif_generator as mg
from src.dna_features import extract_features


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DNA Textile Pattern Generator (Phase 3 — Multi-Layer Pipeline)"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="examples/karen_sample.fasta",
        help="FASTA file or DNA string",
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
        "--complexity",
        choices=["beginner", "intermediate", "expert"],
        default="intermediate",
        help="Pattern complexity level",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--pattern-type", "-p",
        choices=[
            "stripe", "grid", "spiral", "random",
            "cellular_automata", "lace",
            "codon_tile", "phase_shift",
            "fractal_koch", "voronoi", "wave_interference",
            "perlin_noise", "l_system", "fourier_pattern",
            "diffusion", "mosaic",
        ],
        default="stripe",
        help="Pattern algorithm (default: stripe)",
    )

    # ── Motif options ─────────────────────────────────────
    motif_group = parser.add_argument_group("motif settings")
    motif_group.add_argument(
        "--no-motif",
        action="store_true",
        help="Disable motif layer",
    )
    motif_group.add_argument(
        "--motif-placement",
        choices=["center", "grid", "scatter", "border"],
        default="center",
        help="Where to place motifs (default: center)",
    )
    motif_group.add_argument(
        "--motif-count",
        type=int,
        default=1,
        help="Number of motifs (default: 1)",
    )
    motif_group.add_argument(
        "--motif-types",
        nargs="+",
        default=[],
        help="Motif types to generate (default: auto from DNA)",
    )
    motif_group.add_argument(
        "--motif-size",
        type=int,
        default=20,
        help="Motif grid size (default: 20)",
    )

    # ── Symbol options ────────────────────────────────────
    symbol_group = parser.add_argument_group("symbol settings")
    symbol_group.add_argument(
        "--symbol",
        action="store_true",
        help="Enable symbol layer",
    )
    symbol_group.add_argument(
        "--symbol-type",
        default="auto",
        help="Symbol type: auto, totem, mandala, clan_shield, spirit_mask, cosmic_diagram, story_panel",
    )
    symbol_group.add_argument(
        "--symbol-size",
        type=int,
        default=40,
        help="Symbol grid size (default: 40)",
    )

    # ── Layer opacity ─────────────────────────────────────
    layer_group = parser.add_argument_group("layer settings")
    layer_group.add_argument(
        "--opacity-structure",
        type=float,
        default=0.8,
        help="Structure layer opacity (default: 0.8)",
    )
    layer_group.add_argument(
        "--opacity-detail",
        type=float,
        default=0.5,
        help="Detail layer opacity (default: 0.5)",
    )
    layer_group.add_argument(
        "--opacity-motif",
        type=float,
        default=0.7,
        help="Motif layer opacity (default: 0.7)",
    )
    layer_group.add_argument(
        "--opacity-symbol",
        type=float,
        default=0.6,
        help="Symbol layer opacity (default: 0.6)",
    )

    # ── Mix options ───────────────────────────────────────
    parser.add_argument(
        "--mix",
        nargs="+",
        metavar="FASTA",
        help="Mix multiple FASTA files",
    )

    # ── Stitch ratio ──────────────────────────────────────
    parser.add_argument(
        "--stitch-ratio",
        type=float,
        default=1.0,
        help="Stitch aspect ratio (width:height). Default 1.0; typical knitting ~0.85",
    )

    # ── Costume / garment options ─────────────────────────
    costume_group = parser.add_argument_group("costume settings")
    costume_group.add_argument(
        "--output-format",
        choices=["grid", "costume", "costume_preview", "sewing_pattern",
                 "punch_card", "punch_card_csv", "lace_chart"],
        default="grid",
        help="Output format: grid (default), costume, costume_preview, sewing_pattern, punch_card, punch_card_csv, lace_chart",
    )
    costume_group.add_argument(
        "--garment-size",
        choices=["S", "M", "L", "XL"],
        default="M",
        help="Garment size for sewing pattern (default: M)",
    )
    costume_group.add_argument(
        "--seam-allowance",
        type=float,
        default=1.0,
        help="Seam allowance in cm (default: 1.0)",
    )
    costume_group.add_argument(
        "--fabric-width",
        type=float,
        default=150.0,
        help="Fabric width in cm (default: 150)",
    )
    costume_group.add_argument(
        "--garment",
        default="default",
        help="Garment name for costume output (default: first available)",
    )
    costume_group.add_argument(
        "--density-mode",
        choices=["entropy", "fixed"],
        default="entropy",
        help="Density mode: entropy-driven or fixed (default: entropy)",
    )

    # ── Info commands ─────────────────────────────────────
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
        help="List available weaving engines",
    )
    parser.add_argument(
        "--list-garments",
        action="store_true",
        help="List available garment templates for selected community",
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
    parser.add_argument(
        "--sensitivity-check",
        action="store_true",
        help="Run cultural sensitivity check",
    )

    args = parser.parse_args()

    # ── List commands ─────────────────────────────────────

    if args.list_communities:
        print("Available communities:")
        for name in list_communities():
            rule = get_community_rules(name)
            engine_key = name.lower().replace(" ", "_")
            has_engine = "✓" if engine_key in we.list_engines() else " "
            print(f"  [{has_engine}] {name}: {rule.region} ({rule.language_family})")
        print("\n[✓] = has custom weaving engine")
        return

    if args.list_motifs:
        motifs = ml.get_motifs(args.community)
        if not motifs:
            print(f"No motifs found for: {args.community}")
        else:
            print(f"Motifs for {args.community}:")
            for m in motifs:
                print(f"  {m['name']} ({m['type']}, {m['complexity']})")
        print("\nGenerated motif types:")
        gen = mg.MotifGenerator(args.community)
        types = [
            "diamond", "triangle", "zigzag", "wave", "spiral",
            "butterfly", "naga", "elephant", "fish", "bird",
            "lotus", "bamboo", "rice", "flower", "tree",
            "spirit_gate", "sun", "moon", "sacred_geometry",
            "clan_mark", "ancestor_mark",
        ]
        for t in types:
            print(f"  {t}")
        print("\nGenerated symbol types:")
        symbols = ["totem", "mandala", "clan_shield", "spirit_mask", "cosmic_diagram", "story_panel"]
        for s in symbols:
            print(f"  {s}")
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
        print("Available weaving engines:")
        for name in we.list_engines():
            print(f"  {name}")
        print("\nCommunities without custom engine use GenericEngine.")
        return

    if args.list_garments:
        from .garment_templates import get_garment_templates, list_all_garments
        templates = get_garment_templates(args.community)
        if not templates:
            print(f"No garment templates for: {args.community}")
            print("\nAvailable communities with garments:")
            for community, names in list_all_garments().items():
                print(f"  {community}: {', '.join(names)}")
        else:
            print(f"Garments for {args.community}:")
            for t in templates:
                regions = [r.name for r in t.regions]
                print(f"  {t.garment_name} ({t.total_width}×{t.total_height}): {', '.join(regions)}")
        return

    if args.info:
        info = get_community_info(args.community)
        print(f"Community: {info['name']}")
        print(f"  Native name: {info['native_name']}")
        print(f"  Language family: {info['language_family']}")
        print(f"  Region: {info['region']}")
        print(f"  Weaving technique: {info['weaving_technique']}")
        print(f"  Complexity range: {', '.join(info['complexity_range'])}")
        print(f"  Sacred motifs: {', '.join(info['sacred_motifs'])}")
        print(f"  Taboo patterns: {', '.join(info['taboo_patterns'])}")
        engine_key = args.community.lower().replace(" ", "_")
        has_engine = engine_key in we.list_engines()
        print(f"  Custom weaving engine: {'Yes' if has_engine else 'No (using GenericEngine)'}")
        print(f"\nTextile history:")
        print(f"  {info['textile_history']}")
        print(f"\nCultural significance:")
        print(f"  {info['cultural_significance']}")
        return

    if args.analyze:
        input_path = Path(args.input)
        if input_path.exists() and input_path.suffix in (".fasta", ".fa"):
            entries = parse_fasta(input_path)
            header, seq = entries[0]
        else:
            seq = parse_string(args.input)
            header = "input"

        features = extract_features(seq)
        print(f"DNA Sequence Analysis: {header}")
        print(f"  Length: {features.length} bp")
        print(f"  Base composition:")
        for base in "ATGC":
            print(f"    {base}: {features.base_counts[base]} ({features.base_frequencies[base]:.1%})")
        print(f"  GC content: {features.gc_content:.1%}")
        print(f"  Shannon entropy: {features.entropy:.3f}")
        print(f"  Dominant dinucleotide: {features.dominant_dinuc}")
        print(f"  Dominant trinucleotide: {features.dominant_trinuc}")
        print(f"  Dominant tetranucleotide: {features.dominant_tetra}")
        print(f"  Homopolymer runs: {len(features.homopolymer_runs)}")
        for base, start, length in features.homopolymer_runs[:5]:
            print(f"    {base}×{length} at position {start}")
        print(f"  Palindromes: {len(features.palindromes)}")
        for seq_p, start, length in features.palindromes[:5]:
            print(f"    {seq_p} at position {start} (len={length})")
        print(f"  Tandem repeats: {len(features.repeats)}")
        for motif, start, count in features.repeats[:5]:
            print(f"    {motif}×{count} at position {start}")
        print(f"  Codons: {len(features.codons)}")
        print(f"\nDerived scores:")
        print(f"  Complexity: {features.complexity_score:.3f}")
        print(f"  Symmetry: {features.symmetry_score:.3f}")
        print(f"  Rhythm: {features.rhythm_score:.3f}")
        return

    if args.sensitivity_check:
        is_valid, report = sc.validate_sensitivity(
            args.community,
            motifs=args.motif_types if args.motif_types else None,
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

    # ── Generate ──────────────────────────────────────────

    if args.mix:
        all_seqs = []
        for f in args.mix:
            entries = parse_fasta(f)
            all_seqs.extend(seq for _, seq in entries)
        seq = mix_sequences(all_seqs)
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

    # Build config
    config = PipelineConfig(
        grid_size=args.size,
        community=args.community,
        complexity=args.complexity,
        seed=args.seed,
        include_motif=not args.no_motif,
        include_symbol=args.symbol,
        motif_size=args.motif_size,
        symbol_size=args.symbol_size,
        motif_placement=args.motif_placement,
        motif_count=args.motif_count,
        motif_types=args.motif_types,
        symbol_type=args.symbol_type,
        layer_opacity={
            "background": 1.0,
            "structure": args.opacity_structure,
            "detail": args.opacity_detail,
            "motif": args.opacity_motif,
            "symbol": args.opacity_symbol,
            "border": 1.0,
        },
        density_mode=args.density_mode,
        output_format=args.output_format,
        garment_name=args.garment,
        pattern_type=args.pattern_type,
        stitch_ratio=args.stitch_ratio,
        garment_size=args.garment_size,
        seam_allowance_cm=args.seam_allowance,
        fabric_width_cm=args.fabric_width,
    )

    pipeline = Pipeline(config)
    result = pipeline.run(seq)

    # ── Export ────────────────────────────────────────────

    base = out_dir / f"{name}_{args.community}_{args.complexity}_{args.size}x{args.size}"

    fmt = args.output_format
    if fmt == "costume":
        # result is Dict[str, np.ndarray]
        from .costume_mapper import CostumeMapper
        mapper = CostumeMapper(args.community, seed=args.seed)
        garments = mapper.list_available_garments()
        print(f"Costume output ({args.community}):")
        for region_name, region_grid in result.items():
            region_path = export_png(region_grid, f"{base}_{region_name}.png")
            print(f"  Region '{region_name}': {region_path} ({region_grid.shape[1]}x{region_grid.shape[0]})")
        print(f"  Garment: {args.garment}")
        if garments:
            print(f"  Available garments: {', '.join(garments)}")

    elif fmt == "costume_preview":
        # result is a single composite grid
        png_path = export_png(result, f"{base}_preview.png")
        print(f"Costume preview: {args.size}×{args.size}")
        print(f"  PNG: {png_path}")

    elif fmt == "sewing_pattern":
        # result is a dict with sewing pattern package
        from .exporters import export_sewing_pattern
        sewing_path = export_sewing_pattern(
            result,
            f"{base}_sewing.zip",
            args.community,
            args.garment,
            args.garment_size,
            args.seam_allowance,
            args.fabric_width,
        )
        print(f"Sewing pattern ({args.community} {args.garment} size {args.garment_size}):")
        print(f"  ZIP: {sewing_path}")
        if isinstance(result, dict):
            for key, val in result.items():
                print(f"  {key}: {val}")

    elif fmt == "punch_card":
        # Punch card chart export
        pc_path = export_punch_card(
            result, f"{base}_punch_card.png",
            stitch_ratio=args.stitch_ratio,
        )
        print(f"Punch card chart: {args.size}×{args.size} (stitch_ratio={args.stitch_ratio})")
        print(f"  PNG: {pc_path}")

    elif fmt == "punch_card_csv":
        # Punch card CSV export for digital machines
        csv_path = export_punch_card_csv(
            result, f"{base}_punch_card.csv",
            stitch_ratio=args.stitch_ratio,
        )
        print(f"Punch card CSV: {args.size}×{args.size} (stitch_ratio={args.stitch_ratio})")
        print(f"  CSV: {csv_path}")

    elif fmt == "lace_chart":
        # Lace chart export
        lace_path = export_lace_chart(result, f"{base}_lace_chart.png")
        print(f"Lace chart: {args.size}×{args.size}")
        print(f"  PNG: {lace_path}")

    else:
        # Grid output (default)
        png_path = export_png(result, f"{base}.png")
        jac_path = export_jac(result, f"{base}.jac")
        txt_path = export_txt(result, f"{base}.txt")

        rule = get_community_rules(args.community)
        engine_key = args.community.lower().replace(" ", "_")
        engine_name = engine_key if engine_key in we.list_engines() else "generic"

        print(f"Pattern: {args.size}×{args.size}")
        print(f"Community: {rule.name}")
        print(f"Weaving engine: {engine_name}")
        print(f"Complexity: {args.complexity}")
        if not args.no_motif:
            print(f"Motifs: {args.motif_placement} (count={args.motif_count})")
            if args.motif_types:
                print(f"  Types: {', '.join(args.motif_types)}")
        if args.symbol:
            print(f"Symbol: {args.symbol_type}")
        print(f"Border: {rule.border_style} ({rule.border_width}px)")
        print(f"  PNG: {png_path}")
        print(f"  JAC: {jac_path}")
        print(f"  TXT: {txt_path}")

        # Also generate repeat preview
        try:
            repeat_info = export_repeat_analysis(result, out_dir, prefix=f"{name}_{args.community}_{args.pattern_type}")
            print(f"  Repeat unit: {repeat_info['repeat_width']}×{repeat_info['repeat_height']}")
            print(f"  Repeat isolated: {repeat_info['isolated_path']}")
            print(f"  Repeat tiled: {repeat_info['tiled_path']}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
