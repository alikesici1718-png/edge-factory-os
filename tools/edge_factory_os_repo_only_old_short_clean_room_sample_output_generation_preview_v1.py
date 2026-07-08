#!/usr/bin/env python3
"""Repo-only old_short clean-room sample output generation preview v1.

This module writes a sample-output-generation preview artifact only. It does
not generate sample rows, run a runner, run a validator, run old_short, run a
backtest, read raw market data, touch runtime/live/capital, place orders, use
network or APIs, generate candidates, or claim edge.
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

MODULE = "edge_factory_os_repo_only_old_short_clean_room_sample_output_generation_preview_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_sample_output_generation_preview_v1.py"
ARTIFACT_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_sample_output_generation_preview_v1.json"
)
CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
VALIDATOR_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"
BOUNDED_DRY_RUN_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_bounded_sample_dry_run_v1.json"
)

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
BOUNDED_DRY_RUN_PATH = REPO_ROOT / BOUNDED_DRY_RUN_REL

MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
LOGGER_PATH = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")
SUGGESTED_EXTERNAL_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_sample_outputs_v1"
)

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_SCHEMA_SAMPLE_GENERATOR_PREVIEW_V1"

EXPECTED_OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

SAFETY_LABELS = [
    "GENERATED_CLEAN_ROOM_SAMPLE",
    "NOT_ORIGINAL_OUTPUT",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
]

LABEL_FLAGS = {
    "synthetic_schema_sample": True,
    "not_original_old_short": True,
    "not_backtest": True,
    "not_trade": True,
    "not_pnl": True,
    "not_runtime": True,
}

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
        "next_module": "OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW_BLOCKER_REVIEW",
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


def required_fields_from_schema(schema: Any) -> list[str]:
    if isinstance(schema, list):
        return [str(item) for item in schema]
    if isinstance(schema, dict):
        values = schema.get("required_top_level_keys")
        if isinstance(values, list):
            return [str(item) for item in values]
    return []


def expected_schema_map(contract: dict[str, Any], runner_preview: dict[str, Any]) -> dict[str, Any]:
    contract_schema = contract.get("output_schema_contract")
    runner_schema = runner_preview.get("output_schema_preview")
    schema_map: dict[str, Any] = {}
    for name in EXPECTED_OUTPUT_FILES:
        schema = None
        if isinstance(runner_schema, dict) and isinstance(runner_schema.get(name), dict):
            schema = runner_schema[name].get("contract_schema")
        if schema is None and isinstance(contract_schema, dict):
            schema = contract_schema.get(name)
        schema_map[name] = schema if schema is not None else []
    return schema_map


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


def inspect_master_small_samples() -> list[dict[str, Any]]:
    if not MASTER_UPPER_SYSTEM_PATH.exists():
        return [{"path": str(MASTER_UPPER_SYSTEM_PATH), "exists": False, "read_error": "path_missing"}]
    samples: list[dict[str, Any]] = []
    for name in EXPECTED_OUTPUT_FILES:
        path = MASTER_UPPER_SYSTEM_PATH / name
        item: dict[str, Any] = {
            "name": name,
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
            "sample_policy": f"header plus first {SAFE_SAMPLE_ROWS} rows only",
        }
        if path.exists() and path.suffix.lower() == ".csv":
            item.update(sample_csv(path))
        elif path.exists() and path.suffix.lower() == ".json":
            item.update(sample_json_metadata(path))
        else:
            item["read_error"] = None
        samples.append(item)
    return samples


def inspect_logger_text_only() -> dict[str, Any]:
    if not LOGGER_PATH.exists():
        return {"path": str(LOGGER_PATH), "exists": False, "read_error": "path_missing"}
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


def verify_prior_artifacts(
    contract: dict[str, Any],
    runner_preview: dict[str, Any],
    validator_preview: dict[str, Any],
    bounded_dry_run: dict[str, Any],
) -> None:
    checks = {
        "contract_status": contract.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED",
        "runner_status": runner_preview.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED",
        "validator_status": validator_preview.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED",
        "bounded_dry_run_status": bounded_dry_run.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_CREATED",
        "bounded_dry_run_inconclusive": bounded_dry_run.get("result_classification")
        == "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
        "next_step": bounded_dry_run.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_SAMPLE_OUTPUT_GENERATION_PREVIEW_V1",
    }
    if not all(checks.values()):
        fail_closed("PRIOR_ARTIFACT_CHECK_FAILED", checks)
    clean_room_review = bounded_dry_run.get("clean_room_sample_review", {})
    if clean_room_review.get("clean_room_sample_available") is not False:
        fail_closed("BOUNDED_DRY_RUN_NOT_MISSING_CLEAN_ROOM_SAMPLE", clean_room_review)
    identity = contract.get("clean_room_identity", {})
    runner_identity = runner_preview.get("clean_room_runner_identity", {})
    validator_identity = validator_preview.get("validator_identity", {})
    identity_checks = {
        "contract_route_key": identity.get("route_key") == ROUTE_KEY,
        "runner_route_key": runner_identity.get("route_key") == ROUTE_KEY,
        "contract_not_exact": identity.get("original_exact_source_recovered") is False,
        "runner_not_exact": runner_identity.get("original_exact_source_recovered") is False,
        "validator_not_exact": validator_identity.get("exact_original_source_recovered") is False,
        "contract_behavioral": identity.get("behavioral_reconstruction") is True,
        "runner_behavioral": runner_identity.get("behavioral_reconstruction") is True,
    }
    if not all(identity_checks.values()):
        fail_closed("PRIOR_IDENTITY_CHECK_FAILED", identity_checks)


def build_schema_sample_contract(schema_map: dict[str, Any]) -> dict[str, Any]:
    contract: dict[str, Any] = {}
    for name in EXPECTED_OUTPUT_FILES:
        required_columns = required_fields_from_schema(schema_map.get(name))
        minimal_fields = list(dict.fromkeys(required_columns[:12] + SAFETY_LABELS))
        contract[name] = {
            "required_columns": schema_map.get(name),
            "minimal_safe_placeholder_fields": minimal_fields,
            "labels": dict(LABEL_FLAGS),
            "row_generation_allowed_now": False,
            "behavioral_similarity_claim_allowed": False,
        }
    return contract


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
    verify_prior_artifacts(contract, runner_preview, validator_preview, bounded_dry_run)

    schema_map = expected_schema_map(contract, runner_preview)
    schema_sample_contract = build_schema_sample_contract(schema_map)

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "contract_loaded": True,
        "runner_preview_loaded": True,
        "validator_preview_loaded": True,
        "bounded_sample_dry_run_loaded": True,
        "previous_inconclusive_due_missing_clean_room_sample_verified": True,
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
        "safety_labels_defined": len(SAFETY_LABELS) == 6,
        "output_directory_policy_defined": True,
        "exactly_one_python_tool_created": bool(preflight["target_tool_present_as_new_untracked_file"]),
        "exactly_one_json_artifact_created": not preflight["target_artifact_preexisting_before_run"],
        "no_existing_files_modified": bool(preflight["no_existing_files_modified"]),
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        fail_closed("VALIDATION_CHECKS_FAILED_BEFORE_ARTIFACT_WRITE", validation_checks)

    safety_permissions = {
        "sample_generation_preview_created": True,
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
                "artifact_kind": contract.get("artifact_kind"),
                "payload_sha256_excluding_hash": contract.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "runner_preview": {
                "path": RUNNER_PREVIEW_REL,
                "status": runner_preview.get("status"),
                "artifact_kind": runner_preview.get("artifact_kind"),
                "payload_sha256_excluding_hash": runner_preview.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_preview": {
                "path": VALIDATOR_PREVIEW_REL,
                "status": validator_preview.get("status"),
                "artifact_kind": validator_preview.get("artifact_kind"),
                "payload_sha256_excluding_hash": validator_preview.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "bounded_sample_dry_run": {
                "path": BOUNDED_DRY_RUN_REL,
                "status": bounded_dry_run.get("status"),
                "result_classification": bounded_dry_run.get("result_classification"),
                "clean_room_sample_available": bounded_dry_run.get("clean_room_sample_review", {}).get(
                    "clean_room_sample_available"
                ),
                "next_allowed_step": bounded_dry_run.get("next_allowed_step"),
                "payload_sha256_excluding_hash": bounded_dry_run.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "master_upper_system_small_samples": inspect_master_small_samples(),
            "logger_script_text_only_metadata": inspect_logger_text_only(),
        },
        "sample_generation_identity": {
            "route_key": ROUTE_KEY,
            "sample_generation_preview_only": True,
            "sample_generation_allowed_now": False,
            "runner_execution_allowed_now": False,
            "exact_original_source_recovered": False,
            "behavioral_reconstruction": True,
        },
        "future_sample_scope": {
            "purpose": "create clean-room output samples only for validator comparison",
            "future_output_files": EXPECTED_OUTPUT_FILES,
            "future_output_file_count": len(EXPECTED_OUTPUT_FILES),
            "sample_generation_allowed_now": False,
        },
        "input_policy": {
            "may_use": [
                "MASTER_UPPER_SYSTEM sample schemas",
                "logger metadata",
                "contract/runner preview schema",
                "synthetic minimal rows only if explicitly labeled SYNTHETIC_SCHEMA_SAMPLE",
            ],
            "must_not": [
                "claim behavioral match from synthetic rows",
                "read raw market data",
                "compute strategy signals",
                "make PnL claims",
            ],
            "no_raw_market_data": True,
            "no_strategy_signal_computation": True,
            "no_pnl_claims": True,
        },
        "sample_types": {
            "schema_sample_mode": {
                "description": "creates minimal schema-compatible rows",
                "use": "test validator plumbing only",
                "behavioral_similarity_claims_allowed": False,
                "allowed_now": False,
            },
            "replay_sample_mode": {
                "description": "future bounded clean-room runner output from bounded input candles/gate samples",
                "requires_bounded_clean_room_runner_implementation": True,
                "allowed_now": False,
            },
        },
        "output_directory_policy": {
            "not_mixed_with_master_output": True,
            "suggested_external_root": str(SUGGESTED_EXTERNAL_OUTPUT_ROOT),
            "repo_artifact_option": "clearly tracked preview artifact only",
            "sample_generation_allowed_now": False,
        },
        "schema_sample_contract": schema_sample_contract,
        "validator_interaction": {
            "future_generated_sample_should_allow": [
                "schema validation",
                "no-live field validation",
                "family_key / side presence validation",
            ],
            "future_generated_sample_should_not_allow": [
                "behavioral similarity pass",
                "edge claim",
                "live/capital conclusion",
            ],
        },
        "safety_labels": SAFETY_LABELS,
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
        "route_key": payload["sample_generation_identity"]["route_key"],
        "sample_generation_preview_only": payload["sample_generation_identity"][
            "sample_generation_preview_only"
        ],
        "sample_generation_allowed_now": payload["sample_generation_identity"][
            "sample_generation_allowed_now"
        ],
        "sample_type_count": len(payload["sample_types"]),
        "future_output_file_count": payload["future_sample_scope"]["future_output_file_count"],
        "safety_label_count": len(payload["safety_labels"]),
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
