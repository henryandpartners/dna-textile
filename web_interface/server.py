"""Flask server for DNA Textile Web Interface.

Run:  python -m src.web_interface.server
Or:   python src/web_interface/server.py

Serves the web UI and provides a REST API for pattern generation and export.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
from flask import Flask, request, jsonify, send_file, send_from_directory

# Ensure project root is importable
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.dna_parser import parse_string
from src.pattern_generator import PatternGenerator
from src.exporters import export_png, export_jac, export_txt
from src.repeat_preview import detect_repeat_unit

app = Flask(
    __name__,
    static_folder=str(Path(__file__).resolve().parent),
    static_url_path="/",
)

WEB_DIR = Path(__file__).resolve().parent


# ── Helpers ──────────────────────────────────────────────────

def _grid_to_list(grid: np.ndarray) -> list:
    """Convert numpy grid to list of [R,G,B] tuples for JSON."""
    return grid.reshape(-1, 3).tolist()


def _generate_grid_data(
    sequence: str,
    pattern_type: str = "stripe",
    community: str = "generic",
    grid_size: int = 100,
    stitch_ratio: float = 1.0,
    complexity: str = "intermediate",
    seed: int | None = None,
) -> dict:
    """Run pattern generation and return JSON-serialisable dict."""
    seq = parse_string(sequence)
    gen = PatternGenerator(
        grid_size=grid_size,
        community=community,
        complexity=complexity,
        seed=seed,
        stitch_ratio=stitch_ratio,
    )
    grid = gen.generate_grid(seq, pattern_type=pattern_type)

    # Detect repeat
    rw, rh = detect_repeat_unit(grid)
    repeat_grid = grid[:rh, :rw, :]

    return {
        "width": grid.shape[1],
        "height": grid.shape[0],
        "grid": _grid_to_list(grid),
        "pattern_type": pattern_type,
        "community": community,
        "repeat": {
            "width": rw,
            "height": rh,
            "repeat_w": rw,
            "repeat_h": rh,
            "grid": _grid_to_list(repeat_grid),
        },
    }


def _grid_to_png_bytes(grid: np.ndarray) -> bytes:
    """Render grid to PNG bytes."""
    from PIL import Image
    img = Image.fromarray(grid.astype(np.uint8), mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _grid_to_punch_card_bytes(grid: np.ndarray, stitch_ratio: float = 1.0) -> bytes:
    """Render punch card chart to PNG bytes."""
    from src.exporters import export_punch_card
    path = export_punch_card(grid, "/tmp/_pc.png", stitch_ratio=stitch_ratio)
    return path.read_bytes()


def _grid_to_lace_chart_bytes(grid: np.ndarray) -> bytes:
    """Render lace chart to PNG bytes."""
    from src.exporters import export_lace_chart
    path = export_lace_chart(grid, "/tmp/_lace.png")
    return path.read_bytes()


def _grid_to_csv_bytes(grid: np.ndarray, stitch_ratio: float = 1.0) -> bytes:
    """Render punch card CSV to bytes."""
    from src.exporters import export_punch_card_csv
    path = export_punch_card_csv(grid, "/tmp/_pc.csv", stitch_ratio=stitch_ratio)
    return path.read_bytes()


def _grid_to_jac_bytes(grid: np.ndarray) -> bytes:
    """Render JAC to bytes."""
    path = export_jac(grid, "/tmp/_out.jac")
    return path.read_bytes()


# ── Routes ───────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/api/generate")
def api_generate():
    """Generate pattern and return grid data as JSON."""
    try:
        data = _generate_grid_data(
            sequence=request.args.get("sequence", ""),
            pattern_type=request.args.get("pattern_type", "stripe"),
            community=request.args.get("community", "generic"),
            grid_size=int(request.args.get("grid_size", 100)),
            stitch_ratio=float(request.args.get("stitch_ratio", 1.0)),
            complexity=request.args.get("complexity", "intermediate"),
            seed=int(request.args["seed"]) if request.args.get("seed") else None,
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/export")
def api_export():
    """Export pattern in requested format and return as file download."""
    fmt = request.args.get("format", "png")
    stitch_ratio = float(request.args.get("stitch_ratio", 1.0))

    try:
        data = _generate_grid_data(
            sequence=request.args.get("sequence", ""),
            pattern_type=request.args.get("pattern_type", "stripe"),
            community=request.args.get("community", "generic"),
            grid_size=int(request.args.get("grid_size", 100)),
            stitch_ratio=stitch_ratio,
            complexity=request.args.get("complexity", "intermediate"),
            seed=int(request.args["seed"]) if request.args.get("seed") else None,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    grid_np = np.array(data["grid"], dtype=np.uint8).reshape(
        (data["height"], data["width"], 3)
    )

    if fmt == "png":
        return send_file(
            io.BytesIO(_grid_to_png_bytes(grid_np)),
            mimetype="image/png",
            download_name="pattern.png",
        )

    elif fmt == "jac":
        return send_file(
            io.BytesIO(_grid_to_jac_bytes(grid_np)),
            mimetype="text/plain",
            download_name="pattern.jac",
        )

    elif fmt == "punch_card":
        return send_file(
            io.BytesIO(_grid_to_punch_card_bytes(grid_np, stitch_ratio)),
            mimetype="image/png",
            download_name="punch_card.png",
        )

    elif fmt == "lace_chart":
        return send_file(
            io.BytesIO(_grid_to_lace_chart_bytes(grid_np)),
            mimetype="image/png",
            download_name="lace_chart.png",
        )

    elif fmt == "punch_card_csv":
        return send_file(
            io.BytesIO(_grid_to_csv_bytes(grid_np, stitch_ratio)),
            mimetype="text/csv",
            download_name="punch_card.csv",
        )

    elif fmt == "tiled":
        # Return tiled repeat preview
        from src.repeat_preview import export_repeat_tiled
        rw, rh = detect_repeat_unit(grid_np)
        path = export_repeat_tiled(
            grid_np, "/tmp/_tiled.png",
            repeats_x=4, repeats_y=4,
            repeat_w=rw, repeat_h=rh,
        )
        return send_file(
            str(path),
            mimetype="image/png",
            download_name="tiled_preview.png",
        )

    else:
        return jsonify({"error": f"Unknown format: {fmt}"}), 400


# ── Main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"DNA Textile Web Interface → http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
