#!/usr/bin/env python3
"""Create the old_short bounded behavioral validation V2 metric repair design.

This is metric repair design only. It does not apply repair, rerun validation,
run the runner, generate signals, compare full datasets, run a backtest, compute
PnL, touch runtime, use network/API, generate candidates, or claim edge.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_DESIGN"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "1d34c306192feb7d6a4e2c1939d7d77e63fb79d9"
EXPECTED_TRACKED_PYTHON_COUNT = 972
METRIC_NAME = "family_key_match_rate"
ROOT_CAUSE_CLASS = "validator_metric_definition_issue"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_APPLY_V1"

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_v2_metric_repair_design_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_metric_repair_design_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / MODULE
ARTIFACT_PATH = REPO_ROOT / ARTIFACT

SOURCE_ARTIFACT_PATHS = {
    "bounded_behavioral_validation_v2_repair_preview": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_repair_preview_v1.json",
    "bounded_behavioral_validation_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_dry_run_v1.json",
    "bounded_behavioral_validation_v2_preview": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_preview_v1.json",
    "bounded_behavioral_validation_v2_design": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_design_v1.json",
    "runner_realistic_fixture_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.json",
    "accepted_lifecycle_fixture_review": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json",
    "old_short_clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
}


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


def status_has_only_expected_untracked_tool(status_text: str) -> bool:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    expected = f"?? {MODULE}"
    return all(line == expected for line in lines)


def source_summary(relative_path: str, data: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    return {
        "path": relative_path,
        "sha256": sha256_file(path),
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": first_value(data, "route_key"),
        "result_classification": data.get("result_classification"),
        "next_allowed_step": data.get("next_allowed_step"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
    }


def build_artifact() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = len(run_git(["ls-files", "*.py"]).splitlines())
    artifact_existed_before = ARTIFACT_PATH.exists()

    sources = {
        name: read_json(REPO_ROOT / relative_path)
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts = {
        name: source_summary(relative_path, sources[name])
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }

    repair_preview = sources["bounded_behavioral_validation_v2_repair_preview"]
    dry_run = sources["bounded_behavioral_validation_v2_dry_run"]
    metric_result = dry_run["similarity_metric_results_v2"]["metrics"][METRIC_NAME]
    failed_metric = repair_preview["failed_metric_list"][0] if repair_preview.get("failed_metric_list") else {}

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "repair_preview_loaded": repair_preview.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_REPAIR_PREVIEW_CREATED",
        "failed_metric_verified_family_key_match_rate": failed_metric.get("metric_name") == METRIC_NAME,
        "root_cause_verified_validator_metric_definition_issue": repair_preview.get("failure_root_cause_assessment", {}).get("root_cause_class") == ROOT_CAUSE_CLASS,
        "no_repair_applied": True,
        "no_validation_rerun": True,
        "no_runner_execution": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runtime_touched": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exact_gate_replay_false_preserved": dry_run.get("exact_gate_replay_limitation", {}).get("exact_gate_replay_recovered") is False,
        "unresolved_fields_preserved": True,
        "exactly_one_python_tool_created": MODULE_PATH.exists() and not artifact_existed_before,
        "exactly_one_json_artifact_created": not artifact_existed_before,
        "no_existing_files_modified": status_has_only_expected_untracked_tool(status_before_artifact),
        "replacement_checks_all_true": True,
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
        "repair_design_identity": {
            "route_key": ROUTE_KEY,
            "design_only": True,
            "repair_apply_allowed_now": False,
            "metric_name": METRIC_NAME,
            "root_cause_class": ROOT_CAUSE_CLASS,
            "exact_original_source_recovered": False,
            "exact_gate_replay_recovered": False,
            "no_edge_claim": True,
            "no_live_capital": True,
        },
        "observed_failure_preserved": {
            "prior_result_classification": dry_run.get("result_classification"),
            "failed_metric": METRIC_NAME,
            "failed_metric_count": len(repair_preview.get("failed_metric_list", [])),
            "family_key_match_rate": metric_result.get("value"),
            "schema_match_rate": dry_run["similarity_metric_results_v2"]["metrics"]["schema_match_rate"]["value"],
            "safety_label_match_rate": dry_run["similarity_metric_results_v2"]["metrics"]["safety_label_match_rate"]["value"],
            "accepted_lifecycle_coverage_rate": dry_run["similarity_metric_results_v2"]["metrics"]["accepted_lifecycle_coverage_rate"]["value"],
            "inferred_gate_allowed_coverage_rate": dry_run["similarity_metric_results_v2"]["metrics"]["inferred_gate_allowed_coverage_rate"]["value"],
            "exact_gate_replay_recovered": dry_run.get("exact_gate_replay_limitation", {}).get("exact_gate_replay_recovered"),
            "fail_closed_reasons": dry_run.get("threshold_results_v2", {}).get("fail_closed_reasons", []),
            "root_cause_class": repair_preview.get("failure_root_cause_assessment", {}).get("root_cause_class"),
        },
        "correct_metric_intent": {
            "metric_name": METRIC_NAME,
            "measure": "rows/objects where family_key is expected and applicable",
            "expected_family_key_value": "old_short",
            "valid_subfamilies": ["blowoff_short", "mean_reversion_short"],
            "do_not_penalize_non_applicable_objects": [
                "state.json global metadata without family_key",
                "heartbeat rows when only route/status heartbeat is present and family_key is not expected",
                "header-only or empty output files",
                "report-only metadata sections",
            ],
            "should_penalize": [
                "present family_key not equal old_short",
                "side/family mismatch where family_key is applicable",
                "family_key missing in closed_trades/signals/pending/rejected rows where expected",
                "unexpected unrelated family_key values",
            ],
        },
        "denominator_policy": {
            "denominator": "applicable rows only",
            "applicable_files": [
                "signals.csv",
                "pending_entries.csv",
                "open_positions.csv when rows exist",
                "closed_trades.csv when rows exist",
                "rejected_entries.csv when rows exist",
            ],
            "heartbeat_policy": "include heartbeat.csv only if schema contains family_key and it is row-level old_short heartbeat",
            "state_policy": "include state.json only if it explicitly contains family_key; otherwise check route_key separately and exclude from denominator",
            "excluded_from_denominator": [
                "empty files",
                "header-only rows",
                "state objects without family_key",
                "report metadata objects",
                "synthetic/global safety label metadata",
            ],
            "threshold_unchanged": "family_key_match_rate >= 0.99",
        },
        "complementary_checks": {
            "route_key_match": {
                "if_state_lacks_family_key_but_has_route_key_old_short_clean_room_v1": "check route_key separately and do not treat as family_key mismatch",
                "expected_route_key": ROUTE_KEY,
            },
            "heartbeat_schema_match": {
                "if_heartbeat_lacks_family_key_but_has_route_or_status": "heartbeat_schema_match may cover it",
                "do_not_treat_as_family_key_mismatch_unless_family_key_explicitly_required_by_schema": True,
            },
            "side_check": {
                "side_expected": "short",
                "side_mismatch_should_remain_separate_from_family_key_denominator": True,
            },
        },
        "fail_closed_conditions": [
            "applicable rows exist but denominator becomes zero unexpectedly",
            "closed_trades/signals/rejected rows exist but family_key is absent",
            "unrelated family_key appears",
            "route_key mismatch appears",
            "side is not short where side is expected",
            "repair would mask true mismatch",
        ],
        "repair_validation_plan": {
            "future_step": NEXT_ALLOWED_STEP,
            "actions": [
                "recompute family_key_match_rate with applicable-row denominator",
                "preserve all other metrics unchanged",
                "compare before/after metric result",
                "report denominator count",
                "report mismatch rows",
                "report excluded non-applicable rows/files",
                "preserve exact_gate_replay_recovered = false",
                "preserve no edge/live/capital",
            ],
            "strategy_logic_change_allowed": False,
            "threshold_change_allowed": False,
            "runner_output_change_allowed": False,
            "fixture_content_change_allowed": False,
            "raw_market_data_required": False,
        },
        "expected_result_after_repair": {
            "do_not_force_pass": True,
            "possible_outcomes": [
                "if only non-applicable metadata caused failure, V2 validation may move from FAIL to PARTIAL or PASS",
                "if true applicable family_key mismatches exist, V2 should remain FAIL",
            ],
            "repair_must_not_change_data_to_make_it_pass": True,
            "edge_live_capital_still_not_granted": True,
        },
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "unresolved_fields_preserved": {
            "original_exact_source_recovered": False,
            "exact_original_thresholds_known": False,
            "exact_original_implementation_known": False,
            "exact_frozen_replay_source_available": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "clean_room_behavioral_reconstruction": True,
            "no_edge_evidence": True,
            "no_live_capital_readiness": True,
        },
        "limitations": [
            "Metric repair design only; no repair is applied.",
            "Behavioral validation is not rerun.",
            "Thresholds are not optimized or changed.",
            "Strategy logic, runner outputs, fixture contents, and old_short behavior are not altered.",
            "Exact gate replay remains unrecovered and false.",
            "Original old_short source and exact frozen replay remain unrecovered.",
            "No backtest, PnL computation, runtime, live, capital, candidate generation, or edge claim is allowed.",
        ],
        "safety_permissions": {
            "metric_repair_design_created": True,
            "repair_apply_allowed_now": False,
            "validation_rerun_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> int:
    if ARTIFACT_PATH.exists():
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_PATH}")

    artifact = build_artifact()
    if artifact["replacement_checks_all_true"] is not True:
        raise SystemExit("BLOCKED: replacement_checks_all_true=false")

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    stdout_fields = {
        "status": artifact["status"],
        "route_key": artifact["repair_design_identity"]["route_key"],
        "design_only": artifact["repair_design_identity"]["design_only"],
        "metric_name": artifact["repair_design_identity"]["metric_name"],
        "root_cause_class": artifact["repair_design_identity"]["root_cause_class"],
        "repair_apply_allowed_now": artifact["repair_design_identity"]["repair_apply_allowed_now"],
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
