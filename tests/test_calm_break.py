import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.calm_break import DEFAULT_PALETTE, calm_break_html  # noqa: E402


def test_every_placeholder_is_filled():
    html = calm_break_html()
    assert not re.search(r"__[A-Z_]+__", html)


def test_page_is_self_contained_no_network_no_external_files():
    html = calm_break_html()
    assert "http://" not in html and "https://" not in html
    assert "<script src" not in html and "<link" not in html


def test_it_is_a_calm_page_no_timer_score_target_or_game_over():
    html = calm_break_html().lower()
    assert "game over" not in html and "high score" not in html and "time left" not in html
    assert "no timer" in html


def test_has_the_star_canvas_and_the_4_in_6_out_breathing_ring():
    html = calm_break_html()
    assert '<canvas id="sky"' in html and 'id="ring"' in html
    assert "cycle < 4" in html and "(cycle - 4) / 6" in html     # in 4 s, out 6 s
    assert "Breathe in" in html and "Breathe out" in html


def test_respects_reduced_motion():
    assert "prefers-reduced-motion: reduce" in calm_break_html()


def test_palette_can_be_overridden():
    html = calm_break_html({"bg_top": "#123456", "star": "#abcdef"})
    assert "#123456" in html and "#abcdef" in html
    assert DEFAULT_PALETTE["bg_top"] not in html


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_javascript_has_no_syntax_errors(tmp_path):
    html = calm_break_html()
    script = re.search(r"<script>(.*)</script>", html, re.S).group(1)
    js = tmp_path / "calm.js"
    js.write_text(script, encoding="utf-8")
    result = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


st_testing = pytest.importorskip("streamlit.testing.v1")


def test_page_loads_without_errors():
    at = st_testing.AppTest.from_file(str(ROOT / "pages" / "6_Calm_Break.py")).run(timeout=30)
    assert not at.exception
    assert at.title[0].value == "Calm Break"
    assert any("not medical advice" in c.value for c in at.caption)
