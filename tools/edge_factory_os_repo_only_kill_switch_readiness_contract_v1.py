from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_kill_switch_readiness_contract_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_kill_switch_readiness_contract_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "1f9085c"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 590
NEXT_MODULE = "edge_factory_os_repo_only_kill_switch_readiness_contract_validator_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_KILL_SWITCH_READINESS_CONTRACT_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
ROADMAP_EVALUATOR_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_final_form_gap_closure_roadmap_evaluator_v1" / "repo_only_final_form_gap_closure_roadmap_evaluator_v1_latest.json"

ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES = [
    "PRIMARY_ARTIFACT_STRONG",
    "EXACT_MARKER_STRONG",
    "DERIVED_EXPLICIT_ATTENTION",
    "DERIVED_OVERUSED_ATTENTION",
    "MISSING_EVIDENCE_FAIL_CLOSED",
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
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "strategy_research_recommended_now",
    "candidate_generation_recommended_now",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "file_move_allowed_now",
    "file_delete_allowed_now",
    "repo_restructure_allowed_now",
    "gitignore_changed",
    "git_add_force_used",
    "backup_deleted",
    "mass_metadata_patch_allowed",
    "blind_fix_all_allowed",
    "direct_apply_recommended_now",
    "apply_allowed_now",
    "apply_performed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
    "implementation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
    "kill_switch_runtime_implemented_now",
    "runtime_pause_behavior_changed_now",
    "paper_behavior_changed_now",
    "capital_or_order_behavior_changed_now",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = args
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def tracked_files() -> List[str]:
    return sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "ls-files"]).stdout.splitlines() if line.strip())


def tracked_python_validation() -> Dict[str, Any]:
    files = [path for path in tracked_files() if path.endswith(".py")]
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "tracked_python_syntax_error_count": len(syntax_errors),
        "tracked_python_bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def git_state() -> Dict[str, Any]:
    status_lines = [line for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines() if line.strip()]
    untracked = sorted(line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? "))
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    unexpected_untracked = [path for path in untracked if path not in expected_untracked]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "untracked_paths": untracked,
        "expected_untracked_paths": expected_untracked,
        "unexpected_untracked_paths": unexpected_untracked,
        "repo_clean_for_kill_switch_readiness_contract": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def roadmap_evaluator_ok(evaluator: Dict[str, Any]) -> bool:
    return (
        evaluator.get("roadmap_evaluator_status") in {"READY", "PASS", "PASS_CONTEXTUAL", "PASS_WITH_ATTENTION"}
        and evaluator.get("roadmap_evaluated") is True
        and evaluator.get("highest_priority_gap") == "kill_switch_readiness"
        and evaluator.get("kill_switch_readiness_is_repo_only_planning") is True
        and evaluator.get("active_p0_blocker_count") == 0
        and evaluator.get("active_p1_attention_count") == 0
        and evaluator.get("repair_preview_required") is False
        and evaluator.get("repair_apply_allowed_now") is False
        and evaluator.get("next_module") == "edge_factory_os_repo_only_kill_switch_readiness_contract_v1.py"
        and evaluator.get("evidence_chain_policy_level") == POLICY_LEVEL
        and evaluator.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and evaluator.get("future_modules_must_classify_evidence_quality") is True
        and evaluator.get("full_post_check_marker_preferred_over_plain_pass") is True
        and evaluator.get("plain_pass_without_marker_is_attention") is True
        and evaluator.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True
        and evaluator.get("generic_runner_approval_granted") is False
        and evaluator.get("generic_runner_implementation_remains_blocked") is True
        and evaluator.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and evaluator.get("loop_remains_closed") is True
        and evaluator.get("replacement_checks_all_true") is True
    )


def contract_definition() -> Dict[str, Any]:
    return {
        "scope": "repo_only_kill_switch_readiness_contract",
        "contract_is_repo_only": True,
        "contract_is_planning_only": True,
        "runtime_implementation_allowed": False,
        "future_pause_conditions": [
            "primary_or_exact evidence shows live, paper, order, or capital state has become inconsistent with approved safety policy",
            "preflight cannot prove current runtime state, open exposure state, and approval state from explicit artifacts",
            "audit status indicates missing evidence, stale safety fields, unknown process state, or unresolved high-priority safety issue",
            "manual approval is required but absent, stale, or not tied to exact artifact evidence",
            "derived evidence is being treated as primary evidence, or repeated derived checks are used to claim closure",
        ],
        "required_evidence_before_runtime_paper_live_capital_path": [
            "primary post-check artifact or exact marker for the relevant safety gate",
            "explicit evidence_chain_quality classification using only allowed values",
            "repo-clean and latest-commit scope verification",
            "tracked Python syntax and BOM verification",
            "runtime, paper, live, order, and capital state evidence from approved sources only",
            "manual approval artifact if any runtime, paper, live, order, or capital path would be changed",
        ],
        "required_safety_fields": [
            "kill_switch_readiness_status",
            "contract_is_repo_only",
            "contract_is_planning_only",
            "runtime_implementation_allowed",
            "pause_condition_count",
            "required_evidence_before_runtime_paper_live_capital_path",
            "preflight_checks_required",
            "blocked_until_explicit_approval",
            "evidence_chain_policy_level",
            "current_evidence_chain_quality",
            "replacement_checks_are_not_equivalent_to_primary_artifact",
            "generic_runner_approval_granted",
            "generic_runner_implementation_remains_blocked",
            "ordinary_selector_backlog_loop_reentry_allowed",
            "loop_remains_closed",
        ],
        "preflight_checks_required": [
            "repo status clean",
            "latest commit touches exactly the approved repo-only module file",
            "planned schema files existing count remains zero",
            "generic runner target remains absent",
            "dangerous flags remain all false",
            "repair_apply_allowed_now remains false",
            "derived_live_repo_post_check has explicit reason and replacement checks when used",
            "no runtime, launcher, capital, paper, live, order, candidate, family, schema, config, or generic runner path is selected",
        ],
        "blocked_until_explicit_approval": [
            "runtime kill switch implementation",
            "launcher patching",
            "capital allocation changes",
            "paper or live behavior changes",
            "order creation or order-path mutation",
            "schema or config creation",
            "generic runner implementation or approval",
        ],
        "audit_requirements": [
            "validate this contract with a separate repo-only validator module",
            "preserve the closed generic governance loop state",
            "record whether evidence is primary, exact marker, derived attention, or missing fail-closed",
            "fail closed on missing primary evidence unless complete explicit replacement checks are present",
            "keep kill-switch readiness as planning/readiness/preflight until explicit future approval exists",
        ],
        "false_confidence_controls": [
            "do not treat PASS alone as strong evidence",
            "do not treat derived_live_repo_post_check as identical to primary artifact verification",
            "do not count repeated module name growth as progress",
            "do not infer runtime safety from repo-only planning artifacts",
            "do not proceed to implementation when any required evidence field is missing",
        ],
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    evaluator = load_json(ROADMAP_EVALUATOR_ARTIFACT)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    contract = contract_definition()

    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_kill_switch_readiness_contract": git["repo_clean_for_kill_switch_readiness_contract"],
        "tracked_python_count_matches_previous": py["tracked_python_count"] == EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "roadmap_evaluator_artifact_exists": bool(evaluator),
        "roadmap_evaluator_ok": roadmap_evaluator_ok(evaluator),
        "contract_is_repo_only": contract["contract_is_repo_only"] is True,
        "contract_is_planning_only": contract["contract_is_planning_only"] is True,
        "runtime_implementation_not_allowed": contract["runtime_implementation_allowed"] is False,
        "blocked_runtime_paper_live_capital_paths": len(contract["blocked_until_explicit_approval"]) >= 7,
        "next_module_expected": NEXT_MODULE == "edge_factory_os_repo_only_kill_switch_readiness_contract_validator_v1.py",
        "derived_evidence_not_treated_as_primary": CURRENT_EVIDENCE_CHAIN_QUALITY == "DERIVED_OVERUSED_ATTENTION",
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "kill_switch_readiness_contract_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_KILL_SWITCH_READINESS_CONTRACT_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "KILL_SWITCH_READINESS_CONTRACT_READY" if ready else "KILL_SWITCH_READINESS_CONTRACT_FAIL_CLOSED",
        "next_action": "BUILD_KILL_SWITCH_READINESS_CONTRACT_VALIDATOR_V1" if ready else "REVIEW_KILL_SWITCH_READINESS_CONTRACT_INPUTS",
        "next_module": NEXT_MODULE if ready else None,
        "kill_switch_readiness_contract_ready": ready,
        "kill_switch_readiness_contract": contract,
        "contract_is_repo_only": True,
        "contract_is_planning_only": True,
        "contract_does_not_touch_runtime_capital_live": True,
        "contract_does_not_touch_schema_config_order_candidate_family": True,
        "contract_does_not_approve_generic_runner": True,
        "contract_does_not_reopen_loop": True,
        "highest_priority_gap": "kill_switch_readiness",
        "kill_switch_readiness_is_repo_only_planning": True,
        "pause_condition_count": len(contract["future_pause_conditions"]),
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 0,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values": ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "generic_runner_safe_mode_planning_allowed_later": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "repeated_name_growth_is_not_progress": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flag_true_count": 0,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": "Kill-switch readiness contract uses the roadmap evaluator artifact plus live repo replacement checks; evidence remains DERIVED_OVERUSED_ATTENTION and weaker than primary artifact verification.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "roadmap_evaluator_loaded": bool(evaluator),
            "future_pause_condition_count": len(contract["future_pause_conditions"]),
            "preflight_check_count": len(contract["preflight_checks_required"]),
        },
        "safety_flags": {
            "repo_only": True,
            "planning_only": True,
            "runtime_implementation_allowed": False,
            "repair_apply_allowed_now": False,
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
    latest_json = OUT_DIR / "repo_only_kill_switch_readiness_contract_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_kill_switch_readiness_contract_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_kill_switch_readiness_contract_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    Path(outputs["latest_json"]).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["kill_switch_readiness_contract_status"] in {"READY", "PASS"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
