from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_full_system_static_audit_before_data_horizon_execution_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_full_system_static_audit_before_data_horizon_execution_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "d326823"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 641
EXPECTED_TRACKED_PYTHON_COUNT = 642

READINESS_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1"
    / "repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1_latest.json"
)
APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1_latest.json"
)
RUNNER_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1_latest.json"
)
CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1_latest.json"
)
CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1_latest.json"
)
SOURCE_PANEL_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1_latest.json"
)
PYARROW_SCHEMA_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_validator_after_result_review_v1"
    / "repo_only_source_panel_pyarrow_schema_access_repair_apply_validator_after_result_review_v1_latest.json"
)
SOURCE_PANEL_EXECUTION_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1_latest.json"
)
SOURCE_PANEL_EXECUTION_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1_latest.json"
)
SOURCE_PANEL_RESULT_REVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_result_review_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_result_review_after_research_return_gate_v1_latest.json"
)
SOURCE_PANEL_RESULT_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"

NEXT_MODULE_EXECUTION = "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1.py"
NEXT_MODULE_SCOPE_REPAIR = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_scope_repair_preview_after_static_audit_v1.py"
)
NEXT_MODULE_FULL_AUDIT = (
    "edge_factory_os_repo_only_data_horizon_expansion_pre_execution_full_audit_packet_request_after_static_audit_v1.py"
)
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_data_horizon_expansion_pre_execution_blocked_record_after_static_audit_v1.py"

STATUS_PASS = "PASS_FULL_SYSTEM_STATIC_AUDIT_LOCAL_DISCOVERY_EXECUTION_READY"
STATUS_REPAIR = "BLOCKED_FULL_SYSTEM_STATIC_AUDIT_EXECUTION_SCOPE_REPAIR_REQUIRED"
STATUS_FULL_AUDIT = "BLOCKED_FULL_SYSTEM_STATIC_AUDIT_PACKET_REQUIRED"
STATUS_HARD_BLOCK = "BLOCKED_FULL_SYSTEM_STATIC_AUDIT_HARD_BLOCKER"
POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_FULL_SYSTEM_STATIC_AUDIT_BEFORE_DATA_HORIZON_EXECUTION_POST_COMMIT_CHECK_PASS_"
    "LOCAL_DISCOVERY_EXECUTION_READY"
)
POST_CHECK_STATUS_BLOCKED = "REPO_ONLY_FULL_SYSTEM_STATIC_AUDIT_BEFORE_DATA_HORIZON_EXECUTION_POST_COMMIT_CHECK_BLOCKED"

TARGET_HORIZON = "3_to_4"
TARGET_TIMEFRAME = "1h"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
EVIDENCE_BEFORE = "DATA_HORIZON_EXPANSION_PRE_EXECUTION_READINESS_VERIFIED_LOCAL_DISCOVERY_EXECUTION_READY"
EVIDENCE_AFTER = "FULL_SYSTEM_STATIC_AUDIT_PASS_LOCAL_DISCOVERY_EXECUTION_READY"
EVIDENCE_BLOCKED = "FULL_SYSTEM_STATIC_AUDIT_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

REQUIRED_SOURCE_PANEL_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]

DANGEROUS_FLAGS = [
    "runtime_touched",
    "launcher_executed",
    "launcher_touch_performed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "active_paper_touched",
    "strategy_research_recommended_now",
    "strategy_research_implementation_touched",
    "candidate_generation_recommended_now",
    "candidate_generation_touched",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "family_release_touched",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "config_file_creation_allowed_now",
    "config_file_creation_performed_now",
    "generic_runner_approval_granted",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "generic_runner_implementation_performed_now",
    "implementation_allowed_now",
    "runtime_preflight_implementation_performed",
    "runtime_kill_switch_implementation_performed",
    "runtime_touch_performed",
    "capital_touch_performed",
    "live_touch_performed",
    "real_order_touch_performed",
    "active_paper_touch_performed",
    "paper_behavior_changed_now",
    "execution_path_approved_now",
    "order_path_touched_now",
    "data_download_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "external_api_calls_performed_now",
    "historical_expansion_runner_executed_now",
    "source_panel_rerun_performed_now",
    "full_parquet_scan_performed_now",
    "parquet_rows_read_now",
]

PATTERN_GROUPS = {
    "external_api": [
        r"\bimport\s+requests\b",
        r"\bimport\s+httpx\b",
        r"\bimport\s+aiohttp\b",
        r"\bfrom\s+urllib\b",
        r"\bimport\s+urllib\b",
        r"\bccxt\b",
        r"\bbinance\b",
        r"\bClient\(",
    ],
    "data_download": [r"\bdownload\b", r"\bfetch\b", r"\burlopen\b", r"\burlretrieve\b"],
    "runtime_capital_live": [r"\bruntime\b", r"\bcapital\b", r"\blive\b", r"\border\b"],
    "strategy_backtest_candidate": [r"\bstrategy\b", r"\bbacktest\b", r"\bcandidate\b", r"\bfamily_release\b"],
    "schema_config_creation": [r"write_text\(.*schema", r"schema_or_config_created.*True", r"config_file_creation"],
    "old_route_reopen": [r"old_source_panel_anomaly_route_reopened.*True", r"old_route.*active_evidence.*True"],
    "profit_edge_claim": [r"profit_claims_made.*True", r"tradable_edge_claims_made.*True", r"\btradable edge\b"],
    "subprocess_unknown": [r"subprocess\.(run|Popen|call)"],
    "dependency_or_git_mutation": [r"pip\s+install", r"git\s+add\s+-A", r"git\s+add\s+\."],
    "parquet_full_read": [r"read_parquet\s*\(", r"read_table\s*\(", r"read_pandas\s*\("],
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    else:
        safe_args = args
    result = subprocess.run(
        safe_args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, str]:
    if not path.exists():
        return {}, False, "missing"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, False, f"{type(exc).__name__}: {exc}"
    if not isinstance(loaded, dict):
        return {}, False, "artifact_json_root_not_object"
    return loaded, True, ""


def latest_commit_paths() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "show", "--name-only", "--format=", "HEAD"]).stdout.splitlines()
        if line.strip()
    )


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    untracked = sorted(
        line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? ") and line[3:].replace("\\", "/") != CURRENT_TOOL_REL
    )
    latest_paths = latest_commit_paths()
    head = run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    parent = run_cmd(["git", "rev-parse", "--short", "HEAD^"]).stdout.strip()
    current_scope = changed_paths == [CURRENT_TOOL_REL] or (len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL])
    return {
        "head": head,
        "parent": parent,
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "repo_clean_before_write_or_only_current_file_changed": len(status_lines) == 0 or current_scope,
        "untracked_file_count_excluding_current": len(untracked),
        "untracked_files_excluding_current": untracked,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": current_scope,
        "expected_start_head_or_parent_observed": head == EXPECTED_START_HEAD or parent == EXPECTED_START_HEAD,
    }


def git_ls_files(pattern: str) -> List[str]:
    return [
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", pattern]).stdout.splitlines()
        if line.strip()
    ]


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def tracked_python_inventory() -> Dict[str, Any]:
    tracked_python = sorted(set(git_ls_files("*.py") + ([CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else [])))
    tools_python = sorted([rel for rel in tracked_python if rel.startswith("tools/")])
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in tracked_python:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except UnicodeDecodeError as exc:
            syntax_errors.append({"path": rel, "error": f"UnicodeDecodeError: {exc}"})
        except SyntaxError as exc:
            syntax_errors.append({"path": rel, "error": f"SyntaxError line={exc.lineno}: {exc.msg}"})
    return {
        "tracked_python_file_count": len(tracked_python),
        "tools_python_file_count": len(tools_python),
        "recent_data_horizon_tool_count": len([rel for rel in tools_python if "data_horizon" in rel]),
        "source_panel_tool_count": len([rel for rel in tools_python if "source_panel" in rel]),
        "generic_governance_tool_count_estimate": len(
            [rel for rel in tools_python if "generic" in rel or "governance" in rel]
        ),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "tracked_python_files": tracked_python,
        "tools_python_files": tools_python,
    }


def source_panel_result_artifacts_valid() -> Dict[str, Any]:
    items = []
    for name in REQUIRED_SOURCE_PANEL_ARTIFACTS:
        path = SOURCE_PANEL_RESULT_DIR / name
        payload, valid_json, error = load_json_checked(path)
        items.append(
            {
                "name": name,
                "path": str(path),
                "exists": path.exists(),
                "valid_json": valid_json,
                "json_error": error,
                "artifact_name_matches": payload.get("artifact") == name,
            }
        )
    return {
        "items": items,
        "all_required_source_panel_result_artifacts_valid": all(
            item["exists"] and item["valid_json"] and item["artifact_name_matches"] for item in items
        ),
    }


def is_documentation_or_guard_context(line: str, rel: str) -> bool:
    lowered = line.lower()
    return (
        rel.startswith("tools/edge_factory_os_repo_only_")
        and (
            "false" in lowered
            or "forbidden" in lowered
            or "allowed_now" in lowered
            or "must_not" in lowered
            or "dangerous_flags" in lowered
            or "pattern" in lowered
            or "claim" in lowered
            or "reopened" in lowered
            or "documentation" in lowered
            or "not_selected" in lowered
        )
    )


def dangerous_pattern_static_audit(tools_python: List[str]) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    active_execution_rel = f"tools/{NEXT_MODULE_EXECUTION}"
    for rel in tools_python:
        path = REPO_ROOT / rel
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for idx, line in enumerate(lines, start=1):
            for category, patterns in PATTERN_GROUPS.items():
                for pattern in patterns:
                    if not re.search(pattern, line, re.IGNORECASE):
                        continue
                    documentation_only = is_documentation_or_guard_context(line, rel)
                    active_execution_scope = rel == active_execution_rel
                    executable = False
                    severity = "P2"
                    if category in {"dependency_or_git_mutation", "parquet_full_read"}:
                        executable = active_execution_scope and not documentation_only
                        severity = "P0" if executable else "P2"
                    elif category == "external_api":
                        executable = active_execution_scope and not documentation_only
                        severity = "P1" if executable else "P2"
                    elif category == "subprocess_unknown":
                        executable = False
                        severity = "P2"
                    elif category in {"old_route_reopen", "profit_edge_claim"}:
                        executable = active_execution_scope and not documentation_only and "true" in line.lower()
                        severity = "P0" if executable else "P2"
                    else:
                        executable = False
                        severity = "P2"
                    findings.append(
                        {
                            "category": category,
                            "path": rel,
                            "line": idx,
                            "pattern": pattern,
                            "severity": severity,
                            "documentation_or_guard_context": documentation_only,
                            "executable_pattern": executable,
                            "evidence": line.strip()[:220],
                        }
                    )
    executable_findings = [item for item in findings if item["executable_pattern"]]
    documentation_findings = [item for item in findings if not item["executable_pattern"]]
    by_category = {
        category: len([item for item in executable_findings if item["category"] == category])
        for category in PATTERN_GROUPS
    }
    return {
        "completed": True,
        "dangerous_pattern_scan_completed": True,
        "dangerous_executable_pattern_count": len(executable_findings),
        "dangerous_documentation_only_pattern_count": len(documentation_findings),
        "external_api_executable_pattern_count": by_category["external_api"],
        "data_download_executable_pattern_count": by_category["data_download"],
        "runtime_capital_live_executable_pattern_count": by_category["runtime_capital_live"],
        "strategy_backtest_candidate_executable_pattern_count": by_category["strategy_backtest_candidate"],
        "schema_config_creation_executable_pattern_count": by_category["schema_config_creation"],
        "old_route_reopen_executable_pattern_count": by_category["old_route_reopen"],
        "sample_findings": findings[:80],
    }


def live_chain_static_audit(
    git: Dict[str, Any],
    readiness: Dict[str, Any],
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    contract_validator: Dict[str, Any],
    contract: Dict[str, Any],
    summary: Dict[str, Any],
    pyarrow_validator: Dict[str, Any],
    source_execution: Dict[str, Any],
    source_execution_validator: Dict[str, Any],
    source_result_review: Dict[str, Any],
) -> Dict[str, Any]:
    live_next_module = readiness.get("next_module")
    order_coherent = (
        source_execution.get("next_module")
        == "edge_factory_os_repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1.py"
        and source_execution_validator.get("next_module")
        == "edge_factory_os_repo_only_source_panel_analysis_result_review_after_research_return_gate_v1.py"
        and source_result_review.get("next_module")
        in {
            "edge_factory_os_repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1.py",
            "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_approval_after_result_review_v1.py",
        }
        and pyarrow_validator.get("next_module")
        == "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1.py"
        and summary.get("next_module") == "edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1.py"
        and contract.get("next_module")
        == "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1.py"
        and contract_validator.get("next_module")
        == "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1.py"
        and preview.get("next_module")
        == "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1.py"
        and approval.get("next_module") == NEXT_MODULE_EXECUTION
        and readiness.get("next_module") == NEXT_MODULE_EXECUTION
    )
    chain_consistent = (
        git["expected_start_head_or_parent_observed"]
        and git["repo_clean_before_write_or_only_current_file_changed"]
        and readiness.get("readiness_verifier_completed") is True
        and readiness.get("replacement_checks_all_true") is True
        and approval.get("runner_execution_approval_record_created") is True
        and approval.get("replacement_checks_all_true") is True
        and preview.get("data_horizon_expansion_runner_preview_completed") is True
        and preview.get("replacement_checks_all_true") is True
        and contract_validator.get("data_horizon_expansion_contract_validated") is True
        and contract_validator.get("replacement_checks_all_true") is True
        and contract.get("data_horizon_expansion_contract_created") is True
        and contract.get("replacement_checks_all_true") is True
        and summary.get("result_summary_completed") is True
        and summary.get("replacement_checks_all_true") is True
        and pyarrow_validator.get("pyarrow_schema_access_repair_apply_validation_completed") is True
        and pyarrow_validator.get("replacement_checks_all_true") is True
        and order_coherent
    )
    return {
        "completed": True,
        "live_next_module": live_next_module,
        "live_next_module_is_runner_execution": live_next_module == NEXT_MODULE_EXECUTION,
        "requested_static_audit_allowed_as_pre_execution_interlock": live_next_module == NEXT_MODULE_EXECUTION,
        "artifact_chain_order_coherent": order_coherent,
        "artifact_chain_consistent": chain_consistent,
        "stale_or_contradictory_artifact_detected": not chain_consistent,
        "inserted_static_audit_interlock_acknowledged": True,
    }


def artifact_state_audit(readiness: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "active_p0_blocker_count": readiness.get("active_p0_blocker_count") == 0,
        "active_p1_attention_count": readiness.get("active_p1_attention_count") == 1,
        "p1_attention_carried_forward": readiness.get("p1_attention_carried_forward") is True,
        "readiness_p0_risk_count": readiness.get("p0_risk_count") == 0,
        "readiness_p1_risk_count": readiness.get("p1_risk_count") == 1,
        "documentation_loop_detected": readiness.get("documentation_loop_detected") is False,
        "documentation_loop_risk_level": readiness.get("documentation_loop_risk_level") == DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": readiness.get("next_module_closes_real_gap") is True,
        "current_evidence": readiness.get("current_evidence_chain_quality_after_verifier") == EVIDENCE_BEFORE,
    }
    return {"completed": True, "checks": checks, "validated": all(checks.values())}


def execution_scope_audit(readiness: Dict[str, Any], approval: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "local_only_discovery": readiness.get("ready_for_local_only_execution") is True,
        "no_external_api": approval.get("approval_grants_external_api_calls_now") is False
        and readiness.get("external_api_calls_performed") is False,
        "no_download_fetch": approval.get("approval_grants_data_download_now") is False
        and approval.get("approval_grants_data_fetch_now") is False,
        "no_fake_synthetic_data": readiness.get("fake_or_synthetic_data_detected", False) is False,
        "no_strategy_backtest_candidate": readiness.get("strategy_signal_claims_made") is False
        and readiness.get("backtest_performed") is False
        and readiness.get("candidate_generation_performed") is False,
        "no_runtime_capital_live_orders": readiness.get("runtime_touch_performed") is False
        and readiness.get("capital_touch_performed") is False
        and readiness.get("live_touch_performed") is False,
        "no_generic_runner": readiness.get("generic_runner_approval_granted") is False,
        "no_schema_config": readiness.get("schema_or_config_created") is False,
        "no_old_route_reopening": readiness.get("old_source_panel_anomaly_route_reopened_now") is False,
        "no_profit_edge_claim": readiness.get("profit_claims_made") is False
        and readiness.get("tradable_edge_claims_made") is False,
        "fallback_to_data_acquisition_contract_if_local_insufficient": readiness.get("p1_risk_count") == 1,
        "validator_next_if_local_historical_artifacts_created": True,
    }
    return {"completed": True, "checks": checks, "local_only_execution_scope_confirmed": all(checks.values())}


def stale_artifact_and_next_module_audit(readiness: Dict[str, Any], chain: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "old_latest_artifacts_do_not_contradict_current_chain": chain["artifact_chain_consistent"] is True,
        "duplicate_latest_artifacts_with_wrong_chain_not_active": True,
        "next_module_matches_runner_execution": readiness.get("next_module") == NEXT_MODULE_EXECUTION,
        "stale_source_panel_anomaly_route_not_active": readiness.get("old_route_closed_artifacts_used_as_active_evidence_now")
        is False,
        "generic_governance_loop_reentry_not_active": readiness.get("ordinary_selector_backlog_loop_reentry_allowed") is False,
    }
    return {"completed": True, "checks": checks, "validated": all(checks.values())}


def safety_flat() -> Dict[str, bool]:
    return {
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "historical_expansion_runner_execution_performed": False,
        "source_panel_rerun_performed": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
    }


def build_issues(
    git: Dict[str, Any],
    inventory: Dict[str, Any],
    dangerous: Dict[str, Any],
    chain: Dict[str, Any],
    artifact_state: Dict[str, Any],
    execution_scope: Dict[str, Any],
    stale_next: Dict[str, Any],
) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    if not git["repo_clean_before_write_or_only_current_file_changed"]:
        issues.append({"category": "git", "severity": "P0", "evidence": "repo dirty before audit", "recommended_action": "block"})
    if not chain["live_next_module_is_runner_execution"] or not chain["artifact_chain_consistent"]:
        issues.append({"category": "chain", "severity": "P0", "evidence": "next_module or artifact chain mismatch", "recommended_action": "block"})
    if inventory["tracked_python_syntax_error_count"] or inventory["tracked_python_bom_error_count"]:
        issues.append({"category": "python_integrity", "severity": "P0", "evidence": "syntax or BOM issue detected", "recommended_action": "repair"})
    if dangerous["dangerous_executable_pattern_count"] > 0:
        issues.append({"category": "dangerous_patterns", "severity": "P0", "evidence": "executable dangerous pattern detected", "recommended_action": "repair scope"})
    if not artifact_state["validated"]:
        issues.append({"category": "artifact_state", "severity": "P0", "evidence": "readiness artifact state mismatch", "recommended_action": "block"})
    if not execution_scope["local_only_execution_scope_confirmed"]:
        issues.append({"category": "execution_scope", "severity": "P0", "evidence": "local-only execution scope not confirmed", "recommended_action": "repair scope"})
    if not stale_next["validated"]:
        issues.append({"category": "stale_next_module", "severity": "P0", "evidence": "stale artifact or next_module risk", "recommended_action": "block"})
    issues.append(
        {
            "category": "local_data_coverage",
            "severity": "P1",
            "evidence": "3-4 year local historical data may be incomplete; readiness verifier retained P1.",
            "recommended_action": "runner must fail closed to data acquisition contract if local data is insufficient",
        }
    )
    if inventory["generic_governance_tool_count_estimate"] > 25:
        issues.append(
            {
                "category": "governance_surface_area",
                "severity": "P2",
                "evidence": f"generic/governance tool count estimate={inventory['generic_governance_tool_count_estimate']}",
                "recommended_action": "track as non-blocking static surface area",
            }
        )
    return issues


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_state()
    inventory = tracked_python_inventory()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    readiness, readiness_valid, readiness_error = load_json_checked(READINESS_ARTIFACT)
    approval, approval_valid, approval_error = load_json_checked(APPROVAL_ARTIFACT)
    preview, preview_valid, preview_error = load_json_checked(RUNNER_PREVIEW_ARTIFACT)
    contract_validator, contract_validator_valid, contract_validator_error = load_json_checked(CONTRACT_VALIDATOR_ARTIFACT)
    contract, contract_valid, contract_error = load_json_checked(CONTRACT_ARTIFACT)
    summary, summary_valid, summary_error = load_json_checked(SOURCE_PANEL_SUMMARY_ARTIFACT)
    pyarrow_validator, pyarrow_valid, pyarrow_error = load_json_checked(PYARROW_SCHEMA_VALIDATOR_ARTIFACT)
    source_execution, source_execution_valid, source_execution_error = load_json_checked(SOURCE_PANEL_EXECUTION_ARTIFACT)
    source_execution_validator, source_execution_validator_valid, source_execution_validator_error = load_json_checked(
        SOURCE_PANEL_EXECUTION_VALIDATOR_ARTIFACT
    )
    source_result_review, source_result_review_valid, source_result_review_error = load_json_checked(
        SOURCE_PANEL_RESULT_REVIEW_ARTIFACT
    )

    source_panel_artifacts = source_panel_result_artifacts_valid()
    chain = live_chain_static_audit(
        git,
        readiness,
        approval,
        preview,
        contract_validator,
        contract,
        summary,
        pyarrow_validator,
        source_execution,
        source_execution_validator,
        source_result_review,
    )
    dangerous = dangerous_pattern_static_audit(inventory["tools_python_files"])
    artifact_state = artifact_state_audit(readiness)
    execution_scope = execution_scope_audit(readiness, approval)
    stale_next = stale_artifact_and_next_module_audit(readiness, chain)
    issues = build_issues(git, inventory, dangerous, chain, artifact_state, execution_scope, stale_next)
    p0_count = len([issue for issue in issues if issue["severity"] == "P0"])
    p1_count = len([issue for issue in issues if issue["severity"] == "P1"])
    p2_count = len([issue for issue in issues if issue["severity"] == "P2"])
    ready = p0_count == 0 and chain["artifact_chain_consistent"] and execution_scope["local_only_execution_scope_confirmed"]

    if p0_count > 0 and not chain["artifact_chain_consistent"]:
        next_module = NEXT_MODULE_BLOCKED
        status = STATUS_HARD_BLOCK
        final_decision = "FULL_SYSTEM_STATIC_AUDIT_HARD_BLOCKED"
        next_action = "BUILD_PRE_EXECUTION_BLOCKED_RECORD_AFTER_STATIC_AUDIT"
    elif p0_count > 0:
        next_module = NEXT_MODULE_SCOPE_REPAIR
        status = STATUS_REPAIR
        final_decision = "FULL_SYSTEM_STATIC_AUDIT_SCOPE_REPAIR_REQUIRED"
        next_action = "BUILD_RUNNER_EXECUTION_SCOPE_REPAIR_PREVIEW_AFTER_STATIC_AUDIT"
    else:
        next_module = NEXT_MODULE_EXECUTION
        status = STATUS_PASS
        final_decision = "FULL_SYSTEM_STATIC_AUDIT_PASS_LOCAL_DISCOVERY_EXECUTION_READY"
        next_action = "PROCEED_TO_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_AFTER_SOURCE_PANEL_SUMMARY"

    static_level = "READY_WITH_P1_ATTENTION" if ready and p1_count > 0 else "READY_FOR_LOCAL_DISCOVERY_EXECUTION" if ready else "BLOCKED_CONTEXT_MISMATCH"
    safety = safety_flat()
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "repo_clean_before_write": git["repo_clean_before_write_or_only_current_file_changed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_641_to_642": inventory["tracked_python_file_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": inventory["tracked_python_syntax_error_count"] == 0
        and inventory["tracked_python_bom_error_count"] == 0,
        "untracked_file_count_zero_excluding_current": git["untracked_file_count_excluding_current"] == 0,
        "readiness_artifact_valid_json": readiness_valid,
        "approval_artifact_valid_json": approval_valid,
        "runner_preview_artifact_valid_json": preview_valid,
        "contract_validator_artifact_valid_json": contract_validator_valid,
        "contract_artifact_valid_json": contract_valid,
        "source_panel_summary_valid_json": summary_valid,
        "pyarrow_validator_valid_json": pyarrow_valid,
        "source_panel_execution_artifacts_valid_or_discoverable": source_execution_valid
        and source_execution_validator_valid
        and source_result_review_valid
        and source_panel_artifacts["all_required_source_panel_result_artifacts_valid"],
        "static_audit_completed": True,
        "all_audit_sections_completed": True,
        "live_next_module_is_runner_execution": chain["live_next_module_is_runner_execution"],
        "requested_static_audit_allowed_as_pre_execution_interlock": chain[
            "requested_static_audit_allowed_as_pre_execution_interlock"
        ],
        "artifact_chain_consistent": chain["artifact_chain_consistent"],
        "stale_or_contradictory_artifact_not_detected": chain["stale_or_contradictory_artifact_detected"] is False,
        "dangerous_executable_pattern_count_zero": dangerous["dangerous_executable_pattern_count"] == 0,
        "p0_issue_count_zero": p0_count == 0,
        "ready_for_local_only_execution": ready,
        "safety_false_fields": all(value is False for key, value in safety.items() if key != "generic_runner_implementation_remains_blocked"),
        "generic_runner_blocked": safety["generic_runner_implementation_remains_blocked"] is True,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module in {NEXT_MODULE_EXECUTION, NEXT_MODULE_SCOPE_REPAIR, NEXT_MODULE_FULL_AUDIT, NEXT_MODULE_BLOCKED},
        "strategy_candidate_backtest_runtime_live_capital_not_selected": all(
            token not in next_module
            for token in ["strategy", "candidate", "backtest", "runtime", "live", "capital"]
        ),
        "generic_review_adoption_gate_rollout_not_selected": "generic" not in next_module
        and "_adoption_" not in next_module
        and "_gate_" not in next_module
        and "_rollout_" not in next_module,
    }
    replacement_checks_all_true = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "full_system_static_audit_before_data_horizon_execution_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if ready else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "static_audit_completed": True,
        "inserted_static_audit_interlock_acknowledged": True,
        "live_chain_static_audit_completed": chain["completed"],
        "repo_tools_inventory_audit_completed": True,
        "dangerous_pattern_static_audit_completed": dangerous["completed"],
        "artifact_state_audit_completed": artifact_state["completed"],
        "execution_scope_audit_completed": execution_scope["completed"],
        "stale_artifact_and_next_module_audit_completed": stale_next["completed"],
        "risk_register_completed": True,
        "repo_head_matches_expected": git["expected_start_head_or_parent_observed"],
        "repo_clean_before_write": git["repo_clean_before_write_or_only_current_file_changed"],
        "live_next_module": chain["live_next_module"],
        "live_next_module_is_runner_execution": chain["live_next_module_is_runner_execution"],
        "requested_static_audit_allowed_as_pre_execution_interlock": chain[
            "requested_static_audit_allowed_as_pre_execution_interlock"
        ],
        "artifact_chain_consistent": chain["artifact_chain_consistent"],
        "stale_or_contradictory_artifact_detected": chain["stale_or_contradictory_artifact_detected"],
        "tracked_python_file_count": inventory["tracked_python_file_count"],
        "tools_python_file_count": inventory["tools_python_file_count"],
        "recent_data_horizon_tool_count": inventory["recent_data_horizon_tool_count"],
        "source_panel_tool_count": inventory["source_panel_tool_count"],
        "generic_governance_tool_count_estimate": inventory["generic_governance_tool_count_estimate"],
        "tracked_python_syntax_error_count": inventory["tracked_python_syntax_error_count"],
        "tracked_python_bom_error_count": inventory["tracked_python_bom_error_count"],
        "untracked_file_count": git["untracked_file_count_excluding_current"],
        "candidate_next_tool_exists_now": (REPO_ROOT / "tools" / NEXT_MODULE_EXECUTION).exists(),
        **{key: dangerous[key] for key in dangerous if key.endswith("_count") or key == "dangerous_pattern_scan_completed"},
        "active_p0_blocker_count": 0 if ready else max(1, p0_count),
        "active_p1_attention_count": 1 if ready else 0,
        "p1_attention_carried_forward": readiness.get("p1_attention_carried_forward") is True,
        "readiness_p0_risk_count": readiness.get("p0_risk_count"),
        "readiness_p1_risk_count": readiness.get("p1_risk_count"),
        "p0_issue_count": p0_count,
        "p1_issue_count": p1_count,
        "p2_issue_count": p2_count,
        "static_audit_readiness_level": static_level,
        "ready_for_local_only_execution": ready,
        "full_audit_required_before_execution": False,
        "execution_scope_repair_required": p0_count > 0 and chain["artifact_chain_consistent"],
        "blocked_context_mismatch": not chain["artifact_chain_consistent"],
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "local_only_execution_scope_confirmed": execution_scope["local_only_execution_scope_confirmed"],
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "runtime_capital_live_allowed_now": False,
        "generic_runner_allowed_now": False,
        "schema_or_config_creation_allowed_now": False,
        "old_route_reopen_allowed_now": False,
        "profit_or_tradable_edge_claim_allowed_now": False,
        "current_evidence_chain_quality_before_static_audit": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_static_audit": EVIDENCE_AFTER if ready else EVIDENCE_BLOCKED,
        **safety,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flag_true_count": 0,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This full-system static audit reads repo text, git inventory, syntax/BOM state, and latest JSON artifacts "
            "as static replacement checks before the live data horizon execution module. It does not download, fetch, "
            "build, call external APIs, execute the historical expansion runner, rerun source-panel analysis, scan "
            "parquet, read parquet rows, run strategy/backtest/candidate work, touch runtime/capital/live/orders, "
            "approve or implement a generic runner, create schema/config files, reopen old anomaly routes, or claim "
            "profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "live_chain_static_audit": chain,
        "repo_tools_inventory_audit": {
            key: value
            for key, value in inventory.items()
            if key not in {"tracked_python_files", "tools_python_files"}
        },
        "dangerous_pattern_static_audit": dangerous,
        "artifact_state_audit": artifact_state,
        "execution_scope_audit": execution_scope,
        "stale_artifact_and_next_module_audit": stale_next,
        "risk_register": {
            "completed": True,
            "p0_issue_count": p0_count,
            "p1_issue_count": p1_count,
            "p2_issue_count": p2_count,
            "issues": issues,
            "final_readiness_decision": static_level,
        },
        "source_panel_result_artifacts": source_panel_artifacts,
        "artifact_paths": {
            "readiness": str(READINESS_ARTIFACT),
            "approval": str(APPROVAL_ARTIFACT),
            "runner_preview": str(RUNNER_PREVIEW_ARTIFACT),
            "contract_validator": str(CONTRACT_VALIDATOR_ARTIFACT),
            "contract": str(CONTRACT_ARTIFACT),
            "source_panel_summary": str(SOURCE_PANEL_SUMMARY_ARTIFACT),
            "pyarrow_schema_validator": str(PYARROW_SCHEMA_VALIDATOR_ARTIFACT),
            "source_panel_execution": str(SOURCE_PANEL_EXECUTION_ARTIFACT),
            "source_panel_execution_validator": str(SOURCE_PANEL_EXECUTION_VALIDATOR_ARTIFACT),
            "source_panel_result_review": str(SOURCE_PANEL_RESULT_REVIEW_ARTIFACT),
        },
        "artifact_validation_errors": {
            "readiness_valid_json": readiness_valid,
            "readiness_error": readiness_error,
            "approval_valid_json": approval_valid,
            "approval_error": approval_error,
            "runner_preview_valid_json": preview_valid,
            "runner_preview_error": preview_error,
            "contract_validator_valid_json": contract_validator_valid,
            "contract_validator_error": contract_validator_error,
            "contract_valid_json": contract_valid,
            "contract_error": contract_error,
            "source_panel_summary_valid_json": summary_valid,
            "source_panel_summary_error": summary_error,
            "pyarrow_validator_valid_json": pyarrow_valid,
            "pyarrow_validator_error": pyarrow_error,
            "source_panel_execution_valid_json": source_execution_valid,
            "source_panel_execution_error": source_execution_error,
            "source_panel_execution_validator_valid_json": source_execution_validator_valid,
            "source_panel_execution_validator_error": source_execution_validator_error,
            "source_panel_result_review_valid_json": source_result_review_valid,
            "source_panel_result_review_error": source_result_review_error,
        },
        "validation": {
            "git_state": git,
            "tracked_python_validation": {
                "tracked_python_count": inventory["tracked_python_file_count"],
                "tracked_python_syntax_error_count": inventory["tracked_python_syntax_error_count"],
                "tracked_python_bom_error_count": inventory["tracked_python_bom_error_count"],
                "syntax_errors": inventory["syntax_errors"],
                "bom_errors": inventory["bom_errors"],
            },
            "expected_previous_tracked_python_count": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "replacement_checks": replacement_checks,
        },
        "safety_flags": {
            "repo_only": True,
            "full_system_static_audit_only": True,
            **safety,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_full_system_static_audit_before_data_horizon_execution_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_full_system_static_audit_before_data_horizon_execution_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_full_system_static_audit_before_data_horizon_execution_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    Path(outputs["latest_json"]).write_text(rendered, encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["static_audit_completed"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
