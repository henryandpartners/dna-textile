/**
 * DNA Textile Pattern Generator — ported from Python to TypeScript
 * Maps DNA nucleotides → color grids → textile patterns
 */

// ── Types ──────────────────────────────────────────────────

export type PatternType =
  | "stripe"
  | "grid"
  | "spiral"
  | "random"
  | "cellular_automata"
  | "lace"
  | "codon_tile"
  | "phase_shift"
  | "fractal_koch"
  | "voronoi"
  | "wave_interference"
  | "perlin_noise"
  | "l_system"
  | "fourier_pattern"
  | "diffusion"
  | "mosaic";
export type Community = "karen" | "hmong" | "akha" | "lahu" | "lisu" | "generic";
export type Complexity = "beginner" | "intermediate" | "expert";

export interface PatternConfig {
  sequence: string;
  gridSize: number;
  patternType: PatternType;
  community: Community;
  complexity: Complexity;
  seed?: number;
}

export interface PatternResult {
  imageData: ImageData;
  gridSize: number;
  stats: PatternStats;
}

export interface PatternStats {
  length: number;
  gcContent: number;
  uniqueColors: number;
  dominantColor: string;
  patternType: PatternType;
  community: string;
}

// ── DNA Parser ─────────────────────────────────────────────

const VALID_BASES = new Set(["A", "T", "G", "C"]);

export function parseDNA(raw: string): string {
  const seq = raw.replace(/\s+/g, "").toUpperCase();
  const invalid = new Set(seq.split("")).difference(VALID_BASES);
  if (invalid.size > 0) {
    throw new Error(
      `Invalid nucleotide(s): ${[...invalid].join(", ")}. Only A, T, G, C allowed.`
    );
  }
  return seq;
}

export function analyzeSequence(seq: string): PatternStats {
  const gc = seq.split("").filter((b) => b === "G" || b === "C").length;
  const gcContent = seq.length > 0 ? (gc / seq.length) * 100 : 0;

  // Count unique colors
  const colorMap = getDNAColormap();
  const uniqueColors = new Set(
    seq
      .split("")
      .map((b) => {
        const c = colorMap[b as keyof typeof colorMap] || [128, 128, 128];
        return c.join(",");
      })
  ).size;

  // Find dominant color
  const colorCounts: Record<string, number> = {};
  for (const base of seq) {
    const c = colorMap[base as keyof typeof colorMap] || [128, 128, 128];
    const key = c.join(",");
    colorCounts[key] = (colorCounts[key] || 0) + 1;
  }
  const dominant = Object.entries(colorCounts).sort((a, b) => b[1] - a[1])[0];
  const dominantRGB = dominant ? dominant[0].split(",").map(Number) : [0, 0, 0];
  const dominantColor = `#${dominantRGB[0].toString(16).padStart(2, "0")}${dominantRGB[1].toString(16).padStart(2, "0")}${dominantRGB[2].toString(16).padStart(2, "0")}`;

  return {
    length: seq.length,
    gcContent: Math.round(gcContent * 100) / 100,
    uniqueColors,
    dominantColor,
    patternType: "grid",
    community: "generic",
  };
}

// ── Color Palettes ─────────────────────────────────────────

const DNA_COLORS: Record<string, [number, number, number]> = {
  A: [255, 0, 0],
  T: [0, 0, 255],
  G: [0, 255, 0],
  C: [255, 255, 0],
};

function getDNAColormap(): Record<string, [number, number, number]> {
  return DNA_COLORS;
}

const NUC_VALUES: Record<string, number> = { A: 0.0, T: 0.333, G: 0.667, C: 1.0 };
const NUC_PHASE: Record<string, number> = { A: 0, T: Math.PI / 2, G: Math.PI, C: 3 * Math.PI / 2 };
const NUC_FREQ: Record<string, number> = { A: 1.0, T: 2.0, G: 3.0, C: 4.0 };

const COMMUNITY_PALETTES: Record<
  string,
  { primary: string[]; secondary: string[]; accent: string[] }
> = {
  karen: {
    primary: ["#8B0000", "#000000", "#FFFFFF"],
    secondary: ["#8B4513", "#D2691E", "#F5DEB3"],
    accent: ["#FFD700", "#C0C0C0"],
  },
  hmong: {
    primary: ["#000080", "#FFFFFF", "#008000"],
    secondary: ["#FF0000", "#FFD700", "#FF69B4"],
    accent: ["#00CED1", "#FF4500"],
  },
  akha: {
    primary: ["#000000", "#8B0000", "#C0C0C0"],
    secondary: ["#FF0000", "#FFD700", "#FFFFFF"],
    accent: ["#800080", "#006400"],
  },
  lahu: {
    primary: ["#8B0000", "#000000", "#FFFFFF"],
    secondary: ["#FF4500", "#C0C0C0", "#FFD700"],
    accent: ["#000080", "#800080"],
  },
  lisu: {
    primary: ["#FF0000", "#FF8C00", "#FFD700"],
    secondary: ["#008000", "#0000FF", "#800080"],
    accent: ["#FFFFFF", "#000000", "#FF69B4"],
  },
  generic: {
    primary: ["#FF0000", "#0000FF", "#00FF00"],
    secondary: ["#FFFF00", "#FF00FF", "#00FFFF"],
    accent: ["#FFFFFF", "#000000"],
  },
};

function hexToRgb(hex: string): [number, number, number] {
  const v = parseInt(hex.slice(1), 16);
  return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
}

function getCommunityColors(community: string): [number, number, number][] {
  const palette = COMMUNITY_PALETTES[community] || COMMUNITY_PALETTES.generic;
  return [
    ...palette.primary.map(hexToRgb),
    ...palette.secondary.map(hexToRgb),
    ...palette.accent.map(hexToRgb),
  ];
}

function findClosestPaletteColor(
  rgb: [number, number, number],
  palette: [number, number, number][]
): [number, number, number] {
  let minDist = Infinity;
  let closest = palette[0];
  for (const p of palette) {
    const d =
      (rgb[0] - p[0]) ** 2 + (rgb[1] - p[1]) ** 2 + (rgb[2] - p[2]) ** 2;
    if (d < minDist) {
      minDist = d;
      closest = p;
    }
  }
  return closest;
}

// ── Pattern Generation ─────────────────────────────────────

function tileSequence(seq: string, total: number): string[] {
  const repeats = Math.ceil(total / seq.length) + 1;
  const tiled = (seq.repeat(repeats) as string).slice(0, total);
  return tiled.split("");
}

function nucleotideToRgb(
  base: string
): [number, number, number] {
  return DNA_COLORS[base] || [128, 128, 128];
}

function createGrid(size: number): Uint8ClampedArray {
  return new Uint8ClampedArray(size * size * 4);
}

function setPixel(
  grid: Uint8ClampedArray,
  size: number,
  r: number,
  c: number,
  rgb: [number, number, number]
) {
  const idx = (r * size + c) * 4;
  grid[idx] = rgb[0];
  grid[idx + 1] = rgb[1];
  grid[idx + 2] = rgb[2];
  grid[idx + 3] = 255;
}

function patternStripe(
  tiled: string[],
  grid: Uint8ClampedArray,
  size: number
): void {
  let idx = 0;
  for (let r = 0; r < size; r++) {
    const rgb = nucleotideToRgb(tiled[idx]);
    for (let c = 0; c < size; c++) {
      setPixel(grid, size, r, c, rgb);
    }
    idx++;
  }
}

function patternGrid(
  tiled: string[],
  grid: Uint8ClampedArray,
  size: number
): void {
  let idx = 0;
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      setPixel(grid, size, r, c, nucleotideToRgb(tiled[idx]));
      idx++;
    }
  }
}

function patternSpiral(
  tiled: string[],
  grid: Uint8ClampedArray,
  size: number
): void {
  const coords: [number, number][] = [];
  let top = 0,
    bottom = size - 1,
    left = 0,
    right = size - 1;

  while (top <= bottom && left <= right) {
    for (let c = left; c <= right; c++) coords.push([top, c]);
    top++;
    for (let r = top; r <= bottom; r++) coords.push([r, right]);
    right--;
    if (top <= bottom) {
      for (let c = right; c >= left; c--) coords.push([bottom, c]);
      bottom--;
    }
    if (left <= right) {
      for (let r = bottom; r >= top; r--) coords.push([r, left]);
      left++;
    }
  }

  for (let i = 0; i < coords.length && i < tiled.length; i++) {
    setPixel(grid, size, coords[i][0], coords[i][1], nucleotideToRgb(tiled[i]));
  }
}

function patternRandom(
  tiled: string[],
  grid: Uint8ClampedArray,
  size: number,
  seed?: number
): void {
  const shuffled = [...tiled];
  // Seeded shuffle
  let s = seed || Date.now();
  function rand() {
    s = (s * 16807 + 0) % 2147483647;
    return s / 2147483647;
  }
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  let idx = 0;
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      setPixel(grid, size, r, c, nucleotideToRgb(shuffled[idx]));
      idx++;
    }
  }
}

// ── Advanced Patterns ─────────────────────────────────────

function patternCellularAutomata(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number,
  seed?: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  // Seed state from DNA values
  const state: number[][] = [];
  for (let r = 0; r < size; r++) {
    state[r] = [];
    for (let c = 0; c < size; c++) {
      const idx = (r * size + c) % seq.length;
      state[r][c] = NUC_VALUES[seq[idx]] > 0.5 ? 1 : 0;
    }
  }
  // Run CA for n generations
  for (let gen = 0; gen < size; gen++) {
    const newState: number[][] = [];
    for (let r = 0; r < size; r++) {
      newState[r] = [];
      for (let c = 0; c < size; c++) {
        let neighbors = 0;
        for (let dr = -1; dr <= 1; dr++) {
          for (let dc = -1; dc <= 1; dc++) {
            if (dr === 0 && dc === 0) continue;
            const nr = (r + dr + size) % size;
            const nc = (c + dc + size) % size;
            neighbors += state[nr][nc];
          }
        }
        if (state[r][c] === 1) {
          newState[r][c] = (neighbors === 2 || neighbors === 3) ? 1 : 0;
        } else {
          newState[r][c] = (neighbors === 3) ? 1 : 0;
        }
      }
    }
    // Render this generation as one row
    for (let c = 0; c < size; c++) {
      const idx = (gen * size + c) % seq.length;
      if (newState[gen % size][c] === 1) {
        setPixel(grid, size, gen, c, nucleotideToRgb(seq[idx]));
      } else {
        setPixel(grid, size, gen, c, [40, 40, 40]);
      }
    }
    for (let r = 0; r < size; r++) state[r] = [...newState[r]];
  }
}

function patternLace(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const holeThreshold = 0.6 + NUC_VALUES[seq[0]] * 0.2;
  const holeMap: boolean[][] = [];
  for (let r = 0; r < size; r++) {
    holeMap[r] = [];
    for (let c = 0; c < size; c++) {
      const idx = (r * size + c) % seq.length;
      holeMap[r][c] = NUC_VALUES[seq[idx]] > holeThreshold;
    }
  }
  // Validate: hole must be surrounded by non-holes
  const validated: boolean[][] = [];
  for (let r = 0; r < size; r++) {
    validated[r] = [];
    for (let c = 0; c < size; c++) {
      if (!holeMap[r][c]) { validated[r][c] = false; continue; }
      let safe = true;
      for (let dr = -1; dr <= 1 && safe; dr++) {
        for (let dc = -1; dc <= 1 && safe; dc++) {
          if (dr === 0 && dc === 0) continue;
          const nr = r + dr, nc = c + dc;
          if (nr >= 0 && nr < size && nc >= 0 && nc < size && holeMap[nr][nc]) safe = false;
        }
      }
      validated[r][c] = safe;
    }
  }
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (validated[r][c]) {
        setPixel(grid, size, r, c, [255, 255, 255]);
      } else {
        const idx = (r * size + c) % seq.length;
        const rgb = nucleotideToRgb(seq[idx]);
        setPixel(grid, size, r, c, [Math.round(rgb[0]*0.25), Math.round(rgb[1]*0.25), Math.round(rgb[2]*0.25)]);
      }
    }
  }
  // Grid lines
  const barSpacing = Math.max(4, Math.floor(size / 20));
  for (let r = 0; r < size; r += barSpacing)
    for (let c = 0; c < size; c++) setPixel(grid, size, r, c, [200, 200, 200]);
  for (let c = 0; c < size; c += barSpacing)
    for (let r = 0; r < size; r++) setPixel(grid, size, r, c, [200, 200, 200]);
}

function patternCodonTile(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  const codons: string[] = [];
  for (let i = 0; i < seq.length; i += 3) {
    let chunk = seq.substring(i, i + 3);
    while (chunk.length < 3) chunk += "A";
    codons.push(chunk);
  }
  const tileSize = 5;
  const tilesPerRow = Math.floor(size / tileSize);
  for (let row = 0; row < tilesPerRow; row++) {
    for (let col = 0; col < tilesPerRow; col++) {
      const idx = row * tilesPerRow + col;
      if (idx >= codons.length) break;
      const codon = codons[idx];
      const color = nucleotideToRgb(codon[0]);
      const pt = codon[1];
      const cx = Math.floor(tileSize / 2);
      for (let dy = 0; dy < tileSize; dy++) {
        for (let dx = 0; dx < tileSize; dx++) {
          let fill = false;
          if (pt === "A") fill = dy % 2 === 0;
          else if (pt === "T") fill = Math.abs(dy - cx) + Math.abs(dx - cx) <= cx;
          else if (pt === "G") fill = dy === cx || dx === cx;
          else fill = (dy - cx) ** 2 + (dx - cx) ** 2 <= (tileSize / 4) ** 2;
          if (fill) setPixel(grid, size, row * tileSize + dy, col * tileSize + dx, color);
        }
      }
    }
  }
}

function patternPhaseShift(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  // Detect homopolymer runs
  const runs: { base: string; start: number; length: number }[] = [];
  let currentBase = seq[0], runStart = 0;
  for (let i = 1; i < seq.length; i++) {
    if (seq[i] !== currentBase) {
      if (i - runStart >= 3) runs.push({ base: currentBase, start: runStart, length: i - runStart });
      currentBase = seq[i]; runStart = i;
    }
  }
  if (seq.length - runStart >= 3) runs.push({ base: currentBase, start: runStart, length: seq.length - runStart });
  const boundaries = [0];
  for (const run of runs) { boundaries.push(run.start); boundaries.push(run.start + run.length); }
  boundaries.push(seq.length);
  const sortedBoundaries = [...new Set(boundaries)].sort((a, b) => a - b);
  const phaseAlgos: PatternType[] = ["stripe", "spiral", "grid", "random"];
  // Render each phase
  for (let pi = 0; pi < phaseAlgos.length; pi++) {
    const tempGrid = createGrid(size);
    const tiled = tileSequence(seq, size * size);
    switch (phaseAlgos[pi]) {
      case "stripe": patternStripe(tiled, tempGrid, size); break;
      case "spiral": patternSpiral(tiled, tempGrid, size); break;
      case "grid": patternGrid(tiled, tempGrid, size); break;
      case "random": patternRandom(tiled, tempGrid, size); break;
    }
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        const seqPos = (r * size + c) % seq.length;
        let phase = 0;
        for (let i = 0; i < sortedBoundaries.length - 1; i++) {
          if (sortedBoundaries[i] <= seqPos && seqPos < sortedBoundaries[i + 1]) { phase = Math.floor(i / 2) % phaseAlgos.length; break; }
        }
        if (phase === pi) {
          const si = (r * size + c) * 4;
          grid[si] = tempGrid[si]; grid[si+1] = tempGrid[si+1]; grid[si+2] = tempGrid[si+2]; grid[si+3] = 255;
        }
      }
    }
  }
}

function patternFractalKoch(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const depthMap: Record<string, number> = { A: 1, T: 2, G: 3, C: 4 };
  const cx = size / 2, cy = size / 2;
  function kochCurve(x1: number, y1: number, x2: number, y2: number, depth: number): [number, number][] {
    if (depth === 0) return [[x1, y1]];
    const dx = (x2 - x1) / 3, dy = (y2 - y1) / 3;
    const p1: [number, number] = [x1 + dx, y1 + dy];
    const p2: [number, number] = [x1 + 2 * dx, y1 + 2 * dy];
    const midX = (x1 + x2) / 2, midY = (y1 + y2) / 2;
    const h = Math.sqrt(dx * dx + dy * dy) * Math.sqrt(3) / 2;
    const angle = Math.atan2(dy, dx) + Math.PI / 2;
    const peak: [number, number] = [midX + h * Math.cos(angle), midY + h * Math.sin(angle)];
    return [...kochCurve(x1, y1, p1[0], p1[1], depth-1), ...kochCurve(p1[0], p1[1], peak[0], peak[1], depth-1),
      ...kochCurve(peak[0], peak[1], p2[0], p2[1], depth-1), ...kochCurve(p2[0], p2[1], x2, y2, depth-1)];
  }
  const angles = [0, Math.PI/3, 2*Math.PI/3, Math.PI, 4*Math.PI/3, 5*Math.PI/3];
  for (let i = 0; i < angles.length; i++) {
    const base = seq[i % seq.length];
    const depth = depthMap[base] || 2;
    const color = nucleotideToRgb(base);
    const points = kochCurve(0, 0, size * 0.4, 0, depth);
    const cosA = Math.cos(angles[i]), sinA = Math.sin(angles[i]);
    for (const [x, y] of points) {
      const rx = cx + x * cosA - y * sinA, ry = cy + x * sinA + y * cosA;
      const px = Math.round(rx), py = Math.round(ry);
      for (let ddx = -1; ddx <= 1; ddx++) for (let ddy = -1; ddy <= 1; ddy++) setPixel(grid, size, py+ddy, px+ddx, color);
    }
  }
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    const dist = Math.sqrt((r - cy) ** 2 + (c - cx) ** 2);
    if (dist < size * 0.15) setPixel(grid, size, r, c, nucleotideToRgb(seq[Math.floor(dist * seq.length / (size * 0.15)) % seq.length]));
  }
}

function patternVoronoi(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number,
  seed?: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const numSeeds = Math.max(8, Math.floor(seq.length / 3));
  let s = seed || 42;
  function rand() { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }
  interface Seed { x: number; y: number; base: string }
  const seeds: Seed[] = [];
  for (let i = 0; i < numSeeds; i++) {
    const base = seq[i % seq.length];
    const x = Math.max(0, Math.min(size - 1, NUC_VALUES[seq[i % seq.length]] * (size - 20) + 10 + (rand() - 0.5) * 20));
    const y = Math.max(0, Math.min(size - 1, NUC_VALUES[seq[(i+1) % seq.length]] * (size - 20) + 10 + (rand() - 0.5) * 20));
    seeds.push({ x, y, base });
  }
  const labels: number[][] = [];
  const minDist: number[][] = [];
  for (let r = 0; r < size; r++) { labels[r] = new Array(size).fill(0); minDist[r] = new Array(size).fill(Infinity); }
  for (let idx = 0; idx < seeds.length; idx++) {
    const sx = seeds[idx].x, sy = seeds[idx].y;
    for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
      const dist = (r - sy) ** 2 + (c - sx) ** 2;
      if (dist < minDist[r][c]) { minDist[r][c] = dist; labels[r][c] = idx; }
    }
  }
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    setPixel(grid, size, r, c, nucleotideToRgb(seeds[labels[r][c]].base));
  }
  // Draw edges
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    const l = labels[r][c];
    if ((c + 1 < size && labels[r][c+1] !== l) || (r + 1 < size && labels[r+1][c] !== l)) setPixel(grid, size, r, c, [255, 255, 255]);
  }
}

function patternWaveInterference(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const wave = new Float64Array(size * size);
  for (let i = 0; i < Math.min(seq.length, 20); i++) {
    const base = seq[i];
    const k = NUC_FREQ[base] * (1 + i * 0.3);
    const phi = NUC_PHASE[base] + i * 0.5;
    const angle = (i / seq.length) * Math.PI * 2;
    const cosA = Math.cos(angle), sinA = Math.sin(angle);
    for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
      wave[r * size + c] += Math.sin(k * (c / size * cosA + r / size * sinA) + phi);
    }
  }
  let wMin = Infinity, wMax = -Infinity;
  for (let i = 0; i < wave.length; i++) { if (wave[i] < wMin) wMin = wave[i]; if (wave[i] > wMax) wMax = wave[i]; }
  const range = wMax - wMin || 1;
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    const val = (wave[r * size + c] - wMin) / range;
    setPixel(grid, size, r, c, nucleotideToRgb(seq[Math.floor(val * (seq.length - 1)) % seq.length]));
  }
}

function patternPerlinNoise(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number,
  seed?: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const gradSize = Math.max(4, Math.floor(size / 8));
  let s = seed || 42;
  function rand() { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }
  const grads: [number, number][][] = [];
  for (let i = 0; i <= gradSize; i++) {
    grads[i] = [];
    for (let j = 0; j <= gradSize; j++) {
      const base = seq[(i * (gradSize + 1) + j) % seq.length];
      const angle = NUC_VALUES[base] * 2 * Math.PI + (rand() - 0.5) * 0.6;
      grads[i][j] = [Math.cos(angle), Math.sin(angle)];
    }
  }
  function smoothstep(t: number): number { return t * t * (3 - 2 * t); }
  const noise = new Float64Array(size * size);
  const scale = gradSize / size;
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    let fx = c * scale, fy = r * scale;
    let ix = Math.min(Math.floor(fx), gradSize - 1), iy = Math.min(Math.floor(fy), gradSize - 1);
    let dx = fx - ix, dy = fy - iy;
    dx = smoothstep(dx); dy = smoothstep(dy);
    const g00 = grads[iy][ix], g10 = grads[iy][ix + 1], g01 = grads[iy + 1][ix], g11 = grads[iy + 1][ix + 1];
    const d00 = dx * g00[0] + dy * g00[1], d10 = (dx - 1) * g10[0] + dy * g10[1];
    const d01 = dx * g01[0] + (dy - 1) * g01[1], d11 = (dx - 1) * g11[0] + (dy - 1) * g11[1];
    noise[r * size + c] = d00 + dx * (d10 - d00) + dy * (d01 + dx * (d11 - d01) - (d00 + dx * (d10 - d00)));
  }
  let nMin = Infinity, nMax = -Infinity;
  for (let i = 0; i < noise.length; i++) { if (noise[i] < nMin) nMin = noise[i]; if (noise[i] > nMax) nMax = noise[i]; }
  const range = nMax - nMin || 1;
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    const val = (noise[r * size + c] - nMin) / range;
    setPixel(grid, size, r, c, nucleotideToRgb(seq[Math.floor(val * (seq.length - 1)) % seq.length]));
  }
}

function patternLSystem(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const rules: Record<string, string> = {};
  const bases = [...new Set(seq.split(""))];
  for (let i = 0; i < bases.length; i++) rules[bases[i]] = bases[i] + seq[(i + 1) % seq.length];
  let current = seq[0];
  const iterations = Math.min(Math.floor(seq.length / 5) + 1, 6);
  for (let iter = 0; iter < iterations; iter++) {
    let next = "";
    for (const sym of current) next += rules[sym] || sym;
    current = next;
    if (current.length > size * size * 2) break;
  }
  const canvas = new Int32Array(size * size);
  let x = Math.floor(size / 2), y = Math.floor(size / 2);
  let angle = -Math.PI / 2;
  const step = Math.max(1, Math.floor(size / (iterations * 4 + 4)));
  const turnAngle = Math.PI / 3;
  for (let i = 0; i < Math.min(current.length, size * size); i++) {
    const sym = current[i];
    if (sym in rules) angle += NUC_VALUES[sym] < 0.5 ? -turnAngle : turnAngle;
    else if (sym === seq[0]) {
      const nx = Math.round(x + step * Math.cos(angle)), ny = Math.round(y + step * Math.sin(angle));
      if (nx >= 0 && nx < size && ny >= 0 && ny < size) canvas[ny * size + nx]++;
      x = nx; y = ny;
    }
  }
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    if (canvas[r * size + c] > 0) setPixel(grid, size, r, c, nucleotideToRgb(seq[canvas[r * size + c] % seq.length]));
  }
}

function patternFourier(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const pattern = new Float64Array(size * size);
  const terms = Math.min(seq.length, 20);
  for (let i = 0; i < terms; i++) {
    const base = seq[i];
    const u = (i % 8) + 1, v = Math.floor(i / 8) + 1;
    const amp = NUC_VALUES[base], phase = NUC_PHASE[base];
    for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
      pattern[r * size + c] += amp * Math.sin(2 * Math.PI * (u * c / size + v * r / size) + phase);
    }
  }
  let pMin = Infinity, pMax = -Infinity;
  for (let i = 0; i < pattern.length; i++) { if (pattern[i] < pMin) pMin = pattern[i]; if (pattern[i] > pMax) pMax = pattern[i]; }
  const range = pMax - pMin || 1;
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    const val = (pattern[r * size + c] - pMin) / range;
    setPixel(grid, size, r, c, nucleotideToRgb(seq[Math.floor(val * (seq.length - 1)) % seq.length]));
  }
}

function patternDiffusion(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  const f = 0.02 + NUC_VALUES[seq[0]] * 0.08;
  const k = 0.04 + NUC_VALUES[seq[1 % seq.length]] * 0.06;
  const du = 1.0, dv = 0.5;
  const iterations = 50 + Math.floor(NUC_VALUES[seq[0]] * 50);
  const u = new Float64Array(size * size).fill(1);
  const v = new Float64Array(size * size).fill(0);
  const center = Math.floor(size / 2);
  const radius = Math.max(3, Math.floor(size / 15));
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    if ((c - center) ** 2 + (r - center) ** 2 <= radius ** 2) v[r * size + c] = 1;
  }
  const lapW = [0.05, 0.2, 0.05, 0.2, -1.0, 0.2, 0.05, 0.2, 0.05];
  const offsets = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];
  for (let iter = 0; iter < iterations; iter++) {
    const uNew = new Float64Array(size * size);
    const vNew = new Float64Array(size * size);
    for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
      const idx = r * size + c;
      let uLap = 0, vLap = 0;
      for (let i = 0; i < 8; i++) {
        const nr = (r + offsets[i][0] + size) % size, nc = (c + offsets[i][1] + size) % size;
        const ni = nr * size + nc;
        uLap += lapW[i] * u[ni]; vLap += lapW[i] * v[ni];
      }
      uLap += lapW[4] * u[idx]; vLap += lapW[4] * v[idx];
      const uv2 = u[idx] * v[idx] * v[idx];
      uNew[idx] = Math.max(0, Math.min(1, u[idx] + (du * uLap - uv2 + f * (1 - u[idx]))));
      vNew[idx] = Math.max(0, Math.min(1, v[idx] + (dv * vLap + uv2 - (f + k) * v[idx])));
    }
    for (let i = 0; i < u.length; i++) { u[i] = uNew[i]; v[i] = vNew[i]; }
  }
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    const val = v[r * size + c];
    setPixel(grid, size, r, c, nucleotideToRgb(seq[Math.floor(val * (seq.length - 1)) % seq.length]));
  }
}

function patternMosaic(
  sequence: string,
  grid: Uint8ClampedArray,
  size: number,
  seed?: number
): void {
  const seq = sequence.toUpperCase();
  if (!seq.length) return;
  let s = seed || 42;
  function rand() { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }
  const hexSize = Math.max(8, Math.floor(size / 10));
  const rows = Math.floor(size / (hexSize * 1.5)) + 2;
  const cols = Math.floor(size / (hexSize * Math.sqrt(3))) + 2;
  interface Center { x: number; y: number; base: string }
  const centers: Center[] = [];
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const baseX = c * hexSize * Math.sqrt(3), baseY = r * hexSize * 1.5;
    const seqIdx = (r * cols + c) % seq.length;
    const base = seq[seqIdx];
    const dx = (NUC_VALUES[base] - 0.5) * hexSize * 0.5 + (rand() - 0.5) * 6;
    const dy = (NUC_VALUES[seq[(seqIdx + 1) % seq.length]] - 0.5) * hexSize * 0.5 + (rand() - 0.5) * 6;
    centers.push({ x: baseX + dx, y: baseY + dy, base });
  }
  const nearestIdx = new Int32Array(size * size);
  const minDist = new Float64Array(size * size).fill(Infinity);
  for (let idx = 0; idx < centers.length; idx++) {
    const cx = centers[idx].x, cy = centers[idx].y;
    for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
      const dist = (r - cy) ** 2 + (c - cx) ** 2;
      const pi = r * size + c;
      if (dist < minDist[pi]) { minDist[pi] = dist; nearestIdx[pi] = idx; }
    }
  }
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    setPixel(grid, size, r, c, nucleotideToRgb(centers[nearestIdx[r * size + c]].base));
  }
  for (let r = 0; r < size; r++) for (let c = 0; c < size; c++) {
    const l = nearestIdx[r * size + c];
    if ((c + 1 < size && nearestIdx[r * size + c + 1] !== l) || (r + 1 < size && nearestIdx[(r + 1) * size + c] !== l)) setPixel(grid, size, r, c, [64, 64, 64]);
  }
  for (let idx = 0; idx < centers.length; idx++) {
    const { x: cx, y: cy, base } = centers[idx];
    for (let r = 0; r < size; r += 4) for (let c = 0; c < size; c += 4) {
      if (nearestIdx[r * size + c] !== idx) continue;
      if (base === "A" && (r - cy) ** 2 + (c - cx) ** 2 < 9) setPixel(grid, size, r, c, [255, 255, 255]);
      else if (base === "T" && r % 4 === 0) setPixel(grid, size, r, c, [255, 255, 255]);
      else if (base === "G" && c % 4 === 0) setPixel(grid, size, r, c, [255, 255, 255]);
      else if (base === "C" && (r % 6 === 0 || c % 6 === 0)) setPixel(grid, size, r, c, [255, 255, 255]);
    }
  }
}

// ── Border Drawing ─────────────────────────────────────────

const BORDER_COLORS: Record<string, [number, number, number]> = {
  karen: [139, 69, 19],
  hmong: [255, 255, 255],
  akha: [192, 192, 192],
  lahu: [139, 0, 0],
  lisu: [255, 0, 0],
  generic: [0, 0, 0],
};

function drawBorder(
  grid: Uint8ClampedArray,
  size: number,
  community: string
): void {
  const color = BORDER_COLORS[community] || BORDER_COLORS.generic;
  const bw = Math.min(4, Math.floor(size / 25));
  if (bw <= 0) return;

  for (let i = 0; i < size; i++) {
    for (let b = 0; b < bw; b++) {
      // Top
      setPixel(grid, size, b, i, color);
      // Bottom
      setPixel(grid, size, size - 1 - b, i, color);
      // Left
      setPixel(grid, size, i, b, color);
      // Right
      setPixel(grid, size, i, size - 1 - b, color);
    }
  }
}

// ── Main Generator ─────────────────────────────────────────

export function generatePattern(config: PatternConfig): PatternResult {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { sequence, gridSize, patternType, community, complexity, seed } =
    config;
  const total = gridSize * gridSize;
  const tiled = tileSequence(sequence, total);
  const grid = createGrid(gridSize);

  // Generate base pattern
  switch (patternType) {
    case "stripe": patternStripe(tiled, grid, gridSize); break;
    case "grid": patternGrid(tiled, grid, gridSize); break;
    case "spiral": patternSpiral(tiled, grid, gridSize); break;
    case "random": patternRandom(tiled, grid, gridSize, seed); break;
    case "cellular_automata": patternCellularAutomata(sequence, grid, gridSize, seed); break;
    case "lace": patternLace(sequence, grid, gridSize); break;
    case "codon_tile": patternCodonTile(sequence, grid, gridSize); break;
    case "phase_shift": patternPhaseShift(sequence, grid, gridSize); break;
    case "fractal_koch": patternFractalKoch(sequence, grid, gridSize); break;
    case "voronoi": patternVoronoi(sequence, grid, gridSize, seed); break;
    case "wave_interference": patternWaveInterference(sequence, grid, gridSize); break;
    case "perlin_noise": patternPerlinNoise(sequence, grid, gridSize, seed); break;
    case "l_system": patternLSystem(sequence, grid, gridSize); break;
    case "fourier_pattern": patternFourier(sequence, grid, gridSize); break;
    case "diffusion": patternDiffusion(sequence, grid, gridSize); break;
    case "mosaic": patternMosaic(sequence, grid, gridSize, seed); break;
  }

  // Apply community palette (limit to traditional colors)
  const palette = getCommunityColors(community);
  for (let i = 0; i < grid.length; i += 4) {
    const rgb: [number, number, number] = [grid[i], grid[i + 1], grid[i + 2]];
    const closest = findClosestPaletteColor(rgb, palette);
    grid[i] = closest[0];
    grid[i + 1] = closest[1];
    grid[i + 2] = closest[2];
  }

  // Draw border
  drawBorder(grid, gridSize, community);

  // Create ImageData
  const imageData = new ImageData(
    grid as unknown as Uint8ClampedArray<ArrayBuffer>,
    gridSize,
    gridSize
  );

  // Compute stats
  const stats = analyzeSequence(sequence);
  stats.patternType = patternType;
  stats.community = community;

  return { imageData, gridSize, stats };
}

// ── Export ─────────────────────────────────────────────────

export function imageDataToPNG(imageData: ImageData): string {
  const canvas = document.createElement("canvas");
  canvas.width = imageData.width;
  canvas.height = imageData.height;
  const ctx = canvas.getContext("2d")!;
  ctx.putImageData(imageData, 0, 0);
  return canvas.toDataURL("image/png");
}

export function downloadPNG(imageData: ImageData, filename: string): void {
  const dataUrl = imageDataToPNG(imageData);
  const link = document.createElement("a");
  link.href = dataUrl;
  link.download = filename;
  link.click();
}

export function imageDataToDataURL(imageData: ImageData): string {
  const canvas = document.createElement("canvas");
  canvas.width = imageData.width;
  canvas.height = imageData.height;
  const ctx = canvas.getContext("2d")!;
  ctx.putImageData(imageData, 0, 0);
  return canvas.toDataURL("image/png");
}
