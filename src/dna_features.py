"""DNA Feature Extraction — computes sequence statistics that drive pattern decisions.

Phase 3: Extracts GC content, k-mer frequencies, palindromes, homopolymers,
repeats, codons, and Shannon entropy from a cleaned DNA sequence.

All functions operate on uppercase ATGC-only strings.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Dict, List, Tuple


# ── GC Content ─────────────────────────────────────────────

def gc_content(sequence: str) -> float:
    """Overall GC percentage (0.0–1.0)."""
    if not sequence:
        return 0.0
    gc = sum(1 for b in sequence if b in "GC")
    return gc / len(sequence)


def gc_sliding_window(
    sequence: str,
    window_size: int = 50,
    step: int = 25,
) -> List[Dict[str, Any]]:
    """GC content in sliding windows.

    Returns list of dicts with 'start', 'end', 'gc' keys.
    """
    results: List[Dict[str, Any]] = []
    for i in range(0, len(sequence) - window_size + 1, step):
        window = sequence[i : i + window_size]
        gc = sum(1 for b in window if b in "GC") / len(window)
        results.append({"start": i, "end": i + window_size, "gc": gc})
    return results


# ── K-mer Frequencies ──────────────────────────────────────

def kmer_counts(sequence: str, k: int = 3) -> Dict[str, int]:
    """Count all k-mers in the sequence."""
    if len(sequence) < k:
        return {}
    counter: Counter = Counter()
    for i in range(len(sequence) - k + 1):
        counter[sequence[i : i + k]] += 1
    return dict(counter)


def kmer_frequencies(sequence: str, k: int = 3) -> Dict[str, float]:
    """Normalized k-mer frequencies (sum to 1.0)."""
    counts = kmer_counts(sequence, k)
    total = sum(counts.values())
    if total == 0:
        return {}
    return {km: c / total for km, c in counts.items()}


def dominant_kmers(sequence: str, k: int = 3, top_n: int = 5) -> List[Tuple[str, int]]:
    """Return the top-N most frequent k-mers."""
    counts = kmer_counts(sequence, k)
    return sorted(counts.items(), key=lambda x: -x[1])[:top_n]


# ── Palindromes ────────────────────────────────────────────

_COMPLEMENT = str.maketrans("ATGC", "TACG")


def _reverse_complement(seq: str) -> str:
    return seq.translate(_COMPLEMENT)[::-1]


def find_palindromes(sequence: str, min_len: int = 4) -> List[Dict[str, Any]]:
    """Find DNA palindromic sequences (equal to their reverse complement).

    Returns list of dicts with 'sequence', 'start', 'length'.
    """
    results: List[Dict[str, Any]] = []
    for length in range(min_len, len(sequence) + 1, 2):
        for i in range(len(sequence) - length + 1):
            sub = sequence[i : i + length]
            if sub == _reverse_complement(sub):
                results.append({"sequence": sub, "start": i, "length": length})
    # Keep only maximal palindromes (no palindrome is substring of another)
    maximal = []
    for p in results:
        if not any(
            o["start"] <= p["start"] and o["start"] + o["length"] >= p["start"] + p["length"]
            and o["length"] > p["length"]
            for o in results
        ):
            maximal.append(p)
    return maximal


# ── Homopolymers ───────────────────────────────────────────

def find_homopolymers(sequence: str, min_run: int = 3) -> List[Dict[str, Any]]:
    """Find runs of the same base (e.g. AAAAA).

    Returns list of dicts with 'base', 'start', 'length'.
    """
    results: List[Dict[str, Any]] = []
    if not sequence:
        return results
    current_base = sequence[0]
    run_start = 0
    for i in range(1, len(sequence)):
        if sequence[i] != current_base:
            run_len = i - run_start
            if run_len >= min_run:
                results.append({"base": current_base, "start": run_start, "length": run_len})
            current_base = sequence[i]
            run_start = i
    # Last run
    run_len = len(sequence) - run_start
    if run_len >= min_run:
        results.append({"base": current_base, "start": run_start, "length": run_len})
    return results


def homopolymer_stats(sequence: str) -> Dict[str, Any]:
    """Summary statistics about homopolymer runs."""
    runs = find_homopolymers(sequence, min_run=2)
    if not runs:
        return {"total_runs": 0, "max_length": 0, "by_base": {}}
    by_base: Dict[str, List[int]] = {}
    for r in runs:
        by_base.setdefault(r["base"], []).append(r["length"])
    return {
        "total_runs": len(runs),
        "max_length": max(r["length"] for r in runs),
        "by_base": {b: {"count": len(lengths), "max_length": max(lengths)} for b, lengths in by_base.items()},
    }


# ── Repeats ────────────────────────────────────────────────

def find_tandem_repeats(sequence: str, min_unit: int = 2, max_unit: int = 6, min_copies: int = 2) -> List[Dict[str, Any]]:
    """Find tandem repeats (e.g. ATATAT = AT repeated 3 times).

    Returns list of dicts with 'unit', 'copies', 'start', 'length'.
    """
    results: List[Dict[str, Any]] = []
    for unit_len in range(min_unit, min(max_unit + 1, len(sequence) // 2 + 1)):
        i = 0
        while i <= len(sequence) - unit_len * min_copies:
            unit = sequence[i : i + unit_len]
            copies = 0
            j = i
            while j + unit_len <= len(sequence) and sequence[j : j + unit_len] == unit:
                copies += 1
                j += unit_len
            if copies >= min_copies:
                results.append({"unit": unit, "copies": copies, "start": i, "length": copies * unit_len})
                i = j  # skip past this repeat
            else:
                i += 1
    return results


def microsatellites(sequence: str, min_copies: int = 4) -> List[Dict[str, Any]]:
    """Find microsatellites (short tandem repeats, 1–6 bp units)."""
    return find_tandem_repeats(sequence, min_unit=1, max_unit=6, min_copies=min_copies)


# ── Codons ─────────────────────────────────────────────────

def codon_analysis(sequence: str, reading_frame: int = 0) -> Dict[str, Any]:
    """Analyze codons in a given reading frame (0, 1, or 2).

    Returns dict with 'frame', 'codons' (Counter-like dict), 'total_codons',
    'stop_codons', 'start_codons'.
    """
    frame = reading_frame % 3
    codons = sequence[frame:]
    codon_counts: Counter = Counter()
    stop_codons = 0
    start_codons = 0
    for i in range(0, len(codons) - 2, 3):
        c = codons[i : i + 3]
        if len(c) == 3:
            codon_counts[c] += 1
            if c in ("TAA", "TAG", "TGA"):
                stop_codons += 1
            if c == "ATG":
                start_codons += 1
    return {
        "frame": frame,
        "codons": dict(codon_counts),
        "total_codons": sum(codon_counts.values()),
        "stop_codons": stop_codons,
        "start_codons": start_codons,
    }


# ── Shannon Entropy ────────────────────────────────────────

def shannon_entropy(sequence: str) -> float:
    """Shannon entropy of the sequence (bits per symbol).

    Maximum for DNA is 2.0 (equal distribution of 4 bases).
    """
    if not sequence:
        return 0.0
    counter = Counter(sequence)
    length = len(sequence)
    entropy = 0.0
    for count in counter.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def entropy_sliding_window(
    sequence: str,
    window_size: int = 50,
    step: int = 25,
) -> List[Dict[str, Any]]:
    """Shannon entropy in sliding windows."""
    results: List[Dict[str, Any]] = []
    for i in range(0, len(sequence) - window_size + 1, step):
        window = sequence[i : i + window_size]
        ent = shannon_entropy(window)
        results.append({"start": i, "end": i + window_size, "entropy": ent})
    return results


# ── Base Composition ──────────────────────────────────────

def base_composition(sequence: str) -> Dict[str, float]:
    """Fraction of each base in the sequence."""
    if not sequence:
        return {"A": 0.0, "T": 0.0, "G": 0.0, "C": 0.0}
    counter = Counter(sequence)
    length = len(sequence)
    return {b: counter.get(b, 0) / length for b in "ATGC"}


# ── Master Feature Extraction ──────────────────────────────

def extract_features(
    sequence: str,
    kmer_sizes: Tuple[int, ...] = (3, 4),
    gc_window: int = 50,
    gc_step: int = 25,
) -> Dict[str, Any]:
    """Extract ALL DNA features into a single structured dict.

    This is the main entry point for the pipeline.

    Args:
        sequence: Cleaned DNA string (uppercase ATGC).
        kmer_sizes: Which k-mer sizes to compute.
        gc_window: Window size for sliding GC.
        gc_step: Step size for sliding GC.

    Returns:
        Dict with keys: length, gc_content, base_composition,
        kmer_frequencies, palindromes, homopolymers, homopolymer_stats,
        tandem_repeats, microsatellites, codons, shannon_entropy,
        gc_sliding_window, entropy_sliding_window.
    """
    features: Dict[str, Any] = {
        "length": len(sequence),
        "gc_content": gc_content(sequence),
        "base_composition": base_composition(sequence),
        "shannon_entropy": shannon_entropy(sequence),
    }

    # K-mers
    kmers: Dict[str, Dict[str, float]] = {}
    for k in kmer_sizes:
        if len(sequence) >= k:
            kmers[f"{k}mers"] = kmer_frequencies(sequence, k)
    features["kmer_frequencies"] = kmers

    # Palindromes (limit for long sequences)
    pal_limit = 20 if len(sequence) > 500 else 50
    pals = find_palindromes(sequence, min_len=4)
    features["palindromes"] = pals[:pal_limit]
    features["palindrome_count"] = len(pals)

    # Homopolymers
    features["homopolymers"] = find_homopolymers(sequence, min_run=3)
    features["homopolymer_stats"] = homopolymer_stats(sequence)

    # Repeats (limit for long sequences)
    repeats = find_tandem_repeats(sequence, min_unit=2, max_unit=6, min_copies=2)
    features["tandem_repeats"] = repeats[:30]
    features["repeat_count"] = len(repeats)

    micros = microsatellites(sequence, min_copies=4)
    features["microsatellites"] = micros[:20]

    # Codons (frame 0)
    features["codons"] = codon_analysis(sequence, reading_frame=0)

    # Sliding windows
    if len(sequence) >= gc_window:
        features["gc_sliding_window"] = gc_sliding_window(sequence, gc_window, gc_step)
        features["entropy_sliding_window"] = entropy_sliding_window(sequence, gc_window, gc_step)
    else:
        features["gc_sliding_window"] = []
        features["entropy_sliding_window"] = []

    return features


def select_dna_base(features: Dict[str, Any]) -> str:
    """Pick a 'dominant' base from features for motif/symbol selection.

    Uses base composition, ties broken by GC content.
    """
    bc = features.get("base_composition", {})
    if not bc:
        return "A"
    return max(bc, key=lambda b: bc[b])


def entropy_to_complexity(entropy: float) -> str:
    """Map Shannon entropy to a complexity level string."""
    if entropy >= 1.8:
        return "expert"
    elif entropy >= 1.4:
        return "intermediate"
    else:
        return "beginner"


def gc_to_color_index(gc: float, palette_size: int = 8) -> int:
    """Map GC content (0–1) to a palette color index."""
    return min(int(gc * palette_size), palette_size - 1)
