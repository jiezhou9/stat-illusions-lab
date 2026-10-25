"""Tests for the pure simulation layer."""

from __future__ import annotations

import math

import numpy as np
import pytest

from stat_illusions.simulations import (
    base_rate,
    confidence_interval_coverage,
    regression_to_mean,
    simpson_paradox,
    simulate_null_tests,
)


class TestSimpson:
    def test_default_example_reverses_in_each_group(self):
        result = simpson_paradox()

        assert result.advantages["mild"] > 0
        assert result.advantages["severe"] > 0
        assert result.advantages["overall"] < 0

    def test_balanced_severity_mix_preserves_group_effect(self):
        result = simpson_paradox(
            severe_share_treatment=0.5,
            severe_share_control=0.5,
        )

        assert result.advantages["overall"] > 0
        assert not result.is_reversal

    def test_zero_stratum_is_not_called_a_reversal(self):
        result = simpson_paradox(
            mild_treatment=0.85,
            mild_control=0.85,
            severe_treatment=0.62,
            severe_control=0.50,
        )

        assert result.signs == (0, 1, -1)
        assert not result.is_reversal

    def test_reverse_reversal_is_detected(self):
        result = simpson_paradox(
            mild_treatment=0.80,
            severe_treatment=0.40,
            mild_control=0.90,
            severe_control=0.50,
            severe_share_treatment=0.25,
            severe_share_control=0.75,
        )

        assert result.advantages["mild"] < 0
        assert result.advantages["severe"] < 0
        assert result.advantages["overall"] > 0
        assert result.is_reversal

    def test_table_rates_are_bounded_and_consistent(self):
        result = simpson_paradox()
        table = result.table

        assert list(table["group"]) == ["轻症", "重症", "整体"]
        assert table[["treatment", "control"]].to_numpy().min() >= 0
        assert table[["treatment", "control"]].to_numpy().max() <= 1
        assert result.overall_treatment == pytest.approx(table.loc[2, "treatment"])
        assert result.overall_control == pytest.approx(table.loc[2, "control"])

    @pytest.mark.parametrize("bad_rate", [-0.01, 1.01])
    def test_invalid_rates_raise(self, bad_rate):
        with pytest.raises(ValueError):
            simpson_paradox(mild_treatment=bad_rate)


class TestBaseRate:
    def test_default_positive_predictive_value(self):
        result = base_rate()

        # 0.99 * 0.01 / (0.99 * 0.01 + 0.05 * 0.99) = 1 / 6
        assert result.ppv == pytest.approx(1 / 6)
        assert result.positive_total == result.true_positive + result.false_positive

    @pytest.mark.parametrize(
        ("prevalence", "sensitivity", "specificity"),
        [
            (0.001, 0.50, 0.99),
            (0.01, 0.99, 0.95),
            (0.05, 0.80, 0.90),
            (0.20, 0.60, 0.70),
            (0.50, 1.00, 1.00),
        ],
    )
    def test_ppv_matches_exact_bayes_formula(
        self, prevalence, sensitivity, specificity
    ):
        result = base_rate(
            prevalence=prevalence,
            sensitivity=sensitivity,
            specificity=specificity,
        )
        positive_probability = (
            prevalence * sensitivity + (1 - prevalence) * (1 - specificity)
        )
        expected = prevalence * sensitivity / positive_probability

        assert result.ppv == pytest.approx(expected, rel=1e-12, abs=1e-12)

    def test_ppv_is_not_derived_from_rounded_counts(self):
        result = base_rate(prevalence=0.001, sensitivity=0.50, specificity=0.99)

        # The exact value is ~4.8%; the rounded grid would suggest ~9.1%.
        assert result.ppv == pytest.approx(0.0005 / (0.0005 + 0.00999))
        assert result.ppv < 0.05

    def test_undefined_ppv_when_no_positive_results(self):
        result = base_rate(prevalence=0.01, sensitivity=0.0, specificity=1.0)

        assert result.positive_total == 0
        assert math.isnan(result.ppv)

    def test_counts_sum_to_population(self):
        result = base_rate(population=10_000)

        total = (
            result.true_positive
            + result.false_positive
            + result.false_negative
            + result.true_negative
        )
        assert total == 10_000

    def test_perfect_test_has_perfect_predictive_values(self):
        result = base_rate(prevalence=0.02, sensitivity=1.0, specificity=1.0)

        assert result.ppv == pytest.approx(1.0)
        assert result.npv == pytest.approx(1.0)
        assert result.false_positive == 0
        assert result.false_negative == 0

    def test_zero_prevalence_means_no_true_positives(self):
        result = base_rate(prevalence=0.0, sensitivity=0.99, specificity=0.95)

        assert result.true_positive == 0
        assert result.ppv == pytest.approx(0.0)

    def test_invalid_population_raises(self):
        with pytest.raises(ValueError):
            base_rate(population=0)


class TestMultipleTesting:
    def test_p_values_are_valid_and_reproducible(self):
        first = simulate_null_tests(n_tests=200, seed=123)
        second = simulate_null_tests(n_tests=200, seed=123)

        assert first.p_values.shape == (200,)
        assert np.all((first.p_values >= 0) & (first.p_values <= 1))
        assert np.allclose(first.p_values, second.p_values)
        assert np.array_equal(first.significant, second.significant)

    def test_false_positive_rate_is_near_alpha(self):
        result = simulate_null_tests(n_tests=2_000, alpha=0.05, seed=9)

        assert 70 <= result.n_significant <= 130
        assert result.expected_false_positives == pytest.approx(100.0)
        assert result.familywise_error == pytest.approx(1 - 0.95**2_000)

    def test_running_minimum_is_monotone(self):
        result = simulate_null_tests(n_tests=50, seed=3)

        assert np.all(np.diff(result.running_min) <= 1e-12)
        assert result.running_min[0] == pytest.approx(result.p_values[0])

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({"n_tests": 0}, "n_tests"),
            ({"n_per_group": 1}, "n_per_group"),
            ({"alpha": 0.0}, "alpha"),
            ({"alpha": 1.0}, "alpha"),
        ],
    )
    def test_invalid_inputs_raise(self, kwargs, message):
        with pytest.raises(ValueError, match=message):
            simulate_null_tests(**kwargs)


class TestRegressionToMean:
    def test_default_selection_regresses_toward_the_mean(self):
        result = regression_to_mean()

        assert len(result.data) == 500
        assert result.selected.sum() == pytest.approx(50, abs=1)
        assert abs(result.second_mean_selected - result.overall_mean) < abs(
            result.first_mean_selected - result.overall_mean
        )
        assert result.regression_amount > 0

    def test_no_noise_means_no_regression(self):
        result = regression_to_mean(noise=0.0, seed=5)

        assert result.first_mean_selected == pytest.approx(
            result.second_mean_selected
        )

    def test_reproducible(self):
        first = regression_to_mean(seed=99)
        second = regression_to_mean(seed=99)

        assert np.allclose(first.data["first"], second.data["first"])
        assert np.array_equal(first.selected, second.selected)

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({"n": 9}, "n"),
            ({"noise": -0.1}, "noise"),
            ({"top_fraction": 0.0}, "top_fraction"),
            ({"top_fraction": 1.1}, "top_fraction"),
        ],
    )
    def test_invalid_inputs_raise(self, kwargs, message):
        with pytest.raises(ValueError, match=message):
            regression_to_mean(**kwargs)


class TestConfidenceIntervals:
    def test_coverage_is_close_to_nominal(self):
        result = confidence_interval_coverage(n_intervals=2_000, seed=4)

        assert 0.93 <= result.coverage <= 0.97
        assert result.expected_coverage == pytest.approx(0.95)
        assert result.critical_value == pytest.approx(1.959964, abs=1e-5)

    def test_interval_width_shrinks_with_sample_size(self):
        small = confidence_interval_coverage(sample_size=10, seed=1)
        large = confidence_interval_coverage(sample_size=100, seed=1)

        small_width = (small.intervals["upper"] - small.intervals["lower"]).mean()
        large_width = (large.intervals["upper"] - large.intervals["lower"]).mean()
        assert large_width < small_width

    def test_intervals_are_ordered_and_reproducible(self):
        first = confidence_interval_coverage(n_intervals=50, seed=8)
        second = confidence_interval_coverage(n_intervals=50, seed=8)

        assert (first.intervals["lower"] < first.intervals["upper"]).all()
        assert np.allclose(first.intervals["mean"], second.intervals["mean"])
        assert math.isclose(first.coverage, second.coverage)

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({"n_intervals": 0}, "n_intervals"),
            ({"sample_size": 1}, "sample_size"),
            ({"confidence": 0.0}, "confidence"),
            ({"confidence": 1.0}, "confidence"),
            ({"sigma": 0.0}, "sigma"),
        ],
    )
    def test_invalid_inputs_raise(self, kwargs, message):
        with pytest.raises(ValueError, match=message):
            confidence_interval_coverage(**kwargs)
