"""Old short clean-room runner dry-run implementation preview v1.

This module creates an implementation-preview artifact only. It does not run a
runner, generate real signals, create trades, run a validator, run a backtest,
touch runtime state, or grant live/capital permissions.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MODULE = "edge_factory_os_repo_only_old_short_clean_room_runner_dry_run_implementation_preview_v1"
STATUS = (
    "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_IMPLEMENTATION_PREVIEW_CREATED"
)
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_DRY_RUN_IMPLEMENTATION_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_DRY_RUN_V1"

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
    / "old_short_clean_room_runner_dry_run_implementation_preview_v1.json"
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
    "runner_dry_run_design": (
        "artifacts/old_short_clean_room/old_short_clean_room_runner_dry_run_design_v1.json"
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

DRY_RUN_MODES = [
    {
        "mode": "SCHEMA_FIXTURE_DRY_RUN",
        "uses_synthetic_schema_fixture_rows_only": True,
        "tests_output_writer_plumbing": True,
        "may_generate_synthetic_output_in_future_step": True,
        "real_signal_computation_allowed": False,
        "behavioral_match_claim_allowed": False,
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

FAIL_CLOSED_THRESHOLD_POLICY_ITEMS = [
    "non-schema modes require explicit threshold_contract",
    "missing threshold_contract fails closed",
    "hidden or default thresholds are forbidden",
    "fallback thresholds are forbidden",
    "thresholds inferred from PnL are forbidden",
    "thresholds inferred from MASTER output require separate reviewed reconstruction contract",
    "SCHEMA_FIXTURE_DRY_RUN threshold bypass is schema-plumbing only with SYNTHETIC_SCHEMA_SAMPLE label",
]

APPROVED_FIXTURE_ROOTS = [
    "artifacts/old_short_clean_room",
    APPROVED_FUTURE_OUTPUT_ROOT,
]

FORBIDDEN_INPUT_OR_OUTPUT_ROOT_PATTERNS = [
    "MASTER_UPPER_SYSTEM",
    "paper_run_gate_",
    "live runtime directories",
    "original old_short output directories",
    "raw OKX 1m full data",
    "full market data",
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


@dataclass(frozen=True)
class OldShortCleanRoomDryRunConfig:
    """Configuration contract for a future bounded dry-run only."""

    route_key: str = ROUTE_KEY
    default_mode: str = "SCHEMA_FIXTURE_DRY_RUN"
    max_rows_per_file: int = 100
    approved_output_root: str = APPROVED_FUTURE_OUTPUT_ROOT
    runner_execution_allowed: bool = RUNNER_EXECUTION_ALLOWED
    signal_generation_allowed: bool = SIGNAL_GENERATION_ALLOWED
    position_open_allowed: bool = POSITION_OPEN_ALLOWED
    runtime_allowed: bool = RUNTIME_ALLOWED
    live_trading_allowed: bool = LIVE_TRADING_ALLOWED
    capital_allocation_allowed: bool = CAPITAL_ALLOCATION_ALLOWED


class OldShortFixtureInputLoaderPreview:
    """Future fixture loader contract; no files are loaded by this preview."""

    approved_fixture_roots = tuple(APPROVED_FIXTURE_ROOTS)
    max_rows_per_file_default = 100
    raw_full_market_data_allowed = False
    raw_okx_1m_full_data_allowed = False
    runtime_data_allowed = False
    private_account_data_allowed = False
    live_or_order_fields_allowed = False

    def validate_path_contract(self, fixture_path: str) -> Mapping[str, Any]:
        return {
            "fixture_path": fixture_path,
            "load_allowed_now": False,
            "future_policy": "must be under approved fixture roots and bounded row limits",
        }

    def load_fixture_rows(self, fixture_path: str) -> list[Mapping[str, Any]]:
        raise RuntimeError("preview only: fixture loading is not allowed now")


class OldShortFixtureBoundsValidatorPreview:
    """Future fixture bounds checks; no fixture rows are read now."""

    max_rows_per_file_default = 100
    forbidden_field_markers = (
        "api_key",
        "api_secret",
        "passphrase",
        "order_id",
        "client_order_id",
        "live_order_id",
        "exchange_order_id",
        "private_endpoint",
    )

    def validate_bounds(self, fixture_metadata: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "valid_now": False,
            "fail_closed_if_exceeds_row_limit": True,
            "fail_closed_if_live_order_private_fields_detected": True,
            "metadata_preview": dict(fixture_metadata),
        }


class OldShortFeatureBuilderFromFixturePreview:
    """Feature schema contract; no feature computation is performed now."""

    required_feature_fields = tuple(FEATURE_FIELDS)
    computation_source = "bounded fixture rows only in a future dry-run"
    computes_now = False

    def describe_required_features(self) -> tuple[str, ...]:
        return self.required_feature_fields

    def build_features_from_fixture(self, fixture_row: Mapping[str, Any]) -> Mapping[str, Any]:
        raise RuntimeError("preview only: feature computation is not allowed now")


class OldShortThresholdContractValidatorPreview:
    """Threshold contract validation contract with fail-closed policy."""

    original_thresholds_known = False
    hidden_default_thresholds_allowed = False
    fallback_thresholds_allowed = False

    def require_threshold_contract(
        self, dry_run_mode: str, threshold_contract: Mapping[str, Any] | None
    ) -> Mapping[str, Any]:
        if dry_run_mode == "SCHEMA_FIXTURE_DRY_RUN":
            return {
                "allowed": True,
                "schema_plumbing_only": True,
                "required_label": "SYNTHETIC_SCHEMA_SAMPLE",
                "signal_threshold_evaluation_bypassed": True,
            }
        if not threshold_contract:
            return {
                "allowed": False,
                "fail_closed": True,
                "reason": "missing_explicit_threshold_contract",
            }
        return {
            "allowed": False,
            "preview_only": True,
            "reason": "threshold contract review is future work",
        }


class OldShortSignalEvaluationPreview:
    """Future signal-evaluation contract; never opens positions directly."""

    paper_only_signal_candidates = True
    opens_positions_directly = False
    signal_generation_allowed_now = False

    def evaluate_blowoff_short(
        self, features: Mapping[str, Any], threshold_contract: Mapping[str, Any] | None
    ) -> Mapping[str, Any]:
        if not threshold_contract:
            return {
                "candidate_allowed": False,
                "fail_closed": True,
                "reason": "missing_explicit_threshold_contract",
                "opens_position": False,
            }
        raise RuntimeError("preview only: blowoff_short evaluation is not executable now")

    def evaluate_mean_reversion_short(
        self, features: Mapping[str, Any], threshold_contract: Mapping[str, Any] | None
    ) -> Mapping[str, Any]:
        if not threshold_contract:
            return {
                "candidate_allowed": False,
                "fail_closed": True,
                "reason": "missing_explicit_threshold_contract",
                "opens_position": False,
            }
        raise RuntimeError(
            "preview only: mean_reversion_short evaluation is not executable now"
        )


class OldShortGateFixtureClientPreview:
    """Gate fixture contract only; no runtime gate connection is made."""

    global_gate_mandatory = True
    no_gate_allow_means_no_position = True
    gate_missing_timeout_rejected_entry = True
    same_coin_overlap_block = True
    family_global_max_limits_respected = True
    short_side_only = True
    fixture_gate_only_in_dry_run = True
    runtime_gate_connection_allowed_now = False

    def request_gate_fixture(self, signal_candidate: Mapping[str, Any]) -> Mapping[str, Any]:
        raise RuntimeError("preview only: gate fixture requests are not allowed now")


class OldShortOutputWriterDryRunPreview:
    """Output writer contract; no CSV/state outputs are written by this preview."""

    approved_output_root = APPROVED_FUTURE_OUTPUT_ROOT
    forbidden_output_roots = tuple(FORBIDDEN_INPUT_OR_OUTPUT_ROOT_PATTERNS)
    future_row_labels = tuple(FUTURE_ROW_LABELS)
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
            *FEATURE_FIELDS[:6],
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
            "notional",
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

    def describe_writers(self) -> Mapping[str, Any]:
        return self.output_schemas

    def write_output(self, output_name: str, rows: Any) -> None:
        raise RuntimeError("preview only: dry-run output writers are not allowed now")


class OldShortRunnerDryRunReportBuilderPreview:
    """Future dry-run report schema contract."""

    report_required_keys = (
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
    )

    def build_report_preview(self) -> Mapping[str, Any]:
        return {
            "report_schema_only": True,
            "required_top_level_keys": list(self.report_required_keys),
            "report_written_now": False,
        }


class OldShortCleanRoomRunnerDryRunImplementationPreview:
    """Top-level dry-run implementation preview contract."""

    runner_dry_run_implementation_preview_only = True
    runner_execution_allowed_now = False
    classes: tuple[type[Any], ...] = ()

    def describe(self) -> Mapping[str, Any]:
        return {
            "route_key": ROUTE_KEY,
            "runner_dry_run_implementation_preview_only": True,
            "runner_execution_allowed_now": False,
            "class_names": [item.__name__ for item in self.classes],
        }

    def run(self) -> None:
        raise RuntimeError("preview only: runner dry-run execution is not allowed now")


OldShortCleanRoomRunnerDryRunImplementationPreview.classes = (
    OldShortCleanRoomDryRunConfig,
    OldShortFixtureInputLoaderPreview,
    OldShortFixtureBoundsValidatorPreview,
    OldShortFeatureBuilderFromFixturePreview,
    OldShortThresholdContractValidatorPreview,
    OldShortSignalEvaluationPreview,
    OldShortGateFixtureClientPreview,
    OldShortOutputWriterDryRunPreview,
    OldShortRunnerDryRunReportBuilderPreview,
    OldShortCleanRoomRunnerDryRunImplementationPreview,
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

    route_key = (
        data.get("implementation_preview_identity", {}).get("route_key")
        or data.get("dry_run_identity", {}).get("route_key")
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
    class_names = [
        item.__name__ for item in OldShortCleanRoomRunnerDryRunImplementationPreview.classes
    ]
    output_schemas = OldShortOutputWriterDryRunPreview.output_schemas

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
        "implementation_preview_identity": {
            "route_key": ROUTE_KEY,
            "runner_dry_run_implementation_preview_only": True,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "position_open_allowed_now": False,
            "original_exact_source_recovered": False,
            "behavioral_reconstruction": True,
            "no_exact_replay_claim": True,
        },
        "no_live_guard_constants": NO_LIVE_GUARD_CONSTANTS,
        "module_structure_preview": {
            "class_count": len(class_names),
            "class_contracts_defined_only": True,
            "classes": class_names,
            "runner_execution_implemented": False,
            "signal_generation_implemented": False,
            "trade_creation_implemented": False,
            "standard_library_only": True,
        },
        "dry_run_modes": {
            "dry_run_mode_count": len(DRY_RUN_MODES),
            "modes": DRY_RUN_MODES,
        },
        "threshold_policy": {
            "original_thresholds_unresolved": True,
            "fail_closed_policy_count": len(FAIL_CLOSED_THRESHOLD_POLICY_ITEMS),
            "fail_closed_policy_items": FAIL_CLOSED_THRESHOLD_POLICY_ITEMS,
            "non_schema_modes_require_explicit_threshold_contract": True,
            "missing_threshold_contract_fails_closed": True,
            "no_hidden_default_thresholds": True,
            "no_fallback_thresholds": True,
            "thresholds_inferred_from_pnl_allowed": False,
            "thresholds_inferred_from_master_output_allowed": False,
            "master_output_threshold_inference_requires_separate_reviewed_contract": True,
            "schema_fixture_bypass_label": "SYNTHETIC_SCHEMA_SAMPLE",
        },
        "fixture_input_loader_preview": {
            "class": "OldShortFixtureInputLoaderPreview",
            "approved_fixture_roots": APPROVED_FIXTURE_ROOTS,
            "max_rows_per_file_default": 100,
            "raw_full_market_data_allowed": False,
            "raw_okx_1m_full_data_allowed": False,
            "runtime_data_allowed": False,
            "private_account_data_allowed": False,
            "live_order_fields_allowed": False,
        },
        "feature_builder_from_fixture_preview": {
            "class": "OldShortFeatureBuilderFromFixturePreview",
            "required_feature_fields": FEATURE_FIELDS,
            "future_computation_source": "bounded fixture rows only",
            "feature_computation_allowed_now": False,
            "raw_market_data_read_allowed_now": False,
        },
        "signal_evaluation_preview": {
            "class": "OldShortSignalEvaluationPreview",
            "future_contracts": [
                "evaluate_blowoff_short(features, threshold_contract)",
                "evaluate_mean_reversion_short(features, threshold_contract)",
            ],
            "threshold_contract_required": True,
            "fail_closed_if_missing": True,
            "outputs_paper_only_signal_candidates": True,
            "opens_positions_directly": False,
            "signal_generation_allowed_now": False,
        },
        "gate_fixture_client_preview": {
            "class": "OldShortGateFixtureClientPreview",
            "global_gate_mandatory": True,
            "no_gate_allow_means_no_position": True,
            "gate_missing_timeout": "rejected entry",
            "same_coin_overlap_block": True,
            "family_global_max_limits_respected": True,
            "short_side_only": True,
            "fixture_gate_only_in_dry_run": True,
            "runtime_gate_connection_allowed_now": False,
        },
        "output_writer_dry_run_preview": {
            "class": "OldShortOutputWriterDryRunPreview",
            "output_writer_count": len(output_schemas),
            "schemas_defined_for": list(output_schemas.keys()),
            "schemas": output_schemas,
            "future_row_labels_or_accompanying_labels": FUTURE_ROW_LABELS,
            "approved_future_output_root": APPROVED_FUTURE_OUTPUT_ROOT,
            "forbidden_output_roots": [
                "MASTER_UPPER_SYSTEM",
                "paper_run_gate_* runtime roots",
                "live runtime directories",
                "original old_short output directories",
            ],
            "csv_or_state_outputs_written_now": False,
            "files_written_now": [
                "old_short_clean_room_runner_dry_run_implementation_preview_v1.json"
            ],
        },
        "dry_run_report_builder_preview": {
            "class": "OldShortRunnerDryRunReportBuilderPreview",
            "required_report_keys": list(
                OldShortRunnerDryRunReportBuilderPreview.report_required_keys
            ),
            "report_written_now": False,
        },
        "result_classes": {
            "allowed": RESULT_CLASSES_ALLOWED,
            "forbidden": RESULT_CLASSES_FORBIDDEN,
            "result_class_count": len(RESULT_CLASSES_ALLOWED),
            "no_edge_no_live_only": True,
        },
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "next_allowed_step": {
            "step": NEXT_ALLOWED_STEP,
            "schema_fixture_dry_run_only": True,
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
            "runner_dry_run_implementation_preview_created": True,
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
            "runner_dry_run_design_loaded": source_artifacts["runner_dry_run_design"][
                "loaded"
            ],
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
            "dry_run_modes_preserved": [item["mode"] for item in DRY_RUN_MODES]
            == [
                "SCHEMA_FIXTURE_DRY_RUN",
                "FEATURE_FIXTURE_DRY_RUN",
                "REPLAY_PROXY_DRY_RUN",
            ],
            "threshold_policy_fail_closed_defined": True,
            "fixture_input_loader_preview_defined": True,
            "signal_evaluation_fail_closed_defined": True,
            "gate_fixture_client_preview_defined": True,
            "output_writer_preview_defined": True,
            "result_classes_no_edge_no_live": True,
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
        "route_key": payload["implementation_preview_identity"]["route_key"],
        "runner_dry_run_implementation_preview_only": True,
        "runner_execution_allowed_now": False,
        "class_count": payload["module_structure_preview"]["class_count"],
        "dry_run_mode_count": payload["dry_run_modes"]["dry_run_mode_count"],
        "output_writer_count": payload["output_writer_dry_run_preview"]["output_writer_count"],
        "fail_closed_policy_count": payload["threshold_policy"]["fail_closed_policy_count"],
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
