from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "old_short_clean_room_direct_backtest_v2_error_audit_v1.json"
PRIOR_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "old_short_clean_room_direct_backtest_execution_v1.json"
PRIOR_EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "old_short_clean_room_direct_backtest_evaluator_v1.json"
PRIOR_CLOSURE_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "old_short_clean_room_direct_backtest_closure_v1.json"
THRESHOLD_CONTRACT_PATH = REPO_ROOT / "artifacts" / "old_short_clean_room" / "old_short_clean_room_runner_fixture_threshold_contract_v1.json"
SOURCE_REVIEW_PATH = REPO_ROOT / "artifacts" / "old_short" / "old_short_proxy_backtest_data_coverage_source_review_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_ERROR_AUDIT_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_V2_ERROR_AUDIT"
ROUTE_KEY = "old_short_clean_room_v1"
FAMILY_KEY = "old_short"
FAMILIES = ["blowoff_short", "mean_reversion_short"]
SIDE = "short"
REQUIRED_CANDLE_COLUMNS = {"ts", "open", "high", "low", "close", "volCcyQuote", "time"}


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


def walk_dicts(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_dicts(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_dicts(value)


def collect_recovered_okx_1m_sources(source_review: dict[str, Any]) -> list[dict[str, Any]]:
    by_symbol: dict[str, dict[str, Any]] = {}
    for item in walk_dicts(source_review):
        path_text = item.get("path") if isinstance(item, dict) else None
        if not isinstance(path_text, str):
            continue
        lowered = path_text.lower()
        if not (
            lowered.endswith(".csv")
            and "-usdt-swap_1m_" in lowered
            and "\\raw\\candles_long_1m\\" in lowered
        ):
            continue
        path = Path(path_text)
        symbol = path.name.split("-USDT-SWAP", 1)[0]
        if not symbol or symbol in by_symbol:
            continue
        exists = path.exists() and path.is_file()
        header: list[str] = []
        readable = False
        read_error = None
        if exists:
            try:
                with path.open("r", encoding="utf-8", newline="") as handle:
                    header = next(csv.reader(handle), [])
                readable = REQUIRED_CANDLE_COLUMNS.issubset(set(header))
            except Exception as exc:  # noqa: BLE001
                read_error = f"{type(exc).__name__}: {exc}"
        by_symbol[symbol] = {
            "symbol": symbol,
            "path": str(path),
            "exists": exists,
            "readable_okx_1m": readable,
            "header": header,
            "read_error": read_error,
            "size_bytes": path.stat().st_size if exists else None,
        }
    return sorted(by_symbol.values(), key=lambda row: row["symbol"])


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_old_short_clean_room_direct_backtest_v2_error_audit_v1.py",
        "?? artifacts/strategy_reviews/old_short_clean_room_direct_backtest_v2_error_audit_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    prior_execution = load_json(PRIOR_EXECUTION_PATH)
    prior_evaluator = load_json(PRIOR_EVALUATOR_PATH)
    prior_closure = load_json(PRIOR_CLOSURE_PATH)
    threshold_contract = load_json(THRESHOLD_CONTRACT_PATH)
    source_review = load_json(SOURCE_REVIEW_PATH)
    sources = collect_recovered_okx_1m_sources(source_review)
    readable_sources = [row for row in sources if row["readable_okx_1m"]]
    if not readable_sources:
        status = "BLOCKED_OLD_SHORT_CLEAN_ROOM_V2_DATA_SOURCE_MISSING"
        replacement = False
        next_allowed_step = "OLD_SHORT_CLEAN_ROOM_V2_DATA_SOURCE_BLOCKER_REVIEW"
    else:
        status = STATUS
        replacement = True
        next_allowed_step = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_EXECUTION_V2"

    metrics = prior_execution.get("backtest_execution", {}).get("execution_metrics", {})
    split_metrics = prior_execution.get("backtest_execution", {}).get("split_metrics", {})
    suspected_issues = [
        {
            "issue": "portfolio accounting likely used summed trade bps as headline return",
            "repair": "compute trade_pnl_usdt = 50 * net_return_fraction and portfolio_return_bps = sum_pnl / 1000 * 10000",
            "severity": "P0",
        },
        {
            "issue": "50 USDT notional and 1000 USDT base equity were not visible in headline return denominator",
            "repair": "fix notional and equity constants and audit every return denominator",
            "severity": "P0",
        },
        {
            "issue": "all threshold triggers were executed without proxy gate or overlap control",
            "repair": "run MODE A proxy gate conservative and MODE B no-gate upper-bound diagnostic",
            "severity": "P0",
        },
        {
            "issue": "same-symbol overlapping positions may have been allowed",
            "repair": "forbid same-symbol overlap in both V2 diagnostic modes",
            "severity": "P0",
        },
        {
            "issue": "global/family exposure caps were not applied in primary diagnostic mode",
            "repair": "MODE A enforces max global open positions 3 and max open positions per family 2",
            "severity": "P0",
        },
        {
            "issue": "standard 2024 validation split was empty because recovered OKX 1m data starts in 2025",
            "repair": "use available-data chronological split: first 30%, next 35%, final 35%",
            "severity": "P0",
        },
        {
            "issue": "symbol concentration was measured but not controlled",
            "repair": "evaluator requires top symbol share <= 0.25 for diagnostic_promising",
            "severity": "P1",
        },
        {
            "issue": "monthly accounting may have used summed trade bps rather than base-equity denominator",
            "repair": "monthly_portfolio_bps = monthly_pnl_usdt / 1000 * 10000",
            "severity": "P0",
        },
    ]
    corrected_assumptions = {
        "route_key": ROUTE_KEY,
        "family_key": FAMILY_KEY,
        "families": FAMILIES,
        "side": SIDE,
        "timeframe": "1m",
        "base_equity_usdt": 1000.0,
        "per_trade_notional_usdt": 50.0,
        "round_trip_cost_bps": 20.0,
        "entry_delay_minutes": 2,
        "hold_minutes": 120,
        "entry_policy": "signal close + 2 minutes, enter at next available 1m open after delay",
        "exit_policy": "fixed 120 minutes after entry, exit at next available 1m open after planned exit",
        "portfolio_accounting": "sum(trade_pnl_usdt) / base_equity_usdt * 10000",
        "monthly_accounting": "monthly_pnl_usdt / base_equity_usdt * 10000",
        "threshold_changes_allowed": False,
        "threshold_optimization_allowed": False,
        "exact_original_source_recovered": False,
        "exact_gate_replay_recovered": False,
        "clean_room_diagnostic_only": True,
    }
    diagnostic_modes = {
        "MODE_A_PROXY_GATE_CONSERVATIVE": {
            "primary_evaluation_mode": True,
            "same_symbol_overlap_forbidden": True,
            "max_global_open_positions": 3,
            "max_open_positions_per_family": 2,
            "short_only": True,
            "exact_gate_replay_claimed": False,
        },
        "MODE_B_NO_GATE_UPPER_BOUND_DIAGNOSTIC": {
            "primary_evaluation_mode": False,
            "same_symbol_overlap_forbidden": True,
            "max_global_open_positions": None,
            "max_open_positions_per_family": None,
            "short_only": True,
            "upper_bound_not_live_realistic": True,
            "eligible_for_diagnostic_promising_by_itself": False,
        },
    }
    threshold_review = {
        "path": str(THRESHOLD_CONTRACT_PATH),
        "loaded": True,
        "route_key": threshold_contract.get("fixture_threshold_contract_identity", {}).get("route_key"),
        "contract_complete": threshold_contract.get("contract_completeness", {}).get("contract_complete"),
        "family_threshold_count": threshold_contract.get("contract_completeness", {}).get("family_threshold_count"),
        "thresholds_changed": False,
        "thresholds_optimized": False,
    }
    artifact = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_old_short_clean_room_direct_backtest_v2_error_audit_v1",
        "route_key": ROUTE_KEY,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_audit": status_lines,
            "allowed_new_paths_at_audit": sorted(allowed_status),
            "unexpected_dirty_paths_at_audit": unexpected_status,
        },
        "source_artifacts": {
            "prior_execution": str(PRIOR_EXECUTION_PATH),
            "prior_evaluator": str(PRIOR_EVALUATOR_PATH),
            "prior_closure": str(PRIOR_CLOSURE_PATH),
            "threshold_contract": str(THRESHOLD_CONTRACT_PATH),
            "source_review": str(SOURCE_REVIEW_PATH),
        },
        "prior_suspicious_metric_comparison": {
            "prior_total_signals": metrics.get("total_signals"),
            "prior_executed_trades": metrics.get("executed_trades"),
            "prior_validation_net_bps": split_metrics.get("validation", {}).get("net_bps"),
            "prior_holdout_net_bps_sum_trade_like": split_metrics.get("holdout", {}).get("net_bps"),
            "prior_worst_month": metrics.get("worst_month"),
            "prior_top_symbol_concentration": metrics.get("symbol_concentration"),
            "prior_evaluator_result": prior_evaluator.get("result_classification"),
            "prior_closure_result": prior_closure.get("evaluator_result_classification_preserved"),
        },
        "suspected_error_audit": suspected_issues,
        "corrected_repaired_assumptions": corrected_assumptions,
        "diagnostic_modes_required": diagnostic_modes,
        "available_data_split_policy": {
            "standard_2024_validation_disallowed_if_empty": True,
            "if_data_starts_in_2025": "train_or_calibration first 30%, validation next 35%, holdout final 35%",
            "threshold_changes_from_train_or_calibration_allowed": False,
            "validation_closed_trades_below_30_forces_inconclusive": True,
        },
        "data_source_review": {
            "source_review_artifact": str(SOURCE_REVIEW_PATH),
            "candidate_okx_1m_source_count": len(sources),
            "readable_okx_1m_source_count": len(readable_sources),
            "readable_symbols": [row["symbol"] for row in readable_sources],
            "sample_sources": readable_sources[:20],
            "data_source_missing_blocker": not bool(readable_sources),
        },
        "threshold_contract_review": threshold_review,
        "next_allowed_step": next_allowed_step,
        "safety_permissions": {
            "backtest_execution_allowed_next": bool(readable_sources),
            "live_trading_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "capital_allocation_allowed_now": False,
            "real_orders_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": not unexpected_status,
            "prior_execution_loaded": True,
            "prior_evaluator_loaded": True,
            "prior_closure_loaded": True,
            "threshold_contract_loaded": True,
            "source_review_loaded": True,
            "data_source_can_be_discovered_from_old_short_artifacts": bool(readable_sources),
            "no_backtest_execution_in_audit_step": True,
            "no_network_used": True,
            "no_api_used": True,
            "no_runtime_live_capital": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
        },
        "replacement_checks_all_true": replacement,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {status}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"readable_okx_1m_source_count: {len(readable_sources)}")
    print(f"prior_suspected_issue_count: {len(suspected_issues)}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("backtest_execution_in_audit_step: false")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement).lower()}")
    return 0 if replacement else 2


if __name__ == "__main__":
    sys.exit(main())
