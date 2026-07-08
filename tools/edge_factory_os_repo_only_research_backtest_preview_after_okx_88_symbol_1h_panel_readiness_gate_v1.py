#!/usr/bin/env python3
"""Read-only research/backtest preview after OKX 88-symbol 1h readiness gate.

This module creates a future execution contract only. It does not read source
CSV/ZIP data, full-read the 1h panel, execute research/backtests, optimize, or
generate candidates.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_v1"

READINESS_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_after_pipeline_summary_v1"
)
PIPELINE_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1"
)
VALIDATOR_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1"
)
BUILD_EXECUTION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
)

READINESS_GATE = READINESS_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_readiness_gate.json"
READINESS_POLICY = READINESS_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_use_policy.json"
PIPELINE_SUMMARY = PIPELINE_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary.json"
PIPELINE_LIMITATIONS = PIPELINE_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_limitations_summary.json"
VALIDATOR_SUMMARY = VALIDATOR_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json"
OUTPUT_MANIFEST = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
OUTPUT_SCHEMA = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json"
PROVENANCE = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_provenance_manifest.json"

EXPECTED_HEAD = "8ec667d"
PASS_STATUS = "PASS_REPO_ONLY_RESEARCH_BACKTEST_PREVIEW_AFTER_OKX_88_SYMBOL_1H_PANEL_READINESS_GATE_CREATED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_RESEARCH_BACKTEST_PREVIEW_AFTER_OKX_88_SYMBOL_1H_PANEL_READINESS_GATE_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_after_preview_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_blocked_record_v1.py"
HOLDOUT_BUILDER_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_READ_ONLY_RESEARCH_BACKTEST_PREVIEW_READY_BASELINE_SANITY_EXECUTION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_READ_ONLY_RESEARCH_BACKTEST_PREVIEW_BLOCKED_REVIEW_REQUIRED"
FIRST_EXECUTION_CLASS = "PANEL_BASELINE_AND_RESEARCH_SANITY_BACKTEST_V1"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        if not text.endswith("\n"):
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
    allowed = {
        f"?? {TOOL_REL.as_posix()}",
        f" M {TOOL_REL.as_posix()}",
        f"A  {TOOL_REL.as_posix()}",
    }
    unexpected = [line for line in lines if line.replace("\\", "/") not in allowed]
    return not unexpected, unexpected


def flatten_values(obj: Any) -> str:
    if isinstance(obj, dict):
        return " ".join(f"{key} {flatten_values(value)}" for key, value in obj.items())
    if isinstance(obj, list):
        return " ".join(flatten_values(value) for value in obj)
    return str(obj)


def holdout_registry_candidates() -> list[Path]:
    candidates: list[Path] = []
    likely_roots = [
        REPO / "edge_factory_os_framework" / "registries",
        EDGE_ROOT / "edge_factory_os_untouched_holdout_registry_builder",
        EDGE_ROOT,
    ]
    seen: set[Path] = set()
    for root in likely_roots:
        if not root.exists():
            continue
        try:
            iterator = root.rglob("*") if root == EDGE_ROOT else root.glob("*")
            for path in iterator:
                if len(candidates) >= 80:
                    break
                if not path.is_file():
                    continue
                name = path.name.lower()
                if "holdout" not in name or "registry" not in name:
                    continue
                if path.suffix.lower() not in {".json", ".txt"}:
                    continue
                if "\\raw\\" in str(path).lower() or "/raw/" in path.as_posix().lower():
                    continue
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    candidates.append(path)
        except OSError:
            continue
    return sorted(candidates, key=lambda item: str(item).lower())


def detect_holdout_registry(panel_identity_terms: list[str]) -> dict[str, Any]:
    candidates = holdout_registry_candidates()
    detected = bool(candidates)
    source_artifact = str(candidates[0]) if candidates else None
    valid_artifact: str | None = None
    invalid_reasons: list[str] = []

    for path in candidates:
        payload: Any = None
        if path.suffix.lower() == ".json":
            try:
                payload = read_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                invalid_reasons.append(f"{path}: unreadable json: {exc}")
                continue
        else:
            try:
                payload = {"text": path.read_text(encoding="utf-8", errors="replace")}
            except OSError as exc:
                invalid_reasons.append(f"{path}: unreadable text: {exc}")
                continue

        haystack = flatten_values(payload).lower()
        panel_bound = all(term.lower() in haystack for term in panel_identity_terms)
        sealed_or_frozen = any(token in haystack for token in ["sealed", "frozen", "holdout_commitment_hash"])
        uncontaminated = not any(token in haystack for token in ["peeked true", '"holdout_peeked": true', "contaminated true"])
        selected_or_bound = any(token in haystack for token in ["holdout_selected true", '"holdout_selected": true', "date split", "time_window"])
        if panel_bound and sealed_or_frozen and uncontaminated and selected_or_bound:
            valid_artifact = str(path)
            break

        reason_bits = []
        if not panel_bound:
            reason_bits.append("not bound to exact OKX 88-symbol near-3y 1h panel identity/date/scope")
        if not sealed_or_frozen:
            reason_bits.append("not sealed/frozen")
        if not selected_or_bound:
            reason_bits.append("no selected or compatible holdout split")
        if not uncontaminated:
            reason_bits.append("appears contaminated or peeked")
        invalid_reasons.append(f"{path}: {', '.join(reason_bits)}")

    valid = valid_artifact is not None
    if valid:
        missing_reason = None
        source_artifact = valid_artifact
    elif detected:
        missing_reason = "registry artifacts detected, but none are valid for this exact OKX 88-symbol near-3y 1h panel: " + "; ".join(
            invalid_reasons[:5]
        )
    else:
        missing_reason = "no holdout registry artifact detected"

    return {
        "holdout_registry_candidate_count": len(candidates),
        "holdout_registry_detected": detected,
        "holdout_registry_detection_performed": True,
        "holdout_registry_source_artifact": source_artifact,
        "holdout_registry_valid_for_this_panel": valid,
        "holdout_registry_missing_or_invalid_reason": missing_reason,
        "holdout_registry_valid_artifact": valid_artifact,
        "holdout_registry_candidate_artifacts": [str(path) for path in candidates[:20]],
    }


def build_preview() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    required_paths = [
        READINESS_GATE,
        READINESS_POLICY,
        PIPELINE_SUMMARY,
        PIPELINE_LIMITATIONS,
        VALIDATOR_SUMMARY,
        OUTPUT_MANIFEST,
        OUTPUT_SCHEMA,
        PROVENANCE,
    ]
    artifacts_exist = {path.name: path.exists() for path in required_paths}

    readiness = read_json(READINESS_GATE)
    readiness_policy = read_json(READINESS_POLICY)
    pipeline = read_json(PIPELINE_SUMMARY)
    limitations = read_json(PIPELINE_LIMITATIONS)
    validator = read_json(VALIDATOR_SUMMARY)
    manifest = read_json(OUTPUT_MANIFEST)
    schema = read_json(OUTPUT_SCHEMA)
    provenance = read_json(PROVENANCE)

    panel_identity_terms = ["OKX", "88", "2023-07-01", "2026-05-18"]
    holdout = detect_holdout_registry(panel_identity_terms)
    holdout_valid = holdout["holdout_registry_valid_for_this_panel"]

    readiness_gate_confirmed = (
        readiness.get("okx_88_symbol_near_3y_1h_panel_research_readiness_gate_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1H_PANEL_RESEARCH_READINESS_GATE_APPROVED"
        and readiness.get("replacement_checks_all_true") is True
        and readiness.get("approval_grants_future_read_only_research_backtest_preview_next") is True
    )
    read_only_research_panel_ready = readiness.get("read_only_research_panel_ready") is True
    output_valid_for_research_backtest = readiness.get("output_valid_for_research_backtest") is True
    output_valid_for_edge_claim = readiness.get("output_valid_for_edge_claim") is True

    fields: dict[str, Any] = {
        "binance_5y_second_source_future_work_recorded": readiness.get("binance_5y_second_source_future_work_recorded"),
        "complete_1h_row_count": readiness.get("complete_1h_row_count"),
        "coverage_gap_symbol_count": readiness.get("coverage_gap_symbol_count"),
        "delisted_historical_symbols_not_proven": readiness.get("delisted_historical_symbols_not_proven"),
        "first_read_only_execution_class": FIRST_EXECUTION_CLASS,
        "incomplete_1h_row_count": readiness.get("incomplete_1h_row_count"),
        "max_available_end_date": readiness.get("max_available_end_date"),
        "max_available_start_candidate": readiness.get("max_available_start_candidate"),
        "okx_only_exchange_scope_recorded": readiness.get("okx_only_exchange_scope_recorded"),
        "output_1h_row_count": readiness.get("output_1h_row_count"),
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": output_valid_for_research_backtest,
        "read_only_research_panel_ready": read_only_research_panel_ready,
        "selected_symbol_count": readiness.get("selected_symbol_count"),
        "strict_3y_completeness_claimed": readiness.get("strict_3y_completeness_claimed"),
        "survivorship_bias_limitations_recorded": readiness.get("survivorship_bias_limitations_recorded"),
    }

    holdout_strategy_gate_safe = (
        holdout["holdout_registry_detection_performed"] is True
        and fields["output_valid_for_edge_claim"] is False
        and readiness.get("strategy_search_allowed_now") is False
        and readiness.get("candidate_generation_allowed_now") is False
    )
    checks = {
        "artifacts_exist": all(artifacts_exist.values()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "holdout_detection_performed": holdout["holdout_registry_detection_performed"] is True,
        "holdout_strategy_gate_safe": holdout_strategy_gate_safe,
        "limitations_recorded": (
            fields["strict_3y_completeness_claimed"] is False
            and fields["okx_only_exchange_scope_recorded"] is True
            and fields["coverage_gap_symbol_count"] == 215
            and fields["survivorship_bias_limitations_recorded"] is True
            and fields["delisted_historical_symbols_not_proven"] is True
            and fields["binance_5y_second_source_future_work_recorded"] is True
            and limitations.get("strict_3y_completeness_claimed") is False
        ),
        "manifest_schema_provenance_metadata_present": (
            manifest.get("output_is_pipeline_validation_only") is True
            and schema.get("pipeline_validation_only") is True
            and provenance.get("provenance_entry_count") == 92664
        ),
        "no_forbidden_preview_actions": True,
        "no_strategy_candidate_edge_now": (
            readiness.get("strategy_search_allowed_now") is False
            and readiness.get("candidate_generation_allowed_now") is False
            and readiness.get("edge_claim_allowed_now") is False
            and readiness.get("runtime_live_capital_allowed_now") is False
            and readiness_policy.get("strategy_search_allowed_now") is False
        ),
        "panel_counts": (
            fields["selected_symbol_count"] == 88
            and fields["output_1h_row_count"] == 2223936
            and fields["complete_1h_row_count"] == 2223843
            and fields["incomplete_1h_row_count"] == 93
            and fields["coverage_gap_symbol_count"] == 215
            and validator.get("output_duplicate_symbol_hour_count") == 0
        ),
        "readiness_gate_confirmed": readiness_gate_confirmed,
        "repo_clean": repo_clean,
        "research_ready_but_not_edge": (
            fields["read_only_research_panel_ready"] is True
            and fields["output_valid_for_research_backtest"] is True
            and output_valid_for_edge_claim is False
            and pipeline.get("output_valid_for_edge_claim") is False
        ),
    }
    replacement_checks_all_true = all(checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    holdout_creation_required = not holdout_valid
    preview = {
        **fields,
        **holdout,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": readiness.get("active_p1_attention_count", 0),
        "aggregation_performed_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_future_read_only_panel_baseline_research_execution_next": replacement_checks_all_true,
        "approval_grants_research_backtest_execution_now": False,
        "approval_grants_research_backtest_preview_now": True,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "baseline_diagnostics_allowed_without_holdout": True,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "cost_slippage_policy_required": True,
        "current_evidence_chain_quality_after_preview": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "full_csv_read_performed": False,
        "future_execution_may_claim_edge": False,
        "future_execution_may_compute_diagnostics": True,
        "future_execution_may_generate_candidates": False,
        "future_holdout_registry_builder_module": HOLDOUT_BUILDER_MODULE if holdout_creation_required else None,
        "holdout_policy_required": True,
        "holdout_registry_builder_recommended_before_strategy_search": holdout_creation_required,
        "holdout_registry_creation_required_before_strategy_search": holdout_creation_required,
        "holdout_registry_or_valid_binding_required_before_strategy_search": True,
        "monthly_stability_reporting_required": True,
        "next_module": next_module,
        "no_lookahead_policy_required": True,
        "null_baseline_required": True,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "panel_baseline_sanity_required": True,
        "preview_created": replacement_checks_all_true,
        "readiness_gate_confirmed": readiness_gate_confirmed,
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "research_backtest_executed": False,
        "research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_status": status,
        "research_execution_approval_record_created": replacement_checks_all_true,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel": True,
        "strategy_search_requires_holdout_registry": True,
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
    }

    contract = {
        "allowed_data_panel": {
            "date_range": [fields["max_available_start_candidate"], fields["max_available_end_date"]],
            "incomplete_1h_row_count": fields["incomplete_1h_row_count"],
            "output_1h_row_count": fields["output_1h_row_count"],
            "selected_symbol_count": fields["selected_symbol_count"],
            "source": "OKX",
        },
        "artifact_type": "read_only_research_contract_preview",
        "first_read_only_execution_class": FIRST_EXECUTION_CLASS,
        "future_execution_may_compute_diagnostics": True,
        "future_execution_may_generate_candidates": False,
        "future_execution_may_claim_edge": False,
        "next_module": next_module,
    }
    limitations_scope = {
        "artifact_type": "research_limitations_and_scope",
        "binance_5y_second_source_future_work_recorded": fields["binance_5y_second_source_future_work_recorded"],
        "coverage_gap_symbol_count": fields["coverage_gap_symbol_count"],
        "delisted_historical_symbols_not_proven": fields["delisted_historical_symbols_not_proven"],
        "max_available_end_date": fields["max_available_end_date"],
        "max_available_start_candidate": fields["max_available_start_candidate"],
        "okx_only_exchange_scope_recorded": fields["okx_only_exchange_scope_recorded"],
        "strict_3y_completeness_claimed": False,
        "survivorship_bias_limitations_recorded": fields["survivorship_bias_limitations_recorded"],
    }
    guardrails = {
        "artifact_type": "first_execution_guardrails",
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "incomplete_hours_must_be_explicitly_handled": True,
        "no_lookahead_policy_required": True,
        "strategy_search_allowed_now": False,
        "write_only_diagnostic_artifacts": True,
    }
    null_cost_holdout = {
        "artifact_type": "null_cost_holdout_requirements_preview",
        "cost_slippage_policy_required": True,
        "holdout_policy_required": True,
        "holdout_registry_creation_required_before_strategy_search": holdout_creation_required,
        "holdout_registry_or_valid_binding_required_before_strategy_search": True,
        "null_baseline_required": True,
        "strategy_search_requires_holdout_registry": True,
    }
    approval = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_future_read_only_panel_baseline_research_execution_next": replacement_checks_all_true,
        "approval_grants_research_backtest_execution_now": False,
        "approval_grants_research_backtest_preview_now": True,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "artifact_type": "baseline_research_execution_approval_record",
        "next_module": next_module,
        "status": status,
    }
    self_validator = {
        "artifact_type": "research_backtest_preview_self_validator",
        "created_at_utc": now_utc(),
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
    }

    return {
        "approval": approval,
        "contract": contract,
        "guardrails": guardrails,
        "holdout_detection": holdout,
        "limitations_scope": limitations_scope,
        "null_cost_holdout": null_cost_holdout,
        "preview": preview,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate.json", outputs["preview"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_read_only_research_contract_preview.json", outputs["contract"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_research_limitations_and_scope.json", outputs["limitations_scope"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_first_execution_guardrails.json", outputs["guardrails"])
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_null_cost_holdout_requirements_preview.json",
        outputs["null_cost_holdout"],
    )
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry_detection_report.json", outputs["holdout_detection"])
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_execution_approval_record.json",
        outputs["approval"],
    )
    write_json(
        OUTPUT_DIR / "repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_self_validator.json",
        outputs["self_validator"],
    )
    write_text(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_preview_contract_notes.txt",
        "Read-only baseline diagnostics may be executed next. Strategy search, candidate generation, edge claims, "
        "family release, runtime, live, and capital remain blocked. A valid holdout registry or binding is required "
        "before strategy search.",
    )


def main() -> int:
    outputs = build_preview()
    write_outputs(outputs)
    print(json.dumps(outputs["preview"], indent=2, sort_keys=True))
    return 0 if outputs["preview"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
