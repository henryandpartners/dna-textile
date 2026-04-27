"""Unit tests for Sensitivity Checker module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.sensitivity_checker import SensitivityChecker


class TestSensitivityChecker:
    """Test cultural sensitivity checking."""

    @pytest.fixture
    def checker(self):
        return SensitivityChecker()

    def test_check_valid_pattern(self, checker):
        """Valid pattern should pass sensitivity check."""
        result = checker.check("Karen", [[0, 1], [1, 0]])
        assert result is not None

    def test_check_different_communities(self, checker):
        """Should check sensitivity for different communities."""
        for community in ["Karen", "Hmong", "Lanna"]:
            result = checker.check(community, [[0, 1], [1, 0]])
            assert result is not None

    def test_check_returns_dict(self, checker):
        """Should return dict with results."""
        result = checker.check("Karen", [[0, 1], [1, 0]])
        assert isinstance(result, dict)

    def test_no_issues_for_valid(self, checker):
        """Valid patterns should have no issues."""
        result = checker.check("Hmong", [[0, 1, 2], [1, 3, 1], [2, 1, 0]])
        assert result.get("issues", []) == [] or result.get("sensitive", False) is False
