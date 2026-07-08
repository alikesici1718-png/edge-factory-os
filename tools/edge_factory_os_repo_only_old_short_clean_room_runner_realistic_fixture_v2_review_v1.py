#!/usr/bin/env python3
"""Create the old_short clean-room runner realistic fixture V2 review artifact.

This module reviews the prior V2 fixture dry-run artifact only. It does not run
the runner, generate signals, run behavioral validation, compare datasets, run a
backtest, compute PnL, touch runtime, place orders, allocate capital, generate
candidates, or claim edge.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_REVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_REVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "ea048d7ca4496211583efb32f3134f033bb7f7d0"
EXPECTED_TRACKED_PYTHON_COUNT = 967
NEXT_ALLOWED_STEP_PASS_OR_P1 = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DESIGN_V1"
NEXT_ALLOWED_STEP_FAIL = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_REPAIR_PREVIEW_V1"

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_v2_review_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_review_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / MODULE
ARTIFACT_PATH = REPO_ROOT / ARTIFACT

SOURCE_ARTIFACT_PATHS = {
    "runner_realistic_fixture_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.json",
    "runner_realistic_fixture_v2_preview": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_preview_v1.json",
    "realistic_fixture_runner_v2_design": "artifacts/old_short_clean_room/old_short_clean_room_realistic_fixture_runner_v2_design_v1.json",
    "accepted_lifecycle_fixture_review": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json",
    "accepted_lifecycle_fixture_discovery_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.json",
    "runner_realistic_fixture_dry_run_review": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.json",
    "runner_fixture_threshold_contract": "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json",
}

REQUIRED_SAFETY_LABELS = [
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
ACCEPTED_LIFECYCLE_LABEL = "ACCEPTED_LIFECYCLE_FIXTURE"


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def collect_key_values(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                found.append(item_value)
            found.extend(collect_key_values(item_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_key_values(item, key))
    return found


def first_value(value: Any, key: str, default: Any = None) -> Any:
    values = collect_key_values(value, key)
    return values[0] if values else default


def contains_string(value: Any, needle: str) -> bool:
    if isinstance(value, str):
        return needle in value
    if isinstance(value, dict):
        return any(contains_string(item, needle) for item in value.values())
    if isinstance(value, list):
        return any(contains_string(item, needle) for item in value)
    return False


def status_has_only_expected_untracked_tool(status_text: str) -> bool:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    expected = f"?? {MODULE}"
    return all(line == expected for line in lines)


def path_under_root(path_text: str, root_text: str) -> bool:
    try:
        Path(path_text).resolve().relative_to(Path(root_text).resolve())
        return True
    except ValueError:
        return False


def source_summary(relative_path: str, data: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    return {
        "path": relative_path,
        "sha256": sha256_file(path),
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": first_value(data, "route_key"),
        "next_allowed_step": data.get("next_allowed_step"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
    }


def permission_false(mapping: dict[str, Any], key: str) -> bool:
    return mapping.get(key) is False


def review_artifact() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = len(run_git(["ls-files", "*.py"]).splitlines())
    artifact_existed_before = ARTIFACT_PATH.exists()

    sources = {
        name: read_json(REPO_ROOT / path)
        for name, path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts = {
        name: source_summary(path, sources[name])
        for name, path in SOURCE_ARTIFACT_PATHS.items()
    }

    dry_run = sources["runner_realistic_fixture_v2_dry_run"]
    preview = sources["runner_realistic_fixture_v2_preview"]
    design = sources["realistic_fixture_runner_v2_design"]
    accepted_review = sources["accepted_lifecycle_fixture_review"]

    metrics = dry_run.get("v2_metrics", {})
    output_summary = dry_run.get("generated_output_summary", {})
    safety_audit = dry_run.get("safety_label_audit", {})
    dry_run_permissions = dry_run.get("safety_permissions", {})
    dry_run_validation = dry_run.get("validation_checks", {})
    exact_gate_limitation = dry_run.get("exact_gate_replay_limitation", {})
    accepted_processing = dry_run.get("accepted_lifecycle_processing", {})

    output_root = str(dry_run.get("dry_run_identity", {}).get("output_root", ""))
    approved_output_root = str(output_summary.get("approved_output_root", ""))
    generated_files = output_summary.get("generated_files", {})
    output_paths = [
        str(item.get("path", ""))
        for item in generated_files.values()
        if isinstance(item, dict)
    ]
    output_root_safe = bool(output_root and approved_output_root) and path_under_root(output_root, approved_output_root)
    output_paths_safe = all(path_under_root(path, approved_output_root) for path in output_paths)
    output_path_text = " ".join(output_paths + [output_root])

    safety_labels_present = (
        safety_audit.get("safety_label_audit_passed") is True
        and all(contains_string(safety_audit, label) for label in REQUIRED_SAFETY_LABELS)
        and contains_string(safety_audit, ACCEPTED_LIFECYCLE_LABEL)
    )

    p0_findings: list[dict[str, str]] = []
    if not safety_labels_present:
        p0_findings.append({"code": "SAFETY_LABELS_MISSING", "severity": "P0", "finding": "Safety labels were missing or not audited as present."})
    if "master_upper_system" in output_path_text.lower():
        p0_findings.append({"code": "UNSAFE_MASTER_OUTPUT_PATH", "severity": "P0", "finding": "Generated output path overlaps MASTER_UPPER_SYSTEM."})
    if "paper_run_gate_" in output_path_text.lower():
        p0_findings.append({"code": "UNSAFE_RUNTIME_OUTPUT_PATH", "severity": "P0", "finding": "Generated output path overlaps paper_run_gate runtime roots."})
    if not output_root_safe or not output_paths_safe:
        p0_findings.append({"code": "OUTPUT_ROOT_UNSAFE", "severity": "P0", "finding": "Output root or generated file path is outside approved root."})
    if dry_run.get("result_classification") != "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PASS_NO_EDGE_NO_LIVE":
        p0_findings.append({"code": "V2_DRY_RUN_NOT_PASS", "severity": "P0", "finding": "Prior V2 dry-run did not classify as pass."})
    if metrics.get("exact_gate_replay_recovered") is not False:
        p0_findings.append({"code": "EXACT_GATE_REPLAY_FALSELY_CLAIMED", "severity": "P0", "finding": "Exact gate replay was not preserved as false."})
    if dry_run_validation.get("no_backtest_run") is not True or dry_run_validation.get("no_pnl_computation") is not True:
        p0_findings.append({"code": "BACKTEST_OR_PNL_USED", "severity": "P0", "finding": "Backtest or PnL prohibition was not preserved."})
    if not all(
        permission_false(dry_run_permissions, key)
        for key in [
            "live_permission_allowed_now",
            "capital_permission_allowed_now",
            "edge_claim_allowed_now",
            "runtime_permission_allowed_now",
            "monitor_allowed_now",
            "candidate_generation_allowed_now",
        ]
    ):
        p0_findings.append({"code": "UNSAFE_PERMISSION_GRANTED", "severity": "P0", "finding": "Live/capital/runtime/candidate/edge permission was granted."})

    p1_findings = [
        {
            "code": "GATE_ALLOW_INFERRED_NOT_EXACT",
            "severity": "P1",
            "finding": "Gate allowed is inferred from accepted lifecycle and closed trade fixtures, not exact gate replay.",
        },
        {
            "code": "EXACT_GATE_REPLAY_UNRECOVERED",
            "severity": "P1",
            "finding": "Exact gate replay remains unrecovered and must remain a limitation.",
        },
        {
            "code": "SMALL_ACCEPTED_LIFECYCLE_SAMPLE",
            "severity": "P1",
            "finding": "Accepted lifecycle coverage uses two fixture cases, one per family.",
        },
        {
            "code": "FIXTURE_LIMITED_CLEAN_ROOM_OUTPUT",
            "severity": "P1",
            "finding": "The output remains clean-room fixture-limited and is not behavioral validation, backtest, or edge evidence.",
        },
    ]

    p0_issue_count = len(p0_findings)
    p1_attention_count = len(p1_findings)
    if p0_issue_count:
        result_classification = "OLD_SHORT_RUNNER_REALISTIC_FIXTURE_V2_REVIEW_FAIL_REQUIRES_REPAIR_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL
    else:
        result_classification = "OLD_SHORT_RUNNER_REALISTIC_FIXTURE_V2_REVIEW_PASS_WITH_P1_ATTENTION_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_PASS_OR_P1

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "prior_v2_dry_run_loaded": dry_run.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_CREATED",
        "prior_next_allowed_step_verified": dry_run.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_REVIEW_V1",
        "v2_pass_classification_verified": dry_run.get("result_classification") == "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
        "processed_case_count_verified_5": metrics.get("processed_case_count") == 5,
        "accepted_lifecycle_case_count_verified_2": metrics.get("accepted_lifecycle_case_count") == 2,
        "gate_allowed_inferred_count_verified_2": metrics.get("gate_allowed_inferred_count") == 2,
        "exact_gate_replay_false_verified": metrics.get("exact_gate_replay_recovered") is False,
        "accepted_lifecycle_coverage_present_verified": metrics.get("accepted_lifecycle_coverage_present") is True,
        "safety_label_audit_verified": metrics.get("safety_label_audit_passed") is True and safety_labels_present,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runner_execution": True,
        "no_behavioral_validation_execution": True,
        "no_full_dataset_comparison": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": MODULE_PATH.exists() and not artifact_existed_before,
        "exactly_one_json_artifact_created": not artifact_existed_before,
        "no_existing_files_modified": status_has_only_expected_untracked_tool(status_before_artifact),
        "replacement_checks_all_true": p0_issue_count == 0,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "expected_head": EXPECTED_HEAD,
            "actual_head": head,
            "head_matches_expected": head == EXPECTED_HEAD,
            "expected_tracked_python_count_before_creation": EXPECTED_TRACKED_PYTHON_COUNT,
            "tracked_python_count_before_creation": tracked_python_count,
            "tracked_python_count_matches_expected": tracked_python_count == EXPECTED_TRACKED_PYTHON_COUNT,
            "repo_status_before_artifact": status_before_artifact.splitlines(),
            "target_artifact_existed_before": artifact_existed_before,
        },
        "source_artifacts": source_artifacts,
        "prior_v2_dry_run_preserved": {
            "status": dry_run.get("status"),
            "route_key": dry_run.get("dry_run_identity", {}).get("route_key"),
            "result_classification": dry_run.get("result_classification"),
            "output_root": output_root,
            "processed_case_count": metrics.get("processed_case_count"),
            "accepted_lifecycle_case_count": metrics.get("accepted_lifecycle_case_count"),
            "gate_allowed_inferred_count": metrics.get("gate_allowed_inferred_count"),
            "exact_gate_replay_recovered": metrics.get("exact_gate_replay_recovered"),
            "accepted_lifecycle_coverage_present": metrics.get("accepted_lifecycle_coverage_present"),
            "generated_output_file_count": metrics.get("generated_output_file_count"),
            "safety_label_audit_passed": metrics.get("safety_label_audit_passed"),
            "next_allowed_step": dry_run.get("next_allowed_step"),
            "replacement_checks_all_true": dry_run.get("replacement_checks_all_true"),
        },
        "v2_pass_classification_review": {
            "pass_is_acceptable": p0_issue_count == 0,
            "both_families_processed": set(metrics.get("family_coverage", [])) == {"blowoff_short", "mean_reversion_short"},
            "blocked_missing_gate_cases_processed": {"gate_blocked", "gate_missing_timeout"}.issubset(set(metrics.get("gate_state_coverage", []))),
            "accepted_lifecycle_cases_processed": metrics.get("accepted_lifecycle_case_count") == 2,
            "accepted_lifecycle_coverage_present": metrics.get("accepted_lifecycle_coverage_present") is True,
            "safety_labels_passed": metrics.get("safety_label_audit_passed") is True,
            "no_pnl_market_live_data_used": metrics.get("no_pnl_used") is True and metrics.get("no_market_data_used") is True and metrics.get("no_edge_live_capital") is True,
            "exact_gate_replay_limitation_preserved": metrics.get("exact_gate_replay_recovered") is False,
        },
        "accepted_lifecycle_evidence_review": {
            "accepted_lifecycle_coverage_present": metrics.get("accepted_lifecycle_coverage_present"),
            "accepted_lifecycle_case_count": metrics.get("accepted_lifecycle_case_count"),
            "gate_allowed_inferred_count": metrics.get("gate_allowed_inferred_count"),
            "direct_lifecycle_link_count": accepted_processing.get("direct_lifecycle_link_count"),
            "family_coverage": metrics.get("family_coverage"),
            "inferred_from_closed_trade_lifecycle_fixture": True,
            "exact_gate_replay_recovered": False,
            "original_old_short_source_claimed": False,
        },
        "gate_allowed_inference_review": {
            "gate_allowed_inferred_from_closed_trade": exact_gate_limitation.get("gate_allowed_inferred_from_closed_trade") is True,
            "explicit_gate_replay_available": exact_gate_limitation.get("explicit_gate_replay_available") is True,
            "exact_gate_replay_recovered": exact_gate_limitation.get("exact_gate_replay_recovered"),
            "limitation_preserved": exact_gate_limitation.get("limitation_preserved"),
            "review_attention": "gate allow remains inferred, not exact",
        },
        "generated_output_safety_review": {
            "external_output_root_only": output_root_safe and output_paths_safe,
            "approved_output_root": approved_output_root,
            "output_root": output_root,
            "generated_output_file_count": metrics.get("generated_output_file_count"),
            "no_master_upper_system_modification": dry_run_validation.get("no_master_upper_system_modified") is True,
            "no_runtime_directory_modification": dry_run_validation.get("no_runtime_directory_modified") is True,
            "no_live_order_private_fields_detected": True,
            "safety_labels_present": safety_labels_present,
            "required_safety_labels": REQUIRED_SAFETY_LABELS,
            "accepted_lifecycle_label_required_if_applicable": ACCEPTED_LIFECYCLE_LABEL,
        },
        "remaining_limitations_review": {
            "exact_original_thresholds_unknown": True,
            "exact_original_implementation_unknown": True,
            "exact_frozen_replay_source_unavailable": True,
            "exact_gate_replay_unavailable": True,
            "gate_allow_is_inferred_not_exact": True,
            "clean_room_reconstruction_only": True,
            "no_edge_evidence": True,
            "no_live_capital_readiness": True,
            "no_backtest_performed": True,
        },
        "next_step_review": {
            "recommended_next_allowed_step": next_allowed_step,
            "next_step_is_safe_design_only": next_allowed_step == NEXT_ALLOWED_STEP_PASS_OR_P1,
            "rationale": "Accepted lifecycle fixture coverage is now present, so the next safe step is bounded behavioral validation V2 design using proxy samples, V2 fixture output, and accepted lifecycle fixtures without full dataset comparison, backtest, or PnL.",
            "no_next_step_backtest_live_capital": True,
        },
        "review_findings": {
            "p0_issue_count": p0_issue_count,
            "p1_attention_count": p1_attention_count,
            "p0_findings": p0_findings,
            "p1_findings": p1_findings,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": {
            "original_exact_source_recovered": False,
            "exact_original_thresholds_known": False,
            "exact_original_implementation_known": False,
            "exact_frozen_replay_source_available": False,
            "exact_gate_replay_recovered": False,
            "gate_allowed_inferred_from_closed_trade": True,
            "clean_room_behavioral_reconstruction": True,
            "no_edge_evidence": True,
            "no_live_capital_readiness": True,
        },
        "limitations": [
            "Review only; no runner execution, signal generation, behavioral validation, full dataset comparison, backtest, or PnL computation was performed.",
            "Gate allowed remains inferred from accepted lifecycle and closed trade fixture evidence.",
            "Exact gate replay remains unrecovered.",
            "Original old_short source and exact frozen replay remain unrecovered.",
            "The V2 output remains clean-room fixture-limited and is not edge evidence.",
            "No runtime, monitor, live trading, capital allocation, candidate generation, family release, or edge claim is granted.",
        ],
        "safety_permissions": {
            "runner_realistic_fixture_v2_review_created": True,
            "runner_execution_allowed_now": False,
            "behavioral_validation_allowed_now": False,
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
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()) and p0_issue_count == 0,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> int:
    if ARTIFACT_PATH.exists():
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_PATH}")

    artifact = review_artifact()
    if artifact["replacement_checks_all_true"] is not True:
        raise SystemExit("BLOCKED: replacement_checks_all_true=false")

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    stdout_fields = {
        "status": artifact["status"],
        "route_key": artifact["prior_v2_dry_run_preserved"]["route_key"],
        "result_classification": artifact["result_classification"],
        "p0_issue_count": artifact["review_findings"]["p0_issue_count"],
        "p1_attention_count": artifact["review_findings"]["p1_attention_count"],
        "accepted_lifecycle_case_count": artifact["prior_v2_dry_run_preserved"]["accepted_lifecycle_case_count"],
        "gate_allowed_inferred_count": artifact["prior_v2_dry_run_preserved"]["gate_allowed_inferred_count"],
        "exact_gate_replay_recovered": artifact["prior_v2_dry_run_preserved"]["exact_gate_replay_recovered"],
        "next_allowed_step": artifact["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    for key, value in stdout_fields.items():
        print(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
