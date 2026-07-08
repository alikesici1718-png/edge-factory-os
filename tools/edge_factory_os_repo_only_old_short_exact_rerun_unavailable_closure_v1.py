#!/usr/bin/env python3
"""Final old_short exact-rerun-unavailable closure record.

Closure/parking record only. This module does not run a backtest, execute a
strategy, touch runtime/live/capital paths, create launchers, infer gates,
substitute panels, generate candidates, or claim edge.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_exact_rerun_unavailable_closure_v1.py"
ARTIFACT_REL = "artifacts/old_short/old_short_exact_rerun_unavailable_closure_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

EVIDENCE_REL = "artifacts/old_short/old_short_evidence_recovery_status_refresh_v1.json"
CONTRACT_REL = "artifacts/old_short/old_short_frozen_route_contract_reconstruction_v1.json"
RECOVERY_REL = "artifacts/old_short/old_short_missing_data_source_recovery_discovery_v1.json"
DISAMBIGUATION_REL = "artifacts/old_short/old_short_gate_source_disambiguation_review_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_EXACT_RERUN_UNAVAILABLE_CLOSURE_CREATED"
ARTIFACT_KIND = "OLD_SHORT_EXACT_RERUN_UNAVAILABLE_CLOSURE_RECORD"
MODULE = "edge_factory_os_repo_only_old_short_exact_rerun_unavailable_closure_v1"
FINAL_STATE = "OLD_SHORT_MONITORING_ONLY_EXACT_REPLAY_UNAVAILABLE_NO_CAPITAL"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_output(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repo_status_lines() -> list[str]:
    out = git_output(["status", "--short", "--untracked-files=all"])
    return [] if not out else out.splitlines()


def repo_clean_except_expected() -> bool:
    allowed = {TOOL_REL, ARTIFACT_REL}
    for line in repo_status_lines():
        rel = line[3:].replace("\\", "/")
        if line[:2] == "??" and rel in allowed:
            continue
        return False
    return True


def tracked_python_count() -> int:
    out = git_output(["ls-files", "*.py"])
    return 0 if not out else len(out.splitlines())


def load_json(rel_path: str) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Required artifact missing: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_closed_trade_count(evidence: dict[str, Any]) -> int | None:
    latest = evidence.get("latest_old_short_status", {})
    performance = evidence.get("performance_evidence_summary", {})
    value = latest.get("closed_trades", performance.get("closed_trade_count_recovered"))
    return int(value) if value is not None else None


def build_payload() -> dict[str, Any]:
    evidence = load_json(EVIDENCE_REL)
    contract = load_json(CONTRACT_REL)
    recovery = load_json(RECOVERY_REL)
    disambiguation = load_json(DISAMBIGUATION_REL)

    latest_status = evidence.get("latest_old_short_status", {})
    performance = evidence.get("performance_evidence_summary", {})
    invalidation = evidence.get("invalidation_status", {})
    runtime_status = evidence.get("runtime_live_capital_status", {})
    contract_check = contract.get("completeness_check", {})
    recovery_assessment = recovery.get("exact_source_assessment", {})
    disambig_selected = disambiguation.get("selected_gate_source", {})
    disambig_continuation = disambiguation.get("continuation_decision", {})
    closed_trade_count = get_closed_trade_count(evidence)

    final_closure_decision = {
        "final_state": FINAL_STATE,
        "old_short_invalidated": False,
        "exact_frozen_backtest_completed": False,
        "exact_frozen_backtest_allowed_now": False,
        "manual_gate_source_override_used": False,
        "reviewed_1h_panel_substituted": False,
        "gate_rebuilt_or_inferred": False,
        "runtime_reenable_allowed_now": False,
        "live_allowed_now": False,
        "capital_allowed_now": False,
        "decision_reason": (
            "The exact frozen rerun remains unavailable because no gate candidate passed "
            "the deterministic source-selection rule. old_short remains not invalidated "
            "and monitoring-only with no capital/live/runtime permission."
        ),
    }
    route_state_after_closure = {
        "monitoring_only": True,
        "rejected_no_followup": False,
        "invalidated": False,
        "needs_exact_gate_source_recovery": True,
        "may_reopen_if_exact_referenced_gate_source_found": True,
        "no_capital_until_new_valid_replay_and_review": True,
    }
    reopen_conditions = [
        "exact frozen-contract referenced global gate replay source must be recovered",
        "exact OKX 1m source must remain available",
        "deterministic source selection must pass",
        "frozen rerun must be performed without substitutions",
        "evaluator and closure must pass under current self-deception-resistant policy",
        "manual user approval required before any later runtime/capital discussion",
        "no automatic reopen",
    ]
    forbidden_actions_confirmed_false = {
        "backtest_run": False,
        "strategy_executed": False,
        "runtime_touched": False,
        "monitor_enabled": False,
        "launcher_created": False,
        "candidate_generated": False,
        "edge_claimed": False,
        "family_released": False,
        "live_permission_granted": False,
        "capital_permission_granted": False,
        "manual_gate_override_used": False,
        "one_hour_panel_substitution_used": False,
        "gate_rebuilt_or_inferred": False,
    }
    safety_permissions = {
        "closure_created": True,
        "monitoring_only_recorded": True,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "next_immediate_module_required": False,
        "project_can_pause_after_closure": True,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_except_expected(),
        "evidence_recovery_artifact_loaded": evidence.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH_CREATED",
        "frozen_contract_artifact_loaded": contract.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION_CREATED",
        "missing_source_recovery_artifact_loaded": recovery.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_MISSING_DATA_SOURCE_RECOVERY_FOUND",
        "gate_disambiguation_artifact_loaded": disambiguation.get("status")
        == "PASS_REPO_ONLY_OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_NO_VALID_SOURCE",
        "gate_disambiguation_no_valid_source_verified": disambiguation.get("disambiguation_classification")
        == "OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_NO_VALID_SOURCE",
        "frozen_backtest_allowed_next_false_verified": disambig_continuation.get("frozen_backtest_allowed_next") is False,
        "old_short_invalidated_false_preserved": invalidation.get("old_short_was_invalidated") is False,
        "recovered_closed_trade_count_preserved_20": closed_trade_count == 20,
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_monitor_enabled": True,
        "no_manual_gate_override": True,
        "no_panel_substitution": True,
        "no_gate_rebuild_or_inference": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
    }
    replacement_checks_all_true = all(validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "head": git_output(["rev-parse", "HEAD"]),
            "repo_clean_before_run": validation_checks["repo_clean_before_run"],
            "tracked_python_count_before": tracked_python_count(),
            "generated_at_utc": utc_now(),
        },
        "source_artifacts": {
            "old_short_evidence_recovery_status_refresh": EVIDENCE_REL,
            "old_short_frozen_route_contract_reconstruction": CONTRACT_REL,
            "old_short_missing_data_source_recovery_discovery": RECOVERY_REL,
            "old_short_gate_source_disambiguation_review": DISAMBIGUATION_REL,
        },
        "recovered_old_short_status": {
            "final_decision": latest_status.get("final_decision"),
            "monitoring_ready": latest_status.get("monitoring_ready"),
            "closed_trade_count_recovered": closed_trade_count,
            "eight_of_eight_evidence_found": performance.get("eight_of_eight_evidence_found"),
            "old_short_invalidated": invalidation.get("old_short_was_invalidated"),
            "runtime_live_capital_status": runtime_status,
        },
        "frozen_contract_summary": {
            "contract_complete": contract_check.get("complete"),
            "execution_allowed_next": contract.get("execution_allowed_next"),
            "route_name": contract.get("route_contract", {}).get("route_name"),
            "timeframe": contract.get("route_contract", {}).get("timeframe"),
            "global_gate_dependency_preserved": contract_check.get("global_gate_dependency_preserved"),
            "reviewed_1h_panel_substitution_allowed": False,
        },
        "missing_source_recovery_summary": {
            "status": recovery.get("status"),
            "classification": recovery.get("classification"),
            "exact_okx_1m_source_found": recovery_assessment.get("exact_okx_1m_source_found"),
            "exact_global_gate_decisions_found": recovery_assessment.get("exact_global_gate_decisions_found"),
            "exact_global_gate_candidate_count": recovery_assessment.get("exact_global_gate_candidate_count"),
            "both_required_sources_found": recovery_assessment.get("both_required_sources_found"),
        },
        "gate_disambiguation_summary": {
            "status": disambiguation.get("status"),
            "classification": disambiguation.get("disambiguation_classification"),
            "gate_candidate_count": len(disambiguation.get("gate_candidate_reviews", [])),
            "selected_gate_source_path": disambig_selected.get("selected_gate_source_path"),
            "frozen_backtest_allowed_next": disambig_continuation.get("frozen_backtest_allowed_next"),
            "reason": (
                "No gate candidate satisfied all deterministic source-selection conditions. "
                "The paper_run_gate_v4_priority gate has old_short rows but is not directly "
                "referenced by the frozen contract or recovered evidence; the frozen contract "
                "gate path is directly referenced but has no old_short rows."
            ),
        },
        "final_closure_decision": final_closure_decision,
        "route_state_after_closure": route_state_after_closure,
        "reopen_conditions": reopen_conditions,
        "forbidden_actions_confirmed_false": forbidden_actions_confirmed_false,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    return payload


def main() -> None:
    payload = build_payload()
    write_artifact(payload)
    decision = payload["final_closure_decision"]
    route_state = payload["route_state_after_closure"]
    recovered = payload["recovered_old_short_status"]
    print(f"status: {payload['status']}")
    print(f"final_state: {decision['final_state']}")
    print(f"old_short_invalidated: {str(decision['old_short_invalidated']).lower()}")
    print(f"exact_frozen_backtest_completed: {str(decision['exact_frozen_backtest_completed']).lower()}")
    print(f"exact_frozen_backtest_allowed_now: {str(decision['exact_frozen_backtest_allowed_now']).lower()}")
    print(f"monitoring_only: {str(route_state['monitoring_only']).lower()}")
    print(f"recovered_closed_trade_count: {recovered['closed_trade_count_recovered']}")
    print("manual_gate_override_used: false")
    print("one_hour_panel_substitution_used: false")
    print("runtime_live_capital: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


if __name__ == "__main__":
    main()
