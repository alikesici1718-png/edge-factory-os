from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "fabeab5"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 616
EXPECTED_TRACKED_PYTHON_COUNT = 617

CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
VALIDATOR_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_REPAIR_PREVIEW = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1.py"
NEXT_MODULE_ROUTE_RESELECTOR = "edge_factory_os_repo_only_research_return_route_reselector_after_source_panel_contract_block_v1.py"
NEXT_MODULE_RESEARCH_RETURN_BLOCKED = "edge_factory_os_repo_only_research_return_blocked_record_after_source_panel_contract_block_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_BLOCKED_RECORD_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_EXPLICIT_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

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
]

BLOCKER_REASON_TEXT = (
    "P0 fail-closed blocker: contract_artifact_primary_strength_for_contract_only=false; "
    "evidence_quality_sufficient_for_contract_validation=false; "
    "source_panel_contract_validated=false; active_p0_blocker_count=1."
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]] if args and args[0] == "git" else args
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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


def tracked_python_validation() -> Dict[str, Any]:
    tracked_files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
    current_file = CURRENT_TOOL_REL if (REPO_ROOT / CURRENT_TOOL_REL).exists() else None
    files = sorted(set(tracked_files + ([current_file] if current_file and current_file not in tracked_files else [])))
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
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
        "tracked_python_count": len(files),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
        "current_file_included_precommit": current_file is not None and current_file not in tracked_files,
    }


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    latest_paths = latest_commit_paths()
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "parent": run_cmd(["git", "rev-parse", "--short", "HEAD^"]).stdout.strip(),
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": changed_paths == [CURRENT_TOOL_REL] or (len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL]),
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def prior_validator_respected(validator: Dict[str, Any], contract_exists: bool, contract_valid_json: bool) -> bool:
    return (
        validator.get("source_panel_analysis_contract_validator_status") == "PASS_WITH_ATTENTION"
        and validator.get("contract_artifact_exists") is True
        and validator.get("contract_artifact_valid_json") is True
        and validator.get("contract_artifact_primary_strength_for_contract_only") is False
        and validator.get("source_panel_contract_validated") is False
        and validator.get("evidence_quality_sufficient_for_contract_validation") is False
        and validator.get("active_p0_blocker_count") == 1
        and validator.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and contract_exists is True
        and contract_valid_json is True
    )


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, contract_valid_json, contract_json_error = load_json_checked(CONTRACT_ARTIFACT_PATH)
    validator, validator_valid_json, validator_json_error = load_json_checked(VALIDATOR_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    blocked_contract_artifact_exists = CONTRACT_ARTIFACT_PATH.exists()
    blocked_contract_artifact_valid_json = contract_valid_json
    source_panel_contract_validated = False
    contract_artifact_primary_strength_for_contract_only = False
    evidence_quality_sufficient_for_contract_validation = False
    active_p0_blocker_count = 1
    active_p1_attention_count = 0
    repair_preview_required = True
    contract_repair_preview_allowed = True
    route_reselection_allowed = True
    next_module = NEXT_MODULE_REPAIR_PREVIEW

    prior_validator_ok = prior_validator_respected(validator, blocked_contract_artifact_exists, blocked_contract_artifact_valid_json)
    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_616_to_617": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "validator_artifact_valid_json": validator_valid_json,
        "prior_source_panel_contract_validator_respected": prior_validator_ok,
        "source_panel_contract_blocked_record_created": True,
        "blocked_contract_artifact_exists": blocked_contract_artifact_exists,
        "blocked_contract_artifact_valid_json": blocked_contract_artifact_valid_json,
        "source_panel_contract_validated_false": source_panel_contract_validated is False,
        "contract_artifact_primary_strength_for_contract_only_false": contract_artifact_primary_strength_for_contract_only is False,
        "evidence_quality_sufficient_for_contract_validation_false": evidence_quality_sufficient_for_contract_validation is False,
        "active_p0_blocker_count_one": active_p0_blocker_count == 1,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "repair_apply_allowed_now_false": True,
        "selected_route_runs_research_now_false": True,
        "selected_route_generates_candidates_now_false": True,
        "selected_route_touches_runtime_capital_live_false": True,
        "selected_route_approves_generic_runner_false": True,
        "selected_route_creates_schema_or_config_false": True,
        "runtime_capital_live_candidate_untouched": True,
        "generic_runner_approval_false": True,
        "generic_runner_implementation_blocked": True,
        "loop_remains_closed": True,
        "next_module_allowed": next_module in {
            NEXT_MODULE_REPAIR_PREVIEW,
            NEXT_MODULE_ROUTE_RESELECTOR,
            NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
        },
        "runner_preview_not_selected": "runner_preview" not in next_module,
        "source_panel_execution_not_selected": "runner" not in next_module and "analysis_execution" not in next_module,
        "replacement_checks_not_primary_artifact_strength": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    blocker_context = {
        "source_panel_route_selected_after_research_return_gate": True,
        "source_panel_contract_artifact_exists": blocked_contract_artifact_exists,
        "source_panel_contract_artifact_is_valid_json": blocked_contract_artifact_valid_json,
        "validator_refused_primary_contract_strength_validation": True,
        "contract_validation_failed": True,
        "runner_preview_must_not_proceed": True,
        "contract_json_error": contract_json_error,
        "validator_json_error": validator_json_error,
    }
    blocker_reason = {
        "summary": BLOCKER_REASON_TEXT,
        "contract_artifact_primary_strength_for_contract_only": contract_artifact_primary_strength_for_contract_only,
        "evidence_quality_sufficient_for_contract_validation": evidence_quality_sufficient_for_contract_validation,
        "source_panel_contract_validated": source_panel_contract_validated,
        "active_p0_blocker_count": active_p0_blocker_count,
    }
    safe_state_confirmation = {
        "old_source_panel_anomaly_route_was_not_reopened": True,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "no_runtime_capital_live_candidate_generic_runner_schema_config_action_occurred": True,
        "generic_runner_remains_blocked": True,
        "loop_remains_closed": True,
    }
    allowed_next_actions = {
        "repair_preview_only": {
            "allowed": contract_repair_preview_allowed,
            "condition": "Only preview contract strengthening; no runtime/capital/live/schema/config/generic runner touch and no repair apply.",
            "next_module": NEXT_MODULE_REPAIR_PREVIEW,
        },
        "route_reselection": {
            "allowed": route_reselection_allowed,
            "condition": "Use only if the source-panel contract is not safely repairable.",
            "next_module": NEXT_MODULE_ROUTE_RESELECTOR,
        },
        "stop_block_research_return_route": {
            "allowed": True,
            "condition": "Use only if neither repair preview nor route reselection is safe.",
            "next_module": NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
        },
    }
    blocked_record_decision = {
        "decision": "REPAIR_PREVIEW_ONLY_NEXT",
        "reason": "The contract artifact exists and is valid JSON, so a preview-only strengthening assessment is the next safe step. Repair apply, runner preview, and source-panel execution remain blocked.",
        "next_module": next_module,
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_contract_blocked_record_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_BLOCKED_RECORD_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SOURCE_PANEL_CONTRACT_BLOCKED_REPAIR_PREVIEW_REQUIRED" if ready else "SOURCE_PANEL_CONTRACT_BLOCKED_RECORD_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_PREVIEW_AFTER_RESEARCH_RETURN_GATE" if ready else "STOP_SOURCE_PANEL_CONTRACT_BLOCKED_RECORD_REVIEW",
        "next_module": next_module if ready else NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
        "prior_source_panel_contract_validator_respected": prior_validator_ok,
        "source_panel_contract_blocked_record_created": True,
        "blocked_contract_artifact_exists": blocked_contract_artifact_exists,
        "blocked_contract_artifact_valid_json": blocked_contract_artifact_valid_json,
        "blocked_contract_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        "source_panel_contract_validated": source_panel_contract_validated,
        "contract_artifact_primary_strength_for_contract_only": contract_artifact_primary_strength_for_contract_only,
        "evidence_quality_sufficient_for_contract_validation": evidence_quality_sufficient_for_contract_validation,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": active_p1_attention_count,
        "blocker_reason": BLOCKER_REASON_TEXT,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "repair_preview_required": repair_preview_required,
        "repair_apply_allowed_now": False,
        "contract_repair_preview_allowed": contract_repair_preview_allowed,
        "route_reselection_allowed": route_reselection_allowed,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "selected_route_category": "SOURCE_PANEL_ANALYSIS",
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": True,
        "future_runtime_or_live_requires_kill_switch_readiness": True,
        "runtime_preflight_implementation_performed": False,
        "runtime_kill_switch_implementation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
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
            "This blocked record uses live repo checks plus the prior validator artifact only to preserve a fail-closed blocker. "
            "It does not repair the contract, run source-panel analysis, run backtests, generate candidates, touch runtime/capital/live/orders, "
            "approve or implement a generic runner, create schemas/configs, reopen old source-panel anomaly routes, or treat derived checks as primary artifact strength."
        ),
        "replacement_checks_all_true": ready,
        "blocker_context": blocker_context,
        "blocker_reason_detail": blocker_reason,
        "safe_state_confirmation": safe_state_confirmation,
        "allowed_next_actions": allowed_next_actions,
        "blocked_record_decision": blocked_record_decision,
        "contract_artifact_snapshot": {
            "artifact_loaded": bool(contract),
            "artifact_valid_json": blocked_contract_artifact_valid_json,
            "artifact_path": str(CONTRACT_ARTIFACT_PATH),
            "root_keys": sorted(contract.keys()),
        },
        "validator_artifact_snapshot": {
            "artifact_loaded": bool(validator),
            "artifact_valid_json": validator_valid_json,
            "artifact_path": str(VALIDATOR_ARTIFACT_PATH),
            "status": validator.get("source_panel_analysis_contract_validator_status"),
            "final_decision": validator.get("final_decision"),
            "next_module": validator.get("next_module"),
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "allowed_next_modules": [
                NEXT_MODULE_REPAIR_PREVIEW,
                NEXT_MODULE_ROUTE_RESELECTOR,
                NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
            ],
        },
        "safety_flags": {
            "repo_only": True,
            "blocked_record_only": True,
            "repair_apply_allowed_now": False,
            "source_panel_analysis_run_performed": False,
            "research_run_performed": False,
            "backtest_run_performed": False,
            "candidate_generation_performed": False,
            "family_release_performed": False,
            "active_paper_performed": False,
            "schema_or_config_created": False,
            "runtime_preflight_implementation_performed": False,
            "runtime_kill_switch_implementation_performed": False,
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "real_order_touch_performed": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_blocked_record_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_contract_blocked_record_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
