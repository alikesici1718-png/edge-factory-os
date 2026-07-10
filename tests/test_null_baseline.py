"""
Tests for the null-baseline percentile logic used across strategy execution scripts.

The exact computation (from v2/v3/mpv execution files):
    percentile_rank = sum(1 for v in null_values if v <= observed) / len(null_values)
    null_pass = percentile_rank >= 0.95

This module tests that logic in isolation, without importing the execution scripts
(which require panel data and git context).
"""

import pytest


def compute_percentile_rank(null_values: list, observed: float) -> float:
    """Mirror of the one-liner used in every execution script."""
    return sum(1 for v in null_values if v <= observed) / len(null_values)


def null_pass(percentile_rank: float, threshold: float = 0.95) -> bool:
    return percentile_rank >= threshold


class TestPercentileRank:
    def test_observed_above_all_null(self):
        # observed beats every null run → rank = 1.0
        null = list(range(100))   # [0, 1, ..., 99]
        rank = compute_percentile_rank(null, observed=200.0)
        assert rank == 1.0

    def test_observed_below_all_null(self):
        # observed beats none → rank = 0.0
        null = list(range(1, 101))  # [1, 2, ..., 100]
        rank = compute_percentile_rank(null, observed=0.0)
        assert rank == 0.0

    def test_84th_percentile(self):
        # 84 values ≤ observed out of 100 → rank = 0.84
        null = list(range(100))   # [0 .. 99]
        # observed = 83 → 84 values satisfy v <= 83 (0..83)
        rank = compute_percentile_rank(null, observed=83.0)
        assert rank == pytest.approx(0.84)

    def test_95th_percentile_exactly(self):
        # 95 values ≤ observed → rank = 0.95
        null = list(range(100))
        rank = compute_percentile_rank(null, observed=94.0)
        assert rank == pytest.approx(0.95)

    def test_ties_counted(self):
        # values equal to observed count as <= observed
        null = [10.0] * 50 + [20.0] * 50   # 100 values
        rank = compute_percentile_rank(null, observed=10.0)
        # 50 values equal to 10.0, all counted as <=
        assert rank == pytest.approx(0.50)

    def test_negative_observed(self):
        null = [-5.0, -3.0, -1.0, 0.0, 2.0]
        rank = compute_percentile_rank(null, observed=-2.0)
        # only -5.0 and -3.0 are <= -2.0 → 2/5
        assert rank == pytest.approx(0.40)


class TestNullPass:
    def test_84th_percentile_fails(self):
        # The real strategy result: 84th pct → rejected
        assert null_pass(0.84) is False

    def test_95th_percentile_passes(self):
        assert null_pass(0.95) is True

    def test_96th_percentile_passes(self):
        assert null_pass(0.96) is True

    def test_94th_percentile_fails(self):
        assert null_pass(0.94) is False

    def test_custom_threshold(self):
        assert null_pass(0.90, threshold=0.90) is True
        assert null_pass(0.89, threshold=0.90) is False

    def test_full_pipeline_84th(self):
        # Reproduce the actual strategy result in miniature:
        # 100 null runs, observed beats 84 of them → null_pass must be False
        null = list(range(100))
        observed = 83.0   # 84 values satisfy v <= 83
        rank = compute_percentile_rank(null, observed)
        assert null_pass(rank) is False
        assert rank == pytest.approx(0.84)

    def test_full_pipeline_95th_threshold(self):
        # Minimum passing case
        null = list(range(100))
        observed = 94.0   # exactly 95 values satisfy v <= 94
        rank = compute_percentile_rank(null, observed)
        assert null_pass(rank) is True
        assert rank == pytest.approx(0.95)
