#!/usr/bin/env python3
"""Repo-only old_short clean-room bounded-sample validator dry run v2.

This module performs a bounded dry run against MASTER_UPPER_SYSTEM proxy
samples and previously generated synthetic clean-room schema samples. It does
not run old_short, a runner, a full validator, a backtest, a strategy, runtime,
live trading, orders, capital allocation, candidate generation, or edge claims.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
SAFE_DIRECTORY = "C:/Users/alike/OneDrive/Desktop/edge_lab_new/edge_factory_os_repo"

MODULE = "edge_factory_os_repo_only_old_short_clean_room_validator_bounded_sample_dry_run_v2"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_validator_bounded_sample_dry_run_v2.py"
ARTIFACT_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_bounded_sample_dry_run_v2.json"
)

CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
VALIDATOR_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"
BOUNDED_DRY_RUN_V1_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_bounded_sample_dry_run_v1.json"
)
SAMPLE_OUTPUT_GENERATION_PREVIEW_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_sample_output_generation_preview_v1.json"
)
SCHEMA_GENERATOR_PREVIEW_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_schema_sample_generator_preview_v1.json"
)
SCHEMA_GENERATOR_DRY_RUN_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_schema_sample_generator_dry_run_v1.json"
)

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
BOUNDED_DRY_RUN_V1_PATH = REPO_ROOT / BOUNDED_DRY_RUN_V1_REL
SAMPLE_OUTPUT_GENERATION_PREVIEW_PATH = REPO_ROOT / SAMPLE_OUTPUT_GENERATION_PREVIEW_REL
SCHEMA_GENERATOR_PREVIEW_PATH = REPO_ROOT / SCHEMA_GENERATOR_PREVIEW_REL
SCHEMA_GENERATOR_DRY_RUN_PATH = REPO_ROOT / SCHEMA_GENERATOR_DRY_RUN_REL

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V2_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V2"
ROUTE_KEY = "old_short_clean_room_v1"
VALIDATOR_KEY = "old_short_clean_room_validator_v1"
EXPECTED_NEXT_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V2"

MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
SYNTHETIC_SAMPLE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_sample_outputs_v1"
    r"\schema_sample_generator_dry_run_v1"
)

EXPECTED_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

SIMILARITY_METRICS = [
    "schema_match_rate",
    "family_key_match_rate",
    "side_match_rate",
    "entry_delay_median_abs_error_seconds",
    "hold_minutes_median_abs_error",
    "notional_median_abs_error",
    "closed_trade_schema_compatibility",
    "rejected_entry_reason_overlap",
    "signal_feature_distribution_similarity",
    "timestamp_alignment_rate",
    "coin_overlap_rate",
    "gate_behavior_consistency_rate",
]

SAFE_SCHEMA_LEVEL_METRICS = {
    "schema_match_rate",
    "family_key_match_rate",
    "side_match_rate",
    "closed_trade_schema_compatibility",
}

BEHAVIORAL_METRICS_NOT_VALID_FOR_SYNTHETIC = [
    "entry_delay_median_abs_error_seconds",
    "hold_minutes_median_abs_error",
    "notional_median_abs_error",
    "rejected_entry_reason_overlap",
    "signal_feature_distribution_similarity",
    "timestamp_alignment_rate",
    "coin_overlap_rate",
    "gate_behavior_consistency_rate",
]

SYNTHETIC_LABELS = [
    "GENERATED_CLEAN_ROOM_SAMPLE",
    "SYNTHETIC_SCHEMA_SAMPLE",
    "NOT_ORIGINAL_OUTPUT",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
]

FORBIDDEN_LIVE_ORDER_PRIVATE_FIELDS = [
    "api_key",
    "api_secret",
    "passphrase",
    "order_id",
    "client_order_id",
    "live_order_id",
    "exchange_order_id",
    "fill_id",
    "private_endpoint",
    "account_id",
    "subaccount",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

MAX_MASTER_SAMPLE_ROWS = 100
SAFE_JSON_BYTES = 250_000
SAFE_SYNTHETIC_BYTES = 500_000


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_output(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={SAFE_DIRECTORY}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_status_lines() -> list[str]:
    out = git_output(["status", "--short", "--untracked-files=all"])
    return [] if not out else out.splitlines()


def normalize_status_path(line: str) -> str:
    return line[3:].strip().strip('"').replace("\\", "/")


def status_code(line: str) -> str:
    return line[:2]


def fail_closed(reason: str, details: dict[str, Any] | None = None) -> None:
    payload = {
        "status": "BLOCKED",
        "reason": reason,
        "details": details or {},
        "replacement_checks_all_true": False,
        "next_module": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V2_BLOCKER_REVIEW",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(1)


def preflight_repo_status() -> dict[str, Any]:
    lines = git_status_lines()
    allowed_untracked = {TOOL_REL, ARTIFACT_REL}
    dirty_tracked = [line for line in lines if status_code(line) != "??"]
    unexpected_untracked = [
        line
        for line in lines
        if status_code(line) == "??" and normalize_status_path(line) not in allowed_untracked
    ]
    target_tool_is_new = any(
        status_code(line) == "??" and normalize_status_path(line) == TOOL_REL for line in lines
    )
    return {
        "status_lines_before_run": lines,
        "dirty_tracked_before_run": dirty_tracked,
        "unexpected_untracked_before_run": unexpected_untracked,
        "repo_clean_before_run": not dirty_tracked and not unexpected_untracked,
        "no_existing_repo_files_modified": not dirty_tracked,
        "target_tool_present_as_new_untracked_file": target_tool_is_new and TOOL_PATH.exists(),
        "target_artifact_preexisting_before_run": ARTIFACT_PATH.exists(),
    }


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        fail_closed(f"{label}_MISSING", {"path": str(path)})
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail_closed(f"{label}_LOAD_FAILED", {"path": str(path), "error": repr(exc)})
    if not isinstance(data, dict):
        fail_closed(f"{label}_NOT_JSON_OBJECT", {"path": str(path)})
    return data


def ensure_prior_artifacts(prior: dict[str, dict[str, Any]]) -> None:
    checks = {
        "contract_status": prior["contract"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED",
        "runner_preview_status": prior["runner_preview"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED",
        "validator_preview_status": prior["validator_preview"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED",
        "bounded_dry_run_v1_status": prior["bounded_dry_run_v1"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_CREATED",
        "sample_output_generation_preview_status": prior["sample_output_generation_preview"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW_CREATED",
        "schema_generator_preview_status": prior["schema_generator_preview"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_PREVIEW_CREATED",
        "schema_generator_dry_run_status": prior["schema_generator_dry_run"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_DRY_RUN_CREATED",
        "schema_generator_dry_run_next_allowed_step": prior["schema_generator_dry_run"].get(
            "next_allowed_step"
        )
        == EXPECTED_NEXT_STEP,
    }
    if not all(checks.values()):
        fail_closed("PRIOR_ARTIFACT_STATUS_CHECK_FAILED", checks)

    v1 = prior["bounded_dry_run_v1"]
    v1_checks = {
        "v1_inconclusive": v1.get("result_classification")
        == "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
        "v1_missing_clean_room_sample": v1.get("clean_room_sample_review", {}).get(
            "clean_room_sample_available"
        )
        is False,
        "v1_next_step": v1.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW_V1",
    }
    if not all(v1_checks.values()):
        fail_closed("PREVIOUS_V1_INCONCLUSIVE_CAUSE_NOT_VERIFIED", v1_checks)

    identity_checks = {
        "contract_route_key": prior["contract"].get("clean_room_identity", {}).get("route_key")
        == ROUTE_KEY,
        "runner_route_key": prior["runner_preview"].get("clean_room_runner_identity", {}).get(
            "route_key"
        )
        == ROUTE_KEY,
        "validator_route_key": prior["validator_preview"].get("validator_identity", {}).get(
            "route_key"
        )
        == ROUTE_KEY,
        "validator_key": prior["validator_preview"].get("validator_identity", {}).get("validator_key")
        == VALIDATOR_KEY,
        "schema_dry_run_original_not_recovered": prior["schema_generator_dry_run"].get(
            "validator_usage_limitations", {}
        ).get("original_exact_source_recovered")
        is False,
        "contract_original_not_recovered": prior["contract"].get("clean_room_identity", {}).get(
            "original_exact_source_recovered"
        )
        is False,
        "validator_behavioral_only": prior["validator_preview"].get("validator_identity", {}).get(
            "behavioral_validation_only"
        )
        is True,
    }
    if not all(identity_checks.values()):
        fail_closed("PRIOR_IDENTITY_CHECK_FAILED", identity_checks)

    permissions = prior["schema_generator_dry_run"].get("safety_permissions", {})
    permission_checks = {
        "runner_execution_allowed_now": permissions.get("runner_execution_allowed_now") is False,
        "validator_execution_allowed_now": permissions.get("validator_execution_allowed_now") is False,
        "backtest_allowed_now": permissions.get("backtest_allowed_now") is False,
        "runtime_permission_allowed_now": permissions.get("runtime_permission_allowed_now") is False,
        "live_permission_allowed_now": permissions.get("live_permission_allowed_now") is False,
        "capital_permission_allowed_now": permissions.get("capital_permission_allowed_now") is False,
        "candidate_generation_allowed_now": permissions.get("candidate_generation_allowed_now") is False,
        "edge_claim_allowed_now": permissions.get("edge_claim_allowed_now") is False,
    }
    if not all(permission_checks.values()):
        fail_closed("NO_LIVE_PERMISSION_CHECK_FAILED", permission_checks)


def required_fields(schema: Any) -> list[str]:
    if isinstance(schema, list):
        return [str(item) for item in schema]
    if isinstance(schema, dict):
        fields = schema.get("required_top_level_keys")
        if isinstance(fields, list):
            return [str(item) for item in fields]
    return []


def expected_master_schema_map(prior: dict[str, dict[str, Any]]) -> dict[str, Any]:
    contract_schema = prior["contract"].get("output_schema_contract", {})
    runner_schema = prior["runner_preview"].get("output_schema_preview", {})
    schema_map: dict[str, Any] = {}
    for name in EXPECTED_FILES:
        schema: Any = []
        if isinstance(runner_schema, dict) and isinstance(runner_schema.get(name), dict):
            schema = runner_schema[name].get("contract_schema", [])
        if not schema and isinstance(contract_schema, dict):
            schema = contract_schema.get(name, [])
        schema_map[name] = schema
    return schema_map


def expected_synthetic_schema_map(prior: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    file_schemas = prior["schema_generator_dry_run"].get("sample_file_schemas", {})
    schema_map: dict[str, list[str]] = {}
    for name in EXPECTED_FILES:
        schema_record = file_schemas.get(name, {}) if isinstance(file_schemas, dict) else {}
        headers = schema_record.get("header_or_keys", [])
        if not isinstance(headers, list):
            headers = []
        schema_map[name] = [str(item) for item in headers]
    return schema_map


def sample_csv(path: Path, row_limit: int | None) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            header = list(reader.fieldnames or [])
            for row in reader:
                if row_limit is not None and len(rows) >= row_limit:
                    break
                rows.append({str(k): str(v) for k, v in row.items()})
    except Exception as exc:
        return {
            "kind": "csv",
            "header": [],
            "sample_rows": [],
            "row_count_sampled": 0,
            "read_error": repr(exc),
            "sample_limit_enforced": True,
        }
    return analyze_sample("csv", header, rows, row_limit, None)


def sample_json(path: Path, safe_bytes: int) -> dict[str, Any]:
    if path.stat().st_size > safe_bytes:
        return {
            "kind": "json",
            "header": [],
            "top_level_keys": [],
            "sample_rows": [],
            "row_count_sampled": 0,
            "read_error": "json_above_safe_sample_bytes",
            "sample_limit_enforced": True,
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "kind": "json",
            "header": [],
            "top_level_keys": [],
            "sample_rows": [],
            "row_count_sampled": 0,
            "read_error": repr(exc),
            "sample_limit_enforced": True,
        }
    if not isinstance(data, dict):
        return {
            "kind": "json",
            "header": [],
            "top_level_keys": [],
            "sample_rows": [],
            "row_count_sampled": 0,
            "read_error": "json_not_object",
            "sample_limit_enforced": True,
        }
    return analyze_sample("json", sorted(data.keys()), [{str(k): v for k, v in data.items()}], None, sorted(data.keys()))


def analyze_sample(
    kind: str,
    header: list[str],
    rows: list[dict[str, Any]],
    row_limit: int | None,
    top_level_keys: list[str] | None,
) -> dict[str, Any]:
    header_lower = {str(field).lower() for field in header}
    forbidden = sorted(set(FORBIDDEN_LIVE_ORDER_PRIVATE_FIELDS).intersection(header_lower))
    family_key_values: list[str] = []
    side_values: list[str] = []
    families: set[str] = set()
    timestamp_fields = [field for field in header if "time" in str(field).lower()]
    labels_present = False
    for row in rows:
        family_key = str(row.get("family_key", "")).strip()
        side = str(row.get("side", "")).strip()
        family = str(row.get("family", "") or row.get("strategy", "")).strip()
        if family_key:
            family_key_values.append(family_key)
        if side:
            side_values.append(side)
        if family:
            families.add(family)
        labels = row.get("safety_labels")
        if isinstance(labels, list):
            labels_present = labels_present or set(SYNTHETIC_LABELS).issubset(set(map(str, labels)))
        else:
            labels_present = labels_present or set(SYNTHETIC_LABELS).issubset(set(str(labels).split("|")))
    return {
        "kind": kind,
        "header": header,
        "top_level_keys": top_level_keys or [],
        "sample_rows": rows,
        "row_count_sampled": len(rows),
        "sample_limit": row_limit,
        "sample_limit_enforced": row_limit is None or len(rows) <= row_limit,
        "family_key_old_short_detected": "old_short" in family_key_values,
        "side_short_detected": "short" in side_values,
        "family_key_values": family_key_values,
        "side_values": side_values,
        "families_detected": sorted(families),
        "blowoff_short_detected": "blowoff_short" in families,
        "mean_reversion_short_detected": "mean_reversion_short" in families,
        "timestamp_fields_detected": timestamp_fields,
        "synthetic_labels_detected": labels_present,
        "live_order_private_fields_detected": forbidden,
        "read_error": None,
    }


def review_dir(path: Path, label: str, synthetic: bool) -> dict[str, Any]:
    files: dict[str, Any] = {}
    found_count = 0
    any_forbidden = False
    row_limit = None if synthetic else MAX_MASTER_SAMPLE_ROWS
    safe_bytes = SAFE_SYNTHETIC_BYTES if synthetic else SAFE_JSON_BYTES
    for name in EXPECTED_FILES:
        file_path = path / name
        record: dict[str, Any] = {
            "name": name,
            "path": str(file_path),
            "exists": file_path.exists(),
            "synthetic_sample_source": synthetic,
        }
        if file_path.exists():
            found_count += 1
            record["size_bytes"] = file_path.stat().st_size
            if name.endswith(".csv"):
                record.update(sample_csv(file_path, row_limit))
            elif name.endswith(".json"):
                record.update(sample_json(file_path, safe_bytes))
            else:
                record.update({"read_error": "unexpected_extension", "sample_rows": [], "header": []})
            if record.get("live_order_private_fields_detected"):
                any_forbidden = True
        files[name] = record
    return {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
        "files_found_count": found_count,
        "expected_file_count": len(EXPECTED_FILES),
        "files": files,
        "any_live_order_private_fields_detected": any_forbidden,
        "sample_row_policy": "all_synthetic_rows" if synthetic else f"first_{MAX_MASTER_SAMPLE_ROWS}_rows_only",
    }


def schema_match_for_review(
    review: dict[str, Any],
    schema_map: dict[str, Any],
    schema_basis: str,
) -> dict[str, Any]:
    per_file: dict[str, Any] = {}
    matched = 0
    required_total = 0
    for name, record in review.get("files", {}).items():
        expected = required_fields(schema_map.get(name)) if schema_basis != "generated_schema" else schema_map.get(name, [])
        expected_set = {str(item) for item in expected}
        observed = record.get("top_level_keys") or record.get("header") or []
        observed_set = {str(item) for item in observed}
        file_matched = len(expected_set.intersection(observed_set))
        file_required = len(expected_set)
        matched += file_matched
        required_total += file_required
        per_file[name] = {
            "exists": record.get("exists"),
            "schema_basis": schema_basis,
            "required_count": file_required,
            "matched_required_count": file_matched,
            "schema_match_rate": (file_matched / file_required) if file_required else None,
            "missing_required": sorted(expected_set.difference(observed_set)),
            "live_order_private_fields_detected": record.get("live_order_private_fields_detected", []),
        }
    return {
        "schema_basis": schema_basis,
        "per_file": per_file,
        "schema_match_rate": (matched / required_total) if required_total else None,
        "matched_required_count": matched,
        "required_count": required_total,
        "no_live_order_private_fields": not review.get("any_live_order_private_fields_detected", False),
    }


def audit_synthetic_labels(review: dict[str, Any]) -> dict[str, Any]:
    per_file: dict[str, Any] = {}
    all_present = True
    for name, record in review.get("files", {}).items():
        labels_present = False
        if record.get("exists") and not record.get("read_error"):
            if name.endswith(".json"):
                row = (record.get("sample_rows") or [{}])[0]
                labels = row.get("safety_labels", [])
                if isinstance(labels, list):
                    labels_present = set(SYNTHETIC_LABELS).issubset(set(map(str, labels)))
            else:
                rows = record.get("sample_rows") or []
                if rows:
                    labels_present = all(
                        set(SYNTHETIC_LABELS).issubset(set(str(row.get("safety_labels", "")).split("|")))
                        for row in rows
                    )
        all_present = all_present and labels_present
        per_file[name] = {
            "exists": record.get("exists"),
            "labels_present": labels_present,
            "required_labels": SYNTHETIC_LABELS,
        }
    return {"all_labels_present": all_present, "per_file": per_file}


def gather_values(review: dict[str, Any], field: str, file_names: list[str] | None = None) -> list[str]:
    values: list[str] = []
    names = file_names or EXPECTED_FILES
    for name in names:
        rows = review.get("files", {}).get(name, {}).get("sample_rows", [])
        for row in rows:
            value = str(row.get(field, "")).strip()
            if value:
                values.append(value)
    return values


def exact_match_rate(values: list[str], expected: str) -> dict[str, Any]:
    if not values:
        return {"computed": False, "reason": "no_values_available"}
    matches = sum(1 for value in values if value == expected)
    return {"computed": True, "value": matches / len(values), "sample_count": len(values)}


def build_similarity_metrics(
    synthetic_review: dict[str, Any],
    combined_schema_match_rate: float | None,
    synthetic_schema_results: dict[str, Any],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    metrics["schema_match_rate"] = {
        "computed": combined_schema_match_rate is not None,
        "value": combined_schema_match_rate,
        "reason": None if combined_schema_match_rate is not None else "schema_match_rate_unavailable",
        "safe_schema_level_metric": True,
    }
    metrics["family_key_match_rate"] = exact_match_rate(gather_values(synthetic_review, "family_key"), "old_short")
    metrics["family_key_match_rate"]["safe_schema_level_metric"] = True
    metrics["side_match_rate"] = exact_match_rate(gather_values(synthetic_review, "side"), "short")
    metrics["side_match_rate"]["safe_schema_level_metric"] = True
    closed_result = synthetic_schema_results.get("per_file", {}).get("closed_trades.csv", {})
    closed_rate = closed_result.get("schema_match_rate")
    metrics["closed_trade_schema_compatibility"] = {
        "computed": closed_rate is not None,
        "value": closed_rate,
        "reason": None if closed_rate is not None else "closed_trade_schema_unavailable",
        "safe_schema_level_metric": True,
    }
    for metric in BEHAVIORAL_METRICS_NOT_VALID_FOR_SYNTHETIC:
        metrics[metric] = {
            "computed": False,
            "reason": "not_behaviorally_valid_due_synthetic_sample",
            "safe_schema_level_metric": False,
        }
    return {name: metrics[name] for name in SIMILARITY_METRICS}


def classify_result(
    synthetic_root_exists: bool,
    all_synthetic_files_found: bool,
    synthetic_labels_verified: bool,
    synthetic_schema_match_rate: float | None,
    no_forbidden_synthetic_fields: bool,
    previous_v1_resolved: bool,
) -> tuple[str, str, str]:
    if not synthetic_root_exists:
        return (
            "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
            "SYNTHETIC_SAMPLE_ROOT_MISSING",
            "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_REPAIR_PREVIEW_V1",
        )
    if not all_synthetic_files_found:
        return (
            "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
            "SYNTHETIC_SAMPLE_FILES_MISSING",
            "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_REPAIR_PREVIEW_V1",
        )
    if not synthetic_labels_verified or not no_forbidden_synthetic_fields:
        return (
            "CLEAN_ROOM_VALIDATOR_DRY_RUN_FAIL_NO_EDGE_NO_LIVE",
            "SYNTHETIC_SAFETY_LABEL_OR_FIELD_CHECK_FAILED",
            "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_REPAIR_PREVIEW_V1",
        )
    if synthetic_schema_match_rate is not None and synthetic_schema_match_rate >= 0.95 and previous_v1_resolved:
        return (
            "CLEAN_ROOM_VALIDATOR_DRY_RUN_SCHEMA_PLUMBING_PASS_NO_EDGE_NO_LIVE",
            "SYNTHETIC_SCHEMA_PLUMBING_PASS_BEHAVIOR_NOT_VALIDATED",
            "OLD_SHORT_CLEAN_ROOM_RUNNER_IMPLEMENTATION_PREVIEW_V1",
        )
    if synthetic_schema_match_rate is not None and synthetic_schema_match_rate > 0.0:
        return (
            "CLEAN_ROOM_VALIDATOR_DRY_RUN_SCHEMA_PLUMBING_PARTIAL_NO_EDGE_NO_LIVE",
            "SYNTHETIC_SCHEMA_OPTIONAL_DIFFERENCES_REMAIN",
            "OLD_SHORT_CLEAN_ROOM_RUNNER_IMPLEMENTATION_PREVIEW_V1",
        )
    return (
        "CLEAN_ROOM_VALIDATOR_DRY_RUN_FAIL_NO_EDGE_NO_LIVE",
        "SYNTHETIC_SCHEMA_CRITICAL_FAILURE",
        "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_REPAIR_PREVIEW_V1",
    )


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_payload() -> dict[str, Any]:
    preflight = preflight_repo_status()
    if not preflight["repo_clean_before_run"] or not preflight["no_existing_repo_files_modified"]:
        fail_closed("DIRTY_OR_UNEXPECTED_REPO_STATE_BEFORE_RUN", preflight)
    if not preflight["target_tool_present_as_new_untracked_file"]:
        fail_closed("TARGET_TOOL_NOT_THE_SINGLE_NEW_PYTHON_TOOL", preflight)
    if preflight["target_artifact_preexisting_before_run"]:
        fail_closed("TARGET_ARTIFACT_ALREADY_EXISTS", preflight)

    prior = {
        "contract": load_json(CONTRACT_PATH, "CLEAN_ROOM_CONTRACT"),
        "runner_preview": load_json(RUNNER_PREVIEW_PATH, "RUNNER_PREVIEW"),
        "validator_preview": load_json(VALIDATOR_PREVIEW_PATH, "VALIDATOR_PREVIEW"),
        "bounded_dry_run_v1": load_json(BOUNDED_DRY_RUN_V1_PATH, "BOUNDED_DRY_RUN_V1"),
        "sample_output_generation_preview": load_json(
            SAMPLE_OUTPUT_GENERATION_PREVIEW_PATH, "SAMPLE_OUTPUT_GENERATION_PREVIEW"
        ),
        "schema_generator_preview": load_json(SCHEMA_GENERATOR_PREVIEW_PATH, "SCHEMA_GENERATOR_PREVIEW"),
        "schema_generator_dry_run": load_json(SCHEMA_GENERATOR_DRY_RUN_PATH, "SCHEMA_GENERATOR_DRY_RUN"),
    }
    ensure_prior_artifacts(prior)

    master_schema_map = expected_master_schema_map(prior)
    synthetic_schema_map = expected_synthetic_schema_map(prior)
    master_review = review_dir(MASTER_UPPER_SYSTEM_PATH, "MASTER_UPPER_SYSTEM_PROXY_BOUNDED_SAMPLE", False)
    synthetic_review = review_dir(SYNTHETIC_SAMPLE_ROOT, "SYNTHETIC_CLEAN_ROOM_SCHEMA_SAMPLE", True)
    synthetic_label_audit = audit_synthetic_labels(synthetic_review)

    master_schema_results = schema_match_for_review(
        master_review, master_schema_map, "contract_runner_validator_expected_schema"
    )
    synthetic_schema_results = schema_match_for_review(
        synthetic_review, synthetic_schema_map, "generated_schema"
    )
    master_rate = master_schema_results.get("schema_match_rate")
    synthetic_rate = synthetic_schema_results.get("schema_match_rate")
    available_rates = [rate for rate in [master_rate, synthetic_rate] if isinstance(rate, (int, float))]
    combined_rate = sum(available_rates) / len(available_rates) if available_rates else None

    metrics = build_similarity_metrics(synthetic_review, combined_rate, synthetic_schema_results)
    computed_metric_count = sum(1 for item in metrics.values() if item.get("computed"))
    missing_behavioral_metric_count = sum(
        1
        for name, item in metrics.items()
        if name not in SAFE_SCHEMA_LEVEL_METRICS
        and not item.get("computed")
        and item.get("reason") == "not_behaviorally_valid_due_synthetic_sample"
    )

    all_synthetic_files_found = synthetic_review["files_found_count"] == len(EXPECTED_FILES)
    no_forbidden_synthetic_fields = not synthetic_review.get("any_live_order_private_fields_detected", False)
    result_classification, classification_reason, next_allowed_step = classify_result(
        synthetic_review["exists"],
        all_synthetic_files_found,
        synthetic_label_audit["all_labels_present"],
        synthetic_rate,
        no_forbidden_synthetic_fields,
        True,
    )

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "prior_clean_room_artifacts_loaded": True,
        "schema_sample_generator_dry_run_loaded": True,
        "synthetic_output_root_exists": bool(synthetic_review["exists"]),
        "all_7_synthetic_files_found": bool(all_synthetic_files_found),
        "previous_v1_inconclusive_due_missing_sample_verified": True,
        "original_exact_source_not_claimed": True,
        "behavioral_validation_limitations_preserved": True,
        "synthetic_labels_verified": bool(synthetic_label_audit["all_labels_present"]),
        "no_full_dataset_comparison": True,
        "sample_row_limit_enforced": all(
            file.get("sample_limit_enforced", True)
            for file in master_review.get("files", {}).values()
        ),
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_orders_placed": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_live_order_private_fields_detected_or_flagged": bool(no_forbidden_synthetic_fields),
        "unresolved_fields_preserved": len(UNRESOLVED_FIELDS) == 5,
        "exactly_one_python_tool_created": bool(preflight["target_tool_present_as_new_untracked_file"]),
        "exactly_one_json_artifact_created": not preflight["target_artifact_preexisting_before_run"],
        "no_existing_repo_files_modified": bool(preflight["no_existing_repo_files_modified"]),
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        fail_closed("VALIDATION_CHECKS_FAILED_BEFORE_ARTIFACT_WRITE", validation_checks)

    safety_permissions = {
        "bounded_sample_dry_run_v2_created": True,
        "validator_execution_allowed_now": False,
        "full_dataset_comparison_allowed_now": False,
        "backtest_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
    }

    head = git_output(["rev-parse", "HEAD"])
    subject = git_output(["log", "-1", "--format=%s"])

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "git_head": head,
            "git_head_subject": subject,
            "generated_at_utc": utc_now(),
            "preflight_repo_status": preflight,
        },
        "source_artifacts": {
            key: {
                "path": rel,
                "status": value.get("status"),
                "artifact_kind": value.get("artifact_kind"),
                "payload_sha256_excluding_hash": value.get("payload_sha256_excluding_hash"),
                "loaded": True,
            }
            for key, rel, value in [
                ("contract", CONTRACT_REL, prior["contract"]),
                ("runner_preview", RUNNER_PREVIEW_REL, prior["runner_preview"]),
                ("validator_preview", VALIDATOR_PREVIEW_REL, prior["validator_preview"]),
                ("bounded_dry_run_v1", BOUNDED_DRY_RUN_V1_REL, prior["bounded_dry_run_v1"]),
                (
                    "sample_output_generation_preview",
                    SAMPLE_OUTPUT_GENERATION_PREVIEW_REL,
                    prior["sample_output_generation_preview"],
                ),
                ("schema_generator_preview", SCHEMA_GENERATOR_PREVIEW_REL, prior["schema_generator_preview"]),
                ("schema_generator_dry_run", SCHEMA_GENERATOR_DRY_RUN_REL, prior["schema_generator_dry_run"]),
            ]
        },
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "validator_key": VALIDATOR_KEY,
            "bounded_sample_dry_run_v2_only": True,
            "full_validator_execution": False,
            "full_dataset_comparison": False,
            "exact_original_source_recovered": False,
            "behavioral_validation_only": False,
            "schema_plumbing_validation_only": True,
            "synthetic_sample_behavioral_similarity_claim_allowed": False,
            "no_exact_replay_claim": True,
        },
        "master_sample_review": master_review,
        "synthetic_clean_room_sample_review": {
            "synthetic_sample_root": str(SYNTHETIC_SAMPLE_ROOT),
            "synthetic_sample_root_exists": synthetic_review["exists"],
            "synthetic_sample_files_found_count": synthetic_review["files_found_count"],
            "synthetic_label_audit": synthetic_label_audit,
            "review": synthetic_review,
        },
        "schema_check_results": {
            "master_schema_match_rate": master_rate,
            "synthetic_schema_match_rate": synthetic_rate,
            "combined_schema_match_rate": combined_rate,
            "master": master_schema_results,
            "synthetic": synthetic_schema_results,
            "schema_plumbing_pass_basis": "synthetic_generated_schema_and_safety_labels_only",
        },
        "similarity_metric_results": metrics,
        "synthetic_sample_limitations": [
            "synthetic sample validates schema plumbing and safety labels only",
            "synthetic sample does not prove behavioral similarity",
            "synthetic sample does not prove edge",
            "synthetic sample does not recover original old_short source",
            "synthetic sample is not exact frozen replay",
            "synthetic sample is not real strategy output",
            "behavioral metrics are intentionally not computed",
        ],
        "result_classification": result_classification,
        "classification_reason": classification_reason,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_artifact(payload)
    stdout_fields = {
        "status": payload["status"],
        "route_key": payload["dry_run_identity"]["route_key"],
        "validator_key": payload["dry_run_identity"]["validator_key"],
        "result_classification": payload["result_classification"],
        "master_sample_files_found_count": payload["master_sample_review"]["files_found_count"],
        "synthetic_sample_files_found_count": payload["synthetic_clean_room_sample_review"][
            "synthetic_sample_files_found_count"
        ],
        "synthetic_labels_verified": payload["synthetic_clean_room_sample_review"][
            "synthetic_label_audit"
        ]["all_labels_present"],
        "combined_schema_match_rate_if_available": payload["schema_check_results"][
            "combined_schema_match_rate"
        ],
        "computed_similarity_metric_count": sum(
            1 for item in payload["similarity_metric_results"].values() if item.get("computed")
        ),
        "missing_behavioral_metric_count": sum(
            1
            for item in payload["similarity_metric_results"].values()
            if item.get("reason") == "not_behaviorally_valid_due_synthetic_sample"
        ),
        "next_allowed_step": payload["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
    }
    for key, value in stdout_fields.items():
        print(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
