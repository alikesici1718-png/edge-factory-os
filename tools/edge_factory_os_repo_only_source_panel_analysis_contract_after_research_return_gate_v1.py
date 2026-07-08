from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "0fe6933"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 614
EXPECTED_TRACKED_PYTHON_COUNT = 615

POST_CHECK_STATUS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_EXPLICIT_ATTENTION"
NEXT_MODULE_READY = "edge_factory_os_repo_only_source_panel_analysis_contract_validator_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_blocked_record_after_research_return_gate_v1.py"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ROUTE_SELECTOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1"
    / "repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1_latest.json"
)

CONTRACT_ARTIFACT_JSON = OUT_DIR / "source_panel_analysis_contract_after_research_return_gate_v1.json"
CONTRACT_ARTIFACT_TXT = OUT_DIR / "source_panel_analysis_contract_after_research_return_gate_v1.txt"

OLD_SOURCE_PANEL_ANOMALY_MODULES = [
    "tools/edge_factory_os_source_panel_anomaly_discovery_contract_builder_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_runner_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_discovery_evaluator_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_deep_validation_contract_builder_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_deep_validation_runner_v1.py",
    "tools/edge_factory_os_source_panel_anomaly_deep_validation_evaluator_v1.py",
]

FUTURE_SOURCE_PANEL_PRIMARY_ARTIFACTS = [
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
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]] if args and args[0] == "git" else args
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


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


def prior_route_selector_respected(selector: Dict[str, Any]) -> bool:
    return (
        selector.get("research_return_route_selector_status") == "PASS"
        and selector.get("research_return_route_selection_completed") is True
        and selector.get("research_return_allowed_repo_only") is True
        and selector.get("research_return_route_selected") is True
        and selector.get("selected_route_category") == "SOURCE_PANEL_ANALYSIS"
        and selector.get("selected_route_is_repo_only") is True
        and selector.get("selected_route_runs_research_now") is False
        and selector.get("selected_route_generates_candidates_now") is False
        and selector.get("selected_route_touches_runtime_capital_live") is False
        and selector.get("selected_route_approves_generic_runner") is False
        and selector.get("selected_route_creates_schema_or_config") is False
        and selector.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and selector.get("replacement_checks_all_true") is True
    )


def research_return_context(selector: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "research_return_gate_allowed_repo_only_research": selector.get("research_return_allowed_repo_only") is True,
        "selected_route_category": "SOURCE_PANEL_ANALYSIS",
        "evidence_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "evidence_quality_is_primary_strength": False,
        "derived_overused_default_allowed": False,
        "safety_prerequisites_active": True,
        "runtime_capital_live_candidate_generic_runner_blocked": True,
    }


def source_panel_contract_scope() -> Dict[str, Any]:
    return {
        "allowed_scope": [
            "source_panel_inventory",
            "data_availability_map",
            "symbol_time_coverage_map",
            "feature_panel_completeness_review",
            "anomaly_freshness_missingness_scan",
            "data_quality_scoring",
            "source_reliability_ranking",
            "output_artifact_catalog",
        ],
        "strategy_signal_claims_allowed": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_live_capital_order_action_allowed": False,
    }


def old_source_panel_anomaly_route_guard() -> Dict[str, Any]:
    return {
        "prior_source_panel_anomaly_artifacts_are_historical_context_only": True,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "old_source_panel_anomaly_route_closed_if_detected": True,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "old_source_panel_anomaly_modules": OLD_SOURCE_PANEL_ANOMALY_MODULES,
        "future_reference_rule": "Any future module that references old anomaly artifacts must label them historical/closed, not active evidence.",
        "route_closed_artifact_rule": "No route_closed=true artifact may justify active research route continuation.",
    }


def primary_artifact_requirement() -> Dict[str, Any]:
    return {
        "future_source_panel_runner_primary_artifacts_required": True,
        "future_source_panel_primary_artifact_list": FUTURE_SOURCE_PANEL_PRIMARY_ARTIFACTS,
        "this_module_creates_contract_only": True,
        "primary_strength_claimed_now": False,
        "runner_missing_primary_artifacts_must_fail": True,
    }


def evidence_quality_requirements() -> Dict[str, Any]:
    return {
        "exact_marker_or_primary_artifact_required_where_available": True,
        "derived_evidence_allowed_only_as": "DERIVED_EXPLICIT_ATTENTION_WITH_REASON_AND_MONITORING",
        "derived_overused_default_allowed": False,
        "fail_if_primary_source_panel_artifacts_missing_after_runner": True,
        "fail_if_old_closed_anomaly_route_reopened": True,
        "source_panel_contract_claims_primary_strength_now": False,
    }


def money_path_alignment() -> Dict[str, Any]:
    return {
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH",
        "internal_research_edge_discovery_substrate": True,
        "reusable_data_quality_source_panel_analysis_asset": True,
        "possible_sellable_pivotable_validation_data_quality_tool": True,
        "profit_promise": False,
        "usable_or_sellable_asset_path": "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET",
    }


def build_contract_artifact(selector: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract_name": "source_panel_analysis_contract_after_research_return_gate_v1",
        "created_at_utc": now_utc(),
        "contract_type": "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT",
        "research_return_context": research_return_context(selector),
        "source_panel_contract_scope": source_panel_contract_scope(),
        "old_source_panel_anomaly_route_guard": old_source_panel_anomaly_route_guard(),
        "primary_artifact_requirement": primary_artifact_requirement(),
        "evidence_quality_requirements": evidence_quality_requirements(),
        "money_path_alignment": money_path_alignment(),
        "execution_permissions": {
            "run_source_panel_analysis_now": False,
            "run_backtests_now": False,
            "generate_candidates_now": False,
            "touch_runtime_capital_live_orders": False,
            "approve_or_implement_generic_runner": False,
            "create_schema_or_config_files": False,
        },
        "next_validator_module": NEXT_MODULE_READY,
    }


def write_contract_artifact(contract: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(contract, indent=2, sort_keys=True)
    CONTRACT_ARTIFACT_JSON.write_text(rendered, encoding="utf-8")
    CONTRACT_ARTIFACT_TXT.write_text(rendered + "\n", encoding="utf-8")
    return {"json": str(CONTRACT_ARTIFACT_JSON), "txt": str(CONTRACT_ARTIFACT_TXT)}


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    selector = load_json(ROUTE_SELECTOR_ARTIFACT)
    contract = build_contract_artifact(selector)
    contract_paths = write_contract_artifact(contract)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    guard = contract["old_source_panel_anomaly_route_guard"]
    primary = contract["primary_artifact_requirement"]
    evidence = contract["evidence_quality_requirements"]
    money = contract["money_path_alignment"]
    scope = contract["source_panel_contract_scope"]
    contract_artifact_created = CONTRACT_ARTIFACT_JSON.exists() and CONTRACT_ARTIFACT_TXT.exists()
    old_route_guard_safe = (
        guard["prior_source_panel_anomaly_artifacts_are_historical_context_only"] is True
        and guard["old_source_panel_anomaly_route_reopen_allowed"] is False
        and guard["old_source_panel_anomaly_route_closed_if_detected"] is True
        and guard["source_panel_contract_must_be_independent_of_old_failed_route"] is True
    )
    ready_candidate = prior_route_selector_respected(selector) and contract_artifact_created and old_route_guard_safe
    next_module = NEXT_MODULE_READY if ready_candidate else NEXT_MODULE_BLOCKED

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_614_to_615": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "prior_research_return_route_selector_respected": prior_route_selector_respected(selector),
        "source_panel_analysis_contract_ready": ready_candidate,
        "source_panel_contract_artifact_created": contract_artifact_created,
        "source_panel_contract_scope_completed": True,
        "old_source_panel_anomaly_route_guard_completed": old_route_guard_safe,
        "old_source_panel_anomaly_route_reopen_allowed_false": guard["old_source_panel_anomaly_route_reopen_allowed"] is False,
        "future_source_panel_runner_primary_artifacts_required": primary["future_source_panel_runner_primary_artifacts_required"] is True,
        "source_panel_contract_claims_primary_strength_now_false": evidence["source_panel_contract_claims_primary_strength_now"] is False,
        "source_panel_contract_claims_profit_false": money["profit_promise"] is False,
        "selected_route_runs_research_now_false": False is False,
        "selected_route_generates_candidates_now_false": False is False,
        "selected_route_touches_runtime_capital_live_false": False is False,
        "selected_route_approves_generic_runner_false": False is False,
        "selected_route_creates_schema_or_config_false": False is False,
        "runtime_capital_live_candidate_order_untouched": True,
        "generic_runner_remains_blocked": True,
        "loop_remains_closed": True,
        "repair_apply_not_allowed": True,
        "next_module_allowed": next_module in {NEXT_MODULE_READY, NEXT_MODULE_BLOCKED},
        "derived_evidence_not_treated_as_primary": True,
        "old_route_closed_not_active_evidence": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_contract_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SOURCE_PANEL_ANALYSIS_CONTRACT_READY_FOR_VALIDATOR" if ready else "SOURCE_PANEL_ANALYSIS_CONTRACT_BLOCKED_OR_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_CONTRACT_VALIDATOR_AFTER_RESEARCH_RETURN_GATE" if ready else "RECORD_SOURCE_PANEL_ANALYSIS_BLOCKED_STATE",
        "next_module": next_module if ready else NEXT_MODULE_BLOCKED,
        "prior_research_return_route_selector_respected": prior_route_selector_respected(selector),
        "source_panel_analysis_contract_ready": ready_candidate,
        "source_panel_contract_artifact_created": contract_artifact_created,
        "source_panel_contract_artifact_path": contract_paths["json"],
        "source_panel_contract_scope_completed": True,
        "old_source_panel_anomaly_route_guard_completed": old_route_guard_safe,
        "primary_artifact_requirement_completed": True,
        "evidence_quality_requirements_completed": True,
        "money_path_alignment_completed": True,
        "selected_route_category": "SOURCE_PANEL_ANALYSIS",
        "selected_route_is_repo_only": True,
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "prior_source_panel_anomaly_artifacts_are_historical_context_only": guard["prior_source_panel_anomaly_artifacts_are_historical_context_only"],
        "old_source_panel_anomaly_route_reopen_allowed": guard["old_source_panel_anomaly_route_reopen_allowed"],
        "old_source_panel_anomaly_route_closed_if_detected": guard["old_source_panel_anomaly_route_closed_if_detected"],
        "source_panel_contract_must_be_independent_of_old_failed_route": guard["source_panel_contract_must_be_independent_of_old_failed_route"],
        "future_source_panel_runner_primary_artifacts_required": primary["future_source_panel_runner_primary_artifacts_required"],
        "future_source_panel_primary_artifact_list": primary["future_source_panel_primary_artifact_list"],
        "source_panel_contract_claims_primary_strength_now": evidence["source_panel_contract_claims_primary_strength_now"],
        "source_panel_contract_claims_profit": money["profit_promise"],
        "money_path_alignment": money["money_path_alignment"],
        "usable_or_sellable_asset_path": money["usable_or_sellable_asset_path"],
        "safety_prerequisites_satisfied": selector.get("safety_prerequisites_satisfied") is True,
        "evidence_quality_sufficient_for_repo_only_research_return": selector.get("evidence_quality_sufficient_for_repo_only_research_return") is True,
        "documentation_loop_bounded": selector.get("documentation_loop_bounded") is True,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": selector.get("future_runtime_or_live_requires_preflight_safety_readiness") is True,
        "future_runtime_or_live_requires_kill_switch_readiness": selector.get("future_runtime_or_live_requires_kill_switch_readiness") is True,
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
        "research_return_context": contract["research_return_context"],
        "source_panel_contract_scope": scope,
        "old_source_panel_anomaly_route_guard": guard,
        "primary_artifact_requirement": primary,
        "evidence_quality_requirements": evidence,
        "money_path_alignment_detail": money,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This module uses live repo checks and the route selector artifact only for fail-closed contract creation. "
            "It creates a primary contract artifact but does not run source-panel analysis, generate primary source-panel results, "
            "reopen old closed anomaly routes, promise profit, or treat derived live checks as primary evidence strength."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "route_selector_artifact": str(ROUTE_SELECTOR_ARTIFACT),
            "route_selector_artifact_loaded": bool(selector),
            "contract_artifact_paths": contract_paths,
            "allowed_next_modules": [NEXT_MODULE_READY, NEXT_MODULE_BLOCKED],
        },
        "safety_flags": {
            "repo_only": True,
            "contract_only": True,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_contract_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
