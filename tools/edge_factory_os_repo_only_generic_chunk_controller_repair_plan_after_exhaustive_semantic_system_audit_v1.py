from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_generic_chunk_controller_repair_plan_after_exhaustive_semantic_system_audit_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "55bc5bf"
REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

TARGET_REL = "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"
TARGET_FILE = REPO_ROOT / TARGET_REL
TARGET_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py"

EXHAUSTIVE_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_exhaustive_python_semantic_system_audit_before_generic_controller_repair_v1"
EXHAUSTIVE_SUMMARY = EXHAUSTIVE_DIR / "repo_only_exhaustive_python_semantic_system_audit_summary.json"
EXHAUSTIVE_BLOCKER_MAP = EXHAUSTIVE_DIR / "repo_only_exhaustive_python_generic_controller_line_blocker_map.json"
PERMISSION_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_permission_prerequisite_silent_skip_audit_before_generic_controller_repair_plan_v1"
PERMISSION_SUMMARY = PERMISSION_DIR / "repo_only_permission_prerequisite_silent_skip_audit_summary.json"
SEMANTIC_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_python_semantic_route_interference_audit_after_sprawl_audit_v1"
SEMANTIC_SUMMARY = SEMANTIC_DIR / "repo_only_python_semantic_route_interference_audit_summary.json"
CHUNK_PLAN_PATH = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1" / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
CHUNK_03_LEDGER_PATH = EDGE_LAB_ROOT / TARGET_MODULE.removesuffix(".py") / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_cumulative_ledger_after_chunk.json"
CHUNK_03_NEXT_STATE_PATH = EDGE_LAB_ROOT / TARGET_MODULE.removesuffix(".py") / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_next_chunk_state.json"

PASS_STATUS = "PASS_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_PLAN_READY_FOR_APPLY_AFTER_EXHAUSTIVE_AUDITS"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_PLAN_AFTER_EXHAUSTIVE_AUDITS"
PASS_QUALITY = "REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_PLAN_READY_FOR_APPLY_AFTER_EXHAUSTIVE_AUDITS"
BLOCKED_QUALITY = "REPO_ONLY_GENERIC_CHUNK_CONTROLLER_REPAIR_PLAN_BLOCKED_AFTER_EXHAUSTIVE_AUDITS"
NEXT_MODULE_PASS = "edge_factory_os_repo_only_generic_chunk_controller_repair_apply_after_exhaustive_repair_plan_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_generic_chunk_controller_repair_plan_blocked_record_after_exhaustive_audits_v1.py"

REQUIRED_ARTIFACTS = [
    "repo_only_generic_chunk_controller_repair_plan_after_exhaustive_semantic_system_audit.json",
    "repo_only_generic_chunk_controller_repair_plan_blocker_map.json",
    "repo_only_generic_chunk_controller_repair_patch_strategy.json",
    "repo_only_generic_chunk_controller_repair_patch_preview.json",
    "repo_only_generic_chunk_controller_dynamic_state_loading_plan.json",
    "repo_only_generic_chunk_controller_dynamic_artifact_naming_plan.json",
    "repo_only_generic_chunk_controller_dynamic_ledger_update_plan.json",
    "repo_only_generic_chunk_controller_route_logic_repair_plan.json",
    "repo_only_generic_chunk_controller_repair_approval_record.json",
    "repo_only_generic_chunk_controller_repair_plan_self_validator.json",
    "repo_only_generic_chunk_controller_repair_plan_summary.json",
]


class PlanBlocked(RuntimeError):
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


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_python_count() -> int:
    return len([line for line in run_git(["ls-files", "*.py"]).splitlines() if line.strip()])


def syntax_bom_check() -> dict[str, Any]:
    errors = []
    bom = []
    for rel in run_git(["ls-files", "*.py"]).splitlines():
        if not rel.strip():
            continue
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            errors.append({"file": rel, "error": repr(exc)})
    return {"syntax_error_count": len(errors), "syntax_errors": errors, "bom_error_count": len(bom), "bom_errors": bom}


def line_hits(source: str, token: str) -> list[dict[str, Any]]:
    return [
        {"line_number": idx, "text": line.strip()}
        for idx, line in enumerate(source.splitlines(), start=1)
        if token in line
    ]


def validate_inputs() -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    if head != EXPECTED_HEAD:
        raise PlanBlocked(f"expected HEAD {EXPECTED_HEAD}, found {head}")
    lines = status_lines()
    if not repo_effectively_clean(lines):
        raise PlanBlocked(f"repo dirty before plan: {lines}")
    required_paths = [
        EXHAUSTIVE_SUMMARY,
        EXHAUSTIVE_BLOCKER_MAP,
        PERMISSION_SUMMARY,
        SEMANTIC_SUMMARY,
        TARGET_FILE,
        CHUNK_PLAN_PATH,
        CHUNK_03_LEDGER_PATH,
        CHUNK_03_NEXT_STATE_PATH,
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise PlanBlocked(f"missing required inputs: {missing}")
    exhaustive = read_json(EXHAUSTIVE_SUMMARY)
    permission = read_json(PERMISSION_SUMMARY)
    semantic = read_json(SEMANTIC_SUMMARY)
    blocker_map = read_json(EXHAUSTIVE_BLOCKER_MAP)
    chunk_plan = read_json(CHUNK_PLAN_PATH)
    ledger = read_json(CHUNK_03_LEDGER_PATH)
    next_state = read_json(CHUNK_03_NEXT_STATE_PATH)
    target_source = TARGET_FILE.read_text(encoding="utf-8")
    target_hash = sha256_file(TARGET_FILE)
    checks = {
        "exhaustive_semantic_audit_confirmed": (
            exhaustive.get("final_decision") == "EXHAUSTIVE_SEMANTIC_SYSTEM_AUDIT_COMPLETE_READY_FOR_GENERIC_CONTROLLER_REPAIR_PLAN"
            and exhaustive.get("repair_scope_complete") is True
            and exhaustive.get("replacement_checks_all_true") is True
        ),
        "permission_silent_skip_audit_confirmed": (
            permission.get("final_decision") == "PERMISSION_PREREQUISITE_SILENT_SKIP_AUDIT_PASS_READY_FOR_GENERIC_CONTROLLER_REPAIR_PLAN"
            and permission.get("permission_integrity_ok_for_repair_plan") is True
            and permission.get("repair_plan_allowed_next") is True
            and permission.get("replacement_checks_all_true") is True
        ),
        "semantic_audit_block_confirmed": (
            semantic.get("final_decision") == "SEMANTIC_ROUTE_INTERFERENCE_AUDIT_BLOCKED_GENERIC_CONTROLLER_REPAIR_REQUIRED"
            and semantic.get("generic_controller_hardcoded_chunk_only") is True
            and semantic.get("generic_controller_safe_to_rerun_for_chunk_04") is False
        ),
        "target_file_exists": TARGET_FILE.exists(),
        "blocker_count_confirmed": blocker_map.get("generic_controller_blocker_count") == 4,
        "all_blockers_mapped_to_lines": blocker_map.get("all_generic_controller_blockers_mapped_to_lines") is True,
        "chunk_plan_valid": chunk_plan.get("chunk_count") == 16 and len(chunk_plan.get("chunks", [])) == 16,
        "chunk_03_ledger_valid": ledger.get("chunk_id") == "chunk_03" and ledger.get("next_chunk_id_after_execution") == "chunk_04",
        "next_state_valid": next_state.get("next_chunk_id_after_execution") == "chunk_04",
        "target_is_hardcoded_before_repair": 'APPROVED_CHUNK_ID = "chunk_03"' in target_source and "APPROVED_SYMBOLS = [" in target_source,
    }
    if not all(checks.values()):
        raise PlanBlocked(f"input validation failed: {checks}")
    return {
        "head": head,
        "exhaustive": exhaustive,
        "permission": permission,
        "semantic": semantic,
        "blocker_map": blocker_map,
        "chunk_plan": chunk_plan,
        "ledger": ledger,
        "next_state": next_state,
        "target_source": target_source,
        "target_sha256_before": target_hash,
        "checks": checks,
    }


def dynamic_state_loading_plan() -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_generic_chunk_controller_dynamic_state_loading_plan",
        "dynamic_state_loading_required": True,
        "requirements": [
            "Load latest immutable next_chunk_state first when present.",
            "Load latest cumulative ledger after the most recent completed chunk.",
            "Validate next_chunk_id from state and ledger; current expected value is chunk_04.",
            "Use chunk plan state and ledger values, not filename guessing, when state artifacts exist.",
            "Fail closed if state and ledger disagree on completed chunk or next chunk.",
        ],
        "current_state_sources": {
            "latest_next_chunk_state": str(CHUNK_03_NEXT_STATE_PATH),
            "latest_cumulative_ledger": str(CHUNK_03_LEDGER_PATH),
            "current_expected_next_chunk_id": "chunk_04",
        },
    }


def artifact_naming_plan() -> dict[str, Any]:
    base = "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{chunk_id}_"
    immutable = [
        base + "execution_report.json",
        base + "chunk_download_manifest_after_execution.json",
        base + "gap_report.json",
        base + "reuse_validation_report.json",
        base + "sha256_report.json",
        base + "zip_inventory_report.json",
        base + "schema_sample_report.json",
        base + "per_symbol_coverage_summary.json",
        base + "cumulative_ledger_after_chunk.json",
        base + "next_chunk_state.json",
        base + "compliance_report.json",
        base + "summary.json",
    ]
    return {
        "artifact_type": "repo_only_generic_chunk_controller_dynamic_artifact_naming_plan",
        "dynamic_artifact_naming_required": True,
        "immutable_per_chunk_artifact_templates": immutable,
        "chunk_04_examples": [name.format(chunk_id="chunk_04") for name in immutable],
        "latest_pointer_policy": {
            "latest_pointer_allowed": True,
            "required_fields": ["chunk_id", "source_commit", "generated_at", "immutable_artifact_path"],
            "must_not_overwrite_chunk_03_immutable_artifacts": True,
        },
    }


def ledger_update_plan() -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_generic_chunk_controller_dynamic_ledger_update_plan",
        "dynamic_ledger_update_required": True,
        "formulas": {
            "chunks_completed_after": "chunks_completed_before + 1",
            "chunks_remaining_after": "chunks_total - chunks_completed_after",
            "symbols_evaluated_for_download_coverage": "previous_symbols_evaluated_for_download_coverage + chunk_symbol_count",
            "cumulative_near_3y_download_coverage_complete_symbol_count": "previous_complete_count + chunk_near_3y_download_coverage_complete_symbol_count",
            "cumulative_coverage_gap_symbol_count": "previous_gap_count + chunk_coverage_gap_symbol_count",
            "cumulative_pending_symbol_count": "total_candidate_symbol_count - symbols_evaluated_for_download_coverage",
            "cumulative_available_file_count": "previous_available_file_count + chunk_final_available_file_count",
            "cumulative_missing_or_failed_file_count": "previous_missing_or_failed_file_count + chunk_missing_or_failed_file_count",
            "cumulative_planned_file_count_evaluated": "previous_planned_file_count_evaluated + planned_file_count",
            "build_ready_symbol_count": 0,
            "acquisition_ready_symbol_count": 0,
        },
        "current_chunk_03_carry_forward": {
            "chunks_completed_after": 3,
            "chunks_remaining_after": 13,
            "symbols_evaluated_for_download_coverage": 60,
            "next_chunk_id": "chunk_04",
        },
    }


def route_logic_plan() -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_generic_chunk_controller_route_logic_repair_plan",
        "next_route_logic_repair_required": True,
        "rules": [
            {
                "condition": "chunks_remaining_after > 0",
                "next_module": TARGET_MODULE,
                "next_chunk_id_after_execution": "next pending chunk from approved chunk plan",
            },
            {
                "condition": "chunks_remaining_after == 0",
                "next_module": "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1.py",
                "next_chunk_id_after_execution": None,
            },
        ],
        "blocked_route_policy": {
            "blocked_next_module": "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_blocked_record_v1.py",
            "must_be_created_or_existing_before_use": True,
        },
    }


def patch_strategy(blocker_map: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_patch_strategy",
        "repair_patch_required": True,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_creation_required": False,
        "target_file": TARGET_REL,
        "strategy_steps": [
            "Replace APPROVED_CHUNK_ID / APPROVED_SYMBOLS constants with runtime ControllerState derived from latest ledger and next chunk state.",
            "Replace CHUNK_02_LEDGER and fixed chunk counters with latest ledger discovery and validation.",
            "Use approved chunk plan to select exactly one next pending chunk and validate symbols.",
            "Generate immutable chunk-id-qualified artifact names and optional latest pointers with provenance.",
            "Apply dynamic ledger formulas and keep build/acquisition-ready counts at zero.",
            "Switch route to final summary only after chunk_16 completes.",
            "Preserve no API/browse/build/aggregation/full CSV/research/backtest/edge/runtime/capital/live gates.",
        ],
        "source_blockers": blocker_map.get("generic_controller_blockers", []),
    }


def patch_preview() -> dict[str, Any]:
    diff = """--- tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py
+++ tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1.py
@@ repair preview only: static chunk constants
-APPROVED_CHUNK_ID = "chunk_03"
-APPROVED_SYMBOLS = [...]
-CHUNKS_COMPLETED_BEFORE = 2
-CHUNKS_COMPLETED_AFTER = 3
-CHUNKS_REMAINING_AFTER = 13
-NEXT_CHUNK_ID_AFTER_EXECUTION = "chunk_04"
+@dataclass(frozen=True)
+class ControllerState:
+    chunk_id: str
+    chunk_symbols: list[str]
+    chunks_total: int
+    chunks_completed_before: int
+    chunks_remaining_before: int
+    ledger_entries: dict[str, int]
+
+def load_latest_controller_state() -> ControllerState:
+    # Load latest next_chunk_state and latest cumulative ledger.
+    # Validate current next chunk is chunk_04 after chunk_03, then generalize for chunk_05..chunk_16.
+    ...
+
+def select_chunk_from_plan(state: ControllerState, chunk_plan: dict[str, Any]) -> dict[str, Any]:
+    # Find exactly one chunk by state.chunk_id and validate symbol list / expected file count.
+    ...
@@ repair preview only: artifact names
-"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_report.json"
+f"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{state.chunk_id}_execution_report.json"
@@ repair preview only: ledger update
-"chunks_completed_after": CHUNKS_COMPLETED_AFTER
+"chunks_completed_after": state.chunks_completed_before + 1
+"chunks_remaining_after": state.chunks_total - (state.chunks_completed_before + 1)
+"build_ready_symbol_count": 0
+"acquisition_ready_symbol_count": 0
@@ repair preview only: route logic
-"next_chunk_id_after_execution": NEXT_CHUNK_ID_AFTER_EXECUTION
+"next_chunk_id_after_execution": next_pending_chunk_id_or_none
+"next_module": TARGET_MODULE if chunks_remaining_after > 0 else FINAL_SUMMARY_MODULE
"""
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_patch_preview",
        "target_file": TARGET_REL,
        "repair_patch_required": True,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_creation_required": False,
        "expected_after_patch_generic_controller_dynamic_chunk_selection": True,
        "expected_after_patch_generic_controller_hardcoded_chunk_only": False,
        "expected_after_patch_safe_to_rerun_for_chunk_04": True,
        "expected_after_patch_next_chunk_id": "chunk_04",
        "expected_after_patch_next_module": TARGET_MODULE,
        "preview_unified_diff": diff,
        "patch_apply_performed": False,
    }


def approval_record() -> dict[str, Any]:
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_approval_record",
        "repair_approval_record_created": True,
        "approval_grants_repair_plan_now": True,
        "approval_grants_patch_apply_now": False,
        "approval_grants_future_generic_controller_repair_apply_next": True,
        "approval_grants_chunk_04_execution_now": False,
        "approval_grants_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "approval_scope": "future repair apply module only; no patch apply or chunk execution now",
        "next_module": NEXT_MODULE_PASS,
    }


def build_summary(inputs: dict[str, Any], artifacts: dict[str, Any], target_hash_after: str) -> dict[str, Any]:
    blocker_map = inputs["blocker_map"]
    target_source = inputs["target_source"]
    target_modified = inputs["target_sha256_before"] != target_hash_after
    checks = {
        **inputs["checks"],
        "target_file_not_modified": not target_modified,
        "patch_preview_created": artifacts["patch_preview"]["repair_patch_required"] is True,
        "repair_approval_record_created": artifacts["approval"]["repair_approval_record_created"] is True,
        "approval_does_not_apply_patch_now": artifacts["approval"]["approval_grants_patch_apply_now"] is False,
        "approval_does_not_execute_chunk_04_now": artifacts["approval"]["approval_grants_chunk_04_execution_now"] is False,
        "no_forbidden_actions": True,
    }
    all_true = all(checks.values())
    return {
        "artifact_type": "repo_only_generic_chunk_controller_repair_plan_summary",
        "generic_chunk_controller_repair_plan_status": PASS_STATUS if all_true else BLOCKED_STATUS,
        "repair_plan_created": True,
        "created_at_utc": utc_now(),
        "target_file": TARGET_REL.replace("/", "\\"),
        "target_file_modified": target_modified,
        "target_sha256_before": inputs["target_sha256_before"],
        "target_sha256_after": target_hash_after,
        "exhaustive_semantic_audit_confirmed": inputs["checks"]["exhaustive_semantic_audit_confirmed"],
        "permission_silent_skip_audit_confirmed": inputs["checks"]["permission_silent_skip_audit_confirmed"],
        "semantic_audit_block_confirmed": inputs["checks"]["semantic_audit_block_confirmed"],
        "generic_controller_hardcoded_chunk_only_before_repair": blocker_map.get("generic_controller_hardcoded_chunk_only") is True,
        "generic_controller_dynamic_chunk_selection_before_repair": blocker_map.get("generic_controller_dynamic_chunk_selection") is True,
        "generic_controller_safe_to_rerun_for_chunk_04_before_repair": blocker_map.get("generic_controller_safe_to_rerun_for_chunk_04") is True,
        "blocker_count_confirmed": blocker_map.get("generic_controller_blocker_count"),
        "all_blockers_mapped_to_lines": blocker_map.get("all_generic_controller_blockers_mapped_to_lines") is True,
        "hardcoded_chunk_03_reference_count": blocker_map.get("hardcoded_chunk_03_reference_count"),
        "fixed_symbol_list_detected": blocker_map.get("fixed_symbol_list_detected") is True,
        "dynamic_state_loading_required": True,
        "chunk_plan_lookup_required": True,
        "dynamic_artifact_naming_required": True,
        "dynamic_ledger_update_required": True,
        "next_route_logic_repair_required": True,
        "safety_gate_preservation_required": True,
        "patch_preview_created": True,
        "repair_patch_required": True,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_creation_required": False,
        "expected_after_patch_generic_controller_dynamic_chunk_selection": True,
        "expected_after_patch_generic_controller_hardcoded_chunk_only": False,
        "expected_after_patch_safe_to_rerun_for_chunk_04": True,
        "expected_after_patch_next_chunk_id": "chunk_04",
        "expected_after_patch_next_module": TARGET_MODULE,
        "repair_approval_record_created": True,
        "approval_grants_future_generic_controller_repair_apply_next": True,
        "approval_grants_patch_apply_now": False,
        "approval_grants_chunk_04_execution_now": False,
        "approval_grants_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "delete_move_cleanup_performed": False,
        "patch_apply_performed": False,
        "active_p0_blocker_count": 0 if all_true else 1,
        "active_p1_attention_count": inputs["exhaustive"].get("current_p1_attention_count", 0),
        "current_evidence_chain_quality_after_repair_plan": PASS_QUALITY if all_true else BLOCKED_QUALITY,
        "next_module": NEXT_MODULE_PASS if all_true else NEXT_MODULE_BLOCKED,
        "replacement_checks": checks,
        "replacement_checks_all_true": all_true,
    }


def run_plan() -> dict[str, Any]:
    inputs = validate_inputs()
    blocker_map = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_plan_blocker_map",
        "target_file": TARGET_REL,
        "source_audit_artifact": str(EXHAUSTIVE_BLOCKER_MAP),
        "blocker_count_confirmed": inputs["blocker_map"].get("generic_controller_blocker_count"),
        "all_blockers_mapped_to_lines": inputs["blocker_map"].get("all_generic_controller_blockers_mapped_to_lines"),
        "hardcoded_chunk_03_reference_count": inputs["blocker_map"].get("hardcoded_chunk_03_reference_count"),
        "fixed_symbol_list_detected": inputs["blocker_map"].get("fixed_symbol_list_detected"),
        "blockers": inputs["blocker_map"].get("generic_controller_blockers", []),
        "additional_line_hits": {
            "download_dir_chunk_03": line_hits(inputs["target_source"], "downloaded_chunk_03_approved_quarantine"),
            "required_outputs_without_chunk_id": line_hits(inputs["target_source"], "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_"),
        },
    }
    artifacts = {
        "state": dynamic_state_loading_plan(),
        "naming": artifact_naming_plan(),
        "ledger": ledger_update_plan(),
        "route": route_logic_plan(),
        "strategy": patch_strategy(inputs["blocker_map"]),
        "patch_preview": patch_preview(),
        "approval": approval_record(),
    }
    target_hash_after = sha256_file(TARGET_FILE)
    summary = build_summary(inputs, artifacts, target_hash_after)
    self_validator = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_plan_self_validator",
        "self_validator_created": True,
        "replacement_checks": summary["replacement_checks"],
        "replacement_checks_all_true": summary["replacement_checks_all_true"],
        "target_file_modified": summary["target_file_modified"],
        "required_artifacts_expected": REQUIRED_ARTIFACTS,
    }
    main_plan = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_plan_after_exhaustive_semantic_system_audit",
        "summary": summary,
        "repair_goal": "convert existing controller to dynamic one-chunk-per-run controller for chunk_04 through chunk_16",
        "target_file": TARGET_REL,
        "repair_patch_required": True,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_creation_required": False,
        "inputs_used": {
            "exhaustive_summary": str(EXHAUSTIVE_SUMMARY),
            "permission_summary": str(PERMISSION_SUMMARY),
            "semantic_summary": str(SEMANTIC_SUMMARY),
            "chunk_plan": str(CHUNK_PLAN_PATH),
            "latest_cumulative_ledger": str(CHUNK_03_LEDGER_PATH),
            "latest_next_chunk_state": str(CHUNK_03_NEXT_STATE_PATH),
        },
        "blocker_map": blocker_map,
        "patch_strategy": artifacts["strategy"],
        "dynamic_state_loading_plan": artifacts["state"],
        "dynamic_artifact_naming_plan": artifacts["naming"],
        "dynamic_ledger_update_plan": artifacts["ledger"],
        "route_logic_repair_plan": artifacts["route"],
        "approval_record": artifacts["approval"],
        "forbidden_actions_performed_by_this_plan": {
            "target_file_modified": summary["target_file_modified"],
            "patch_apply_performed": False,
            "download": False,
            "api": False,
            "browse": False,
            "url_fetch": False,
            "data_build": False,
            "aggregation": False,
            "full_csv_read": False,
            "delete": False,
            "move": False,
            "cleanup": False,
            "research_backtest_edge": False,
            "runtime_capital_live": False,
        },
    }
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_plan_after_exhaustive_semantic_system_audit.json", main_plan)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_plan_blocker_map.json", blocker_map)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_patch_strategy.json", artifacts["strategy"])
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_patch_preview.json", artifacts["patch_preview"])
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_dynamic_state_loading_plan.json", artifacts["state"])
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_dynamic_artifact_naming_plan.json", artifacts["naming"])
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_dynamic_ledger_update_plan.json", artifacts["ledger"])
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_route_logic_repair_plan.json", artifacts["route"])
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_approval_record.json", artifacts["approval"])
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_plan_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_plan_summary.json", summary)
    missing = [name for name in REQUIRED_ARTIFACTS if not (OUTPUT_DIR / name).exists()]
    if missing:
        raise PlanBlocked(f"missing required artifacts: {missing}")
    return summary


def blocked_summary(message: str) -> dict[str, Any]:
    summary = {
        "artifact_type": "repo_only_generic_chunk_controller_repair_plan_summary",
        "generic_chunk_controller_repair_plan_status": BLOCKED_STATUS,
        "repair_plan_created": False,
        "blocked_reason": message,
        "target_file": TARGET_REL.replace("/", "\\"),
        "target_file_modified": False,
        "exhaustive_semantic_audit_confirmed": False,
        "permission_silent_skip_audit_confirmed": False,
        "semantic_audit_block_confirmed": False,
        "generic_controller_hardcoded_chunk_only_before_repair": True,
        "generic_controller_dynamic_chunk_selection_before_repair": False,
        "generic_controller_safe_to_rerun_for_chunk_04_before_repair": False,
        "blocker_count_confirmed": 0,
        "all_blockers_mapped_to_lines": False,
        "hardcoded_chunk_03_reference_count": 0,
        "fixed_symbol_list_detected": False,
        "dynamic_state_loading_required": True,
        "chunk_plan_lookup_required": True,
        "dynamic_artifact_naming_required": True,
        "dynamic_ledger_update_required": True,
        "next_route_logic_repair_required": True,
        "safety_gate_preservation_required": True,
        "patch_preview_created": False,
        "repair_patch_required": True,
        "patch_scope": "EXISTING_GENERIC_CONTROLLER_ONLY",
        "chunk_specific_file_creation_required": False,
        "expected_after_patch_generic_controller_dynamic_chunk_selection": True,
        "expected_after_patch_generic_controller_hardcoded_chunk_only": False,
        "expected_after_patch_safe_to_rerun_for_chunk_04": True,
        "expected_after_patch_next_chunk_id": "chunk_04",
        "repair_approval_record_created": False,
        "approval_grants_future_generic_controller_repair_apply_next": False,
        "approval_grants_patch_apply_now": False,
        "approval_grants_chunk_04_execution_now": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "current_evidence_chain_quality_after_repair_plan": BLOCKED_QUALITY,
        "next_module": NEXT_MODULE_BLOCKED,
        "replacement_checks_all_true": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_generic_chunk_controller_repair_plan_summary.json", summary)
    return summary


def main() -> int:
    try:
        syntax = syntax_bom_check()
        if syntax["syntax_error_count"] or syntax["bom_error_count"]:
            raise PlanBlocked(f"syntax/BOM precheck failed: {syntax}")
        summary = run_plan()
    except Exception as exc:
        summary = blocked_summary(type(exc).__name__ + ": " + str(exc))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
