"""
Cultural Sensitivity Checker — validates patterns against cultural taboos
and sacred motif restrictions.

Phase 2: Loads sensitivity rules from cultural_sensitivity.json and provides
taboo detection, sacred motif checking, and approval workflow management.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


_BASE_DIR = Path(__file__).resolve().parent.parent
_SENSITIVITY_FILE = _BASE_DIR / "cultural_sensitivity.json"

_SENSITIVITY_DATA: Optional[Dict[str, Any]] = None


class Severity(str, Enum):
    """Severity levels for cultural sensitivity violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SensitivityViolation:
    """A detected cultural sensitivity violation."""
    pattern_name: str
    community: str
    severity: Severity
    reason: str
    is_taboo: bool = False
    is_sacred: bool = False
    approval_required: bool = False
    context: str = ""


@dataclass
class SensitivityReport:
    """Complete sensitivity check report."""
    community: str
    violations: List[SensitivityViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sacred_motifs_used: List[str] = field(default_factory=list)
    taboo_patterns_found: List[str] = field(default_factory=list)
    approval_needed: bool = False

    @property
    def is_clean(self) -> bool:
        """Check if there are no violations."""
        return len(self.violations) == 0

    @property
    def has_high_severity(self) -> bool:
        """Check if any violations are high severity."""
        return any(v.severity in (Severity.HIGH, Severity.CRITICAL) for v in self.violations)

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"Sensitivity Report for {self.community}:",
            f"  Violations: {len(self.violations)}",
            f"  Warnings: {len(self.warnings)}",
            f"  Sacred motifs used: {len(self.sacred_motifs_used)}",
            f"  Taboo patterns found: {len(self.taboo_patterns_found)}",
            f"  Approval needed: {self.approval_needed}",
        ]
        for v in self.violations:
            lines.append(f"  [{v.severity.value}] {v.pattern_name}: {v.reason}")
        return "\n".join(lines)


def _load_sensitivity_data() -> Dict[str, Any]:
    """Load sensitivity data from JSON."""
    global _SENSITIVITY_DATA
    if _SENSITIVITY_DATA is not None:
        return _SENSITIVITY_DATA

    if not _SENSITIVITY_FILE.exists():
        _SENSITIVITY_DATA = {
            "taboo_patterns": {},
            "sacred_motifs": {},
            "general_guidelines": {},
            "approval_workflow": {"steps": []},
        }
        return _SENSITIVITY_DATA

    with open(_SENSITIVITY_FILE, "r", encoding="utf-8") as f:
        _SENSITIVITY_DATA = json.load(f)

    return _SENSITIVITY_DATA


def get_taboo_patterns(community: str) -> List[str]:
    """Get list of taboo pattern names for a community."""
    data = _load_sensitivity_data()
    taboos = data.get("taboo_patterns", {})
    result = []
    for pattern_name, pattern_data in taboos.items():
        if not isinstance(pattern_data, dict):
            continue  # skip _description metadata
        taboo_in = pattern_data.get("taboo_in", [])
        if community.lower() in [c.lower() for c in taboo_in]:
            result.append(pattern_name)
    return result


def get_sacred_motifs(community: str) -> Dict[str, Dict[str, Any]]:
    """Get sacred motifs for a community with their restrictions."""
    data = _load_sensitivity_data()
    key = community.lower().replace(" ", "_")
    sacred = data.get("sacred_motifs", {})
    return sacred.get(key, {})


def check_taboo(pattern_name: str, community: str) -> Optional[SensitivityViolation]:
    """Check if a pattern is taboo for a community."""
    data = _load_sensitivity_data()
    taboos = data.get("taboo_patterns", {})

    pattern_data = taboos.get(pattern_name)
    if not pattern_data:
        return None

    taboo_in = [c.lower() for c in pattern_data.get("taboo_in", [])]
    if community.lower() not in taboo_in:
        return None

    severity_map = {
        "low": Severity.LOW,
        "medium": Severity.MEDIUM,
        "high": Severity.HIGH,
        "critical": Severity.CRITICAL,
    }

    return SensitivityViolation(
        pattern_name=pattern_name,
        community=community,
        severity=severity_map.get(pattern_data.get("severity", "medium"), Severity.MEDIUM),
        reason=pattern_data.get("reason", f"Pattern '{pattern_name}' is taboo for {community}"),
        is_taboo=True,
    )


def check_sacred_motif(motif_name: str, community: str) -> Optional[SensitivityViolation]:
    """Check if a motif is sacred and requires approval."""
    sacred = get_sacred_motifs(community)
    motif_data = sacred.get(motif_name)

    if not motif_data:
        return None

    if not motif_data.get("approval_required", False):
        return None

    return SensitivityViolation(
        pattern_name=motif_name,
        community=community,
        severity=Severity.HIGH,
        reason=f"Sacred motif '{motif_name}' requires community approval",
        is_sacred=True,
        approval_required=True,
        context=motif_data.get("context", ""),
    )


def check_pattern_set(
    pattern_names: List[str],
    community: str,
) -> SensitivityReport:
    """
    Check a set of patterns/motifs against cultural sensitivity rules.

    Args:
        pattern_names: List of pattern/motif names to check.
        community: Target community.

    Returns:
        SensitivityReport with all findings.
    """
    report = SensitivityReport(community=community)

    for name in pattern_names:
        # Check taboos
        taboo_violation = check_taboo(name, community)
        if taboo_violation:
            report.violations.append(taboo_violation)
            report.taboo_patterns_found.append(name)

        # Check sacred motifs
        sacred_violation = check_sacred_motif(name, community)
        if sacred_violation:
            report.violations.append(sacred_violation)
            report.sacred_motifs_used.append(name)
            report.approval_needed = True

    # Add general warnings
    guidelines = _load_sensitivity_data().get("general_guidelines", {})
    if report.sacred_motifs_used:
        report.warnings.append(
            "Sacred motifs detected. Community approval is required before use."
        )
    if report.taboo_patterns_found:
        report.warnings.append(
            f"Taboo patterns detected: {', '.join(report.taboo_patterns_found)}. "
            "These patterns must not be used."
        )

    return report


def get_approval_workflow() -> List[Dict[str, Any]]:
    """Get the community approval workflow steps."""
    data = _load_sensitivity_data()
    return data.get("approval_workflow", {}).get("steps", [])


def get_general_guidelines() -> Dict[str, Any]:
    """Get general cultural sensitivity guidelines."""
    data = _load_sensitivity_data()
    return data.get("general_guidelines", {})


def validate_sensitivity(
    community: str,
    motifs: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> Tuple[bool, SensitivityReport]:
    """
    Full sensitivity validation for a pattern set.

    Args:
        community: Target community.
        motifs: List of motif names.
        patterns: List of pattern names.

    Returns:
        Tuple of (is_valid, report).
    """
    all_names = []
    if motifs:
        all_names.extend(motifs)
    if patterns:
        all_names.extend(patterns)

    report = check_pattern_set(all_names, community)
    is_valid = report.is_clean and not report.has_high_severity
    return (is_valid, report)
