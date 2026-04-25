"""Export format tests (PNG, JAC, TXT)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.exporters import Exporter


class TestPNGExport:
    """Test PNG export functionality."""

    @pytest.fixture
    def exporter(self):
        return Exporter()

    @pytest.mark.export
    def test_export_png(self, exporter, sample_pattern, tmp_output_dir):
        """Should export pattern to PNG."""
        output_path = tmp_output_dir / "pattern.png"
        result = exporter.export_png(sample_pattern, str(output_path))
        assert result is True
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    @pytest.mark.export
    def test_export_png_with_colors(self, exporter, sample_pattern, tmp_output_dir, sample_colors):
        """Should export PNG with custom colors."""
        output_path = tmp_output_dir / "pattern_colors.png"
        result = exporter.export_png(sample_pattern, str(output_path), colors=sample_colors)
        assert result is True
        assert output_path.exists()

    @pytest.mark.export
    def test_export_png_with_cell_size(self, exporter, sample_pattern, tmp_output_dir):
        """Should export PNG with custom cell size."""
        output_path = tmp_output_dir / "pattern_large.png"
        result = exporter.export_png(sample_pattern, str(output_path), cell_size=20)
        assert result is True
        assert output_path.exists()

    @pytest.mark.export
    def test_export_png_large_pattern(self, exporter, tmp_output_dir):
        """Should export large pattern to PNG."""
        large_pattern = [[i % 5 for i in range(20)] for _ in range(20)]
        output_path = tmp_output_dir / "large_pattern.png"
        result = exporter.export_png(large_pattern, str(output_path))
        assert result is True
        assert output_path.exists()


class TestJACExport:
    """Test JAC (embroidery format) export."""

    @pytest.fixture
    def exporter(self):
        return Exporter()

    @pytest.mark.export
    def test_export_jac(self, exporter, sample_pattern, tmp_output_dir):
        """Should export pattern to JAC format."""
        output_path = tmp_output_dir / "pattern.jac"
        result = exporter.export_jac(sample_pattern, str(output_path))
        assert result is True
        assert output_path.exists()

    @pytest.mark.export
    def test_jac_file_format(self, exporter, sample_pattern, tmp_output_dir):
        """JAC file should have valid format."""
        output_path = tmp_output_dir / "pattern.jac"
        exporter.export_jac(sample_pattern, str(output_path))

        content = output_path.read_text()
        assert len(content) > 0


class TestTXTExport:
    """Test TXT export functionality."""

    @pytest.fixture
    def exporter(self):
        return Exporter()

    @pytest.mark.export
    def test_export_txt(self, exporter, sample_pattern, tmp_output_dir):
        """Should export pattern to TXT."""
        output_path = tmp_output_dir / "pattern.txt"
        result = exporter.export_txt(sample_pattern, str(output_path))
        assert result is True
        assert output_path.exists()

    @pytest.mark.export
    def test_txt_content(self, exporter, sample_pattern, tmp_output_dir):
        """TXT file should contain pattern data."""
        output_path = tmp_output_dir / "pattern.txt"
        exporter.export_txt(sample_pattern, str(output_path))

        content = output_path.read_text()
        assert len(content) > 0
        # Should contain the pattern values
        for row in sample_pattern:
            for val in row:
                assert str(val) in content

    @pytest.mark.export
    def test_txt_format_options(self, exporter, sample_pattern, tmp_output_dir):
        """Should support different TXT formats."""
        output_path = tmp_output_dir / "pattern.csv"
        result = exporter.export_txt(sample_pattern, str(output_path), delimiter=",")
        assert result is True
        assert output_path.exists()


class TestExportMetadata:
    """Test export with metadata."""

    @pytest.fixture
    def exporter(self):
        return Exporter()

    @pytest.mark.export
    def test_export_with_metadata(self, exporter, sample_pattern, tmp_output_dir):
        """Should export with metadata."""
        output_path = tmp_output_dir / "pattern_meta.txt"
        metadata = {
            "community": "Karen",
            "dna_length": 20,
            "pattern_size": "5x5",
        }
        result = exporter.export_txt(sample_pattern, str(output_path), metadata=metadata)
        assert result is True
        assert output_path.exists()


class TestExportErrorHandling:
    """Test export error handling."""

    @pytest.fixture
    def exporter(self):
        return Exporter()

    def test_export_invalid_path(self, exporter, sample_pattern):
        """Should handle invalid path gracefully."""
        result = exporter.export_png(sample_pattern, "/nonexistent/path/pattern.png")
        assert result is False

    def test_export_empty_pattern(self, exporter, tmp_output_dir):
        """Should handle empty pattern."""
        output_path = tmp_output_dir / "empty.png"
        result = exporter.export_png([], str(output_path))
        # May return False or handle gracefully
        assert isinstance(result, bool)
