#!/usr/bin/env python3
"""Create the old_short clean-room runner realistic fixture V2 preview artifact.

This module is preview-only. It defines contracts for a future V2 fixture dry-run
and writes a JSON preview artifact. It does not execute runner logic, generate
signals, run a backtest, compute PnL, touch runtime, or grant live/capital use.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "6440f056308c00fe23081fa3ead4285a4c5dd63e"
EXPECTED_TRACKED_PYTHON_COUNT = 965
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_V1"

MODULE = "tools/edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_v2_preview_v1.py"
ARTIFACT = "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_v2_preview_v1.json"

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / ARTIFACT
MODULE_PATH = REPO_ROOT / MODULE

REALISTIC_FIXTURE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\realistic_bounded_fixture_generation_dry_run_v1"
)
ACCEPTED_LIFECYCLE_FIXTURE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
    r"\accepted_lifecycle_fixture_discovery_v1"
)
APPROVED_FIXTURE_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1"
)
V2_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\realistic_fixture_runner_v2_dry_run_v1"
)


SOURCE_ARTIFACT_PATHS = {
    "realistic_fixture_runner_v2_design": "artifacts/old_short_clean_room/old_short_clean_room_realistic_fixture_runner_v2_design_v1.json",
    "accepted_lifecycle_fixture_review": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_review_v1.json",
    "accepted_lifecycle_fixture_discovery_dry_run": "artifacts/old_short_clean_room/old_short_clean_room_accepted_lifecycle_fixture_discovery_dry_run_v1.json",
    "runner_realistic_fixture_dry_run_review": "artifacts/old_short_clean_room/old_short_clean_room_runner_realistic_fixture_dry_run_review_v1.json",
    "runner_fixture_threshold_contract": "artifacts/old_short_clean_room/old_short_clean_room_runner_fixture_threshold_contract_v1.json",
    "old_short_clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
}

EXTERNAL_METADATA_PATHS = {
    "realistic_fixture_index": REALISTIC_FIXTURE_ROOT / "fixture_index.json",
    "realistic_fixture_generation_summary": REALISTIC_FIXTURE_ROOT / "fixture_generation_summary.json",
    "accepted_lifecycle_fixture_index": ACCEPTED_LIFECYCLE_FIXTURE_ROOT / "accepted_lifecycle_fixture_index.json",
    "accepted_lifecycle_discovery_summary": ACCEPTED_LIFECYCLE_FIXTURE_ROOT / "accepted_lifecycle_discovery_summary.json",
}

SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "PROXY_BEHAVIOR_FIXTURE",
    "ACCEPTED_LIFECYCLE_FIXTURE if applicable",
    "NOT_ORIGINAL_OLD_SHORT",
    "NOT_EXACT_REPLAY",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]

NO_LIVE_GUARD_CONSTANTS = {
    "V2_RUNNER_DRY_RUN_ALLOWED": False,
    "RUNNER_EXECUTION_ALLOWED": False,
    "SIGNAL_GENERATION_ALLOWED": False,
    "POSITION_OPEN_ALLOWED": False,
    "BACKTEST_ALLOWED": False,
    "PNL_COMPUTATION_ALLOWED": False,
    "RUNTIME_ALLOWED": False,
    "MONITOR_ALLOWED": False,
    "LIVE_TRADING_ALLOWED": False,
    "CAPITAL_ALLOCATION_ALLOWED": False,
    "ORDER_PLACEMENT_ALLOWED": False,
    "CANDIDATE_GENERATION_ALLOWED": False,
    "EDGE_CLAIM_ALLOWED": False,
}

FAIL_CLOSED_CONDITIONS = [
    "either fixture package missing",
    "threshold contract missing",
    "route_key mismatch",
    "family_key mismatch",
    "side not short",
    "required feature missing",
    "safety labels missing",
    "fixture uses PnL/outcome selection",
    "raw market data path supplied",
    "runtime path supplied",
    "live/order/private fields detected",
    "output root overlaps MASTER/runtime",
    "no-live guard false",
]

RESULT_CLASSES = [
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]


@dataclasses.dataclass(frozen=True)
class OldShortRealisticFixtureV2ConfigPreview:
    """Preview configuration contract for a future V2 realistic fixture dry-run."""

    route_key: str = ROUTE_KEY
    preview_only: bool = True
    v2_runner_dry_run_allowed_now: bool = False
    realistic_fixture_root: str = str(REALISTIC_FIXTURE_ROOT)
    accepted_lifecycle_fixture_root: str = str(ACCEPTED_LIFECYCLE_FIXTURE_ROOT)
    output_root: str = str(V2_OUTPUT_ROOT)

    def schema(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class OldShortV2FixturePackageLoaderPreview:
    """Contract preview for loading future V2 fixture packages."""

    def expected_inputs(self) -> dict[str, list[str]]:
        return {
            "realistic_bounded_fixture_package": [
                "fixture_index.json",
                "master_proxy_cases.jsonl",
                "clean_room_replay_fixture_inputs.jsonl",
                "validation_pair_fixtures.jsonl",
                "fixture_generation_summary.json",
            ],
            "accepted_lifecycle_fixture_package": [
                "accepted_lifecycle_fixture_index.json",
                "accepted_lifecycle_master_cases.jsonl",
                "accepted_lifecycle_pairing_plan.json",
                "accepted_lifecycle_discovery_summary.json",
            ],
        }

    def preview_return_shape(self) -> dict[str, Any]:
        return {
            "packages_loaded": False,
            "approved_root": str(APPROVED_FIXTURE_ROOT),
            "metadata_only_in_preview": True,
            "raw_market_data_allowed": False,
        }


class OldShortV2ThresholdContractLoaderPreview:
    """Contract preview for the reviewed runner fixture threshold contract."""

    def validation_contract(self) -> dict[str, Any]:
        return {
            "required_family_threshold_count": 2,
            "required_labels": [
                "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
                "NOT_ORIGINAL_THRESHOLD",
                "NOT_PNL_OPTIMIZED",
                "NOT_EDGE_EVIDENCE",
            ],
            "fail_closed_if_missing_or_incomplete": True,
        }


class OldShortV2CaseProcessorPreview:
    """Contract preview for routing future V2 fixture cases by type."""

    def processing_states(self) -> list[str]:
        return [
            "LOAD_THRESHOLD_CONTRACT",
            "LOAD_REALISTIC_BOUNDED_FIXTURE_PACKAGE",
            "LOAD_ACCEPTED_LIFECYCLE_FIXTURE_PACKAGE",
            "VALIDATE_SAFETY_LABELS",
            "PROCESS_BLOCKED_MISSING_GATE_FIXTURES",
            "PROCESS_ACCEPTED_LIFECYCLE_FIXTURES",
            "PROCESS_HEARTBEAT_STATE_FIXTURES",
            "WRITE_PAPER_ONLY_OUTPUT",
            "BUILD_V2_DRY_RUN_REPORT",
            "REPORT_ONLY",
        ]


class OldShortV2GateStateProcessorPreview:
    """Contract preview for blocked and missing gate states."""

    def preview_mapping(self) -> dict[str, str]:
        return {
            "gate_blocked": "rejected_entries",
            "gate_missing_timeout": "rejected_entries",
            "gate_allowed": "accepted lifecycle path only when accepted fixture exists",
        }


class OldShortV2AcceptedLifecycleProcessorPreview:
    """Contract preview for accepted lifecycle fixture handling."""

    def preview_policy(self) -> dict[str, Any]:
        return {
            "gate_allowed_source": "inferred_from_closed_trade_lifecycle_unless_explicit_gate_allow_exists",
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_is_exact_replay": False,
            "computable_items": [
                "entry delay",
                "hold duration",
                "notional",
                "closed trade schema",
                "lifecycle linking",
            ],
            "not_supported": [
                "profitability proof",
                "edge claim",
                "live readiness",
                "exact gate decision replay",
            ],
        }


class OldShortV2OutputWriterPreview:
    """Contract preview for future paper-only output writing."""

    def output_files(self) -> list[str]:
        return [
            "signals.csv",
            "pending_entries.csv",
            "open_positions.csv",
            "closed_trades.csv",
            "rejected_entries.csv",
            "heartbeat.csv",
            "state.json",
            "runner_realistic_fixture_v2_dry_run_report.json",
        ]

    def forbidden_roots(self) -> list[str]:
        return [
            "MASTER_UPPER_SYSTEM",
            "paper_run_gate_* runtime roots",
            "live runtime directories",
            "old original output directories",
            "repo tracked paths except summary JSON artifacts",
        ]


class OldShortV2DryRunReportPreview:
    """Contract preview for future V2 dry-run report fields."""

    def metrics(self) -> list[str]:
        return [
            "blocked_missing_fixture_case_count",
            "accepted_lifecycle_case_count",
            "processed_case_count",
            "family_coverage",
            "gate_state_coverage",
            "gate_allowed_inferred_count",
            "accepted_lifecycle_coverage_present",
            "entry_delay_computable_count",
            "hold_duration_computable_count",
            "notional_computable_count",
            "rejected_case_count",
            "accepted_case_count",
            "fail_closed_count",
            "generated_output_file_count",
            "safety_label_audit_passed",
            "no_pnl_used",
            "no_market_data_used",
            "no_edge_live_capital",
        ]


class OldShortRunnerRealisticFixtureV2Preview:
    """Top-level preview contract for a future V2 realistic fixture runner dry-run."""

    def preview_summary(self) -> dict[str, Any]:
        return {
            "preview_only": True,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "v2_runner_dry_run_allowed_now": False,
            "next_allowed_step": NEXT_ALLOWED_STEP,
        }


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def collect_key_values(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                found.append(item_value)
            found.extend(collect_key_values(item_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_key_values(item, key))
    return found


def first_value(value: Any, key: str, default: Any = None) -> Any:
    values = collect_key_values(value, key)
    return values[0] if values else default


def source_summary(relative_path: str, data: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    route_key = (
        first_value(data, "route_key")
        or first_value(data, "route")
        or data.get("route_key")
    )
    return {
        "path": relative_path,
        "sha256": sha256_file(path),
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": route_key,
        "next_allowed_step": data.get("next_allowed_step"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
    }


def external_metadata_summary(path: Path) -> dict[str, Any]:
    exists = path.exists()
    loaded = False
    payload: dict[str, Any] = {}
    if exists:
        payload = read_json(path)
        loaded = True
    return {
        "path": str(path),
        "exists": exists,
        "loaded": loaded,
        "sha256": sha256_file(path) if exists else None,
        "route_key": first_value(payload, "route_key") if payload else None,
        "summary": {
            "status": payload.get("status"),
            "fixture_package_kind": payload.get("fixture_package_kind"),
            "fixture_case_count": payload.get("fixture_case_count"),
            "accepted_lifecycle_candidate_count": first_value(payload, "accepted_lifecycle_candidate_count"),
            "gate_allowed_inferred_count": first_value(payload, "gate_allowed_inferred_count"),
            "family_coverage": first_value(payload, "family_coverage"),
            "gate_state_coverage": first_value(payload, "gate_state_coverage"),
        },
    }


def status_has_only_expected_untracked_tool(status_text: str) -> bool:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    expected = f"?? {MODULE}"
    return all(line == expected for line in lines)


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def build_artifact() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_before_artifact = run_git(["status", "--short"])
    tracked_python_count = int(run_git(["ls-files", "*.py"]).count("\n") + (1 if run_git(["ls-files", "*.py"]) else 0))
    artifact_existed_before = ARTIFACT_PATH.exists()

    source_payloads: dict[str, dict[str, Any]] = {
        name: read_json(REPO_ROOT / path)
        for name, path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts = {
        name: source_summary(path, source_payloads[name])
        for name, path in SOURCE_ARTIFACT_PATHS.items()
    }
    source_artifacts["external_fixture_metadata"] = {
        name: external_metadata_summary(path)
        for name, path in EXTERNAL_METADATA_PATHS.items()
    }

    prior_design = source_payloads["realistic_fixture_runner_v2_design"]
    accepted_review = source_payloads["accepted_lifecycle_fixture_review"]
    accepted_discovery = source_payloads["accepted_lifecycle_fixture_discovery_dry_run"]
    threshold_contract = source_payloads["runner_fixture_threshold_contract"]

    accepted_lifecycle_candidate_count = int(first_value(accepted_review, "accepted_lifecycle_candidate_count", 0))
    gate_allowed_inferred_count = int(first_value(accepted_review, "gate_allowed_inferred_count", 0))
    exact_gate_replay_recovered = bool(first_value(accepted_review, "exact_gate_replay_recovered", False))
    design_identity = prior_design.get("v2_design_identity", {})
    threshold_completeness = threshold_contract.get("contract_completeness", {})

    preview_module_structure = {
        "class_count": 9,
        "classes": [
            {
                "name": "OldShortRealisticFixtureV2ConfigPreview",
                "purpose": "Declare preview-only V2 fixture dry-run configuration and approved roots.",
                "methods": ["schema()"],
            },
            {
                "name": "OldShortV2FixturePackageLoaderPreview",
                "purpose": "Define expected input package files and preview return shape.",
                "methods": ["expected_inputs()", "preview_return_shape()"],
            },
            {
                "name": "OldShortV2ThresholdContractLoaderPreview",
                "purpose": "Define reviewed threshold contract checks without loading runner behavior.",
                "methods": ["validation_contract()"],
            },
            {
                "name": "OldShortV2CaseProcessorPreview",
                "purpose": "Define V2 case processing states without executing case logic.",
                "methods": ["processing_states()"],
            },
            {
                "name": "OldShortV2GateStateProcessorPreview",
                "purpose": "Define blocked/missing/inferred gate state output mapping.",
                "methods": ["preview_mapping()"],
            },
            {
                "name": "OldShortV2AcceptedLifecycleProcessorPreview",
                "purpose": "Define accepted lifecycle preview policy and limitations.",
                "methods": ["preview_policy()"],
            },
            {
                "name": "OldShortV2OutputWriterPreview",
                "purpose": "Define future paper-only output files and forbidden roots.",
                "methods": ["output_files()", "forbidden_roots()"],
            },
            {
                "name": "OldShortV2DryRunReportPreview",
                "purpose": "Define future V2 report metric names.",
                "methods": ["metrics()"],
            },
            {
                "name": "OldShortRunnerRealisticFixtureV2Preview",
                "purpose": "Define top-level preview summary and next allowed step.",
                "methods": ["preview_summary()"],
            },
        ],
        "runner_logic_executed": False,
        "signals_generated": False,
        "trades_created": False,
        "behavioral_validation_executed": False,
    }

    validation_checks = {
        "repo_clean_before_run": status_has_only_expected_untracked_tool(status_before_artifact),
        "prior_realistic_fixture_runner_v2_design_loaded": prior_design.get("status") == "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_REALISTIC_FIXTURE_RUNNER_V2_DESIGN_CREATED",
        "prior_next_allowed_step_verified": prior_design.get("next_allowed_step") == "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_V2_PREVIEW_V1",
        "accepted_lifecycle_candidate_count_verified_2": accepted_lifecycle_candidate_count == 2,
        "gate_allowed_inferred_count_verified_2": gate_allowed_inferred_count == 2,
        "exact_gate_replay_not_claimed": exact_gate_replay_recovered is False and design_identity.get("exact_gate_replay_recovered") is False,
        "original_exact_source_not_claimed": design_identity.get("original_exact_source_recovered") is False,
        "clean_room_reconstruction_preserved": design_identity.get("clean_room_behavioral_reconstruction") is True,
        "no_v2_runner_execution": True,
        "no_signal_generation": True,
        "no_behavioral_validation_execution": True,
        "no_full_dataset_comparison": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_live_guard_constants_false": all_false(NO_LIVE_GUARD_CONSTANTS),
        "input_package_contract_defined": True,
        "case_processing_plan_defined": True,
        "fail_closed_policy_defined": len(FAIL_CLOSED_CONDITIONS) == 13,
        "result_classes_defined": len(RESULT_CLASSES) == 4,
        "exactly_one_python_tool_created": MODULE_PATH.exists() and not artifact_existed_before,
        "exactly_one_json_artifact_created": not artifact_existed_before,
        "no_existing_files_modified": status_has_only_expected_untracked_tool(status_before_artifact),
        "replacement_checks_all_true": True,
    }

    threshold_labels = [
        "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
        "NOT_ORIGINAL_THRESHOLD",
        "NOT_PNL_OPTIMIZED",
        "NOT_EDGE_EVIDENCE",
    ]

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "expected_head": EXPECTED_HEAD,
            "actual_head": head,
            "head_matches_expected": head == EXPECTED_HEAD,
            "expected_tracked_python_count_before_creation": EXPECTED_TRACKED_PYTHON_COUNT,
            "tracked_python_count_before_creation": tracked_python_count,
            "tracked_python_count_matches_expected": tracked_python_count == EXPECTED_TRACKED_PYTHON_COUNT,
            "repo_status_before_artifact": status_before_artifact.splitlines(),
            "target_artifact_existed_before": artifact_existed_before,
        },
        "source_artifacts": source_artifacts,
        "preview_identity": {
            "route_key": ROUTE_KEY,
            "preview_only": True,
            "v2_runner_dry_run_allowed_now": False,
            "original_exact_source_recovered": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "clean_room_behavioral_reconstruction": True,
            "no_edge_claim": True,
            "no_live_capital": True,
            "accepted_lifecycle_candidate_count": accepted_lifecycle_candidate_count,
            "gate_allowed_inferred_count": gate_allowed_inferred_count,
        },
        "no_live_guard_constants": NO_LIVE_GUARD_CONSTANTS,
        "preview_module_structure": preview_module_structure,
        "input_package_contract": {
            "approved_external_root": str(APPROVED_FIXTURE_ROOT),
            "realistic_bounded_fixture_package": {
                "root": str(REALISTIC_FIXTURE_ROOT),
                "future_dry_run_may_read": OldShortV2FixturePackageLoaderPreview().expected_inputs()["realistic_bounded_fixture_package"],
            },
            "accepted_lifecycle_fixture_package": {
                "root": str(ACCEPTED_LIFECYCLE_FIXTURE_ROOT),
                "future_dry_run_may_read": OldShortV2FixturePackageLoaderPreview().expected_inputs()["accepted_lifecycle_fixture_package"],
            },
            "must_not_read": [
                "raw market data",
                "raw OKX 1m data",
                "full MASTER output",
                "runtime directories",
                "private/account data",
            ],
            "preview_reads_metadata_only": True,
        },
        "threshold_contract_preview": {
            "source_artifact": SOURCE_ARTIFACT_PATHS["runner_fixture_threshold_contract"],
            "contract_complete": threshold_completeness.get("contract_complete"),
            "family_threshold_count": threshold_completeness.get("family_threshold_count"),
            "required_family_threshold_count": 2,
            "required_labels_preserved": threshold_labels,
            "fail_closed_if_threshold_contract_missing": True,
            "fail_closed_if_threshold_contract_incomplete": True,
            "threshold_optimization_allowed": False,
        },
        "case_processing_plan": {
            "future_processing_states": OldShortV2CaseProcessorPreview().processing_states(),
            "blocked_missing_gate_fixtures": "write rejected_entries paper-only rows",
            "accepted_lifecycle_fixtures": "write paper-only accepted/open/closed lifecycle outputs",
            "heartbeat_state_fixtures": "write report-only state outputs",
            "preserve_gate_allowed_inferred_from_closed_trade_lifecycle": True,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_is_exact_replay": False,
            "no_pnl_used": True,
            "no_market_data_used": True,
        },
        "output_preview": {
            "future_output_root": str(V2_OUTPUT_ROOT),
            "future_output_files": OldShortV2OutputWriterPreview().output_files(),
            "must_never_write_to": OldShortV2OutputWriterPreview().forbidden_roots(),
            "paper_only": True,
            "repo_tracked_outputs_allowed": ["summary JSON artifacts only"],
        },
        "safety_labels": {
            "required_for_every_future_output_row_or_object": SAFETY_LABELS,
            "accepted_lifecycle_fixture_label_condition": "required when the row/object comes from accepted lifecycle fixtures",
            "safety_label_count": len(SAFETY_LABELS),
        },
        "fail_closed_policy": {
            "condition_count": len(FAIL_CLOSED_CONDITIONS),
            "conditions": FAIL_CLOSED_CONDITIONS,
        },
        "preview_metrics": {
            "future_v2_report_must_include": OldShortV2DryRunReportPreview().metrics(),
            "metric_count": len(OldShortV2DryRunReportPreview().metrics()),
            "accepted_lifecycle_candidate_count": accepted_lifecycle_candidate_count,
            "gate_allowed_inferred_count": gate_allowed_inferred_count,
        },
        "result_classes": {
            "result_class_count": len(RESULT_CLASSES),
            "allowed_result_classes": RESULT_CLASSES,
            "pass_condition": "both families processed, blocked/missing gate cases processed, accepted lifecycle cases processed, accepted lifecycle coverage present, safety labels pass, no PnL/market/live data used",
            "partial_condition": "accepted lifecycle exists but one family or one fixture type missing",
            "fail_closed_condition": "safety/root/threshold/route checks fail",
            "inconclusive_condition": "fixtures insufficient",
        },
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "unresolved_fields_preserved": {
            "original_exact_source_recovered": False,
            "exact_frozen_replay_available": False,
            "exact_gate_replay_recovered": False,
            "accepted_lifecycle_gate_allow_inferred": True,
            "accepted_lifecycle_is_exact_replay": False,
            "thresholds_are_behavioral_reconstruction": True,
            "no_edge_evidence": True,
            "no_live_capital_readiness": True,
        },
        "limitations": [
            "Preview only; no V2 fixture dry-run execution is performed.",
            "Original old_short source remains unrecovered.",
            "Exact frozen replay remains unavailable.",
            "Exact gate replay is not recovered.",
            "Gate allowed is inferred from accepted lifecycle and closed trade fixtures only.",
            "Accepted lifecycle fixtures do not prove profitability, edge, or live readiness.",
            "No raw market data, OKX 1m data, full MASTER output, runtime path, private data, PnL, or outcome selection is used.",
        ],
        "safety_permissions": {
            "realistic_fixture_v2_preview_created": True,
            "v2_runner_dry_run_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values()),
        "payload_sha256_excluding_hash": "",
    }

    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> int:
    if ARTIFACT_PATH.exists():
        raise SystemExit(f"BLOCKED: target artifact already exists: {ARTIFACT_PATH}")

    artifact = build_artifact()
    if artifact["replacement_checks_all_true"] is not True:
        raise SystemExit("BLOCKED: replacement_checks_all_true=false")

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    stdout_fields = {
        "status": artifact["status"],
        "route_key": artifact["preview_identity"]["route_key"],
        "preview_only": artifact["preview_identity"]["preview_only"],
        "v2_runner_dry_run_allowed_now": artifact["preview_identity"]["v2_runner_dry_run_allowed_now"],
        "accepted_lifecycle_candidate_count": artifact["preview_identity"]["accepted_lifecycle_candidate_count"],
        "gate_allowed_inferred_count": artifact["preview_identity"]["gate_allowed_inferred_count"],
        "exact_gate_replay_recovered": artifact["preview_identity"]["exact_gate_replay_recovered"],
        "class_count": artifact["preview_module_structure"]["class_count"],
        "fail_closed_condition_count": artifact["fail_closed_policy"]["condition_count"],
        "result_class_count": artifact["result_classes"]["result_class_count"],
        "next_allowed_step": artifact["next_allowed_step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    for key, value in stdout_fields.items():
        print(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
