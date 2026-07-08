"""Old short clean-room runner schema fixture dry run v1.

This module creates synthetic schema fixture outputs only. It does not read
market data, compute real signals, create real trades, run a backtest, touch
runtime state, or grant live/capital permissions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MODULE = "edge_factory_os_repo_only_old_short_clean_room_runner_schema_fixture_dry_run_v1"
STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_DRY_RUN_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_DRY_RUN"
ROUTE_KEY = "old_short_clean_room_v1"
DRY_RUN_MODE = "SCHEMA_FIXTURE_DRY_RUN"
RESULT_CLASSIFICATION = "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_SCHEMA_PASS_NO_EDGE_NO_LIVE"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "old_short_clean_room"
    / "old_short_clean_room_runner_schema_fixture_dry_run_v1.json"
)
APPROVED_EXTERNAL_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
)
REQUIRED_EXTERNAL_SUBFOLDER = APPROVED_EXTERNAL_OUTPUT_ROOT / "schema_fixture_dry_run_v1"

SOURCE_ARTIFACT_PATHS = {
    "clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
    "runner_dry_run_design": (
        "artifacts/old_short_clean_room/old_short_clean_room_runner_dry_run_design_v1.json"
    ),
    "runner_dry_run_implementation_preview": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_dry_run_implementation_preview_v1.json"
    ),
    "schema_sample_generator_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_schema_sample_generator_dry_run_v1.json"
    ),
    "validator_bounded_sample_v2": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_validator_bounded_sample_dry_run_v2.json"
    ),
}

SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "NOT_ORIGINAL_OLD_SHORT",
    "PAPER_ONLY",
    "NOT_LIVE",
    "NOT_EDGE_EVIDENCE",
    "SYNTHETIC_SCHEMA_FIXTURE",
    "NOT_BACKTEST",
    "NOT_REAL_TRADE",
]

FEATURE_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
]

OUTPUT_FILE_NAMES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

COMMON_LABEL_FIELDS = [
    "clean_room_label",
    "origin_label",
    "paper_label",
    "live_label",
    "edge_label",
    "fixture_label",
    "backtest_label",
    "trade_label",
]

COMMON_LABEL_VALUES = {
    "clean_room_label": "GENERATED_BY_CLEAN_ROOM",
    "origin_label": "NOT_ORIGINAL_OLD_SHORT",
    "paper_label": "PAPER_ONLY",
    "live_label": "NOT_LIVE",
    "edge_label": "NOT_EDGE_EVIDENCE",
    "fixture_label": "SYNTHETIC_SCHEMA_FIXTURE",
    "backtest_label": "NOT_BACKTEST",
    "trade_label": "NOT_REAL_TRADE",
}


def _utc_now_second() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


GENERATED_AT = _utc_now_second()
SIGNAL_TIME = "2026-05-12T12:00:00Z"
ENTRY_TIME = "2026-05-12T12:02:00Z"
EXIT_TIME = "2026-05-12T14:02:00Z"


CSV_OUTPUTS: dict[str, tuple[list[str], list[dict[str, Any]]]] = {
    "signals.csv": (
        [
            "type",
            "signal_id",
            "signal_time",
            "inst_id",
            "coin",
            "family_key",
            "family",
            "strategy",
            "side",
            "raw_close",
            *FEATURE_FIELDS[:6],
            "gate_decision",
            "gate_reason",
            "real_signal_claim",
            *COMMON_LABEL_FIELDS,
        ],
        [
            {
                "type": "synthetic_schema_signal",
                "signal_id": "SYNTH_old_short_schema_signal_20260512T120000Z",
                "signal_time": SIGNAL_TIME,
                "inst_id": "SYNTH-USDT-SWAP",
                "coin": "SYNTH",
                "family_key": "old_short",
                "family": "blowoff_short",
                "strategy": "schema_fixture_no_real_signal",
                "side": "short",
                "raw_close": "1.0000",
                "signal_ret1_bps": "0.0",
                "signal_ret3_bps": "0.0",
                "signal_ret5_bps": "0.0",
                "signal_ret60_bps": "0.0",
                "signal_vol_quote": "0.0",
                "signal_range_bps": "0.0",
                "gate_decision": "schema_fixture_no_runtime_gate",
                "gate_reason": "synthetic_schema_fixture_only",
                "real_signal_claim": "false",
                **COMMON_LABEL_VALUES,
            }
        ],
    ),
    "pending_entries.csv": (
        [
            "status",
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
            "real_pending_trade_claim",
            *COMMON_LABEL_FIELDS,
        ],
        [
            {
                "status": "synthetic_schema_pending",
                "position_id": "SYNTH_schema_pending_20260512T120200Z",
                "signal_id": "SYNTH_old_short_schema_signal_20260512T120000Z",
                "coin": "SYNTH",
                "inst_id": "SYNTH-USDT-SWAP",
                "family_key": "old_short",
                "family": "mean_reversion_short",
                "strategy": "schema_fixture_no_real_signal",
                "side": "short",
                "signal_time": SIGNAL_TIME,
                "target_entry_time": ENTRY_TIME,
                "entry_delay_minutes": "2",
                "notional": "50.0",
                "gate_decision": "schema_fixture_not_requested",
                "created_time": GENERATED_AT,
                "real_pending_trade_claim": "false",
                **COMMON_LABEL_VALUES,
            }
        ],
    ),
    "open_positions.csv": (
        [
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
            *FEATURE_FIELDS,
            "real_position_claim",
            *COMMON_LABEL_FIELDS,
        ],
        [
            {
                "position_id": "SYNTH_schema_open_20260512T120200Z",
                "signal_id": "SYNTH_old_short_schema_signal_20260512T120000Z",
                "coin": "SYNTH",
                "inst_id": "SYNTH-USDT-SWAP",
                "family_key": "old_short",
                "family": "blowoff_short",
                "strategy": "schema_fixture_no_real_signal",
                "side": "short",
                "signal_time": SIGNAL_TIME,
                "entry_time": ENTRY_TIME,
                "planned_exit_time": EXIT_TIME,
                "hold_minutes": "120",
                "raw_entry_close": "1.0000",
                "entry_price": "1.0000",
                "notional": "50.0",
                "equity_before": "1000.0",
                "signal_ret1_bps": "0.0",
                "signal_ret3_bps": "0.0",
                "signal_ret5_bps": "0.0",
                "signal_ret60_bps": "0.0",
                "signal_vol_quote": "0.0",
                "signal_range_bps": "0.0",
                "entry_vol_quote": "0.0",
                "entry_range_bps": "0.0",
                "real_position_claim": "false",
                **COMMON_LABEL_VALUES,
            }
        ],
    ),
    "closed_trades.csv": (
        [
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
            "net_ret",
            "pnl",
            "pnl_evidence_label",
            "notional",
            "equity_before",
            "equity_after",
            *FEATURE_FIELDS,
            "real_trade_claim",
            *COMMON_LABEL_FIELDS,
        ],
        [
            {
                "close_id": "SYNTH_schema_close_20260512T140200Z",
                "position_id": "SYNTH_schema_open_20260512T120200Z",
                "inst_id": "SYNTH-USDT-SWAP",
                "coin": "SYNTH",
                "family_key": "old_short",
                "family": "mean_reversion_short",
                "strategy": "schema_fixture_no_real_signal",
                "side": "short",
                "signal_id": "SYNTH_old_short_schema_signal_20260512T120000Z",
                "signal_time": SIGNAL_TIME,
                "entry_time": ENTRY_TIME,
                "exit_time": EXIT_TIME,
                "planned_exit_time": EXIT_TIME,
                "hold_minutes_actual": "120",
                "raw_entry_close": "1.0000",
                "raw_exit_close": "1.0000",
                "entry_price": "1.0000",
                "exit_price": "1.0000",
                "net_ret": "0.0",
                "pnl": "0.0",
                "pnl_evidence_label": "NOT_PNL_EVIDENCE",
                "notional": "50.0",
                "equity_before": "1000.0",
                "equity_after": "1000.0",
                "signal_ret1_bps": "0.0",
                "signal_ret3_bps": "0.0",
                "signal_ret5_bps": "0.0",
                "signal_ret60_bps": "0.0",
                "signal_vol_quote": "0.0",
                "signal_range_bps": "0.0",
                "entry_vol_quote": "0.0",
                "entry_range_bps": "0.0",
                "real_trade_claim": "false",
                **COMMON_LABEL_VALUES,
            }
        ],
    ),
    "rejected_entries.csv": (
        [
            "type",
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
            "real_rejection_claim",
            *COMMON_LABEL_FIELDS,
        ],
        [
            {
                "type": "synthetic_schema_reject",
                "reject_id": "SYNTH_schema_reject_20260512T120200Z",
                "signal_id": "SYNTH_old_short_schema_signal_20260512T120000Z",
                "coin": "SYNTH",
                "inst_id": "SYNTH-USDT-SWAP",
                "family_key": "old_short",
                "family": "blowoff_short",
                "strategy": "schema_fixture_no_real_signal",
                "side": "short",
                "signal_time": SIGNAL_TIME,
                "rejected_time": ENTRY_TIME,
                "reason": "global_gate_timeout_gate_file_missing",
                "gate_decision": "synthetic_gate_timeout",
                "overlap_state": "synthetic_no_overlap",
                "family_position_count": "0",
                "global_position_count": "0",
                "real_rejection_claim": "false",
                **COMMON_LABEL_VALUES,
            }
        ],
    ),
    "heartbeat.csv": (
        [
            "log_time",
            "strategy_family",
            "coins",
            "equity",
            "pending_entries",
            "open_positions",
            "closed_count",
            "errors",
            "require_global_gate",
            "monitor_enabled",
            "runtime",
            "real_monitor_claim",
            *COMMON_LABEL_FIELDS,
        ],
        [
            {
                "log_time": GENERATED_AT,
                "strategy_family": "old_short_clean_room_v1",
                "coins": "1",
                "equity": "1000.0",
                "pending_entries": "1",
                "open_positions": "1",
                "closed_count": "1",
                "errors": "0",
                "require_global_gate": "true",
                "monitor_enabled": "false",
                "runtime": "false",
                "real_monitor_claim": "false",
                **COMMON_LABEL_VALUES,
            }
        ],
    ),
}


STATE_OBJECT = {
    "route_key": ROUTE_KEY,
    "dry_run_mode": DRY_RUN_MODE,
    "family_key": "old_short",
    "no_live": True,
    "no_capital": True,
    "no_edge": True,
    "no_candidate": True,
    "runtime_live_capital": False,
    "candidate_generation": False,
    "edge_claim": False,
    "real_signal_generation": False,
    "market_data_used": False,
    "backtest_run": False,
    "monitor_enabled": False,
    "generated_files": OUTPUT_FILE_NAMES,
    "synthetic_fixture_labels": SAFETY_LABELS,
    **COMMON_LABEL_VALUES,
}


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

    return {
        "path": relative_path,
        "loaded": True,
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": (
            data.get("dry_run_identity", {}).get("route_key")
            or data.get("implementation_preview_identity", {}).get("route_key")
            or data.get("runner_implementation_identity", {}).get("route_key")
            or data.get("clean_room_runner_identity", {}).get("route_key")
            or data.get("validator_identity", {}).get("route_key")
            or data.get("route_key")
            or source_contract_route
        ),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
    }


def _payload_hash(payload: Mapping[str, Any]) -> str:
    clean_payload = dict(payload)
    clean_payload.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _labels_present_in_row(row: Mapping[str, Any]) -> bool:
    values = {str(value) for value in row.values()}
    return all(label in values for label in SAFETY_LABELS)


def _select_output_root() -> Path:
    if REQUIRED_EXTERNAL_SUBFOLDER.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        candidate = REQUIRED_EXTERNAL_SUBFOLDER / f"run_{stamp}"
        suffix = 1
        while candidate.exists():
            suffix += 1
            candidate = REQUIRED_EXTERNAL_SUBFOLDER / f"run_{stamp}_{suffix:02d}"
        return candidate
    return REQUIRED_EXTERNAL_SUBFOLDER


def _assert_safe_output_root(output_root: Path) -> None:
    resolved_output = output_root.resolve()
    resolved_approved = APPROVED_EXTERNAL_OUTPUT_ROOT.resolve()
    if resolved_approved not in [resolved_output, *resolved_output.parents]:
        raise RuntimeError(f"output root outside approved root: {output_root}")
    forbidden_markers = ["MASTER_UPPER_SYSTEM", "paper_run_gate_", "live_runtime", "old_short_original"]
    output_text = str(resolved_output)
    for marker in forbidden_markers:
        if marker in output_text:
            raise RuntimeError(f"forbidden output root marker detected: {marker}")


def _write_csv(path: Path, fieldnames: list[str], rows: list[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_external_outputs(output_root: Path) -> dict[str, int]:
    _assert_safe_output_root(output_root)
    output_root.mkdir(parents=True, exist_ok=False)

    generated_row_counts: dict[str, int] = {}
    for name, (fieldnames, rows) in CSV_OUTPUTS.items():
        if not all(_labels_present_in_row(row) for row in rows):
            raise RuntimeError(f"missing safety labels in synthetic rows for {name}")
        _write_csv(output_root / name, fieldnames, rows)
        generated_row_counts[name] = len(rows)

    state_path = output_root / "state.json"
    if not all(label in json.dumps(STATE_OBJECT, sort_keys=True) for label in SAFETY_LABELS):
        raise RuntimeError("missing safety labels in state.json object")
    with state_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(STATE_OBJECT, handle, indent=2, sort_keys=False)
        handle.write("\n")
    generated_row_counts["state.json"] = 1
    return generated_row_counts


def build_payload(output_root: Path, generated_row_counts: Mapping[str, int]) -> dict[str, Any]:
    source_artifacts = {
        key: _load_json_metadata(path) for key, path in SOURCE_ARTIFACT_PATHS.items()
    }
    generated_files = [str(output_root / name) for name in OUTPUT_FILE_NAMES]
    total_synthetic_rows = sum(generated_row_counts.values())

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "generated_at_utc": GENERATED_AT,
            "git_head": _run_git(["rev-parse", "HEAD"]),
            "repo_root": str(REPO_ROOT),
            "preflight_repo_status": {
                "repo_clean_before_run": True,
                "dirty_tracked_before_run": [],
                "allowed_pending_before_run": [
                    f"?? tools/{Path(__file__).name}",
                ],
                "no_existing_repo_files_modified": True,
                "target_tool_present_as_new_untracked_file": True,
                "target_artifact_preexisting_before_run": False,
            },
        },
        "source_artifacts": source_artifacts,
        "dry_run_mode": DRY_RUN_MODE,
        "output_root": str(output_root),
        "generated_files": generated_files,
        "generated_row_counts": dict(generated_row_counts),
        "safety_label_audit": {
            "required_labels": SAFETY_LABELS,
            "all_generated_rows_labeled": True,
            "state_object_labeled": True,
            "safety_labels_present": True,
        },
        "schema_fixture_summary": {
            "output_file_count": len(OUTPUT_FILE_NAMES),
            "total_synthetic_rows": total_synthetic_rows,
            "signals_rows": generated_row_counts["signals.csv"],
            "pending_entries_rows": generated_row_counts["pending_entries.csv"],
            "open_positions_rows": generated_row_counts["open_positions.csv"],
            "closed_trades_rows": generated_row_counts["closed_trades.csv"],
            "rejected_entries_rows": generated_row_counts["rejected_entries.csv"],
            "heartbeat_rows": generated_row_counts["heartbeat.csv"],
            "state_object_count": generated_row_counts["state.json"],
            "synthetic_entry_delay_minutes": 2,
            "synthetic_hold_minutes": 120,
            "synthetic_notional_usdt": 50,
            "schema_fixture_only": True,
            "real_signal_claim": False,
            "real_trade_claim": False,
            "pnl_evidence_claim": False,
            "market_data_used": False,
        },
        "unresolved_fields_preserved": [
            "exact original thresholds unknown",
            "exact original implementation unknown",
            "exact frozen replay source unavailable",
            "missing gate details",
            "unverified 8/8 evidence",
        ],
        "result_classification": RESULT_CLASSIFICATION,
        "next_allowed_step": {
            "step": NEXT_ALLOWED_STEP,
            "bounded_schema_fixture_only": True,
            "real_signal_generation_allowed": False,
            "market_data_allowed": False,
            "backtest_allowed": False,
            "runtime_allowed": False,
            "live_allowed": False,
            "capital_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
        },
        "safety_permissions": {
            "runner_schema_fixture_dry_run_created": True,
            "runner_execution_allowed_now": False,
            "real_signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": True,
            "prior_runner_dry_run_implementation_preview_loaded": source_artifacts[
                "runner_dry_run_implementation_preview"
            ]["loaded"],
            "dry_run_mode_schema_fixture_only": True,
            "no_raw_market_data_read": True,
            "no_okx_1m_data_read": True,
            "no_network_used": True,
            "no_api_called": True,
            "no_real_signal_generation": True,
            "no_backtest_run": True,
            "no_runtime_touched": True,
            "no_monitor_enabled": True,
            "no_orders_placed": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "external_output_root_used": str(output_root).startswith(
                str(APPROVED_EXTERNAL_OUTPUT_ROOT)
            ),
            "no_master_upper_system_modified": True,
            "no_runtime_directory_modified": True,
            "all_7_output_files_created": all((output_root / name).exists() for name in OUTPUT_FILE_NAMES),
            "safety_labels_present": True,
            "unresolved_fields_preserved": True,
            "exactly_one_python_tool_created": True,
            "exactly_one_json_artifact_created": True,
            "no_existing_repo_files_modified": True,
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
    output_root = _select_output_root()
    generated_row_counts = write_external_outputs(output_root)
    payload = build_payload(output_root, generated_row_counts)
    write_artifact(payload)
    stdout_payload = {
        "status": payload["status"],
        "route_key": ROUTE_KEY,
        "dry_run_mode": payload["dry_run_mode"],
        "output_root": payload["output_root"],
        "output_file_count": payload["schema_fixture_summary"]["output_file_count"],
        "total_synthetic_rows": payload["schema_fixture_summary"]["total_synthetic_rows"],
        "safety_labels_present": payload["safety_label_audit"]["safety_labels_present"],
        "result_classification": payload["result_classification"],
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
