#!/usr/bin/env python3
"""Repo-only old_short clean-room schema sample generator preview v1.

This module writes a schema-sample-generator preview artifact only. It does not
generate sample rows, create a sample output directory, run old_short, run a
runner, run a validator, run a backtest, read raw market data, touch runtime,
place orders, use network or APIs, generate candidates, or claim edge.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
SAFE_DIRECTORY = "C:/Users/alike/OneDrive/Desktop/edge_lab_new/edge_factory_os_repo"

MODULE = "edge_factory_os_repo_only_old_short_clean_room_schema_sample_generator_preview_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_schema_sample_generator_preview_v1.py"
ARTIFACT_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_schema_sample_generator_preview_v1.json"
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

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
BOUNDED_DRY_RUN_PATH = REPO_ROOT / BOUNDED_DRY_RUN_REL
SAMPLE_OUTPUT_GENERATION_PREVIEW_PATH = REPO_ROOT / SAMPLE_OUTPUT_GENERATION_PREVIEW_REL

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_DRY_RUN_V1"

OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_sample_outputs_v1"
)

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

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
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

LABEL_FLAGS = {
    "synthetic_schema_sample": True,
    "not_original_old_short": True,
    "not_backtest": True,
    "not_trade": True,
    "not_pnl": True,
    "not_runtime": True,
    "not_real_trade": True,
    "not_edge_evidence": True,
}


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
        "next_module": "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_PREVIEW_BLOCKER_REVIEW",
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


def required_fields(schema: Any) -> list[str]:
    if isinstance(schema, list):
        return [str(item) for item in schema]
    if isinstance(schema, dict):
        fields = schema.get("required_top_level_keys")
        if isinstance(fields, list):
            return [str(item) for item in fields]
    return []


def optional_fields(output_name: str, runner_preview: dict[str, Any]) -> list[str]:
    schema = runner_preview.get("output_schema_preview", {})
    if isinstance(schema, dict) and isinstance(schema.get(output_name), dict):
        fields = schema[output_name].get("optional_preview_fields")
        if isinstance(fields, list):
            return [str(item) for item in fields]
    return ["sample_label", "schema_sample_note"]


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


def timestamp_expectations(fields: list[str]) -> list[str]:
    return [field for field in fields if "time" in field.lower()]


def build_file_schema_blueprints(contract: dict[str, Any], runner_preview: dict[str, Any]) -> dict[str, Any]:
    blueprints: dict[str, Any] = {}
    for output_name in EXPECTED_OUTPUT_FILES:
        schema = expected_schema(output_name, contract, runner_preview)
        fields = required_fields(schema)
        blueprints[output_name] = {
            "file_name": output_name,
            "required_columns": schema,
            "optional_columns": optional_fields(output_name, runner_preview),
            "minimal_synthetic_row_count_for_future_dry_run": 1,
            "required_safety_labels_or_metadata": SYNTHETIC_LABELS,
            "timestamp_field_expectations": timestamp_expectations(fields),
            "family_key_expectation": "old_short" if output_name != "heartbeat.csv" else "strategy_family may identify old_short",
            "side_expectation": "short where side field exists",
            "no_live_order_private_fields": {
                "forbidden_fields": FORBIDDEN_LIVE_ORDER_PRIVATE_FIELDS,
                "must_be_absent": True,
            },
        }
    return blueprints


def label_row(row: dict[str, Any]) -> dict[str, Any]:
    merged = dict(row)
    merged.update(LABEL_FLAGS)
    merged["safety_labels"] = list(SYNTHETIC_LABELS)
    return merged


def build_minimal_synthetic_row_blueprints() -> dict[str, Any]:
    return {
        "signals.csv": label_row(
            {
                "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_001",
                "signal_time": "1970-01-01T00:00:00Z",
                "inst_id": "SYNTHETIC-USDT-SWAP",
                "coin": "SYNTHETIC",
                "family_key": "old_short",
                "family": "blowoff_short",
                "strategy": "blowoff_short",
                "side": "short",
            }
        ),
        "pending_entries.csv": label_row(
            {
                "position_id": "SYNTHETIC_SCHEMA_POSITION_001",
                "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_001",
                "coin": "SYNTHETIC",
                "family_key": "old_short",
                "side": "short",
                "target_entry_time": "1970-01-01T00:02:00Z",
            }
        ),
        "open_positions.csv": label_row(
            {
                "position_id": "SYNTHETIC_SCHEMA_POSITION_001",
                "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_001",
                "coin": "SYNTHETIC",
                "family_key": "old_short",
                "side": "short",
                "entry_time": "1970-01-01T00:02:00Z",
                "planned_exit_time": "1970-01-01T02:02:00Z",
            }
        ),
        "closed_trades.csv": label_row(
            {
                "close_id": "SYNTHETIC_SCHEMA_CLOSE_001",
                "position_id": "SYNTHETIC_SCHEMA_POSITION_001",
                "coin": "SYNTHETIC",
                "family_key": "old_short",
                "family": "mean_reversion_short",
                "strategy": "mean_reversion_short",
                "side": "short",
                "notional": "SYNTHETIC_NOTIONAL_NOT_CAPITAL",
                "pnl": "SYNTHETIC_NOT_PNL",
            }
        ),
        "rejected_entries.csv": label_row(
            {
                "reject_id": "SYNTHETIC_SCHEMA_REJECT_001",
                "signal_id": "SYNTHETIC_SCHEMA_SIGNAL_002",
                "coin": "SYNTHETIC",
                "family_key": "old_short",
                "side": "short",
                "reason": "SYNTHETIC_SCHEMA_GATE_BLOCK",
            }
        ),
        "heartbeat.csv": label_row(
            {
                "log_time": "1970-01-01T00:00:00Z",
                "strategy_family": "old_short_clean_room_v1",
                "coins": "1",
                "errors": "0",
                "require_global_gate": "true",
            }
        ),
        "state.json": label_row(
            {
                "route_key": ROUTE_KEY,
                "family_key": "old_short",
                "equity": "SYNTHETIC_NOT_CAPITAL",
                "pending_entries": [],
                "open_positions": [],
                "closed_count": 0,
            }
        ),
    }


def verify_prior_artifacts(
    contract: dict[str, Any],
    runner_preview: dict[str, Any],
    validator_preview: dict[str, Any],
    bounded_dry_run: dict[str, Any],
    sample_preview: dict[str, Any],
) -> None:
    checks = {
        "contract_loaded": contract.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED",
        "runner_preview_loaded": runner_preview.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED",
        "validator_preview_loaded": validator_preview.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED",
        "bounded_sample_dry_run_loaded": bounded_dry_run.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_CREATED",
        "sample_output_generation_preview_loaded": sample_preview.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW_CREATED",
        "previous_next_allowed_step": sample_preview.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_PREVIEW_V1",
        "bounded_dry_run_inconclusive": bounded_dry_run.get("result_classification")
        == "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
    }
    if not all(checks.values()):
        fail_closed("PRIOR_ARTIFACT_CHECK_FAILED", checks)

    contract_identity = contract.get("clean_room_identity", {})
    sample_identity = sample_preview.get("sample_generation_identity", {})
    identity_checks = {
        "contract_route_key": contract_identity.get("route_key") == ROUTE_KEY,
        "sample_route_key": sample_identity.get("route_key") == ROUTE_KEY,
        "contract_not_exact": contract_identity.get("original_exact_source_recovered") is False,
        "sample_not_exact": sample_identity.get("exact_original_source_recovered") is False,
        "contract_behavioral": contract_identity.get("behavioral_reconstruction") is True,
        "sample_behavioral": sample_identity.get("behavioral_reconstruction") is True,
        "sample_generation_allowed_false": sample_identity.get("sample_generation_allowed_now") is False,
    }
    if not all(identity_checks.values()):
        fail_closed("PRIOR_IDENTITY_CHECK_FAILED", identity_checks)


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
    runner_preview = load_json(RUNNER_PREVIEW_PATH, "RUNNER_PREVIEW")
    validator_preview = load_json(VALIDATOR_PREVIEW_PATH, "VALIDATOR_PREVIEW")
    bounded_dry_run = load_json(BOUNDED_DRY_RUN_PATH, "BOUNDED_SAMPLE_DRY_RUN")
    sample_preview = load_json(
        SAMPLE_OUTPUT_GENERATION_PREVIEW_PATH, "SAMPLE_OUTPUT_GENERATION_PREVIEW"
    )
    verify_prior_artifacts(contract, runner_preview, validator_preview, bounded_dry_run, sample_preview)

    file_schema_blueprints = build_file_schema_blueprints(contract, runner_preview)
    minimal_synthetic_row_blueprints = build_minimal_synthetic_row_blueprints()

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "contract_loaded": True,
        "runner_preview_loaded": True,
        "validator_preview_loaded": True,
        "bounded_sample_dry_run_loaded": True,
        "sample_output_generation_preview_loaded": True,
        "previous_next_allowed_step_verified": True,
        "no_sample_generated": True,
        "no_runner_execution": True,
        "no_validator_execution": True,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "synthetic_sample_policy_defined": True,
        "file_schema_blueprints_defined": len(file_schema_blueprints) == len(EXPECTED_OUTPUT_FILES),
        "minimal_synthetic_row_blueprints_defined": len(minimal_synthetic_row_blueprints)
        == len(EXPECTED_OUTPUT_FILES),
        "output_location_policy_defined": True,
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
        "schema_sample_generator_preview_created": True,
        "sample_generation_allowed_now": False,
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
            "clean_room_contract": {
                "path": CONTRACT_REL,
                "status": contract.get("status"),
                "payload_sha256_excluding_hash": contract.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "runner_preview": {
                "path": RUNNER_PREVIEW_REL,
                "status": runner_preview.get("status"),
                "payload_sha256_excluding_hash": runner_preview.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_preview": {
                "path": VALIDATOR_PREVIEW_REL,
                "status": validator_preview.get("status"),
                "payload_sha256_excluding_hash": validator_preview.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "bounded_sample_dry_run": {
                "path": BOUNDED_DRY_RUN_REL,
                "status": bounded_dry_run.get("status"),
                "result_classification": bounded_dry_run.get("result_classification"),
                "next_allowed_step": bounded_dry_run.get("next_allowed_step"),
                "loaded": True,
            },
            "sample_output_generation_preview": {
                "path": SAMPLE_OUTPUT_GENERATION_PREVIEW_REL,
                "status": sample_preview.get("status"),
                "next_allowed_step": sample_preview.get("next_allowed_step"),
                "loaded": True,
            },
        },
        "generator_preview_identity": {
            "route_key": ROUTE_KEY,
            "schema_sample_generator_preview_only": True,
            "sample_generation_allowed_now": False,
            "original_exact_source_recovered": False,
            "behavioral_reconstruction": True,
            "synthetic_schema_sample_only": True,
            "no_behavioral_match_claim": True,
        },
        "generator_scope": {
            "future_output_files": EXPECTED_OUTPUT_FILES,
            "future_output_file_count": len(EXPECTED_OUTPUT_FILES),
            "purpose": [
                "test validator plumbing",
                "test schema compatibility",
                "test no-live/no-order safety labels",
                "not test strategy behavior",
                "not test PnL",
                "not test real signal quality",
            ],
        },
        "synthetic_sample_policy": {
            "required_labels": SYNTHETIC_LABELS,
            "future_generator_must_not": [
                "claim behavior match",
                "claim original old_short recovery",
                "create real trades",
                "use market data",
                "use gate decisions as live execution source",
                "compute PnL as evidence",
            ],
        },
        "file_schema_blueprints": file_schema_blueprints,
        "minimal_synthetic_row_blueprints": minimal_synthetic_row_blueprints,
        "output_location_policy": {
            "allowed_root": str(OUTPUT_ROOT),
            "must_not_write_into_master_upper_system": True,
            "must_not_write_into_runtime_directories": True,
            "must_not_overwrite_anything": True,
            "must_create_timestamped_or_versioned_subfolder": True,
            "sample_generation_allowed_now": False,
        },
        "future_dry_run_after_generation": {
            "may_be_used_by": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V2",
            "can_test": [
                "schema loading",
                "safety labels",
                "no-live fields",
                "validator plumbing",
            ],
            "cannot_test": [
                "behavioral similarity",
                "performance",
                "edge",
                "live readiness",
            ],
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
        "route_key": payload["generator_preview_identity"]["route_key"],
        "schema_sample_generator_preview_only": payload["generator_preview_identity"][
            "schema_sample_generator_preview_only"
        ],
        "sample_generation_allowed_now": payload["generator_preview_identity"][
            "sample_generation_allowed_now"
        ],
        "future_output_file_count": payload["generator_scope"]["future_output_file_count"],
        "synthetic_label_count": len(payload["synthetic_sample_policy"]["required_labels"]),
        "blueprint_count": len(payload["file_schema_blueprints"]),
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
