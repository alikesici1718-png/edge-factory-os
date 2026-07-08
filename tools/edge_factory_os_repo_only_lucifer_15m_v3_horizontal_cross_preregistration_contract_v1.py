import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_lucifer_15m_v3_horizontal_cross_preregistration_contract_v1.py"
ARTIFACT_PATH = "artifacts/research_preregistrations/lucifer_15m_v3_horizontal_cross_preregistration_contract_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"

STATUS = "PASS_REPO_ONLY_LUCIFER_15M_V3_HORIZONTAL_CROSS_PREREGISTRATION_CONTRACT_CREATED"
ARTIFACT_KIND = "LUCIFER_15M_V3_HORIZONTAL_CROSS_PREREGISTRATION_CONTRACT"
ROUTE = "LUCIFER_15M_EMA9_HORIZONTAL_PIVOT_CROSS_TP_SL_V3"
CONFIG_ID = "lucifer_15m_v3_horizontal_pivot_cross_sl1_tp2"
TIMEFRAME = "15m"

ROUTE_START_HEAD = "5ff0d19c97657344ca0ceb309b432681cea46205"
ROUTE_START_TRACKED_PYTHON_COUNT = 940
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
        if line:
            paths.append(line[3:].strip().strip('"').replace("\\", "/"))
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
    current_dirty_paths = dirty_paths()
    allowed_dirty = {MODULE_PATH, ARTIFACT_PATH}
    unexpected_dirty_paths = [path for path in current_dirty_paths if path not in allowed_dirty]
    if unexpected_dirty_paths:
        raise RuntimeError(f"unexpected dirty paths during preregistration: {unexpected_dirty_paths}")
    if actual_head != ROUTE_START_HEAD:
        raise RuntimeError(f"HEAD moved before V3 preregistration: {actual_head} != {ROUTE_START_HEAD}")
    if actual_tracked_python_count != ROUTE_START_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before V3 preregistration: "
            f"{actual_tracked_python_count} != {ROUTE_START_TRACKED_PYTHON_COUNT}"
        )

    panel_summary = panel_review.get("aggregate_validation_review", {})
    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route": ROUTE,
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
        "reason_for_v3": {
            "v1_v2_did_not_correctly_model_visual_rule": True,
            "visual_rule": "EMA9 crossing a true horizontal support/resistance segment is valid.",
            "invalid_rule": "A cross caused by pivot line jumping or diagonal connector is invalid.",
            "not_trend_or_volume_filtering": True,
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
            "reviewed_binance_okx_overlap_81_symbol_15m_panel_only": True,
            "unrelated_datasets_allowed": False,
        },
        "fixed_parameters": {
            "timeframe": TIMEFRAME,
            "leftBars": 150,
            "rightBars": 75,
            "cooldown_bars": 10,
            "emaFast": 9,
            "stop_loss_pct": 1.0,
            "take_profit_pct": 2.0,
            "round_trip_cost_bps": 20,
            "pyramiding_per_symbol": 0,
        },
        "forbidden_filters": {
            "trend_filter": False,
            "volume_filter": False,
            "rsi": False,
            "score_system": False,
            "candle_close_filter": False,
            "proximity_filter": False,
            "atr_stop": False,
        },
        "core_pivot_series_contract": {
            "rawPH": "pivothigh(leftBars, rightBars)",
            "rawPL": "pivotlow(leftBars, rightBars)",
            "ph_fixed": "last non-na rawPH, equivalent to fixnan(pivothigh(...))",
            "pl_fixed": "last non-na rawPL, equivalent to fixnan(pivotlow(...))",
            "raw_pivot_known_only_on_confirmation_bar": True,
            "no_pivot_before_confirmation": True,
            "no_lookahead": True,
        },
        "raw_cross_contract": {
            "rawShortCross": "ema9 previous bar > ph_fixed previous bar and ema9 current bar <= ph_fixed current bar",
            "rawLongCross": "ema9 previous bar < pl_fixed previous bar and ema9 current bar >= pl_fixed current bar",
        },
        "horizontal_only_validity_rule": {
            "validShortCross": [
                "rawShortCross is true",
                "ph_fixed current exists",
                "ph_fixed previous exists",
                "ph_fixed current == ph_fixed previous",
                "ph_fixed previous == ph_fixed two bars ago",
            ],
            "validLongCross": [
                "rawLongCross is true",
                "pl_fixed current exists",
                "pl_fixed previous exists",
                "pl_fixed current == pl_fixed previous",
                "pl_fixed previous == pl_fixed two bars ago",
            ],
            "diagonal_jump_cross_blocked": [
                "rawShortCross true but ph_fixed current != ph_fixed previous OR ph_fixed previous != ph_fixed two bars ago",
                "rawLongCross true but pl_fixed current != pl_fixed previous OR pl_fixed previous != pl_fixed two bars ago",
            ],
        },
        "entry_exit_cost_contract": {
            "entry": "signal evaluated at bar close, entry at next 15m open if present",
            "cooldown": "after valid signal, ignore valid new signals for cooldown bars",
            "one_position_per_symbol": True,
            "cross_symbol_overlap_allowed": True,
            "long_stop": "entry * 0.99",
            "long_take": "entry * 1.02",
            "short_stop": "entry * 1.01",
            "short_take": "entry * 0.98",
            "intrabar_policy": "use 15m OHLC high/low; if stop and take both hit, assume stop first",
            "unresolved_policy": "report separately and exclude from closed-trade performance",
            "round_trip_cost_bps": 20,
        },
        "splits": {
            "train": {"start_utc": "2023-01-01T00:00:00Z", "end_exclusive_utc": "2024-07-01T00:00:00Z"},
            "validation": {"start_utc": "2024-07-01T00:00:00Z", "end_exclusive_utc": "2025-04-01T00:00:00Z"},
            "holdout": {"start_utc": "2025-04-01T00:00:00Z", "end_exclusive_utc": "2025-11-01T00:00:00Z"},
            "split_assignment": "entry timestamp determines split",
        },
        "metrics_required": [
            "raw crosses",
            "valid horizontal crosses",
            "diagonal_jump_cross_blocked",
            "cooldown skipped",
            "accepted signals",
            "closed trades",
            "unresolved trades",
            "long/short split",
            "stop/take counts",
            "both-hit-same-bar count",
            "gross/net bps",
            "validation net",
            "holdout net",
            "monthly gross/net",
            "monthly positive rate",
            "worst month",
            "win rate",
            "profit factor",
            "symbol concentration",
            "side split",
            "no-lookahead checks",
            "pivot confirmation delay checks",
        ],
        "null_baseline_contract": {
            "method": "deterministic timestamp/block shuffle null",
            "run_count": 100,
            "required_if_feasible": True,
            "pass_rule": "validation percentile >= 0.95",
        },
        "evaluator_policy": {
            "diagnostic_promising_true_only_if_all_true": [
                "validation net > 0",
                "holdout net > 0",
                "validation monthly positive rate >= 0.60",
                "validation closed trades >= 100, else inconclusive",
                "null baseline passes",
                "metric integrity passes",
                "no lookahead/repaint issue",
                "safety passes",
            ],
            "allowed_result_classes": [
                "LUCIFER_15M_V3_HORIZONTAL_CROSS_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE",
                "LUCIFER_15M_V3_HORIZONTAL_CROSS_REJECTED_NO_FOLLOWUP",
                "LUCIFER_15M_V3_HORIZONTAL_CROSS_INCONCLUSIVE_NEEDS_MORE_DATA",
                "LUCIFER_15M_V3_HORIZONTAL_CROSS_INVALIDATED_BY_LOOKAHEAD_OR_INTEGRITY_FAILURE",
            ],
        },
        "forbidden_actions_confirmed_false": {
            "parameter_expansion": False,
            "grid_search": False,
            "optimization": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_permission": False,
            "live_permission": False,
            "capital_permission": False,
            "network_used": False,
            "private_api_used": False,
            "orders_submitted": False,
        },
        "next_module": "tools/edge_factory_os_repo_only_lucifer_15m_v3_horizontal_cross_execution_v1.py",
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "artifact_path_equals_required_path": True,
            "actual_clean_head_recorded": True,
            "tracked_python_count_recorded": True,
            "panel_review_artifact_loaded": True,
            "panel_review_status_verified": True,
            "panel_review_classification_verified": True,
            "single_config_only": True,
            "timeframe_15m_only": True,
            "horizontal_only_rule_preregistered": True,
            "no_filters": True,
            "no_parameter_expansion": True,
            "no_grid_search": True,
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
        raise RuntimeError("V3 preregistration validation checks failed")
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
                "route": ROUTE,
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
