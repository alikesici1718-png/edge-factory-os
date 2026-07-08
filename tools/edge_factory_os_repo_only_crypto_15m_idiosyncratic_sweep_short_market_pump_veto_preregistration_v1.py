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
V3_EXECUTION = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1.json"
V3_NULL_AUDIT = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_short_only_v3_null_failure_audit_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_preregistration_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_PREREGISTRATION_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_PREREGISTRATION"
STRATEGY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_V1"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_v1"
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
        "?? tools/edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_market_pump_veto_preregistration_v1.py",
        "?? artifacts/research_preregistrations/crypto_15m_idiosyncratic_sweep_short_market_pump_veto_preregistration_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    panel_review = load_json(PANEL_REVIEW)
    v3_execution = load_json(V3_EXECUTION)
    v3_null_audit = load_json(V3_NULL_AUDIT)
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
        "long_entries_enabled": False,
    }
    market_pump_veto = {
        "name": "MARKET_PUMP_VETO",
        "applied_at": "signal timestamp before accepting a short trade",
        "thresholds_are_structural_round_numbers_not_optimized": True,
        "veto_true_if_any": [
            "btc_ret_4h > 0.015 and eth_ret_4h > 0.015",
            "btc_ret_24h > 0.04 and eth_ret_24h > 0.04",
            "pump_breadth > 0.35",
            "median_universe_ret_4h > 0.01",
        ],
        "pump_breadth_definition": "share of eligible panel symbols with 4h return > +0.02",
        "median_universe_ret_4h_definition": "median of current/past 4h returns across eligible panel symbols",
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_market_pump_veto_preregistration_v1",
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
            "panel_review": str(PANEL_REVIEW),
            "v3_execution": str(V3_EXECUTION),
            "v3_null_failure_audit": str(V3_NULL_AUDIT),
        },
        "prior_failure_evidence": {
            "v3_validation_net_bps": v3_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "v3_holdout_net_bps": v3_execution.get("split_metrics", {}).get("holdout", {}).get("portfolio_net_bps"),
            "v3_null_percentile": v3_execution.get("null_baseline", {}).get("validation_percentile"),
            "v3_null_pass": v3_execution.get("null_baseline", {}).get("null_pass"),
            "null_audit_v4_decision": v3_null_audit.get("v4_decision", {}).get("v4_direction_classification"),
            "null_audit_effect_size": v3_null_audit.get("effect_size_audit", {}).get("effect_size_classification"),
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
            "hypothesis": "Shorting idiosyncratic alt overextension may work only when the broad crypto market is not in a strong pump regime.",
            "inherited_v3_parameters": fixed_parameters,
            "new_structural_filter": market_pump_veto,
            "short_signal_stack": [
                "residual z >= +3.5",
                "48h high sweep and failed close",
                "confirmation bar required",
                "cost-aware gate",
                "stop-risk quality gate",
                "market pump veto false",
            ],
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
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_REJECTED_NO_FOLLOWUP",
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_INCONCLUSIVE_NEEDS_MORE_DATA",
                    "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_MARKET_PUMP_VETO_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE",
                ],
            },
        },
        "safety_permissions": {
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "live_permission_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "capital_permission_allowed_now": False,
            "real_orders_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": not unexpected_status,
            "panel_review_loaded": True,
            "v3_execution_loaded": True,
            "v3_null_audit_loaded": True,
            "panel_file_count_verified_81": len(symbols) == 81,
            "btc_anchor_available": btc["exists"],
            "eth_anchor_available": eth["exists"],
            "no_parameter_grid": True,
            "no_optimization": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "no_network_used": True,
            "no_api_used": True,
        },
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["replacement_checks_all_true"] = all(artifact["validation_checks"].values()) and all(
        value is False for value in artifact["safety_permissions"].values()
    )
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"strategy: {STRATEGY}")
    print(f"route_family: {ROUTE_FAMILY}")
    print(f"config_id: {CONFIG_ID}")
    print(f"symbol_file_count: {len(symbols)}")
    print("market_pump_veto_preregistered: true")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
