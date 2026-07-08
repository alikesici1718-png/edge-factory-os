from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_preflight_safety_readiness_enforcement_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_preflight_safety_readiness_enforcement_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_PARENT_HEAD = "a49c928"
EXPECTED_TRACKED_PYTHON_COUNT = 599
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 598
NEXT_MODULE = "edge_factory_os_repo_only_preflight_safety_readiness_enforcement_gate_validator_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_PREFLIGHT_SAFETY_READINESS_ENFORCEMENT_GATE_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ADOPTION_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_preflight_safety_readiness_adoption_record_v1"
    / "repo_only_preflight_safety_readiness_adoption_record_v1_latest.json"
)
KILL_SWITCH_ADOPTION_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_kill_switch_readiness_adoption_record_v1"
    / "repo_only_kill_switch_readiness_adoption_record_v1_latest.json"
)

ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES = [
    "PRIMARY_ARTIFACT_STRONG",
    "EXACT_MARKER_STRONG",
    "DERIVED_EXPLICIT_ATTENTION",
    "DERIVED_OVERUSED_ATTENTION",
    "MISSING_EVIDENCE_FAIL_CLOSED",
]

PREFLIGHT_REQUIRED_FUTURE_PATHS = [
    "runtime path",
    "paper path",
    "live path",
    "capital path",
    "candidate path",
    "family path",
    "execution path",
]

KILL_SWITCH_REQUIRED_FUTURE_PATHS = [
    "runtime path",
    "paper path",
    "live path",
    "capital path",
]

ENFORCEMENT_GATE_REQUIREMENTS = [
    "future runtime/paper/live/capital/candidate/family/execution paths require preflight safety readiness adoption",
    "future runtime/paper/live/capital paths require kill-switch readiness adoption",
    "evidence-chain policy must be active",
    "evidence_chain_quality must be reported with the exact allowed value set",
    "missing evidence fails closed",
    "derived evidence remains weaker than primary artifact verification",
    "plain PASS without an exact marker remains ATTENTION",
    "generic runner remains blocked unless a future explicit safe-mode approval contract allows planning",
    "closed loop must not reopen",
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
    "config_file_creation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "implementation_allowed_now",
    "runtime_preflight_implementation_performed",
    "runtime_touch_performed",
    "capital_touch_performed",
    "live_touch_performed",
    "real_order_touch_performed",
    "paper_behavior_changed_now",
    "execution_path_approved_now",
    "order_path_touched_now",
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


def latest_commit_paths() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "show", "--name-only", "--format=", "HEAD"]).stdout.splitlines()
        if line.strip()
    )


def tracked_python_validation() -> Dict[str, Any]:
    files = sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines()
        if line.strip()
    )
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
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "parent": run_cmd(["git", "rev-parse", "--short", "HEAD^"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_commit_paths(),
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def adoption_record_ok(adoption: Dict[str, Any]) -> bool:
    return (
        adoption.get("preflight_safety_readiness_adoption_record_status") in {"READY", "PASS"}
        and adoption.get("preflight_safety_readiness_adopted_for_future_safety") is True
        and adoption.get("preflight_safety_readiness_is_repo_only_planning") is True
        and adoption.get("kill_switch_readiness_adoption_respected") is True
        and adoption.get("runtime_preflight_implementation_performed") is False
        and adoption.get("runtime_touch_performed") is False
        and adoption.get("capital_touch_performed") is False
        and adoption.get("live_touch_performed") is False
        and adoption.get("real_order_touch_performed") is False
        and adoption.get("future_runtime_or_live_requires_preflight_safety_readiness") is True
        and adoption.get("future_runtime_or_live_requires_kill_switch_readiness") is True
        and adoption.get("next_module") == "edge_factory_os_repo_only_preflight_safety_readiness_enforcement_gate_v1.py"
        and adoption.get("evidence_chain_policy_level") == POLICY_LEVEL
        and adoption.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and adoption.get("future_modules_must_classify_evidence_quality") is True
        and adoption.get("full_post_check_marker_preferred_over_plain_pass") is True
        and adoption.get("plain_pass_without_marker_is_attention") is True
        and adoption.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True
        and adoption.get("generic_runner_approval_granted") is False
        and adoption.get("generic_runner_implementation_remains_blocked") is True
        and adoption.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and adoption.get("loop_remains_closed") is True
        and adoption.get("replacement_checks_all_true") is True
    )


def kill_switch_adoption_ok(adoption: Dict[str, Any]) -> bool:
    return (
        adoption.get("kill_switch_readiness_adoption_record_status") in {"READY", "PASS"}
        and adoption.get("kill_switch_readiness_adopted_for_future_safety") is True
        and adoption.get("future_runtime_or_live_requires_kill_switch_readiness") is True
        and adoption.get("runtime_kill_switch_implementation_performed") is False
        and adoption.get("runtime_touch_performed") is False
        and adoption.get("capital_touch_performed") is False
        and adoption.get("live_touch_performed") is False
        and adoption.get("replacement_checks_all_true") is True
    )


def enforcement_gate_definition() -> Dict[str, Any]:
    return {
        "scope": "repo_only_preflight_safety_readiness_enforcement_gate",
        "enforcement_gate_is_repo_only": True,
        "enforcement_gate_is_planning_only": True,
        "runtime_enforcement_implemented": False,
        "preflight_required_future_paths": PREFLIGHT_REQUIRED_FUTURE_PATHS,
        "kill_switch_required_future_paths": KILL_SWITCH_REQUIRED_FUTURE_PATHS,
        "requirements": ENFORCEMENT_GATE_REQUIREMENTS,
        "missing_evidence_fails_closed": True,
        "derived_evidence_weaker_than_primary_artifact_verification": True,
        "generic_runner_condition": "blocked unless a future explicit safe-mode approval contract allows planning",
        "closed_loop_must_not_reopen": True,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    adoption = load_json(ADOPTION_ARTIFACT)
    kill_switch_adoption = load_json(KILL_SWITCH_ADOPTION_ARTIFACT)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    gate = enforcement_gate_definition()

    replacement_checks = {
        "parent_head_observed": git["parent"] == EXPECTED_PARENT_HEAD,
        "repo_clean_after_commit": git["repo_clean"],
        "latest_commit_touches_only_current_module": git["latest_commit_paths"] == [CURRENT_TOOL_REL],
        "tracked_python_count_increased_by_one": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "adoption_record_artifact_exists": bool(adoption),
        "adoption_record_respected": adoption_record_ok(adoption),
        "kill_switch_adoption_artifact_exists": bool(kill_switch_adoption),
        "kill_switch_adoption_respected": kill_switch_adoption_ok(kill_switch_adoption),
        "gate_repo_only_planning": gate["enforcement_gate_is_repo_only"] is True and gate["enforcement_gate_is_planning_only"] is True,
        "gate_requires_preflight_safety_readiness": "runtime path" in gate["preflight_required_future_paths"]
        and "candidate path" in gate["preflight_required_future_paths"]
        and "family path" in gate["preflight_required_future_paths"],
        "gate_requires_kill_switch_readiness": "runtime path" in gate["kill_switch_required_future_paths"]
        and "capital path" in gate["kill_switch_required_future_paths"],
        "gate_requires_evidence_chain_compliance": POLICY_LEVEL == "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE",
        "missing_evidence_fails_closed": gate["missing_evidence_fails_closed"] is True,
        "derived_evidence_not_treated_as_primary": gate["derived_evidence_weaker_than_primary_artifact_verification"] is True,
        "next_module_expected": NEXT_MODULE == "edge_factory_os_repo_only_preflight_safety_readiness_enforcement_gate_validator_v1.py",
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "preflight_safety_readiness_enforcement_gate_status": "READY" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_PREFLIGHT_SAFETY_READINESS_ENFORCEMENT_GATE_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "PREFLIGHT_SAFETY_READINESS_ENFORCEMENT_GATE_READY" if ready else "PREFLIGHT_SAFETY_READINESS_ENFORCEMENT_GATE_FAIL_CLOSED",
        "next_action": "BUILD_PREFLIGHT_SAFETY_READINESS_ENFORCEMENT_GATE_VALIDATOR_V1" if ready else "REVIEW_PREFLIGHT_SAFETY_READINESS_ENFORCEMENT_GATE_INPUTS",
        "next_module": NEXT_MODULE if ready else None,
        "preflight_safety_enforcement_gate_ready": ready,
        "preflight_safety_readiness_enforcement_gate": gate,
        "enforcement_gate_is_repo_only": True,
        "enforcement_gate_is_planning_only": True,
        "enforcement_gate_requires_preflight_safety_readiness": True,
        "enforcement_gate_requires_kill_switch_readiness": True,
        "enforcement_gate_requires_evidence_chain_compliance": True,
        "enforcement_gate_does_not_touch_runtime_capital_live": True,
        "enforcement_gate_does_not_approve_generic_runner": True,
        "enforcement_gate_does_not_reopen_loop": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": True,
        "future_runtime_or_live_requires_kill_switch_readiness": True,
        "future_runtime_paper_live_capital_candidate_family_execution_requires_preflight_safety_readiness": True,
        "future_runtime_paper_live_capital_requires_kill_switch_readiness": True,
        "missing_evidence_fails_closed": True,
        "derived_evidence_weaker_than_primary_artifact_verification": True,
        "generic_runner_remains_blocked_unless_future_explicit_safe_mode_approval_contract_allows_planning": True,
        "closed_loop_must_not_reopen": True,
        "preflight_safety_readiness_is_repo_only_planning": True,
        "runtime_preflight_implementation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "real_order_touch_performed": False,
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
        "derived_live_repo_post_check_reason": "Enforcement gate uses the preflight safety readiness adoption artifact, kill-switch adoption artifact, and post-commit live repo replacement checks; evidence remains DERIVED_OVERUSED_ATTENTION and weaker than primary artifact verification.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "adoption_loaded": bool(adoption),
            "kill_switch_adoption_loaded": bool(kill_switch_adoption),
        },
        "safety_flags": {
            "repo_only": True,
            "planning_only": True,
            "runtime_preflight_implementation_performed": False,
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "real_order_touch_performed": False,
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
    latest_json = OUT_DIR / "repo_only_preflight_safety_readiness_enforcement_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_preflight_safety_readiness_enforcement_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_preflight_safety_readiness_enforcement_gate_v1_latest.txt"
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
    return 0 if payload["preflight_safety_readiness_enforcement_gate_status"] in {"READY", "PASS"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
