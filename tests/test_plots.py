"""Regression tests for figure annotations and encodings."""

from __future__ import annotations

from stat_illusions.plots import multiple_testing_figure, simpson_figure
from stat_illusions.simulations import simpson_paradox, simulate_null_tests


def _annotation_texts(figure) -> list[str]:
    return [annotation.text or "" for annotation in figure.layout.annotations]


def test_simpson_annotation_only_appears_when_reversal_occurs():
    reversed_figure = simpson_figure(simpson_paradox())
    assert "合并后反转" in _annotation_texts(reversed_figure)

    no_reversal = simpson_paradox(
        severe_share_treatment=0.50,
        severe_share_control=0.50,
    )
    no_reversal_figure = simpson_figure(no_reversal)
    assert "合并后反转" not in _annotation_texts(no_reversal_figure)


def test_simpson_annotation_absent_when_a_stratum_is_tied():
    tied = simpson_paradox(
        mild_treatment=0.85,
        mild_control=0.85,
        severe_treatment=0.62,
        severe_control=0.50,
    )
    figure = simpson_figure(tied)

    assert "合并后反转" not in _annotation_texts(figure)


def test_simpson_annotation_detects_reverse_reversal():
    reverse = simpson_paradox(
        mild_treatment=0.80,
        severe_treatment=0.40,
        mild_control=0.90,
        severe_control=0.50,
        severe_share_treatment=0.25,
        severe_share_control=0.75,
    )
    figure = simpson_figure(reverse)

    assert "合并后反转" in _annotation_texts(figure)


def test_alpha_label_keeps_small_values_readable():
    result = simulate_null_tests(n_tests=20, alpha=0.001, seed=3)
    figure = multiple_testing_figure(result)

    assert "α = 0.001" in _annotation_texts(figure)
