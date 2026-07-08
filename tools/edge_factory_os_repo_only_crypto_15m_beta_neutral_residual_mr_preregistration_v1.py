from __future__ import annotations

import csv
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1\panel_15m_by_symbol"
)
PANEL_REVIEW = REPO_ROOT / "artifacts" / "panel_build_reviews" / "binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_beta_neutral_residual_mr_preregistration_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_BETA_NEUTRAL_RESIDUAL_MR_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_BETA_NEUTRAL_RESIDUAL_MR_PREREGISTRATION"
STRATEGY = "CRYPTO_15M_BTC_ETH_BETA_NEUTRAL_RESIDUAL_MEAN_REVERSION_V1"
ROUTE_FAMILY = "CRYPTO_15M_BETA_NEUTRAL_RESIDUAL_STAT_ARB_BASELINE"
CONFIG_ID = "crypto_15m_btc_eth_beta_neutral_residual_z30d_abs25_hold8h_v1"
EXPECTED_COLUMNS = {
    "symbol",
    "timestamp_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "complete_15m",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def inspect_anchor(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "header": [], "first_row": None}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        first_row = next(reader, None)
    return {
        "path": str(path),
        "exists": True,
        "header": header,
        "has_required_columns": EXPECTED_COLUMNS.issubset(set(header)),
        "first_row": first_row,
    }


def inspect_panel() -> dict[str, Any]:
    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    return {
        "panel_dir": str(PANEL_DIR),
        "panel_dir_exists": PANEL_DIR.exists(),
        "symbol_file_count": len(files),
        "symbols": symbols,
        "btc_anchor": inspect_anchor(PANEL_DIR / "BTCUSDT_15m.csv.gz"),
        "eth_anchor": inspect_anchor(PANEL_DIR / "ETHUSDT_15m.csv.gz"),
        "traded_residual_universe_count": len([symbol for symbol in symbols if symbol not in {"BTCUSDT", "ETHUSDT"}]),
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_beta_neutral_residual_mr_preregistration_v1.py",
        "?? artifacts/research_preregistrations/crypto_15m_beta_neutral_residual_mr_preregistration_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    panel_review = load_json(PANEL_REVIEW)
    panel = inspect_panel()
    if not panel["panel_dir_exists"] or panel["symbol_file_count"] != 81:
        raise RuntimeError("reviewed 81-symbol 15m panel missing")
    if not panel["btc_anchor"]["exists"] or not panel["eth_anchor"]["exists"]:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    if not panel["btc_anchor"].get("has_required_columns") or not panel["eth_anchor"].get("has_required_columns"):
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")

    preregistered_config = {
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "single_config_only": True,
        "parameter_grid_allowed": False,
        "optimization_allowed": False,
        "threshold_changes_allowed": False,
        "dataset": {
            "name": "reviewed Binance/OKX overlap 81-symbol 15m panel",
            "panel_directory": str(PANEL_DIR),
            "panel_review_artifact": str(PANEL_REVIEW),
            "expected_symbol_count": 81,
            "expected_timeframe": "15m",
            "expected_start_utc": "2023-01-01T00:00:00Z",
            "expected_end_utc": "2025-10-31T23:45:00Z",
            "expected_rows": 7808472,
            "required_anchor_symbols": ["BTCUSDT", "ETHUSDT"],
            "traded_residual_universe": "all reviewed symbols except BTCUSDT and ETHUSDT",
        },
        "feature_construction": {
            "return_source": "15m close-to-close returns",
            "rolling_beta_window_bars": 2880,
            "minimum_beta_observations": 1000,
            "ols_model": "rS = alpha + beta_btc * rB + beta_eth * rE + residual",
            "beta_lookahead_policy": "use only data strictly before signal timestamp",
            "residual_impulse_window_bars": 16,
            "residual_z_history_window_bars": 2880,
            "liquidity_filter": "24h quote_volume sum > 1000000 USDT when quote_volume exists; current quote_volume > 0",
        },
        "signals": {
            "long_residual_mean_reversion": "z_residual <= -2.5",
            "short_residual_mean_reversion": "z_residual >= 2.5",
            "rank_if_capacity_exceeded": "abs(z_residual) descending",
            "max_concurrent_residual_positions": 8,
            "one_open_position_per_symbol": True,
            "btc_eth_not_traded_as_residual_legs": True,
        },
        "entry_exit": {
            "entry": "signal at 15m close, enter next 15m open",
            "hold_bars": 32,
            "exit": "next available 15m open after fixed 8h hold",
            "missing_entry_or_exit": "skip entry or mark unresolved",
        },
        "portfolio_and_hedge": {
            "base_equity_usdt": 1000.0,
            "symbol_leg_notional_usdt": 50.0,
            "gross_package_notional_cap_usdt": 150.0,
            "btc_hedge_notional": "abs(beta_btc) * symbol_leg_notional",
            "eth_hedge_notional": "abs(beta_eth) * symbol_leg_notional",
            "hedge_sign_policy": "opposite beta exposure to residual leg with beta sign preserved in PnL",
            "symbol_round_trip_cost_bps": 20.0,
            "btc_hedge_round_trip_cost_bps": 10.0,
            "eth_hedge_round_trip_cost_bps": 10.0,
            "no_leverage_assumption": True,
            "no_compounding": True,
        },
        "splits": {
            "train": ["2023-01-01T00:00:00Z", "2024-07-01T00:00:00Z"],
            "validation": ["2024-07-01T00:00:00Z", "2025-04-01T00:00:00Z"],
            "holdout": ["2025-04-01T00:00:00Z", "2025-11-01T00:00:00Z"],
        },
        "evaluator_policy": {
            "diagnostic_promising_requires": [
                "validation portfolio net bps > 0",
                "holdout portfolio net bps > 0",
                "validation monthly positive rate >= 0.60",
                "holdout monthly positive rate >= 0.50",
                "validation closed trades >= 50",
                "null baseline passes",
                "top symbol trade share <= 0.25",
                "worst month > -1000 bps",
                "metric integrity passes",
                "no candidate/edge/live/capital",
            ],
            "allowed_result_classes": [
                "CRYPTO_15M_BETA_NEUTRAL_RESIDUAL_MR_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
                "CRYPTO_15M_BETA_NEUTRAL_RESIDUAL_MR_REJECTED_NO_FOLLOWUP",
                "CRYPTO_15M_BETA_NEUTRAL_RESIDUAL_MR_INCONCLUSIVE_NEEDS_MORE_DATA",
                "CRYPTO_15M_BETA_NEUTRAL_RESIDUAL_MR_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE",
            ],
        },
    }
    safety_permissions = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "live_permission_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "capital_permission_allowed_now": False,
        "real_orders_allowed_now": False,
        "family_release_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "panel_review_artifact_loaded": True,
        "panel_directory_exists": panel["panel_dir_exists"],
        "symbol_file_count_verified_81": panel["symbol_file_count"] == 81,
        "btc_anchor_available": panel["btc_anchor"]["exists"],
        "eth_anchor_available": panel["eth_anchor"]["exists"],
        "btc_anchor_header_verified": panel["btc_anchor"].get("has_required_columns") is True,
        "eth_anchor_header_verified": panel["eth_anchor"].get("has_required_columns") is True,
        "no_network_used": True,
        "no_api_used": True,
        "no_parameter_grid": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_beta_neutral_residual_mr_preregistration_v1",
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_preregistration": status_lines,
            "allowed_new_paths_at_preregistration": sorted(allowed_status),
            "unexpected_dirty_paths_at_preregistration": unexpected_status,
        },
        "source_artifacts": {"panel_review": str(PANEL_REVIEW)},
        "panel_review_status": panel_review.get("status"),
        "panel_inspection": panel,
        "preregistered_config": preregistered_config,
        "metric_integrity_preregistration": {
            "no_lookahead_required": True,
            "beta_uses_prior_returns_only": True,
            "residual_z_uses_prior_residual_history_only": True,
            "entry_next_bar_open": True,
            "exit_fixed_hold_next_available_open": True,
            "portfolio_bps_uses_base_equity_denominator": True,
            "package_notional_cap_required": True,
            "btc_eth_excluded_as_traded_residual_legs": True,
        },
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()) and all(value is False for value in safety_permissions.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"strategy: {STRATEGY}")
    print(f"route_family: {ROUTE_FAMILY}")
    print(f"config_id: {CONFIG_ID}")
    print(f"symbol_file_count: {panel['symbol_file_count']}")
    print(f"btc_anchor_available: {str(panel['btc_anchor']['exists']).lower()}")
    print(f"eth_anchor_available: {str(panel['eth_anchor']['exists']).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
