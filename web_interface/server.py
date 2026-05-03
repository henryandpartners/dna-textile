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
from PIL import Image

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


# ── Community Reference Images ───────────────────────────────

@app.route("/api/community-images")
def api_community_images():
    """Return list of image URLs for a community."""
    community = request.args.get("community", "generic")
    base = _project_root
    # Try the community directory name (handle multi-word like "Thai Lue")
    dirs_to_check = [community.replace(" ", "_"), community.replace(" ", ""), community]
    image_urls = []
    for dirname in dirs_to_check:
        img_dir = base / dirname
        if img_dir.exists() and img_dir.is_dir():
            for ext in ("jpg", "jpeg", "png", "gif", "webp"):
                for f in sorted(img_dir.glob(f"*.{ext}")):
                    rel = f.relative_to(base)
                    image_urls.append(f"/api/serve-image/{rel}")
            break
    return jsonify({"community": community, "images": image_urls, "count": len(image_urls)})


@app.route("/api/serve-image/<path:filepath>")
def api_serve_image(filepath):
    """Serve a community image file."""
    base = _project_root
    full_path = base / filepath
    # Security: ensure path is within project root
    try:
        full_path.resolve().relative_to(base.resolve())
    except ValueError:
        return "Invalid path", 403
    if not full_path.exists() or not full_path.is_file():
        return "Not found", 404
    return send_file(str(full_path))


# ── Image Upload & Color Extraction ──────────────────────────

@app.route("/api/extract-colors", methods=["POST"])
def api_extract_colors():
    """Extract dominant colors from an uploaded image."""
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    try:
        img = Image.open(file.stream).convert("RGB")
        # Resize for processing
        img.thumbnail((200, 200))
        # Quantize to reduce colors
        quantized = img.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()
        color_counts = quantized.getcolors(maxcolors=256)

        if not color_counts:
            return jsonify({"error": "Could not extract colors"}), 400

        # Sort by count (descending)
        color_counts.sort(key=lambda x: x[0], reverse=True)

        # Extract dominant colors
        colors = []
        for count, idx in color_counts[:6]:
            r = palette[idx * 3]
            g = palette[idx * 3 + 1]
            b = palette[idx * 3 + 2]
            colors.append({"rgb": [r, g, b], "count": count, "hex": f"#{r:02x}{g:02x}{b:02x}"})

        return jsonify({"colors": colors, "total_pixels": img.width * img.height})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-from-colors", methods=["POST"])
def api_generate_from_colors():
    """Generate a pattern using uploaded image's color palette."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    colors = data.get("colors", [])
    sequence = data.get("sequence", "ATGCATGC")

    if len(colors) < 2:
        return jsonify({"error": "Need at least 2 colors"}), 400

    # Build a color map from extracted colors
    bases = ["A", "T", "G", "C"]
    color_map = {}
    for i, c in enumerate(colors[:4]):
        color_map[bases[i]] = tuple(c["rgb"])

    # Generate using the custom color map
    seq = parse_string(sequence)
    gen = PatternGenerator(
        grid_size=int(data.get("grid_size", 100)),
        color_map=color_map,
        community=data.get("community", "generic"),
        complexity=data.get("complexity", "intermediate"),
        stitch_ratio=float(data.get("stitch_ratio", 1.0)),
    )
    grid = gen.generate_grid(seq, pattern_type=data.get("pattern_type", "stripe"))

    return jsonify({
        "width": grid.shape[1],
        "height": grid.shape[0],
        "grid": _grid_to_list(grid),
        "pattern_type": data.get("pattern_type", "stripe"),
        "community": data.get("community", "generic"),
        "colors_used": len(colors),
    })


# ── Main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"DNA Textile Web Interface → http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
