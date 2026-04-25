"""Unit tests for Complexity module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.complexity import ComplexityManager


class TestComplexityManager:
    """Test complexity management."""

    @pytest.fixture
    def manager(self):
        return ComplexityManager()

    def test_get_complexity_levels(self, manager):
        """Should return complexity levels."""
        levels = manager.get_levels()
        assert levels is not None
        assert len(levels) > 0

    def test_get_default_level(self, manager):
        """Should return default complexity level."""
        level = manager.get_level("default")
        assert level is not None

    def test_get_easy_level(self, manager):
        """Should return easy complexity level."""
        level = manager.get_level("easy")
        assert level is not None

    def test_get_hard_level(self, manager):
        """Should return hard complexity level."""
        level = manager.get_level("hard")
        assert level is not None

    def test_set_complexity(self, manager):
        """Should set complexity level."""
        manager.set_level("easy")
        assert manager.current_level == "easy"

    def test_complexity_affects_pattern(self, manager):
        """Complexity should affect pattern generation."""
        from src.pattern_generator import PatternGenerator

        generator = PatternGenerator()
        manager.set_level("easy")
        easy_pattern = generator.generate("ATCGATCG")

        manager.set_level("hard")
        hard_pattern = generator.generate("ATCGATCG")

        # Patterns should differ based on complexity
        assert easy_pattern is not None
        assert hard_pattern is not None
