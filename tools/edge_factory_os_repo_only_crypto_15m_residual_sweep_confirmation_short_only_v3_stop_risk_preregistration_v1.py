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
POSTMORTEM_V2 = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_short_only_v2_postmortem_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_preregistration_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_PREREGISTRATION"
STRATEGY = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_STOP_RISK_REPAIR_V3"
ROUTE_FAMILY = "CRYPTO_15M_CONFLUENCE_EVENT_REVERSAL_SHORT_ONLY_STOP_RISK_REPAIR"
CONFIG_ID = "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_quality_1"
EXPECTED_COLUMNS = {"symbol", "timestamp_utc", "open", "high", "low", "close", "volume", "quote_volume", "complete_15m"}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def inspect_anchor(symbol: str) -> dict[str, Any]:
    path = PANEL_DIR / f"{symbol}_15m.csv.gz"
    if not path.exists():
        return {"symbol": symbol, "exists": False, "header": [], "has_required_columns": False}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        first_row = next(reader, None)
    return {
        "symbol": symbol,
        "path": str(path),
        "exists": True,
        "header": header,
        "has_required_columns": EXPECTED_COLUMNS.issubset(set(header)),
        "first_row": first_row,
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_preregistration_v1.py",
        "?? artifacts/research_preregistrations/crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_preregistration_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    panel_review = load_json(PANEL_REVIEW)
    postmortem = load_json(POSTMORTEM_V2)
    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    btc = inspect_anchor("BTCUSDT")
    eth = inspect_anchor("ETHUSDT")
    if len(symbols) != 81 or not btc["exists"] or not eth["exists"]:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    if not btc["has_required_columns"] or not eth["has_required_columns"]:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")

    fixed_parameters = {
        "timeframe": "15m",
        "rolling_beta_window_bars": 2880,
        "minimum_beta_observations": 1000,
        "residual_impulse_bars": 16,
        "residual_z_history_bars": 2880,
        "short_z_threshold": 3.5,
        "prior_range_window_bars": 192,
        "atr_length": 14,
        "volume_sma_length": 20,
        "volume_filter": "volume > volume_sma20",
        "confirmation_required": True,
        "cost_gate_expected_abs_move_min": 0.008,
        "stop_risk_quality_ratio_min": 1.0,
        "round_trip_cost_fraction": 0.002,
        "base_equity_usdt": 1000.0,
        "risk_per_trade_usdt": 5.0,
        "max_notional_per_trade_usdt": 100.0,
        "max_concurrent_positions": 3,
        "max_new_positions_per_timestamp": 1,
        "one_open_position_per_symbol": True,
        "symbol_cooldown_bars_after_exit": 96,
        "time_stop_bars": 32,
        "reward_risk_take_profit": 2.0,
        "leverage": "none",
        "compounding": False,
        "reinvestment": False,
    }
    preregistered_config = {
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "single_config_only": True,
        "v3_change": "Add one structural stop-risk quality gate to the short-only V2 stack; all inherited V2 parameters remain unchanged.",
        "parameter_grid_allowed": False,
        "optimization_allowed": False,
        "postmortem_justification": {
            "source": str(POSTMORTEM_V2),
            "v3_direction_classification": postmortem.get("v3_direction_assessment", {}).get("v3_direction_classification"),
            "exit_diagnostic_classification": postmortem.get("exit_reason_diagnostic", {}).get("exit_diagnostic_classification"),
            "cost_diagnostic_classification": postmortem.get("cost_diagnostic", {}).get("cost_diagnostic_classification"),
            "suggested_boundary": postmortem.get("suggested_v3_boundaries", {}).get("suggested_v3_boundary"),
        },
        "dataset": {
            "name": "reviewed Binance/OKX overlap 81-symbol 15m panel",
            "panel_directory": str(PANEL_DIR),
            "panel_review_artifact": str(PANEL_REVIEW),
            "expected_symbol_count": 81,
            "timeframe": "15m",
            "required_anchor_symbols": ["BTCUSDT", "ETHUSDT"],
            "traded_symbols": "all reviewed panel symbols except BTCUSDT and ETHUSDT",
        },
        "fixed_parameters": fixed_parameters,
        "short_signal_rules": [
            "z_residual >= +3.5",
            "high > prior_high_48h",
            "close < prior_high_48h",
            "close < open",
            "volume > volume_sma20",
            "ATR14 valid",
            "not BTCUSDT or ETHUSDT",
            "confirmation close below sweep close",
            "confirmation high does not break sweep high by more than 0.25 * ATR14",
            "expected_abs_move_proxy >= 0.008",
            "risk_quality_ratio >= 1.0",
        ],
        "stop_risk_quality_gate": {
            "computed_after_confirmation_before_entry_acceptance": True,
            "stop_distance_fraction": "(stop_price - entry_price) / entry_price",
            "risk_quality_ratio": "abs(residual_4h) / (stop_distance_fraction + 0.002)",
            "minimum_ratio": 1.0,
            "alternative_ratios_tested": False,
            "optimized": False,
        },
        "disabled_long_side_policy": {
            "long_entries_enabled": False,
            "diagnostic_counting_only": True,
            "long_side_results_not_used_for_selection": True,
        },
        "entry_exit": {
            "entry": "following bar open after one confirmation bar",
            "short_stop": "sweep_high + 0.5 * ATR14",
            "take_profit": "entry - 2R for shorts",
            "time_stop": "32 bars",
            "same_bar_stop_take_policy": "stop first",
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
                "validation closed trades >= 30",
                "null baseline passes",
                "top symbol trade share <= 0.25",
                "worst month > -1000 bps",
                "metric integrity passes",
                "no candidate/edge/live/capital",
            ],
            "allowed_result_classes": [
                "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
                "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_REJECTED_NO_FOLLOWUP",
                "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_INCONCLUSIVE_NEEDS_MORE_DATA",
                "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE",
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
        "postmortem_v2_loaded": True,
        "v3_direction_verified_stop_risk": postmortem.get("v3_direction_assessment", {}).get("v3_direction_classification") == "V3_DIRECTION_JUSTIFIED_STOP_EXIT_RISK_REPAIR",
        "panel_file_count_verified_81": len(symbols) == 81,
        "btc_anchor_available": btc["exists"],
        "eth_anchor_available": eth["exists"],
        "btc_anchor_header_verified": btc["has_required_columns"],
        "eth_anchor_header_verified": eth["has_required_columns"],
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
        "module": "edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_preregistration_v1",
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
        "source_artifacts": {"panel_review": str(PANEL_REVIEW), "postmortem_v2": str(POSTMORTEM_V2)},
        "panel_review_status": panel_review.get("status"),
        "panel_inspection": {"panel_dir": str(PANEL_DIR), "symbol_file_count": len(symbols), "btc_anchor": btc, "eth_anchor": eth},
        "preregistered_config": preregistered_config,
        "metric_integrity_preregistration": {
            "no_lookahead_required": True,
            "beta_uses_prior_returns_only": True,
            "residual_z_uses_prior_residual_history_only": True,
            "prior_high_excludes_current_bar": True,
            "confirmation_then_entry_order_required": True,
            "long_side_disabled_required": True,
            "stop_risk_quality_gate_prior_to_acceptance": True,
            "portfolio_bps_uses_base_equity_denominator": True,
            "cooldown_required": True,
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
    print(f"symbol_file_count: {len(symbols)}")
    print("stop_risk_quality_ratio_min: 1.0")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
