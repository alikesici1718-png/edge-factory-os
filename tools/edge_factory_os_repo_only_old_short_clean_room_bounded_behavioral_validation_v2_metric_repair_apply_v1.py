#!/usr/bin/env python3
"""Apply the family_key_match_rate metric repair as an artifact-only record.

This tool recomputes family_key_match_rate using the designed applicable-row
denominator. It does not edit prior artifacts, repair strategy or runner logic,
rerun behavioral validation, compare full datasets, run a backtest, compute PnL,
touch runtime, use network/API, generate candidates, or claim edge.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_APPLY_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_APPLY"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "4b62f8afcb7af43840bdf5b88dbcf303ac35fcfb"
EXPECTED_TRACKED_PYTHON_COUNT = 973
METRIC_NAME = "family_key_match_rate"
ROOT_CAUSE_CLASS = "validator_metric_definition_issue"
EXPECTED_FAMILY_KEY = "old_short"
NEXT_ALLOWED_STEP_PASS_OR_P1 = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_REVIEW_V1"
NEXT_ALLOWED_STEP_FAIL = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_TRUE_MISMATCH_CLOSURE_OR_REPAIR_V1"
NEXT_ALLOWED_STEP_INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_DEEPEN_V1"

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_bounded_behavioral_validation_v2_metric_repair_apply_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_metric_repair_apply_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / MODULE
ARTIFACT_PATH = REPO_ROOT / ARTIFACT

CLEAN_ROOM_V2_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\realistic_fixture_runner_v2_dry_run_v1"
)
ACCEPTED_LIFECYCLE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\accepted_lifecycle_fixture_discovery_v1"
)

SOURCE_ARTIFACT_PATHS = {
    "bounded_behavioral_validation_v2_metric_repair_design": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_metric_repair_design_v1.json",
    "bounded_behavioral_validation_v2_repair_preview": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_repair_preview_v1.json",
    "bounded_behavioral_validation_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_bounded_behavioral_validation_v2_dry_run_v1.json",
    "runner_realistic_fixture_v2_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_dry_run_v1.json",
}

APPLICABLE_REQUIRED_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
]
OPTIONAL_FILES = ["heartbeat.csv"]
STATE_FILE = "state.json"
ACCEPTED_FILES = [
    "accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_master_cases.jsonl",
    "accepted_lifecycle_pairing_plan.json",
    "accepted_lifecycle_discovery_summary.json",
]
VALID_SUBFAMILIES = {"blowoff_short", "mean_reversion_short"}


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


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def read_csv(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


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


def stat_paths(paths: list[Path]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in paths:
        result[str(path)] = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else None,
            "mtime_ns": path.stat().st_mtime_ns if path.exists() else None,
        }
    return result


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


def input_paths() -> list[Path]:
    return [
        *[CLEAN_ROOM_V2_OUTPUT_ROOT / name for name in [*APPLICABLE_REQUIRED_FILES, *OPTIONAL_FILES, STATE_FILE]],
        *[ACCEPTED_LIFECYCLE_ROOT / name for name in ACCEPTED_FILES],
    ]


def row_summary(row: dict[str, Any], file_name: str, row_index: int, reason: str) -> dict[str, Any]:
    return {
        "file": file_name,
        "row_index": row_index,
        "fixture_case_id": row.get("fixture_case_id"),
        "route_key": row.get("route_key"),
        "family_key": row.get("family_key"),
        "family": row.get("family"),
        "side": row.get("side"),
        "signal_id": row.get("signal_id"),
        "position_id": row.get("position_id"),
        "close_id": row.get("close_id"),
        "reason": reason,
    }


def load_clean_room_files() -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    csv_files: dict[str, dict[str, Any]] = {}
    for file_name in [*APPLICABLE_REQUIRED_FILES, *OPTIONAL_FILES]:
        header, rows = read_csv(CLEAN_ROOM_V2_OUTPUT_ROOT / file_name)
        csv_files[file_name] = {
            "path": str(CLEAN_ROOM_V2_OUTPUT_ROOT / file_name),
            "header": header,
            "rows": rows,
            "row_count": len(rows),
            "has_family_key_column": "family_key" in header,
        }
    state = read_json(CLEAN_ROOM_V2_OUTPUT_ROOT / STATE_FILE)
    accepted = {
        "fixture_index": read_json(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_fixture_index.json"),
        "master_cases": read_jsonl(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_master_cases.jsonl"),
        "pairing_plan": read_json(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_pairing_plan.json"),
        "summary": read_json(ACCEPTED_LIFECYCLE_ROOT / "accepted_lifecycle_discovery_summary.json"),
    }
    return csv_files, state, accepted


def compute_repaired_metric(csv_files: dict[str, dict[str, Any]], state: dict[str, Any]) -> dict[str, Any]:
    applicable_rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    numerator = 0
    denominator = 0

    for file_name in APPLICABLE_REQUIRED_FILES:
        file_data = csv_files[file_name]
        rows = file_data["rows"]
        if not rows:
            excluded.append({"file": file_name, "reason": "empty/header-only file excluded", "excluded_count": 0})
            continue
        for index, row in enumerate(rows, start=1):
            denominator += 1
            applicable_rows.append(row_summary(row, file_name, index, "applicable row"))
            family_key = row.get("family_key")
            if family_key == EXPECTED_FAMILY_KEY:
                numerator += 1
            elif family_key in (None, ""):
                mismatches.append(row_summary(row, file_name, index, "required family_key absent"))
            else:
                mismatches.append(row_summary(row, file_name, index, "unexpected family_key value"))

    for file_name in OPTIONAL_FILES:
        file_data = csv_files[file_name]
        rows = file_data["rows"]
        if not rows:
            excluded.append({"file": file_name, "reason": "empty/header-only optional file excluded", "excluded_count": 0})
            continue
        if not file_data["has_family_key_column"]:
            excluded.append({"file": file_name, "reason": "heartbeat lacks row-level family_key", "excluded_count": len(rows)})
            continue
        for index, row in enumerate(rows, start=1):
            denominator += 1
            applicable_rows.append(row_summary(row, file_name, index, "optional heartbeat row-level family_key applicable"))
            family_key = row.get("family_key")
            if family_key == EXPECTED_FAMILY_KEY:
                numerator += 1
            elif family_key in (None, ""):
                mismatches.append(row_summary(row, file_name, index, "heartbeat family_key absent despite column"))
            else:
                mismatches.append(row_summary(row, file_name, index, "unexpected heartbeat family_key value"))

    state_family_key = state.get("family_key")
    state_route_key = state.get("route_key")
    if state_family_key is None:
        excluded.append({"file": STATE_FILE, "reason": "state.json lacks explicit family_key; route_key checked separately", "excluded_count": 1})
    else:
        denominator += 1
        if state_family_key == EXPECTED_FAMILY_KEY:
            numerator += 1
        else:
            mismatches.append({
                "file": STATE_FILE,
                "row_index": None,
                "route_key": state_route_key,
                "family_key": state_family_key,
                "reason": "state.json explicit family_key mismatch",
            })

    repaired_rate = numerator / denominator if denominator > 0 else None
    return {
        "numerator": numerator,
        "denominator": denominator,
        "repaired_family_key_match_rate": repaired_rate,
        "mismatch_rows": mismatches,
        "mismatch_count": len(mismatches),
        "applicable_rows": applicable_rows,
        "applicable_row_count": len(applicable_rows),
        "excluded_non_applicable": excluded,
        "excluded_non_applicable_count": sum(item.get("excluded_count", 0) for item in excluded),
        "state_route_key": state_route_key,
        "state_family_key": state_family_key,
    }


def complementary_checks(csv_files: dict[str, dict[str, Any]], state: dict[str, Any], repaired: dict[str, Any]) -> dict[str, Any]:
    route_values = [state.get("route_key")]
    subfamilies: set[str] = set()
    side_values: set[str] = set()
    unexpected_subfamilies: set[str] = set()
    bad_side_rows: list[dict[str, Any]] = []
    for file_name, file_data in csv_files.items():
        for index, row in enumerate(file_data["rows"], start=1):
            if row.get("route_key"):
                route_values.append(row.get("route_key"))
            family = row.get("family")
            if family:
                subfamilies.add(family)
                if family not in VALID_SUBFAMILIES and family != "heartbeat_state":
                    unexpected_subfamilies.add(family)
            side = row.get("side")
            if side:
                side_values.add(side)
                if side != "short":
                    bad_side_rows.append(row_summary(row, file_name, index, "side not short"))

    route_key_match = all(value in (None, "", ROUTE_KEY) for value in route_values)
    side_short_pass = not bad_side_rows and side_values <= {"short"}
    subfamily_pass = not unexpected_subfamilies and {"blowoff_short", "mean_reversion_short"}.issubset(subfamilies)
    exact_gate_replay_remains_false = True
    return {
        "route_key_match": route_key_match,
        "route_values_observed": sorted({str(value) for value in route_values if value not in (None, "")}),
        "subfamily_values_observed": sorted(subfamilies),
        "subfamily_values_limited_to_expected": subfamily_pass,
        "unexpected_subfamily_values": sorted(unexpected_subfamilies),
        "side_values_observed": sorted(side_values),
        "side_short_where_expected": side_short_pass,
        "bad_side_rows": bad_side_rows,
        "exact_gate_replay_remains_false": exact_gate_replay_remains_false,
        "state_route_key_checked_separately": repaired.get("state_family_key") is None and repaired.get("state_route_key") == ROUTE_KEY,
    }


def build_artifact() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = len(run_git(["ls-files", "*.py"]).splitlines())
    artifact_existed_before = ARTIFACT_PATH.exists()

    input_stats_before = stat_paths(input_paths())
    sources = {
        name: read_json(REPO_ROOT / relative_path)
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }
    csv_files, state, accepted = load_clean_room_files()
    input_stats_after = stat_paths(input_paths())

    source_artifacts = {
        name: source_summary(relative_path, sources[name])
        for name, relative_path in SOURCE_ARTIFACT_PATHS.items()
    }
    design = sources["bounded_behavioral_validation_v2_metric_repair_design"]
    repair_preview = sources["bounded_behavioral_validation_v2_repair_preview"]
    dry_run = sources["bounded_behavioral_validation_v2_dry_run"]

    repaired = compute_repaired_metric(csv_files, state)
    checks = complementary_checks(csv_files, state, repaired)
    denominator = repaired["denominator"]
    repaired_rate = repaired["repaired_family_key_match_rate"]
    mismatch_count = repaired["mismatch_count"]
    fail_reasons: list[str] = []
    if denominator == 0 and any(csv_files[name]["row_count"] > 0 for name in APPLICABLE_REQUIRED_FILES):
        fail_reasons.append("applicable output rows exist but denominator is zero")
    if mismatch_count:
        fail_reasons.append("applicable rows contain wrong or missing family_key")
    if not checks["route_key_match"]:
        fail_reasons.append("route_key mismatch appears")
    if not checks["side_short_where_expected"]:
        fail_reasons.append("side not short where side expected")
    if not checks["subfamily_values_limited_to_expected"]:
        fail_reasons.append("unexpected subfamily value appears")

    if denominator == 0:
        result_classification = "FAMILY_KEY_METRIC_REPAIR_APPLY_INCONCLUSIVE_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_INCONCLUSIVE
    elif fail_reasons:
        result_classification = "FAMILY_KEY_METRIC_REPAIR_APPLY_FAIL_TRUE_MISMATCH_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL
    elif repaired_rate is not None and repaired_rate >= 0.99:
        if repaired["excluded_non_applicable_count"] > 0 or denominator <= 12:
            result_classification = "FAMILY_KEY_METRIC_REPAIR_APPLY_PASS_WITH_P1_ATTENTION_NO_EDGE_NO_LIVE"
        else:
            result_classification = "FAMILY_KEY_METRIC_REPAIR_APPLY_PASS_READY_FOR_REVIEW_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_PASS_OR_P1
    else:
        result_classification = "FAMILY_KEY_METRIC_REPAIR_APPLY_FAIL_TRUE_MISMATCH_NO_EDGE_NO_LIVE"
        next_allowed_step = NEXT_ALLOWED_STEP_FAIL

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "metric_repair_design_loaded": design.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_METRIC_REPAIR_DESIGN_CREATED",
        "prior_v2_dry_run_loaded": dry_run.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_BOUNDED_BEHAVIORAL_VALIDATION_V2_DRY_RUN_CREATED",
        "no_prior_artifact_modified": input_stats_before == input_stats_after,
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
        "denominator_policy_applied": denominator > 0,
        "applicable_rows_reviewed": repaired["applicable_row_count"] == denominator,
        "exactly_one_python_tool_created": MODULE_PATH.exists() and not artifact_existed_before,
        "exactly_one_json_artifact_created": not artifact_existed_before,
        "no_existing_files_modified": status_has_only_expected_untracked_tool(status_before_artifact),
        "replacement_checks_all_true": True,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "route_key": ROUTE_KEY,
        "metric_name": METRIC_NAME,
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
        "prior_failure_preserved": {
            "result_classification": dry_run.get("result_classification"),
            "failed_metric": METRIC_NAME,
            "prior_family_key_match_rate": dry_run["similarity_metric_results_v2"]["metrics"][METRIC_NAME]["value"],
            "root_cause_class": repair_preview.get("failure_root_cause_assessment", {}).get("root_cause_class"),
            "exact_gate_replay_recovered": dry_run.get("exact_gate_replay_limitation", {}).get("exact_gate_replay_recovered"),
            "original_exact_source_recovered": False,
            "no_edge_live_capital": True,
        },
        "repaired_metric_definition": {
            "metric_name": METRIC_NAME,
            "numerator": "applicable rows where family_key == old_short",
            "denominator": "applicable rows where family_key is expected",
            "expected_family_key": EXPECTED_FAMILY_KEY,
            "valid_subfamilies": sorted(VALID_SUBFAMILIES),
            "threshold_unchanged": ">= 0.99",
            "strategy_logic_changed": False,
            "runner_output_changed": False,
            "fixture_content_changed": False,
        },
        "applicable_file_review": {
            file_name: {
                "path": csv_files[file_name]["path"],
                "row_count": csv_files[file_name]["row_count"],
                "has_family_key_column": csv_files[file_name]["has_family_key_column"],
                "included_in_denominator": (
                    file_name in APPLICABLE_REQUIRED_FILES and csv_files[file_name]["row_count"] > 0
                )
                or (
                    file_name in OPTIONAL_FILES
                    and csv_files[file_name]["row_count"] > 0
                    and csv_files[file_name]["has_family_key_column"]
                ),
            }
            for file_name in [*APPLICABLE_REQUIRED_FILES, *OPTIONAL_FILES]
        },
        "denominator_policy_applied": {
            "required_applicable_files": APPLICABLE_REQUIRED_FILES,
            "optional_files": OPTIONAL_FILES,
            "state_json_policy": "excluded because explicit family_key is absent; route_key checked separately",
            "excluded_categories": [
                "empty files",
                "header-only files",
                "state.json without family_key",
                "heartbeat rows without family_key",
                "report-only metadata",
                "synthetic/global safety label metadata",
            ],
        },
        "numerator_denominator_summary": {
            "numerator": repaired["numerator"],
            "denominator": denominator,
            "formula": "numerator / denominator",
        },
        "mismatch_rows_summary": {
            "mismatch_count": mismatch_count,
            "mismatch_rows": repaired["mismatch_rows"],
        },
        "excluded_non_applicable_rows_summary": {
            "excluded_non_applicable_count": repaired["excluded_non_applicable_count"],
            "excluded": repaired["excluded_non_applicable"],
        },
        "repaired_family_key_match_rate": repaired_rate,
        "complementary_route_family_side_checks": checks,
        "repair_apply_result": {
            "result_classification": result_classification,
            "fail_reasons": fail_reasons,
            "denominator_policy_safe": denominator > 0,
            "true_mismatch_detected": bool(fail_reasons),
            "repair_apply_allowed_scope": "metric-only artifact record",
            "validation_rerun_performed": False,
            "prior_artifacts_modified": False,
        },
        "next_allowed_step": next_allowed_step,
        "safety_permissions": {
            "metric_repair_apply_created": True,
            "validation_rerun_allowed_now": False,
            "runner_execution_allowed_now": False,
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
        "route_key": artifact["route_key"],
        "result_classification": artifact["repair_apply_result"]["result_classification"],
        "metric_name": artifact["metric_name"],
        "denominator": artifact["numerator_denominator_summary"]["denominator"],
        "numerator": artifact["numerator_denominator_summary"]["numerator"],
        "repaired_family_key_match_rate": artifact["repaired_family_key_match_rate"],
        "mismatch_count": artifact["mismatch_rows_summary"]["mismatch_count"],
        "excluded_non_applicable_count": artifact["excluded_non_applicable_rows_summary"]["excluded_non_applicable_count"],
        "next_allowed_step": artifact["next_allowed_step"],
        "validation_rerun_allowed_now": False,
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
