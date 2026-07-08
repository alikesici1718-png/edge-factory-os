#!/usr/bin/env python3
"""Repo-only old_short clean-room validator dry-run design v1.

This module writes a dry-run design artifact only. It does not execute a
validator, compare full datasets, run old_short, compute PnL, run a backtest,
touch runtime, place orders, use network or APIs, generate candidates, claim
edge, or grant runtime/live/capital permission.
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

MODULE = "edge_factory_os_repo_only_old_short_clean_room_validator_dry_run_design_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_validator_dry_run_design_v1.py"
ARTIFACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_dry_run_design_v1.json"
CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
VALIDATOR_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"
IMPLEMENTATION_PREVIEW_REL = (
    "artifacts/old_short_clean_room/old_short_clean_room_validator_implementation_preview_v1.json"
)

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
IMPLEMENTATION_PREVIEW_PATH = REPO_ROOT / IMPLEMENTATION_PREVIEW_REL
OLD_SHORT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "old_short"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_DESIGN"
ROUTE_KEY = "old_short_clean_room_v1"
VALIDATOR_KEY = "old_short_clean_room_validator_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_IMPLEMENTATION_PREVIEW_V1"

MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
LOGGER_PATH = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")

EXPECTED_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

DRY_RUN_FLOW_STEPS = [
    "LOAD_CONTRACT",
    "LOAD_VALIDATOR_PREVIEW",
    "LOAD_SAMPLE_SCHEMAS",
    "LOAD_MASTER_PROXY_SAMPLE",
    "LOAD_CLEAN_ROOM_SAMPLE",
    "RUN_SCHEMA_CHECKS",
    "RUN_BEHAVIORAL_SIMILARITY_CHECKS",
    "BUILD_DRY_RUN_REPORT",
    "REPORT_ONLY",
]

BEHAVIORAL_CHECKS = [
    "family_key_match_rate",
    "side_match_rate",
    "subfamily_presence",
    "signal_feature_presence_rate",
    "entry_delay_abs_error_if_signal_and_entry_times_available",
    "hold_minutes_abs_error_if_entry_exit_or_planned_exit_available",
    "notional_abs_error",
    "rejected_reason_overlap",
    "gate_behavior_consistency",
    "no_position_without_gate_allow",
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

DRY_RUN_RESULT_CLASSES = [
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_FAIL_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]

FORBIDDEN_RESULT_CLASSES = [
    "original source recovered",
    "exact replay",
    "candidate",
    "edge claim",
    "runtime/live/capital permission",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

NO_LIVE_ORDER_FIELDS = [
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

SAFE_SAMPLE_ROWS_NOW = 3
FUTURE_DEFAULT_SAMPLE_ROWS = 100
LOGGER_SAMPLE_BYTES = 200_000


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
        "next_module": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_DESIGN_BLOCKER_REVIEW",
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
    allowed_pending = [
        line
        for line in lines
        if status_code(line) == "??" and normalize_status_path(line) in allowed_untracked
    ]
    target_tool_is_new = any(
        status_code(line) == "??" and normalize_status_path(line) == TOOL_REL for line in lines
    )
    return {
        "status_lines_before_run": lines,
        "allowed_pending_before_run": allowed_pending,
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


def summarize_old_short_metadata_only() -> list[dict[str, Any]]:
    if not OLD_SHORT_ARTIFACT_DIR.exists():
        fail_closed("OLD_SHORT_ARTIFACT_DIR_MISSING", {"path": str(OLD_SHORT_ARTIFACT_DIR)})
    summaries: list[dict[str, Any]] = []
    for path in sorted(OLD_SHORT_ARTIFACT_DIR.glob("*.json")):
        stat = path.stat()
        summaries.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "exists": True,
                "metadata_only": True,
                "size_bytes": stat.st_size,
                "modified_time_utc": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )
    if not summaries:
        fail_closed("NO_PRIOR_OLD_SHORT_ARTIFACTS_FOUND", {"path": str(OLD_SHORT_ARTIFACT_DIR)})
    return summaries


def sample_csv_header_and_rows(path: Path) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            header = list(reader.fieldnames or [])
            for row in reader:
                if len(rows) >= SAFE_SAMPLE_ROWS_NOW:
                    break
                rows.append({str(k): str(v) for k, v in row.items()})
    except Exception as exc:
        return {"header": [], "sample_rows": [], "read_error": repr(exc)}
    return {"header": header, "sample_rows": rows, "read_error": None}


def sample_json_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"top_level_keys": [], "sample": None, "read_error": repr(exc)}
    if isinstance(data, dict):
        return {
            "top_level_keys": sorted(data.keys()),
            "sample": {key: data[key] for key in sorted(data.keys())[:10]},
            "read_error": None,
        }
    return {"top_level_keys": [], "sample_type": type(data).__name__, "read_error": None}


def inspect_master_proxy_small_samples() -> list[dict[str, Any]]:
    if not MASTER_UPPER_SYSTEM_PATH.exists():
        fail_closed("MASTER_UPPER_SYSTEM_PATH_MISSING", {"path": str(MASTER_UPPER_SYSTEM_PATH)})
    samples: list[dict[str, Any]] = []
    for name in EXPECTED_FILES:
        path = MASTER_UPPER_SYSTEM_PATH / name
        item: dict[str, Any] = {
            "name": name,
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
            "sample_policy": f"header plus first {SAFE_SAMPLE_ROWS_NOW} rows only",
        }
        if path.exists() and path.suffix.lower() == ".csv":
            item.update(sample_csv_header_and_rows(path))
        elif path.exists() and path.suffix.lower() == ".json":
            item.update(sample_json_metadata(path))
        else:
            item["read_error"] = None
        samples.append(item)
    return samples


def inspect_logger_text_only() -> dict[str, Any]:
    if not LOGGER_PATH.exists():
        fail_closed("LOGGER_SCRIPT_MISSING", {"path": str(LOGGER_PATH)})
    text = LOGGER_PATH.read_text(encoding="utf-8", errors="replace")[:LOGGER_SAMPLE_BYTES]
    lower = text.lower()
    return {
        "path": str(LOGGER_PATH),
        "exists": True,
        "checked_as_text_only": True,
        "executed": False,
        "sample_bytes": min(len(text), LOGGER_SAMPLE_BYTES),
        "contains_old_short": "old_short" in lower,
        "contains_gate_reference": "gate" in lower,
        "contains_blowoff_short": "blowoff_short" in text,
        "contains_mean_reversion_short": "mean_reversion_short" in text,
    }


def ensure_prior_artifacts(
    contract: dict[str, Any],
    runner: dict[str, Any],
    validator: dict[str, Any],
    implementation: dict[str, Any],
) -> None:
    checks = {
        "contract_status": contract.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED",
        "runner_status": runner.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED",
        "validator_status": validator.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED",
        "implementation_status": implementation.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW_CREATED",
        "implementation_next_allowed_step": implementation.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_DESIGN_V1",
    }
    if not all(checks.values()):
        fail_closed("PRIOR_ARTIFACT_CHECK_FAILED", checks)

    contract_identity = contract.get("clean_room_identity", {})
    runner_identity = runner.get("clean_room_runner_identity", {})
    validator_identity = validator.get("validator_identity", {})
    implementation_identity = implementation.get("implementation_preview_identity", {})
    identity_checks = {
        "contract_route_key": contract_identity.get("route_key") == ROUTE_KEY,
        "runner_route_key": runner_identity.get("route_key") == ROUTE_KEY,
        "validator_route_key": validator_identity.get("route_key") == ROUTE_KEY,
        "implementation_route_key": implementation_identity.get("route_key") == ROUTE_KEY,
        "validator_key": validator_identity.get("validator_key") == VALIDATOR_KEY,
        "implementation_validator_key": implementation_identity.get("validator_key") == VALIDATOR_KEY,
        "contract_not_exact_source": contract_identity.get("original_exact_source_recovered") is False,
        "runner_not_exact_source": runner_identity.get("original_exact_source_recovered") is False,
        "validator_not_exact_source": validator_identity.get("exact_original_source_recovered") is False,
        "implementation_not_exact_source": implementation_identity.get("exact_original_source_recovered") is False,
        "validator_behavioral_only": validator_identity.get("behavioral_validation_only") is True,
        "implementation_behavioral_only": implementation_identity.get("behavioral_validation_only") is True,
        "implementation_execution_false": implementation_identity.get("validator_execution_allowed_now") is False,
    }
    if not all(identity_checks.values()):
        fail_closed("PRIOR_IDENTITY_CHECK_FAILED", identity_checks)


def build_schema_checks(implementation: dict[str, Any]) -> dict[str, Any]:
    schema_preview = implementation.get("schema_validator_preview")
    if not isinstance(schema_preview, dict):
        fail_closed("IMPLEMENTATION_SCHEMA_PREVIEW_MISSING", {"path": IMPLEMENTATION_PREVIEW_REL})
    schema_checks: dict[str, Any] = {}
    for name in EXPECTED_FILES:
        entry = schema_preview.get(name)
        if not isinstance(entry, dict):
            fail_closed("IMPLEMENTATION_SCHEMA_FILE_MISSING", {"file": name})
        schema_checks[name] = {
            "required_columns": entry.get("required_columns"),
            "optional_columns": entry.get("optional_columns", []),
            "type_expectations": entry.get("type_expectations"),
            "timestamp_fields": entry.get("timestamp_expectations"),
            "family_key_expectation": {
                "expected_family_key": "old_short",
                "source_expectation": entry.get("family_key_expectations"),
            },
            "side_expectation": {
                "expected_side": "short",
                "source_expectation": entry.get("side_expectations"),
            },
            "no_live_order_private_fields": {
                "forbidden_fields": NO_LIVE_ORDER_FIELDS,
                "must_be_absent": True,
            },
            "schema_compatibility_rate": "matched_required_columns / required_columns",
        }
    return schema_checks


def build_behavioral_similarity_checks() -> dict[str, Any]:
    return {
        "family_key_match_rate": {
            "expected": "old_short",
            "formula": "rows_with_old_short / comparable_rows",
        },
        "side_match_rate": {
            "expected": "short",
            "formula": "rows_with_short_side / comparable_rows",
        },
        "subfamily_presence": {
            "expected": ["blowoff_short", "mean_reversion_short"],
            "formula": "required_subfamilies_present_in_bounded_samples",
        },
        "signal_feature_presence_rate": {
            "required_features": SIGNAL_FEATURE_FIELDS,
            "formula": "present_required_signal_features / required_signal_features",
        },
        "entry_delay_abs_error": {
            "condition": "if both samples provide signal_time and entry_time",
            "target": "approximately 2 minutes",
            "formula": "abs(candidate_entry_delay_seconds - proxy_entry_delay_seconds)",
        },
        "hold_minutes_abs_error": {
            "condition": "if both samples provide entry and exit or planned_exit times",
            "target": "approximately 120 minutes",
            "formula": "abs(candidate_hold_minutes - proxy_hold_minutes)",
        },
        "notional_abs_error": {
            "target": "near 50 USDT for 1000 USDT base equity",
            "formula": "abs(candidate_notional_usdt - proxy_notional_usdt)",
        },
        "rejected_reason_overlap": {
            "expected_reasons": ["gate_missing", "gate_timeout", "gate_block"],
            "formula": "reason_set_intersection / reason_set_union",
        },
        "gate_behavior_consistency": {
            "required": "gate allow required before open",
            "formula": "consistent_gate_events / comparable_gate_events",
        },
        "no_position_without_gate_allow": {
            "required": True,
            "formula": "candidate_open_positions_without_gate_allow == 0",
        },
    }


def build_dry_run_thresholds(implementation: dict[str, Any]) -> dict[str, Any]:
    threshold_preview = implementation.get("threshold_policy_preview")
    if not isinstance(threshold_preview, dict):
        fail_closed("IMPLEMENTATION_THRESHOLD_POLICY_MISSING", {"path": IMPLEMENTATION_PREVIEW_REL})
    thresholds = threshold_preview.get("thresholds")
    if not isinstance(thresholds, dict):
        fail_closed("IMPLEMENTATION_THRESHOLDS_MISSING", {"path": IMPLEMENTATION_PREVIEW_REL})
    required = {
        "schema_match_rate",
        "family_key_match_rate",
        "side_match_rate",
        "median_entry_delay_error_seconds",
        "median_hold_error_minutes",
        "notional_median_error_usdt",
        "no_position_without_gate_allow",
        "no_live_order_fields",
        "closed_trades_schema_compatible",
    }
    missing = sorted(required.difference(thresholds.keys()))
    if missing:
        fail_closed("IMPLEMENTATION_THRESHOLDS_INCOMPLETE", {"missing": missing})
    return {
        "schema_match_rate": thresholds["schema_match_rate"],
        "family_key_match_rate": thresholds["family_key_match_rate"],
        "side_match_rate": thresholds["side_match_rate"],
        "median_entry_delay_error_seconds": thresholds["median_entry_delay_error_seconds"],
        "median_hold_error_minutes": thresholds["median_hold_error_minutes"],
        "notional_median_error_usdt": thresholds["notional_median_error_usdt"],
        "no_position_without_gate_allow": thresholds["no_position_without_gate_allow"],
        "no_live_order_fields": thresholds["no_live_order_fields"],
        "closed_trades_schema_compatible": thresholds["closed_trades_schema_compatible"],
        "threshold_type": "validation_thresholds_not_strategy_parameters",
    }


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

    contract = load_json(CONTRACT_PATH, "CLEAN_ROOM_CONTRACT")
    runner = load_json(RUNNER_PREVIEW_PATH, "RUNNER_PREVIEW")
    validator = load_json(VALIDATOR_PREVIEW_PATH, "VALIDATOR_PREVIEW")
    implementation = load_json(IMPLEMENTATION_PREVIEW_PATH, "VALIDATOR_IMPLEMENTATION_PREVIEW")
    ensure_prior_artifacts(contract, runner, validator, implementation)

    schema_checks = build_schema_checks(implementation)
    behavioral_similarity_checks = build_behavioral_similarity_checks()
    dry_run_thresholds = build_dry_run_thresholds(implementation)

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "clean_room_contract_loaded": True,
        "runner_preview_loaded": True,
        "validator_preview_loaded": True,
        "validator_implementation_preview_loaded": True,
        "validator_implementation_next_allowed_step_verified": True,
        "original_exact_source_not_claimed": True,
        "behavioral_validation_only_preserved": True,
        "no_validator_execution": True,
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "dry_run_scope_defined": True,
        "sample_policy_defined": True,
        "schema_checks_defined": len(schema_checks) == len(EXPECTED_FILES),
        "behavioral_similarity_checks_defined": len(behavioral_similarity_checks) == len(BEHAVIORAL_CHECKS),
        "result_classes_no_edge_no_live": all(value.endswith("_NO_EDGE_NO_LIVE") for value in DRY_RUN_RESULT_CLASSES),
        "unresolved_fields_preserved": len(UNRESOLVED_FIELDS) == 5,
        "exactly_one_python_tool_created": bool(preflight["target_tool_present_as_new_untracked_file"]),
        "exactly_one_json_artifact_created": not preflight["target_artifact_preexisting_before_run"],
        "no_existing_files_modified": bool(preflight["no_existing_files_modified"]),
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        fail_closed("VALIDATION_CHECKS_FAILED_BEFORE_ARTIFACT_WRITE", validation_checks)

    safety_permissions = {
        "validator_dry_run_design_created": True,
        "validator_execution_allowed_now": False,
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
            "clean_room_contract": {
                "path": CONTRACT_REL,
                "status": contract.get("status"),
                "artifact_kind": contract.get("artifact_kind"),
                "payload_sha256_excluding_hash": contract.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "runner_preview": {
                "path": RUNNER_PREVIEW_REL,
                "status": runner.get("status"),
                "artifact_kind": runner.get("artifact_kind"),
                "payload_sha256_excluding_hash": runner.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_preview": {
                "path": VALIDATOR_PREVIEW_REL,
                "status": validator.get("status"),
                "artifact_kind": validator.get("artifact_kind"),
                "payload_sha256_excluding_hash": validator.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_implementation_preview": {
                "path": IMPLEMENTATION_PREVIEW_REL,
                "status": implementation.get("status"),
                "artifact_kind": implementation.get("artifact_kind"),
                "payload_sha256_excluding_hash": implementation.get("payload_sha256_excluding_hash"),
                "next_allowed_step": implementation.get("next_allowed_step"),
                "loaded": True,
            },
            "old_short_artifact_metadata_only": summarize_old_short_metadata_only(),
            "master_upper_system_small_samples": inspect_master_proxy_small_samples(),
            "logger_script_text_only_metadata": inspect_logger_text_only(),
        },
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "validator_key": VALIDATOR_KEY,
            "dry_run_design_only": True,
            "validator_execution_allowed_now": False,
            "exact_original_source_recovered": False,
            "behavioral_validation_only": True,
            "no_exact_replay_claim": True,
        },
        "future_dry_run_scope": {
            "operate_only_on_small_bounded_samples": True,
            "compare_clean_room_preview_output_sample_to_master_proxy_output_sample": True,
            "never_claim_exact_original_match": True,
            "never_produce_edge_candidate_runtime_live_capital_permission": True,
            "never_run_full_historical_backtest": True,
            "never_infer_missing_original_thresholds": True,
            "validator_execution_allowed_now": False,
        },
        "future_inputs": {
            "clean_room_output_sample_dir": "future bounded sample directory from clean-room preview output",
            "master_upper_system_proxy_sample_dir": str(MASTER_UPPER_SYSTEM_PATH),
            "validator_config_json": "future dry-run config JSON with sample limits and guards",
            "logger_metadata_reference": str(LOGGER_PATH),
            "old_short_clean_room_contract": CONTRACT_REL,
            "old_short_runner_preview": RUNNER_PREVIEW_REL,
            "old_short_validator_preview": VALIDATOR_PREVIEW_REL,
        },
        "sample_policy": {
            "maximum_rows_per_file_default": FUTURE_DEFAULT_SAMPLE_ROWS,
            "selected_bounded_window_if_available": True,
            "allowed_sample_material": [
                "headers and schema samples",
                "closed_trades sample",
                "rejected_entries sample",
                "signals sample",
                "pending/open sample if present",
            ],
            "must_not": [
                "read unbounded full datasets by default",
                "read raw market data",
                "run old_short strategy",
                "create new trades",
                "calculate live/order data",
            ],
            "this_module_sample_policy": f"metadata/header plus first {SAFE_SAMPLE_ROWS_NOW} rows only",
        },
        "dry_run_validation_flow": DRY_RUN_FLOW_STEPS,
        "schema_checks": schema_checks,
        "behavioral_similarity_checks": behavioral_similarity_checks,
        "dry_run_result_classes": {
            "allowed": DRY_RUN_RESULT_CLASSES,
            "forbidden": FORBIDDEN_RESULT_CLASSES,
        },
        "dry_run_thresholds": dry_run_thresholds,
        "output_report_schema": {
            "required_top_level_keys": [
                "status",
                "route_key",
                "validator_key",
                "sample_paths",
                "sample_row_counts",
                "schema_check_results",
                "behavioral_similarity_results",
                "threshold_results",
                "unresolved_fields_preserved",
                "pass_fail_classification",
                "limitations",
                "no_edge_no_live_permissions",
                "payload_sha256_excluding_hash",
            ],
            "classification_values": DRY_RUN_RESULT_CLASSES,
            "no_edge_no_live_permissions": True,
        },
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "next_allowed_step": NEXT_ALLOWED_STEP,
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
        "dry_run_design_only": payload["dry_run_identity"]["dry_run_design_only"],
        "validator_execution_allowed_now": payload["dry_run_identity"]["validator_execution_allowed_now"],
        "validation_flow_step_count": len(payload["dry_run_validation_flow"]),
        "schema_file_count": len(payload["schema_checks"]),
        "behavioral_check_count": len(payload["behavioral_similarity_checks"]),
        "result_class_count": len(payload["dry_run_result_classes"]["allowed"]),
        "unresolved_field_count": len(payload["unresolved_fields_preserved"]),
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
