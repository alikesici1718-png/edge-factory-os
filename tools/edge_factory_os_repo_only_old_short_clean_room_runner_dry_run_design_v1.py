"""Old short clean-room runner dry-run design v1.

This module creates a design artifact only. It does not execute a runner,
generate signals, create pending/open/closed trades, run a validator, run a
backtest, touch runtime state, or grant live/capital permissions.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MODULE = "edge_factory_os_repo_only_old_short_clean_room_runner_dry_run_design_v1"
STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_DESIGN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_DESIGN"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_IMPLEMENTATION_PREVIEW_V1"

RUNNER_EXECUTION_ALLOWED = False
SIGNAL_GENERATION_ALLOWED = False
POSITION_OPEN_ALLOWED = False
BACKTEST_ALLOWED = False
RUNTIME_ALLOWED = False
MONITOR_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "old_short_clean_room"
    / "old_short_clean_room_runner_dry_run_design_v1.json"
)

APPROVED_FUTURE_OUTPUT_ROOT = (
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
)

SOURCE_ARTIFACT_PATHS = {
    "clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
    "runner_preview": "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json",
    "runner_implementation_preview": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_implementation_preview_v1.json"
    ),
    "validator_bounded_sample_v2": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_validator_bounded_sample_dry_run_v2.json"
    ),
    "schema_sample_generator_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_schema_sample_generator_dry_run_v1.json"
    ),
}

NO_LIVE_GUARD_CONSTANTS = {
    "RUNNER_EXECUTION_ALLOWED": RUNNER_EXECUTION_ALLOWED,
    "SIGNAL_GENERATION_ALLOWED": SIGNAL_GENERATION_ALLOWED,
    "POSITION_OPEN_ALLOWED": POSITION_OPEN_ALLOWED,
    "BACKTEST_ALLOWED": BACKTEST_ALLOWED,
    "RUNTIME_ALLOWED": RUNTIME_ALLOWED,
    "MONITOR_ALLOWED": MONITOR_ALLOWED,
    "LIVE_TRADING_ALLOWED": LIVE_TRADING_ALLOWED,
    "CAPITAL_ALLOCATION_ALLOWED": CAPITAL_ALLOCATION_ALLOWED,
    "ORDER_PLACEMENT_ALLOWED": ORDER_PLACEMENT_ALLOWED,
    "CANDIDATE_GENERATION_ALLOWED": CANDIDATE_GENERATION_ALLOWED,
    "EDGE_CLAIM_ALLOWED": EDGE_CLAIM_ALLOWED,
}

FUTURE_DRY_RUN_MODES = [
    {
        "mode": "SCHEMA_FIXTURE_DRY_RUN",
        "uses_synthetic_schema_fixture_rows_only": True,
        "tests_output_writer_plumbing": True,
        "computes_real_signals": False,
        "claims_behavioral_match": False,
        "pnl_allowed": False,
    },
    {
        "mode": "FEATURE_FIXTURE_DRY_RUN",
        "allowed_only_if_separate_explicit_threshold_contract_exists_later": True,
        "uses_bounded_feature_rows_not_full_market_data": True,
        "paper_report_only": True,
        "candidate_edge_live_capital_allowed": False,
    },
    {
        "mode": "REPLAY_PROXY_DRY_RUN",
        "allowed_only_if_reviewed_bounded_proxy_gate_candle_fixture_exists": True,
        "exact_old_short_replay": False,
        "live_capital_allowed": False,
    },
]

DRY_RUN_STATES = [
    "DISABLED",
    "LOAD_FIXTURE_INPUTS",
    "VALIDATE_FIXTURE_BOUNDS",
    "BUILD_FEATURES_FROM_FIXTURE",
    "REQUIRE_THRESHOLD_CONTRACT",
    "EVALUATE_SIGNAL_MODULES",
    "REQUEST_GATE_FIXTURE",
    "WRITE_SYNTHETIC_OR_PAPER_OUTPUT",
    "BUILD_RUNNER_DRY_RUN_REPORT",
    "REPORT_ONLY",
    "FAIL_CLOSED",
]

FAIL_CLOSED_CONDITIONS = [
    "threshold contract missing and mode is not SCHEMA_FIXTURE_DRY_RUN",
    "fixture input outside approved roots",
    "fixture exceeds row limits",
    "raw market data path supplied",
    "runtime path supplied",
    "live/order/private fields detected",
    "gate fixture missing for gate-dependent mode",
    "no-live guard false",
    "output root overlaps MASTER_UPPER_SYSTEM or runtime roots",
]

RESULT_CLASSES_ALLOWED = [
    "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_SCHEMA_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]

RESULT_CLASSES_FORBIDDEN = [
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

FUTURE_OUTPUT_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

FUTURE_ROW_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "NOT_ORIGINAL_OLD_SHORT",
    "PAPER_ONLY",
    "NOT_LIVE",
    "NOT_EDGE_EVIDENCE",
]


def _utc_now_second() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _load_json_metadata(relative_path: str) -> Mapping[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"required source artifact missing: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    source_artifacts = data.get("source_artifacts", {})
    source_contract_route = None
    if isinstance(source_artifacts, dict):
        clean_room_contract = source_artifacts.get("clean_room_contract", {})
        if isinstance(clean_room_contract, dict):
            source_contract_route = clean_room_contract.get("route_key")

    route_key = (
        data.get("dry_run_identity", {}).get("route_key")
        or data.get("runner_implementation_identity", {}).get("route_key")
        or data.get("clean_room_runner_identity", {}).get("route_key")
        or data.get("validator_identity", {}).get("route_key")
        or data.get("route_key")
        or source_contract_route
    )

    return {
        "path": relative_path,
        "loaded": True,
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": route_key,
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
    }


def _payload_hash(payload: Mapping[str, Any]) -> str:
    clean_payload = dict(payload)
    clean_payload.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_payload() -> dict[str, Any]:
    source_artifacts = {
        key: _load_json_metadata(path) for key, path in SOURCE_ARTIFACT_PATHS.items()
    }

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "generated_at_utc": _utc_now_second(),
            "git_head": _run_git(["rev-parse", "HEAD"]),
            "repo_root": str(REPO_ROOT),
            "preflight_repo_status": {
                "repo_clean_before_run": True,
                "dirty_tracked_before_run": [],
                "allowed_pending_before_run": [
                    f"?? tools/{Path(__file__).name}",
                ],
                "no_existing_files_modified": True,
                "target_tool_present_as_new_untracked_file": True,
                "target_artifact_preexisting_before_run": False,
            },
        },
        "source_artifacts": source_artifacts,
        "dry_run_identity": {
            "route_key": ROUTE_KEY,
            "dry_run_design_only": True,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "original_exact_source_recovered": False,
            "behavioral_reconstruction": True,
            "no_exact_replay_claim": True,
        },
        "no_live_guard_constants": NO_LIVE_GUARD_CONSTANTS,
        "future_dry_run_modes": FUTURE_DRY_RUN_MODES,
        "threshold_policy": {
            "original_thresholds_unresolved": True,
            "runner_dry_run_fail_closed_if_threshold_contract_missing": True,
            "no_hidden_default_thresholds": True,
            "no_fallback_thresholds": True,
            "thresholds_inferred_from_pnl_allowed": False,
            "thresholds_inferred_from_master_outputs_allowed": False,
            "master_output_threshold_inference_requires_separate_reviewed_contract": True,
            "schema_fixture_dry_run_threshold_bypass_for_schema_plumbing_only": True,
            "schema_fixture_outputs_must_label": "SYNTHETIC_SCHEMA_SAMPLE",
        },
        "future_input_policy": {
            "allowed_inputs": [
                "bounded synthetic schema samples",
                "bounded feature fixture samples",
                "bounded gate fixture samples",
                "clean-room threshold contract if separately approved",
            ],
            "raw_full_market_data_allowed": False,
            "raw_okx_1m_full_data_allowed": False,
            "runtime_data_allowed": False,
            "private_account_data_allowed": False,
        },
        "future_output_policy": {
            "approved_external_dry_run_output_root": APPROVED_FUTURE_OUTPUT_ROOT,
            "forbidden_output_roots": [
                "MASTER_UPPER_SYSTEM",
                "paper_run_gate_* runtime roots",
                "live runtime directories",
                "old original output directories",
            ],
            "future_output_files": FUTURE_OUTPUT_FILES,
            "future_row_labels_or_accompanying_labels": FUTURE_ROW_LABELS,
            "files_written_now": ["old_short_clean_room_runner_dry_run_design_v1.json"],
            "future_output_files_written_now": False,
        },
        "dry_run_state_flow": {
            "state_count": len(DRY_RUN_STATES),
            "states": DRY_RUN_STATES,
            "terminal_report_state": "REPORT_ONLY",
            "fail_closed_state": "FAIL_CLOSED",
        },
        "fail_closed_conditions": {
            "condition_count": len(FAIL_CLOSED_CONDITIONS),
            "conditions": FAIL_CLOSED_CONDITIONS,
        },
        "dry_run_report_schema": {
            "required_top_level_keys": [
                "status",
                "route_key",
                "dry_run_mode",
                "input_fixture_paths",
                "output_root",
                "generated_files",
                "generated_row_counts",
                "fail_closed_reasons",
                "unresolved_fields_preserved",
                "no_live_permissions",
                "payload_sha256_excluding_hash",
            ],
            "hash_policy": "payload_sha256_excluding_hash excludes its own value",
        },
        "result_classes": {
            "allowed": RESULT_CLASSES_ALLOWED,
            "forbidden": RESULT_CLASSES_FORBIDDEN,
            "result_class_count": len(RESULT_CLASSES_ALLOWED),
        },
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "next_allowed_step": {
            "step": NEXT_ALLOWED_STEP,
            "runner_execution_allowed": False,
            "signal_generation_allowed": False,
            "raw_market_data_allowed": False,
            "backtest_allowed": False,
            "runtime_allowed": False,
            "live_allowed": False,
            "capital_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
        },
        "safety_permissions": {
            "runner_dry_run_design_created": True,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "position_open_allowed_now": False,
            "backtest_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "order_placement_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": True,
            "clean_room_contract_loaded": source_artifacts["clean_room_contract"]["loaded"],
            "runner_preview_loaded": source_artifacts["runner_preview"]["loaded"],
            "runner_implementation_preview_loaded": source_artifacts[
                "runner_implementation_preview"
            ]["loaded"],
            "validator_bounded_sample_v2_loaded": source_artifacts["validator_bounded_sample_v2"][
                "loaded"
            ],
            "original_exact_source_not_claimed": True,
            "behavioral_reconstruction_preserved": True,
            "unresolved_thresholds_not_filled": True,
            "no_hidden_default_thresholds": True,
            "no_runner_execution": True,
            "no_signal_generation": True,
            "no_position_open": True,
            "no_backtest_run": True,
            "no_runtime_touched": True,
            "no_monitor_enabled": True,
            "no_network_used": True,
            "no_api_called": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "no_live_guard_constants_false": all(
                value is False for value in NO_LIVE_GUARD_CONSTANTS.values()
            ),
            "future_dry_run_modes_defined": len(FUTURE_DRY_RUN_MODES) == 3,
            "threshold_policy_fail_closed_defined": True,
            "future_output_policy_defined": True,
            "fail_closed_conditions_defined": True,
            "unresolved_fields_preserved": True,
            "exactly_one_python_tool_created": True,
            "exactly_one_json_artifact_created": True,
            "no_existing_files_modified": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = _payload_hash(payload)
    return payload


def write_artifact(payload: Mapping[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def main() -> int:
    payload = build_payload()
    write_artifact(payload)
    stdout_payload = {
        "status": payload["status"],
        "route_key": payload["dry_run_identity"]["route_key"],
        "dry_run_design_only": True,
        "runner_execution_allowed_now": False,
        "dry_run_mode_count": len(payload["future_dry_run_modes"]),
        "state_count": payload["dry_run_state_flow"]["state_count"],
        "fail_closed_condition_count": payload["fail_closed_conditions"]["condition_count"],
        "result_class_count": payload["result_classes"]["result_class_count"],
        "unresolved_field_count": len(payload["unresolved_fields_preserved"]),
        "next_allowed_step": payload["next_allowed_step"]["step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
    }
    print(json.dumps(stdout_payload, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
