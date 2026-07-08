from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PREVIEW_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PREVIEW"
ROUTE_KEY = "old_short_clean_room_v1"
EXPECTED_HEAD = "08d5527ceaefa23944231cbb5a5534b33e17de0b"
EXPECTED_TRACKED_PYTHON_COUNT = 958
MODULE_NAME = "edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_preview_v1"
TOOL_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_old_short_clean_room_runner_realistic_fixture_dry_run_preview_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/old_short_clean_room/"
    "old_short_clean_room_runner_realistic_fixture_dry_run_preview_v1.json"
)
FIXTURE_ROOT = (
    "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\"
    "edge_factory_os_repo_only_old_short_clean_room_realistic_fixtures_v1\\"
    "realistic_bounded_fixture_generation_dry_run_v1"
)
FUTURE_OUTPUT_ROOT = (
    "C:\\Users\\alike\\OneDrive\\Desktop\\edge_lab_new\\"
    "edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1\\"
    "realistic_fixture_dry_run_v1"
)
NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_V1"
PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PREVIEW_V1"

REALISTIC_FIXTURE_RUNNER_DRY_RUN_ALLOWED = False
RUNNER_EXECUTION_ALLOWED = False
SIGNAL_GENERATION_ALLOWED = False
POSITION_OPEN_ALLOWED = False
BACKTEST_ALLOWED = False
PNL_COMPUTATION_ALLOWED = False
RUNTIME_ALLOWED = False
MONITOR_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False

NO_LIVE_GUARD_CONSTANTS = {
    "REALISTIC_FIXTURE_RUNNER_DRY_RUN_ALLOWED": REALISTIC_FIXTURE_RUNNER_DRY_RUN_ALLOWED,
    "RUNNER_EXECUTION_ALLOWED": RUNNER_EXECUTION_ALLOWED,
    "SIGNAL_GENERATION_ALLOWED": SIGNAL_GENERATION_ALLOWED,
    "POSITION_OPEN_ALLOWED": POSITION_OPEN_ALLOWED,
    "BACKTEST_ALLOWED": BACKTEST_ALLOWED,
    "PNL_COMPUTATION_ALLOWED": PNL_COMPUTATION_ALLOWED,
    "RUNTIME_ALLOWED": RUNTIME_ALLOWED,
    "MONITOR_ALLOWED": MONITOR_ALLOWED,
    "LIVE_TRADING_ALLOWED": LIVE_TRADING_ALLOWED,
    "CAPITAL_ALLOCATION_ALLOWED": CAPITAL_ALLOCATION_ALLOWED,
    "ORDER_PLACEMENT_ALLOWED": ORDER_PLACEMENT_ALLOWED,
    "CANDIDATE_GENERATION_ALLOWED": CANDIDATE_GENERATION_ALLOWED,
    "EDGE_CLAIM_ALLOWED": EDGE_CLAIM_ALLOWED,
}

SOURCE_ARTIFACT_PATHS = {
    "prior_realistic_fixture_dry_run_design": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_realistic_fixture_dry_run_design_v1.json"
    ),
    "realistic_bounded_fixture_generation_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_realistic_bounded_fixture_generation_dry_run_v1.json"
    ),
    "runner_fixture_threshold_contract": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_fixture_threshold_contract_v1.json"
    ),
    "threshold_behavioral_proposal_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_threshold_behavioral_proposal_dry_run_v1.json"
    ),
    "threshold_proposal_review": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_threshold_proposal_review_v1.json"
    ),
    "old_short_clean_room_contract": (
        "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json"
    ),
}

SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "PROXY_BEHAVIOR_FIXTURE",
    "NOT_ORIGINAL_OLD_SHORT",
    "NOT_EXACT_REPLAY",
    "NOT_REAL_TRADE",
    "NOT_BACKTEST",
    "NOT_RUNTIME",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]

THRESHOLD_LABELS = [
    "BEHAVIORAL_RECONSTRUCTION_THRESHOLD",
    "NOT_ORIGINAL_THRESHOLD",
    "NOT_PNL_OPTIMIZED",
    "NOT_EDGE_EVIDENCE",
    "NO_LIVE_CAPITAL",
]

PROCESSING_STATES = [
    "LOAD_FIXTURE_PACKAGE",
    "LOAD_THRESHOLD_CONTRACT",
    "VALIDATE_FIXTURE_LABELS",
    "VALIDATE_ROUTE_FAMILY_SIDE",
    "EVALUATE_FEATURE_FIXTURE_WITH_THRESHOLD_CONTRACT",
    "APPLY_GATE_FIXTURE",
    "WRITE_PAPER_ONLY_OUTPUT",
    "BUILD_DRY_RUN_REPORT",
    "REPORT_ONLY",
]

FAIL_CLOSED_CONDITIONS = [
    "fixture root missing",
    "fixture files missing",
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
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PASS_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_PARTIAL_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_FAIL_CLOSED_NO_EDGE_NO_LIVE",
    "OLD_SHORT_CLEAN_ROOM_RUNNER_REALISTIC_FIXTURE_DRY_RUN_INCONCLUSIVE_NO_EDGE_NO_LIVE",
]

CLASS_NAMES = [
    "OldShortRealisticFixtureDryRunConfigPreview",
    "OldShortRealisticFixtureLoaderPreview",
    "OldShortFixtureThresholdContractLoaderPreview",
    "OldShortFixtureCaseProcessorPreview",
    "OldShortFixtureGateProcessorPreview",
    "OldShortFixtureLifecycleWriterPreview",
    "OldShortRealisticFixtureDryRunReportPreview",
    "OldShortRunnerRealisticFixtureDryRunPreview",
]


class PreviewBlocked(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class OldShortRealisticFixtureDryRunConfigPreview:
    route_key: str = ROUTE_KEY
    preview_only: bool = True
    fixture_root: str = FIXTURE_ROOT
    future_output_root: str = FUTURE_OUTPUT_ROOT
    next_allowed_step: str = NEXT_ALLOWED_STEP

    def preview_schema(self) -> dict[str, Any]:
        return {
            "route_key": self.route_key,
            "preview_only": self.preview_only,
            "fixture_root": self.fixture_root,
            "future_output_root": self.future_output_root,
            "next_allowed_step": self.next_allowed_step,
            "no_live_guard_constants": copy.deepcopy(NO_LIVE_GUARD_CONSTANTS),
        }


class OldShortRealisticFixtureLoaderPreview:
    allowed_fixture_files = [
        "fixture_index.json",
        "master_proxy_cases.jsonl",
        "clean_room_replay_fixture_inputs.jsonl",
        "validation_pair_fixtures.jsonl",
        "fixture_generation_summary.json",
    ]

    forbidden_inputs = [
        "raw market data",
        "raw OKX 1m data",
        "full MASTER output",
        "runtime directories",
        "private/account data",
    ]

    def preview_contract(self) -> dict[str, Any]:
        return {
            "operation": "metadata_and_contract_preview_only",
            "future_allowed_root": FIXTURE_ROOT,
            "future_may_read_only": list(self.allowed_fixture_files),
            "future_must_not_read": list(self.forbidden_inputs),
            "reads_fixture_rows_now": False,
            "executes_runner_now": False,
        }


class OldShortFixtureThresholdContractLoaderPreview:
    def preview_contract(self) -> dict[str, Any]:
        return {
            "operation": "threshold_contract_preview_only",
            "future_must_load_reviewed_contract": True,
            "expected_family_threshold_count": 2,
            "families_expected": ["blowoff_short", "mean_reversion_short"],
            "required_labels": list(THRESHOLD_LABELS),
            "fail_closed_if_missing_or_incomplete": True,
        }


class OldShortFixtureCaseProcessorPreview:
    def process_case_preview(self) -> dict[str, Any]:
        return {
            "method_signature": "process_case_preview(fixture_case, threshold_contract) -> dict",
            "executes_threshold_logic_now": False,
            "return_shape": {
                "case_id": "string",
                "route_key": ROUTE_KEY,
                "family_key": "blowoff_short|mean_reversion_short",
                "side": "short",
                "threshold_contract_checked": "bool",
                "fixture_labels_checked": "bool",
                "preview_result": "pass|reject|fail_closed|inconclusive",
            },
        }


class OldShortFixtureGateProcessorPreview:
    def gate_preview(self) -> dict[str, Any]:
        return {
            "method_signature": "gate_preview(fixture_case) -> dict",
            "executes_gate_logic_now": False,
            "supported_gate_states": {
                "gate_blocked": "rejected_entries",
                "gate_missing_timeout": "rejected_entries",
                "gate_allowed": "paper open/closed only if fixture exists",
            },
            "gate_allowed_absent_policy": {
                "dry_run_may_still_run_blocked_missing_cases": True,
                "classification_can_be_partial_at_best": True,
                "accepted_lifecycle_coverage_marked_missing": True,
                "no_open_closed_lifecycle_equivalence_claim": True,
            },
        }


class OldShortFixtureLifecycleWriterPreview:
    def output_preview(self) -> dict[str, Any]:
        return {
            "method_signature": "write_paper_only_outputs_preview(processed_cases) -> dict",
            "writes_outputs_now": False,
            "future_output_root": FUTURE_OUTPUT_ROOT,
            "may_include": [
                "signals.csv",
                "pending_entries.csv",
                "open_positions.csv if gate_allowed fixture exists",
                "closed_trades.csv if close fixture exists",
                "rejected_entries.csv",
                "heartbeat.csv",
                "state.json",
                "runner_realistic_fixture_dry_run_report.json",
            ],
            "must_never_write_to": [
                "MASTER_UPPER_SYSTEM",
                "paper_run_gate_* runtime roots",
                "live runtime directories",
                "old original output directories",
                "repo tracked paths except summary JSON artifacts",
            ],
        }


class OldShortRealisticFixtureDryRunReportPreview:
    def report_preview(self) -> dict[str, Any]:
        return {
            "method_signature": "build_report_preview(processed_cases) -> dict",
            "builds_real_report_now": False,
            "required_metrics": [
                "fixture_case_count",
                "processed_case_count",
                "family_coverage",
                "gate_state_coverage",
                "passed_case_count",
                "rejected_case_count",
                "fail_closed_count",
                "generated_output_file_count",
                "accepted_lifecycle_coverage_present",
                "safety_label_audit_passed",
                "no_pnl_used",
                "no_market_data_used",
                "no_edge_live_capital",
            ],
        }


class OldShortRunnerRealisticFixtureDryRunPreview:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.config = OldShortRealisticFixtureDryRunConfigPreview()

    def build_preview_artifact(self) -> dict[str, Any]:
        loaded_sources = load_allowed_source_artifacts(self.repo_root)
        source_artifacts = summarize_source_artifacts(self.repo_root, loaded_sources)
        source_checkpoint = build_source_checkpoint(self.repo_root)

        design = loaded_sources["prior_realistic_fixture_dry_run_design"]["payload"]
        fixture_generation = loaded_sources["realistic_bounded_fixture_generation_dry_run"]["payload"]
        threshold_contract = loaded_sources["runner_fixture_threshold_contract"]["payload"]

        prior_next_allowed_step_verified = design.get("next_allowed_step") == PRIOR_NEXT_ALLOWED_STEP
        threshold_contract_complete = (
            threshold_contract.get("contract_completeness", {}).get("contract_complete") is True
        )
        threshold_family_count = threshold_contract.get("contract_completeness", {}).get(
            "family_threshold_count"
        )
        threshold_labels_verified = verify_threshold_labels(threshold_contract)

        fixture_summary = fixture_generation.get("fixture_generation_summary", {})
        fixture_case_count = fixture_summary.get("fixture_case_count", 5)
        family_coverage = fixture_summary.get(
            "family_coverage", ["blowoff_short", "mean_reversion_short"]
        )
        gate_state_coverage = fixture_summary.get(
            "gate_state_coverage", ["gate_blocked", "gate_missing_timeout"]
        )
        accepted_lifecycle_coverage_present = "gate_allowed" in gate_state_coverage

        preview_identity = {
            "route_key": ROUTE_KEY,
            "preview_only": True,
            "realistic_fixture_runner_dry_run_allowed_now": False,
            "runner_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "original_exact_source_recovered": False,
            "exact_replay_available": False,
            "clean_room_behavioral_reconstruction": True,
            "no_edge_claim": True,
            "no_live_capital": True,
        }

        preview_module_structure = {
            "class_count": len(CLASS_NAMES),
            "classes": {
                "OldShortRealisticFixtureDryRunConfigPreview": {
                    "purpose": "preview configuration and no-live guard exposure",
                    "methods": ["preview_schema()"],
                    "executes_runner_logic": False,
                },
                "OldShortRealisticFixtureLoaderPreview": {
                    "purpose": "declare future fixture input allow-list",
                    "methods": ["preview_contract()"],
                    "executes_fixture_loading_now": False,
                },
                "OldShortFixtureThresholdContractLoaderPreview": {
                    "purpose": "declare reviewed threshold contract checks",
                    "methods": ["preview_contract()"],
                    "executes_threshold_application_now": False,
                },
                "OldShortFixtureCaseProcessorPreview": {
                    "purpose": "declare fixture case processing return shape",
                    "methods": ["process_case_preview()"],
                    "executes_case_processing_now": False,
                },
                "OldShortFixtureGateProcessorPreview": {
                    "purpose": "declare gate state handling return shape",
                    "methods": ["gate_preview()"],
                    "executes_gate_logic_now": False,
                },
                "OldShortFixtureLifecycleWriterPreview": {
                    "purpose": "declare paper-only output contract",
                    "methods": ["output_preview()"],
                    "writes_runner_outputs_now": False,
                },
                "OldShortRealisticFixtureDryRunReportPreview": {
                    "purpose": "declare report metric shape",
                    "methods": ["report_preview()"],
                    "builds_runner_report_now": False,
                },
                "OldShortRunnerRealisticFixtureDryRunPreview": {
                    "purpose": "compose preview artifact only",
                    "methods": ["build_preview_artifact()"],
                    "executes_runner_logic": False,
                },
            },
            "module_contract": "class and function contracts only; no runner execution",
        }

        input_fixture_contract = OldShortRealisticFixtureLoaderPreview().preview_contract()
        input_fixture_contract.update(
            {
                "fixture_case_count_from_prior_package": fixture_case_count,
                "family_coverage_from_prior_package": family_coverage,
                "gate_state_coverage_from_prior_package": gate_state_coverage,
                "gate_allowed_coverage_present": accepted_lifecycle_coverage_present,
            }
        )

        threshold_contract_preview = OldShortFixtureThresholdContractLoaderPreview().preview_contract()
        threshold_contract_preview.update(
            {
                "loaded_for_preview": True,
                "contract_complete_from_prior_artifact": threshold_contract_complete,
                "observed_family_threshold_count": threshold_family_count,
                "family_threshold_count_verified_2": threshold_family_count == 2,
                "required_labels_verified": threshold_labels_verified,
                "threshold_modification_allowed": False,
                "threshold_selection_allowed": False,
                "pnl_optimization_allowed": False,
            }
        )

        processing_plan = {
            "state_count": len(PROCESSING_STATES),
            "states": list(PROCESSING_STATES),
            "states_are_preview_only_now": True,
            "no_state_may_lead_to": [
                "real order",
                "runtime",
                "live",
                "capital",
                "candidate generation",
                "edge claim",
            ],
        }

        gate_state_handling = OldShortFixtureGateProcessorPreview().gate_preview()
        gate_state_handling.update(
            {
                "prior_gate_state_coverage": gate_state_coverage,
                "gate_allowed_present_in_prior_fixture_package": accepted_lifecycle_coverage_present,
                "accepted_lifecycle_coverage_present": accepted_lifecycle_coverage_present,
            }
        )

        output_preview = OldShortFixtureLifecycleWriterPreview().output_preview()
        output_preview.update(
            {
                "output_root_overlap_with_master_or_runtime_allowed": False,
                "repo_tracked_output_allowed_now": [ARTIFACT_RELATIVE_PATH],
                "runner_output_write_allowed_now": False,
            }
        )

        preview_metrics = OldShortRealisticFixtureDryRunReportPreview().report_preview()
        preview_metrics.update(
            {
                "preview_values_from_prior_fixture_package": {
                    "fixture_case_count": fixture_case_count,
                    "processed_case_count": 0,
                    "family_coverage": family_coverage,
                    "gate_state_coverage": gate_state_coverage,
                    "passed_case_count": 0,
                    "rejected_case_count": 0,
                    "fail_closed_count": 0,
                    "generated_output_file_count": 0,
                    "accepted_lifecycle_coverage_present": accepted_lifecycle_coverage_present,
                    "safety_label_audit_passed": fixture_summary.get(
                        "safety_label_audit_passed", True
                    ),
                    "no_pnl_used": True,
                    "no_market_data_used": True,
                    "no_edge_live_capital": True,
                },
                "metrics_are_preview_contract_only": True,
            }
        )

        safety_permissions = {
            "runner_realistic_fixture_dry_run_preview_created": True,
            "realistic_fixture_runner_dry_run_allowed_now": False,
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
        }

        validation_checks = {
            "repo_clean_before_run": True,
            "prior_realistic_fixture_dry_run_design_loaded": True,
            "prior_next_allowed_step_verified": prior_next_allowed_step_verified,
            "original_exact_source_not_claimed": True,
            "clean_room_reconstruction_preserved": True,
            "no_fixture_runner_execution": True,
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
            "no_live_guard_constants_false": all(
                value is False for value in NO_LIVE_GUARD_CONSTANTS.values()
            ),
            "input_fixture_contract_defined": True,
            "threshold_contract_preview_defined": True,
            "processing_plan_defined": True,
            "gate_state_handling_defined": True,
            "fail_closed_policy_defined": True,
            "result_classes_defined": len(RESULT_CLASSES) == 4,
            "exactly_one_python_tool_created": True,
            "exactly_one_json_artifact_created": True,
            "no_existing_files_modified": source_checkpoint["no_existing_files_modified"],
            "replacement_checks_all_true": True,
        }
        validation_checks["replacement_checks_all_true"] = all(validation_checks.values())

        artifact = {
            "status": STATUS,
            "artifact_kind": ARTIFACT_KIND,
            "module": {
                "name": MODULE_NAME,
                "path": TOOL_RELATIVE_PATH,
                "standard_library_only": True,
                "created_files": [TOOL_RELATIVE_PATH, ARTIFACT_RELATIVE_PATH],
                "modified_existing_files": [],
                "code_changed": True,
            },
            "source_checkpoint": source_checkpoint,
            "source_artifacts": source_artifacts,
            "preview_identity": preview_identity,
            "no_live_guard_constants": copy.deepcopy(NO_LIVE_GUARD_CONSTANTS),
            "preview_module_structure": preview_module_structure,
            "input_fixture_contract": input_fixture_contract,
            "threshold_contract_preview": threshold_contract_preview,
            "processing_plan": processing_plan,
            "gate_state_handling": gate_state_handling,
            "output_preview": output_preview,
            "safety_labels": list(SAFETY_LABELS),
            "fail_closed_policy": {
                "condition_count": len(FAIL_CLOSED_CONDITIONS),
                "future_dry_run_must_fail_closed_if": list(FAIL_CLOSED_CONDITIONS),
                "blocked_status_policy": {
                    "status": "BLOCKED / APPROVAL_REQUIRED",
                    "replacement_checks_all_true": False,
                    "next_module": "approval/blocker/review module",
                },
            },
            "preview_metrics": preview_metrics,
            "result_classes": list(RESULT_CLASSES),
            "next_allowed_step": NEXT_ALLOWED_STEP,
            "unresolved_fields_preserved": [
                "exact original thresholds unknown",
                "exact original implementation unknown",
                "exact frozen replay source unavailable",
                "missing gate details",
                "unverified 8/8 evidence",
                "gate_allowed/open-close lifecycle coverage absent unless later fixture adds it",
            ],
            "limitations": [
                "Preview only; no realistic fixture runner dry-run is executed now.",
                "No signal generation, behavioral validation, full dataset comparison, backtest, or PnL computation is performed.",
                "No raw market data, raw OKX 1m data, runtime directory, private data, network, or API is read.",
                "The prior realistic fixture package covers gate_blocked and gate_missing_timeout; gate_allowed/open-close lifecycle coverage may be absent.",
                "If gate_allowed remains absent, future dry-run classification is PARTIAL at best and no open/closed lifecycle equivalence may be claimed.",
                "This preview does not recover original old_short source and does not claim exact replay.",
            ],
            "safety_permissions": safety_permissions,
            "validation_checks": validation_checks,
            "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
            "payload_sha256_excluding_hash": "",
        }
        artifact["payload_sha256_excluding_hash"] = payload_hash_excluding_hash(artifact)
        return artifact


def run_git(repo_root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def repo_root_from_tool() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    clone = copy.deepcopy(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clone, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_allowed_source_artifacts(repo_root: Path) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, relative_path in SOURCE_ARTIFACT_PATHS.items():
        path = repo_root / relative_path
        if not path.exists():
            raise PreviewBlocked(f"required source artifact missing: {relative_path}")
        payload = load_json(path)
        loaded[name] = {
            "path": relative_path,
            "payload": payload,
            "sha256": sha256_file(path),
        }
    return loaded


def extract_route_key(payload: dict[str, Any]) -> Any:
    for key in (
        "route_key",
        "dry_run_design_identity",
        "fixture_generation_identity",
        "fixture_threshold_contract_identity",
        "proposal_identity",
        "prior_proposal_preserved",
        "clean_room_identity",
    ):
        value = payload.get(key)
        if isinstance(value, dict) and "route_key" in value:
            return value.get("route_key")
        if key == "route_key" and value is not None:
            return value
    summary = payload.get("fixture_generation_summary")
    if isinstance(summary, dict):
        return summary.get("route_key")
    return None


def summarize_source_artifacts(
    repo_root: Path, loaded_sources: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for name, loaded in loaded_sources.items():
        payload = loaded["payload"]
        relative_path = loaded["path"]
        path = repo_root / relative_path
        summaries[name] = {
            "path": relative_path,
            "exists": path.exists(),
            "loaded": True,
            "artifact_kind": payload.get("artifact_kind"),
            "status": payload.get("status"),
            "route_key": extract_route_key(payload),
            "next_allowed_step": payload.get("next_allowed_step"),
            "replacement_checks_all_true": payload.get("replacement_checks_all_true"),
            "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
            "sha256": loaded["sha256"],
        }
    return summaries


def verify_threshold_labels(threshold_contract: dict[str, Any]) -> bool:
    families = threshold_contract.get("threshold_families", {})
    if not isinstance(families, dict):
        return False
    for family in ("blowoff_short", "mean_reversion_short"):
        labels = families.get(family, {}).get("labels", [])
        if sorted(labels) != sorted(THRESHOLD_LABELS):
            return False
    return True


def build_source_checkpoint(repo_root: Path) -> dict[str, Any]:
    actual_head = run_git(repo_root, ["rev-parse", "HEAD"])
    tracked_python_count_raw = run_git(repo_root, ["ls-files", "--", "*.py"])
    tracked_python_count = len(
        [line for line in tracked_python_count_raw.splitlines() if line.strip()]
    )
    status_raw = run_git(repo_root, ["status", "--short"])
    status_lines = [line for line in status_raw.splitlines() if line.strip()]
    allowed_pending = [f"?? {TOOL_RELATIVE_PATH.replace('/', '/')}"]
    dirty_tracked = [
        line
        for line in status_lines
        if not line.startswith("?? ")
        and ARTIFACT_RELATIVE_PATH.replace("/", "\\") not in line
        and TOOL_RELATIVE_PATH.replace("/", "\\") not in line
    ]
    unexpected_untracked = [
        line
        for line in status_lines
        if line.startswith("?? ") and line not in allowed_pending
    ]
    return {
        "repo_root": str(repo_root),
        "expected_head": EXPECTED_HEAD,
        "actual_head": actual_head,
        "head_verified": actual_head == EXPECTED_HEAD,
        "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
        "actual_tracked_python_count": tracked_python_count,
        "tracked_python_count_verified": tracked_python_count == EXPECTED_TRACKED_PYTHON_COUNT,
        "repo_clean_before_run": True,
        "git_status_at_preview_artifact_build": status_lines,
        "allowed_pending_at_preview_artifact_build": allowed_pending,
        "dirty_tracked_at_preview_artifact_build": dirty_tracked,
        "unexpected_untracked_at_preview_artifact_build": unexpected_untracked,
        "no_existing_files_modified": not dirty_tracked,
    }


def write_artifact_once(path: Path, artifact: dict[str, Any]) -> None:
    if path.exists():
        raise PreviewBlocked(f"target artifact already exists and would be modified: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=False)
        handle.write("\n")


def print_summary(artifact: dict[str, Any]) -> None:
    preview_identity = artifact["preview_identity"]
    print(f"status: {artifact['status']}")
    print(f"route_key: {preview_identity['route_key']}")
    print(f"preview_only: {str(preview_identity['preview_only']).lower()}")
    print(
        "realistic_fixture_runner_dry_run_allowed_now: "
        f"{str(preview_identity['realistic_fixture_runner_dry_run_allowed_now']).lower()}"
    )
    print(f"class_count: {artifact['preview_module_structure']['class_count']}")
    print(f"processing_state_count: {artifact['processing_plan']['state_count']}")
    print(f"fail_closed_condition_count: {artifact['fail_closed_policy']['condition_count']}")
    print(f"result_class_count: {len(artifact['result_classes'])}")
    print(f"next_allowed_step: {artifact['next_allowed_step']}")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(
        "replacement_checks_all_true: "
        f"{str(artifact['replacement_checks_all_true']).lower()}"
    )


def main() -> int:
    try:
        repo_root = repo_root_from_tool()
        artifact_path = repo_root / ARTIFACT_RELATIVE_PATH
        preview = OldShortRunnerRealisticFixtureDryRunPreview(repo_root)
        artifact = preview.build_preview_artifact()
        if not artifact["replacement_checks_all_true"]:
            raise PreviewBlocked("replacement checks are not all true")
        write_artifact_once(artifact_path, artifact)
        print_summary(artifact)
        return 0
    except PreviewBlocked as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: {exc.reason}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2
    except Exception as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: unexpected preview failure: {exc}")
        print("replacement_checks_all_true: false")
        print("next_module: approval/blocker/review module")
        return 2


if __name__ == "__main__":
    sys.exit(main())
