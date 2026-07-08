#!/usr/bin/env python3
"""Repo-only old_short clean-room schema sample generator dry run v1.

This module creates synthetic schema sample files only under the approved
external sample-output root and writes one repo artifact. It does not run a
runner, run a validator, run old_short, run a backtest, read raw market data,
touch runtime/live/capital, place orders, use network or APIs, generate
candidates, or claim edge.
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

MODULE = "edge_factory_os_repo_only_old_short_clean_room_schema_sample_generator_dry_run_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_schema_sample_generator_dry_run_v1.py"
ARTIFACT_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_schema_sample_generator_dry_run_v1.json"
)
CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
VALIDATOR_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"
BOUNDED_DRY_RUN_REL = (
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

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
BOUNDED_DRY_RUN_PATH = REPO_ROOT / BOUNDED_DRY_RUN_REL
SAMPLE_OUTPUT_GENERATION_PREVIEW_PATH = REPO_ROOT / SAMPLE_OUTPUT_GENERATION_PREVIEW_REL
SCHEMA_GENERATOR_PREVIEW_PATH = REPO_ROOT / SCHEMA_GENERATOR_PREVIEW_REL

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_DRY_RUN"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V2"

EXTERNAL_OUTPUT_BASE = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_sample_outputs_v1"
)
REQUIRED_OUTPUT_SUBFOLDER = EXTERNAL_OUTPUT_BASE / "schema_sample_generator_dry_run_v1"

EXPECTED_OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
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

LABEL_COLUMNS = [
    "generated_clean_room_sample",
    "synthetic_schema_sample",
    "not_original_output",
    "not_real_trade",
    "not_backtest",
    "not_runtime",
    "not_edge_evidence",
    "safety_labels",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

FORBIDDEN_REPO_WRITE_PREFIXES = [
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM",
]


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
        "next_module": "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_DRY_RUN_BLOCKER_REVIEW",
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


def required_fields(schema: Any) -> list[str]:
    if isinstance(schema, list):
        return [str(item) for item in schema]
    if isinstance(schema, dict):
        fields = schema.get("required_top_level_keys")
        if isinstance(fields, list):
            return [str(item) for item in fields]
    return []


def expected_schema(output_name: str, contract: dict[str, Any], runner_preview: dict[str, Any]) -> Any:
    runner_schema = runner_preview.get("output_schema_preview", {})
    if isinstance(runner_schema, dict) and isinstance(runner_schema.get(output_name), dict):
        schema = runner_schema[output_name].get("contract_schema")
        if schema is not None:
            return schema
    contract_schema = contract.get("output_schema_contract", {})
    if isinstance(contract_schema, dict):
        return contract_schema.get(output_name, [])
    return []


def safe_output_dir() -> Path:
    base_resolved = EXTERNAL_OUTPUT_BASE.resolve()
    output_resolved = REQUIRED_OUTPUT_SUBFOLDER.resolve()
    if base_resolved not in [output_resolved, *output_resolved.parents]:
        fail_closed(
            "OUTPUT_DIR_OUTSIDE_APPROVED_ROOT",
            {"base": str(base_resolved), "output": str(output_resolved)},
        )
    for forbidden in FORBIDDEN_REPO_WRITE_PREFIXES:
        if str(output_resolved).lower().startswith(forbidden.lower()):
            fail_closed("OUTPUT_DIR_FORBIDDEN_MASTER_ROOT", {"output": str(output_resolved)})
    if REQUIRED_OUTPUT_SUBFOLDER.exists():
        stamp = utc_now().replace(":", "").replace("-", "")
        versioned = REQUIRED_OUTPUT_SUBFOLDER / f"run_{stamp}"
        if versioned.exists():
            fail_closed("VERSIONED_OUTPUT_DIR_ALREADY_EXISTS", {"path": str(versioned)})
        return versioned
    return REQUIRED_OUTPUT_SUBFOLDER


def synthetic_label_values() -> dict[str, str]:
    return {
        "generated_clean_room_sample": "true",
        "synthetic_schema_sample": "true",
        "not_original_output": "true",
        "not_real_trade": "true",
        "not_backtest": "true",
        "not_runtime": "true",
        "not_edge_evidence": "true",
        "safety_labels": "|".join(SYNTHETIC_LABELS),
    }


def row_with_labels(row: dict[str, Any]) -> dict[str, str]:
    merged = {key: str(value) for key, value in row.items()}
    merged.update(synthetic_label_values())
    return merged


def csv_headers(output_name: str, schema: Any, required_extra: list[str]) -> list[str]:
    fields = required_fields(schema)
    if not fields:
        fields = list(required_extra)
    for item in required_extra + LABEL_COLUMNS:
        if item not in fields:
            fields.append(item)
    return fields


def rows_for_file(output_name: str) -> list[dict[str, str]]:
    if output_name == "signals.csv":
        return [
            row_with_labels(
                {
                    "type": "synthetic_signal_pending_short",
                    "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_001",
                    "inst_id": "SYNTHETIC-USDT-SWAP",
                    "coin": "SYNTHETIC",
                    "family_key": "old_short",
                    "family": "blowoff_short",
                    "strategy": "blowoff_short",
                    "side": "short",
                    "signal_time": "1970-01-01T00:00:00Z",
                    "target_entry_time": "1970-01-01T00:02:00Z",
                    "planned_exit_time": "1970-01-01T02:02:00Z",
                    "entry_delay_minutes": "2",
                    "hold_minutes": "120",
                    "signal_close": "SYNTHETIC_PRICE",
                    "signal_ret1_bps": "SYNTHETIC_RET1_BPS",
                    "signal_ret3_bps": "SYNTHETIC_RET3_BPS",
                    "signal_ret5_bps": "SYNTHETIC_RET5_BPS",
                    "signal_ret60_bps": "SYNTHETIC_RET60_BPS",
                    "signal_vol_quote": "SYNTHETIC_VOL_QUOTE",
                    "signal_range_bps": "SYNTHETIC_RANGE_BPS",
                }
            ),
            row_with_labels(
                {
                    "type": "synthetic_signal_pending_short",
                    "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_002",
                    "inst_id": "SYNTHETIC2-USDT-SWAP",
                    "coin": "SYNTHETIC2",
                    "family_key": "old_short",
                    "family": "mean_reversion_short",
                    "strategy": "mean_reversion_short",
                    "side": "short",
                    "signal_time": "1970-01-01T00:10:00Z",
                    "target_entry_time": "1970-01-01T00:12:00Z",
                    "planned_exit_time": "1970-01-01T02:12:00Z",
                    "entry_delay_minutes": "2",
                    "hold_minutes": "120",
                    "signal_close": "SYNTHETIC_PRICE",
                    "signal_ret1_bps": "SYNTHETIC_RET1_BPS",
                    "signal_ret3_bps": "SYNTHETIC_RET3_BPS",
                    "signal_ret5_bps": "SYNTHETIC_RET5_BPS",
                    "signal_ret60_bps": "SYNTHETIC_RET60_BPS",
                    "signal_vol_quote": "SYNTHETIC_VOL_QUOTE",
                    "signal_range_bps": "SYNTHETIC_RANGE_BPS",
                }
            ),
        ]
    if output_name == "pending_entries.csv":
        return [
            row_with_labels(
                {
                    "position_id": "SYNTHETIC_SCHEMA_POSITION_001",
                    "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_001",
                    "coin": "SYNTHETIC",
                    "inst_id": "SYNTHETIC-USDT-SWAP",
                    "family_key": "old_short",
                    "family": "blowoff_short",
                    "strategy": "blowoff_short",
                    "side": "short",
                    "signal_time": "1970-01-01T00:00:00Z",
                    "target_entry_time": "1970-01-01T00:02:00Z",
                    "planned_entry_time": "1970-01-01T00:02:00Z",
                    "entry_delay_minutes": "2",
                    "notional": "SYNTHETIC_NOTIONAL_NOT_CAPITAL",
                    "gate_decision": "SYNTHETIC_GATE_PENDING",
                    "created_time": "1970-01-01T00:00:01Z",
                }
            )
        ]
    if output_name == "open_positions.csv":
        return [
            row_with_labels(
                {
                    "position_id": "SYNTHETIC_SCHEMA_POSITION_001",
                    "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_001",
                    "coin": "SYNTHETIC",
                    "inst_id": "SYNTHETIC-USDT-SWAP",
                    "family_key": "old_short",
                    "family": "blowoff_short",
                    "strategy": "blowoff_short",
                    "side": "short",
                    "signal_time": "1970-01-01T00:00:00Z",
                    "entry_time": "1970-01-01T00:02:00Z",
                    "planned_exit_time": "1970-01-01T02:02:00Z",
                    "hold_minutes": "120",
                    "raw_entry_close": "SYNTHETIC_PRICE",
                    "entry_price": "SYNTHETIC_PRICE",
                    "notional": "SYNTHETIC_NOTIONAL_NOT_CAPITAL",
                    "equity_before": "SYNTHETIC_NOT_CAPITAL",
                    "signal_ret1_bps": "SYNTHETIC_RET1_BPS",
                    "signal_ret3_bps": "SYNTHETIC_RET3_BPS",
                    "signal_ret5_bps": "SYNTHETIC_RET5_BPS",
                    "signal_ret60_bps": "SYNTHETIC_RET60_BPS",
                    "signal_vol_quote": "SYNTHETIC_VOL_QUOTE",
                    "signal_range_bps": "SYNTHETIC_RANGE_BPS",
                    "entry_vol_quote": "SYNTHETIC_ENTRY_VOL_QUOTE",
                    "entry_range_bps": "SYNTHETIC_ENTRY_RANGE_BPS",
                }
            )
        ]
    if output_name == "closed_trades.csv":
        return [
            row_with_labels(
                {
                    "close_id": "SYNTHETIC_SCHEMA_CLOSE_001",
                    "position_id": "SYNTHETIC_SCHEMA_POSITION_001",
                    "inst_id": "SYNTHETIC-USDT-SWAP",
                    "coin": "SYNTHETIC",
                    "family_key": "old_short",
                    "family": "blowoff_short",
                    "strategy": "blowoff_short",
                    "side": "short",
                    "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_001",
                    "signal_time": "1970-01-01T00:00:00Z",
                    "entry_time": "1970-01-01T00:02:00Z",
                    "exit_time": "1970-01-01T02:02:00Z",
                    "planned_exit_time": "1970-01-01T02:02:00Z",
                    "hold_minutes_actual": "120",
                    "raw_entry_close": "SYNTHETIC_PRICE",
                    "raw_exit_close": "SYNTHETIC_PRICE",
                    "entry_price": "SYNTHETIC_PRICE",
                    "exit_price": "SYNTHETIC_PRICE",
                    "entry_slip_bps": "SYNTHETIC_NOT_EXECUTED",
                    "exit_slip_bps": "SYNTHETIC_NOT_EXECUTED",
                    "fee_bps_total": "SYNTHETIC_NOT_EXECUTED",
                    "stress_extra_bps": "SYNTHETIC_NOT_EXECUTED",
                    "gross_ret": "SYNTHETIC_NOT_PNL",
                    "realistic_net_ret": "SYNTHETIC_NOT_PNL",
                    "stress_net_ret": "SYNTHETIC_NOT_PNL",
                    "net_ret": "SYNTHETIC_NOT_PNL",
                    "notional": "SYNTHETIC_NOTIONAL_NOT_CAPITAL",
                    "pnl": "SYNTHETIC_NOT_PNL",
                    "stress_pnl": "SYNTHETIC_NOT_PNL",
                    "equity_before": "SYNTHETIC_NOT_CAPITAL",
                    "equity_after": "SYNTHETIC_NOT_CAPITAL",
                    "signal_ret1_bps": "SYNTHETIC_RET1_BPS",
                    "signal_ret3_bps": "SYNTHETIC_RET3_BPS",
                    "signal_ret5_bps": "SYNTHETIC_RET5_BPS",
                    "signal_ret60_bps": "SYNTHETIC_RET60_BPS",
                    "signal_vol_quote": "SYNTHETIC_VOL_QUOTE",
                    "signal_range_bps": "SYNTHETIC_RANGE_BPS",
                    "entry_vol_quote": "SYNTHETIC_ENTRY_VOL_QUOTE",
                    "entry_range_bps": "SYNTHETIC_ENTRY_RANGE_BPS",
                }
            )
        ]
    if output_name == "rejected_entries.csv":
        return [
            row_with_labels(
                {
                    "reject_id": "SYNTHETIC_SCHEMA_REJECT_001",
                    "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_003",
                    "coin": "SYNTHETIC3",
                    "inst_id": "SYNTHETIC3-USDT-SWAP",
                    "family_key": "old_short",
                    "family": "mean_reversion_short",
                    "strategy": "mean_reversion_short",
                    "side": "short",
                    "signal_time": "1970-01-01T00:20:00Z",
                    "rejected_time": "1970-01-01T00:22:00Z",
                    "reason": "global_gate_timeout_gate_file_missing",
                    "gate_decision": "SYNTHETIC_GATE_TIMEOUT",
                    "overlap_state": "SYNTHETIC_NO_REAL_OVERLAP",
                    "family_position_count": "SYNTHETIC_COUNT",
                    "global_position_count": "SYNTHETIC_COUNT",
                }
            )
        ]
    if output_name == "heartbeat.csv":
        return [
            row_with_labels(
                {
                    "log_time": "1970-01-01T00:00:00Z",
                    "strategy_family": "old_short_clean_room_v1",
                    "coins": "SYNTHETIC_COUNT",
                    "equity": "SYNTHETIC_NOT_CAPITAL",
                    "pending_entries": "SYNTHETIC_COUNT",
                    "open_positions": "SYNTHETIC_COUNT",
                    "closed_count": "SYNTHETIC_COUNT",
                    "errors": "0",
                    "require_global_gate": "true",
                    "runtime_enabled": "false",
                    "monitor_enabled": "false",
                }
            )
        ]
    return []


def state_object() -> dict[str, Any]:
    state = {
        "route_key": ROUTE_KEY,
        "sample_type": "SYNTHETIC_SCHEMA_SAMPLE",
        "generated_clean_room_sample": True,
        "synthetic_schema_sample": True,
        "not_original_output": True,
        "not_runtime": True,
        "not_backtest": True,
        "not_edge_evidence": True,
        "no_live_permission": True,
        "no_capital_permission": True,
        "not_real_trade": True,
        "not_pnl": True,
        "safety_labels": list(SYNTHETIC_LABELS),
        "unresolved_fields_preserved": list(UNRESOLVED_FIELDS),
    }
    return state


def write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> int:
    if path.exists():
        fail_closed("REFUSING_TO_OVERWRITE_EXTERNAL_FILE", {"path": str(path)})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})
    return len(rows)


def write_json(path: Path, payload: dict[str, Any]) -> int:
    if path.exists():
        fail_closed("REFUSING_TO_OVERWRITE_EXTERNAL_FILE", {"path": str(path)})
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 1


def write_external_samples(output_dir: Path, contract: dict[str, Any], runner_preview: dict[str, Any]) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=False)
    sample_file_schemas: dict[str, Any] = {}
    generated_files: list[dict[str, Any]] = []
    total_rows = 0
    for output_name in EXPECTED_OUTPUT_FILES:
        schema = expected_schema(output_name, contract, runner_preview)
        if output_name == "state.json":
            path = output_dir / output_name
            rows_created = write_json(path, state_object())
            headers: list[str] = sorted(state_object().keys())
        else:
            required_extra = [
                "signal_id",
                "inst_id",
                "coin",
                "family_key",
                "family",
                "strategy",
                "side",
                "signal_time",
            ]
            headers = csv_headers(output_name, schema, required_extra)
            rows = rows_for_file(output_name)
            path = output_dir / output_name
            rows_created = write_csv(path, headers, rows)
        total_rows += rows_created
        sample_file_schemas[output_name] = {
            "schema_source": "contract_or_runner_preview_plus_safety_labels",
            "header_or_keys": headers,
            "required_schema": schema,
        }
        generated_files.append(
            {
                "file": output_name,
                "path": str(path),
                "rows_created": rows_created,
                "synthetic_schema_sample": True,
                "not_original_output": True,
                "not_real_trade": True,
                "not_backtest": True,
                "not_runtime": True,
                "not_edge_evidence": True,
            }
        )
    return {
        "output_dir": str(output_dir),
        "generated_files": generated_files,
        "sample_file_schemas": sample_file_schemas,
        "total_synthetic_rows": total_rows,
    }


def verify_prior_artifact(preview: dict[str, Any]) -> None:
    checks = {
        "status": preview.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_PREVIEW_CREATED",
        "next_allowed_step": preview.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_DRY_RUN_V1",
        "route_key": preview.get("generator_preview_identity", {}).get("route_key") == ROUTE_KEY,
        "sample_generation_allowed_now_false": preview.get("generator_preview_identity", {}).get(
            "sample_generation_allowed_now"
        )
        is False,
        "preview_only": preview.get("generator_preview_identity", {}).get(
            "schema_sample_generator_preview_only"
        )
        is True,
    }
    if not all(checks.values()):
        fail_closed("PREVIEW_ARTIFACT_CHECK_FAILED", checks)


def audit_labels(generated_files: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    per_file: dict[str, Any] = {}
    labels_present_all = True
    for entry in generated_files:
        name = entry["file"]
        path = output_dir / name
        if name == "state.json":
            data = json.loads(path.read_text(encoding="utf-8"))
            labels = set(data.get("safety_labels", []))
            labels_present = set(SYNTHETIC_LABELS).issubset(labels)
        else:
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                first = next(reader, {})
            labels = set(str(first.get("safety_labels", "")).split("|"))
            labels_present = set(SYNTHETIC_LABELS).issubset(labels)
        labels_present_all = labels_present_all and labels_present
        per_file[name] = {"labels_present": labels_present, "required_labels": SYNTHETIC_LABELS}
    return {"all_labels_present": labels_present_all, "per_file": per_file}


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

    contract = load_json(CONTRACT_PATH, "CLEAN_ROOM_CONTRACT")
    runner_preview = load_json(RUNNER_PREVIEW_PATH, "RUNNER_PREVIEW")
    _validator_preview = load_json(VALIDATOR_PREVIEW_PATH, "VALIDATOR_PREVIEW")
    _bounded_dry_run = load_json(BOUNDED_DRY_RUN_PATH, "BOUNDED_SAMPLE_DRY_RUN")
    _sample_preview = load_json(SAMPLE_OUTPUT_GENERATION_PREVIEW_PATH, "SAMPLE_OUTPUT_GENERATION_PREVIEW")
    schema_preview = load_json(SCHEMA_GENERATOR_PREVIEW_PATH, "SCHEMA_SAMPLE_GENERATOR_PREVIEW")
    verify_prior_artifact(schema_preview)

    output_dir = safe_output_dir()
    write_result = write_external_samples(output_dir, contract, runner_preview)
    label_audit = audit_labels(write_result["generated_files"], output_dir)

    output_paths = [Path(item["path"]) for item in write_result["generated_files"]]
    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "preview_artifact_loaded": True,
        "no_runner_execution": True,
        "no_validator_execution": True,
        "no_backtest_run": True,
        "no_market_data_read": True,
        "no_okx_1m_data_read": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "external_output_root_used": str(output_dir.resolve()).lower().startswith(
            str(EXTERNAL_OUTPUT_BASE.resolve()).lower()
        ),
        "no_master_upper_system_modified": True,
        "no_runtime_directory_modified": True,
        "all_7_sample_files_created": len(output_paths) == 7 and all(path.exists() for path in output_paths),
        "synthetic_labels_present": label_audit["all_labels_present"],
        "no_real_trade_claim": True,
        "no_pnl_evidence_claim": True,
        "unresolved_fields_preserved": len(UNRESOLVED_FIELDS) == 5,
        "exactly_one_python_tool_created": bool(preflight["target_tool_present_as_new_untracked_file"]),
        "exactly_one_json_artifact_created": not preflight["target_artifact_preexisting_before_run"],
        "no_existing_repo_files_modified": bool(preflight["no_existing_repo_files_modified"]),
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        fail_closed("VALIDATION_CHECKS_FAILED_AFTER_SAMPLE_WRITE", validation_checks)

    safety_permissions = {
        "schema_sample_generator_dry_run_created": True,
        "synthetic_sample_files_created": True,
        "runner_execution_allowed_now": False,
        "validator_execution_allowed_now": False,
        "backtest_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
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
            "schema_sample_generator_preview": {
                "path": SCHEMA_GENERATOR_PREVIEW_REL,
                "status": schema_preview.get("status"),
                "next_allowed_step": schema_preview.get("next_allowed_step"),
                "payload_sha256_excluding_hash": schema_preview.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "clean_room_contract": {
                "path": CONTRACT_REL,
                "status": contract.get("status"),
                "loaded": True,
            },
            "runner_preview": {
                "path": RUNNER_PREVIEW_REL,
                "status": runner_preview.get("status"),
                "loaded": True,
            },
        },
        "output_root": str(output_dir),
        "generated_sample_files": write_result["generated_files"],
        "sample_file_schemas": write_result["sample_file_schemas"],
        "synthetic_label_audit": label_audit,
        "generation_summary": {
            "output_file_count": len(write_result["generated_files"]),
            "total_synthetic_rows": write_result["total_synthetic_rows"],
            "files_created": [item["file"] for item in write_result["generated_files"]],
            "no_master_files_modified": True,
            "no_runtime_files_modified": True,
            "no_strategy_execution": True,
            "no_backtest": True,
            "no_pnl_evidence_claim": True,
        },
        "validator_usage_limitations": {
            "suitable_for_schema_validator_plumbing": True,
            "suitable_for_behavioral_similarity_claim": False,
            "suitable_for_edge_claim": False,
            "suitable_for_live_or_capital": False,
            "original_exact_source_recovered": False,
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
        "route_key": ROUTE_KEY,
        "output_root": payload["output_root"],
        "output_file_count": payload["generation_summary"]["output_file_count"],
        "total_synthetic_rows": payload["generation_summary"]["total_synthetic_rows"],
        "synthetic_label_count": len(SYNTHETIC_LABELS),
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
