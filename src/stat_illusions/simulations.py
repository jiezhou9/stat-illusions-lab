"""Reproducible simulations behind the five experiments.

Every function in this module is pure: given the same arguments and seed it
returns the same result, and it never touches Streamlit or global random state.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import erfc, sqrt
from statistics import NormalDist

import numpy as np
import pandas as pd


def _check_rate(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1, got {value!r}")
    return value


def _sign(value: float, tolerance: float = 1e-9) -> int:
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def _check_seed(seed: int | None) -> int | None:
    if seed is None:
        return None
    if not isinstance(seed, (int, np.integer)):
        raise TypeError("seed must be an integer or None")
    return int(seed)


# ---------------------------------------------------------------------------
# 1. Simpson's paradox
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SimpsonResult:
    """Recovery rates by severity group and overall."""

    table: pd.DataFrame
    overall_treatment: float
    overall_control: float
    advantages: dict[str, float]
    severe_share_treatment: float
    severe_share_control: float

    @property
    def signs(self) -> tuple[int, int, int]:
        """Signs of the mild, severe and overall advantages, with a tolerance."""

        return (
            _sign(self.advantages["mild"]),
            _sign(self.advantages["severe"]),
            _sign(self.advantages["overall"]),
        )

    @property
    def is_reversal(self) -> bool:
        """Whether both strata point one way and the aggregate points the other."""

        mild, severe, overall = self.signs
        return mild != 0 and mild == severe and overall == -mild


def simpson_paradox(
    mild_treatment: float = 0.92,
    severe_treatment: float = 0.62,
    mild_control: float = 0.85,
    severe_control: float = 0.50,
    severe_share_treatment: float = 0.75,
    severe_share_control: float = 0.25,
) -> SimpsonResult:
    """Combine two severity-specific recovery rates into an overall rate.

    The treatment can be better in *both* severity groups while looking worse
    overall when it is given to a larger share of severe patients.
    """

    mild_treatment = _check_rate(mild_treatment, "mild_treatment")
    severe_treatment = _check_rate(severe_treatment, "severe_treatment")
    mild_control = _check_rate(mild_control, "mild_control")
    severe_control = _check_rate(severe_control, "severe_control")
    severe_share_treatment = _check_rate(
        severe_share_treatment, "severe_share_treatment"
    )
    severe_share_control = _check_rate(severe_share_control, "severe_share_control")

    overall_treatment = (
        severe_share_treatment * severe_treatment
        + (1.0 - severe_share_treatment) * mild_treatment
    )
    overall_control = (
        severe_share_control * severe_control
        + (1.0 - severe_share_control) * mild_control
    )

    table = pd.DataFrame(
        {
            "group": ["轻症", "重症", "整体"],
            "treatment": [mild_treatment, severe_treatment, overall_treatment],
            "control": [mild_control, severe_control, overall_control],
        }
    )
    table["advantage"] = table["treatment"] - table["control"]

    advantages = {
        "mild": mild_treatment - mild_control,
        "severe": severe_treatment - severe_control,
        "overall": overall_treatment - overall_control,
    }
    return SimpsonResult(
        table=table,
        overall_treatment=float(overall_treatment),
        overall_control=float(overall_control),
        advantages=advantages,
        severe_share_treatment=severe_share_treatment,
        severe_share_control=severe_share_control,
    )


# ---------------------------------------------------------------------------
# 2. Base-rate fallacy
# ---------------------------------------------------------------------------


def _allocate_counts(expected: list[float], total: int) -> list[int]:
    """Round expected counts so the result sums exactly to ``total``."""

    raw = np.asarray(expected, dtype=float)
    if not np.isclose(raw.sum(), total, rtol=1e-9, atol=1e-9):
        raise ValueError("expected counts must sum to the population")
    counts = np.floor(raw).astype(int)
    remainder = total - int(counts.sum())
    if remainder:
        order = np.argsort(-(raw - counts), kind="stable")
        counts[order[:remainder]] += 1
    return [int(value) for value in counts]


@dataclass(frozen=True)
class BaseRateResult:
    """Bayesian breakdown of a positive test result."""

    prevalence: float
    sensitivity: float
    specificity: float
    ppv: float
    npv: float
    population: int
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int

    @property
    def positive_total(self) -> int:
        return self.true_positive + self.false_positive

    @property
    def negative_total(self) -> int:
        return self.true_negative + self.false_negative


def base_rate(
    prevalence: float = 0.01,
    sensitivity: float = 0.99,
    specificity: float = 0.95,
    population: int = 1000,
) -> BaseRateResult:
    """Compute P(disease | positive test) from prevalence and test accuracy."""

    prevalence = _check_rate(prevalence, "prevalence")
    sensitivity = _check_rate(sensitivity, "sensitivity")
    specificity = _check_rate(specificity, "specificity")
    if population < 1:
        raise ValueError("population must be a positive integer")

    tp_raw = population * prevalence * sensitivity
    fn_raw = population * prevalence * (1.0 - sensitivity)
    fp_raw = population * (1.0 - prevalence) * (1.0 - specificity)
    tn_raw = population * (1.0 - prevalence) * specificity
    tp, fp, fn, tn = _allocate_counts([tp_raw, fp_raw, fn_raw, tn_raw], population)

    # Predictive values must come from the exact probabilities, not from the
    # rounded counts used by the icon grid. Rounding 0.5 true positives to 1
    # can otherwise change a small PPV by almost a factor of two.
    positive_probability = (
        prevalence * sensitivity + (1.0 - prevalence) * (1.0 - specificity)
    )
    negative_probability = (
        prevalence * (1.0 - sensitivity) + (1.0 - prevalence) * specificity
    )
    ppv = (
        prevalence * sensitivity / positive_probability
        if positive_probability
        else float("nan")
    )
    npv = (
        (1.0 - prevalence) * specificity / negative_probability
        if negative_probability
        else float("nan")
    )

    return BaseRateResult(
        prevalence=prevalence,
        sensitivity=sensitivity,
        specificity=specificity,
        ppv=float(ppv),
        npv=float(npv),
        population=population,
        true_positive=tp,
        false_positive=fp,
        false_negative=fn,
        true_negative=tn,
    )


# ---------------------------------------------------------------------------
# 3. Multiple testing / p-hacking
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MultipleTestingResult:
    """A batch of null experiments and their two-sided p-values."""

    p_values: np.ndarray
    alpha: float
    significant: np.ndarray
    n_tests: int
    n_significant: int
    expected_false_positives: float
    familywise_error: float
    running_min: np.ndarray


def simulate_null_tests(
    n_tests: int = 100,
    n_per_group: int = 30,
    alpha: float = 0.05,
    seed: int | None = 42,
) -> MultipleTestingResult:
    """Run A/A tests and count how often a false positive appears.

    Each experiment compares two independent samples from the same standard
    normal distribution with a two-sided z-test for equal means. Under the null
    hypothesis the p-values are uniformly distributed, so roughly ``alpha`` of
    them fall below ``alpha`` even though there is no effect.
    """

    if n_tests < 1:
        raise ValueError("n_tests must be at least 1")
    if n_per_group < 2:
        raise ValueError("n_per_group must be at least 2")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")
    seed = _check_seed(seed)

    rng = np.random.default_rng(seed)
    group_a = rng.normal(size=(n_tests, n_per_group))
    group_b = rng.normal(size=(n_tests, n_per_group))
    difference = group_b.mean(axis=1) - group_a.mean(axis=1)
    standard_error = sqrt(2.0 / n_per_group)
    z_scores = difference / standard_error
    p_values = np.array(
        [erfc(abs(float(z)) / sqrt(2.0)) for z in z_scores], dtype=float
    )

    significant = p_values < alpha
    return MultipleTestingResult(
        p_values=p_values,
        alpha=alpha,
        significant=significant,
        n_tests=n_tests,
        n_significant=int(significant.sum()),
        expected_false_positives=float(n_tests * alpha),
        familywise_error=float(1.0 - (1.0 - alpha) ** n_tests),
        running_min=np.minimum.accumulate(p_values),
    )


# ---------------------------------------------------------------------------
# 4. Regression to the mean
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegressionResult:
    """Two noisy measurements of the same latent ability."""

    data: pd.DataFrame
    selected: np.ndarray
    first_mean_selected: float
    second_mean_selected: float
    overall_mean: float
    regression_amount: float
    noise: float
    top_fraction: float


def regression_to_mean(
    n: int = 500,
    noise: float = 1.0,
    top_fraction: float = 0.10,
    seed: int | None = 7,
) -> RegressionResult:
    """Select top performers on a noisy first test and re-measure them.

    ``theta`` is the stable latent ability; both measurements add independent
    normal noise. Because the selection is partly based on luck, the selected
    group's second score is expected to move closer to the overall mean.
    """

    if n < 10:
        raise ValueError("n must be at least 10")
    if noise < 0:
        raise ValueError("noise must be non-negative")
    if not 0.0 < top_fraction <= 1.0:
        raise ValueError("top_fraction must be between 0 and 1")
    seed = _check_seed(seed)

    rng = np.random.default_rng(seed)
    ability = rng.normal(size=n)
    first = ability + rng.normal(scale=noise, size=n)
    second = ability + rng.normal(scale=noise, size=n)

    threshold = float(np.quantile(first, 1.0 - top_fraction))
    selected = first >= threshold

    first_mean_selected = float(first[selected].mean())
    second_mean_selected = float(second[selected].mean())
    overall_mean = float(second.mean())

    data = pd.DataFrame(
        {
            "ability": ability,
            "first": first,
            "second": second,
            "selected": selected,
        }
    )
    return RegressionResult(
        data=data,
        selected=selected,
        first_mean_selected=first_mean_selected,
        second_mean_selected=second_mean_selected,
        overall_mean=overall_mean,
        regression_amount=first_mean_selected - second_mean_selected,
        noise=noise,
        top_fraction=top_fraction,
    )


# ---------------------------------------------------------------------------
# 5. Confidence-interval coverage
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoverageResult:
    """Repeated confidence intervals for a known population mean."""

    intervals: pd.DataFrame
    coverage: float
    expected_coverage: float
    critical_value: float
    standard_error: float
    population_mean: float


def confidence_interval_coverage(
    n_intervals: int = 100,
    sample_size: int = 30,
    confidence: float = 0.95,
    population_mean: float = 0.0,
    sigma: float = 1.0,
    seed: int | None = 11,
) -> CoverageResult:
    """Draw repeated samples and check whether each CI captures the truth."""

    if n_intervals < 1:
        raise ValueError("n_intervals must be at least 1")
    if sample_size < 2:
        raise ValueError("sample_size must be at least 2")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    seed = _check_seed(seed)

    rng = np.random.default_rng(seed)
    samples = rng.normal(
        loc=population_mean,
        scale=sigma,
        size=(n_intervals, sample_size),
    )
    means = samples.mean(axis=1)
    standard_error = sigma / sqrt(sample_size)
    critical_value = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    lower = means - critical_value * standard_error
    upper = means + critical_value * standard_error
    captured = (lower <= population_mean) & (population_mean <= upper)

    intervals = pd.DataFrame(
        {
            "interval": np.arange(1, n_intervals + 1),
            "mean": means,
            "lower": lower,
            "upper": upper,
            "captured": captured,
        }
    )
    return CoverageResult(
        intervals=intervals,
        coverage=float(captured.mean()),
        expected_coverage=confidence,
        critical_value=float(critical_value),
        standard_error=float(standard_error),
        population_mean=population_mean,
    )
