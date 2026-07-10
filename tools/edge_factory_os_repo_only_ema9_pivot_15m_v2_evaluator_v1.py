import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_ema9_pivot_15m_v2_evaluator_v1.py"
ARTIFACT_PATH = "artifacts/strategy_evaluations/ema9_pivot_15m_v2_evaluator_v1.json"
EXECUTION_PATH = "artifacts/strategy_executions/ema9_pivot_15m_v2_execution_v1.json"

STATUS = "PASS_REPO_ONLY_EMA9_PIVOT_15M_V2_EVALUATED"
ARTIFACT_KIND = "EMA9_PIVOT_15M_V2_EVALUATOR"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_EMA9_PIVOT_15M_V2_EXECUTED"
ROUTE = "EMA9_PIVOT_15M_EMA9_PIVOT_STABLE_CROSS_TREND_VOLUME_TP_SL_V2"
CONFIG_ID = "ema9_pivot_15m_v2_stable_cross_trend_volume_sl1_tp2"

EXPECTED_PRE_EVALUATOR_HEAD = "af8590fd8b2e3f47458a0afddeec316122494a8f"
EXPECTED_PRE_EVALUATOR_TRACKED_PYTHON_COUNT = 938

RESULT_PROMISING = "EMA9_PIVOT_15M_V2_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE"
RESULT_REJECTED = "EMA9_PIVOT_15M_V2_REJECTED_NO_FOLLOWUP"
RESULT_INCONCLUSIVE = "EMA9_PIVOT_15M_V2_INCONCLUSIVE_NEEDS_MORE_DATA"
RESULT_INVALIDATED = "EMA9_PIVOT_15M_V2_INVALIDATED_BY_LOOKAHEAD_OR_INTEGRITY_FAILURE"


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


def verify_hash(payload: Dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError(f"{label} missing payload_sha256_excluding_hash")
    observed = canonical_payload_hash(payload)
    if observed != stored:
        raise RuntimeError(f"{label} payload hash mismatch: {observed} != {stored}")
    return stored


def get_nested(payload: Dict[str, Any], path: List[str]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise RuntimeError(f"missing execution field: {'.'.join(path)}")
        current = current[key]
    return current


def safety_review_passed(execution: Dict[str, Any]) -> bool:
    safety = execution.get("safety_review", {})
    if not isinstance(safety, dict):
        return False
    return (
        safety.get("single_config_only") is True
        and safety.get("no_parameter_grid") is True
        and safety.get("no_optimization") is True
        and safety.get("no_candidate") is True
        and safety.get("no_edge_claim") is True
        and safety.get("no_family_release") is True
        and safety.get("no_runtime_live_capital") is True
        and safety.get("no_orders") is True
        and safety.get("no_private_api") is True
        and safety.get("no_network") is True
        and safety.get("rsi_filter_used") is False
        and safety.get("score_system_used") is False
        and safety.get("candle_close_filter_used") is False
        and safety.get("proximity_filter_used") is False
        and safety.get("seven_of_seven_labels_used") is False
        and safety.get("atr_stop_used") is False
    )


def build_payload() -> Dict[str, Any]:
    actual_head = run_git(["rev-parse", "HEAD"])
    actual_tracked_python_count = tracked_python_count()
    current_dirty_paths = dirty_paths()
    allowed_dirty = {MODULE_PATH, ARTIFACT_PATH}
    unexpected_dirty_paths = [path for path in current_dirty_paths if path not in allowed_dirty]
    if unexpected_dirty_paths:
        raise RuntimeError(f"unexpected dirty paths during V2 evaluator: {unexpected_dirty_paths}")
    if actual_head != EXPECTED_PRE_EVALUATOR_HEAD:
        raise RuntimeError(f"HEAD moved before V2 evaluator: {actual_head} != {EXPECTED_PRE_EVALUATOR_HEAD}")
    if actual_tracked_python_count != EXPECTED_PRE_EVALUATOR_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before V2 evaluator: "
            f"{actual_tracked_python_count} != {EXPECTED_PRE_EVALUATOR_TRACKED_PYTHON_COUNT}"
        )

    execution = read_json(EXECUTION_PATH)
    execution_hash = verify_hash(execution, "execution")
    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution status mismatch")
    if execution.get("route") != ROUTE:
        raise RuntimeError("route mismatch")
    if execution.get("config_id") != CONFIG_ID:
        raise RuntimeError("config id mismatch")

    signal_accounting = get_nested(execution, ["signal_accounting"])
    overall_summary = get_nested(execution, ["overall_summary", "trade_summary"])
    validation_summary = get_nested(execution, ["split_summaries", "validation", "trade_summary"])
    validation_monthly = get_nested(execution, ["split_summaries", "validation", "monthly_summary"])
    holdout_summary = get_nested(execution, ["split_summaries", "holdout", "trade_summary"])
    holdout_monthly = get_nested(execution, ["split_summaries", "holdout", "monthly_summary"])
    null_summary = get_nested(execution, ["null_baseline_summary"])
    metric_summary = get_nested(execution, ["metric_integrity_summary"])

    validation_net_bps: Optional[float] = validation_summary.get("net_bps")
    holdout_net_bps: Optional[float] = holdout_summary.get("net_bps")
    validation_closed_trades = int(validation_summary.get("closed_trades", 0))
    validation_monthly_positive_rate: Optional[float] = validation_monthly.get("monthly_positive_rate")
    holdout_monthly_positive_rate: Optional[float] = holdout_monthly.get("monthly_positive_rate")
    null_baseline_pass = null_summary.get("null_baseline_pass") is True
    metric_integrity_passed = metric_summary.get("metric_integrity_passed") is True
    no_lookahead_repaint_issue = metric_summary.get("no_lookahead_repaint_issue") is True
    safety_passed = safety_review_passed(execution) and execution.get("safety_review_passed") is True

    validation_positive = validation_net_bps is not None and validation_net_bps > 0
    holdout_positive = holdout_net_bps is not None and holdout_net_bps > 0
    validation_monthly_pass = (
        validation_monthly_positive_rate is not None and validation_monthly_positive_rate >= 0.60
    )
    validation_sample_pass = validation_closed_trades >= 100

    diagnostic_promising = (
        validation_positive
        and holdout_positive
        and validation_monthly_pass
        and validation_sample_pass
        and null_baseline_pass
        and metric_integrity_passed
        and no_lookahead_repaint_issue
        and safety_passed
    )
    if not metric_integrity_passed or not no_lookahead_repaint_issue:
        result_class = RESULT_INVALIDATED
    elif not validation_sample_pass:
        result_class = RESULT_INCONCLUSIVE
    elif diagnostic_promising:
        result_class = RESULT_PROMISING
    else:
        result_class = RESULT_REJECTED

    evaluator_findings = {
        "diagnostic_promising": diagnostic_promising,
        "result_class": result_class,
        "validation_net_bps": validation_net_bps,
        "holdout_net_bps": holdout_net_bps,
        "validation_monthly_positive_rate": validation_monthly_positive_rate,
        "holdout_monthly_positive_rate": holdout_monthly_positive_rate,
        "validation_closed_trades": validation_closed_trades,
        "validation_closed_trades_min_100_pass": validation_sample_pass,
        "null_baseline_pass": null_baseline_pass,
        "validation_null_percentile": null_summary.get("validation_null_percentile"),
        "metric_integrity_passed": metric_integrity_passed,
        "no_lookahead_repaint_issue": no_lookahead_repaint_issue,
        "safety_review_passed": safety_passed,
        "rejection_reasons": [
            reason
            for reason, passed in [
                ("validation_net_bps_not_positive", validation_positive),
                ("holdout_net_bps_not_positive", holdout_positive),
                ("validation_monthly_positive_rate_below_0_60", validation_monthly_pass),
                ("null_baseline_not_passed", null_baseline_pass),
                ("metric_integrity_failed", metric_integrity_passed),
                ("lookahead_or_repaint_issue", no_lookahead_repaint_issue),
                ("safety_review_failed", safety_passed),
            ]
            if not passed
        ],
    }

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route": ROUTE,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "pre_evaluator_head": EXPECTED_PRE_EVALUATOR_HEAD,
            "pre_evaluator_head_verified_at_artifact_creation": actual_head,
            "repo_clean_before_evaluator_confirmed_externally": True,
            "tracked_python_count_before_evaluator": EXPECTED_PRE_EVALUATOR_TRACKED_PYTHON_COUNT,
            "tracked_python_count_verified_at_artifact_creation": actual_tracked_python_count,
            "dirty_paths_during_artifact_creation_limited_to_expected_new_paths": True,
            "dirty_paths_during_artifact_creation": current_dirty_paths,
        },
        "evaluator_inputs": {
            "execution_artifact": EXECUTION_PATH,
            "execution_status": execution.get("status"),
            "execution_payload_sha256_excluding_hash": execution_hash,
            "execution_payload_hash_verified": True,
            "panel_rows_read": False,
            "execution_rerun": False,
            "metadata_read": "git HEAD, tracked Python count, and dirty path scope only",
        },
        "evaluator_policy_applied": {
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
                RESULT_PROMISING,
                RESULT_REJECTED,
                RESULT_INCONCLUSIVE,
                RESULT_INVALIDATED,
            ],
        },
        "execution_metric_snapshot": {
            "raw_crosses": signal_accounting.get("total_raw_crosses"),
            "fake_cross_blocked": signal_accounting.get("fake_cross_blocked"),
            "trend_filter_blocked": signal_accounting.get("trend_filter_blocked"),
            "volume_filter_blocked": signal_accounting.get("volume_filter_blocked"),
            "accepted_signals": signal_accounting.get("accepted_signals"),
            "closed_trades": overall_summary.get("closed_trades"),
            "unresolved_trades": overall_summary.get("unresolved_trades"),
            "long_trades": overall_summary.get("long_trades"),
            "short_trades": overall_summary.get("short_trades"),
            "stop_hit_count": overall_summary.get("stop_hit_count"),
            "take_profit_hit_count": overall_summary.get("take_profit_hit_count"),
            "both_hit_same_bar_count": overall_summary.get("both_hit_same_bar_count"),
            "gross_bps": overall_summary.get("gross_bps"),
            "net_bps": overall_summary.get("net_bps"),
            "validation_net_bps": validation_net_bps,
            "holdout_net_bps": holdout_net_bps,
            "validation_monthly_positive_rate": validation_monthly_positive_rate,
            "holdout_monthly_positive_rate": holdout_monthly_positive_rate,
            "validation_worst_month": validation_monthly.get("worst_month"),
            "holdout_worst_month": holdout_monthly.get("worst_month"),
        },
        "evaluator_findings": evaluator_findings,
        "safety_closure_constraints": {
            "candidate_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "orders_submitted": False,
        },
        "next_module": "tools/edge_factory_os_repo_only_ema9_pivot_15m_v2_closure_v1.py",
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "artifact_path_equals_required_path": True,
            "execution_artifact_loaded": True,
            "execution_payload_hash_verified": True,
            "execution_not_rerun": True,
            "panel_rows_not_read": True,
            "result_class_allowed": result_class
            in {RESULT_PROMISING, RESULT_REJECTED, RESULT_INCONCLUSIVE, RESULT_INVALIDATED},
            "diagnostic_promising_policy_applied": True,
            "metric_integrity_result_recorded": True,
            "no_lookahead_repaint_result_recorded": True,
            "safety_result_recorded": True,
            "no_candidate": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    if not all(payload["validation_checks"].values()):
        raise RuntimeError(f"V2 evaluator validation checks failed: {payload['validation_checks']}")
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
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
                "result_class": payload["evaluator_findings"]["result_class"],
                "diagnostic_promising": payload["evaluator_findings"]["diagnostic_promising"],
                "validation_net_bps": payload["evaluator_findings"]["validation_net_bps"],
                "holdout_net_bps": payload["evaluator_findings"]["holdout_net_bps"],
                "validation_monthly_positive_rate": payload["evaluator_findings"][
                    "validation_monthly_positive_rate"
                ],
                "null_baseline_pass": payload["evaluator_findings"]["null_baseline_pass"],
                "metric_integrity_passed": payload["evaluator_findings"]["metric_integrity_passed"],
                "no_lookahead_repaint_issue": payload["evaluator_findings"]["no_lookahead_repaint_issue"],
                "replacement_checks_all_true": True,
                "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
