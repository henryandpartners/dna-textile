"use client";

import { useState, useRef, useCallback } from "react";
import Image from "next/image";
import Link from "next/link";
import { parseDNA, generatePattern, downloadPNG, imageDataToDataURL, type PatternConfig, type PatternResult, type PatternType, type Community, type Complexity } from "@/lib/dna-pattern";

const COMMUNITIES: { value: Community; label: string }[] = [
  { value: "karen", label: "Karen (Kayah)" }, { value: "hmong", label: "Hmong" },
  { value: "akha", label: "Akha" }, { value: "lahu", label: "Lahu" },
  { value: "lisu", label: "Lisu" }, { value: "generic", label: "Generic" },
];

const PATTERN_TYPES: { value: PatternType; label: string; icon: string }[] = [
  { value: "stripe", label: "Stripe", icon: "▮" }, { value: "grid", label: "Grid", icon: "▦" },
  { value: "spiral", label: "Spiral", icon: "◎" }, { value: "random", label: "Random", icon: "◈" },
  { value: "cellular_automata", label: "Cellular", icon: "⬡" }, { value: "lace", label: "Lace", icon: "◌" },
  { value: "codon_tile", label: "Codon", icon: "⬢" }, { value: "phase_shift", label: "Phase", icon: "≋" },
  { value: "fractal_koch", label: "Fractal", icon: "❄" }, { value: "voronoi", label: "Voronoi", icon: "⬣" },
  { value: "wave_interference", label: "Wave", icon: "∿" }, { value: "perlin_noise", label: "Perlin", icon: "◫" },
  { value: "l_system", label: "L-System", icon: "⌘" }, { value: "fourier_pattern", label: "Fourier", icon: "∑" },
  { value: "diffusion", label: "Diffusion", icon: "◉" }, { value: "mosaic", label: "Mosaic", icon: "⬟" },
];

const EXAMPLES: { label: string; seq: string }[] = [
  { label: "Short (16bp)", seq: "ATGCATGCATGCATGC" },
  { label: "Gene fragment (60bp)", seq: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA" },
  { label: "Mitochondrial (200bp)", seq: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGAATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGAATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA" },
  { label: "Random 500bp", seq: Array.from({ length: 500 }, () => "ATGC"[Math.floor(Math.random() * 4)]).join("") },
];

function imageDataToSVG(imageData: ImageData): string {
  const { width, height, data } = imageData;
  let rects = "";
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const i = (y * width + x) * 4;
      const r = data[i], g = data[i + 1], b = data[i + 2], a = data[i + 3];
      const hex = `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
      rects += `<rect x="${x}" y="${y}" width="1" height="1" fill="${hex}"${a < 255 ? ` opacity="${(a / 255).toFixed(2)}"` : ""}/>`;
    }
  }
  return `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">\n${rects}\n</svg>`;
}

function downloadSVG(svgContent: string, filename: string) {
  const blob = new Blob([svgContent], { type: "image/svg+xml" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
}

export default function Home() {
  const [sequence, setSequence] = useState("");
  const [gridSize, setGridSize] = useState(64);
  const [patternType, setPatternType] = useState<PatternType>("grid");
  const [community, setCommunity] = useState<Community>("karen");
  const [complexity] = useState<Complexity>("intermediate");
  const [result, setResult] = useState<PatternResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewSize, setPreviewSize] = useState(512);
  const [mockupDataUrl, setMockupDataUrl] = useState<string>("");
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleGenerate = useCallback(() => {
    setError(null); setResult(null); setMockupDataUrl("");
    if (!sequence.trim()) { setError("Please enter a DNA sequence (A, T, G, C only)."); return; }
    try {
      const cleaned = parseDNA(sequence);
      if (cleaned.length === 0) { setError("Sequence is empty after cleaning."); return; }
      const res = generatePattern({ sequence: cleaned, gridSize, patternType, community, complexity });
      setResult(res);
      if (canvasRef.current) { canvasRef.current.width = gridSize; canvasRef.current.height = gridSize; canvasRef.current.getContext("2d")!.putImageData(res.imageData, 0, 0); }
      const mockSize = 512, offscreen = document.createElement("canvas");
      offscreen.width = mockSize; offscreen.height = mockSize;
      const offCtx = offscreen.getContext("2d")!;
      offCtx.imageSmoothingEnabled = false;
      offCtx.putImageData(res.imageData, 0, 0, 0, 0, res.gridSize, res.gridSize);
      for (let y = 0; y < mockSize; y += res.gridSize) for (let x = 0; x < mockSize; x += res.gridSize) { if (x === 0 && y === 0) continue; offCtx.drawImage(offscreen, 0, 0, res.gridSize, res.gridSize, x, y, res.gridSize, res.gridSize); }
      setMockupDataUrl(offscreen.toDataURL("image/png"));
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to generate pattern."); }
  }, [sequence, gridSize, patternType, community, complexity]);

  const handleDownloadPNG = () => { if (result) downloadPNG(result.imageData, `${community}_${patternType}_${gridSize}x${gridSize}.png`); };
  const handleDownloadSVG = () => { if (result) { const svg = imageDataToSVG(result.imageData); downloadSVG(svg, `${community}_${patternType}_${gridSize}x${gridSize}.svg`); } };
  const handleCopyDataUrl = () => { if (result) { navigator.clipboard.writeText(imageDataToDataURL(result.imageData)); alert("Data URL copied!"); } };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-6"><div className="flex items-center justify-between"><div className="flex items-center gap-3"><span className="text-3xl">🧬</span><div><h1 className="text-2xl font-bold tracking-tight">DNA Textile Pattern Generator</h1><p className="text-gray-400 text-sm mt-0.5">Encode DNA sequences into Thai indigenous textile patterns</p></div></div><Link href="/research" className="text-sm text-gray-400 hover:text-gray-200 transition px-4 py-2 rounded-lg border border-gray-700 hover:border-gray-500 flex items-center gap-2">🔬 Research</Link></div></div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-6">
            <section className="bg-gray-900 rounded-xl border border-gray-800 p-5">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">DNA Sequence</h2>
              <textarea value={sequence} onChange={(e) => setSequence(e.target.value)} placeholder="ATGCATGCATGC..." className="w-full h-32 bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-mono text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-600" />
              <div className="flex items-center justify-between mt-2 text-xs text-gray-500"><span>{sequence.replace(/\s/g, "").length} bp</span><span>GC: {sequence.replace(/\s/g, "") ? ((sequence.replace(/\s/g, "").split("").filter((b) => b === "G" || b === "C").length / sequence.replace(/\s/g, "").length) * 100).toFixed(1) : "0.0"}%</span></div>
              <div className="mt-3 flex flex-wrap gap-2"><span className="text-xs text-gray-500 self-center">Try:</span>{EXAMPLES.map((ex) => (<button key={ex.label} onClick={() => setSequence(ex.seq)} className="text-xs px-2.5 py-1 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors">{ex.label}</button>))}</div>
            </section>
            <section className="bg-gray-900 rounded-xl border border-gray-800 p-5">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Pattern Type</h2>
              <div className="grid grid-cols-4 gap-2">{PATTERN_TYPES.map((pt) => (<button key={pt.value} onClick={() => setPatternType(pt.value)} className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-all ${patternType === pt.value ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}><span className="text-lg">{pt.icon}</span>{pt.label}</button>))}</div>
            </section>
            <section className="bg-gray-900 rounded-xl border border-gray-800 p-5">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Community Palette</h2>
              <div className="space-y-1.5">{COMMUNITIES.map((c) => (<button key={c.value} onClick={() => setCommunity(c.value)} className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all ${community === c.value ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}>{c.label}</button>))}</div>
            </section>
            <section className="bg-gray-900 rounded-xl border border-gray-800 p-5">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">Grid Size</h2>
              <div className="flex items-center gap-3"><input type="range" min="16" max="128" step="8" value={gridSize} onChange={(e) => setGridSize(Number(e.target.value))} className="flex-1 accent-blue-500" /><span className="text-sm font-mono text-gray-400 w-16 text-right">{gridSize}×{gridSize}</span></div>
              <div className="text-xs text-gray-600 mt-1">Higher = more detail, slower render</div>
            </section>
            <button onClick={handleGenerate} className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 rounded-xl font-semibold text-white shadow-lg shadow-blue-600/20 transition-all active:scale-[0.98]">Generate Pattern</button>
          </div>
          <div className="lg:col-span-2 space-y-6">
            {error && <div className="bg-red-950/50 border border-red-800 rounded-xl p-4 text-red-300 text-sm">⚠️ {error}</div>}
            {!result ? (<div className="bg-gray-900 rounded-xl border border-gray-800 p-16 text-center"><div className="text-6xl mb-4 opacity-30">🧵</div><p className="text-gray-500 text-lg">Enter a DNA sequence and click Generate</p><p className="text-gray-600 text-sm mt-2">Patterns are generated client-side — no data leaves your browser</p></div>) : (<>
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
                <div className="flex items-center justify-between mb-4"><h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Preview</h2><div className="flex items-center gap-2"><label className="text-xs text-gray-500">Scale:</label><select value={previewSize} onChange={(e) => setPreviewSize(Number(e.target.value))} className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-gray-300"><option value={256}>256px</option><option value={512}>512px</option><option value={768}>768px</option></select></div></div>
                <div className="flex justify-center bg-gray-950 rounded-lg p-4"><canvas ref={canvasRef} width={previewSize} height={previewSize} className="rounded border border-gray-800" style={{ width: previewSize, height: previewSize, imageRendering: "pixelated" }} /></div>
              </div>
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
                <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">Comparison</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2"><h3 className="text-xs font-semibold text-gray-400 uppercase">Traditional Reference</h3><div className="bg-gray-950 rounded-lg p-2 flex items-center justify-center"><Image src={`/tribes/${community}-reference.svg`} alt={`${community} traditional pattern`} width={256} height={256} className="rounded border border-gray-800" /></div><p className="text-xs text-gray-500 text-center">Traditional {community} weaving pattern</p></div>
                  <div className="space-y-2"><h3 className="text-xs font-semibold text-gray-400 uppercase">DNA Generated</h3><div className="bg-gray-950 rounded-lg p-2 flex items-center justify-center"><ComparisonCanvas result={result} /></div><p className="text-xs text-gray-500 text-center">Generated from DNA sequence</p></div>
                </div>
              </div>
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
                <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">Costume Mockup</h2>
                <div className="flex justify-center">
                  <svg viewBox="0 0 400 510" width="260" height="333" className="rounded-lg">
                    <defs><clipPath id="garment-clip"><path d="M 100 50 L 150 20 L 250 20 L 300 50 L 320 150 L 300 450 L 100 450 L 80 150 Z"/></clipPath></defs>
                    <rect width="400" height="510" fill="#1a1a2e"/>
                    <g clipPath="url(#garment-clip)">{mockupDataUrl ? (<image href={mockupDataUrl} x="0" y="0" width="512" height="512" preserveAspectRatio="xMidYMid slice" style={{ imageRendering: "pixelated" }}/>) : (<rect x="0" y="0" width="400" height="510" fill="#2a2a3e"/>)}</g>
                    <path d="M 100 50 L 150 20 L 250 20 L 300 50 L 320 150 L 300 450 L 100 450 L 80 150 Z" fill="none" stroke="#444" strokeWidth="2"/>
                    <text x="200" y="495" textAnchor="middle" fill="#888" fontFamily="serif" fontSize="14">Costume Mockup</text>
                  </svg>
                </div>
                <p className="text-xs text-gray-500 text-center mt-3">Generated pattern applied to traditional garment silhouette</p>
              </div>
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
                <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">Sequence Stats</h2>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <StatCard label="Length" value={`${result.stats.length} bp`} /><StatCard label="GC Content" value={`${result.stats.gcContent}%`} />
                  <StatCard label="Unique Colors" value={String(result.stats.uniqueColors)} /><StatCard label="Dominant" value={result.stats.dominantColor} color={result.stats.dominantColor} />
                </div>
              </div>
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
                <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">Export</h2>
                <div className="flex flex-wrap gap-3">
                  <button onClick={handleDownloadPNG} className="px-5 py-2.5 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium transition-colors">⬇ Download PNG</button>
                  <button onClick={handleDownloadSVG} className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors">⬇ Download SVG</button>
                  <button onClick={handleCopyDataUrl} className="px-5 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors">📋 Copy Data URL</button>
                </div>
                <div className="text-xs text-gray-600 mt-3">PNG: {gridSize}×{gridSize}px • SVG: scalable vector • {community} palette • {patternType} pattern</div>
              </div>
            </>)}
          </div>
        </div>
      </main>
      <footer className="border-t border-gray-800 mt-12"><div className="max-w-7xl mx-auto px-4 py-6 text-center text-xs text-gray-600">DNA Textile Project • 15 Thai indigenous communities • 106 motifs • Client-side generation</div></footer>
    </div>
  );
}

function ComparisonCanvas({ result }: { result: PatternResult }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const SIZE = 256;
  if (canvasRef.current && result) { const ctx = canvasRef.current.getContext("2d"); if (ctx) { ctx.imageSmoothingEnabled = false; ctx.putImageData(result.imageData, 0, 0, 0, 0, result.gridSize, result.gridSize); for (let y = 0; y < SIZE; y += result.gridSize) for (let x = 0; x < SIZE; x += result.gridSize) { if (x === 0 && y === 0) continue; ctx.drawImage(canvasRef.current, 0, 0, result.gridSize, result.gridSize, x, y, result.gridSize, result.gridSize); } } }
  return <canvas ref={canvasRef} width={SIZE} height={SIZE} className="rounded border border-gray-800" style={{ width: SIZE, height: SIZE, imageRendering: "pixelated" }} />;
}

function StatCard({ label, value, color }: { label: string; value: string; color?: string }) {
  return (<div className="bg-gray-800 rounded-lg p-3"><div className="text-xs text-gray-500">{label}</div><div className="text-lg font-mono font-bold mt-0.5 flex items-center gap-2">{color && <span className="inline-block w-4 h-4 rounded border border-gray-600" style={{ backgroundColor: color }} />}{value}</div></div>);
}
