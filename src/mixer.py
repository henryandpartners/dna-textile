"""DNA pattern mixer — blend patterns from multiple sequences."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from .pattern_generator import PatternGenerator


def mix_patterns(
    sequences: List[str],
    weights: List[float] | None = None,
    grid_size: int = 100,
    pattern_type: str = "grid",
    seed: int | None = None,
) -> np.ndarray:
    """
    Blend multiple DNA sequences into a single pattern grid.

    Each sequence is independently mapped to a color grid, then
    the grids are combined using weighted averaging of RGB values.

    Args:
        sequences:    List of cleaned DNA strings.
        weights:      Optional weight for each sequence (normalized internally).
                      Defaults to equal weights.
        grid_size:    Output grid dimension.
        pattern_type: Pattern algorithm to use.
        seed:         RNG seed for reproducibility.

    Returns:
        Blended color grid (H×W×3 uint8).
    """
    if len(sequences) == 0:
        raise ValueError("At least one sequence is required")

    if weights is None:
        weights = [1.0] * len(sequences)
    if len(weights) != len(sequences):
        raise ValueError("weights length must match sequences length")

    # Normalize weights
    total = sum(weights)
    weights = [w / total for w in weights]

    gen = PatternGenerator(grid_size=grid_size)
    blended = np.zeros((grid_size, grid_size, 3), dtype=np.float64)

    for seq, w in zip(sequences, weights):
        grid = gen.generate_grid(seq, pattern_type=pattern_type, seed=seed)
        blended += grid.astype(np.float64) * w

    # Clip and convert
    blended = np.clip(blended, 0, 255).astype(np.uint8)
    return blended


def mix_sequences(
    sequences: List[str],
    weights: List[float] | None = None,
) -> str:
    """
    Blend DNA sequences at the string level (before pattern generation).

    Uses weighted random sampling: for each position, pick a nucleotide
    from one of the sequences based on weights.

    Args:
        sequences:  List of DNA strings.
        weights:    Optional weights (normalized internally).

    Returns:
        Blended DNA string (length = shortest input sequence).
    """
    import random

    if len(sequences) == 0:
        raise ValueError("At least one sequence is required")

    if weights is None:
        weights = [1.0] * len(sequences)
    if len(weights) != len(sequences):
        raise ValueError("weights length must match sequences length")

    total = sum(weights)
    weights = [w / total for w in weights]

    min_len = min(len(s) for s in sequences)
    result = []

    for i in range(min_len):
        # Weighted choice of which sequence to pull from
        choice = random.choices(range(len(sequences)), weights=weights, k=1)[0]
        result.append(sequences[choice][i])

    return "".join(result)


def _mix_alternating(dna1: str, dna2: str) -> str:
    """Mix two sequences by alternating which parent to pick from at each position.
    Output length equals the shorter input length."""
    result = []
    min_len = min(len(dna1), len(dna2))
    for i in range(min_len):
        if i % 2 == 0:
            result.append(dna1[i])
        else:
            result.append(dna2[i])
    return "".join(result)


def _mix_crossover(dna1: str, dna2: str) -> str:
    """Mix two sequences with a single crossover point."""
    import random
    if len(dna1) == 0 or len(dna2) == 0:
        return dna1 or dna2
    point = random.randint(1, min(len(dna1), len(dna2)) - 1)
    return dna1[:point] + dna2[point:]


class DNAMixer:
    """Thin wrapper for DNA mixer functions."""

    def __init__(self):
        pass

    def mix(self, dna1: str, dna2: str, method: str = "alternating") -> str:
        if not dna1 or not dna2:
            raise ValueError("Both sequences must be non-empty")
        if method == "alternating":
            return _mix_alternating(dna1, dna2)
        elif method == "random":
            return mix_sequences([dna1, dna2])
        elif method == "crossover":
            return _mix_crossover(dna1, dna2)
        else:
            raise ValueError(f"Unknown mix method: {method}")
