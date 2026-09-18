"""Tests for SVGRenderer module."""

import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from exceptions import ELSTRIXError
from renderer import SVGRenderer


def test_dots_and_dashes() -> None:
    """Test helper functions _dots and _dashes."""
    dots = SVGRenderer._dots("Key", "Value", total=20)
    assert isinstance(dots, str)
    assert len(dots) >= 2
    assert set(dots) == {"."}

    dashes = SVGRenderer._dashes("Header", total=20)
    assert isinstance(dashes, str)
    assert len(dashes) == 14
    assert set(dashes) == {"\u2500"}


def test_render_line_escaping() -> None:
    """Test XML/HTML escaping in _render_line."""
    renderer = SVGRenderer(output_dir="tmp")
    line = renderer._render_line(
        [("<script>alert('xss')</script>&", "#ffffff")],
        y=50,
    )
    assert "<script>" not in line
    assert "&lt;script&gt;alert('xss')&lt;/script&gt;&amp;" in line


def test_render_execution(mocker, tmp_path) -> None:
    """Test full render loop with mock paths."""
    out_dir = tmp_path / "svg_out"
    out_dir.mkdir()

    mocker.patch("renderer.PathManager.GENERATED_STATS_DIR", new=tmp_path)
    mocker.patch("renderer.PathManager.GENERATED_SVG_DIR", new=tmp_path)

    renderer = SVGRenderer(output_dir=str(out_dir))
    renderer.render()

    assert (out_dir / "light.svg").exists()
    assert (out_dir / "dark.svg").exists()


def test_render_failure_raises_error(mocker, tmp_path) -> None:
    """Test error handling when writing SVG fails."""
    mocker.patch("renderer.PathManager.GENERATED_STATS_DIR", new=tmp_path)
    mocker.patch("renderer.PathManager.GENERATED_SVG_DIR", new=tmp_path)

    renderer = SVGRenderer(output_dir=str(tmp_path))
    mocker.patch("builtins.open", side_effect=OSError("Write permission denied"))

    with pytest.raises(ELSTRIXError):
        renderer.render()
