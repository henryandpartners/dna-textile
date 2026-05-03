"""
DNA Feature Extractor — extracts semantic features from DNA sequences
to drive multi-layer pattern generation.

Phase 3: Replaces single-base→RGB mapping with rich feature extraction.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DNAFeatures:
    """All extracted features from a DNA sequence."""
    sequence: str
    length: int

    # ── Composition ──────────────────────────────────────
    base_counts: Dict[str, int] = field(default_factory=dict)
    base_frequencies: Dict[str, float] = field(default_factory=dict)
    gc_content: float = 0.0
    at_content: float = 0.0

    # ── k-mer analysis ───────────────────────────────────
    di_nucleotides: Dict[str, int] = field(default_factory=dict)
    tri_nucleotides: Dict[str, int] = field(default_factory=dict)
    tetra_nucleotides: Dict[str, int] = field(default_factory=dict)
    dominant_dinuc: str = ""
    dominant_trinuc: str = ""
    dominant_tetra: str = ""

    # ── Structural patterns ──────────────────────────────
    homopolymer_runs: List[Tuple[str, int, int]] = field(default_factory=list)  # (base, start, length)
    palindromes: List[Tuple[str, int, int]] = field(default_factory=list)  # (seq, start, length)
    repeats: List[Tuple[str, int, int]] = field(default_factory=list)  # (motif, start, repeat_count)

    # ── Codon table (triplet reading frame) ──────────────
    codons: List[str] = field(default_factory=list)
    codon_frequencies: Dict[str, int] = field(default_factory=dict)

    # ── Derived pattern parameters ───────────────────────
    complexity_score: float = 0.0  # 0-1, drives color count & motif density
    symmetry_score: float = 0.0    # 0-1, drives symmetry preference
    rhythm_score: float = 0.0      # 0-1, drives repeat density vs randomness
    entropy: float = 0.0           # Shannon entropy of base distribution


def extract_features(sequence: str) -> DNAFeatures:
    """Extract all features from a cleaned DNA sequence."""
    seq = sequence.upper()
    length = len(seq)

    features = DNAFeatures(sequence=seq, length=length)

    # ── Base composition ─────────────────────────────────
    counts = Counter(seq)
    features.base_counts = {b: counts.get(b, 0) for b in "ATGC"}
    features.base_frequencies = {b: c / max(length, 1) for b, c in features.base_counts.items()}
    features.gc_content = (features.base_counts["G"] + features.base_counts["C"]) / max(length, 1)
    features.at_content = (features.base_counts["A"] + features.base_counts["T"]) / max(length, 1)

    # ── k-mer frequencies ────────────────────────────────
    features.di_nucleotides = _count_kmers(seq, 2)
    features.tri_nucleotides = _count_kmers(seq, 3)
    features.tetra_nucleotides = _count_kmers(seq, 4)

    if features.di_nucleotides:
        features.dominant_dinuc = max(features.di_nucleotides, key=features.di_nucleotides.get)
    if features.tri_nucleotides:
        features.dominant_trinuc = max(features.tri_nucleotides, key=features.tri_nucleotides.get)
    if features.tetra_nucleotides:
        features.dominant_tetra = max(features.tetra_nucleotides, key=features.tetra_nucleotides.get)

    # ── Homopolymer runs ─────────────────────────────────
    features.homopolymer_runs = _find_homopolymers(seq)

    # ── Palindromes ──────────────────────────────────────
    features.palindromes = _find_palindromes(seq)

    # ── Tandem repeats ───────────────────────────────────
    features.repeats = _find_repeats(seq)

    # ── Codons (reading frame 1) ─────────────────────────
    features.codons = [seq[i:i+3] for i in range(0, length - 2, 3)]
    features.codon_frequencies = dict(Counter(features.codons))

    # ── Shannon entropy ──────────────────────────────────
    freqs = [f for f in features.base_frequencies.values() if f > 0]
    features.entropy = -sum(f * math.log2(f) for f in freqs)

    # ── Derived scores ───────────────────────────────────
    # Complexity: higher when more diverse k-mers, moderate GC
    kmer_diversity = len(features.tri_nucleotides) / max(len(features.codons), 1)
    gc_balance = 1.0 - abs(features.gc_content - 0.5) * 2  # peaks at 50% GC
    features.complexity_score = min(1.0, (kmer_diversity * 0.6 + gc_balance * 0.4))

    # Symmetry: higher with more palindromes and balanced composition
    palindrome_density = len(features.palindromes) / max(length / 10, 1)
    composition_balance = 1.0 - max(features.base_frequencies.values()) + min(features.base_frequencies.values())
    features.symmetry_score = min(1.0, (palindrome_density * 0.5 + composition_balance * 0.5))

    # Rhythm: higher with more homopolymers and repeats (structured)
    homopolymer_fraction = sum(l for _, _, l in features.homopolymer_runs) / max(length, 1)
    repeat_fraction = sum(rc * len(m) for m, _, rc in features.repeats) / max(length, 1)
    features.rhythm_score = min(1.0, homopolymer_fraction * 0.5 + repeat_fraction * 0.5)

    return features


def _count_kmers(sequence: str, k: int) -> Dict[str, int]:
    """Count all k-mers in a sequence."""
    return dict(Counter(sequence[i:i+k] for i in range(len(sequence) - k + 1)))


def _find_homopolymers(sequence: str, min_length: int = 3) -> List[Tuple[str, int, int]]:
    """Find runs of the same nucleotide."""
    runs = []
    for base in "ATGC":
        pattern = re.compile(rf"{base}{{{min_length},}}")
        for match in pattern.finditer(sequence):
            runs.append((base, match.start(), len(match.group())))
    return sorted(runs, key=lambda x: -x[2])


def _find_palindromes(sequence: str, min_length: int = 4) -> List[Tuple[str, int, int]]:
    """Find palindromic sequences (DNA complement palindrome: A↔T, G↔C)."""
    complement = str.maketrans("ATGC", "TACG")
    palindromes = []
    for length in range(min_length, min(len(sequence) // 2, 13), 2):
        for i in range(len(sequence) - length + 1):
            sub = sequence[i:i+length]
            if sub == sub.translate(complement)[::-1]:
                # Avoid nested palindromes — only keep longest
                palindromes.append((sub, i, length))
    # Filter out substrings of longer palindromes
    result = []
    for p in sorted(palindromes, key=lambda x: -x[2]):
        if not any(
            other[1] <= p[1] and other[1] + other[2] >= p[1] + p[2] and other[2] > p[2]
            for other in palindromes if other is not p
        ):
            result.append(p)
    return result[:20]  # Cap


def _find_repeats(
    sequence: str, min_motif_len: int = 2, max_motif_len: int = 8, min_repeats: int = 3
) -> List[Tuple[str, int, int]]:
    """Find tandem repeats (e.g., ATATAT = AT repeated 3x)."""
    repeats = []
    for motif_len in range(min_motif_len, max_motif_len + 1):
        i = 0
        while i <= len(sequence) - motif_len * min_repeats:
            motif = sequence[i:i+motif_len]
            count = 0
            while i + (count + 1) * motif_len <= len(sequence):
                if sequence[i + count*motif_len:i + (count+1)*motif_len] == motif:
                    count += 1
                else:
                    break
            if count >= min_repeats:
                repeats.append((motif, i, count))
                i += count * motif_len
            else:
                i += 1
    return sorted(repeats, key=lambda x: -(x[2] * len(x[0])))[:15]


def get_kmer_signature(features: DNAFeatures, top_n: int = 10) -> List[Tuple[str, int]]:
    """Get the top N most frequent k-mers (any length)."""
    all_kmers = {}
    all_kmers.update(features.di_nucleotides)
    all_kmers.update(features.tri_nucleotides)
    all_kmers.update(features.tetra_nucleotides)
    return sorted(all_kmers.items(), key=lambda x: -x[1])[:top_n]


def sequence_similarity(seq_a: str, seq_b: str) -> float:
    """Compute simple sequence similarity (shared k-mer fraction)."""
    kmers_a = set(_count_kmers(seq_a, 3).keys())
    kmers_b = set(_count_kmers(seq_b, 3).keys())
    if not kmers_a or not kmers_b:
        return 0.0
    intersection = kmers_a & kmers_b
    union = kmers_a | kmers_b
    return len(intersection) / len(union)
