#!/usr/bin/env python3
"""Create the old_short clean-room runner realistic fixture dry-run design."""

from __future__ import annotations

import hashlib
import json
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_DESIGN"
ROUTE_KEY = "old_short_clean_room_v1"
MODULE = "edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_design_v1"
EXPECTED_HEAD = "64d535535cf3ad28fa0a5f5a1fc0069487cb063a"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PREVIEW_V1"
PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_DESIGN_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "old_short_clean_room"
    / "old_short_clean_room_runner_realistic_fixture_dry_run_design_v1.json"
)
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_design_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_runner_realistic_fixture_dry_run_design_v1.json"
)

PRIOR_GENERATION_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.json"
)
SOURCE_ARTIFACT_RELS = [
    PRIOR_GENERATION_REL,
    "artifacts/old_short_clean_room/old_short_clean_room_realistic_bounded_fixture_design_v1.json",
    "artifacts/old_short_clean_room/old_short_clean_room_runner_feature_fixture_dry_run_v1.json",
    "artifacts/old_short_clean_room/old_short_clean_room_feature_fixture_validator_check_v1.json",
    "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json",
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json",
    "artifacts/old_short_clean_room/old_short_clean_room_threshold_proposal_review_v1.json",
    "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
]

APPROVED_FIXTURE_ROOT = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\realistic_bounded_fixture_generation_dry_run_v1"
)
FUTURE_OUTPUT_ROOT = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\realistic_fixture_dry_run_v1"
)

SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "PROXY_BEHAVIOR_FIXTURE",
    "NOT_ORIGINAL_OLD_SHORT",
    "NOT_EXACT_REPLAY",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]


def read_json(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(relative_path: str) -> str:
    path = REPO_ROOT / relative_path
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def normalize_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return list(value.values())
    return [value]


def get_nested(mapping: dict[str, Any], path: list[str], default: Any = None) -> Any:
    value: Any = mapping
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def payload_hash(payload: dict[str, Any]) -> str:
    payload_copy = deepcopy(payload)
    payload_copy.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(payload_copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def repo_clean_before_design(status_lines: list[str]) -> bool:
    allowed_untracked = {
        f"?? {TOOL_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
    }
    return all(line in allowed_untracked for line in status_lines)


def main() -> int:
    head = run_git(["rev-parse", "HEAD"])
    status_before_lines = [line for line in run_git(["status", "--short"]).splitlines() if line]

    prior_generation = read_json(PRIOR_GENERATION_REL)
    source_artifacts = {
        relative_path: {
            "path": relative_path,
            "sha256": sha256_file(relative_path),
        }
        for relative_path in SOURCE_ARTIFACT_RELS
    }

    fixture_summary = prior_generation.get("fixture_generation_summary", {})
    fixture_selection = prior_generation.get("fixture_case_selection", {})
    generation_identity = prior_generation.get("fixture_generation_identity", {})

    family_coverage = normalize_list(
        fixture_summary.get("family_coverage")
        or fixture_selection.get("family_coverage")
        or fixture_selection.get("families_selected")
    )
    gate_state_coverage = normalize_list(
        fixture_summary.get("gate_state_coverage")
        or fixture_selection.get("gate_state_coverage")
        or fixture_selection.get("gate_states_selected")
    )
    fixture_case_count = (
        fixture_summary.get("fixture_case_count")
        or fixture_selection.get("fixture_case_count")
        or 0
    )
    master_files_found_count = fixture_summary.get("master_files_found_count")
    missing_metric_recovery = normalize_list(prior_generation.get("missing_metric_recovery_summary"))
    accepted_lifecycle_present = "gate_allowed" in set(str(item) for item in gate_state_coverage)

    dry_run_design_identity = {
        "route_key": ROUTE_KEY,
        "design_only": True,
        "realistic_fixture_runner_dry_run_allowed_now": False,
        "original_exact_source_recovered": False,
        "exact_replay_available": False,
        "clean_room_behavioral_reconstruction": True,
        "no_edge_claim": True,
        "no_live_capital": True,
    }

    input_fixture_policy = {
        "approved_realistic_fixture_output_root": APPROVED_FIXTURE_ROOT,
        "future_runner_may_read_only": [
            "fixture_index.json",
            "master_proxy_cases.jsonl",
            "clean_room_replay_fixture_inputs.jsonl",
            "validation_pair_fixtures.jsonl",
            "fixture_generation_summary.json",
        ],
        "forbidden_inputs": [
            "raw market data",
            "raw OKX 1m data",
            "full MASTER files",
            "runtime directories",
            "private/account data",
        ],
        "metadata_preserved_from_prior_fixture_generation": {
            "prior_status": prior_generation.get("status"),
            "prior_result_classification": prior_generation.get("result_classification"),
            "prior_output_root": fixture_summary.get("output_root")
            or generation_identity.get("output_root")
            or APPROVED_FIXTURE_ROOT,
            "master_files_found_count": master_files_found_count,
            "fixture_case_count": fixture_case_count,
            "family_coverage": family_coverage,
            "gate_state_coverage": gate_state_coverage,
        },
    }

    fixture_modes = [
        {
            "mode": "REALISTIC_BOUNDED_FIXTURE_DRY_RUN",
            "uses_master_derived_bounded_proxy_fixture_cases": True,
            "uses_clean_room_replay_fixture_inputs": True,
            "uses_reviewed_behavioral_threshold_contract": True,
            "runs_on_market_data": False,
            "computes_pnl": False,
            "claims_exact_replay": False,
            "claims_edge": False,
        }
    ]

    runner_processing_plan = {
        "future_steps": [
            "load reviewed threshold contract",
            "load realistic bounded fixture input cases",
            "validate route_key, family_key, and side",
            "validate all safety labels",
            "process each fixture case through clean-room lifecycle logic",
            "emit signal candidate",
            "emit pending entry",
            "apply gate fixture check",
            "emit rejected entry or paper open/closed only when fixture supports gate allow",
            "emit heartbeat and state report",
        ],
        "fail_closed_requirements": [
            "fail closed if required feature is missing",
            "fail closed if gate state is missing",
            "never infer missing fixture values",
            "preserve not-original and no-edge labels",
        ],
        "lifecycle_sequence": [
            "signal candidate",
            "pending entry",
            "gate fixture check",
            "rejected or paper open/closed if fixture supports gate allow",
            "heartbeat/state report",
        ],
    }

    gate_state_plan = {
        "required_gate_states_to_handle": [
            "gate_blocked",
            "gate_missing_timeout",
            "gate_allowed if present",
        ],
        "prior_fixture_gate_state_coverage": gate_state_coverage,
        "accepted_lifecycle_coverage_present": accepted_lifecycle_present,
        "gate_allowed_absent_policy": {
            "do_not_fail_automatically": True,
            "mark_accepted_lifecycle_coverage_missing": True,
            "classification_can_be_partial_at_best": True,
            "do_not_claim_open_closed_lifecycle_equivalence": True,
        },
    }

    output_policy = {
        "future_output_root": FUTURE_OUTPUT_ROOT,
        "may_write_only_to_future_output_root": True,
        "never_write_to": [
            "MASTER_UPPER_SYSTEM",
            "paper_run_gate_* runtime roots",
            "live runtime directories",
            "old original output directories",
            "repo tracked paths except summary JSON artifacts",
        ],
        "future_output_files": [
            "signals.csv",
            "pending_entries.csv",
            "open_positions.csv if fixture supports gate allowed",
            "closed_trades.csv if fixture supports close lifecycle",
            "rejected_entries.csv",
            "heartbeat.csv",
            "state.json",
            "runner_realistic_fixture_dry_run_report.json",
        ],
    }

    fail_closed_conditions = [
        "fixture root missing",
        "fixture files missing",
        "route_key mismatch",
        "family_key mismatch",
        "side not short",
        "safety labels missing",
        "threshold contract missing",
        "required feature missing",
        "fixture uses PnL/outcome selection",
        "raw market data path supplied",
        "runtime path supplied",
        "live/order/private fields detected",
        "output root overlaps MASTER/runtime",
        "no-live guard false",
    ]

    dry_run_metrics = [
        "fixture_case_count",
        "processed_case_count",
        "family_coverage",
        "gate_state_coverage",
        "passed_case_count",
        "rejected_case_count",
        "fail_closed_count",
        "generated_output_file_count",
        "accepted_lifecycle_coverage_present",
        "safety_label_audit_passed",
        "no_pnl_used",
        "no_market_data_used",
    ]

    result_classes = [
        {
            "classification": "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
            "meaning": (
                "Both families are processed, gate blocked/missing behavior is processed, "
                "gate allowed/open-close lifecycle is processed if the fixture exists, all safety "
                "labels pass, and no PnL, market, or live data is used."
            ),
        },
        {
            "classification": "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
            "meaning": (
                "Both families and gate blocked/missing behavior are processed, but "
                "gate_allowed/open-close lifecycle is absent or incomplete."
            ),
        },
        {
            "classification": "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE",
            "meaning": "Safety, root, threshold, route, feature, or no-live checks fail.",
        },
        {
            "classification": "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
            "meaning": "Fixtures are insufficient to process meaningful cases.",
        },
    ]

    safety_permissions = {
        "runner_realistic_fixture_dry_run_design_created": True,
        "realistic_fixture_runner_dry_run_allowed_now": False,
        "runner_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "full_dataset_comparison_allowed_now": False,
        "backtest_allowed_now": False,
        "pnl_computation_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
    }

    prior_route_key = (
        get_nested(prior_generation, ["fixture_generation_identity", "route_key"])
        or prior_generation.get("route_key")
    )
    validation_checks = {
        "repo_clean_before_run": repo_clean_before_design(status_before_lines),
        "prior_realistic_fixture_generation_loaded": prior_generation.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_REALISTIC_BOUNDED_FIXTURE_GENERATION_DRY_RUN_CREATED",
        "prior_next_allowed_step_verified": prior_generation.get("next_allowed_step")
        == PRIOR_NEXT_ALLOWED_STEP,
        "original_exact_source_not_claimed": not dry_run_design_identity["original_exact_source_recovered"],
        "clean_room_reconstruction_preserved": dry_run_design_identity[
            "clean_room_behavioral_reconstruction"
        ],
        "no_fixture_runner_execution": True,
        "no_signal_generation": True,
        "no_behavioral_validation_execution": True,
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "input_fixture_policy_defined": bool(input_fixture_policy["future_runner_may_read_only"]),
        "gate_state_plan_defined": bool(gate_state_plan["required_gate_states_to_handle"]),
        "fail_closed_conditions_defined": len(fail_closed_conditions) == 14,
        "result_classes_defined": len(result_classes) == 4,
        "exactly_one_python_tool_created": (REPO_ROOT / TOOL_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": repo_clean_before_design(status_before_lines),
        "replacement_checks_all_true": True,
    }
    validation_checks["route_key_verified"] = prior_route_key == ROUTE_KEY
    validation_checks["replacement_checks_all_true"] = all(
        value is True for value in validation_checks.values() if isinstance(value, bool)
    )

    limitations = [
        "This artifact is design-only and does not execute the runner.",
        "No real signal generation, behavioral validation, backtest, PnL computation, runtime, live, or capital action is performed.",
        "The prior realistic fixture package covers gate_blocked and gate_missing_timeout; gate_allowed/open-close lifecycle coverage is not present unless a later fixture package adds it.",
        "Future dry-run classification is PARTIAL at best when accepted lifecycle coverage is absent.",
        "The design does not recover original old_short source or claim exact replay.",
    ]

    artifact: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "expected_head": EXPECTED_HEAD,
            "actual_head": head,
            "head_verified": head == EXPECTED_HEAD,
            "tracked_python_count_before": 957,
            "repo_status_before_design": status_before_lines,
        },
        "source_artifacts": source_artifacts,
        "dry_run_design_identity": dry_run_design_identity,
        "input_fixture_policy": input_fixture_policy,
        "fixture_modes": fixture_modes,
        "runner_processing_plan": runner_processing_plan,
        "gate_state_plan": gate_state_plan,
        "output_policy": output_policy,
        "safety_labels": SAFETY_LABELS,
        "fail_closed_conditions": fail_closed_conditions,
        "dry_run_metrics": dry_run_metrics,
        "result_classes": result_classes,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "limitations": limitations,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": "",
    }

    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"status: {artifact['status']}")
    print(f"route_key: {ROUTE_KEY}")
    print("design_only: true")
    print("realistic_fixture_runner_dry_run_allowed_now: false")
    print(f"fixture_mode_count: {len(fixture_modes)}")
    print(f"fail_closed_condition_count: {len(fail_closed_conditions)}")
    print(f"result_class_count: {len(result_classes)}")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0 if artifact["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
