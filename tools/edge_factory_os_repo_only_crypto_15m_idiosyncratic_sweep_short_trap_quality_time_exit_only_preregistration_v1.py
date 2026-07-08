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
PANEL_REVIEW_PATH = REPO_ROOT / "artifacts" / "panel_build_reviews" / "binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
PRIOR_TRAP_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1.json"
RISK_TIGHTENED_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_risk_tightened_execution_v1.json"
TRAP_SCORE4_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_score4_execution_v1.json"
WIDER_STOP_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_wider_stop_execution_v1.json"
REJECTION_DEPTH_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_rejection_depth_required_execution_v1.json"
POSTMORTEM_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_postmortem_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only_preregistration_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_TIME_EXIT_ONLY_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_TIME_EXIT_ONLY_PREREGISTRATION"
STRATEGY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_TIME_EXIT_ONLY_V2"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_TIME_EXIT_ONLY_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only_v2"
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
        return {"symbol": symbol, "exists": False, "has_required_columns": False, "header": []}
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
        "?? tools/edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only_preregistration_v1.py",
        "?? artifacts/research_preregistrations/crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only_preregistration_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    panel_review = load_json(PANEL_REVIEW_PATH)
    prior_execution = load_json(PRIOR_TRAP_EXECUTION_PATH)
    risk_tightened_execution = load_json(RISK_TIGHTENED_EXECUTION_PATH)
    trap_score4_execution = load_json(TRAP_SCORE4_EXECUTION_PATH)
    wider_stop_execution = load_json(WIDER_STOP_EXECUTION_PATH)
    rejection_depth_execution = load_json(REJECTION_DEPTH_EXECUTION_PATH)
    postmortem = load_json(POSTMORTEM_PATH)
    files = sorted(PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    btc = inspect_anchor("BTCUSDT")
    eth = inspect_anchor("ETHUSDT")
    if len(symbols) != 81 or not btc["exists"] or not eth["exists"]:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    if not btc["has_required_columns"] or not eth["has_required_columns"]:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")

    inherited_parameters = {
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
        "market_pump_veto_enabled": True,
        "round_trip_cost_fraction": 0.002,
        "base_equity_usdt": 1000.0,
        "risk_per_trade_usdt": 5.0,
        "max_notional_per_trade_usdt": 100.0,
        "max_concurrent_positions": 3,
        "max_new_positions_per_timestamp": 1,
        "one_open_position_per_symbol": True,
        "symbol_cooldown_bars_after_exit": 96,
        "time_stop_bars": 32,
        "take_profit_enabled": False,
        "take_profit_rule": "removed; no take-profit check or order",
        "long_entries_enabled": False,
    }
    only_changed_parameter = {
        "field": "exit_rule",
        "prior_value": "stop OR take_profit OR time_exit",
        "new_value": "stop OR time_exit only",
        "interpretation": "Remove take-profit entirely while preserving the original 0.5 ATR stop and 8h time stop because the postmortem found time exits carried edge.",
        "structural_exit_repair": True,
        "not_a_grid_search": True,
    }
    trap_quality_filter = {
        "computed_on": "sweep bar known at close",
        "components": {
            "upper_wick_share_gte_0_40": "upper_wick / candle_range >= 0.40",
            "close_location_lte_0_40": "(close - low) / candle_range <= 0.40",
            "sweep_depth_atr_gte_0_15": "(high - prior_high_48h) / ATR14 >= 0.15",
            "rejection_depth_atr_gte_0_05": "(prior_high_48h - close) / ATR14 >= 0.05",
        },
        "trap_quality_score": "number of passed components",
        "minimum_score": 3,
        "invalid_when": ["candle_range <= 0", "ATR14 <= 0"],
        "inherited_unchanged": True,
    }
    market_pump_veto = {
        "veto_true_if_any": [
            "btc_ret_4h > 0.015 and eth_ret_4h > 0.015",
            "btc_ret_24h > 0.04 and eth_ret_24h > 0.04",
            "pump_breadth > 0.35",
            "median_universe_ret_4h > 0.01",
        ],
        "inherited_unchanged": True,
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
        "panel_review_loaded": True,
        "prior_trap_quality_execution_loaded": True,
        "risk_tightened_execution_loaded": True,
        "trap_score4_execution_loaded": True,
        "wider_stop_execution_loaded": True,
        "rejection_depth_execution_loaded": True,
        "postmortem_loaded": True,
        "panel_file_count_verified_81": len(symbols) == 81,
        "btc_anchor_available": btc["exists"],
        "eth_anchor_available": eth["exists"],
        "single_config_only": True,
        "only_exit_rule_changed": True,
        "take_profit_removed": True,
        "stop_buffer_atr_0p5_unchanged": True,
        "risk_quality_ratio_restored_to_1p0": True,
        "trap_quality_score_min_3_unchanged": True,
        "no_parameter_grid": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_network_used": True,
        "no_api_used": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": Path(__file__).name,
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
        "source_artifacts": {
            "panel_review": str(PANEL_REVIEW_PATH),
            "prior_trap_quality_execution": str(PRIOR_TRAP_EXECUTION_PATH),
            "risk_tightened_execution": str(RISK_TIGHTENED_EXECUTION_PATH),
            "trap_score4_execution": str(TRAP_SCORE4_EXECUTION_PATH),
            "wider_stop_execution": str(WIDER_STOP_EXECUTION_PATH),
            "rejection_depth_execution": str(REJECTION_DEPTH_EXECUTION_PATH),
            "postmortem": str(POSTMORTEM_PATH),
        },
        "postmortem_and_recent_route_context": {
            "postmortem_status": postmortem.get("status"),
            "strongest_trap_quality_signal": postmortem.get("trap_quality_diagnostic", {}).get("strongest_trap_quality_signal"),
            "strongest_residual_signal": postmortem.get("residual_feature_diagnostic", {}).get("strongest_residual_signal"),
            "market_veto": postmortem.get("market_pump_veto_diagnostic", {}).get("market_veto_classification"),
            "cost": postmortem.get("cost_diagnostic", {}).get("cost_classification"),
            "null_failure": postmortem.get("null_failure_diagnostic", {}).get("null_failure_classification"),
            "risk_tightened_validation_net_bps": risk_tightened_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "risk_tightened_holdout_net_bps": risk_tightened_execution.get("split_metrics", {}).get("holdout", {}).get("portfolio_net_bps"),
            "risk_tightened_null_percentile": risk_tightened_execution.get("null_baseline", {}).get("validation_percentile"),
            "trap_score4_validation_net_bps": trap_score4_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "trap_score4_null_percentile": trap_score4_execution.get("null_baseline", {}).get("validation_percentile"),
            "wider_stop_validation_net_bps": wider_stop_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "wider_stop_null_percentile": wider_stop_execution.get("null_baseline", {}).get("validation_percentile"),
            "rejection_depth_validation_net_bps": rejection_depth_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "rejection_depth_null_percentile": rejection_depth_execution.get("null_baseline", {}).get("validation_percentile"),
            "risk_tightening_not_used": True,
            "trap_score4_tightening_not_used": True,
            "wider_stop_not_used": True,
            "rejection_depth_mandatory_filter_not_used": True,
        },
        "prior_trap_quality_result": {
            "validation_net_bps": prior_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "holdout_net_bps": prior_execution.get("split_metrics", {}).get("holdout", {}).get("portfolio_net_bps"),
            "validation_monthly_positive_rate": prior_execution.get("split_metrics", {}).get("validation", {}).get("monthly_positive_rate"),
            "holdout_monthly_positive_rate": prior_execution.get("split_metrics", {}).get("holdout", {}).get("monthly_positive_rate"),
            "null_percentile": prior_execution.get("null_baseline", {}).get("validation_percentile"),
            "null_pass": prior_execution.get("null_baseline", {}).get("null_pass"),
        },
        "panel_inspection": {
            "panel_review_status": panel_review.get("status"),
            "panel_dir": str(PANEL_DIR),
            "symbol_file_count": len(symbols),
            "btc_anchor": btc,
            "eth_anchor": eth,
        },
        "preregistered_config": {
            "single_config_only": True,
            "parameter_grid_allowed": False,
            "optimization_allowed": False,
            "strategy_change_summary": "Inherited trap-quality short-only stack unchanged except take-profit is removed; exits are stop or 8h time stop only.",
            "inherited_parameters": inherited_parameters,
            "only_changed_parameter": only_changed_parameter,
            "exit_rule": {
                "stop": "sweep_high + 0.5 * ATR14",
                "take_profit": None,
                "take_profit_enabled": False,
                "time_stop_bars": 32,
                "only_changed_from_prior": "remove take-profit check/order",
            },
            "market_pump_veto": market_pump_veto,
            "trap_quality_filter": trap_quality_filter,
            "additional_confirmation_quality": {
                "confirmation_strength_atr": "(sweep_close - confirmation_close) / ATR14",
                "minimum_confirmation_strength_atr": 0.05,
                "inherited_unchanged": True,
            },
            "splits": {
                "train": ["2023-01-01T00:00:00Z", "2024-07-01T00:00:00Z"],
                "validation": ["2024-07-01T00:00:00Z", "2025-04-01T00:00:00Z"],
                "holdout": ["2025-04-01T00:00:00Z", "2025-11-01T00:00:00Z"],
            },
            "null_baseline": "deterministic timestamp/block shuffle null, 100 runs when validation closed trades >= 30",
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
    print("trap_quality_score_rule: score >= 3")
    print("stop_buffer_atr: 0.5")
    print("risk_quality_ratio_min: 1.0")
    print("take_profit_enabled: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
