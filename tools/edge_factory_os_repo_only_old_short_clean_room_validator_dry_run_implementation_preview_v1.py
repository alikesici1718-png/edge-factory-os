#!/usr/bin/env python3
"""Repo-only old_short clean-room validator dry-run implementation preview v1.

This module writes an implementation preview artifact only. It does not execute
a validator, compare full datasets, run old_short, compute PnL, run a backtest,
touch runtime, place orders, use network or APIs, generate candidates, claim
edge, or grant runtime/live/capital permission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
SAFE_DIRECTORY = "C:/Users/alike/OneDrive/Desktop/edge_lab_new/edge_factory_os_repo"

MODULE = "edge_factory_os_repo_only_old_short_clean_room_validator_dry_run_implementation_preview_v1"
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_clean_room_validator_dry_run_implementation_preview_v1.py"
ARTIFACT_REL = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_validator_dry_run_implementation_preview_v1.json"
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

TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
RUNNER_PREVIEW_PATH = REPO_ROOT / RUNNER_PREVIEW_REL
VALIDATOR_PREVIEW_PATH = REPO_ROOT / VALIDATOR_PREVIEW_REL
VALIDATOR_IMPLEMENTATION_PREVIEW_PATH = REPO_ROOT / VALIDATOR_IMPLEMENTATION_PREVIEW_REL
DRY_RUN_DESIGN_PATH = REPO_ROOT / DRY_RUN_DESIGN_REL
OLD_SHORT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "old_short"

MASTER_UPPER_SYSTEM_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"
)
LOGGER_PATH = Path(r"C:\Users\alike\old_short_gate_aware_live_paper_logger.py")

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_IMPLEMENTATION_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_IMPLEMENTATION_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
VALIDATOR_KEY = "old_short_clean_room_validator_v1"
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_EXECUTION_PREVIEW_V1"

VALIDATOR_EXECUTION_ALLOWED = False
FULL_DATASET_COMPARISON_ALLOWED = False
BACKTEST_ALLOWED = False
RUNTIME_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False

EXPECTED_SAMPLE_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

IMPLEMENTATION_PREVIEW_CLASSES = [
    "OldShortDryRunValidatorConfig",
    "OldShortSampleLoaderPreview",
    "OldShortSchemaCheckPreview",
    "OldShortBehavioralCheckPreview",
    "OldShortSimilarityMetricPreview",
    "OldShortDryRunReportPreview",
    "OldShortValidatorDryRunImplementationPreview",
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

DEFAULT_MAX_ROWS_PER_FILE = 100
SAFE_SAMPLE_ROWS_NOW = 3
LOGGER_SAMPLE_BYTES = 200_000


@dataclass(frozen=True)
class OldShortDryRunValidatorConfig:
    """Future bounded dry-run config shape; no validation is executed here."""

    clean_room_sample_dir: str
    master_proxy_sample_dir: str
    max_rows_per_file: int = DEFAULT_MAX_ROWS_PER_FILE
    route_key: str = ROUTE_KEY
    validator_key: str = VALIDATOR_KEY
    validator_execution_allowed: bool = VALIDATOR_EXECUTION_ALLOWED
    full_dataset_comparison_allowed: bool = FULL_DATASET_COMPARISON_ALLOWED
    backtest_allowed: bool = BACKTEST_ALLOWED
    runtime_allowed: bool = RUNTIME_ALLOWED
    live_trading_allowed: bool = LIVE_TRADING_ALLOWED
    capital_allocation_allowed: bool = CAPITAL_ALLOCATION_ALLOWED
    order_placement_allowed: bool = ORDER_PLACEMENT_ALLOWED
    candidate_generation_allowed: bool = CANDIDATE_GENERATION_ALLOWED
    edge_claim_allowed: bool = EDGE_CLAIM_ALLOWED

    def preview_config_checks(self) -> dict[str, bool]:
        guards = [
            self.validator_execution_allowed,
            self.full_dataset_comparison_allowed,
            self.backtest_allowed,
            self.runtime_allowed,
            self.live_trading_allowed,
            self.capital_allocation_allowed,
            self.order_placement_allowed,
            self.candidate_generation_allowed,
            self.edge_claim_allowed,
        ]
        return {
            "route_key_valid": self.route_key == ROUTE_KEY,
            "validator_key_valid": self.validator_key == VALIDATOR_KEY,
            "sample_limit_bounded": 0 < self.max_rows_per_file <= DEFAULT_MAX_ROWS_PER_FILE,
            "all_execution_guards_false": not any(guards),
        }


@dataclass(frozen=True)
class OldShortSampleLoaderPreview:
    """Bounded sample loader contract; does not load future validation datasets."""

    expected_files: list[str]
    max_rows_per_file: int = DEFAULT_MAX_ROWS_PER_FILE
    headers_only_allowed: bool = True
    small_sample_rows_only: bool = True
    full_dataset_reads_allowed_by_default: bool = False
    raw_market_data_reads_allowed: bool = False
    strategy_execution_allowed: bool = False

    def sample_file_type_count(self) -> int:
        return len(self.expected_files)


@dataclass(frozen=True)
class OldShortSchemaCheckPreview:
    """Schema check contract holder; checks are described, not run."""

    schema_checks: dict[str, Any]

    def schema_file_count(self) -> int:
        return len(self.schema_checks)


@dataclass(frozen=True)
class OldShortBehavioralCheckPreview:
    """Behavioral check hook holder; hooks are not executed here."""

    behavioral_hooks: list[str]

    def hook_count(self) -> int:
        return len(self.behavioral_hooks)


@dataclass(frozen=True)
class OldShortSimilarityMetricPreview:
    """Similarity metric formula holder; metrics are not computed here."""

    metric_formulas: dict[str, str]

    def metric_count(self) -> int:
        return len(self.metric_formulas)


@dataclass(frozen=True)
class OldShortDryRunReportPreview:
    """Future report schema holder; no dry-run report is produced here."""

    required_keys: list[str]
    result_classes: list[str] = field(default_factory=lambda: list(DRY_RUN_RESULT_CLASSES))

    def result_class_count(self) -> int:
        return len(self.result_classes)


@dataclass(frozen=True)
class OldShortValidatorDryRunImplementationPreview:
    """Preview composition of the future bounded dry-run validator."""

    config: OldShortDryRunValidatorConfig
    sample_loader: OldShortSampleLoaderPreview
    schema_check: OldShortSchemaCheckPreview
    behavioral_check: OldShortBehavioralCheckPreview
    similarity_metric: OldShortSimilarityMetricPreview
    report_preview: OldShortDryRunReportPreview

    def preview_summary(self) -> dict[str, Any]:
        config_checks = self.config.preview_config_checks()
        return {
            "route_key": self.config.route_key,
            "validator_key": self.config.validator_key,
            "dry_run_implementation_preview_only": True,
            "validator_execution_allowed_now": self.config.validator_execution_allowed,
            "class_count": len(IMPLEMENTATION_PREVIEW_CLASSES),
            "sample_file_type_count": self.sample_loader.sample_file_type_count(),
            "schema_file_count": self.schema_check.schema_file_count(),
            "behavioral_hook_count": self.behavioral_check.hook_count(),
            "similarity_metric_count": self.similarity_metric.metric_count(),
            "result_class_count": self.report_preview.result_class_count(),
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
        "next_module": "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_IMPLEMENTATION_PREVIEW_BLOCKER_REVIEW",
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
    for name in EXPECTED_SAMPLE_FILES:
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
    }


def ensure_prior_artifacts(
    contract: dict[str, Any],
    runner: dict[str, Any],
    validator: dict[str, Any],
    implementation: dict[str, Any],
    dry_run_design: dict[str, Any],
) -> None:
    checks = {
        "contract_status": contract.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_CONTRACT_CREATED",
        "runner_status": runner.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_PREVIEW_CREATED",
        "validator_status": validator.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_PREVIEW_CREATED",
        "implementation_status": implementation.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_IMPLEMENTATION_PREVIEW_CREATED",
        "dry_run_design_status": dry_run_design.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_DESIGN_CREATED",
        "dry_run_design_next_allowed_step": dry_run_design.get("next_allowed_step")
        == "OLD_SHORT_CLEAN_ROOM_VALIDATOR_DRY_RUN_IMPLEMENTATION_PREVIEW_V1",
    }
    if not all(checks.values()):
        fail_closed("PRIOR_ARTIFACT_CHECK_FAILED", checks)

    contract_identity = contract.get("clean_room_identity", {})
    runner_identity = runner.get("clean_room_runner_identity", {})
    validator_identity = validator.get("validator_identity", {})
    implementation_identity = implementation.get("implementation_preview_identity", {})
    dry_run_identity = dry_run_design.get("dry_run_identity", {})
    identity_checks = {
        "contract_route_key": contract_identity.get("route_key") == ROUTE_KEY,
        "runner_route_key": runner_identity.get("route_key") == ROUTE_KEY,
        "validator_route_key": validator_identity.get("route_key") == ROUTE_KEY,
        "implementation_route_key": implementation_identity.get("route_key") == ROUTE_KEY,
        "dry_run_route_key": dry_run_identity.get("route_key") == ROUTE_KEY,
        "validator_key": validator_identity.get("validator_key") == VALIDATOR_KEY,
        "implementation_validator_key": implementation_identity.get("validator_key") == VALIDATOR_KEY,
        "dry_run_validator_key": dry_run_identity.get("validator_key") == VALIDATOR_KEY,
        "contract_not_exact_source": contract_identity.get("original_exact_source_recovered") is False,
        "runner_not_exact_source": runner_identity.get("original_exact_source_recovered") is False,
        "validator_not_exact_source": validator_identity.get("exact_original_source_recovered") is False,
        "implementation_not_exact_source": implementation_identity.get("exact_original_source_recovered") is False,
        "dry_run_not_exact_source": dry_run_identity.get("exact_original_source_recovered") is False,
        "dry_run_behavioral_only": dry_run_identity.get("behavioral_validation_only") is True,
        "dry_run_execution_false": dry_run_identity.get("validator_execution_allowed_now") is False,
        "dry_run_no_exact_replay": dry_run_identity.get("no_exact_replay_claim") is True,
    }
    if not all(identity_checks.values()):
        fail_closed("PRIOR_IDENTITY_CHECK_FAILED", identity_checks)


def no_live_guard_constants() -> dict[str, bool]:
    return {
        "VALIDATOR_EXECUTION_ALLOWED": VALIDATOR_EXECUTION_ALLOWED,
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


def build_module_structure_preview() -> dict[str, Any]:
    return {
        "classes": {
            "OldShortDryRunValidatorConfig": {
                "role": "future bounded dry-run config schema",
                "may_validate": ["sample limits", "route/validator keys", "guard constants"],
                "must_not": ["execute validator", "compare full datasets", "run backtest"],
            },
            "OldShortSampleLoaderPreview": {
                "role": "bounded sample loader contract",
                "must_not": ["read full datasets by default", "read raw market data", "run strategy"],
            },
            "OldShortSchemaCheckPreview": {
                "role": "schema check contract holder",
                "must_not": ["validate full rows now", "mutate source files"],
            },
            "OldShortBehavioralCheckPreview": {
                "role": "behavioral hook registry",
                "must_not": ["compute behavior against full real data now"],
            },
            "OldShortSimilarityMetricPreview": {
                "role": "metric formula registry",
                "must_not": ["evaluate full-data metrics now"],
            },
            "OldShortDryRunReportPreview": {
                "role": "future report schema holder",
                "must_not": ["claim edge", "grant live/capital permission"],
            },
            "OldShortValidatorDryRunImplementationPreview": {
                "role": "preview composition of future dry-run validator",
                "must_not": ["execute validator"],
            },
        },
        "class_count": len(IMPLEMENTATION_PREVIEW_CLASSES),
    }


def build_sample_loader_preview() -> dict[str, Any]:
    return {
        "max_rows_per_file_default": DEFAULT_MAX_ROWS_PER_FILE,
        "headers_only_allowed": True,
        "small_sample_rows_only": True,
        "full_dataset_reads_allowed_by_default": False,
        "raw_market_data_reads_allowed": False,
        "strategy_execution_allowed": False,
        "expected_sample_file_types": EXPECTED_SAMPLE_FILES,
        "sample_file_type_count": len(EXPECTED_SAMPLE_FILES),
    }


def build_schema_check_preview(dry_run_design: dict[str, Any]) -> dict[str, Any]:
    design_schema = dry_run_design.get("schema_checks")
    if not isinstance(design_schema, dict):
        fail_closed("DRY_RUN_DESIGN_SCHEMA_CHECKS_MISSING", {"path": DRY_RUN_DESIGN_REL})
    preview: dict[str, Any] = {}
    for name in EXPECTED_SAMPLE_FILES:
        entry = design_schema.get(name)
        if not isinstance(entry, dict):
            fail_closed("DRY_RUN_DESIGN_SCHEMA_FILE_MISSING", {"file": name})
        preview[name] = {
            "required_columns": entry.get("required_columns"),
            "optional_columns": entry.get("optional_columns", []),
            "type_expectations": entry.get("type_expectations"),
            "timestamp_expectations": entry.get("timestamp_fields"),
            "family_key_expectations": entry.get("family_key_expectation"),
            "side_expectations": entry.get("side_expectation"),
            "no_live_order_private_fields": {
                "forbidden_fields": NO_LIVE_ORDER_PRIVATE_FIELDS,
                "must_be_absent": True,
            },
        }
    return preview


def build_behavioral_check_preview() -> dict[str, Any]:
    return {
        "family_key_old_short": {"expected": "old_short", "hook": "check_family_key_match_rate"},
        "subfamilies": {
            "expected": ["blowoff_short", "mean_reversion_short"],
            "hook": "check_subfamily_presence",
        },
        "side_short": {"expected": "short", "hook": "check_side_match_rate"},
        "signal_feature_presence": {
            "required_fields": SIGNAL_FEATURE_FIELDS,
            "hook": "check_signal_feature_presence_rate",
        },
        "entry_delay_approximately_2_minutes": {
            "target": "approximately 2 minutes",
            "hook": "check_entry_delay_error",
        },
        "hold_approximately_120_minutes": {
            "target": "approximately 120 minutes",
            "hook": "check_hold_minutes_error",
        },
        "notional_near_50_usdt_for_1000_usdt_base_equity": {
            "target": "near 50 USDT for 1000 USDT base equity",
            "hook": "check_notional_abs_error",
        },
        "rejected_entries_gate_behavior": {
            "expected_reasons": ["gate_missing", "gate_timeout", "gate_block"],
            "hook": "check_rejected_reason_overlap",
        },
        "no_position_without_global_gate_allow": {
            "required": True,
            "hook": "check_no_position_without_gate_allow",
        },
        "same_coin_overlap_behavior_if_evidence_supports_it": {
            "required_if_supported": True,
            "hook": "check_same_coin_overlap_behavior",
        },
    }


def build_similarity_metric_preview() -> dict[str, Any]:
    return {
        "schema_match_rate": "matched_required_columns / required_columns",
        "family_key_match_rate": "rows_with_old_short / comparable_rows",
        "side_match_rate": "rows_with_short_side / comparable_rows",
        "entry_delay_median_abs_error_seconds": "median(abs(candidate_entry_delay_seconds - proxy_entry_delay_seconds))",
        "hold_minutes_median_abs_error": "median(abs(candidate_hold_minutes - proxy_hold_minutes))",
        "notional_median_abs_error": "median(abs(candidate_notional_usdt - proxy_notional_usdt))",
        "closed_trade_schema_compatibility": "closed_trade_required_fields_present / closed_trade_required_fields",
        "rejected_entry_reason_overlap": "reason_set_intersection / reason_set_union",
        "signal_feature_distribution_similarity": "bounded distribution similarity over required signal feature fields",
        "timestamp_alignment_rate": "aligned_timestamps_within_tolerance / comparable_timestamps",
        "coin_overlap_rate": "intersection(candidate_coins, proxy_coins) / proxy_coins",
        "gate_behavior_consistency_rate": "consistent_gate_events / comparable_gate_events",
    }


def build_dry_run_report_preview() -> dict[str, Any]:
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
            "no_edge_no_live_permissions",
            "payload_sha256_excluding_hash",
        ],
        "allowed_future_result_classes": DRY_RUN_RESULT_CLASSES,
        "forbidden_future_results": [
            "original source recovered",
            "exact replay",
            "candidate",
            "edge claim",
            "runtime/live/capital permission",
        ],
        "no_edge_no_live_permissions_required": True,
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
    implementation = load_json(VALIDATOR_IMPLEMENTATION_PREVIEW_PATH, "VALIDATOR_IMPLEMENTATION_PREVIEW")
    dry_run_design = load_json(DRY_RUN_DESIGN_PATH, "DRY_RUN_DESIGN")
    ensure_prior_artifacts(contract, runner, validator, implementation, dry_run_design)

    module_structure_preview = build_module_structure_preview()
    sample_loader_preview = build_sample_loader_preview()
    schema_check_preview = build_schema_check_preview(dry_run_design)
    behavioral_check_preview = build_behavioral_check_preview()
    similarity_metric_preview = build_similarity_metric_preview()
    dry_run_report_preview = build_dry_run_report_preview()

    config = OldShortDryRunValidatorConfig(
        clean_room_sample_dir="future_clean_room_bounded_sample_dir",
        master_proxy_sample_dir="future_master_proxy_bounded_sample_dir",
    )
    composed_preview = OldShortValidatorDryRunImplementationPreview(
        config=config,
        sample_loader=OldShortSampleLoaderPreview(EXPECTED_SAMPLE_FILES),
        schema_check=OldShortSchemaCheckPreview(schema_check_preview),
        behavioral_check=OldShortBehavioralCheckPreview(sorted(behavioral_check_preview.keys())),
        similarity_metric=OldShortSimilarityMetricPreview(similarity_metric_preview),
        report_preview=OldShortDryRunReportPreview(
            dry_run_report_preview["required_top_level_keys"]
        ),
    )
    module_structure_preview["composition_preview_summary"] = composed_preview.preview_summary()

    validation_checks: dict[str, bool] = {
        "repo_clean_before_run": bool(preflight["repo_clean_before_run"]),
        "clean_room_contract_loaded": True,
        "runner_preview_loaded": True,
        "validator_preview_loaded": True,
        "validator_implementation_preview_loaded": True,
        "validator_dry_run_design_loaded": True,
        "validator_dry_run_design_next_allowed_step_verified": True,
        "original_exact_source_not_claimed": True,
        "behavioral_validation_only_preserved": True,
        "no_validator_execution": True,
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
        "module_structure_preview_defined": module_structure_preview["class_count"] == 7,
        "sample_loader_preview_defined": sample_loader_preview["sample_file_type_count"] == len(EXPECTED_SAMPLE_FILES),
        "schema_check_preview_defined": len(schema_check_preview) == len(EXPECTED_SAMPLE_FILES),
        "behavioral_check_preview_defined": len(behavioral_check_preview) == 10,
        "similarity_metrics_defined": set(similarity_metric_preview.keys()) == set(SIMILARITY_METRIC_NAMES),
        "dry_run_report_preview_defined": len(dry_run_report_preview["allowed_future_result_classes"]) == 4,
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
        "validator_dry_run_implementation_preview_created": True,
        "validator_execution_allowed_now": False,
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
                "loaded": True,
            },
            "validator_implementation_preview": {
                "path": VALIDATOR_IMPLEMENTATION_PREVIEW_REL,
                "status": implementation.get("status"),
                "artifact_kind": implementation.get("artifact_kind"),
                "payload_sha256_excluding_hash": implementation.get("payload_sha256_excluding_hash"),
                "loaded": True,
            },
            "validator_dry_run_design": {
                "path": DRY_RUN_DESIGN_REL,
                "status": dry_run_design.get("status"),
                "artifact_kind": dry_run_design.get("artifact_kind"),
                "payload_sha256_excluding_hash": dry_run_design.get("payload_sha256_excluding_hash"),
                "next_allowed_step": dry_run_design.get("next_allowed_step"),
                "loaded": True,
            },
            "old_short_artifact_metadata_only": summarize_old_short_metadata_only(),
            "master_upper_system_small_samples": inspect_master_proxy_small_samples(),
            "logger_script_text_only_metadata": inspect_logger_text_only(),
        },
        "implementation_preview_identity": {
            "route_key": ROUTE_KEY,
            "validator_key": VALIDATOR_KEY,
            "dry_run_implementation_preview_only": True,
            "validator_execution_allowed_now": False,
            "exact_original_source_recovered": False,
            "behavioral_validation_only": True,
            "no_exact_replay_claim": True,
        },
        "no_live_guard_constants": no_live_guard_constants(),
        "module_structure_preview": module_structure_preview,
        "sample_loader_preview": sample_loader_preview,
        "schema_check_preview": schema_check_preview,
        "behavioral_check_preview": behavioral_check_preview,
        "similarity_metric_preview": similarity_metric_preview,
        "dry_run_report_preview": dry_run_report_preview,
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
        "dry_run_implementation_preview_only": payload["implementation_preview_identity"][
            "dry_run_implementation_preview_only"
        ],
        "validator_execution_allowed_now": payload["implementation_preview_identity"][
            "validator_execution_allowed_now"
        ],
        "class_count": payload["module_structure_preview"]["class_count"],
        "sample_file_type_count": payload["sample_loader_preview"]["sample_file_type_count"],
        "similarity_metric_count": len(payload["similarity_metric_preview"]),
        "result_class_count": len(payload["dry_run_report_preview"]["allowed_future_result_classes"]),
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
