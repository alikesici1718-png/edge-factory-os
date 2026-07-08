#!/usr/bin/env python3
"""Repo-only old_short clean-room validator dry-run execution preview v1.

This module writes an execution-preview artifact only. It does not execute a
validator, execute a bounded-sample validator, compare full datasets, run
old_short, compute PnL, run a backtest, touch runtime, place orders, use
network or APIs, generate candidates, claim edge, or grant permissions.
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

MODULE = "edge_factory_os_repo_only_old_short_clean_room_validator_dry_run_execution_preview_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_validator_dry_run_execution_preview_v1.py"
ARTIFACT_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_dry_run_execution_preview_v1.json"
)
CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
VALIDATOR_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"
VALIDATOR_IMPLEMENTATION_PREVIEW_REL = (
    "artifacts/old_short_clean_room/old_short_clean_room_validator_implementation_preview_v1.json"
)
DRY_RUN_DESIGN_REL = (
    "artifacts/old_short_clean_room/old_short_clean_room_validator_dry_run_design_v1.json"
)
DRY_RUN_IMPLEMENTATION_PREVIEW_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_dry_run_implementation_preview_v1.json"
)

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
VALIDATOR_IMPLEMENTATION_PREVIEW_PATH = REPO_ROOT / VALIDATOR_IMPLEMENTATION_PREVIEW_REL
DRY_RUN_DESIGN_PATH = REPO_ROOT / DRY_RUN_DESIGN_REL
DRY_RUN_IMPLEMENTATION_PREVIEW_PATH = REPO_ROOT / DRY_RUN_IMPLEMENTATION_PREVIEW_REL
OLD_SHORT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "old_short"

MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
LOGGER_PATH = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_EXECUTION_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_EXECUTION_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
VALIDATOR_KEY = "old_short_clean_room_validator_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_BOUNDED_SAMPLE_DRY_RUN_V1"

VALIDATOR_EXECUTION_ALLOWED = False
BOUNDED_SAMPLE_EXECUTION_ALLOWED = False
FULL_DATASET_COMPARISON_ALLOWED = False
BACKTEST_ALLOWED = False
RUNTIME_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False

EXPECTED_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

EXECUTION_STATES = [
    "DISABLED",
    "LOAD_VALIDATOR_CONFIG",
    "LOAD_SAMPLE_SOURCES",
    "CHECK_SAMPLE_BOUNDS",
    "RUN_SCHEMA_CHECKS",
    "RUN_BEHAVIORAL_CHECKS",
    "COMPUTE_SIMILARITY_METRICS",
    "APPLY_THRESHOLD_POLICY",
    "BUILD_DRY_RUN_REPORT",
    "REPORT_ONLY",
]

GUARDRAILS = [
    "fail_if_sample_path_outside_allowed_roots",
    "fail_if_file_size_exceeds_safe_bound_without_explicit_sample_limit",
    "fail_if_required_schemas_missing",
    "fail_if_clean_room_sample_missing",
    "fail_if_master_proxy_sample_missing",
    "fail_if_sample_row_count_exceeds_configured_max",
    "fail_if_live_order_private_fields_appear",
    "fail_if_any_no_live_guard_is_true",
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

DRY_RUN_RESULT_CLASSES = [
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_FAIL_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_VALIDATOR_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

NO_LIVE_ORDER_PRIVATE_FIELDS = [
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
FUTURE_DEFAULT_MAX_ROWS = 100
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
        "next_module": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_EXECUTION_PREVIEW_BLOCKER_REVIEW",
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
        return [{"path": str(MASTER_UPPER_SYSTEM_PATH), "exists": False, "read_error": "path_missing"}]
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
        "dry_run_implementation_next_allowed_step": prior["dry_run_implementation"].get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_EXECUTION_PREVIEW_V1",
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
    }
    identity_checks = {
        "contract_route_key": identities["contract"].get("route_key") == ROUTE_KEY,
        "runner_route_key": identities["runner"].get("route_key") == ROUTE_KEY,
        "validator_route_key": identities["validator"].get("route_key") == ROUTE_KEY,
        "validator_implementation_route_key": identities["validator_implementation"].get("route_key") == ROUTE_KEY,
        "dry_run_design_route_key": identities["dry_run_design"].get("route_key") == ROUTE_KEY,
        "dry_run_implementation_route_key": identities["dry_run_implementation"].get("route_key") == ROUTE_KEY,
        "validator_key": identities["validator"].get("validator_key") == VALIDATOR_KEY,
        "validator_implementation_key": identities["validator_implementation"].get("validator_key") == VALIDATOR_KEY,
        "dry_run_design_key": identities["dry_run_design"].get("validator_key") == VALIDATOR_KEY,
        "dry_run_implementation_key": identities["dry_run_implementation"].get("validator_key") == VALIDATOR_KEY,
        "contract_not_exact": identities["contract"].get("original_exact_source_recovered") is False,
        "runner_not_exact": identities["runner"].get("original_exact_source_recovered") is False,
        "validator_not_exact": identities["validator"].get("exact_original_source_recovered") is False,
        "implementation_not_exact": identities["validator_implementation"].get("exact_original_source_recovered") is False,
        "dry_run_design_not_exact": identities["dry_run_design"].get("exact_original_source_recovered") is False,
        "dry_run_implementation_not_exact": identities["dry_run_implementation"].get("exact_original_source_recovered") is False,
        "dry_run_implementation_behavioral": identities["dry_run_implementation"].get("behavioral_validation_only")
        is True,
        "dry_run_implementation_execution_false": identities["dry_run_implementation"].get(
            "validator_execution_allowed_now"
        )
        is False,
    }
    if not all(identity_checks.values()):
        fail_closed("PRIOR_IDENTITY_CHECK_FAILED", identity_checks)


def no_live_guard_constants() -> dict[str, bool]:
    return {
        "VALIDATOR_EXECUTION_ALLOWED": VALIDATOR_EXECUTION_ALLOWED,
        "BOUNDED_SAMPLE_EXECUTION_ALLOWED": BOUNDED_SAMPLE_EXECUTION_ALLOWED,
        "FULL_DATASET_COMPARISON_ALLOWED": FULL_DATASET_COMPARISON_ALLOWED,
        "BACKTEST_ALLOWED": BACKTEST_ALLOWED,
        "RUNTIME_ALLOWED": RUNTIME_ALLOWED,
        "LIVE_TRADING_ALLOWED": LIVE_TRADING_ALLOWED,
        "CAPITAL_ALLOCATION_ALLOWED": CAPITAL_ALLOCATION_ALLOWED,
        "ORDER_PLACEMENT_ALLOWED": ORDER_PLACEMENT_ALLOWED,
        "CANDIDATE_GENERATION_ALLOWED": CANDIDATE_GENERATION_ALLOWED,
        "EDGE_CLAIM_ALLOWED": EDGE_CLAIM_ALLOWED,
    }


def all_guard_constants_false() -> bool:
    return not any(no_live_guard_constants().values())


def build_future_bounded_sample_execution_plan() -> dict[str, Any]:
    return {
        "load_clean_room_validator_dry_run_implementation": True,
        "load_small_bounded_master_upper_system_sample": True,
        "load_small_bounded_clean_room_output_sample_if_available": True,
        "validate_schemas": True,
        "compute_behavioral_metrics_only_on_bounded_samples": True,
        "generate_dry_run_report": True,
        "never_run_strategy": True,
        "never_compute_pnl": True,
        "never_claim_exact_match": True,
        "execution_allowed_now": False,
    }


def build_sample_source_policy() -> dict[str, Any]:
    return {
        "maximum_rows_per_file_default": FUTURE_DEFAULT_MAX_ROWS,
        "allowed_sources": [
            "headers and small samples",
            "MASTER_UPPER_SYSTEM proxy output samples",
            "clean-room output sample directory if explicitly provided later",
        ],
        "no_raw_market_data": True,
        "no_full_data_comparison": True,
        "expected_files": EXPECTED_FILES,
    }


def build_execution_state_flow_preview() -> dict[str, Any]:
    return {
        "states": EXECUTION_STATES,
        "state_count": len(EXECUTION_STATES),
        "forbidden_state_targets": [
            "runtime",
            "monitor",
            "backtest",
            "orders",
            "candidate",
            "edge_claim",
        ],
        "terminal_state": "REPORT_ONLY",
        "all_states_report_or_sample_only": True,
    }


def build_bounded_sample_guardrails() -> dict[str, Any]:
    return {
        "guardrails": GUARDRAILS,
        "guardrail_count": len(GUARDRAILS),
        "fail_closed": True,
        "guard_constants_must_all_be_false": True,
    }


def build_similarity_metric_execution_preview() -> dict[str, Any]:
    return {
        "schema_match_rate": "bounded sample matched required columns / required columns",
        "family_key_match_rate": "bounded sample rows with old_short / comparable rows",
        "side_match_rate": "bounded sample rows with short side / comparable rows",
        "entry_delay_median_abs_error_seconds": "median bounded abs(candidate_delay_seconds - proxy_delay_seconds)",
        "hold_minutes_median_abs_error": "median bounded abs(candidate_hold_minutes - proxy_hold_minutes)",
        "notional_median_abs_error": "median bounded abs(candidate_notional - proxy_notional)",
        "closed_trade_schema_compatibility": "bounded closed_trades required fields present / required fields",
        "rejected_entry_reason_overlap": "bounded rejection reason set intersection / union",
        "signal_feature_distribution_similarity": "bounded similarity over required signal feature distributions",
        "timestamp_alignment_rate": "bounded aligned timestamps within tolerance / comparable timestamps",
        "coin_overlap_rate": "bounded coin set intersection / proxy coin set",
        "gate_behavior_consistency_rate": "bounded consistent gate events / comparable gate events",
    }


def build_threshold_policy_application_preview() -> dict[str, Any]:
    return {
        "schema_match_rate": {">=": 0.95},
        "family_key_match_rate": {">=": 0.99},
        "side_match_rate": {">=": 0.99},
        "median_entry_delay_error_seconds": {"<=": 60},
        "median_hold_error_minutes": {"<=": 10},
        "notional_median_error_usdt": {"<=": 5},
        "no_position_without_gate_allow": {"must_be": True},
        "no_live_order_fields": {"must_be": True},
        "closed_trades_schema_compatible": {"must_be": True},
        "threshold_type": "dry_run_validation_thresholds_not_strategy_parameters",
    }


def build_report_output_preview() -> dict[str, Any]:
    return {
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
            "result_classification",
            "limitations",
            "safety_permissions",
            "payload_sha256_excluding_hash",
        ],
        "allowed_result_classes": DRY_RUN_RESULT_CLASSES,
        "must_preserve_no_edge_no_live_permissions": True,
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
    }
    ensure_prior_artifacts(prior)

    future_plan = build_future_bounded_sample_execution_plan()
    sample_policy = build_sample_source_policy()
    state_flow = build_execution_state_flow_preview()
    guardrails = build_bounded_sample_guardrails()
    metric_preview = build_similarity_metric_execution_preview()
    threshold_preview = build_threshold_policy_application_preview()
    result_classes = list(DRY_RUN_RESULT_CLASSES)

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "clean_room_contract_loaded": True,
        "runner_preview_loaded": True,
        "validator_preview_loaded": True,
        "validator_implementation_preview_loaded": True,
        "validator_dry_run_design_loaded": True,
        "validator_dry_run_implementation_preview_loaded": True,
        "implementation_preview_next_allowed_step_verified": True,
        "original_exact_source_not_claimed": True,
        "behavioral_validation_only_preserved": True,
        "no_validator_execution": True,
        "no_bounded_sample_execution": True,
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_live_guard_constants_false": all_guard_constants_false(),
        "sample_source_policy_defined": len(sample_policy["expected_files"]) == len(EXPECTED_FILES),
        "execution_state_flow_defined": state_flow["state_count"] == len(EXECUTION_STATES),
        "bounded_sample_guardrails_defined": guardrails["guardrail_count"] == len(GUARDRAILS),
        "similarity_metric_execution_preview_defined": set(metric_preview.keys()) == set(SIMILARITY_METRICS),
        "future_result_classes_defined": len(result_classes) == 4,
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
        "validator_dry_run_execution_preview_created": True,
        "validator_execution_allowed_now": False,
        "bounded_sample_execution_allowed_now": False,
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
            "clean_room_contract": {
                "path": CONTRACT_REL,
                "status": prior["contract"].get("status"),
                "artifact_kind": prior["contract"].get("artifact_kind"),
                "payload_sha256_excluding_hash": prior["contract"].get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "runner_preview": {
                "path": RUNNER_PREVIEW_REL,
                "status": prior["runner"].get("status"),
                "artifact_kind": prior["runner"].get("artifact_kind"),
                "payload_sha256_excluding_hash": prior["runner"].get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_preview": {
                "path": VALIDATOR_PREVIEW_REL,
                "status": prior["validator"].get("status"),
                "artifact_kind": prior["validator"].get("artifact_kind"),
                "payload_sha256_excluding_hash": prior["validator"].get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_implementation_preview": {
                "path": VALIDATOR_IMPLEMENTATION_PREVIEW_REL,
                "status": prior["validator_implementation"].get("status"),
                "artifact_kind": prior["validator_implementation"].get("artifact_kind"),
                "payload_sha256_excluding_hash": prior["validator_implementation"].get(
                    "payload_sha256_excluding_hash"
                ),
                "loaded": True,
            },
            "validator_dry_run_design": {
                "path": DRY_RUN_DESIGN_REL,
                "status": prior["dry_run_design"].get("status"),
                "artifact_kind": prior["dry_run_design"].get("artifact_kind"),
                "payload_sha256_excluding_hash": prior["dry_run_design"].get(
                    "payload_sha256_excluding_hash"
                ),
                "loaded": True,
            },
            "validator_dry_run_implementation_preview": {
                "path": DRY_RUN_IMPLEMENTATION_PREVIEW_REL,
                "status": prior["dry_run_implementation"].get("status"),
                "artifact_kind": prior["dry_run_implementation"].get("artifact_kind"),
                "payload_sha256_excluding_hash": prior["dry_run_implementation"].get(
                    "payload_sha256_excluding_hash"
                ),
                "next_allowed_step": prior["dry_run_implementation"].get("next_allowed_step"),
                "loaded": True,
            },
            "old_short_artifact_metadata_only": summarize_old_short_metadata_only(),
            "master_upper_system_small_samples": inspect_master_proxy_small_samples(),
            "logger_script_text_only_metadata": inspect_logger_text_only(),
        },
        "execution_preview_identity": {
            "route_key": ROUTE_KEY,
            "validator_key": VALIDATOR_KEY,
            "execution_preview_only": True,
            "validator_execution_allowed_now": False,
            "bounded_sample_execution_allowed_now": False,
            "exact_original_source_recovered": False,
            "behavioral_validation_only": True,
            "no_exact_replay_claim": True,
        },
        "no_live_guard_constants": no_live_guard_constants(),
        "future_bounded_sample_execution_plan": future_plan,
        "sample_source_policy": sample_policy,
        "execution_state_flow_preview": state_flow,
        "bounded_sample_guardrails": guardrails,
        "similarity_metric_execution_preview": metric_preview,
        "threshold_policy_application_preview": threshold_preview,
        "future_dry_run_result_classes": result_classes,
        "report_output_preview": build_report_output_preview(),
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
        "route_key": payload["execution_preview_identity"]["route_key"],
        "validator_key": payload["execution_preview_identity"]["validator_key"],
        "execution_preview_only": payload["execution_preview_identity"]["execution_preview_only"],
        "validator_execution_allowed_now": payload["execution_preview_identity"][
            "validator_execution_allowed_now"
        ],
        "bounded_sample_execution_allowed_now": payload["execution_preview_identity"][
            "bounded_sample_execution_allowed_now"
        ],
        "state_count": payload["execution_state_flow_preview"]["state_count"],
        "guardrail_count": payload["bounded_sample_guardrails"]["guardrail_count"],
        "similarity_metric_count": len(payload["similarity_metric_execution_preview"]),
        "result_class_count": len(payload["future_dry_run_result_classes"]),
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
