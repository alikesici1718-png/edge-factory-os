"""
Tests for trade-level cost adjustment and portfolio bps computation.

Formulas from v2 execution script (trade_from_candidate / split_trades):
    gross = -1 * notional * (exit_price / entry_price - 1.0)   # short direction = -1
    cost  = notional * ROUND_TRIP_COST_FRACTION                 # 0.002
    net   = gross - cost
    portfolio_net_bps = net / BASE_EQUITY * 10000.0             # BASE_EQUITY = 1000.0

Constants verified in:
  tools/edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v2_execution_v1.py
    BASE_EQUITY = 1000.0
    ROUND_TRIP_COST_FRACTION = 0.002
"""

import pytest

BASE_EQUITY = 1000.0
ROUND_TRIP_COST_FRACTION = 0.002


def compute_trade(
    entry_price: float,
    exit_price: float,
    notional: float,
    side: str = "short",
) -> dict:
    direction = -1 if side == "short" else 1
    gross = direction * notional * (exit_price / entry_price - 1.0)
    cost = notional * ROUND_TRIP_COST_FRACTION
    net = gross - cost
    return {
        "gross_pnl_usdt": gross,
        "cost_pnl_usdt": cost,
        "net_pnl_usdt": net,
        "trade_portfolio_bps": net / BASE_EQUITY * 10000.0,
    }


def portfolio_net_bps(net_pnl_usdt: float) -> float:
    return net_pnl_usdt / BASE_EQUITY * 10000.0


class TestCostAdjustment:
    def test_profitable_short(self):
        # Short: entry 100, exit 90 → price fell → profit
        t = compute_trade(entry_price=100.0, exit_price=90.0, notional=100.0)
        assert t["gross_pnl_usdt"] == pytest.approx(10.0)
        assert t["cost_pnl_usdt"] == pytest.approx(0.2)
        assert t["net_pnl_usdt"] == pytest.approx(9.8)

    def test_losing_short(self):
        # Short: entry 100, exit 110 → price rose → loss
        t = compute_trade(entry_price=100.0, exit_price=110.0, notional=100.0)
        assert t["gross_pnl_usdt"] == pytest.approx(-10.0)
        assert t["cost_pnl_usdt"] == pytest.approx(0.2)
        assert t["net_pnl_usdt"] == pytest.approx(-10.2)

    def test_cost_always_positive(self):
        # Cost is always a drag regardless of direction
        t_win = compute_trade(entry_price=100.0, exit_price=90.0, notional=50.0)
        t_loss = compute_trade(entry_price=100.0, exit_price=110.0, notional=50.0)
        assert t_win["cost_pnl_usdt"] > 0
        assert t_loss["cost_pnl_usdt"] > 0

    def test_cost_fraction(self):
        # cost = notional * 0.002
        for notional in [50.0, 100.0, 200.0]:
            t = compute_trade(entry_price=100.0, exit_price=95.0, notional=notional)
            assert t["cost_pnl_usdt"] == pytest.approx(notional * 0.002)

    def test_bps_conversion(self):
        # 10 USDT net on BASE_EQUITY 1000 = 100 bps
        assert portfolio_net_bps(10.0) == pytest.approx(100.0)

    def test_bps_negative(self):
        assert portfolio_net_bps(-5.0) == pytest.approx(-50.0)

    def test_trade_portfolio_bps(self):
        t = compute_trade(entry_price=100.0, exit_price=90.0, notional=100.0)
        # net = 9.8 → bps = 9.8 / 1000 * 10000 = 98.0
        assert t["trade_portfolio_bps"] == pytest.approx(98.0)

    def test_breakeven_exactly_at_cost(self):
        # If gross = cost, net = 0
        # gross = notional * (entry-exit)/entry = notional * 0.002
        # entry=100, exit=99.8 → price_return = 0.2/100 = 0.002
        t = compute_trade(entry_price=100.0, exit_price=99.8, notional=100.0)
        assert t["gross_pnl_usdt"] == pytest.approx(0.2, abs=1e-10)
        assert t["net_pnl_usdt"] == pytest.approx(0.0, abs=1e-10)

    def test_net_less_than_gross(self):
        # Cost always makes net < gross (when cost > 0)
        t = compute_trade(entry_price=100.0, exit_price=80.0, notional=100.0)
        assert t["net_pnl_usdt"] < t["gross_pnl_usdt"]

    def test_long_direction(self):
        # Long: entry 90, exit 100 → profit
        t = compute_trade(entry_price=90.0, exit_price=100.0, notional=100.0, side="long")
        assert t["gross_pnl_usdt"] == pytest.approx(100.0 * (100.0 / 90.0 - 1.0))
        assert t["net_pnl_usdt"] == pytest.approx(t["gross_pnl_usdt"] - 0.2)
