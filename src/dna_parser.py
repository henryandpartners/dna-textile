"""DNA sequence parser — supports FASTA files and raw string input."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


# Canonical nucleotide set
VALID_BASES = frozenset("ATGC")


class DNASparseError(ValueError):
    """Raised when a DNA sequence contains invalid characters."""
    pass


def clean_sequence(raw: str) -> str:
    """Strip whitespace and newlines, uppercase, validate."""
    seq = re.sub(r"\s+", "", raw).upper()
    invalid = set(seq) - VALID_BASES
    if invalid:
        raise DNASparseError(
            f"Invalid nucleotide(s) found: {invalid}. "
            f"Only {VALID_BASES} are allowed."
        )
    return seq


def parse_string(sequence: str) -> str:
    """Parse a raw DNA string and return cleaned uppercase sequence."""
    return clean_sequence(sequence)


def parse_fasta(filepath: str | Path) -> List[Tuple[str, str]]:
    """
    Parse a FASTA file.

    Returns:
        List of (header, sequence) tuples.
        header includes the '>' prefix stripped.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"FASTA file not found: {path}")

    entries: List[Tuple[str, str]] = []
    current_header: str | None = None
    current_lines: List[str] = []

    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                # Flush previous entry
                if current_header is not None:
                    seq = clean_sequence("".join(current_lines))
                    entries.append((current_header, seq))
                current_header = line[1:].strip()
                current_lines = []
            else:
                current_lines.append(line)

    # Flush last entry
    if current_header is not None:
        seq = clean_sequence("".join(current_lines))
        entries.append((current_header, seq))

    if not entries:
        raise DNASparseError(f"No valid FASTA entries found in {path}")

    return entries


def parse_input(source: str | Path, is_fasta: bool = False) -> List[Tuple[str, str]]:
    """
    Unified entry point.

    - If is_fasta=True or source ends with .fasta/.fa → parse as FASTA.
    - Otherwise treat as raw DNA string (single entry with header "input").
    """
    source_str = str(source)
    if is_fasta or source_str.lower().endswith((".fasta", ".fa")):
        return parse_fasta(source)
    seq = parse_string(source_str)
    return [("input", seq)]
