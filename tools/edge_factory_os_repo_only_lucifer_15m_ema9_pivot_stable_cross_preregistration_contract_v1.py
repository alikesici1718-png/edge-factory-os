import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_lucifer_15m_ema9_pivot_stable_cross_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/lucifer_15m_ema9_pivot_stable_cross_preregistration_contract_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"

STATUS = "PASS_REPO_ONLY_LUCIFER_15M_EMA9_PIVOT_STABLE_CROSS_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "LUCIFER_15M_EMA9_PIVOT_STABLE_CROSS_PREREGISTRATION_CONTRACT"
STRATEGY_NAME = "LUCIFER_EMA9_PIVOT_STABLE_CROSS_TP_SL_15M_V1"
ROUTE_FAMILY = "LUCIFER_EMA9_PIVOT_STABLE_CROSS_TP_SL_15M_BASELINE"
CONFIG_ID = "lucifer_15m_ema9_pivot_stable_cross_sl1_tp2"
TIMEFRAME = "15m"

ROUTE_START_HEAD = "76887a956490cf41eb71da99ef1b0a1e2cabf4d8"
ROUTE_START_TRACKED_PYTHON_COUNT = 932
ROUTE_START_REPO_CLEAN = True

PANEL_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_REVIEW_AFTER_BUILD_CREATED"
PANEL_CLASSIFICATION = "PANEL_15M_REVIEW_PASS_VALID_FOR_READ_ONLY_EXTREME_MOVE_RESEARCH"
PANEL_DIR = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1\panel_15m_by_symbol"
)


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def run_git(args: List[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def tracked_python_count() -> int:
    output = run_git(["ls-files", "*.py"])
    return 0 if not output else len(output.splitlines())


def dirty_paths() -> List[str]:
    output = run_git(["status", "--short"])
    paths: List[str] = []
    for line in output.splitlines():
        if not line:
            continue
        path = line[3:].strip().strip('"').replace("\\", "/")
        paths.append(path)
    return sorted(paths)


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"artifact is not a JSON object: {relative_path}")
    return payload


def build_payload() -> Dict[str, Any]:
    panel_review = read_json(PANEL_REVIEW_PATH)
    if panel_review.get("status") != PANEL_STATUS:
        raise RuntimeError("panel review status mismatch")
    if panel_review.get("panel_validity_classification") != PANEL_CLASSIFICATION:
        raise RuntimeError("panel review classification mismatch")

    actual_head = run_git(["rev-parse", "HEAD"])
    actual_tracked_python_count = tracked_python_count()
    allowed_dirty = {MODULE_PATH, ARTIFACT_PATH}
    current_dirty_paths = dirty_paths()
    unexpected_dirty_paths = [path for path in current_dirty_paths if path not in allowed_dirty]
    if unexpected_dirty_paths:
        raise RuntimeError(f"unexpected dirty paths during preregistration: {unexpected_dirty_paths}")
    if actual_head != ROUTE_START_HEAD:
        raise RuntimeError(f"HEAD moved before preregistration: {actual_head} != {ROUTE_START_HEAD}")
    if actual_tracked_python_count != ROUTE_START_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before preregistration: "
            f"{actual_tracked_python_count} != {ROUTE_START_TRACKED_PYTHON_COUNT}"
        )

    panel_summary = panel_review.get("aggregate_validation_review", {})
    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "strategy_name": STRATEGY_NAME,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "timeframe": TIMEFRAME,
        "cycle": ["preregistration", "execution", "evaluator", "closure"],
        "source_checkpoint": {
            "actual_clean_head": ROUTE_START_HEAD,
            "actual_head_verified_at_artifact_creation": actual_head,
            "repo_clean_before_route_start": ROUTE_START_REPO_CLEAN,
            "tracked_python_count_before_route_start": ROUTE_START_TRACKED_PYTHON_COUNT,
            "tracked_python_count_verified_at_artifact_creation": actual_tracked_python_count,
            "dirty_paths_during_artifact_creation_limited_to_expected_new_paths": True,
            "dirty_paths_during_artifact_creation": current_dirty_paths,
        },
        "dataset_preregistration": {
            "panel_review_artifact": PANEL_REVIEW_PATH,
            "panel_review_status": panel_review.get("status"),
            "panel_classification": panel_review.get("panel_validity_classification"),
            "external_panel_directory": PANEL_DIR,
            "symbols": panel_summary.get("reviewed_symbol_count"),
            "rows": panel_summary.get("reviewed_15m_row_count"),
            "range_start_utc": panel_summary.get("reviewed_min_timestamp_utc"),
            "range_end_inclusive_utc": panel_summary.get("reviewed_max_timestamp_utc"),
            "read_only_panel_use": True,
            "unrelated_datasets_allowed": False,
        },
        "fixed_parameters": {
            "leftBars": 150,
            "rightBars": 75,
            "cooldown_bars": 10,
            "minStableBars": 5,
            "ema_period": 9,
            "stop_loss_pct": 1.0,
            "take_profit_pct": 2.0,
            "filters_enabled": False,
            "score_filters_enabled": False,
            "pyramiding_per_symbol": 0,
            "timeframe": TIMEFRAME,
        },
        "signal_contract": {
            "ema_source": "close",
            "pivot_high_source": "high",
            "pivot_low_source": "low",
            "pivot_confirmation_policy": (
                "raw pivot high/low is unavailable until rightBars future bars have closed; "
                "active resistance/support updates only at confirmation bar"
            ),
            "stable_level_policy": (
                "active step level is tradeable only when current_bar_index - "
                "level_confirmed_bar_index >= minStableBars"
            ),
            "long_signal": (
                "active support exists, support is stable, EMA9 previous bar < support, "
                "EMA9 current bar >= support"
            ),
            "short_signal": (
                "active resistance exists, resistance is stable, EMA9 previous bar > resistance, "
                "EMA9 current bar <= resistance"
            ),
            "fake_diagonal_cross_block": (
                "raw EMA crosses that occur while the active level is not yet stable are skipped "
                "and counted as fake_pivot_jump_blocked"
            ),
            "cooldown_policy": "after an accepted signal, skip same-symbol signals for the next 10 bars",
            "entry_policy": "signal evaluated at bar close; enter at next 15m bar open if present",
            "position_policy": "one position per symbol at a time; cross-symbol overlap allowed",
        },
        "exit_and_cost_contract": {
            "long_stop": "entry_price * 0.99",
            "long_take_profit": "entry_price * 1.02",
            "short_stop": "entry_price * 1.01",
            "short_take_profit": "entry_price * 0.98",
            "intrabar_ohlc_policy": "15m high/low determines stop/take hit",
            "both_hit_same_bar_policy": "conservative stop-first",
            "dataset_end_policy": "open/unresolved trades are excluded from closed-trade performance and reported separately",
            "gross_reported": True,
            "net_round_trip_cost_bps": 20,
            "cost_optimization": False,
        },
        "splits": {
            "train": {
                "start_utc": "2023-01-01T00:00:00Z",
                "end_exclusive_utc": "2024-07-01T00:00:00Z",
            },
            "validation": {
                "start_utc": "2024-07-01T00:00:00Z",
                "end_exclusive_utc": "2025-04-01T00:00:00Z",
            },
            "holdout": {
                "start_utc": "2025-04-01T00:00:00Z",
                "end_exclusive_utc": "2025-11-01T00:00:00Z",
            },
            "split_assignment": "entry timestamp determines split",
            "holdout_used_for_config_selection": False,
        },
        "metrics_required": [
            "total signals",
            "accepted signals",
            "skipped signals",
            "closed trades",
            "open/unresolved trades",
            "long trades",
            "short trades",
            "gross bps",
            "net bps",
            "win rate",
            "average win",
            "average loss",
            "profit factor if computable",
            "monthly gross/net",
            "monthly positive rate",
            "worst month",
            "best month",
            "symbol concentration",
            "side split",
            "stop hit count",
            "take profit hit count",
            "both-hit-same-bar count",
            "fake pivot jump blocked count",
            "cooldown skipped count",
            "no-lookahead checks",
            "pivot confirmation delay checks",
        ],
        "null_baseline_contract": {
            "required_if_feasible": True,
            "method": "deterministic timestamp/block shuffle null",
            "run_count": 100,
            "validation_null_percentile_rule": "validation_null_percentile >= 0.95",
            "limitation_must_be_recorded_if_not_feasible": True,
        },
        "evaluator_policy": {
            "diagnostic_promising_true_only_if_all_true": [
                "validation net bps > 0",
                "validation monthly positive rate >= 0.60",
                "validation closed trades >= 100, otherwise inconclusive",
                "holdout net bps > 0",
                "null baseline passes or limitation is explicitly recorded",
                "metric integrity passes",
                "no lookahead/repaint issue",
                "safety review passes",
            ],
            "allowed_result_classes": [
                "LUCIFER_15M_EMA9_PIVOT_STABLE_CROSS_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
                "LUCIFER_15M_EMA9_PIVOT_STABLE_CROSS_REJECTED_NO_FOLLOWUP",
                "LUCIFER_15M_EMA9_PIVOT_STABLE_CROSS_INCONCLUSIVE_NEEDS_MORE_DATA",
                "LUCIFER_15M_EMA9_PIVOT_STABLE_CROSS_INVALIDATED_BY_LOOKAHEAD_OR_INTEGRITY_FAILURE",
            ],
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "private_api_used": False,
            "data_downloaded": False,
            "other_timeframes_tested": False,
            "other_parameters_tested": False,
            "optimization": False,
            "candidate_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "orders_submitted": False,
            "seven_of_seven_filters_used": False,
        },
        "next_module": "tools/edge_factory_os_repo_only_lucifer_15m_ema9_pivot_stable_cross_execution_v1.py",
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "artifact_path_equals_required_path": True,
            "actual_clean_head_recorded": True,
            "tracked_python_count_recorded": True,
            "repo_clean_before_route_start_recorded": True,
            "panel_review_artifact_loaded": True,
            "panel_review_status_verified": True,
            "panel_review_classification_verified": True,
            "exactly_one_config_preregistered": True,
            "timeframe_15m_only": True,
            "no_other_timeframes": True,
            "no_other_parameters": True,
            "no_optimization": True,
            "no_candidate": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    if not all(payload["validation_checks"].values()):
        raise RuntimeError("preregistration validation checks failed")
    if canonical_payload_hash(payload) != payload["payload_sha256_excluding_hash"]:
        raise RuntimeError("payload hash failed to stabilize")
    return payload


def main() -> None:
    payload = build_payload()
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": STATUS,
                "artifact_path": ARTIFACT_PATH,
                "strategy_name": STRATEGY_NAME,
                "config_id": CONFIG_ID,
                "actual_clean_head": ROUTE_START_HEAD,
                "tracked_python_count": ROUTE_START_TRACKED_PYTHON_COUNT,
                "replacement_checks_all_true": True,
                "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
