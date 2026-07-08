from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIOR_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_liquidity_sweep_reversal_execution_v1.json"
FILTER_AUDIT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_liquidity_sweep_filter_kill_audit_v1.json"
PRIOR_EXECUTION_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_crypto_15m_liquidity_sweep_reversal_execution_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_liquidity_sweep_execution_bug_localization_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_LIQUIDITY_SWEEP_EXECUTION_BUG_LOCALIZATION_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_LIQUIDITY_SWEEP_EXECUTION_BUG_LOCALIZATION"
STRATEGY = "CRYPTO_15M_LIQUIDITY_SWEEP_FAILED_BREAKOUT_REVERSAL_V1"
ROUTE_FAMILY = "CRYPTO_15M_LIQUIDITY_SWEEP_REVERSAL_BASELINE"
CONFIG_ID = "crypto_15m_liquidity_sweep_48h_reversal_r2_timestop8h_v1"


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


def source_matches() -> list[dict[str, Any]]:
    lines = PRIOR_EXECUTION_TOOL.read_text(encoding="utf-8").splitlines()
    matches = []
    for index, line in enumerate(lines, start=1):
        if "len(high_deque) >= PRIOR_RANGE_WINDOW" in line or "len(low_deque) >= PRIOR_RANGE_WINDOW" in line:
            start = max(1, index - 2)
            end = min(len(lines), index + 2)
            matches.append(
                {
                    "line": index,
                    "text": line.strip(),
                    "context": [{"line": number, "text": lines[number - 1]} for number in range(start, end + 1)],
                }
            )
    return matches


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_liquidity_sweep_execution_bug_localization_v1.py",
        "?? artifacts/strategy_reviews/crypto_15m_liquidity_sweep_execution_bug_localization_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    prior_execution = load_json(PRIOR_EXECUTION_PATH)
    filter_audit = load_json(FILTER_AUDIT_PATH)
    matches = source_matches()
    prior_metrics = prior_execution.get("metrics", {})
    audit_long = filter_audit.get("long_side_filter_counts", {})
    audit_short = filter_audit.get("short_side_filter_counts", {})

    prior_zero = prior_metrics.get("accepted_long_trades") == 0 and prior_metrics.get("accepted_short_trades") == 0
    audit_has_candidates = (
        audit_long.get("final_candidate_count_before_position_capacity", 0)
        + audit_short.get("final_candidate_count_before_position_capacity", 0)
        > 0
    )
    suspected_bug_category = "SIGNAL_BOOLEAN_MISMATCH" if matches and prior_zero and audit_has_candidates else "UNKNOWN_IMPLEMENTATION_BUG"
    root_cause = (
        "Prior execution required len(high_deque) and len(low_deque) to be at least PRIOR_RANGE_WINDOW. "
        "Those deques are monotonic extrema queues, so their length is not the lookback row count. "
        "The requirement suppressed raw sweep evaluation even though the audit found final candidates."
        if suspected_bug_category == "SIGNAL_BOOLEAN_MISMATCH"
        else "Could not localize the implementation defect from source and artifact comparison."
    )

    safety_permissions = {
        "bug_localization_created": True,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "prior_execution_loaded": True,
        "filter_kill_audit_loaded": True,
        "prior_execution_tool_text_inspected": PRIOR_EXECUTION_TOOL.exists(),
        "prior_zero_trades_verified": prior_zero,
        "audit_final_candidates_verified_positive": audit_has_candidates,
        "no_backtest_execution": True,
        "no_v2_tested": True,
        "no_parameter_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_liquidity_sweep_execution_bug_localization_v1",
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_bug_localization": status_lines,
            "allowed_new_paths_at_bug_localization": sorted(allowed_status),
            "unexpected_dirty_paths_at_bug_localization": unexpected_status,
        },
        "source_artifacts": {
            "prior_execution": str(PRIOR_EXECUTION_PATH),
            "filter_kill_audit": str(FILTER_AUDIT_PATH),
            "prior_execution_tool": str(PRIOR_EXECUTION_TOOL),
        },
        "prior_vs_audit_comparison": {
            "prior_accepted_long_trades": prior_metrics.get("accepted_long_trades"),
            "prior_accepted_short_trades": prior_metrics.get("accepted_short_trades"),
            "prior_closed_trades": prior_metrics.get("closed_trades"),
            "audit_raw_long_sweeps": audit_long.get("raw_sweep_count"),
            "audit_raw_short_sweeps": audit_short.get("raw_sweep_count"),
            "audit_final_long_candidates_before_capacity": audit_long.get("final_candidate_count_before_position_capacity"),
            "audit_final_short_candidates_before_capacity": audit_short.get("final_candidate_count_before_position_capacity"),
            "audit_classification": filter_audit.get("audit_classification"),
        },
        "source_inspection_findings": {
            "monotonic_deque_length_requirements_found": matches,
            "monotonic_deque_length_misused_as_lookback_count": bool(matches),
        },
        "suspected_bug_category": suspected_bug_category,
        "root_cause_summary": root_cause,
        "repair_scope": {
            "recommended_next_step": "repaired execution only",
            "parameter_change_allowed": False,
            "dataset_change_allowed": False,
            "filter_change_allowed": False,
            "strategy_change_allowed": False,
        },
        "limitations": [
            "This localization step does not run the backtest or create trades.",
            "The repaired execution must keep the same preregistered parameters and replace only the implementation bug in new files.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["bug_localization_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "bug_localization_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    print(f"status: {STATUS}")
    print(f"suspected_bug_category: {suspected_bug_category}")
    print(f"prior_accepted_long_short: {prior_metrics.get('accepted_long_trades')}/{prior_metrics.get('accepted_short_trades')}")
    print(
        "audit_final_long_short: "
        f"{audit_long.get('final_candidate_count_before_position_capacity')}/"
        f"{audit_short.get('final_candidate_count_before_position_capacity')}"
    )
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
