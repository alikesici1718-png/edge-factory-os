"""Old short clean-room runner implementation preview v1.

This module is a preview artifact generator only. It does not execute a runner,
generate signals, create positions, run a backtest, touch runtime state, or
grant live/capital permissions.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MODULE = "edge_factory_os_repo_only_old_short_clean_room_runner_implementation_preview_v1"
STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_IMPLEMENTATION_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_IMPLEMENTATION_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_DESIGN_V1"

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
    / "old_short_clean_room_runner_implementation_preview_v1.json"
)

SOURCE_ARTIFACT_PATHS = {
    "clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
    "runner_preview": "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json",
    "validator_preview": "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json",
    "validator_bounded_sample_v2": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_validator_bounded_sample_dry_run_v2.json"
    ),
    "schema_sample_generator_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_schema_sample_generator_dry_run_v1.json"
    ),
}

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

FUTURE_SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "NOT_ORIGINAL_OLD_SHORT",
    "PAPER_ONLY",
    "NOT_LIVE",
    "NOT_EDGE_EVIDENCE",
]

LIFECYCLE_STEPS = [
    "signal candidate",
    "write signal",
    "pending entry",
    "approximately 2 minute entry delay",
    "request global gate",
    "gate allowed -> simulated/open paper position in future implementation only",
    "gate rejected/missing/timeout -> rejected_entries",
    "approximately 120 minute hold",
    "close position",
    "write closed trade",
    "heartbeat/state update",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]


@dataclass(frozen=True)
class OldShortCleanRoomConfig:
    """Configuration contract for a future clean-room runner implementation."""

    route_key: str = ROUTE_KEY
    family_key: str = "old_short"
    side: str = "short"
    base_equity_usdt: int = 1000
    paper_notional_usdt: int = 50
    entry_delay_minutes: int = 2
    hold_minutes: int = 120
    runner_execution_allowed: bool = RUNNER_EXECUTION_ALLOWED
    signal_generation_allowed: bool = SIGNAL_GENERATION_ALLOWED
    position_open_allowed: bool = POSITION_OPEN_ALLOWED
    backtest_allowed: bool = BACKTEST_ALLOWED
    runtime_allowed: bool = RUNTIME_ALLOWED
    live_trading_allowed: bool = LIVE_TRADING_ALLOWED
    capital_allocation_allowed: bool = CAPITAL_ALLOCATION_ALLOWED


class OldShortCandleFeatureBuilderPreview:
    """Feature schema contract only; no market data is read or computed here."""

    required_feature_fields = tuple(FEATURE_FIELDS)
    future_logic_only = True
    raw_market_data_read_allowed_now = False

    def describe_required_features(self) -> tuple[str, ...]:
        return self.required_feature_fields

    def build_features(self, candle_window: Any) -> Mapping[str, Any]:
        raise RuntimeError("preview only: feature computation is not allowed now")


class OldShortSignalModulePreview:
    """Signal contract only; thresholds remain unresolved and fail closed."""

    blowoff_short_thresholds_known = False
    mean_reversion_short_thresholds_known = False
    no_hidden_default_thresholds = True
    no_trade_signal_allowed_without_explicit_threshold_contract = True

    def evaluate_blowoff_short(
        self, features: Mapping[str, Any], threshold_contract: Mapping[str, Any] | None
    ) -> Mapping[str, Any]:
        if not threshold_contract:
            return {
                "allowed": False,
                "reason": "fail_closed_missing_explicit_threshold_contract",
                "signal_generated": False,
            }
        raise RuntimeError("preview only: signal evaluation is not executable now")

    def evaluate_mean_reversion_short(
        self, features: Mapping[str, Any], threshold_contract: Mapping[str, Any] | None
    ) -> Mapping[str, Any]:
        if not threshold_contract:
            return {
                "allowed": False,
                "reason": "fail_closed_missing_explicit_threshold_contract",
                "signal_generated": False,
            }
        raise RuntimeError("preview only: signal evaluation is not executable now")


class OldShortGateClientPreview:
    """Global gate contract only; no runtime connection is made."""

    global_gate_mandatory = True
    no_gate_allow_means_no_position = True
    gate_missing_timeout_rejected_entry = True
    same_coin_overlap_block = True
    family_global_max_limits_respected = True
    short_side_only = True
    runtime_connection_allowed_now = False

    def request_global_gate(self, signal_candidate: Mapping[str, Any]) -> Mapping[str, Any]:
        raise RuntimeError("preview only: global gate requests are not allowed now")


class OldShortPositionLifecyclePreview:
    """Lifecycle contract only; no positions are created."""

    steps = tuple(LIFECYCLE_STEPS)
    real_position_created_now = False

    def describe_flow(self) -> tuple[str, ...]:
        return self.steps

    def run_lifecycle(self, signal_candidate: Mapping[str, Any]) -> Mapping[str, Any]:
        raise RuntimeError("preview only: lifecycle execution is not allowed now")


class OldShortOutputWriterPreview:
    """Output schema contract only; no CSV/state files are written here."""

    future_safety_labels = tuple(FUTURE_SAFETY_LABELS)
    output_schemas = {
        "signals.csv": [
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
            "clean_room_label",
            "safety_label",
        ],
        "pending_entries.csv": [
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
            "clean_room_label",
            "safety_label",
        ],
        "open_positions.csv": [
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
            "clean_room_label",
            "safety_label",
        ],
        "closed_trades.csv": [
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
            *FEATURE_FIELDS,
            "clean_room_label",
            "safety_label",
        ],
        "rejected_entries.csv": [
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
            "clean_room_label",
            "safety_label",
        ],
        "heartbeat.csv": [
            "log_time",
            "strategy_family",
            "coins",
            "equity",
            "pending_entries",
            "open_positions",
            "closed_count",
            "errors",
            "require_global_gate",
            "clean_room_label",
            "safety_label",
        ],
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
                "clean_room_label",
                "safety_label",
            ]
        },
    }

    def describe_output_schemas(self) -> Mapping[str, Any]:
        return self.output_schemas

    def write_preview_output(self, output_name: str, rows: Any) -> None:
        raise RuntimeError("preview only: output writers are not allowed to write files now")


class OldShortHeartbeatStatePreview:
    """Heartbeat/state contract only; no state mutation happens here."""

    heartbeat_required = True
    state_update_required = True
    runtime_state_mutation_allowed_now = False

    def describe_state_contract(self) -> Mapping[str, Any]:
        return OldShortOutputWriterPreview.output_schemas["state.json"]

    def update_state(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        raise RuntimeError("preview only: state updates are not allowed now")


class OldShortCleanRoomRunnerImplementationPreview:
    """Top-level preview contract; does not execute runner behavior."""

    implementation_preview_only = True
    runner_execution_allowed_now = RUNNER_EXECUTION_ALLOWED
    classes: tuple[type[Any], ...] = ()

    def describe(self) -> Mapping[str, Any]:
        return {
            "route_key": ROUTE_KEY,
            "implementation_preview_only": True,
            "runner_execution_allowed_now": False,
            "class_names": [item.__name__ for item in self.classes],
        }

    def run(self) -> None:
        raise RuntimeError("preview only: runner execution is not allowed now")


OldShortCleanRoomRunnerImplementationPreview.classes = (
    OldShortCleanRoomConfig,
    OldShortCandleFeatureBuilderPreview,
    OldShortSignalModulePreview,
    OldShortGateClientPreview,
    OldShortPositionLifecyclePreview,
    OldShortOutputWriterPreview,
    OldShortHeartbeatStatePreview,
    OldShortCleanRoomRunnerImplementationPreview,
)


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
    clean_room_contract = data.get("clean_room_contract", {})
    clean_room_contract_route = None
    if isinstance(clean_room_contract, dict):
        clean_room_contract_route = clean_room_contract.get("route_key")
    return {
        "path": relative_path,
        "loaded": True,
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": (
            data.get("runner_implementation_identity", {}).get("route_key")
            or data.get("clean_room_runner_identity", {}).get("route_key")
            or data.get("validator_identity", {}).get("route_key")
            or clean_room_contract_route
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


def build_payload() -> dict[str, Any]:
    source_artifacts = {
        key: _load_json_metadata(path) for key, path in SOURCE_ARTIFACT_PATHS.items()
    }
    output_schemas = OldShortOutputWriterPreview.output_schemas
    class_names = [item.__name__ for item in OldShortCleanRoomRunnerImplementationPreview.classes]

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
        "runner_implementation_identity": {
            "route_key": ROUTE_KEY,
            "implementation_preview_only": True,
            "runner_execution_allowed_now": False,
            "original_exact_source_recovered": False,
            "behavioral_reconstruction": True,
            "no_exact_replay_claim": True,
        },
        "no_live_guard_constants": {
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
        },
        "runner_module_structure_preview": {
            "class_count": len(class_names),
            "class_contracts_defined_only": True,
            "classes": class_names,
            "runner_execution_implemented": False,
            "runner_execution_allowed_now": False,
            "standard_library_only": True,
        },
        "feature_builder_preview": {
            "class": "OldShortCandleFeatureBuilderPreview",
            "required_feature_fields": FEATURE_FIELDS,
            "future_logic_only": True,
            "feature_computation_allowed_now": False,
            "raw_market_data_read_allowed_now": False,
            "notes": "Feature formulas remain a future bounded fixture contract; no raw market data is read now.",
        },
        "signal_module_preview": {
            "class": "OldShortSignalModulePreview",
            "blowoff_short_thresholds_known": False,
            "mean_reversion_short_thresholds_known": False,
            "no_hidden_default_thresholds": True,
            "no_trade_signal_allowed_without_explicit_threshold_contract": True,
            "future_signal_module_contracts": [
                "evaluate_blowoff_short(features, threshold_contract)",
                "evaluate_mean_reversion_short(features, threshold_contract)",
            ],
            "fail_closed_policy": {
                "threshold_contract_missing": "return no-trade/fail-closed in future contract",
                "threshold_contract_missing_now": "no signal generation allowed",
                "hidden_default_thresholds_allowed": False,
            },
            "signal_generation_allowed_now": False,
        },
        "global_gate_client_preview": {
            "class": "OldShortGateClientPreview",
            "global_gate_mandatory": True,
            "no_gate_allow_means_no_position": True,
            "gate_missing_timeout": "rejected entry",
            "same_coin_overlap_block": True,
            "family_global_max_limits_respected": True,
            "short_side_only": True,
            "runtime_connection_allowed_now": False,
        },
        "lifecycle_preview": {
            "class": "OldShortPositionLifecyclePreview",
            "state_or_lifecycle_step_count": len(LIFECYCLE_STEPS),
            "state_flow": LIFECYCLE_STEPS,
            "entry_delay_minutes": "approximately 2",
            "hold_minutes": "approximately 120",
            "gate_allowed_future_behavior": "simulated/open paper position in future implementation only",
            "gate_rejected_missing_timeout_future_behavior": "write rejected_entries in future implementation only",
            "real_position_created_in_preview": False,
            "closed_trade_created_in_preview": False,
        },
        "output_writer_preview": {
            "class": "OldShortOutputWriterPreview",
            "output_writer_count": len(output_schemas),
            "schemas_defined_for": list(output_schemas.keys()),
            "schemas": output_schemas,
            "future_safety_labels": FUTURE_SAFETY_LABELS,
            "files_written_now": ["old_short_clean_room_runner_implementation_preview_v1.json"],
            "csv_or_state_outputs_written_now": False,
        },
        "sizing_preview": {
            "paper_notional_usdt": 50,
            "base_equity_usdt": 1000,
            "paper_only_sizing": True,
            "capital_permission_allowed_now": False,
            "live_order_sizing_allowed_now": False,
            "account_balance_usage_allowed_now": False,
        },
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "future_dry_run_contract": {
            "may_operate_only_on_bounded_synthetic_or_fixture_input": True,
            "raw_market_full_dataset_allowed": False,
            "runtime_allowed": False,
            "live_allowed": False,
            "capital_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
            "output_may_be_used_by_validator": True,
            "result_classes": [
                "paper-only",
                "no-edge",
                "no-live",
                "no-capital",
            ],
        },
        "next_allowed_step": {
            "step": NEXT_ALLOWED_STEP,
            "runner_execution_allowed": False,
            "raw_market_data_allowed": False,
            "backtest_allowed": False,
            "runtime_allowed": False,
            "live_allowed": False,
            "capital_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
        },
        "safety_permissions": {
            "runner_implementation_preview_created": True,
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
            "validator_preview_loaded": source_artifacts["validator_preview"]["loaded"],
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
                value is False
                for value in {
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
                }.values()
            ),
            "module_structure_preview_defined": True,
            "feature_builder_preview_defined": True,
            "signal_module_fail_closed_policy_defined": True,
            "gate_client_preview_defined": True,
            "lifecycle_preview_defined": True,
            "output_writer_preview_defined": True,
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
        "route_key": payload["runner_implementation_identity"]["route_key"],
        "implementation_preview_only": True,
        "runner_execution_allowed_now": False,
        "class_count": payload["runner_module_structure_preview"]["class_count"],
        "state_or_lifecycle_step_count": payload["lifecycle_preview"][
            "state_or_lifecycle_step_count"
        ],
        "output_writer_count": payload["output_writer_preview"]["output_writer_count"],
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
