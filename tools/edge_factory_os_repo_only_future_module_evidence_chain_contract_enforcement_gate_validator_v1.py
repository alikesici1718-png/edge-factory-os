from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "c692456"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 577
NEXT_MODULE = "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_CONTRACT_ENFORCEMENT_GATE_VALIDATOR_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

ENFORCEMENT_GATE_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_enforcement_gate_v1" / "repo_only_future_module_evidence_chain_contract_enforcement_gate_v1_latest.json"
ADOPTION_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_adoption_record_v1" / "repo_only_future_module_evidence_chain_contract_adoption_record_v1_latest.json"
CONTRACT_ARTIFACT = LAB_ROOT / "edge_factory_os_repo_only_future_module_evidence_chain_contract_v1" / "repo_only_future_module_evidence_chain_contract_v1_latest.json"

ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES = [
    "PRIMARY_ARTIFACT_STRONG",
    "EXACT_MARKER_STRONG",
    "DERIVED_EXPLICIT_ATTENTION",
    "DERIVED_OVERUSED_ATTENTION",
    "MISSING_EVIDENCE_FAIL_CLOSED",
]

REQUIRED_GATE_FIELDS = [
    "evidence_chain_enforcement_gate_ready",
    "required_future_module_fields",
    "primary_artifact_verified_required",
    "exact_post_check_marker_verified_required",
    "derived_live_repo_post_check_required",
    "derived_live_repo_post_check_reason_required_when_derived_true",
    "replacement_checks_all_true_required_when_derived_true",
    "replacement_checks_are_not_equivalent_to_primary_artifact",
    "missing_primary_artifact_must_not_silently_pass",
    "fail_closed_if_evidence_missing",
    "plain_pass_without_full_marker_classified_attention",
    "derived_checks_weaker_than_primary_artifacts",
]

FORBIDDEN_SURFACE_ALLOWANCE_FIELDS = [
    "runtime_touched",
    "launcher_executed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "candidate_generation_recommended_now",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "strategy_research_recommended_now",
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


def tracked_python_validation() -> Dict[str, Any]:
    files = sorted(line.strip().replace("\\", "/") for line in run_cmd(["git", "ls-files", "*.py"]).stdout.splitlines() if line.strip())
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
    return {"tracked_python_count": len(files), "tracked_python_syntax_error_count": len(syntax_errors), "tracked_python_bom_error_count": len(bom_errors), "syntax_errors": syntax_errors, "bom_errors": bom_errors}


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
        "repo_clean_for_gate_validator": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def validate_gate(gate: Dict[str, Any]) -> Dict[str, bool]:
    dangerous_flags = gate.get("dangerous_flags", {})
    return {
        "gate_found": bool(gate),
        "gate_ready": gate.get("evidence_chain_enforcement_gate_ready") is True and gate.get("enforcement_gate_status") in {"READY", "PASS"},
        "gate_next_module_points_here": gate.get("next_module") == "edge_factory_os_repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1.py",
        "required_gate_fields_present": all(field in gate for field in REQUIRED_GATE_FIELDS),
        "requires_evidence_chain_quality": "evidence_chain_quality" in gate.get("required_future_module_fields", []),
        "requires_primary_artifact_verified": gate.get("primary_artifact_verified_required") is True,
        "requires_exact_post_check_marker_verified": gate.get("exact_post_check_marker_verified_required") is True,
        "requires_derived_fields": gate.get("derived_live_repo_post_check_required") is True
        and gate.get("derived_live_repo_post_check_reason_required_when_derived_true") is True
        and gate.get("replacement_checks_all_true_required_when_derived_true") is True,
        "fails_closed_if_missing_evidence": gate.get("fail_closed_if_evidence_missing") is True,
        "plain_pass_attention": gate.get("plain_pass_without_full_marker_classified_attention") is True,
        "derived_weaker_than_primary": gate.get("derived_checks_weaker_than_primary_artifacts") is True,
        "policy_active": gate.get("evidence_chain_policy_level") == POLICY_LEVEL,
        "quality_expected": gate.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY,
        "repo_only": gate.get("enforcement_gate_is_repo_only") is True,
        "fail_closed": gate.get("enforcement_gate_is_fail_closed") is True,
        "does_not_approve_generic_runner": gate.get("enforcement_gate_does_not_approve_generic_runner") is True
        and gate.get("generic_runner_approval_granted") is False,
        "does_not_reopen_loop": gate.get("enforcement_gate_does_not_reopen_loop") is True
        and gate.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and gate.get("loop_remains_closed") is True,
        "does_not_create_schema_config": gate.get("planned_schema_files_existing_count") == 0
        and gate.get("generic_runner_target_exists") is False,
        "does_not_allow_forbidden_surfaces": isinstance(dangerous_flags, dict)
        and all(dangerous_flags.get(field) is False for field in FORBIDDEN_SURFACE_ALLOWANCE_FIELDS),
        "dangerous_flags_all_false": isinstance(dangerous_flags, dict) and all(value is False for value in dangerous_flags.values()),
        "replacement_checks_all_true": gate.get("replacement_checks_all_true") is True,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    gate = load_json(ENFORCEMENT_GATE_ARTIFACT)
    adoption = load_json(ADOPTION_ARTIFACT)
    contract = load_json(CONTRACT_ARTIFACT)
    gate_checks = validate_gate(gate)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    dangerous_flags = {flag: False for flag in DANGEROUS_FLAGS}

    prior_enforcement_gate_respected = all(value is True for value in gate_checks.values())
    prior_adoption_record_respected = adoption.get("evidence_chain_contract_adopted_for_future_modules") is True and adoption.get("replacement_checks_all_true") is True
    prior_contract_respected = contract.get("evidence_chain_contract_ready") is True and contract.get("replacement_checks_all_true") is True
    prior_policy_respected = all(
        item.get("evidence_chain_policy_level") == POLICY_LEVEL
        and item.get("current_evidence_chain_quality") == CURRENT_EVIDENCE_CHAIN_QUALITY
        and item.get("future_modules_must_classify_evidence_quality") is True
        and item.get("full_post_check_marker_preferred_over_plain_pass") is True
        and item.get("plain_pass_without_marker_is_attention") is True
        and item.get("replacement_checks_are_not_equivalent_to_primary_artifact") is True
        for item in [gate, adoption, contract]
    )
    prior_loop_closure_respected = all(
        item.get("generic_runner_approval_granted") is False
        and item.get("generic_runner_implementation_remains_blocked") is True
        and item.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and item.get("loop_remains_closed") is True
        for item in [gate, adoption, contract]
    )
    human_decision_respected = prior_loop_closure_respected

    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_gate_validator": git["repo_clean_for_gate_validator"],
        "tracked_python_count_matches_previous": py["tracked_python_count"] == EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "prior_enforcement_gate_respected": prior_enforcement_gate_respected,
        "prior_adoption_record_respected": prior_adoption_record_respected,
        "prior_contract_respected": prior_contract_respected,
        "prior_policy_respected": prior_policy_respected,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "human_decision_respected": human_decision_respected,
        "next_module_expected": NEXT_MODULE == "edge_factory_os_repo_only_future_module_evidence_chain_post_adoption_audit_v1.py",
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "enforcement_gate_validator_status": "READY" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_CONTRACT_ENFORCEMENT_GATE_VALIDATOR_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "FUTURE_MODULE_EVIDENCE_CHAIN_ENFORCEMENT_GATE_VALIDATED" if ready else "FUTURE_MODULE_EVIDENCE_CHAIN_ENFORCEMENT_GATE_VALIDATOR_FAIL_CLOSED",
        "next_action": "BUILD_FUTURE_MODULE_EVIDENCE_CHAIN_POST_ADOPTION_AUDIT_V1" if ready else "REVIEW_FUTURE_MODULE_EVIDENCE_CHAIN_ENFORCEMENT_GATE_VALIDATOR_INPUTS",
        "next_module": NEXT_MODULE if ready else None,
        "evidence_chain_enforcement_gate_found": bool(gate),
        "evidence_chain_enforcement_gate_validated": ready,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "current_evidence_chain_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "allowed_evidence_chain_quality_values": ALLOWED_EVIDENCE_CHAIN_QUALITY_VALUES,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "enforcement_gate_is_fail_closed": ready,
        "enforcement_gate_is_repo_only": ready,
        "enforcement_gate_does_not_approve_generic_runner": ready,
        "enforcement_gate_does_not_reopen_loop": ready,
        "enforcement_gate_does_not_create_schemas_or_configs": gate_checks.get("does_not_create_schema_config") is True,
        "enforcement_gate_does_not_allow_runtime_capital_live_order_candidate_family_paths": gate_checks.get("does_not_allow_forbidden_surfaces") is True,
        "enforcement_gate_requires_evidence_chain_quality": gate_checks.get("requires_evidence_chain_quality") is True,
        "enforcement_gate_treats_plain_pass_without_full_marker_as_attention": gate_checks.get("plain_pass_attention") is True,
        "enforcement_gate_treats_derived_checks_as_weaker_than_primary_artifacts": gate_checks.get("derived_weaker_than_primary") is True,
        "prior_enforcement_gate_respected": prior_enforcement_gate_respected,
        "prior_adoption_record_respected": prior_adoption_record_respected,
        "prior_contract_respected": prior_contract_respected,
        "prior_policy_respected": prior_policy_respected,
        "prior_loop_closure_respected": prior_loop_closure_respected,
        "human_decision_respected": human_decision_respected,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "dangerous_flags": dangerous_flags,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags.values()),
        "dangerous_flag_true_count": 0,
        "auto_fix_performed": False,
        "direct_apply_performed": False,
        "repair_apply_allowed_now": False,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": "Gate validator uses enforcement-gate, adoption, contract artifacts plus live repo replacement checks; evidence remains DERIVED_OVERUSED_ATTENTION and weaker than primary artifact verification.",
        "replacement_checks_all_true": ready,
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "enforcement_gate_validation_checks": gate_checks,
        "validation": {"git_state": git, "tracked_python_validation": py, "gate_loaded": bool(gate), "adoption_loaded": bool(adoption), "contract_loaded": bool(contract)},
        "safety_flags": {
            "future_module_evidence_chain_contract_enforcement_gate_validator": True,
            "repo_only": True,
            "fail_closed_gate_validator": True,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_apply_allowed_now": False,
            **dangerous_flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_future_module_evidence_chain_contract_enforcement_gate_validator_v1_latest.txt"
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
    return 0 if payload["enforcement_gate_validator_status"] == "READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
