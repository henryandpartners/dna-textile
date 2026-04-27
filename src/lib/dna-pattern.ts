/**
 * DNA Textile Pattern Generator — ported from Python to TypeScript
 * Maps DNA nucleotides → color grids → textile patterns
 */

// ── Types ──────────────────────────────────────────────────

export type PatternType = "stripe" | "grid" | "spiral" | "random";
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
  const { sequence, gridSize, patternType, community, complexity, seed } =
    config;
  const total = gridSize * gridSize;
  const tiled = tileSequence(sequence, total);
  const grid = createGrid(gridSize);

  // Generate base pattern
  switch (patternType) {
    case "stripe":
      patternStripe(tiled, grid, gridSize);
      break;
    case "grid":
      patternGrid(tiled, grid, gridSize);
      break;
    case "spiral":
      patternSpiral(tiled, grid, gridSize);
      break;
    case "random":
      patternRandom(tiled, grid, gridSize, seed);
      break;
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
