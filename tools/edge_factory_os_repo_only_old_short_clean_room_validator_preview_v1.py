#!/usr/bin/env python3
"""Repo-only old_short clean-room validator preview v1.

This module writes a validator preview artifact only. It does not execute a
validator, run old_short, compute backtest returns, read full market data,
start monitors, touch runtime, place orders, use network or APIs, generate
candidates, claim edge, or grant runtime/live/capital permission.
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

MODULE = "edge_factory_os_repo_only_old_short_clean_room_validator_preview_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_validator_preview_v1.py"
ARTIFACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"
CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
OLD_SHORT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "old_short"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
VALIDATOR_KEY = "old_short_clean_room_validator_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW_V1"

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

TIMESTAMP_COLUMNS = {
    "signals.csv": ["signal_time", "target_entry_time", "planned_exit_time"],
    "pending_entries.csv": ["signal_time", "target_entry_time", "created_time"],
    "open_positions.csv": ["signal_time", "entry_time", "planned_exit_time"],
    "closed_trades.csv": ["signal_time", "entry_time", "exit_time", "planned_exit_time"],
    "rejected_entries.csv": ["signal_time", "rejected_time"],
    "heartbeat.csv": ["log_time"],
    "state.json": ["last_signal_time", "last_heartbeat_time"],
}

OPTIONAL_COLUMNS = {
    "signals.csv": ["preview_run_id", "preview_validation_note"],
    "pending_entries.csv": ["preview_run_id", "preview_validation_note"],
    "open_positions.csv": ["preview_run_id", "preview_validation_note"],
    "closed_trades.csv": ["preview_run_id", "preview_validation_note"],
    "rejected_entries.csv": ["preview_run_id", "preview_validation_note"],
    "heartbeat.csv": ["preview_run_id", "preview_validation_note"],
    "state.json": ["preview_run_id", "preview_validation_note"],
}

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

SIMILARITY_METRICS = {
    "schema_match_rate": "fraction of required output columns present and compatible",
    "family_key_match_rate": "fraction of comparable rows preserving family_key old_short",
    "side_match_rate": "fraction of comparable rows preserving side short",
    "entry_delay_median_abs_error_seconds": "median absolute entry-delay error versus proxy rows",
    "hold_minutes_median_abs_error": "median absolute hold duration error versus proxy rows",
    "notional_median_abs_error": "median absolute notional error versus proxy rows",
    "closed_trade_schema_compatibility": "closed_trades schema compatibility score",
    "rejected_entry_reason_overlap": "overlap between preview rejection reasons and proxy gate/rejection evidence",
    "signal_feature_distribution_similarity": "distributional similarity for required signal feature fields",
    "timestamp_alignment_rate": "rate of timestamps aligned within configured tolerance",
    "coin_overlap_rate": "coin overlap rate between preview and MASTER proxy samples",
    "gate_behavior_consistency_rate": "rate of gate allow/block behavior consistency",
}

SUGGESTED_VALIDATION_THRESHOLDS = {
    "schema_match_rate": {">=": 0.95},
    "family_key_match_rate": {">=": 0.99},
    "side_match_rate": {">=": 0.99},
    "median_entry_delay_error_seconds": {"<=": 60},
    "median_hold_error_minutes": {"<=": 10},
    "notional_median_error_usdt": {"<=": 5},
    "no_position_without_gate_allow": {"must_be": True},
    "no_live_order_fields": {"must_be": True},
    "closed_trades_schema_compatible": {"must_be": True},
}

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

SAFE_SAMPLE_ROWS = 3
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
        "next_module": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_BLOCKER_REVIEW",
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


def summarize_json_artifacts() -> list[dict[str, Any]]:
    if not OLD_SHORT_ARTIFACT_DIR.exists():
        fail_closed("OLD_SHORT_ARTIFACT_DIR_MISSING", {"path": str(OLD_SHORT_ARTIFACT_DIR)})
    summaries: list[dict[str, Any]] = []
    for path in sorted(OLD_SHORT_ARTIFACT_DIR.glob("*.json")):
        data = load_json(path, "OLD_SHORT_SOURCE_ARTIFACT")
        summaries.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "exists": True,
                "loaded": True,
                "size_bytes": path.stat().st_size,
                "artifact_kind": data.get("artifact_kind"),
                "status": data.get("status"),
                "top_level_keys": sorted(data.keys()),
            }
        )
    if not summaries:
        fail_closed("NO_PRIOR_OLD_SHORT_ARTIFACTS_LOADED", {"path": str(OLD_SHORT_ARTIFACT_DIR)})
    return summaries


def sample_csv(path: Path) -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            header = list(reader.fieldnames or [])
            for row in reader:
                if len(rows) >= SAFE_SAMPLE_ROWS:
                    break
                rows.append({str(k): str(v) for k, v in row.items()})
    except Exception as exc:
        return {"header": [], "sample_rows": [], "read_error": repr(exc)}
    return {"header": header, "sample_rows": rows, "read_error": None}


def sample_json(path: Path) -> dict[str, Any]:
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


def inspect_master_outputs() -> list[dict[str, Any]]:
    if not MASTER_UPPER_SYSTEM_PATH.exists():
        fail_closed("MASTER_UPPER_SYSTEM_PATH_MISSING", {"path": str(MASTER_UPPER_SYSTEM_PATH)})
    outputs: list[dict[str, Any]] = []
    for name in EXPECTED_FILES:
        path = MASTER_UPPER_SYSTEM_PATH / name
        item: dict[str, Any] = {
            "name": name,
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
        }
        if path.exists() and path.suffix.lower() == ".csv":
            item.update(sample_csv(path))
        elif path.exists() and path.suffix.lower() == ".json":
            item.update(sample_json(path))
        else:
            item["read_error"] = None
        outputs.append(item)
    return outputs


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
        "size_bytes": LOGGER_PATH.stat().st_size,
        "contains_old_short": "old_short" in lower,
        "contains_blowoff_short": "blowoff_short" in text,
        "contains_mean_reversion_short": "mean_reversion_short" in text,
        "contains_gate_reference": "gate" in lower,
    }


def required_columns_from_runner(runner_preview: dict[str, Any]) -> dict[str, Any]:
    output_preview = runner_preview.get("output_schema_preview")
    if not isinstance(output_preview, dict):
        fail_closed("RUNNER_PREVIEW_OUTPUT_SCHEMA_MISSING", {"path": RUNNER_PREVIEW_REL})
    required: dict[str, Any] = {}
    for name in EXPECTED_FILES:
        entry = output_preview.get(name)
        if not isinstance(entry, dict):
            fail_closed("RUNNER_PREVIEW_SCHEMA_FILE_MISSING", {"file": name})
        required[name] = entry.get("contract_schema")
    return required


def build_schema_validation_plan(runner_preview: dict[str, Any]) -> dict[str, Any]:
    required_by_file = required_columns_from_runner(runner_preview)
    plan: dict[str, Any] = {}
    for name in EXPECTED_FILES:
        required_columns = required_by_file[name]
        if isinstance(required_columns, dict):
            required_for_checks = required_columns.get("required_top_level_keys", [])
        else:
            required_for_checks = required_columns
        plan[name] = {
            "required_columns": required_columns,
            "optional_columns": OPTIONAL_COLUMNS[name],
            "type_checks": {
                "timestamp_columns": "ISO-8601 UTC parseable where present",
                "numeric_columns": "parseable numeric values for returns, prices, sizes, pnl, counts where present",
                "identity_columns": "non-empty strings where required",
                "state_json": "JSON object with required top-level keys" if name == "state.json" else None,
            },
            "timestamp_checks": {
                "columns": TIMESTAMP_COLUMNS[name],
                "must_be_monotonic_where_applicable": name in {"heartbeat.csv", "closed_trades.csv"},
                "no_future_runtime_requirement": True,
            },
            "family_key_checks": {
                "required_value": "old_short",
                "columns_checked": ["family_key"] if name != "heartbeat.csv" else ["strategy_family"],
                "heartbeat_strategy_family_allowed": ["old_short_gate_aware", "old_short_clean_room_v1"],
            },
            "side_checks": {
                "required_value": "short",
                "columns_checked": ["side"] if name not in {"heartbeat.csv", "state.json"} else [],
                "short_only": True,
            },
            "no_live_order_fields": {
                "forbidden_columns_or_keys": NO_LIVE_ORDER_FIELDS,
                "must_be_absent": True,
            },
            "schema_source": "runner_preview_contract_schema_and_MASTER_UPPER_SYSTEM_header_samples",
            "unknown_columns_policy": "reject_unless_explicitly_listed_optional_columns",
        }
        if isinstance(required_for_checks, list):
            plan[name]["required_column_count"] = len(required_for_checks)
    return plan


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
    runner_preview = load_json(RUNNER_PREVIEW_PATH, "CLEAN_ROOM_RUNNER_PREVIEW")

    contract_identity = contract.get("clean_room_identity", {})
    runner_identity = runner_preview.get("clean_room_runner_identity", {})
    if contract.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED":
        fail_closed("CLEAN_ROOM_CONTRACT_STATUS_UNEXPECTED", {"status": contract.get("status")})
    if runner_preview.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED":
        fail_closed("RUNNER_PREVIEW_STATUS_UNEXPECTED", {"status": runner_preview.get("status")})
    if contract_identity.get("route_key") != ROUTE_KEY or runner_identity.get("route_key") != ROUTE_KEY:
        fail_closed(
            "CLEAN_ROOM_ROUTE_KEY_MISMATCH",
            {
                "contract_route_key": contract_identity.get("route_key"),
                "runner_route_key": runner_identity.get("route_key"),
            },
        )
    if contract_identity.get("original_exact_source_recovered") is not False:
        fail_closed("CONTRACT_CLAIMS_ORIGINAL_EXACT_SOURCE", contract_identity)
    if runner_identity.get("original_exact_source_recovered") is not False:
        fail_closed("RUNNER_PREVIEW_CLAIMS_ORIGINAL_EXACT_SOURCE", runner_identity)
    if runner_identity.get("behavioral_reconstruction") is not True:
        fail_closed("RUNNER_PREVIEW_DOES_NOT_PRESERVE_BEHAVIORAL_RECONSTRUCTION", runner_identity)
    if runner_identity.get("preview_only") is not True:
        fail_closed("RUNNER_PREVIEW_IS_NOT_PREVIEW_ONLY", runner_identity)

    old_short_artifacts = summarize_json_artifacts()
    master_outputs = inspect_master_outputs()
    logger_review = inspect_logger_text_only()
    head = git_output(["rev-parse", "HEAD"])
    subject = git_output(["log", "-1", "--format=%s"])

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "clean_room_contract_loaded": True,
        "runner_preview_loaded": True,
        "original_exact_source_not_claimed": True,
        "behavioral_validation_only_declared": True,
        "no_backtest_run": True,
        "no_validator_execution": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": bool(preflight["target_tool_present_as_new_untracked_file"]),
        "exactly_one_json_artifact_created": not preflight["target_artifact_preexisting_before_run"],
        "no_existing_files_modified": bool(preflight["no_existing_files_modified"]),
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        fail_closed("VALIDATION_CHECKS_FAILED_BEFORE_ARTIFACT_WRITE", validation_checks)

    safety_permissions = {
        "validator_preview_created": True,
        "validator_execution_allowed_now": False,
        "backtest_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
    }

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
                "route_key": contract_identity.get("route_key"),
                "payload_sha256_excluding_hash": contract.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "runner_preview": {
                "path": RUNNER_PREVIEW_REL,
                "status": runner_preview.get("status"),
                "artifact_kind": runner_preview.get("artifact_kind"),
                "route_key": runner_identity.get("route_key"),
                "preview_only": runner_identity.get("preview_only"),
                "payload_sha256_excluding_hash": runner_preview.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "prior_old_short_artifacts": old_short_artifacts,
            "master_upper_system_output_samples": master_outputs,
            "logger_script_metadata": logger_review,
        },
        "validator_identity": {
            "route_key": ROUTE_KEY,
            "validator_key": VALIDATOR_KEY,
            "preview_only": True,
            "exact_original_source_recovered": False,
            "behavioral_validation_only": True,
            "not_validator_execution": True,
            "not_backtest": True,
            "not_strategy_execution": True,
            "not_edge_claim": True,
        },
        "validation_inputs": {
            "clean_room_runner_output_candidate_directory": "future_preview_output_directory_not_created_by_this_module",
            "master_upper_system_proxy_output_directory": str(MASTER_UPPER_SYSTEM_PATH),
            "logger_script_metadata": logger_review,
            "expected_files": EXPECTED_FILES,
            "input_scope": "metadata_headers_small_samples_only",
        },
        "schema_validation_plan": build_schema_validation_plan(runner_preview),
        "behavioral_validation_plan": {
            "comparison_basis": "clean-room output candidate versus MASTER_UPPER_SYSTEM proxy output",
            "required_behavior_checks": [
                "family_key old_short",
                "family blowoff_short / mean_reversion_short",
                "side short",
                "signal feature availability",
                "entry delay near 2 minutes",
                "hold near 120 minutes",
                "notional near 50 USDT for 1000 USDT base equity",
                "rejected entries caused by gate missing/timeout/block",
                "no open without gate allow",
                "same coin overlap blocked if evidence supports it",
            ],
            "signal_feature_availability": SIGNAL_FEATURE_FIELDS,
            "entry_delay_target": "near 2 minutes",
            "hold_target": "near 120 minutes",
            "notional_target": "near 50 USDT for 1000 USDT base equity",
            "gate_behavior": {
                "rejected_reasons": ["gate_missing", "gate_timeout", "gate_block"],
                "no_open_without_gate_allow": True,
                "same_coin_overlap_blocked_if_evidence_supports_it": True,
            },
            "no_exact_source_claim": True,
            "no_backtest_return_computation": True,
        },
        "similarity_metrics": SIMILARITY_METRICS,
        "pass_fail_policy": {
            "allowed_outcomes": [
                "CLEAN_ROOM_BEHAVIOR_MATCH_PASS_NO_EDGE_NO_LIVE",
                "CLEAN_ROOM_BEHAVIOR_MATCH_PARTIAL_NO_EDGE_NO_LIVE",
                "CLEAN_ROOM_BEHAVIOR_MATCH_FAIL_NO_EDGE_NO_LIVE",
                "CLEAN_ROOM_VALIDATION_INCONCLUSIVE_NO_EDGE_NO_LIVE",
            ],
            "forbidden_outcomes": [
                "original source recovered",
                "exact replay",
                "candidate",
                "edge claim",
                "runtime/live/capital permission",
            ],
            "exact_replay_claim_allowed": False,
            "edge_claim_allowed": False,
            "live_or_capital_permission_allowed": False,
        },
        "suggested_validation_thresholds": SUGGESTED_VALIDATION_THRESHOLDS,
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
        "route_key": payload["validator_identity"]["route_key"],
        "validator_key": payload["validator_identity"]["validator_key"],
        "preview_only": payload["validator_identity"]["preview_only"],
        "behavioral_validation_only": payload["validator_identity"]["behavioral_validation_only"],
        "similarity_metric_count": len(payload["similarity_metrics"]),
        "suggested_threshold_count": len(payload["suggested_validation_thresholds"]),
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
