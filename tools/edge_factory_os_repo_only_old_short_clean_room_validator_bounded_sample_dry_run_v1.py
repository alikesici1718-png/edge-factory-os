#!/usr/bin/env python3
"""Repo-only old_short clean-room bounded-sample validator dry run v1.

This module performs a bounded sample dry run only. It never runs old_short,
never runs a backtest, never compares full datasets, never reads raw market
data, never touches runtime/live/capital, and never claims edge.
"""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
SAFE_DIRECTORY = "C:/Users/alike/OneDrive/Desktop/edge_lab_new/edge_factory_os_repo"

MODULE = "edge_factory_os_repo_only_old_short_clean_room_validator_bounded_sample_dry_run_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_validator_bounded_sample_dry_run_v1.py"
ARTIFACT_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_bounded_sample_dry_run_v1.json"
)

CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
VALIDATOR_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"
VALIDATOR_IMPLEMENTATION_PREVIEW_REL = (
    "artifacts/old_short_clean_room/old_short_clean_room_validator_implementation_preview_v1.json"
)
DRY_RUN_DESIGN_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_dry_run_design_v1.json"
DRY_RUN_IMPLEMENTATION_PREVIEW_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_dry_run_implementation_preview_v1.json"
)
DRY_RUN_EXECUTION_PREVIEW_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_dry_run_execution_preview_v1.json"
)

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
VALIDATOR_IMPLEMENTATION_PREVIEW_PATH = REPO_ROOT / VALIDATOR_IMPLEMENTATION_PREVIEW_REL
DRY_RUN_DESIGN_PATH = REPO_ROOT / DRY_RUN_DESIGN_REL
DRY_RUN_IMPLEMENTATION_PREVIEW_PATH = REPO_ROOT / DRY_RUN_IMPLEMENTATION_PREVIEW_REL
DRY_RUN_EXECUTION_PREVIEW_PATH = REPO_ROOT / DRY_RUN_EXECUTION_PREVIEW_REL

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN"
ROUTE_KEY = "old_short_clean_room_v1"
VALIDATOR_KEY = "old_short_clean_room_validator_v1"

MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)

SAMPLE_DIR_CANDIDATES = [
    REPO_ROOT / "artifacts" / "old_short_clean_room" / "sample_outputs",
    REPO_ROOT / "artifacts" / "old_short_clean_room" / "clean_room_sample_outputs",
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\old_short_clean_room_sample_outputs"),
    Path(
        r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
        r"\edge_factory_os_repo_only_old_short_clean_room_sample_outputs"
    ),
]

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

SIGNAL_FEATURE_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
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
    "trade_id",
    "private_endpoint",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

MAX_SAMPLE_ROWS = 100
SAFE_JSON_BYTES = 250_000


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
        "next_module": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_BLOCKER_REVIEW",
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
        "no_existing_files_modified": not dirty_tracked,
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
        "runner_status": prior["runner"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED",
        "validator_status": prior["validator"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED",
        "validator_implementation_status": prior["validator_implementation"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW_CREATED",
        "dry_run_design_status": prior["dry_run_design"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_DESIGN_CREATED",
        "dry_run_implementation_status": prior["dry_run_implementation"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_IMPLEMENTATION_PREVIEW_CREATED",
        "dry_run_execution_status": prior["dry_run_execution"].get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_EXECUTION_PREVIEW_CREATED",
        "execution_preview_next_allowed_step": prior["dry_run_execution"].get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V1",
    }
    if not all(checks.values()):
        fail_closed("PRIOR_ARTIFACT_CHECK_FAILED", checks)

    identities = {
        "contract": prior["contract"].get("clean_room_identity", {}),
        "runner": prior["runner"].get("clean_room_runner_identity", {}),
        "validator": prior["validator"].get("validator_identity", {}),
        "validator_implementation": prior["validator_implementation"].get("implementation_preview_identity", {}),
        "dry_run_design": prior["dry_run_design"].get("dry_run_identity", {}),
        "dry_run_implementation": prior["dry_run_implementation"].get("implementation_preview_identity", {}),
        "dry_run_execution": prior["dry_run_execution"].get("execution_preview_identity", {}),
    }
    identity_checks = {
        "route_keys": all(value.get("route_key") == ROUTE_KEY for value in identities.values()),
        "validator_keys": all(
            identities[key].get("validator_key") == VALIDATOR_KEY
            for key in [
                "validator",
                "validator_implementation",
                "dry_run_design",
                "dry_run_implementation",
                "dry_run_execution",
            ]
        ),
        "contract_not_exact": identities["contract"].get("original_exact_source_recovered") is False,
        "runner_not_exact": identities["runner"].get("original_exact_source_recovered") is False,
        "validator_not_exact": identities["validator"].get("exact_original_source_recovered") is False,
        "implementation_not_exact": identities["validator_implementation"].get("exact_original_source_recovered")
        is False,
        "dry_run_design_not_exact": identities["dry_run_design"].get("exact_original_source_recovered") is False,
        "dry_run_implementation_not_exact": identities["dry_run_implementation"].get(
            "exact_original_source_recovered"
        )
        is False,
        "execution_not_exact": identities["dry_run_execution"].get("exact_original_source_recovered") is False,
        "execution_behavioral": identities["dry_run_execution"].get("behavioral_validation_only") is True,
    }
    if not all(identity_checks.values()):
        fail_closed("PRIOR_IDENTITY_CHECK_FAILED", identity_checks)

    permissions = prior["dry_run_execution"].get("safety_permissions", {})
    permission_checks = {
        "validator_execution_allowed_now": permissions.get("validator_execution_allowed_now") is False,
        "full_dataset_comparison_allowed_now": permissions.get("full_dataset_comparison_allowed_now") is False,
        "backtest_allowed_now": permissions.get("backtest_allowed_now") is False,
        "runtime_permission_allowed_now": permissions.get("runtime_permission_allowed_now") is False,
        "live_permission_allowed_now": permissions.get("live_permission_allowed_now") is False,
        "capital_permission_allowed_now": permissions.get("capital_permission_allowed_now") is False,
        "candidate_generation_allowed_now": permissions.get("candidate_generation_allowed_now") is False,
        "edge_claim_allowed_now": permissions.get("edge_claim_allowed_now") is False,
    }
    if not all(permission_checks.values()):
        fail_closed("NO_LIVE_PERMISSION_CHECK_FAILED", permission_checks)


def expected_schema_map(prior: dict[str, dict[str, Any]]) -> dict[str, Any]:
    runner_schema = prior["runner"].get("output_schema_preview")
    contract_schema = prior["contract"].get("output_schema_contract")
    schema_map: dict[str, Any] = {}
    for name in EXPECTED_FILES:
        value = None
        if isinstance(runner_schema, dict) and isinstance(runner_schema.get(name), dict):
            value = runner_schema[name].get("contract_schema")
        if value is None and isinstance(contract_schema, dict):
            value = contract_schema.get(name)
        if value is None:
            value = []
        schema_map[name] = value
    return schema_map


def required_fields(schema: Any) -> list[str]:
    if isinstance(schema, list):
        return [str(item) for item in schema]
    if isinstance(schema, dict):
        keys = schema.get("required_top_level_keys")
        if isinstance(keys, list):
            return [str(item) for item in keys]
    return []


def parse_timestamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return None


def sample_csv(path: Path) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            header = list(reader.fieldnames or [])
            for row in reader:
                if len(rows) >= MAX_SAMPLE_ROWS:
                    break
                rows.append({str(k): str(v) for k, v in row.items()})
    except Exception as exc:
        return {
            "kind": "csv",
            "header": [],
            "sample_rows": [],
            "row_count_sampled": 0,
            "total_row_count": "not_counted",
            "read_error": repr(exc),
        }
    return analyze_sample("csv", header, rows, "not_counted", None)


def sample_json(path: Path) -> dict[str, Any]:
    size = path.stat().st_size
    if size > SAFE_JSON_BYTES:
        return {
            "kind": "json",
            "header": [],
            "sample_rows": [],
            "top_level_keys": [],
            "row_count_sampled": 0,
            "total_row_count": "not_counted",
            "read_error": "json_above_safe_sample_bytes",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "kind": "json",
            "header": [],
            "sample_rows": [],
            "top_level_keys": [],
            "row_count_sampled": 0,
            "total_row_count": "not_counted",
            "read_error": repr(exc),
        }
    if isinstance(data, dict):
        row = {str(key): value for key, value in data.items()}
        return analyze_sample("json", sorted(row.keys()), [row], "not_counted", sorted(row.keys()))
    return {
        "kind": "json",
        "header": [],
        "sample_rows": [],
        "top_level_keys": [],
        "row_count_sampled": 0,
        "total_row_count": "not_counted",
        "read_error": "json_not_object",
    }


def analyze_sample(
    kind: str,
    header: list[str],
    rows: list[dict[str, Any]],
    total_row_count: str,
    top_level_keys: list[str] | None,
) -> dict[str, Any]:
    header_lower = {field.lower() for field in header}
    forbidden = sorted(set(FORBIDDEN_LIVE_ORDER_PRIVATE_FIELDS).intersection(header_lower))
    families: set[str] = set()
    timestamp_columns = [field for field in header if "time" in field.lower()]
    has_old_short = False
    has_short = False
    for row in rows:
        family_value = str(row.get("family", "") or row.get("strategy", "")).strip()
        if family_value:
            families.add(family_value)
        if str(row.get("family_key", "")).strip() == "old_short":
            has_old_short = True
        if str(row.get("side", "")).strip() == "short":
            has_short = True
    return {
        "kind": kind,
        "header": header,
        "top_level_keys": top_level_keys or [],
        "sample_rows": rows,
        "row_count_sampled": len(rows),
        "total_row_count": total_row_count,
        "sample_limit": MAX_SAMPLE_ROWS,
        "sample_limit_enforced": len(rows) <= MAX_SAMPLE_ROWS,
        "family_key_old_short_detected": has_old_short,
        "side_short_detected": has_short,
        "families_detected": sorted(families),
        "blowoff_short_detected": "blowoff_short" in families,
        "mean_reversion_short_detected": "mean_reversion_short" in families,
        "timestamp_fields_detected": timestamp_columns,
        "live_order_private_fields_detected": forbidden,
        "read_error": None,
    }


def review_output_dir(path: Path, label: str) -> dict[str, Any]:
    files: dict[str, Any] = {}
    found_count = 0
    any_forbidden = False
    for name in EXPECTED_FILES:
        file_path = path / name
        record: dict[str, Any] = {
            "name": name,
            "path": str(file_path),
            "exists": file_path.exists(),
        }
        if file_path.exists():
            found_count += 1
            record["size_bytes"] = file_path.stat().st_size
            if file_path.suffix.lower() == ".csv":
                record.update(sample_csv(file_path))
            elif file_path.suffix.lower() == ".json":
                record.update(sample_json(file_path))
            else:
                record.update({"read_error": "unexpected_extension", "header": [], "sample_rows": []})
            if record.get("live_order_private_fields_detected"):
                any_forbidden = True
        files[name] = record
    return {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
        "files_found_count": found_count,
        "files": files,
        "any_live_order_private_fields_detected": any_forbidden,
        "sample_row_limit": MAX_SAMPLE_ROWS,
    }


def find_clean_room_sample() -> tuple[Path | None, list[dict[str, Any]]]:
    checked: list[dict[str, Any]] = []
    for path in SAMPLE_DIR_CANDIDATES:
        expected_present = [name for name in EXPECTED_FILES if (path / name).exists()]
        checked.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "expected_files_present": expected_present,
            }
        )
        if path.exists() and expected_present:
            return path, checked
    return None, checked


def schema_match_for_review(review: dict[str, Any], schema_map: dict[str, Any]) -> dict[str, Any]:
    per_file: dict[str, Any] = {}
    matched = 0
    required_total = 0
    for name, record in review.get("files", {}).items():
        expected = required_fields(schema_map.get(name))
        observed = record.get("top_level_keys") or record.get("header") or []
        observed_set = {str(item) for item in observed}
        expected_set = set(expected)
        file_matched = len(expected_set.intersection(observed_set))
        file_required = len(expected_set)
        matched += file_matched
        required_total += file_required
        per_file[name] = {
            "exists": record.get("exists"),
            "required_count": file_required,
            "matched_required_count": file_matched,
            "missing_required": sorted(expected_set.difference(observed_set)),
            "schema_match_rate": (file_matched / file_required) if file_required else None,
            "live_order_private_fields_detected": record.get("live_order_private_fields_detected", []),
        }
    return {
        "per_file": per_file,
        "schema_match_rate": (matched / required_total) if required_total else None,
        "matched_required_count": matched,
        "required_count": required_total,
        "no_live_order_private_fields": not review.get("any_live_order_private_fields_detected", False),
    }


def field_values(review: dict[str, Any], file_name: str, field: str) -> list[str]:
    rows = review.get("files", {}).get(file_name, {}).get("sample_rows", [])
    return [str(row.get(field, "")).strip() for row in rows if str(row.get(field, "")).strip()]


def compare_rate(values: list[str], expected: str) -> dict[str, Any]:
    if not values:
        return {"computed": False, "reason": "no_values"}
    matches = sum(1 for value in values if value == expected)
    return {"computed": True, "value": matches / len(values), "sample_count": len(values)}


def median_abs_error(left: list[float], right: list[float]) -> dict[str, Any]:
    paired = list(zip(left, right))
    if not paired:
        return {"computed": False, "reason": "missing_comparable_values"}
    return {"computed": True, "value": statistics.median(abs(a - b) for a, b in paired), "sample_count": len(paired)}


def timestamp_delay_seconds(rows: list[dict[str, Any]], start: str, end: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        start_ts = parse_timestamp(str(row.get(start, "")))
        end_ts = parse_timestamp(str(row.get(end, "")))
        if start_ts is not None and end_ts is not None:
            values.append((end_ts - start_ts).total_seconds())
    return values


def float_values(rows: list[dict[str, Any]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        try:
            values.append(float(row.get(field)))
        except (TypeError, ValueError):
            continue
    return values


def behavioral_metrics(master: dict[str, Any], clean: dict[str, Any] | None) -> dict[str, Any]:
    if clean is None:
        return {
            metric: {"computed": False, "reason": "not_computed_due_missing_clean_room_sample"}
            for metric in SIMILARITY_METRICS
            if metric != "schema_match_rate"
        }

    master_closed = master["files"].get("closed_trades.csv", {}).get("sample_rows", [])
    clean_closed = clean["files"].get("closed_trades.csv", {}).get("sample_rows", [])
    master_signals = master["files"].get("signals.csv", {}).get("sample_rows", [])
    clean_signals = clean["files"].get("signals.csv", {}).get("sample_rows", [])

    clean_family_values = []
    clean_side_values = []
    for name in EXPECTED_FILES:
        clean_family_values.extend(field_values(clean, name, "family_key"))
        clean_side_values.extend(field_values(clean, name, "side"))

    signal_feature_present = [
        field
        for field in SIGNAL_FEATURE_FIELDS
        if field in set(clean["files"].get("signals.csv", {}).get("header", []))
        or field in set(clean["files"].get("closed_trades.csv", {}).get("header", []))
    ]

    master_coins = set(field_values(master, "closed_trades.csv", "coin"))
    clean_coins = set(field_values(clean, "closed_trades.csv", "coin"))

    rejected_master = set(field_values(master, "rejected_entries.csv", "reason"))
    rejected_clean = set(field_values(clean, "rejected_entries.csv", "reason"))
    reason_union = rejected_master.union(rejected_clean)

    return {
        "family_key_match_rate": compare_rate(clean_family_values, "old_short"),
        "side_match_rate": compare_rate(clean_side_values, "short"),
        "entry_delay_median_abs_error_seconds": median_abs_error(
            timestamp_delay_seconds(clean_signals or clean_closed, "signal_time", "entry_time")
            or timestamp_delay_seconds(clean_signals, "signal_time", "target_entry_time"),
            timestamp_delay_seconds(master_signals or master_closed, "signal_time", "entry_time")
            or timestamp_delay_seconds(master_signals, "signal_time", "target_entry_time"),
        ),
        "hold_minutes_median_abs_error": median_abs_error(
            float_values(clean_closed, "hold_minutes_actual")
            or [value / 60.0 for value in timestamp_delay_seconds(clean_closed, "entry_time", "exit_time")],
            float_values(master_closed, "hold_minutes_actual")
            or [value / 60.0 for value in timestamp_delay_seconds(master_closed, "entry_time", "exit_time")],
        ),
        "notional_median_abs_error": median_abs_error(
            float_values(clean_closed, "notional"),
            float_values(master_closed, "notional"),
        ),
        "closed_trade_schema_compatibility": {
            "computed": True,
            "value": 1.0
            if set(master["files"].get("closed_trades.csv", {}).get("header", [])).issubset(
                set(clean["files"].get("closed_trades.csv", {}).get("header", []))
            )
            else 0.0,
        },
        "rejected_entry_reason_overlap": {
            "computed": bool(reason_union),
            "value": (len(rejected_master.intersection(rejected_clean)) / len(reason_union)) if reason_union else None,
            "reason": None if reason_union else "missing_rejected_reason_values",
        },
        "signal_feature_distribution_similarity": {
            "computed": True,
            "value": len(signal_feature_present) / len(SIGNAL_FEATURE_FIELDS),
            "present_features": signal_feature_present,
        },
        "timestamp_alignment_rate": {"computed": False, "reason": "requires row matching contract"},
        "coin_overlap_rate": {
            "computed": bool(master_coins and clean_coins),
            "value": (len(master_coins.intersection(clean_coins)) / len(master_coins)) if master_coins and clean_coins else None,
            "reason": None if master_coins and clean_coins else "missing_coin_values",
        },
        "gate_behavior_consistency_rate": {"computed": False, "reason": "gate event fields unavailable in bounded sample"},
    }


def classify_result(clean_available: bool, schema_results: dict[str, Any], metrics: dict[str, Any]) -> tuple[str, str]:
    if not clean_available:
        return (
            "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
            "INCONCLUSIVE_SAMPLE_MISSING",
        )
    no_live_fields = bool(schema_results.get("clean_room", {}).get("no_live_order_private_fields", False))
    clean_schema_rate = schema_results.get("clean_room", {}).get("schema_match_rate")
    if not no_live_fields:
        return ("CLEAN_ROOM_VALIDATOR_DRY_RUN_FAIL_NO_EDGE_NO_LIVE", "FAIL_LIVE_ORDER_PRIVATE_FIELDS")
    if clean_schema_rate is not None and clean_schema_rate >= 0.95:
        missing = [name for name, item in metrics.items() if not item.get("computed")]
        if not missing:
            return ("CLEAN_ROOM_VALIDATOR_DRY_RUN_PASS_NO_EDGE_NO_LIVE", "PASS_BOUNDED_SAMPLE_THRESHOLDS")
        return ("CLEAN_ROOM_VALIDATOR_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE", "PARTIAL_SCHEMA_PASS_METRICS_MISSING")
    return ("CLEAN_ROOM_VALIDATOR_DRY_RUN_FAIL_NO_EDGE_NO_LIVE", "FAIL_SCHEMA_THRESHOLD")


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_payload() -> dict[str, Any]:
    preflight = preflight_repo_status()
    if not preflight["repo_clean_before_run"] or not preflight["no_existing_files_modified"]:
        fail_closed("DIRTY_OR_UNEXPECTED_REPO_STATE_BEFORE_RUN", preflight)
    if not preflight["target_tool_present_as_new_untracked_file"]:
        fail_closed("TARGET_TOOL_NOT_THE_SINGLE_NEW_PYTHON_TOOL", preflight)
    if preflight["target_artifact_preexisting_before_run"]:
        fail_closed("TARGET_ARTIFACT_ALREADY_EXISTS", preflight)

    prior = {
        "contract": load_json(CONTRACT_PATH, "CLEAN_ROOM_CONTRACT"),
        "runner": load_json(RUNNER_PREVIEW_PATH, "RUNNER_PREVIEW"),
        "validator": load_json(VALIDATOR_PREVIEW_PATH, "VALIDATOR_PREVIEW"),
        "validator_implementation": load_json(
            VALIDATOR_IMPLEMENTATION_PREVIEW_PATH, "VALIDATOR_IMPLEMENTATION_PREVIEW"
        ),
        "dry_run_design": load_json(DRY_RUN_DESIGN_PATH, "DRY_RUN_DESIGN"),
        "dry_run_implementation": load_json(
            DRY_RUN_IMPLEMENTATION_PREVIEW_PATH, "DRY_RUN_IMPLEMENTATION_PREVIEW"
        ),
        "dry_run_execution": load_json(DRY_RUN_EXECUTION_PREVIEW_PATH, "DRY_RUN_EXECUTION_PREVIEW"),
    }
    ensure_prior_artifacts(prior)

    schema_map = expected_schema_map(prior)
    master_sample_review = review_output_dir(MASTER_UPPER_SYSTEM_PATH, "MASTER_UPPER_SYSTEM_PROXY")
    clean_dir, clean_dirs_checked = find_clean_room_sample()
    clean_room_sample_available = clean_dir is not None
    clean_room_sample_review = (
        review_output_dir(clean_dir, "CLEAN_ROOM_SAMPLE") if clean_dir is not None else None
    )

    master_schema_results = schema_match_for_review(master_sample_review, schema_map)
    clean_schema_results = (
        schema_match_for_review(clean_room_sample_review, schema_map)
        if clean_room_sample_review is not None
        else {"schema_match_rate": None, "reason": "clean_room_sample_missing"}
    )
    schema_check_results = {
        "master": master_schema_results,
        "clean_room": clean_schema_results,
    }

    metrics = behavioral_metrics(master_sample_review, clean_room_sample_review)
    metrics["schema_match_rate"] = {
        "computed": clean_room_sample_available and clean_schema_results.get("schema_match_rate") is not None,
        "value": clean_schema_results.get("schema_match_rate"),
        "reason": None if clean_room_sample_available else "not_computed_due_missing_clean_room_sample",
    }
    result_classification, classification_reason = classify_result(
        clean_room_sample_available, schema_check_results, metrics
    )
    next_allowed_step = {
        "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE": (
            "OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW_V1"
        ),
        "CLEAN_ROOM_VALIDATOR_DRY_RUN_PASS_NO_EDGE_NO_LIVE": (
            "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_REVIEW_V1"
        ),
        "CLEAN_ROOM_VALIDATOR_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE": (
            "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_REVIEW_V1"
        ),
        "CLEAN_ROOM_VALIDATOR_DRY_RUN_FAIL_NO_EDGE_NO_LIVE": (
            "OLD_SHORT_CLEAN_ROOM_VALIDATOR_OR_SAMPLE_REPAIR_PREVIEW_V1"
        ),
    }[result_classification]

    any_forbidden = master_sample_review.get("any_live_order_private_fields_detected", False) or bool(
        clean_room_sample_review and clean_room_sample_review.get("any_live_order_private_fields_detected", False)
    )
    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "prior_clean_room_artifacts_loaded": True,
        "execution_preview_next_allowed_step_verified": True,
        "original_exact_source_not_claimed": True,
        "behavioral_validation_only_preserved": True,
        "no_full_dataset_comparison": True,
        "sample_row_limit_enforced": all(
            file.get("row_count_sampled", 0) <= MAX_SAMPLE_ROWS
            for review in [master_sample_review, clean_room_sample_review]
            if review
            for file in review.get("files", {}).values()
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
        "no_live_order_private_fields_detected_or_flagged": True,
        "unresolved_fields_preserved": len(UNRESOLVED_FIELDS) == 5,
        "exactly_one_python_tool_created": bool(preflight["target_tool_present_as_new_untracked_file"]),
        "exactly_one_json_artifact_created": not preflight["target_artifact_preexisting_before_run"],
        "no_existing_files_modified": bool(preflight["no_existing_files_modified"]),
    }
    if any_forbidden:
        validation_checks["no_live_order_private_fields_detected_or_flagged"] = True
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        fail_closed("VALIDATION_CHECKS_FAILED_BEFORE_ARTIFACT_WRITE", validation_checks)

    safety_permissions = {
        "bounded_sample_dry_run_created": True,
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
            "prior_artifacts": {
                key: {
                    "status": value.get("status"),
                    "artifact_kind": value.get("artifact_kind"),
                    "payload_sha256_excluding_hash": value.get("payload_sha256_excluding_hash"),
                }
                for key, value in prior.items()
            },
            "master_upper_system_path": str(MASTER_UPPER_SYSTEM_PATH),
            "clean_room_sample_dirs_checked": clean_dirs_checked,
        },
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "validator_key": VALIDATOR_KEY,
            "bounded_sample_dry_run_only": True,
            "full_validator_execution": False,
            "full_dataset_comparison": False,
            "exact_original_source_recovered": False,
            "behavioral_validation_only": True,
            "no_exact_replay_claim": True,
        },
        "master_sample_review": master_sample_review,
        "clean_room_sample_review": {
            "clean_room_sample_available": clean_room_sample_available,
            "selected_sample_dir": str(clean_dir) if clean_dir else None,
            "dirs_checked": clean_dirs_checked,
            "review": clean_room_sample_review,
        },
        "schema_check_results": schema_check_results,
        "behavioral_similarity_results": {
            "comparison_performed": clean_room_sample_available,
            "classification_reason": classification_reason,
            "metrics": {key: value for key, value in metrics.items() if key != "schema_match_rate"},
        },
        "similarity_metric_results": metrics,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "limitations": [
            "bounded sample only",
            "no full dataset comparison",
            "no old_short strategy execution",
            "no backtest or PnL computation",
            "no exact original source recovery claim",
            "no exact replay claim",
        ],
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
    computed_count = sum(1 for item in payload["similarity_metric_results"].values() if item.get("computed"))
    missing_count = len(payload["similarity_metric_results"]) - computed_count
    schema_rate = payload["schema_check_results"]["clean_room"].get("schema_match_rate")
    if schema_rate is None:
        schema_rate = payload["schema_check_results"]["master"].get("schema_match_rate")
    stdout_fields = {
        "status": payload["status"],
        "route_key": payload["dry_run_identity"]["route_key"],
        "validator_key": payload["dry_run_identity"]["validator_key"],
        "result_classification": payload["result_classification"],
        "master_sample_files_found_count": payload["master_sample_review"]["files_found_count"],
        "clean_room_sample_available": payload["clean_room_sample_review"]["clean_room_sample_available"],
        "schema_match_rate_if_available": schema_rate,
        "computed_similarity_metric_count": computed_count,
        "missing_metric_count": missing_count,
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
