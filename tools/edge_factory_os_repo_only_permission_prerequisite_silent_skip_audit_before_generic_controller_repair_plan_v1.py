from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_permission_prerequisite_silent_skip_audit_before_generic_controller_repair_plan_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "e376b06"
REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

ACTIVE_FRONTIER_NAME = "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER"
ACTIVE_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
ACTIVE_ARTIFACT_DIR = EDGE_LAB_ROOT / ACTIVE_NEXT_MODULE.removesuffix(".py")
ACTIVE_NEXT_CHUNK_STATE = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json"
ACTIVE_COMPLIANCE_REPORT = ACTIVE_ARTIFACT_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_compliance_report.json"
PREVIOUS_EXHAUSTIVE_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_exhaustive_python_semantic_system_audit_before_generic_controller_repair_v1"
PREVIOUS_EXHAUSTIVE_SUMMARY = PREVIOUS_EXHAUSTIVE_DIR / "repo_only_exhaustive_python_semantic_system_audit_summary.json"

PASS_STATUS = "PERMISSION_PREREQUISITE_SILENT_SKIP_AUDIT_PASS_READY_FOR_GENERIC_CONTROLLER_REPAIR_PLAN"
FAIL_STATUS = "PERMISSION_PREREQUISITE_SILENT_SKIP_AUDIT_FAIL_P0_REVIEW_REQUIRED"
PASS_QUALITY = "REPO_ONLY_PERMISSION_PREREQUISITE_SILENT_SKIP_AUDIT_PASS_REPAIR_PLAN_ALLOWED"
FAIL_QUALITY = "REPO_ONLY_PERMISSION_PREREQUISITE_SILENT_SKIP_AUDIT_FAIL_CLOSED_P0_REVIEW_REQUIRED"
PASS_NEXT_MODULE = "edge_factory_os_repo_only_generic_chunk_controller_repair_plan_after_exhaustive_semantic_system_audit_v1.py"
FAIL_NEXT_MODULE = "edge_factory_os_repo_only_permission_prerequisite_silent_skip_p0_review_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_permission_prerequisite_silent_skip_audit_report.json",
    "repo_only_permission_approval_chain_audit.json",
    "repo_only_prerequisite_missing_pass_audit.json",
    "repo_only_silent_skip_detection_report.json",
    "repo_only_blocked_vs_pass_consistency_audit.json",
    "repo_only_operation_flag_consistency_audit.json",
    "repo_only_coverage_gap_integrity_audit.json",
    "repo_only_replacement_checks_integrity_audit.json",
    "repo_only_permission_prerequisite_silent_skip_audit_summary.json",
]

PHASES = [
    {
        "phase": "single-symbol smoke-test download",
        "preview": "single_symbol_pipeline_smoke_test_preview",
        "approval": "smoke_test",
        "execution": "single_symbol_smoke_test_download_execution",
        "validator": "single_symbol_smoke_test_download_execution_validator",
        "operation": "download",
    },
    {
        "phase": "single-symbol 30-day download/build",
        "preview": "single_symbol_30_day",
        "approval": "30_day",
        "execution": "single_symbol_30_day",
        "validator": "single_symbol_30_day",
        "operation": "download_build",
    },
    {
        "phase": "single-symbol 3-year download/build",
        "preview": "single_symbol_3_year",
        "approval": "3_year",
        "execution": "single_symbol_3_year",
        "validator": "single_symbol_3_year",
        "operation": "download_build",
    },
    {
        "phase": "10-symbol pilot download/build",
        "preview": "10_symbol_pilot",
        "approval": "pilot",
        "execution": "10_symbol_pilot",
        "validator": "10_symbol_pilot",
        "operation": "download_build",
    },
    {
        "phase": "batch policy-clean build",
        "preview": "batch_policy",
        "approval": "batch_policy",
        "execution": "batch_policy_clean_build_execution",
        "validator": "batch_policy_clean_build_execution_validator",
        "operation": "build",
    },
    {
        "phase": "full USDT-SWAP symbol source discovery",
        "preview": "symbol_universe_discovery_preview",
        "approval": "symbol_source_discovery",
        "execution": "symbol_source_discovery",
        "validator": "symbol_source",
        "operation": "repo_only_discovery",
    },
    {
        "phase": "chunk_01 download execution",
        "preview": "first_chunk_download_preview",
        "approval": "first_chunk",
        "execution": "first_chunk_download_execution",
        "validator": "first_chunk_download_execution_validator",
        "operation": "download",
    },
    {
        "phase": "chunk_02 download execution",
        "preview": "chunk_02_download_preview",
        "approval": "chunk_02",
        "execution": "chunk_02_download_execution",
        "validator": "chunk_02_download_execution_validator",
        "operation": "download",
    },
    {
        "phase": "generic chunk_03 cycle execution",
        "preview": "generic_chunk_coverage_controller_preview",
        "approval": "generic_chunk_coverage_controller_approval_record",
        "execution": "generic_chunk_coverage_cycle_execution",
        "validator": "generic_chunk_coverage_cycle_compliance",
        "operation": "download",
    },
    {
        "phase": "semantic audits and sprawl audits",
        "preview": "python_file_sprawl_full_audit",
        "approval": "repo_only_audit_no_runtime_permission_required",
        "execution": "semantic_system_audit",
        "validator": "replacement_checks_all_true",
        "operation": "repo_only_audit",
    },
]


class AuditBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def approved_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def status_lines() -> list[str]:
    return [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]


def repo_effectively_clean(lines: list[str]) -> bool:
    rel = approved_tool_rel()
    return not [line for line in lines if line[3:].replace("\\", "/") != rel]


def tracked_python_files() -> list[str]:
    return sorted(path.replace("\\", "/") for path in run_git(["ls-files", "*.py"]).splitlines() if path.strip())


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def syntax_bom_check(files: list[str]) -> dict[str, Any]:
    syntax_errors = []
    bom_errors = []
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"file": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "syntax_error_files": syntax_errors,
        "bom_error_count": len(bom_errors),
        "bom_error_files": bom_errors,
    }


def is_artifact_json(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    if ".git" in parts or "__pycache__" in parts:
        return False
    if any(part.startswith("downloaded") for part in parts):
        return False
    if path.suffix.lower() != ".json":
        return False
    try:
        return path.stat().st_size <= 15_000_000
    except OSError:
        return False


def load_artifacts() -> list[dict[str, Any]]:
    artifacts = []
    for path in sorted(EDGE_LAB_ROOT.rglob("*.json")):
        if not is_artifact_json(path):
            continue
        try:
            payload = read_json(path)
        except Exception as exc:
            artifacts.append({"path": str(path), "rel": str(path.relative_to(EDGE_LAB_ROOT)), "payload": {}, "load_error": repr(exc)})
            continue
        if isinstance(payload, dict):
            artifacts.append({"path": str(path), "rel": str(path.relative_to(EDGE_LAB_ROOT)), "payload": payload, "load_error": None})
    return artifacts


def artifact_text(artifact: dict[str, Any]) -> str:
    return (artifact["rel"] + "\n" + json.dumps(artifact["payload"], sort_keys=True, default=str)).lower()


def find_artifacts(artifacts: list[dict[str, Any]], token: str) -> list[dict[str, Any]]:
    lower = token.lower()
    direct = [artifact for artifact in artifacts if lower in artifact["rel"].lower()]
    if direct:
        return direct
    return [artifact for artifact in artifacts if lower in artifact_text(artifact)]


def is_current_route_artifact(rel: str) -> bool:
    lower = rel.lower().replace("\\", "/")
    return any(
        token in lower
        for token in (
            "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_after_chunk_02_summary_v1/",
            "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1/",
            "edge_factory_os_repo_only_exhaustive_python_semantic_system_audit_before_generic_controller_repair_v1/",
            "edge_factory_os_repo_only_permission_prerequisite_silent_skip_audit_before_generic_controller_repair_plan_v1/",
        )
    )


def status_value(payload: dict[str, Any]) -> str | None:
    for key, value in payload.items():
        if isinstance(value, str) and ("status" in key.lower() or key in {"final_decision"}):
            if value.startswith(("PASS", "BLOCKED", "FAIL", "EXHAUSTIVE", "PERMISSION")):
                return value
    return None


def bool_values(obj: Any) -> list[bool]:
    values = []
    if isinstance(obj, bool):
        values.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            values.extend(bool_values(value))
    elif isinstance(obj, list):
        for value in obj:
            values.extend(bool_values(value))
    return values


def active_frontier_audit() -> dict[str, Any]:
    next_state = read_json(ACTIVE_NEXT_CHUNK_STATE) if ACTIVE_NEXT_CHUNK_STATE.exists() else {}
    compliance = read_json(ACTIVE_COMPLIANCE_REPORT) if ACTIVE_COMPLIANCE_REPORT.exists() else {}
    previous = read_json(PREVIOUS_EXHAUSTIVE_SUMMARY) if PREVIOUS_EXHAUSTIVE_SUMMARY.exists() else {}
    active = (
        ACTIVE_NEXT_CHUNK_STATE.exists()
        and next_state.get("controller_name") == "OKX_FULL_USDT_SWAP_GENERIC_CHUNK_COVERAGE_CONTROLLER_V1"
        and next_state.get("next_module") == ACTIVE_NEXT_MODULE
        and next_state.get("next_chunk_id_after_execution") == "chunk_04"
        and previous.get("final_decision") == "EXHAUSTIVE_SEMANTIC_SYSTEM_AUDIT_COMPLETE_READY_FOR_GENERIC_CONTROLLER_REPAIR_PLAN"
    )
    return {
        "active_frontier_identified": active,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "current_next_module_confirmed": next_state.get("next_module") == ACTIVE_NEXT_MODULE,
        "expected_next_chunk_id": "chunk_04",
        "previous_exhaustive_audit_status": previous.get("exhaustive_python_semantic_system_audit_status"),
        "previous_repair_scope_complete": previous.get("repair_scope_complete"),
        "next_chunk_state": {
            key: next_state.get(key)
            for key in (
                "chunk_id",
                "next_chunk_id_after_execution",
                "next_module",
                "replacement_checks_all_true",
                "data_download_performed",
                "data_build_performed",
                "aggregation_performed_now",
                "okx_api_call_performed",
                "okx_browse_performed",
                "broad_acquisition_ready",
                "safe_for_full_universe_acquisition",
            )
        },
        "compliance": {
            key: compliance.get(key)
            for key in ("no_api", "no_browse", "no_build", "no_aggregation", "no_research_backtest_edge", "no_runtime_capital_live")
        },
    }


def approval_chain_audit(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    phase_records = []
    violations = []
    for phase in PHASES:
        preview_hits = find_artifacts(artifacts, phase["preview"])
        approval_hits = find_artifacts(artifacts, phase["approval"])
        execution_hits = find_artifacts(artifacts, phase["execution"])
        validator_hits = find_artifacts(artifacts, phase["validator"])
        if phase["operation"] == "repo_only_audit":
            approval_ok = True
            now_false_respected = True
            future_ok = True
        else:
            approval_payloads = [hit["payload"] for hit in approval_hits]
            approval_ok = bool(approval_payloads)
            future_ok = any(
                value is True
                for payload in approval_payloads
                for key, value in payload.items()
                if "approval_grants" in key.lower() and ("future" in key.lower() or "next" in key.lower())
            )
            now_false_respected = all(
                value is False
                for payload in approval_payloads
                for key, value in payload.items()
                if "approval_grants" in key.lower() and key.lower().endswith("_now") and "preview" not in key.lower()
            )
        record = {
            "phase": phase["phase"],
            "operation": phase["operation"],
            "preview_found": bool(preview_hits),
            "approval_found_or_not_required": approval_ok,
            "future_or_next_permission_found": future_ok,
            "now_false_respected": now_false_respected,
            "execution_artifact_found": bool(execution_hits),
            "validator_or_summary_artifact_found": bool(validator_hits),
            "classification": "PREREQUISITE_PRESENT_OK",
            "preview_examples": [hit["rel"] for hit in preview_hits[:3]],
            "approval_examples": [hit["rel"] for hit in approval_hits[:3]],
            "execution_examples": [hit["rel"] for hit in execution_hits[:3]],
            "validator_examples": [hit["rel"] for hit in validator_hits[:3]],
        }
        if not (record["preview_found"] and record["approval_found_or_not_required"] and record["execution_artifact_found"]):
            record["classification"] = "MANUAL_REVIEW_HISTORICAL_EVIDENCE_GAP"
        if phase["phase"] == "generic chunk_03 cycle execution" and not all(
            [record["preview_found"], record["approval_found_or_not_required"], record["future_or_next_permission_found"], record["execution_artifact_found"], record["now_false_respected"]]
        ):
            record["classification"] = "APPROVAL_CHAIN_VIOLATION_P0"
            violations.append(record)
        phase_records.append(record)
    return {
        "artifact_type": "repo_only_permission_approval_chain_audit",
        "approval_chain_checked": True,
        "approval_chain_violation_count": len(violations),
        "violations": violations,
        "phase_records": phase_records,
    }


def missing_prerequisite_audit(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    required_current = [
        ACTIVE_NEXT_CHUNK_STATE,
        ACTIVE_COMPLIANCE_REPORT,
        PREVIOUS_EXHAUSTIVE_SUMMARY,
        EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_after_chunk_02_summary_v1" / "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_approval_record.json",
        EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_controller_preview_after_chunk_02_summary_v1" / "historical_okx_full_usdt_swap_generic_chunk_coverage_controller_next_chunk_selection_preview.json",
        EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json",
        EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1" / "historical_okx_full_usdt_swap_candidate_symbol_list.json",
    ]
    records = []
    violations = []
    for path in required_current:
        exists = path.exists()
        record = {
            "path": str(path),
            "exists": exists,
            "classification": "PREREQUISITE_PRESENT_OK" if exists else "MISSING_AND_PASS_CLAIMED_P0",
        }
        if not exists:
            violations.append(record)
        records.append(record)
    pass_artifacts = []
    for artifact in artifacts:
        payload = artifact["payload"]
        status = status_value(payload)
        if isinstance(status, str) and status.startswith("PASS"):
            pass_artifacts.append({"path": artifact["rel"], "status": status, "classification": "PREREQUISITE_PRESENT_OK"})
    return {
        "artifact_type": "repo_only_prerequisite_missing_pass_audit",
        "missing_prerequisite_pass_claim_count": len(violations),
        "required_current_prerequisites": records,
        "pass_artifact_count": len(pass_artifacts),
        "pass_artifact_sample": pass_artifacts[:200],
        "violations": violations,
    }


def silent_skip_audit(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    suspects = []
    p0 = []
    for artifact in artifacts:
        payload = artifact["payload"]
        status = status_value(payload) or ""
        replacement_true = payload.get("replacement_checks_all_true") is True
        if replacement_true and isinstance(payload.get("replacement_checks"), dict) and False in bool_values(payload["replacement_checks"]):
            row = {"path": artifact["rel"], "classification": "MANUAL_REVIEW_REQUIRED", "reason": "replacement_checks_all_true true but nested false detected"}
            suspects.append(row)
        if status.startswith("PASS") and payload.get("count_reconciliation_pass") is False:
            row = {"path": artifact["rel"], "classification": "CURRENT_ROUTE_SILENT_SKIP_P0" if "generic_chunk_coverage_cycle" in artifact["rel"] else "HISTORICAL_ATTENTION", "reason": "PASS with count_reconciliation_pass=false"}
            suspects.append(row)
            if row["classification"] == "CURRENT_ROUTE_SILENT_SKIP_P0":
                p0.append(row)
        if status.startswith("PASS") and payload.get("coverage_gap_detected") is True and payload.get("coverage_gaps") == []:
            suspects.append({"path": artifact["rel"], "classification": "HISTORICAL_ATTENTION", "reason": "coverage gap flag true but gap list empty in same artifact"})
    return {
        "artifact_type": "repo_only_silent_skip_detection_report",
        "silent_skip_suspect_count": len(suspects),
        "current_route_silent_skip_p0_count": len(p0),
        "suspects": suspects,
        "current_route_p0": p0,
    }


def blocked_vs_pass_consistency_audit(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    inconsistencies = []
    historical_attention = []
    for artifact in artifacts:
        payload = artifact["payload"]
        status = status_value(payload) or ""
        rel = artifact["rel"]
        bucket = inconsistencies if is_current_route_artifact(rel) else historical_attention
        if status.startswith("PASS") and int(payload.get("active_p0_blocker_count") or 0) > 0:
            bucket.append({"path": rel, "reason": "PASS with active_p0_blocker_count > 0"})
        if payload.get("replacement_checks_all_true") is False and status.startswith("PASS") and "blocked" not in str(payload.get("next_module", "")).lower() and "review" not in str(payload.get("next_module", "")).lower():
            bucket.append({"path": rel, "reason": "PASS with replacement_checks_all_true=false and non-review next_module"})
        if status.startswith("BLOCKED") and "execution" in str(payload.get("next_module", "")).lower() and "blocked" not in str(payload.get("next_module", "")).lower():
            bucket.append({"path": rel, "reason": "BLOCKED status routes to execution"})
        for key, value in payload.items():
            lower = key.lower()
            if lower.startswith("approval_grants") and lower.endswith("_now") and value is False:
                op_key = lower.replace("approval_grants_", "").replace("_now", "_performed")
                if payload.get(op_key) is True:
                    bucket.append({"path": rel, "reason": f"{key}=false but {op_key}=true"})
    return {
        "artifact_type": "repo_only_blocked_vs_pass_consistency_audit",
        "blocked_vs_pass_inconsistency_count": len(inconsistencies),
        "historical_attention_count": len(historical_attention),
        "inconsistencies": inconsistencies,
        "historical_attention": historical_attention[:500],
    }


def operation_flag_consistency_audit(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    inconsistencies = []
    unauthorized = []
    false_readiness = []
    for artifact in artifacts:
        payload = artifact["payload"]
        rel_lower = artifact["rel"].lower()
        download = payload.get("data_download_performed") is True or payload.get("archive_download_performed") is True
        build = payload.get("data_build_performed") is True
        aggregation = payload.get("aggregation_performed_now") is True
        api = payload.get("okx_api_call_performed") is True
        browse = payload.get("okx_browse_performed") is True
        if download and not any(token in rel_lower for token in ("download_execution", "generic_chunk_coverage_cycle_execution", "pilot_download", "first_chunk_download", "chunk_02_download")):
            unauthorized.append({"path": artifact["rel"], "reason": "download flag true outside approved download execution artifact"})
        if build and not any(token in rel_lower for token in ("build_execution", "rebuild_execution", "policy_clean_build")):
            unauthorized.append({"path": artifact["rel"], "reason": "build flag true outside approved build execution artifact"})
        if aggregation and "build" not in rel_lower:
            unauthorized.append({"path": artifact["rel"], "reason": "aggregation flag true outside approved build artifact"})
        if api or browse:
            unauthorized.append({"path": artifact["rel"], "reason": "api/browse performed flag true"})
        if payload.get("output_valid_for_research_backtest") is True or payload.get("output_valid_for_edge_claim") is True:
            false_readiness.append({"path": artifact["rel"], "reason": "research/backtest/edge validity true"})
        if payload.get("full_universe_acquisition_allowed_now") is True or payload.get("broad_acquisition_ready") is True:
            false_readiness.append({"path": artifact["rel"], "reason": "full universe/broad acquisition readiness true"})
        if payload.get("source_manifest_acquisition_ready") is True and "full_usdt_swap" in rel_lower:
            false_readiness.append({"path": artifact["rel"], "reason": "full route source_manifest_acquisition_ready true"})
    inconsistencies.extend(unauthorized)
    inconsistencies.extend(false_readiness)
    return {
        "artifact_type": "repo_only_operation_flag_consistency_audit",
        "operation_flag_inconsistency_count": len(inconsistencies),
        "false_readiness_claim_count": len(false_readiness),
        "unauthorized_operation_count": len(unauthorized),
        "inconsistencies": inconsistencies,
        "unauthorized_operations": unauthorized,
        "false_readiness_claims": false_readiness,
    }


def coverage_gap_integrity_audit() -> dict[str, Any]:
    chunk_artifacts = [
        {
            "chunk": "chunk_01",
            "path": EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_after_validator_v1" / "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary.json",
        },
        {
            "chunk": "chunk_02",
            "path": EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_coverage_summary_after_validator_v1" / "historical_okx_full_usdt_swap_chunk_02_download_coverage_summary.json",
        },
        {
            "chunk": "chunk_03",
            "path": ACTIVE_NEXT_CHUNK_STATE,
        },
    ]
    records = []
    violations = []
    for item in chunk_artifacts:
        path = item["path"]
        payload = read_json(path) if path.exists() else {}
        planned = int(payload.get("planned_file_count") or payload.get("expected_chunk_file_count") or payload.get("expected_file_count") or 0)
        available = int(payload.get("final_available_file_count") or payload.get("available_file_count") or payload.get("downloaded_file_count") or 0)
        missing = int(payload.get("missing_or_failed_file_count") or payload.get("missing_file_count") or 0)
        reconciliation = payload.get("count_reconciliation_pass")
        if reconciliation is None and planned:
            reconciliation = planned == available + missing
        build_ready = payload.get("build_ready_symbol_count", 0) or payload.get("files_marked_build_ready", False)
        record = {
            "chunk": item["chunk"],
            "path": str(path),
            "artifact_exists": path.exists(),
            "planned_file_count": planned,
            "available_file_count": available,
            "missing_or_failed_file_count": missing,
            "count_reconciliation_pass": bool(reconciliation),
            "coverage_gap_detected": bool(payload.get("coverage_gap_detected")),
            "build_ready_signal": build_ready,
            "classification": "PREREQUISITE_PRESENT_OK",
        }
        if not path.exists() or not record["count_reconciliation_pass"] or build_ready not in (0, False, None):
            record["classification"] = "COVERAGE_GAP_INTEGRITY_VIOLATION"
            violations.append(record)
        records.append(record)
    return {
        "artifact_type": "repo_only_coverage_gap_integrity_audit",
        "coverage_gap_integrity_checked": True,
        "coverage_gap_integrity_violation_count": len(violations),
        "chunk_records": records,
        "violations": violations,
    }


def replacement_checks_integrity_audit(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    violations = []
    historical_attention = []
    for artifact in artifacts:
        payload = artifact["payload"]
        if "replacement_checks_all_true" not in payload and "replacement_checks" not in payload:
            continue
        checks = payload.get("replacement_checks")
        all_true = payload.get("replacement_checks_all_true")
        nested_false = isinstance(checks, dict) and False in bool_values(checks)
        status = status_value(payload) or ""
        record = {
            "path": artifact["rel"],
            "replacement_checks_all_true": all_true,
            "nested_false_detected": nested_false,
            "status": status,
            "classification": "REPLACEMENT_CHECKS_OK",
        }
        if all_true is True and nested_false:
            record["classification"] = "REPLACEMENT_CHECKS_INTEGRITY_VIOLATION"
            (violations if is_current_route_artifact(artifact["rel"]) else historical_attention).append(record)
        if all_true is False and status.startswith("PASS") and "review" not in str(payload.get("next_module", "")).lower() and "blocked" not in str(payload.get("next_module", "")).lower():
            record["classification"] = "REPLACEMENT_CHECKS_INTEGRITY_VIOLATION"
            (violations if is_current_route_artifact(artifact["rel"]) else historical_attention).append(record)
        records.append(record)
    active_missing = []
    for path in [ACTIVE_NEXT_CHUNK_STATE, ACTIVE_COMPLIANCE_REPORT, PREVIOUS_EXHAUSTIVE_SUMMARY]:
        payload = read_json(path) if path.exists() else {}
        if "replacement_checks_all_true" not in payload:
            active_missing.append(str(path))
    return {
        "artifact_type": "repo_only_replacement_checks_integrity_audit",
        "replacement_checks_integrity_checked": True,
        "replacement_checks_violation_count": len(violations) + len(active_missing),
        "historical_attention_count": len(historical_attention),
        "active_current_route_missing_replacement_checks": active_missing,
        "records_checked_count": len(records),
        "violations": violations,
        "historical_attention": historical_attention[:500],
    }


def build_summary(
    tracked_count: int,
    active: dict[str, Any],
    approval: dict[str, Any],
    prereq: dict[str, Any],
    silent: dict[str, Any],
    blocked: dict[str, Any],
    flags: dict[str, Any],
    coverage: dict[str, Any],
    replacement: dict[str, Any],
) -> dict[str, Any]:
    current_p0 = (
        approval["approval_chain_violation_count"]
        + prereq["missing_prerequisite_pass_claim_count"]
        + silent["current_route_silent_skip_p0_count"]
        + blocked["blocked_vs_pass_inconsistency_count"]
        + flags["unauthorized_operation_count"]
        + flags["false_readiness_claim_count"]
        + coverage["coverage_gap_integrity_violation_count"]
        + replacement["replacement_checks_violation_count"]
    )
    clean = current_p0 == 0 and active["active_frontier_identified"] and active["current_next_module_confirmed"]
    return {
        "artifact_type": "repo_only_permission_prerequisite_silent_skip_audit_summary",
        "permission_prerequisite_silent_skip_audit_status": PASS_STATUS if clean else FAIL_STATUS,
        "audit_performed": True,
        "created_at_utc": utc_now(),
        "repo_clean": True,
        "tracked_python_count": tracked_count,
        "active_frontier_identified": active["active_frontier_identified"],
        "active_frontier_name": active["active_frontier_name"],
        "current_next_module_confirmed": active["current_next_module_confirmed"],
        "expected_next_chunk_id": active["expected_next_chunk_id"],
        "approval_chain_checked": approval["approval_chain_checked"],
        "approval_chain_violation_count": approval["approval_chain_violation_count"],
        "missing_prerequisite_pass_claim_count": prereq["missing_prerequisite_pass_claim_count"],
        "silent_skip_suspect_count": silent["silent_skip_suspect_count"],
        "current_route_silent_skip_p0_count": silent["current_route_silent_skip_p0_count"],
        "blocked_vs_pass_inconsistency_count": blocked["blocked_vs_pass_inconsistency_count"],
        "operation_flag_inconsistency_count": flags["operation_flag_inconsistency_count"],
        "coverage_gap_integrity_checked": coverage["coverage_gap_integrity_checked"],
        "coverage_gap_integrity_violation_count": coverage["coverage_gap_integrity_violation_count"],
        "replacement_checks_integrity_checked": replacement["replacement_checks_integrity_checked"],
        "replacement_checks_violation_count": replacement["replacement_checks_violation_count"],
        "false_readiness_claim_count": flags["false_readiness_claim_count"],
        "unauthorized_operation_count": flags["unauthorized_operation_count"],
        "current_p0_count": current_p0,
        "current_p1_attention_count": silent["silent_skip_suspect_count"],
        "permission_integrity_ok_for_repair_plan": clean,
        "repair_plan_allowed_next": clean,
        "repair_apply_allowed_now": False,
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "patch_allowed_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "final_decision": PASS_STATUS if clean else FAIL_STATUS,
        "current_evidence_chain_quality_after_audit": PASS_QUALITY if clean else FAIL_QUALITY,
        "next_module": PASS_NEXT_MODULE if clean else FAIL_NEXT_MODULE,
        "replacement_checks_all_true": clean,
        "replacement_checks": {
            "active_frontier_identified": active["active_frontier_identified"],
            "current_next_module_confirmed": active["current_next_module_confirmed"],
            "approval_chain_clean": approval["approval_chain_violation_count"] == 0,
            "no_missing_prerequisite_pass_claim": prereq["missing_prerequisite_pass_claim_count"] == 0,
            "no_current_route_silent_skip_p0": silent["current_route_silent_skip_p0_count"] == 0,
            "blocked_vs_pass_consistent": blocked["blocked_vs_pass_inconsistency_count"] == 0,
            "operation_flags_consistent": flags["operation_flag_inconsistency_count"] == 0,
            "coverage_gap_integrity_clean": coverage["coverage_gap_integrity_violation_count"] == 0,
            "replacement_checks_integrity_clean": replacement["replacement_checks_violation_count"] == 0,
            "repair_apply_not_allowed_now": True,
            "forbidden_actions_not_performed": True,
        },
    }


def run_audit() -> dict[str, Any]:
    lines = status_lines()
    if not repo_effectively_clean(lines):
        raise AuditBlocked(f"repo dirty before audit: {lines}")
    head = run_git(["rev-parse", "--short", "HEAD"])
    if head != EXPECTED_HEAD:
        raise AuditBlocked(f"expected HEAD {EXPECTED_HEAD}, found {head}")
    files = tracked_python_files()
    syntax = syntax_bom_check(files)
    if syntax["syntax_error_count"] or syntax["bom_error_count"]:
        raise AuditBlocked("tracked Python syntax/BOM check failed")
    artifacts = load_artifacts()
    active = active_frontier_audit()
    approval = approval_chain_audit(artifacts)
    prereq = missing_prerequisite_audit(artifacts)
    silent = silent_skip_audit(artifacts)
    blocked = blocked_vs_pass_consistency_audit(artifacts)
    flags = operation_flag_consistency_audit(artifacts)
    coverage = coverage_gap_integrity_audit()
    replacement = replacement_checks_integrity_audit(artifacts)
    summary = build_summary(len(files), active, approval, prereq, silent, blocked, flags, coverage, replacement)
    report = {
        "artifact_type": "repo_only_permission_prerequisite_silent_skip_audit_report",
        "summary": summary,
        "syntax_bom_precheck": syntax,
        "active_frontier_audit": active,
        "approval_chain_audit": approval,
        "missing_prerequisite_audit": prereq,
        "silent_skip_detection": silent,
        "blocked_vs_pass_consistency": blocked,
        "operation_flag_consistency": flags,
        "coverage_gap_integrity": coverage,
        "replacement_checks_integrity": replacement,
        "artifact_json_count_scanned": len(artifacts),
        "forbidden_actions_performed_by_this_audit": {
            "patch_existing_files": False,
            "download": False,
            "api": False,
            "browse": False,
            "zip_csv_parquet_row_read": False,
            "data_build": False,
            "aggregation": False,
            "delete": False,
            "move": False,
            "cleanup": False,
        },
    }
    write_json(OUTPUT_DIR / "repo_only_permission_prerequisite_silent_skip_audit_report.json", report)
    write_json(OUTPUT_DIR / "repo_only_permission_approval_chain_audit.json", approval)
    write_json(OUTPUT_DIR / "repo_only_prerequisite_missing_pass_audit.json", prereq)
    write_json(OUTPUT_DIR / "repo_only_silent_skip_detection_report.json", silent)
    write_json(OUTPUT_DIR / "repo_only_blocked_vs_pass_consistency_audit.json", blocked)
    write_json(OUTPUT_DIR / "repo_only_operation_flag_consistency_audit.json", flags)
    write_json(OUTPUT_DIR / "repo_only_coverage_gap_integrity_audit.json", coverage)
    write_json(OUTPUT_DIR / "repo_only_replacement_checks_integrity_audit.json", replacement)
    write_json(OUTPUT_DIR / "repo_only_permission_prerequisite_silent_skip_audit_summary.json", summary)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise AuditBlocked(f"missing required artifacts: {missing}")
    return summary


def blocked_summary(message: str) -> dict[str, Any]:
    summary = {
        "artifact_type": "repo_only_permission_prerequisite_silent_skip_audit_summary",
        "permission_prerequisite_silent_skip_audit_status": FAIL_STATUS,
        "audit_performed": False,
        "blocked_reason": message,
        "repo_clean": False,
        "tracked_python_count": 0,
        "active_frontier_identified": False,
        "active_frontier_name": ACTIVE_FRONTIER_NAME,
        "current_next_module_confirmed": False,
        "expected_next_chunk_id": "chunk_04",
        "approval_chain_checked": False,
        "approval_chain_violation_count": 1,
        "missing_prerequisite_pass_claim_count": 0,
        "silent_skip_suspect_count": 0,
        "current_route_silent_skip_p0_count": 0,
        "blocked_vs_pass_inconsistency_count": 0,
        "operation_flag_inconsistency_count": 0,
        "coverage_gap_integrity_checked": False,
        "coverage_gap_integrity_violation_count": 0,
        "replacement_checks_integrity_checked": False,
        "replacement_checks_violation_count": 0,
        "false_readiness_claim_count": 0,
        "unauthorized_operation_count": 0,
        "current_p0_count": 1,
        "current_p1_attention_count": 0,
        "permission_integrity_ok_for_repair_plan": False,
        "repair_plan_allowed_next": False,
        "repair_apply_allowed_now": False,
        "deletion_allowed_now": False,
        "move_allowed_now": False,
        "cleanup_allowed_now": False,
        "patch_allowed_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "final_decision": FAIL_STATUS,
        "current_evidence_chain_quality_after_audit": FAIL_QUALITY,
        "next_module": FAIL_NEXT_MODULE,
        "replacement_checks_all_true": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_permission_prerequisite_silent_skip_audit_summary.json", summary)
    return summary


def main() -> int:
    try:
        summary = run_audit()
    except Exception as exc:
        summary = blocked_summary(type(exc).__name__ + ": " + str(exc))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
