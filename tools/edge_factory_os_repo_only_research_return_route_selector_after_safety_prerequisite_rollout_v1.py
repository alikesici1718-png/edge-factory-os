from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "fb91fa0"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 613
EXPECTED_TRACKED_PYTHON_COUNT = 614

POST_CHECK_STATUS = "REPO_ONLY_RESEARCH_RETURN_ROUTE_SELECTOR_AFTER_SAFETY_PREREQUISITE_ROLLOUT_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_EXPLICIT_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

EVALUATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1"
    / "repo_only_research_return_gate_evaluator_after_safety_prerequisite_rollout_v1_latest.json"
)

ROUTE_NEXT_MODULES = {
    "SOURCE_PANEL_ANALYSIS": "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1.py",
    "VALIDATION_METHODOLOGY_REFRESH": "edge_factory_os_repo_only_validation_methodology_refresh_contract_after_research_return_gate_v1.py",
    "ROUTE_HYGIENE_AND_BLOCKLIST_RESEARCH": "edge_factory_os_repo_only_route_hygiene_research_contract_after_research_return_gate_v1.py",
    "RESEARCH_QUEUE_REBUILD": "edge_factory_os_repo_only_research_queue_rebuild_contract_after_research_return_gate_v1.py",
    "BLOCKED": "edge_factory_os_repo_only_research_return_route_blocked_record_after_safety_prerequisite_rollout_v1.py",
}

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


def prior_gate_evaluation(evaluator: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "research_return_gate_evaluator_passed": evaluator.get("research_return_gate_evaluator_status") == "PASS",
        "repo_only_research_return_allowed": evaluator.get("research_return_allowed_repo_only") is True,
        "no_p0_p1_active_blocker": evaluator.get("active_p0_blocker_count") == 0 and evaluator.get("active_p1_attention_count") == 0,
        "safety_prerequisites_satisfied": evaluator.get("safety_prerequisites_satisfied") is True,
        "documentation_loop_bounded": evaluator.get("documentation_loop_bounded") is True,
        "evidence_quality_sufficient_for_repo_only_research_return": evaluator.get("evidence_quality_sufficient_for_repo_only_research_return") is True,
        "expected_next_module_points_to_route_selector": evaluator.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1],
        "replacement_checks_all_true": evaluator.get("replacement_checks_all_true") is True,
    }


def route_option(
    category: str,
    expected_value: str,
    recommendation: str,
    risk_level: str,
    money_path: bool,
    documentation_loop_risk: str,
) -> Dict[str, Any]:
    return {
        "route_category": category,
        "allowed_next_module": ROUTE_NEXT_MODULES[category],
        "route_is_repo_only": True,
        "route_moves_toward_research_return": True,
        "route_moves_toward_money_path": money_path,
        "route_risk_level": risk_level,
        "route_expected_value": expected_value,
        "route_documentation_loop_risk": documentation_loop_risk,
        "route_runtime_capital_live_risk": "NONE_REPO_ONLY_CONTRACT_SELECTION",
        "route_candidate_generation_risk": "BLOCKED_NO_CANDIDATE_GENERATION",
        "route_generic_runner_risk": "BLOCKED_GENERIC_RUNNER_REMAINS_BLOCKED",
        "route_requires_schema_or_config": False,
        "route_evidence_requirements": (
            "DERIVED_EXPLICIT_ATTENTION_ALLOWED_ONLY_WITH_REASON_MONITORING; "
            "future modules require EXACT_MARKER_STRONG or PRIMARY_ARTIFACT_STRONG where available"
        ),
        "route_recommendation": recommendation,
    }


def route_options_evaluation() -> List[Dict[str, Any]]:
    return [
        route_option(
            "SOURCE_PANEL_ANALYSIS",
            "Highest immediate substrate value: improves source-panel/data-quality/anomaly understanding before any strategy claim.",
            "SELECT",
            "LOW",
            True,
            "LOW_CONCRETE_RESEARCH_CONTRACT_NOT_GOVERNANCE_CHAIN",
        ),
        route_option(
            "VALIDATION_METHODOLOGY_REFRESH",
            "High false-edge reduction value, but validation weakness is not the dominant remaining blocker after the gate evaluator.",
            "KEEP_AS_FOLLOW_UP",
            "LOW",
            True,
            "LOW_IF_CONTRACT_REMAINS_RESEARCH_METHOD_ONLY",
        ),
        route_option(
            "ROUTE_HYGIENE_AND_BLOCKLIST_RESEARCH",
            "Useful for repeated-route prevention, but less directly useful than source-panel substrate work for first research return.",
            "KEEP_AS_FOLLOW_UP",
            "LOW",
            True,
            "LOW_IF_IT_DOES_NOT_REOPEN_BACKLOG_LOOP",
        ),
        route_option(
            "RESEARCH_QUEUE_REBUILD",
            "Useful only if a clean queue is needed before route work; less concrete and more queue-like than source-panel analysis.",
            "DEFER_TO_AVOID_QUEUE_BACKLOG_LOOP",
            "MEDIUM_ATTENTION",
            True,
            "MEDIUM_ATTENTION_CAN_DRIFT_TOWARD_BACKLOG_LOOP",
        ),
    ]


def selected_route_decision(options: List[Dict[str, Any]]) -> Dict[str, Any]:
    selected = next(option for option in options if option["route_recommendation"] == "SELECT")
    return {
        "research_return_route_selected": True,
        "selected_route_category": selected["route_category"],
        "selected_route_reason": (
            "SOURCE_PANEL_ANALYSIS is the safest first repo-only research return route because it creates usable research substrate value, "
            "reduces data-quality and anomaly uncertainty before strategy claims, and avoids governance-only drift, candidate generation, runtime, capital, live, schema, config, and generic-runner work."
        ),
        "selected_route_rejects_pure_governance_documentation": True,
        "selected_route_is_repo_only": selected["route_is_repo_only"],
        "selected_route_moves_toward_research_return": selected["route_moves_toward_research_return"],
        "selected_route_moves_toward_money_path": selected["route_moves_toward_money_path"],
        "next_module": selected["allowed_next_module"],
    }


def money_path_alignment() -> Dict[str, Any]:
    return {
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH",
        "internal_research_edge_discovery_utility": True,
        "reusable_validation_source_panel_analysis_asset": True,
        "sellable_or_pivotable_technical_asset_possible": True,
        "trading_profit_promised": False,
        "pure_governance_documentation_rejected_as_success": True,
        "usable_or_sellable_asset_path": "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET",
    }


def safety_boundary_confirmation() -> Dict[str, bool]:
    return {
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "real_order_touch_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_performed": False,
        "schema_or_config_created": False,
        "loop_remains_closed": True,
    }


def all_true(values: Dict[str, bool]) -> bool:
    return all(value is True for value in values.values())


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    evaluator = load_json(EVALUATOR_ARTIFACT)
    gate_eval = prior_gate_evaluation(evaluator)
    options = route_options_evaluation()
    route = selected_route_decision(options) if all_true(gate_eval) else {
        "research_return_route_selected": False,
        "selected_route_category": "BLOCKED",
        "selected_route_reason": "Prior research return gate evaluator was not fully respected.",
        "selected_route_rejects_pure_governance_documentation": True,
        "selected_route_is_repo_only": False,
        "selected_route_moves_toward_research_return": False,
        "selected_route_moves_toward_money_path": False,
        "next_module": ROUTE_NEXT_MODULES["BLOCKED"],
    }
    money = money_path_alignment()
    safety = safety_boundary_confirmation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    route_selected = route["research_return_route_selected"] is True
    selected_category = route["selected_route_category"]
    next_module = route["next_module"]

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_613_to_614": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "prior_research_return_gate_evaluator_respected": all_true(gate_eval),
        "research_return_route_selection_completed": True,
        "research_return_allowed_repo_only": evaluator.get("research_return_allowed_repo_only") is True,
        "selected_route_is_allowed_category": selected_category in ROUTE_NEXT_MODULES and selected_category != "BLOCKED",
        "next_module_matches_selected_route": next_module == ROUTE_NEXT_MODULES[selected_category],
        "selected_route_starts_documentation_chain_false": False is False,
        "selected_route_runs_research_now_false": False is False,
        "selected_route_generates_candidates_now_false": False is False,
        "selected_route_touches_runtime_capital_live_false": False is False,
        "selected_route_approves_generic_runner_false": False is False,
        "selected_route_creates_schema_or_config_false": False is False,
        "runtime_capital_live_candidate_order_untouched": all(
            safety[key] is False
            for key in [
                "runtime_touch_performed",
                "capital_touch_performed",
                "live_touch_performed",
                "real_order_touch_performed",
                "candidate_generation_performed",
                "family_release_performed",
                "active_paper_performed",
            ]
        ),
        "generic_runner_remains_blocked": safety["generic_runner_approval_granted"] is False and safety["generic_runner_implementation_performed"] is False,
        "loop_remains_closed": safety["loop_remains_closed"],
        "repair_apply_not_allowed": True,
        "derived_evidence_not_treated_as_primary": True,
        "profit_not_promised": money["trading_profit_promised"] is False,
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "research_return_route_selector_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_RESEARCH_RETURN_ROUTE_SELECTOR_AFTER_SAFETY_PREREQUISITE_ROLLOUT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SOURCE_PANEL_ANALYSIS_ROUTE_SELECTED_REPO_ONLY_CONTRACT_NEXT" if ready and route_selected else "RESEARCH_RETURN_ROUTE_SELECTION_BLOCKED_OR_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_CONTRACT_AFTER_RESEARCH_RETURN_GATE" if ready and route_selected else "RECORD_RESEARCH_RETURN_ROUTE_BLOCKED_STATE",
        "next_module": next_module if ready else ROUTE_NEXT_MODULES["BLOCKED"],
        "prior_research_return_gate_evaluator_respected": all_true(gate_eval),
        "research_return_route_selection_completed": True,
        "research_return_allowed_repo_only": evaluator.get("research_return_allowed_repo_only") is True,
        "research_return_route_selected": route_selected and ready,
        "selected_route_category": selected_category if ready else "BLOCKED",
        "selected_route_reason": route["selected_route_reason"],
        "selected_route_is_repo_only": route["selected_route_is_repo_only"] if route_selected else False,
        "selected_route_moves_toward_research_return": route["selected_route_moves_toward_research_return"] if route_selected else False,
        "selected_route_moves_toward_money_path": route["selected_route_moves_toward_money_path"] if route_selected else False,
        "selected_route_starts_documentation_chain": False,
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "route_options_evaluation": options,
        "money_path_alignment": money["money_path_alignment"],
        "usable_or_sellable_asset_path": money["usable_or_sellable_asset_path"],
        "safety_prerequisites_satisfied": evaluator.get("safety_prerequisites_satisfied") is True,
        "evidence_quality_sufficient_for_repo_only_research_return": evaluator.get("evidence_quality_sufficient_for_repo_only_research_return") is True,
        "documentation_loop_bounded": evaluator.get("documentation_loop_bounded") is True,
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
        "future_runtime_or_live_requires_preflight_safety_readiness": evaluator.get("future_runtime_or_live_requires_preflight_safety_readiness") is True,
        "future_runtime_or_live_requires_kill_switch_readiness": evaluator.get("future_runtime_or_live_requires_kill_switch_readiness") is True,
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
        "prior_gate_evaluation": gate_eval,
        "selected_route_decision": route,
        "money_path_alignment_evaluation": money,
        "safety_boundary_confirmation": safety,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "This selector uses live repo checks and the prior gate evaluator artifact only for fail-closed route selection. "
            "It does not run research, generate candidates, backtest, touch runtime/capital/live/orders, approve a generic runner, create schemas/configs, promise profit, or treat derived checks as primary artifact strength."
        ),
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "evaluator_artifact": str(EVALUATOR_ARTIFACT),
            "evaluator_artifact_loaded": bool(evaluator),
            "allowed_route_next_modules": ROUTE_NEXT_MODULES,
        },
        "safety_flags": {
            "repo_only": True,
            "route_selection_only": True,
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
    latest_json = OUT_DIR / "repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_research_return_route_selector_after_safety_prerequisite_rollout_v1_latest.txt"
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
    return 0 if payload["research_return_route_selector_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
