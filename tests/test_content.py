"""Tests for editorial copy that depends on the current parameters."""

from __future__ import annotations

from dataclasses import replace

import pytest

from stat_illusions.content import explanation_for
from stat_illusions.simulations import (
    base_rate,
    confidence_interval_coverage,
    regression_to_mean,
    simpson_paradox,
    simulate_null_tests,
)


def test_simpson_copy_tracks_shares_and_reversal():
    reversed_result = simpson_paradox(
        severe_share_treatment=0.75,
        severe_share_control=0.25,
    )
    text = explanation_for("simpson", reversed_result)

    assert "75%" in text["why"]
    assert "25%" in text["why"]
    assert "这就是辛普森悖论" in text["why"]

    no_reversal = simpson_paradox(
        severe_share_treatment=0.50,
        severe_share_control=0.50,
    )
    text = explanation_for("simpson", no_reversal)

    assert "当前没有发生反转" in text["why"]


def test_simpson_copy_handles_reverse_reversal_and_both_worse():
    reverse = simpson_paradox(
        mild_treatment=0.80,
        severe_treatment=0.40,
        mild_control=0.90,
        severe_control=0.50,
        severe_share_treatment=0.25,
        severe_share_control=0.75,
    )
    text = explanation_for("simpson", reverse)

    assert "反方向的辛普森悖论" in text["why"]

    both_worse = simpson_paradox(
        mild_treatment=0.80,
        severe_treatment=0.40,
        mild_control=0.90,
        severe_control=0.50,
        severe_share_treatment=0.50,
        severe_share_control=0.50,
    )
    text = explanation_for("simpson", both_worse)

    assert "当前两层都更差" in text["why"]


def test_simpson_copy_handles_zero_stratum():
    result = simpson_paradox(
        mild_treatment=0.85,
        mild_control=0.85,
        severe_treatment=0.62,
        severe_control=0.50,
    )
    text = explanation_for("simpson", result)

    assert result.signs == (0, 1, -1)
    assert not result.is_reversal
    assert "至少一个分层" in text["see"]
    assert "至少一个分层的差值为 0" in text["why"]


def test_base_rate_copy_uses_exact_ppv_and_false_positive_share():
    result = base_rate(prevalence=0.001, sensitivity=0.50, specificity=0.99)
    text = explanation_for("base_rate", result)

    assert f"{result.ppv:.1%}" in text["see"]
    assert f"{1 - result.ppv:.1%}" in text["why"]
    assert "方块数量按人数取整" in text["why"]
    assert result.ppv == pytest.approx(0.0005 / (0.0005 + 0.00999))


def test_base_rate_copy_handles_exact_half():
    result = base_rate(prevalence=0.01, sensitivity=0.99, specificity=0.99)
    text = explanation_for("base_rate", result)

    assert result.ppv == pytest.approx(0.5)
    assert "50.0%" in text["why"]


def test_multiple_testing_copy_tracks_number_of_tests():
    result = simulate_null_tests(n_tests=10, alpha=0.01, seed=3)
    text = explanation_for("multiple", result)

    assert "10 次" in text["see"]
    assert "1.0%" in text["why"]


def test_regression_copy_tracks_selection_share():
    result = regression_to_mean(top_fraction=0.20, seed=3)
    text = explanation_for("regression", result)

    assert "20%" in text["see"]
    assert "当前测量噪声" in text["why"]


def test_regression_copy_handles_negative_sample_estimate():
    result = regression_to_mean(seed=3)
    result = replace(result, regression_amount=-0.01)
    text = explanation_for("regression", result)

    assert "抽样波动" in text["why"]
    assert "不代表回归均值失效" in text["why"]


def test_ci_copy_tracks_confidence_level():
    result = confidence_interval_coverage(
        n_intervals=50,
        confidence=0.80,
        seed=3,
    )
    text = explanation_for("ci", result)

    assert "80%" in text["see"]
    assert "80%" in text["why"]


def test_unknown_experiment_raises():
    with pytest.raises(KeyError):
        explanation_for("not-an-experiment", object())
