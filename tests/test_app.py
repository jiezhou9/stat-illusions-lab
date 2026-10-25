"""Smoke tests for the Streamlit application."""

from __future__ import annotations

from pathlib import Path

import pytest

streamlit = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _app() -> AppTest:
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)


def test_home_page_renders_without_exception():
    at = _app().run()

    assert not at.exception
    assert at.title or at.markdown
    assert any("统计错觉" in item.value for item in at.markdown)


def test_every_experiment_page_renders_without_exception():
    at = _app().run()
    radio = at.sidebar.radio[0]
    labels = list(radio.options)

    assert len(labels) == 6
    for label in labels[1:]:
        radio.set_value(label)
        at.run()
        assert not at.exception, f"{label} raised: {at.exception}"


@pytest.mark.parametrize(
    ("index", "label"),
    [
        (0, "01 · 辛普森悖论"),
        (1, "02 · 基础率谬误"),
        (2, "03 · p 值狩猎"),
        (3, "04 · 回归均值"),
        (4, "05 · 置信区间"),
    ],
)
def test_home_buttons_navigate_to_experiment_pages(index, label):
    at = _app().run()

    assert len(at.button) == 5
    at.button[index].click().run()

    assert not at.exception
    assert at.radio[0].value == label


def test_ci_callout_uses_selected_confidence_level():
    at = _app().run()
    at.sidebar.radio[0].set_value("05 · 置信区间").run()
    at.select_slider[0].set_value(80).run()

    assert not at.exception
    assert any("80% 描述的是长期频率" in item.value for item in at.markdown)
