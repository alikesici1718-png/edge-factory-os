#!/usr/bin/env python3
"""Repo-only old_short clean-room rebuild contract v1.

This module creates a contract artifact only. It does not run a backtest,
implement a runner, touch runtime, start monitors, place orders, use network
or APIs, generate candidates, claim edge, or grant runtime/live/capital.
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
MODULE = "edge_factory_os_repo_only_old_short_clean_room_contract_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_contract_v1.py"
ARTIFACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_REBUILD_CONTRACT"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_V1"

OLD_SHORT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "old_short"
MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
LOGGER_PATH = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")
OLD_RELATED_PATHS = [
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_priority\live_blowoff_short_paper_realistic"),
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_1_no_session\live_blowoff_short_paper_realistic"),
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_2_final\live_blowoff_short_paper_realistic"),
]

EXPECTED_OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

CLOSED_TRADES_FIELDS = [
    "close_id",
    "position_id",
    "inst_id",
    "coin",
    "family_key",
    "family",
    "strategy",
    "side",
    "signal_id",
    "signal_time",
    "entry_time",
    "exit_time",
    "planned_exit_time",
    "hold_minutes_actual",
    "raw_entry_close",
    "raw_exit_close",
    "entry_price",
    "exit_price",
    "entry_slip_bps",
    "exit_slip_bps",
    "fee_bps_total",
    "stress_extra_bps",
    "gross_ret",
    "realistic_net_ret",
    "stress_net_ret",
    "net_ret",
    "notional",
    "pnl",
    "stress_pnl",
    "equity_before",
    "equity_after",
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
]

SIGNAL_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
]

SAFE_SAMPLE_ROWS = 3
LOGGER_SAMPLE_BYTES = 200_000
SAFE_DIRECTORY = "C:/Users/alike/OneDrive/Desktop/edge_lab_new/edge_factory_os_repo"


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
    artifact_preexisting = ARTIFACT_PATH.exists()
    return {
        "status_lines_before_run": lines,
        "allowed_pending_before_run": allowed_pending,
        "dirty_tracked_before_run": dirty_tracked,
        "unexpected_untracked_before_run": unexpected_untracked,
        "repo_clean_before_run": not dirty_tracked and not unexpected_untracked,
        "no_existing_files_modified": not dirty_tracked,
        "tool_created_as_single_python_tool": tool_created and TOOL_PATH.exists(),
        "artifact_preexisting_before_run": artifact_preexisting,
        "artifact_will_be_single_json_artifact": not artifact_preexisting,
    }


def fail_closed(reason: str, details: dict[str, Any] | None = None) -> None:
    payload = {
        "status": "BLOCKED",
        "reason": reason,
        "details": details or {},
        "replacement_checks_all_true": False,
        "next_module": "OLD_SHORT_CLEAN_ROOM_CONTRACT_BLOCKER_REVIEW",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(1)


def load_old_short_artifacts() -> list[dict[str, Any]]:
    if not OLD_SHORT_ARTIFACT_DIR.exists():
        fail_closed("OLD_SHORT_ARTIFACT_DIR_MISSING", {"path": str(OLD_SHORT_ARTIFACT_DIR)})
    loaded: list[dict[str, Any]] = []
    for path in sorted(OLD_SHORT_ARTIFACT_DIR.glob("*.json")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
        except Exception as exc:
            fail_closed("OLD_SHORT_ARTIFACT_LOAD_FAILED", {"path": rel, "error": repr(exc)})
        loaded.append(
            {
                "path": rel,
                "exists": True,
                "loaded": True,
                "size_bytes": path.stat().st_size,
                "top_level_keys": sorted(data.keys()) if isinstance(data, dict) else [],
                "status": data.get("status") if isinstance(data, dict) else None,
                "artifact_kind": data.get("artifact_kind") if isinstance(data, dict) else None,
            }
        )
    if not loaded:
        fail_closed("NO_PRIOR_OLD_SHORT_ARTIFACTS_LOADED", {"path": str(OLD_SHORT_ARTIFACT_DIR)})
    return loaded


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
        return {"read_error": repr(exc), "header": [], "sample_rows": []}
    return {"read_error": None, "header": header, "sample_rows": rows}


def sample_state_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"read_error": repr(exc), "top_level_keys": [], "sample": None}
    if isinstance(data, dict):
        sample = {key: data[key] for key in sorted(data.keys())[:10]}
        return {"read_error": None, "top_level_keys": sorted(data.keys()), "sample": sample}
    return {"read_error": None, "top_level_keys": [], "sample_type": type(data).__name__}


def inspect_master_outputs() -> list[dict[str, Any]]:
    if not MASTER_UPPER_SYSTEM_PATH.exists():
        fail_closed("MASTER_UPPER_SYSTEM_PATH_MISSING", {"path": str(MASTER_UPPER_SYSTEM_PATH)})
    outputs: list[dict[str, Any]] = []
    for name in EXPECTED_OUTPUT_FILES:
        path = MASTER_UPPER_SYSTEM_PATH / name
        record: dict[str, Any] = {
            "name": name,
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
        }
        if path.exists() and path.suffix.lower() == ".csv":
            record.update(sample_csv(path))
        elif path.exists() and path.suffix.lower() == ".json":
            record.update(sample_state_json(path))
        else:
            record["read_error"] = None
        outputs.append(record)
    return outputs


def inspect_logger() -> dict[str, Any]:
    if not LOGGER_PATH.exists():
        fail_closed("LOGGER_SCRIPT_MISSING", {"path": str(LOGGER_PATH)})
    text = LOGGER_PATH.read_text(encoding="utf-8", errors="replace")
    sample = text[:LOGGER_SAMPLE_BYTES]
    return {
        "path": str(LOGGER_PATH),
        "exists": True,
        "checked_as_text_only": True,
        "executed": False,
        "size_bytes": LOGGER_PATH.stat().st_size,
        "contains_old_short": "old_short" in sample.lower(),
        "contains_blowoff_short": "blowoff_short" in sample,
        "contains_mean_reversion_short": "mean_reversion_short" in sample,
        "contains_global_gate_reference": "gate" in sample.lower(),
    }


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_output_schema_contract() -> dict[str, Any]:
    base_signal_schema = [
        "signal_id",
        "signal_time",
        "inst_id",
        "coin",
        "family_key",
        "family",
        "strategy",
        "side",
        "raw_close",
        "signal_ret1_bps",
        "signal_ret3_bps",
        "signal_ret5_bps",
        "signal_ret60_bps",
        "signal_vol_quote",
        "signal_range_bps",
        "gate_decision",
        "gate_reason",
    ]
    pending_schema = [
        "position_id",
        "signal_id",
        "coin",
        "inst_id",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_time",
        "target_entry_time",
        "entry_delay_minutes",
        "notional",
        "gate_decision",
        "created_time",
    ]
    open_schema = [
        "position_id",
        "signal_id",
        "coin",
        "inst_id",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_time",
        "entry_time",
        "planned_exit_time",
        "hold_minutes",
        "raw_entry_close",
        "entry_price",
        "notional",
        "equity_before",
        "signal_ret1_bps",
        "signal_ret3_bps",
        "signal_ret5_bps",
        "signal_ret60_bps",
        "signal_vol_quote",
        "signal_range_bps",
        "entry_vol_quote",
        "entry_range_bps",
    ]
    rejected_schema = [
        "reject_id",
        "signal_id",
        "coin",
        "inst_id",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_time",
        "rejected_time",
        "reason",
        "gate_decision",
        "overlap_state",
        "family_position_count",
        "global_position_count",
    ]
    heartbeat_schema = [
        "log_time",
        "strategy_family",
        "coins",
        "equity",
        "pending_entries",
        "open_positions",
        "closed_count",
        "errors",
        "require_global_gate",
    ]
    return {
        "signals.csv": base_signal_schema,
        "pending_entries.csv": pending_schema,
        "open_positions.csv": open_schema,
        "closed_trades.csv": CLOSED_TRADES_FIELDS,
        "rejected_entries.csv": rejected_schema,
        "heartbeat.csv": heartbeat_schema,
        "state.json": {
            "required_top_level_keys": [
                "route_key",
                "family_key",
                "equity",
                "pending_entries",
                "open_positions",
                "closed_count",
                "last_signal_time",
                "last_heartbeat_time",
                "errors",
            ],
            "format": "JSON object",
        },
    }


def build_payload() -> dict[str, Any]:
    preflight = preflight_repo_status()
    if not preflight["repo_clean_before_run"] or not preflight["no_existing_files_modified"]:
        fail_closed("DIRTY_OR_UNEXPECTED_REPO_STATE_BEFORE_RUN", preflight)
    if not preflight["tool_created_as_single_python_tool"]:
        fail_closed("TARGET_TOOL_NOT_THE_SINGLE_NEW_PYTHON_TOOL", preflight)
    if not preflight["artifact_will_be_single_json_artifact"]:
        fail_closed("TARGET_ARTIFACT_ALREADY_EXISTS_OR_WOULD_MODIFY_EXISTING_FILE", preflight)

    source_artifacts = load_old_short_artifacts()
    master_outputs = inspect_master_outputs()
    logger_review = inspect_logger()
    head = git_output(["rev-parse", "HEAD"])
    commit_subject = git_output(["log", "-1", "--format=%s"])

    master_closed = next((item for item in master_outputs if item["name"] == "closed_trades.csv"), {})
    master_closed_header = master_closed.get("header") or []

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "prior_old_short_artifacts_loaded": bool(source_artifacts),
        "master_upper_system_path_checked": MASTER_UPPER_SYSTEM_PATH.exists(),
        "logger_script_checked_not_executed": bool(logger_review["exists"] and not logger_review["executed"]),
        "original_exact_source_not_claimed": True,
        "behavioral_reconstruction_declared": True,
        "no_backtest_run": True,
        "no_runner_implemented": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": bool(preflight["tool_created_as_single_python_tool"]),
        "exactly_one_json_artifact_created": bool(preflight["artifact_will_be_single_json_artifact"]),
        "no_existing_files_modified": bool(preflight["no_existing_files_modified"]),
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    if not replacement_checks_all_true:
        fail_closed("VALIDATION_CHECKS_FAILED_BEFORE_ARTIFACT_WRITE", validation_checks)

    safety_permissions = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }

    unresolved_fields = [
        "exact original thresholds",
        "exact original source implementation",
        "exact frozen replay source",
        "any missing gate details",
        "any unverified 8/8 evidence",
    ]

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "git_head": head,
            "git_head_subject": commit_subject,
            "generated_at_utc": utc_now(),
            "preflight_repo_status": preflight,
        },
        "source_artifacts": source_artifacts,
        "clean_room_identity": {
            "route_key": ROUTE_KEY,
            "name": "old_short_clean_room_v1",
            "original_exact_source_recovered": False,
            "behavioral_reconstruction": True,
            "not_exact_old_short": True,
            "exact_frozen_replay_claimed": False,
            "evidence_limitation": [
                "This is not original old_short source recovery.",
                "This is a clean-room behavioral reconstruction contract.",
                "MASTER_UPPER_SYSTEM evidence is proxy behavioral evidence.",
                "Exact frozen replay and frozen contract compatibility are not established.",
            ],
        },
        "behavioral_evidence_summary": {
            "master_upper_system_path": str(MASTER_UPPER_SYSTEM_PATH),
            "logger_path": str(LOGGER_PATH),
            "logger_script_review": logger_review,
            "old_related_paths": [{"path": str(path), "exists": path.exists()} for path in OLD_RELATED_PATHS],
            "known_output_files": master_outputs,
            "known_schema": {
                "closed_trades_header_from_master_sample": master_closed_header,
                "closed_trades_contract_fields": CLOSED_TRADES_FIELDS,
                "signal_fields": SIGNAL_FIELDS,
            },
            "known_family_subfamily_behavior": {
                "family_key": "old_short",
                "side": "short",
                "subfamilies": ["blowoff_short", "mean_reversion_short"],
                "entry_delay_minutes_observed": "approximately 2",
                "hold_minutes_observed": "approximately 120",
                "notional_observed": "50 USDT for 1000 USDT base equity under MASTER_UPPER_SYSTEM policy",
                "global_gate_required": True,
            },
        },
        "signal_contract": {
            "required_1m_fields": [
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
            "side": "short_only",
            "family_key": "old_short",
            "signal_fields": SIGNAL_FIELDS,
            "families": {
                "blowoff_short": {
                    "contract_definition": (
                        "Clean-room short signal family for upside blowoff behavior followed by short entry "
                        "eligibility, using 1m return, range, and quote-volume features observed in proxy outputs."
                    ),
                    "threshold_status": "unresolved_not_guessed",
                    "exact_original_thresholds_recovered": False,
                },
                "mean_reversion_short": {
                    "contract_definition": (
                        "Clean-room short signal family for upside mean-reversion behavior, using 1m return, "
                        "range, and quote-volume features observed in proxy outputs."
                    ),
                    "threshold_status": "unresolved_not_guessed",
                    "exact_original_thresholds_recovered": False,
                },
            },
            "threshold_policy": "Do not guess exact thresholds; future preview may parameterize candidates for review only.",
        },
        "gate_contract": {
            "global_gate_mandatory": True,
            "no_gate_allow_means_no_position": True,
            "same_coin_overlap_block": True,
            "family_max_positions_respected": True,
            "global_max_positions_respected": True,
            "gate_timeout_or_missing_file_behavior": "reject_entry_and_record_rejected_entries_row",
            "no_position_without_global_gate": True,
            "gate_details_status": "partially_proxy_observed_exact_details_unresolved",
        },
        "execution_contract": {
            "entry_delay_minutes": "approximately 2",
            "hold_minutes": "approximately 120",
            "output_lifecycle": ["signal", "pending", "open", "closed_or_rejected"],
            "entry_lifecycle_files": ["signals.csv", "pending_entries.csv", "open_positions.csv"],
            "exit_lifecycle_files": ["closed_trades.csv", "rejected_entries.csv"],
            "heartbeat_and_state_files": ["heartbeat.csv", "state.json"],
            "live_order_permission": False,
            "runtime_enablement": False,
            "runner_implemented_here": False,
            "backtest_run_here": False,
        },
        "sizing_contract": {
            "observed_notional_policy": "50 USDT notional at 1000 USDT base equity",
            "base_equity_reference_usdt": 1000,
            "observed_notional_usdt": 50,
            "paper_only_sizing": True,
            "capital_permission": False,
            "live_capital_allocation": False,
        },
        "output_schema_contract": build_output_schema_contract(),
        "validation_plan": {
            "future_validator_scope": "preview_only_behavioral_comparison_against_MASTER_UPPER_SYSTEM_proxy_evidence",
            "must_compare": [
                "family_key old_short preserved",
                "subfamily blowoff_short / mean_reversion_short preserved",
                "side short",
                "entry delay near 2 minutes",
                "hold near 120 minutes",
                "output schema compatible",
                "rejected/gate behavior compatible",
                "no position without global gate",
                "notional policy compatible",
                "behavior similarity measured but not claimed exact",
            ],
            "exact_identity_claim_allowed": False,
            "edge_claim_allowed": False,
        },
        "unresolved_fields": unresolved_fields,
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
        "route_key": payload["clean_room_identity"]["route_key"],
        "original_exact_source_recovered": payload["clean_room_identity"]["original_exact_source_recovered"],
        "behavioral_reconstruction": payload["clean_room_identity"]["behavioral_reconstruction"],
        "next_allowed_step": payload["next_allowed_step"],
        "unresolved_field_count": len(payload["unresolved_fields"]),
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
