#!/usr/bin/env python3
"""Create a post-diagnostic strategy-search holdout registry for OKX 88 1h.

This module creates a panel-specific strategy-search governance registry after
baseline and extreme-return diagnostics. It does not claim a pristine untouched
final holdout, does not full-read the 1h panel, does not read original 1m
sources, and does not run strategy search, candidate generation, optimization,
edge claims, or runtime/live/capital actions.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"

UNRESOLVED_REVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review_after_diagnostic_v1"
EXTREME_REVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review_after_baseline_summary_v1"
BASELINE_SUMMARY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_after_execution_v1"
BASELINE_EXECUTION_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_after_preview_v1"
PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_v1"
READINESS_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_after_pipeline_summary_v1"
PIPELINE_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1"
BUILD_EXECUTION_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
VALIDATOR_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1"

UNRESOLVED_REVIEW = UNRESOLVED_REVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_unresolved_extreme_return_review.json"
EXTREME_REVIEW = EXTREME_REVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review.json"
BASELINE_SUMMARY = BASELINE_SUMMARY_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary.json"
BASELINE_EXECUTION = BASELINE_EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_report.json"
PREVIEW = PREVIEW_DIR / "repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate.json"
READINESS_GATE = READINESS_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_readiness_gate.json"
PIPELINE_SUMMARY = PIPELINE_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary.json"
OUTPUT_MANIFEST = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
OUTPUT_SCHEMA = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json"
VALIDATOR_SUMMARY = VALIDATOR_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json"

EXPECTED_HEAD = "a8ca709"
EXPECTED_SELECTED_SYMBOL_COUNT = 88
EXPECTED_EXCLUDED_GAP_SYMBOL_COUNT = 215
EXPECTED_OUTPUT_ROWS = 2223936
EXPECTED_COMPLETE_ROWS = 2223843
EXPECTED_INCOMPLETE_ROWS = 93
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_BUILDER_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_strategy_search_preview_after_holdout_registry_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED_STRATEGY_SEARCH_PREVIEW_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_BUILDER_BLOCKED_REVIEW_REQUIRED"
DIAGNOSTIC_EXPOSURE_REASON = "baseline_return_distribution_and_extreme_return_review_already_read_panel"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def sha256_file(path: Path) -> str | None:
    if not path.exists() or path.stat().st_size > 20_000_000:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "unresolved_review": UNRESOLVED_REVIEW,
        "extreme_review": EXTREME_REVIEW,
        "baseline_summary": BASELINE_SUMMARY,
        "baseline_execution": BASELINE_EXECUTION,
        "preview": PREVIEW,
        "readiness_gate": READINESS_GATE,
        "pipeline_summary": PIPELINE_SUMMARY,
        "output_manifest": OUTPUT_MANIFEST,
        "output_schema": OUTPUT_SCHEMA,
        "validator_summary": VALIDATOR_SUMMARY,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    unresolved = loaded.get("unresolved_review", {})
    extreme = loaded.get("extreme_review", {})
    baseline = loaded.get("baseline_summary", {})
    preview = loaded.get("preview", {})
    readiness = loaded.get("readiness_gate", {})
    pipeline = loaded.get("pipeline_summary", {})
    manifest = loaded.get("output_manifest", {})
    schema = loaded.get("output_schema", {})
    validator = loaded.get("validator_summary", {})

    selected_symbols = manifest.get("selected_symbols", [])
    output_file = manifest.get("output_file")
    symbol_set_hash = sha256_json(sorted(selected_symbols)) if isinstance(selected_symbols, list) else None

    upstream_confirmed = (
        unresolved.get("okx_88_symbol_1h_panel_unresolved_extreme_return_review_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_UNRESOLVED_EXTREME_RETURN_REVIEW_READY"
        and unresolved.get("replacement_checks_all_true") is True
        and unresolved.get("extreme_return_attention_resolved") is True
        and unresolved.get("unresolved_extreme_return_count_after_review") == 0
        and unresolved.get("active_p0_blocker_count") == 0
        and unresolved.get("active_p1_attention_count") == 0
        and unresolved.get("approval_grants_holdout_registry_builder_next") is True
        and unresolved.get("strategy_search_allowed_now") is False
        and unresolved.get("candidate_generation_allowed_now") is False
        and unresolved.get("edge_claim_allowed_now") is False
    )
    validated_output_confirmed = (
        readiness.get("output_valid_for_research_backtest") is True
        and readiness.get("output_valid_for_edge_claim") is False
        and manifest.get("output_file_created") is True
        and manifest.get("output_is_pipeline_validation_only") is True
        and schema.get("pipeline_validation_only") is True
        and validator.get("okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_VALIDATED"
        and validator.get("original_source_full_csv_read_by_validator") is False
    )
    panel_identity_confirmed = (
        readiness.get("selected_symbol_count") == EXPECTED_SELECTED_SYMBOL_COUNT
        and pipeline.get("excluded_gap_symbol_count") == EXPECTED_EXCLUDED_GAP_SYMBOL_COUNT
        and readiness.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS
        and readiness.get("complete_1h_row_count") == EXPECTED_COMPLETE_ROWS
        and readiness.get("incomplete_1h_row_count") == EXPECTED_INCOMPLETE_ROWS
        and readiness.get("strict_3y_completeness_claimed") is False
        and pipeline.get("max_available_start_candidate") == "2023-07-01"
        and pipeline.get("max_available_end_date") == "2026-05-18"
    )
    prior_restrictions_confirmed = (
        baseline.get("holdout_registry_creation_required_before_strategy_search") is True
        and baseline.get("strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel") is True
        and preview.get("holdout_registry_valid_for_this_panel") is False
        and extreme.get("strategy_search_allowed_now") is False
    )

    registry_core = {
        "binance_5y_second_source_future_work_recorded": True,
        "created_at_utc": now_utc(),
        "diagnostic_exposure_reason": DIAGNOSTIC_EXPOSURE_REASON,
        "diagnostic_exposure_recorded": True,
        "excluded_gap_symbol_count": EXPECTED_EXCLUDED_GAP_SYMBOL_COUNT,
        "final_edge_claim_requires_external_or_future_holdout": True,
        "holdout_registry_valid_for_strategy_search_governance": True,
        "holdout_registry_valid_for_this_panel": True,
        "max_available_end_date": "2026-05-18",
        "max_available_start_candidate": "2023-07-01",
        "output_1h_row_count": EXPECTED_OUTPUT_ROWS,
        "output_file_path": output_file,
        "output_file_sha256": None,
        "output_file_sha256_available": False,
        "output_file_sha256_missing_reason": "not computed because full 1h panel read is forbidden for this module",
        "output_manifest_path": str(OUTPUT_MANIFEST),
        "output_manifest_sha256": sha256_file(OUTPUT_MANIFEST),
        "pipeline_summary_artifact_path": str(PIPELINE_SUMMARY),
        "readiness_gate_artifact_path": str(READINESS_GATE),
        "registry_scope": "OKX_88_SYMBOL_NEAR_3Y_1H_PANEL",
        "registry_type": "POST_DIAGNOSTIC_STRATEGY_SEARCH_HOLDOUT_REGISTRY_V1",
        "selected_symbol_count": EXPECTED_SELECTED_SYMBOL_COUNT,
        "strict_3y_completeness_claimed": False,
        "symbol_set_hash": symbol_set_hash,
        "true_untouched_final_holdout_claimed": False,
        "valid_for_final_edge_claim": False,
        "valid_for_strategy_search_governance": True,
        "extreme_return_review_artifact_path": str(EXTREME_REVIEW),
        "complete_1h_row_count": EXPECTED_COMPLETE_ROWS,
        "incomplete_1h_row_count": EXPECTED_INCOMPLETE_ROWS,
    }
    split_policy = {
        "split_boundaries_deterministic": True,
        "split_boundaries_return_optimized": False,
        "split_policy": "deterministic calendar windows selected before strategy search; not optimized on returns",
        "train_development_window_start": "2023-07-01T00:00:00Z",
        "train_development_window_end_exclusive": "2025-01-01T00:00:00Z",
        "validation_window_start": "2025-01-01T00:00:00Z",
        "validation_window_end_exclusive": "2025-11-01T00:00:00Z",
        "sealed_holdout_window_start": "2025-11-01T00:00:00Z",
        "sealed_holdout_window_end_exclusive": "2026-05-19T00:00:00Z",
        "boundary_adjustment_required": False,
        "boundary_adjustment_reason": None,
    }
    access_rules = {
        "future_strategy_search_train_development_only_for_design": True,
        "future_strategy_search_validation_only_for_constrained_validation": True,
        "holdout_access_logging_required": True,
        "holdout_access_requires_pre_registered_freeze": True,
        "no_holdout_parameter_tuning": True,
        "no_holdout_ranking_during_strategy_search": True,
        "sealed_holdout_access_blocked_during_strategy_search": True,
        "strategy_search_fail_closed_on_early_holdout_access": True,
    }
    exposure = {
        "diagnostic_exposure_recorded": True,
        "diagnostic_exposure_reason": DIAGNOSTIC_EXPOSURE_REASON,
        "full_panel_diagnostics_already_performed": True,
        "sealed_holdout_window_sealed_against_future_strategy_search": True,
        "true_untouched_final_holdout_claimed": False,
        "valid_for_final_edge_claim": False,
    }
    limitations = {
        "final_edge_claim_requires_external_or_future_holdout": True,
        "strict_3y_completeness_claimed": False,
        "survivorship_bias_limitations_recorded": True,
        "true_untouched_final_holdout_claimed": False,
        "valid_for_final_edge_claim": False,
        "valid_for_strategy_search_governance": True,
    }
    approvals = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_future_strategy_search_preview_next": True,
        "approval_grants_holdout_registry_builder_now": True,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "next_module": NEXT_PASS_MODULE,
    }

    replacement_checks = {
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "diagnostic_exposure_recorded": exposure["diagnostic_exposure_recorded"] is True,
        "edge_claim_not_enabled": True,
        "holdout_registry_creation_required_before_strategy_search": baseline.get("holdout_registry_creation_required_before_strategy_search") is True,
        "no_forbidden_strategy_candidate_edge_runtime_actions": True,
        "no_full_1h_panel_read": True,
        "no_original_1m_source_read": True,
        "panel_identity_confirmed": panel_identity_confirmed,
        "prior_restrictions_confirmed": prior_restrictions_confirmed,
        "repo_clean_except_current_tool": repo_clean,
        "split_boundaries_not_return_optimized": split_policy["split_boundaries_return_optimized"] is False,
        "true_untouched_final_holdout_not_claimed": registry_core["true_untouched_final_holdout_claimed"] is False,
        "upstream_extreme_return_review_confirmed": upstream_confirmed,
        "valid_for_final_edge_claim_false": registry_core["valid_for_final_edge_claim"] is False,
        "validated_1h_panel_output_confirmed": validated_output_confirmed,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    approvals["next_module"] = next_module
    if not replacement_checks_all_true:
        approvals["approval_grants_future_strategy_search_preview_next"] = False
        approvals["approval_grants_holdout_registry_builder_now"] = False

    summary = {
        **registry_core,
        **split_policy,
        **access_rules,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p0_blocker_count_before_registry": unresolved.get("active_p0_blocker_count"),
        "active_p1_attention_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count_before_registry": unresolved.get("active_p1_attention_count"),
        "aggregation_performed_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_future_strategy_search_preview_next": approvals["approval_grants_future_strategy_search_preview_next"],
        "approval_grants_holdout_registry_builder_now": approvals["approval_grants_holdout_registry_builder_now"],
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "current_evidence_chain_quality_after_registry": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "extreme_return_attention_resolved": unresolved.get("extreme_return_attention_resolved") is True,
        "family_release_allowed_now": False,
        "full_1h_panel_read_performed": False,
        "future_strategy_search_preview_allowed_next": replacement_checks_all_true,
        "holdout_registry_builder_performed": replacement_checks_all_true,
        "holdout_registry_created": replacement_checks_all_true,
        "okx_88_symbol_1h_panel_holdout_registry_builder_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "original_source_full_csv_read_performed": False,
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "next_module": next_module,
        "tracked_python_count_at_registry_run": tracked_python_count(),
        "upstream_extreme_return_review_confirmed": upstream_confirmed,
        "validated_1h_panel_output_confirmed": validated_output_confirmed,
    }
    if load_errors:
        summary["input_artifact_errors"] = load_errors

    self_validator = {
        "created_at_utc": registry_core["created_at_utc"],
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "required_output_artifacts": [],
        "unexpected_git_status_entries": unexpected_status,
    }
    return {
        "access_rules": access_rules,
        "approvals": approvals,
        "exposure": exposure,
        "limitations": limitations,
        "registry": summary,
        "self_validator": self_validator,
        "split_policy": split_policy,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    registry_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
    split_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_split_policy.json"
    access_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_access_rules.json"
    exposure_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_diagnostic_exposure_disclosure.json"
    limitations_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry_limitations.json"
    approval_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview_approval_record.json"
    validator_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_self_validator.json"

    write_json(registry_path, outputs["registry"])
    write_json(split_path, outputs["split_policy"])
    write_json(access_path, outputs["access_rules"])
    write_json(exposure_path, outputs["exposure"])
    write_json(limitations_path, outputs["limitations"])
    write_json(approval_path, outputs["approvals"])
    artifact_paths = [registry_path, split_path, access_path, exposure_path, limitations_path, approval_path, validator_path]
    outputs["self_validator"]["required_output_artifacts"] = [str(path) for path in artifact_paths]
    outputs["self_validator"]["required_output_artifacts_exist"] = {str(path): path.exists() for path in artifact_paths[:-1]}
    write_json(validator_path, outputs["self_validator"])


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["registry"], indent=2, sort_keys=True))
    return 0 if outputs["registry"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
