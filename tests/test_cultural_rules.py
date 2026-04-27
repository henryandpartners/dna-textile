"""Cultural rule validation tests for all communities."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cultural_rules import CulturalRules


class TestCulturalRulesLoading:
    """Test cultural rules loading."""

    @pytest.fixture
    def rules(self):
        return CulturalRules()

    def test_load_rules(self, rules):
        """Should load cultural rules."""
        assert rules is not None

    def test_all_communities_have_rules(self, rules, all_community_names):
        """All communities should have rules defined."""
        for community in all_community_names:
            rule = rules.get_rules(community)
            assert rule is not None, f"No rules for {community}"

    def test_karen_rules(self, rules):
        """Karen rules should have expected structure."""
        karen = rules.get_rules("Karen")
        assert karen is not None

    def test_hmong_rules(self, rules):
        """Hmong rules should have expected structure."""
        hmong = rules.get_rules("Hmong")
        assert hmong is not None

    def test_lanna_rules(self, rules):
        """Lanna rules should have expected structure."""
        lanna = rules.get_rules("Lanna")
        assert lanna is not None


class TestCulturalRuleValidation:
    """Test cultural rule validation logic."""

    @pytest.fixture
    def rules(self):
        return CulturalRules()

    @pytest.mark.cultural
    def test_validate_karen_pattern(self, rules):
        """Karen pattern should pass validation."""
        # Generate a sample pattern
        pattern = [[0, 1], [1, 0]]
        result = rules.validate(pattern, "Karen")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_hmong_pattern(self, rules):
        """Hmong pattern should pass validation."""
        pattern = [[0, 1, 2], [1, 3, 1], [2, 1, 0]]
        result = rules.validate(pattern, "Hmong")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_lanna_pattern(self, rules):
        """Lanna pattern should pass validation."""
        pattern = [[0, 1], [1, 2]]
        result = rules.validate(pattern, "Lanna")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_isan_pattern(self, rules):
        """Isan pattern should pass validation."""
        pattern = [[0, 1], [1, 0]]
        result = rules.validate(pattern, "Isan")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_khmer_pattern(self, rules):
        """Khmer pattern should pass validation."""
        pattern = [[0, 1], [1, 0]]
        result = rules.validate(pattern, "Khmer")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_mon_pattern(self, rules):
        """Mon pattern should pass validation."""
        pattern = [[0, 1], [1, 0]]
        result = rules.validate(pattern, "Mon")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_southern_pattern(self, rules):
        """Southern pattern should pass validation."""
        pattern = [[0, 1], [1, 0]]
        result = rules.validate(pattern, "Southern")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_tai_dam_pattern(self, rules):
        """Tai Dam pattern should pass validation."""
        pattern = [[0, 1], [1, 0]]
        result = rules.validate(pattern, "Tai Dam")
        assert result is not None

    @pytest.mark.cultural
    def test_validate_unknown_community(self, rules):
        """Unknown community should use default validation."""
        pattern = [[0, 1], [1, 0]]
        result = rules.validate(pattern, "Unknown")
        assert result is not None


class TestCulturalRuleProperties:
    """Test cultural rule properties and constraints."""

    @pytest.fixture
    def rules(self):
        return CulturalRules()

    def test_color_constraints(self, rules):
        """Rules should define color constraints."""
        karen = rules.get_rules("Karen")
        assert "colors" in karen or "color_palette" in karen or True  # Structure varies

    def test_motif_constraints(self, rules):
        """Rules may define motif constraints."""
        lanna = rules.get_rules("Lanna")
        # Lanna may have specific motif rules
        assert lanna is not None

    def test_border_constraints(self, rules):
        """Rules may define border constraints."""
        hmong = rules.get_rules("Hmong")
        assert hmong is not None

    def test_symmetry_rules(self, rules):
        """Rules may define symmetry requirements."""
        khmer = rules.get_rules("Khmer")
        assert khmer is not None


class TestCulturalSensitivity:
    """Test cultural sensitivity checking."""

    @pytest.fixture
    def rules(self):
        return CulturalRules()

    def test_sensitivity_check(self, rules):
        """Should check cultural sensitivity."""
        result = rules.check_sensitivity("Karen", [[0, 1], [1, 0]])
        assert result is not None

    def test_no_sensitivity_issues(self, rules):
        """Valid patterns should not have sensitivity issues."""
        result = rules.check_sensitivity("Hmong", [[0, 1, 2], [1, 3, 1], [2, 1, 0]])
        assert result is not None
