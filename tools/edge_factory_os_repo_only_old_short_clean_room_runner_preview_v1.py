#!/usr/bin/env python3
"""Repo-only old_short clean-room runner preview v1.

This module writes a runner preview contract artifact only. It does not run a
backtest, read full market data, start monitors, touch runtime, place orders,
use network or APIs, generate candidates, claim edge, or grant permissions.
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

MODULE = "edge_factory_os_repo_only_old_short_clean_room_runner_preview_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_runner_preview_v1.py"
ARTIFACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_V1"

MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
LOGGER_PATH = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")
OLD_SHORT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "old_short"

EXPECTED_OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

RUNNER_STATES = [
    "DISABLED",
    "LOAD_1M_CANDLE",
    "COMPUTE_SIGNAL_FEATURES",
    "EVALUATE_BLOWOFF_SHORT",
    "EVALUATE_MEAN_REVERSION_SHORT",
    "WRITE_SIGNAL",
    "WAIT_ENTRY_DELAY",
    "REQUEST_GLOBAL_GATE",
    "GATE_ALLOWED",
    "GATE_REJECTED",
    "SIMULATE_OPEN_POSITION",
    "MONITOR_POSITION",
    "SIMULATE_CLOSE_POSITION",
    "WRITE_CLOSED_TRADE",
    "WRITE_REJECTED_ENTRY",
    "HEARTBEAT",
    "REPORT_ONLY",
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

UNRESOLVED_FIELDS = [
    "exact original thresholds",
    "exact original implementation",
    "exact frozen replay source",
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
        "next_module": "OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_BLOCKER_REVIEW",
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
    tool_created = any(
        status_code(line) == "??" and normalize_status_path(line) == TOOL_REL for line in lines
    )
    artifact_created_or_pending = ARTIFACT_PATH.exists() or any(
        status_code(line) == "??" and normalize_status_path(line) == ARTIFACT_REL for line in lines
    )
    return {
        "status_lines_before_run": lines,
        "allowed_pending_before_run": allowed_pending,
        "dirty_tracked_before_run": dirty_tracked,
        "unexpected_untracked_before_run": unexpected_untracked,
        "repo_clean_before_run": not dirty_tracked and not unexpected_untracked,
        "no_existing_files_modified": not dirty_tracked,
        "target_tool_present_as_new_untracked_file": tool_created and TOOL_PATH.exists(),
        "target_artifact_preexisting_before_run": ARTIFACT_PATH.exists(),
        "target_artifact_created_or_pending_before_run": artifact_created_or_pending,
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


def summarize_old_short_artifacts() -> list[dict[str, Any]]:
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
    for name in EXPECTED_OUTPUT_FILES:
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


def build_output_schema_preview(contract: dict[str, Any], master_outputs: list[dict[str, Any]]) -> dict[str, Any]:
    contract_schema = contract.get("output_schema_contract")
    if not isinstance(contract_schema, dict):
        fail_closed("CONTRACT_OUTPUT_SCHEMA_MISSING", {"contract_path": CONTRACT_REL})
    master_headers = {
        item["name"]: item.get("header", [])
        for item in master_outputs
        if item.get("exists") and item["name"].endswith(".csv")
    }
    preview: dict[str, Any] = {}
    for name in EXPECTED_OUTPUT_FILES:
        schema = contract_schema.get(name)
        if schema is None:
            fail_closed("CONTRACT_SCHEMA_OUTPUT_MISSING", {"output": name})
        preview[name] = {
            "contract_schema": schema,
            "master_upper_system_observed_header": master_headers.get(name),
            "optional_preview_fields": [
                "preview_run_id",
                "preview_validation_note",
            ],
            "unknown_columns_policy": "do_not_add_unknown_columns_unless_explicitly_marked_optional_preview_fields",
        }
    return preview


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
    if contract.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED":
        fail_closed("CLEAN_ROOM_CONTRACT_STATUS_UNEXPECTED", {"status": contract.get("status")})
    identity = contract.get("clean_room_identity", {})
    if not isinstance(identity, dict):
        fail_closed("CLEAN_ROOM_CONTRACT_IDENTITY_MISSING", {"contract_path": CONTRACT_REL})
    if identity.get("route_key") != ROUTE_KEY:
        fail_closed("CLEAN_ROOM_CONTRACT_ROUTE_KEY_MISMATCH", {"route_key": identity.get("route_key")})
    if identity.get("original_exact_source_recovered") is not False:
        fail_closed("CLEAN_ROOM_CONTRACT_CLAIMS_EXACT_SOURCE", identity)
    if identity.get("behavioral_reconstruction") is not True:
        fail_closed("CLEAN_ROOM_CONTRACT_DOES_NOT_DECLARE_BEHAVIORAL_RECONSTRUCTION", identity)

    old_short_artifacts = summarize_old_short_artifacts()
    master_outputs = inspect_master_outputs()
    logger_review = inspect_logger_text_only()
    head = git_output(["rev-parse", "HEAD"])
    subject = git_output(["log", "-1", "--format=%s"])

    source_artifacts = {
        "clean_room_contract": {
            "path": CONTRACT_REL,
            "status": contract.get("status"),
            "artifact_kind": contract.get("artifact_kind"),
            "route_key": identity.get("route_key"),
            "payload_sha256_excluding_hash": contract.get("payload_sha256_excluding_hash"),
            "loaded": True,
        },
        "prior_old_short_artifacts": old_short_artifacts,
        "master_upper_system_outputs_sampled": master_outputs,
        "logger_script_text_review": logger_review,
    }

    safety_permissions = {
        "runner_preview_created": True,
        "backtest_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
    }

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "clean_room_contract_loaded": True,
        "original_exact_source_not_claimed": True,
        "behavioral_reconstruction_preserved": True,
        "unresolved_thresholds_not_filled": True,
        "no_backtest_run": True,
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
        "source_artifacts": source_artifacts,
        "clean_room_runner_identity": {
            "route_key": ROUTE_KEY,
            "original_exact_source_recovered": False,
            "behavioral_reconstruction": True,
            "preview_only": True,
            "not_runtime": True,
            "not_backtest": True,
            "not_live_trading": True,
            "not_capital_allocation": True,
            "not_candidate_generation": True,
            "not_edge_claim": True,
        },
        "runner_state_machine": {
            "states": RUNNER_STATES,
            "initial_state": "DISABLED",
            "terminal_report_state": "REPORT_ONLY",
            "runtime_activation_allowed": False,
            "state_transition_preview": [
                "DISABLED -> LOAD_1M_CANDLE only inside future preview harness",
                "LOAD_1M_CANDLE -> COMPUTE_SIGNAL_FEATURES",
                "COMPUTE_SIGNAL_FEATURES -> EVALUATE_BLOWOFF_SHORT and EVALUATE_MEAN_REVERSION_SHORT",
                "eligible placeholder signal -> WRITE_SIGNAL -> WAIT_ENTRY_DELAY",
                "WAIT_ENTRY_DELAY -> REQUEST_GLOBAL_GATE",
                "gate allow -> GATE_ALLOWED -> SIMULATE_OPEN_POSITION",
                "gate block/missing/timeout -> GATE_REJECTED -> WRITE_REJECTED_ENTRY",
                "SIMULATE_OPEN_POSITION -> MONITOR_POSITION -> SIMULATE_CLOSE_POSITION -> WRITE_CLOSED_TRADE",
                "HEARTBEAT and REPORT_ONLY remain preview/report outputs only",
            ],
        },
        "signal_feature_schema": {
            "required_fields": SIGNAL_FEATURE_FIELDS,
            "source_timeframe": "1m candles",
            "required_input_columns": [
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "quote_volume_or_vol_quote",
                "inst_id",
                "coin",
            ],
        },
        "signal_module_contract": {
            "blowoff_short_thresholds_known": False,
            "mean_reversion_short_thresholds_known": False,
            "signal_evaluation_modules": "placeholders_only_until_explicit_threshold_contract",
            "future_implementation_requirement": "explicit_threshold_contract_required_before_execution",
            "no_hidden_default_thresholds_allowed": True,
            "unresolved_threshold_policy": "preserve_unresolved_status_do_not_guess",
            "allowed_preview_behavior": "describe state machine and schemas only; do not emit executable signal rules",
        },
        "gate_aware_contract": {
            "global_gate_mandatory": True,
            "no_gate_allow_means_no_position": True,
            "gate_missing_or_timeout_to_rejected_entries": True,
            "same_coin_overlap_blocked": True,
            "family_max_limits_respected": True,
            "global_max_limits_respected": True,
            "side": "short_only",
        },
        "lifecycle_contract": {
            "signal_to_pending_entries": True,
            "entry_delay_minutes": "approximately 2",
            "pending_to_open_condition": "global_gate_allow_required",
            "open_to_closed_after_hold_minutes": "approximately 120",
            "rejected_path": "gate_blocks_missing_or_timeout",
            "heartbeat_update": True,
            "state_update": True,
            "position_opening_is_simulated_preview_only": True,
        },
        "output_schema_preview": build_output_schema_preview(contract, master_outputs),
        "validation_preview": {
            "future_validator_target": "MASTER_UPPER_SYSTEM proxy output behavioral comparison",
            "must_compare": [
                "family_key old_short",
                "family blowoff_short / mean_reversion_short",
                "side short",
                "entry delay ~2 minutes",
                "hold ~120 minutes",
                "notional 50 USDT at 1000 USDT base equity",
                "output schema compatibility",
                "gate behavior compatibility",
                "no position without gate",
                "no exact-source claim",
            ],
            "exact_source_claim_allowed": False,
            "behavior_similarity_only": True,
            "backtest_or_edge_claim_allowed": False,
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
        "route_key": payload["clean_room_runner_identity"]["route_key"],
        "preview_only": payload["clean_room_runner_identity"]["preview_only"],
        "original_exact_source_recovered": payload["clean_room_runner_identity"]["original_exact_source_recovered"],
        "behavioral_reconstruction": payload["clean_room_runner_identity"]["behavioral_reconstruction"],
        "state_count": len(payload["runner_state_machine"]["states"]),
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
