#!/usr/bin/env python3
"""Repo-only old_short clean-room validator implementation preview v1.

This module writes an implementation preview artifact only. It does not execute
a validator, compare full datasets, run old_short, compute PnL, run a backtest,
touch runtime, place orders, use network or APIs, generate candidates, claim
edge, or grant runtime/live/capital permission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
SAFE_DIRECTORY = "C:/Users/alike/OneDrive/Desktop/edge_lab_new/edge_factory_os_repo"

MODULE = "edge_factory_os_repo_only_old_short_clean_room_validator_implementation_preview_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_validator_implementation_preview_v1.py"
ARTIFACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_implementation_preview_v1.json"
CONTRACT_REL = "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
RUNNER_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json"
VALIDATOR_PREVIEW_REL = "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json"

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
OLD_SHORT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "old_short"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
VALIDATOR_KEY = "old_short_clean_room_validator_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_DESIGN_V1"

VALIDATOR_EXECUTION_ALLOWED = False
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

NO_LIVE_ORDER_FIELDS = [
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

SIMILARITY_METRIC_NAMES = [
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

RESULT_CLASSES = [
    "CLEAN_ROOM_BEHAVIOR_MATCH_PASS_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_BEHAVIOR_MATCH_PARTIAL_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_BEHAVIOR_MATCH_FAIL_NO_EDGE_NO_LIVE",
    "CLEAN_ROOM_VALIDATION_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]

IMPLEMENTATION_PREVIEW_CLASSES = [
    "OldShortCleanRoomValidatorConfig",
    "OldShortSchemaValidatorPreview",
    "OldShortBehavioralComparatorPreview",
    "OldShortSimilarityMetricPreview",
    "OldShortThresholdPolicyPreview",
    "OldShortValidationReportBuilderPreview",
    "OldShortValidatorImplementationPreview",
]


@dataclass(frozen=True)
class OldShortCleanRoomValidatorConfig:
    """Future dry-run config shape; not used here to execute validation."""

    clean_room_output_dir: str
    master_proxy_output_dir: str
    route_key: str = ROUTE_KEY
    validator_key: str = VALIDATOR_KEY
    validator_execution_allowed: bool = VALIDATOR_EXECUTION_ALLOWED
    backtest_allowed: bool = BACKTEST_ALLOWED
    runtime_allowed: bool = RUNTIME_ALLOWED
    live_trading_allowed: bool = LIVE_TRADING_ALLOWED
    capital_allocation_allowed: bool = CAPITAL_ALLOCATION_ALLOWED
    order_placement_allowed: bool = ORDER_PLACEMENT_ALLOWED
    candidate_generation_allowed: bool = CANDIDATE_GENERATION_ALLOWED
    edge_claim_allowed: bool = EDGE_CLAIM_ALLOWED

    def validate_preview_config(self) -> dict[str, Any]:
        return {
            "route_key_valid": self.route_key == ROUTE_KEY,
            "validator_key_valid": self.validator_key == VALIDATOR_KEY,
            "all_execution_guards_false": not any(
                [
                    self.validator_execution_allowed,
                    self.backtest_allowed,
                    self.runtime_allowed,
                    self.live_trading_allowed,
                    self.capital_allocation_allowed,
                    self.order_placement_allowed,
                    self.candidate_generation_allowed,
                    self.edge_claim_allowed,
                ]
            ),
        }


@dataclass(frozen=True)
class OldShortSchemaValidatorPreview:
    """Schema validation plan holder; no dataset validation is performed."""

    schema_plan: dict[str, Any]

    def planned_files(self) -> list[str]:
        return sorted(self.schema_plan.keys())


@dataclass(frozen=True)
class OldShortBehavioralComparatorPreview:
    """Behavioral comparison hook holder; no behavioral comparison is run."""

    hooks: list[str]

    def hook_count(self) -> int:
        return len(self.hooks)


@dataclass(frozen=True)
class OldShortSimilarityMetricPreview:
    """Similarity metric formula registry; formulas are not evaluated here."""

    formulas: dict[str, str]

    def metric_names(self) -> list[str]:
        return sorted(self.formulas.keys())


@dataclass(frozen=True)
class OldShortThresholdPolicyPreview:
    """Validation threshold policy holder; thresholds are not strategy params."""

    thresholds: dict[str, Any]

    def threshold_count(self) -> int:
        return len(self.thresholds)


@dataclass(frozen=True)
class OldShortValidationReportBuilderPreview:
    """Future report schema holder; no report is built from real validation."""

    result_classes: list[str] = field(default_factory=lambda: list(RESULT_CLASSES))

    def allowed_result_classes(self) -> list[str]:
        return list(self.result_classes)


@dataclass(frozen=True)
class OldShortValidatorImplementationPreview:
    """Preview composition of future validator parts; execution is disabled."""

    config: OldShortCleanRoomValidatorConfig
    schema_validator: OldShortSchemaValidatorPreview
    behavioral_comparator: OldShortBehavioralComparatorPreview
    metric_preview: OldShortSimilarityMetricPreview
    threshold_policy: OldShortThresholdPolicyPreview
    report_builder: OldShortValidationReportBuilderPreview

    def preview_summary(self) -> dict[str, Any]:
        config_checks = self.config.validate_preview_config()
        return {
            "route_key": self.config.route_key,
            "validator_key": self.config.validator_key,
            "validator_execution_allowed_now": self.config.validator_execution_allowed,
            "class_count": len(IMPLEMENTATION_PREVIEW_CLASSES),
            "planned_file_count": len(self.schema_validator.planned_files()),
            "behavioral_hook_count": self.behavioral_comparator.hook_count(),
            "similarity_metric_count": len(self.metric_preview.metric_names()),
            "threshold_count": self.threshold_policy.threshold_count(),
            "result_class_count": len(self.report_builder.allowed_result_classes()),
            "all_execution_guards_false": config_checks["all_execution_guards_false"],
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
        "next_module": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW_BLOCKER_REVIEW",
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


def ensure_prior_artifacts(contract: dict[str, Any], runner: dict[str, Any], validator: dict[str, Any]) -> None:
    if contract.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED":
        fail_closed("CLEAN_ROOM_CONTRACT_STATUS_UNEXPECTED", {"status": contract.get("status")})
    if runner.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED":
        fail_closed("RUNNER_PREVIEW_STATUS_UNEXPECTED", {"status": runner.get("status")})
    if validator.get("status") != "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED":
        fail_closed("VALIDATOR_PREVIEW_STATUS_UNEXPECTED", {"status": validator.get("status")})
    identity = contract.get("clean_room_identity", {})
    runner_identity = runner.get("clean_room_runner_identity", {})
    validator_identity = validator.get("validator_identity", {})
    if identity.get("route_key") != ROUTE_KEY:
        fail_closed("CONTRACT_ROUTE_KEY_MISMATCH", {"route_key": identity.get("route_key")})
    if runner_identity.get("route_key") != ROUTE_KEY:
        fail_closed("RUNNER_ROUTE_KEY_MISMATCH", {"route_key": runner_identity.get("route_key")})
    if validator_identity.get("route_key") != ROUTE_KEY:
        fail_closed("VALIDATOR_ROUTE_KEY_MISMATCH", {"route_key": validator_identity.get("route_key")})
    if validator_identity.get("validator_key") != VALIDATOR_KEY:
        fail_closed(
            "VALIDATOR_KEY_MISMATCH", {"validator_key": validator_identity.get("validator_key")}
        )
    if validator.get("next_allowed_step") != "OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW_V1":
        fail_closed(
            "VALIDATOR_PREVIEW_NEXT_ALLOWED_STEP_UNEXPECTED",
            {"next_allowed_step": validator.get("next_allowed_step")},
        )
    if identity.get("original_exact_source_recovered") is not False:
        fail_closed("CONTRACT_CLAIMS_ORIGINAL_SOURCE_RECOVERED", identity)
    if runner_identity.get("original_exact_source_recovered") is not False:
        fail_closed("RUNNER_CLAIMS_ORIGINAL_SOURCE_RECOVERED", runner_identity)
    if validator_identity.get("exact_original_source_recovered") is not False:
        fail_closed("VALIDATOR_CLAIMS_ORIGINAL_SOURCE_RECOVERED", validator_identity)
    if validator_identity.get("behavioral_validation_only") is not True:
        fail_closed("VALIDATOR_NOT_BEHAVIORAL_VALIDATION_ONLY", validator_identity)


def no_live_guard_constants() -> dict[str, bool]:
    return {
        "VALIDATOR_EXECUTION_ALLOWED": VALIDATOR_EXECUTION_ALLOWED,
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


def build_schema_validator_preview(validator_preview: dict[str, Any]) -> dict[str, Any]:
    plan = validator_preview.get("schema_validation_plan")
    if not isinstance(plan, dict):
        fail_closed("VALIDATOR_PREVIEW_SCHEMA_PLAN_MISSING", {"path": VALIDATOR_PREVIEW_REL})
    preview: dict[str, Any] = {}
    for name in EXPECTED_FILES:
        entry = plan.get(name)
        if not isinstance(entry, dict):
            fail_closed("VALIDATOR_PREVIEW_SCHEMA_FILE_MISSING", {"file": name})
        preview[name] = {
            "required_columns": entry.get("required_columns"),
            "optional_columns": entry.get("optional_columns", []),
            "type_expectations": entry.get("type_checks"),
            "timestamp_expectations": entry.get("timestamp_checks"),
            "family_key_expectations": entry.get("family_key_checks"),
            "side_expectations": entry.get("side_checks"),
            "no_live_order_field_expectations": {
                "forbidden_columns_or_keys": NO_LIVE_ORDER_FIELDS,
                "must_be_absent": True,
            },
            "execution_status": "plan_only_not_run",
        }
    return preview


def build_behavioral_comparator_preview() -> dict[str, Any]:
    hooks = [
        "compare_family_key_old_short",
        "compare_family_blowoff_short_mean_reversion_short",
        "compare_side_short",
        "compare_signal_feature_availability",
        "compare_entry_delay_near_2_minutes",
        "compare_hold_near_120_minutes",
        "compare_notional_near_50_usdt_for_1000_usdt_base_equity",
        "compare_rejected_entries_gate_behavior",
        "compare_no_position_without_global_gate_allow",
        "compare_same_coin_overlap_behavior_if_evidence_supports_it",
    ]
    return {
        "comparison_hooks": hooks,
        "hook_contracts": {
            "family_key": {"expected": "old_short", "metric": "family_key_match_rate"},
            "family": {
                "expected_values": ["blowoff_short", "mean_reversion_short"],
                "metric": "signal_feature_distribution_similarity",
            },
            "side": {"expected": "short", "metric": "side_match_rate"},
            "signal_feature_availability": {
                "required_fields": SIGNAL_FEATURE_FIELDS,
                "metric": "signal_feature_distribution_similarity",
            },
            "entry_delay": {"target": "near 2 minutes", "metric": "entry_delay_median_abs_error_seconds"},
            "hold": {"target": "near 120 minutes", "metric": "hold_minutes_median_abs_error"},
            "notional": {
                "target": "near 50 USDT for 1000 USDT base equity",
                "metric": "notional_median_abs_error",
            },
            "rejected_entries_gate_behavior": {
                "expected_reasons": ["gate_missing", "gate_timeout", "gate_block"],
                "metric": "rejected_entry_reason_overlap",
            },
            "no_position_without_global_gate_allow": {
                "required": True,
                "metric": "gate_behavior_consistency_rate",
            },
            "same_coin_overlap_behavior": {
                "required_if_evidence_supports_it": True,
                "metric": "gate_behavior_consistency_rate",
            },
        },
        "execution_status": "hooks_defined_only_not_run",
    }


def build_similarity_metric_preview() -> dict[str, Any]:
    return {
        "schema_match_rate": {
            "signature": "schema_match_rate(candidate_schema, proxy_schema) -> float",
            "formula": "matched_required_columns / required_columns",
            "computed_now": False,
        },
        "family_key_match_rate": {
            "signature": "family_key_match_rate(candidate_rows, expected='old_short') -> float",
            "formula": "rows_with_family_key_old_short / comparable_rows",
            "computed_now": False,
        },
        "side_match_rate": {
            "signature": "side_match_rate(candidate_rows, expected='short') -> float",
            "formula": "rows_with_side_short / comparable_rows",
            "computed_now": False,
        },
        "entry_delay_median_abs_error_seconds": {
            "signature": "entry_delay_median_abs_error_seconds(candidate_rows, proxy_rows) -> float",
            "formula": "median(abs(candidate_entry_delay_seconds - proxy_entry_delay_seconds))",
            "computed_now": False,
        },
        "hold_minutes_median_abs_error": {
            "signature": "hold_minutes_median_abs_error(candidate_rows, proxy_rows) -> float",
            "formula": "median(abs(candidate_hold_minutes - proxy_hold_minutes))",
            "computed_now": False,
        },
        "notional_median_abs_error": {
            "signature": "notional_median_abs_error(candidate_rows, proxy_rows) -> float",
            "formula": "median(abs(candidate_notional_usdt - proxy_notional_usdt))",
            "computed_now": False,
        },
        "closed_trade_schema_compatibility": {
            "signature": "closed_trade_schema_compatibility(candidate_closed_schema, contract_schema) -> float",
            "formula": "closed_trade_required_fields_present / closed_trade_required_fields",
            "computed_now": False,
        },
        "rejected_entry_reason_overlap": {
            "signature": "rejected_entry_reason_overlap(candidate_reasons, proxy_reasons) -> float",
            "formula": "intersection(candidate_reasons, proxy_reasons) / union(candidate_reasons, proxy_reasons)",
            "computed_now": False,
        },
        "signal_feature_distribution_similarity": {
            "signature": "signal_feature_distribution_similarity(candidate_features, proxy_features) -> float",
            "formula": "bounded distribution similarity over required signal feature fields",
            "computed_now": False,
        },
        "timestamp_alignment_rate": {
            "signature": "timestamp_alignment_rate(candidate_rows, proxy_rows, tolerance_seconds) -> float",
            "formula": "aligned_timestamps_within_tolerance / comparable_timestamps",
            "computed_now": False,
        },
        "coin_overlap_rate": {
            "signature": "coin_overlap_rate(candidate_coins, proxy_coins) -> float",
            "formula": "intersection(candidate_coins, proxy_coins) / proxy_coins",
            "computed_now": False,
        },
        "gate_behavior_consistency_rate": {
            "signature": "gate_behavior_consistency_rate(candidate_gate_events, proxy_gate_events) -> float",
            "formula": "consistent_gate_events / comparable_gate_events",
            "computed_now": False,
        },
    }


def build_threshold_policy_preview(validator_preview: dict[str, Any]) -> dict[str, Any]:
    thresholds = validator_preview.get("suggested_validation_thresholds")
    if not isinstance(thresholds, dict):
        fail_closed("VALIDATOR_PREVIEW_THRESHOLDS_MISSING", {"path": VALIDATOR_PREVIEW_REL})
    required = {
        "schema_match_rate",
        "family_key_match_rate",
        "side_match_rate",
        "median_entry_delay_error_seconds",
        "median_hold_error_minutes",
        "notional_median_error_usdt",
        "no_position_without_gate_allow",
        "no_live_order_fields",
        "closed_trades_schema_compatible",
    }
    missing = sorted(required.difference(thresholds.keys()))
    if missing:
        fail_closed("VALIDATOR_PREVIEW_THRESHOLDS_INCOMPLETE", {"missing": missing})
    return {
        "thresholds": thresholds,
        "threshold_type": "validation_thresholds_not_strategy_parameters",
        "strategy_thresholds_filled": False,
        "exact_original_thresholds_remain_unknown": True,
    }


def build_validator_module_structure_preview() -> dict[str, Any]:
    return {
        "classes": {
            "OldShortCleanRoomValidatorConfig": {
                "role": "future dry-run config shape with execution guards",
                "may_validate": ["route_key", "validator_key", "all guard constants false"],
                "must_not": ["run validator", "read full datasets", "compute PnL"],
            },
            "OldShortSchemaValidatorPreview": {
                "role": "schema validation plan holder",
                "methods": ["planned_files"],
                "execution_status": "no row validation now",
            },
            "OldShortBehavioralComparatorPreview": {
                "role": "behavioral comparison hook holder",
                "methods": ["hook_count"],
                "execution_status": "hooks only",
            },
            "OldShortSimilarityMetricPreview": {
                "role": "metric formula registry",
                "methods": ["metric_names"],
                "execution_status": "formulas only",
            },
            "OldShortThresholdPolicyPreview": {
                "role": "validation threshold policy holder",
                "methods": ["threshold_count"],
                "execution_status": "validation thresholds only",
            },
            "OldShortValidationReportBuilderPreview": {
                "role": "future report schema holder",
                "methods": ["allowed_result_classes"],
                "execution_status": "no report from real validation now",
            },
            "OldShortValidatorImplementationPreview": {
                "role": "preview composition of future validator parts",
                "methods": ["preview_summary"],
                "execution_status": "summary only",
            },
        },
        "class_count": len(IMPLEMENTATION_PREVIEW_CLASSES),
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

    contract = load_json(CONTRACT_PATH, "CLEAN_ROOM_CONTRACT")
    runner = load_json(RUNNER_PREVIEW_PATH, "RUNNER_PREVIEW")
    validator = load_json(VALIDATOR_PREVIEW_PATH, "VALIDATOR_PREVIEW")
    ensure_prior_artifacts(contract, runner, validator)

    guard_constants = no_live_guard_constants()
    similarity_metric_preview = build_similarity_metric_preview()
    threshold_policy_preview = build_threshold_policy_preview(validator)
    schema_validator_preview = build_schema_validator_preview(validator)
    behavioral_comparator_preview = build_behavioral_comparator_preview()
    module_structure_preview = build_validator_module_structure_preview()

    config = OldShortCleanRoomValidatorConfig(
        clean_room_output_dir="future_clean_room_output_directory",
        master_proxy_output_dir="MASTER_UPPER_SYSTEM_proxy_evidence_directory",
    )
    implementation_preview = OldShortValidatorImplementationPreview(
        config=config,
        schema_validator=OldShortSchemaValidatorPreview(schema_validator_preview),
        behavioral_comparator=OldShortBehavioralComparatorPreview(
            behavioral_comparator_preview["comparison_hooks"]
        ),
        metric_preview=OldShortSimilarityMetricPreview(
            {key: value["formula"] for key, value in similarity_metric_preview.items()}
        ),
        threshold_policy=OldShortThresholdPolicyPreview(threshold_policy_preview["thresholds"]),
        report_builder=OldShortValidationReportBuilderPreview(),
    )
    implementation_summary = implementation_preview.preview_summary()

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "clean_room_contract_loaded": True,
        "runner_preview_loaded": True,
        "validator_preview_loaded": True,
        "validator_preview_next_allowed_step_verified": True,
        "original_exact_source_not_claimed": True,
        "behavioral_validation_only_preserved": True,
        "no_validator_execution": True,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_live_guard_constants_false": all_guard_constants_false(),
        "module_structure_preview_defined": module_structure_preview["class_count"] == len(IMPLEMENTATION_PREVIEW_CLASSES),
        "similarity_metrics_defined": set(similarity_metric_preview.keys()) == set(SIMILARITY_METRIC_NAMES),
        "threshold_policy_defined": len(threshold_policy_preview["thresholds"]) == 9,
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
        "validator_implementation_preview_created": True,
        "validator_execution_allowed_now": False,
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

    module_structure_preview["composition_preview_summary"] = implementation_summary

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
                "status": runner.get("status"),
                "artifact_kind": runner.get("artifact_kind"),
                "payload_sha256_excluding_hash": runner.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_preview": {
                "path": VALIDATOR_PREVIEW_REL,
                "status": validator.get("status"),
                "artifact_kind": validator.get("artifact_kind"),
                "payload_sha256_excluding_hash": validator.get("payload_sha256_excluding_hash"),
                "next_allowed_step": validator.get("next_allowed_step"),
                "loaded": True,
            },
            "prior_old_short_artifact_metadata_only": summarize_old_short_metadata_only(),
        },
        "implementation_preview_identity": {
            "route_key": ROUTE_KEY,
            "validator_key": VALIDATOR_KEY,
            "implementation_preview_only": True,
            "validator_execution_allowed_now": False,
            "exact_original_source_recovered": False,
            "behavioral_validation_only": True,
            "exact_frozen_replay_claimed": False,
        },
        "no_live_guard_constants": guard_constants,
        "validator_module_structure_preview": module_structure_preview,
        "schema_validator_preview": schema_validator_preview,
        "behavioral_comparator_preview": behavioral_comparator_preview,
        "similarity_metric_preview": similarity_metric_preview,
        "threshold_policy_preview": threshold_policy_preview,
        "validator_dry_run_contract": {
            "future_inputs": [
                "clean-room output directory",
                "MASTER proxy evidence directory",
                "validation config",
            ],
            "future_output": "behavioral validation JSON",
            "no_runtime": True,
            "no_live": True,
            "no_capital": True,
            "no_candidate": True,
            "no_edge": True,
            "result_classes": RESULT_CLASSES,
            "validator_execution_allowed_now": False,
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
        "route_key": payload["implementation_preview_identity"]["route_key"],
        "validator_key": payload["implementation_preview_identity"]["validator_key"],
        "implementation_preview_only": payload["implementation_preview_identity"]["implementation_preview_only"],
        "validator_execution_allowed_now": payload["implementation_preview_identity"]["validator_execution_allowed_now"],
        "class_count": payload["validator_module_structure_preview"]["class_count"],
        "similarity_metric_count": len(payload["similarity_metric_preview"]),
        "threshold_count": len(payload["threshold_policy_preview"]["thresholds"]),
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
