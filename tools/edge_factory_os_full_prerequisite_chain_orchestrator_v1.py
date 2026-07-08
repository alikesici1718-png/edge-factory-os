from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_full_prerequisite_chain_orchestrator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent
TOOLS_DIR = REPO_DIR / "tools"

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"full_prerequisite_chain_orchestrator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "full_prerequisite_chain_orchestrator_latest.json"
LATEST_MD = OUT_ROOT / "full_prerequisite_chain_orchestrator_latest.md"

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

CANONICAL_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_canonical_month_window_guard_v1"
    / "canonical_month_window_guard_latest.json"
)

BROADER_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_broader_month_feature_engine_contract_builder_v1"
    / "broader_month_feature_engine_contract_builder_latest.json"
)


# This orchestrator intentionally runs only prerequisite / research / validation modules.
# It never executes a runtime mutator, capital changer, live launcher, or real-order module.
CHAIN = [
    {
        "step_key": "BROADER_MONTH_FEATURE_ENGINE_RUNNER",
        "script": "edge_factory_os_broader_month_feature_engine_runner_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_broader_month_feature_engine_runner_v1" / "broader_month_feature_engine_runner_latest.json",
        "required_before": ["candidate_contract", "family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "BROADER_MONTH_FEATURE_ENGINE_EVALUATOR",
        "script": "edge_factory_os_broader_month_feature_engine_evaluator_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_broader_month_feature_engine_evaluator_v1" / "broader_month_feature_engine_evaluator_latest.json",
        "required_before": ["candidate_contract", "family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "CANDIDATE_CONTRACT_PREFLIGHT_GUARD",
        "script": "edge_factory_os_candidate_contract_preflight_guard_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_candidate_contract_preflight_guard_v1" / "candidate_contract_preflight_guard_latest.json",
        "required_before": ["candidate_contract"],
        "read_only": True,
    },
    {
        "step_key": "NEW_CANDIDATE_CONTRACT_BUILDER",
        "script": "edge_factory_os_new_candidate_contract_builder_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_new_candidate_contract_builder_v1" / "new_candidate_contract_builder_latest.json",
        "required_before": ["candidate_generation"],
        "read_only": True,
        "requires_guard_field": "candidate_contract_allowed",
    },
    {
        "step_key": "FULL_UNIVERSE_BACKTEST_RUNNER",
        "script": "edge_factory_os_full_universe_candidate_backtest_runner_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_full_universe_candidate_backtest_runner_v1" / "full_universe_candidate_backtest_runner_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "FULL_UNIVERSE_BACKTEST_EVALUATOR",
        "script": "edge_factory_os_full_universe_candidate_backtest_evaluator_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_full_universe_candidate_backtest_evaluator_v1" / "full_universe_candidate_backtest_evaluator_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "TRAIN_OOS_VALIDATION",
        "script": "edge_factory_os_train_oos_validation_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_train_oos_validation_v1" / "train_oos_validation_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "STRICT_12_OF_12_MONTH_STABILITY_VALIDATOR",
        "script": "edge_factory_os_strict_12_of_12_month_stability_validator_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_strict_12_of_12_month_stability_validator_v1" / "strict_12_of_12_month_stability_validator_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "COST_SLIPPAGE_SENSITIVITY",
        "script": "edge_factory_os_cost_slippage_sensitivity_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_cost_slippage_sensitivity_v1" / "cost_slippage_sensitivity_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "SYMBOL_CONCENTRATION_RISK",
        "script": "edge_factory_os_symbol_concentration_risk_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_symbol_concentration_risk_v1" / "symbol_concentration_risk_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "REGIME_BUCKET_DIAGNOSTIC",
        "script": "edge_factory_os_regime_bucket_release_diagnostic_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_regime_bucket_release_diagnostic_v1" / "regime_bucket_release_diagnostic_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "RISK_AND_CAPITAL_SAFETY_REVIEW",
        "script": "edge_factory_os_risk_and_capital_safety_review_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_risk_and_capital_safety_review_v1" / "risk_and_capital_safety_review_latest.json",
        "required_before": ["capital"],
        "read_only": True,
    },
    {
        "step_key": "MANUAL_OR_AI_REVIEW_NON_OVERRIDE",
        "script": "edge_factory_os_manual_or_ai_review_gate_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_manual_or_ai_review_gate_v1" / "manual_or_ai_review_gate_latest.json",
        "required_before": ["family_release", "runtime", "capital"],
        "read_only": True,
    },
    {
        "step_key": "FINAL_RELEASE_GATE",
        "script": "edge_factory_os_final_candidate_release_gate_v1.py",
        "latest_json": BASE_DIR / "edge_factory_os_final_candidate_release_gate_v1" / "final_candidate_release_gate_latest.json",
        "required_before": ["candidate_generation", "family_release", "runtime", "capital"],
        "read_only": True,
    },
]


FORBIDDEN_ACTION_SCRIPT_KEYWORDS = [
    "live_order",
    "real_order",
    "send_order",
    "execute_order",
    "runtime_patch",
    "patch_runtime",
    "launcher_live",
    "capital_apply",
    "capital_change_apply",
    "mutate_runtime",
    "active_paper_launcher",
]


def load_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def script_is_forbidden(script_name: str) -> bool:
    low = script_name.lower()
    return any(k in low for k in FORBIDDEN_ACTION_SCRIPT_KEYWORDS)


def read_authorization() -> Dict[str, Any]:
    action_guard = load_json(ACTION_GUARD_LATEST)
    if not isinstance(action_guard, dict):
        return {
            "available": False,
            "reason": "action_guard_missing",
            "authorization": {},
        }

    auth = action_guard.get("authorization")
    if not isinstance(auth, dict):
        auth = {}

    return {
        "available": True,
        "guard_status": action_guard.get("guard_status"),
        "authorization": auth,
        "failed_or_not_run_checks": action_guard.get("failed_or_not_run_checks"),
        "passed_checks": action_guard.get("passed_checks"),
        "next_action": action_guard.get("next_action"),
    }


def all_actions_blocked(auth_state: Dict[str, Any]) -> bool:
    auth = auth_state.get("authorization") or {}
    if not auth:
        return True
    return all(v is False for v in auth.values())


def validate_root_guards() -> Dict[str, Any]:
    critical = []
    attention = []

    policy = load_json(STRICT_POLICY_LATEST)
    canonical = load_json(CANONICAL_GUARD_LATEST)
    broader = load_json(BROADER_CONTRACT_LATEST)
    action = load_json(ACTION_GUARD_LATEST)

    if not isinstance(policy, dict):
        critical.append("strict_policy_missing")
        policy = {}

    if not isinstance(canonical, dict):
        critical.append("canonical_guard_missing")
        canonical = {}

    if not isinstance(broader, dict):
        critical.append("broader_contract_builder_missing")
        broader = {}

    if not isinstance(action, dict):
        critical.append("action_guard_missing")
        action = {}

    if policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"policy_not_12_of_12:{policy.get('policy_key')}")

    if canonical.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical.get('guard_status')}")

    if safe_get(canonical, ["month_window", "canonical_policy_month_count"]) != 12:
        critical.append("canonical_policy_month_count_not_12")

    if broader.get("builder_status") != "BROADER_MONTH_FEATURE_ENGINE_CONTRACT_READY":
        critical.append(f"broader_contract_not_ready:{broader.get('builder_status')}")

    if action.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action.get('guard_status')}")

    auth = action.get("authorization") if isinstance(action.get("authorization"), dict) else {}
    for k, v in auth.items():
        if v is not False:
            critical.append(f"authorization_not_false:{k}={v}")

    return {
        "critical": critical,
        "attention": attention,
        "policy": {
            "policy_key": policy.get("policy_key"),
            "min_active_months": safe_get(policy, ["release_requirement", "min_active_months"]),
            "min_positive_months": safe_get(policy, ["release_requirement", "min_positive_months"]),
            "min_positive_month_rate": safe_get(policy, ["release_requirement", "min_positive_month_rate"]),
        },
        "canonical": {
            "guard_status": canonical.get("guard_status"),
            "raw_calendar_month_count": safe_get(canonical, ["month_window", "raw_calendar_month_count"]),
            "canonical_policy_month_count": safe_get(canonical, ["month_window", "canonical_policy_month_count"]),
            "boundary_partial_months": safe_get(canonical, ["month_window", "boundary_partial_months"]),
            "canonical_policy_months": safe_get(canonical, ["month_window", "canonical_policy_months"]),
        },
        "broader_contract": {
            "builder_status": broader.get("builder_status"),
            "contract_id": safe_get(broader, ["contract", "contract_id"]),
            "next_module": safe_get(broader, ["contract", "expected_next_module", "module_name"]),
            "candidate_generation_allowed_now": safe_get(broader, ["contract", "required_runner_behavior", "candidate_generation_allowed_now"]),
            "family_release_allowed_now": safe_get(broader, ["contract", "required_runner_behavior", "family_release_allowed_now"]),
        },
        "action_guard": {
            "guard_status": action.get("guard_status"),
            "authorization": auth,
            "passed_checks": action.get("passed_checks"),
            "failed_or_not_run_checks": action.get("failed_or_not_run_checks"),
        },
    }


def run_step(step: Dict[str, Any]) -> Dict[str, Any]:
    script_name = step["script"]
    script_path = TOOLS_DIR / script_name

    if script_is_forbidden(script_name):
        return {
            "step_key": step["step_key"],
            "script": script_name,
            "status": "BLOCKED_FORBIDDEN_ACTION_SCRIPT",
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": "",
            "latest_json_exists": False,
            "latest_json": str(step["latest_json"]),
        }

    if not script_path.exists():
        return {
            "step_key": step["step_key"],
            "script": script_name,
            "status": "MISSING_MODULE_IMPLEMENTATION",
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": "",
            "latest_json_exists": False,
            "latest_json": str(step["latest_json"]),
        }

    proc = subprocess.run(
        [sys.executable, "-u", str(script_path)],
        cwd=str(REPO_DIR),
        capture_output=True,
        text=True,
        timeout=3600,
    )

    latest_json = step["latest_json"]
    latest_obj = load_json(latest_json) if latest_json.exists() else None

    return {
        "step_key": step["step_key"],
        "script": script_name,
        "status": "PASS" if proc.returncode == 0 else "RETURN_CODE_ATTENTION",
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-6000:],
        "stderr_tail": proc.stderr[-6000:],
        "latest_json_exists": latest_json.exists(),
        "latest_json": str(latest_json),
        "latest_status_fields": {
            k: latest_obj.get(k)
            for k in [
                "runner_status",
                "evaluator_status",
                "builder_status",
                "guard_status",
                "release_status",
                "validator_status",
            ]
            if isinstance(latest_obj, dict) and k in latest_obj
        },
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    root = validate_root_guards()

    critical: List[str] = list(root["critical"])
    attention: List[str] = list(root["attention"])
    run_results: List[Dict[str, Any]] = []

    if critical:
        status = "FULL_PREREQUISITE_CHAIN_ORCHESTRATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        next_action = "FIX_ROOT_GUARDS_BEFORE_ORCHESTRATION"
        reason = "; ".join(critical)
    else:
        status = "FULL_PREREQUISITE_CHAIN_ORCHESTRATOR_STARTED"
        severity = "ATTENTION"
        next_action = "RUN_CHAIN_UNTIL_MISSING_OR_BLOCKED_STEP"
        reason = "root guards passed; starting read-only prerequisite chain"

        for step in CHAIN:
            auth_state = read_authorization()

            if not all_actions_blocked(auth_state):
                attention.append("authorization_flags_changed_non_false_stop_chain")
                run_results.append({
                    "step_key": step["step_key"],
                    "script": step["script"],
                    "status": "STOPPED_AUTHORIZATION_FLAGS_CHANGED",
                    "authorization_state": auth_state,
                })
                break

            result = run_step(step)
            run_results.append(result)

            if result["status"] in {
                "MISSING_MODULE_IMPLEMENTATION",
                "BLOCKED_FORBIDDEN_ACTION_SCRIPT",
                "RETURN_CODE_ATTENTION",
            }:
                break

        missing = [r for r in run_results if r.get("status") == "MISSING_MODULE_IMPLEMENTATION"]
        forbidden = [r for r in run_results if r.get("status") == "BLOCKED_FORBIDDEN_ACTION_SCRIPT"]
        bad_return = [r for r in run_results if r.get("status") == "RETURN_CODE_ATTENTION"]

        if missing:
            status = "FULL_PREREQUISITE_CHAIN_STOPPED_MISSING_MODULE"
            severity = "ATTENTION"
            next_action = f"BUILD_MISSING_MODULE_{missing[0]['script']}"
            reason = f"missing_module={missing[0]['script']}"

        elif forbidden:
            status = "FULL_PREREQUISITE_CHAIN_STOPPED_FORBIDDEN_ACTION_SCRIPT"
            severity = "CRITICAL"
            next_action = "REMOVE_FORBIDDEN_ACTION_SCRIPT_FROM_CHAIN"
            reason = f"forbidden_script={forbidden[0]['script']}"

        elif bad_return:
            status = "FULL_PREREQUISITE_CHAIN_STOPPED_STEP_RETURN_CODE_ATTENTION"
            severity = "ATTENTION"
            next_action = f"INSPECT_STEP_{bad_return[0]['script']}"
            reason = f"step_returncode={bad_return[0]['script']}:{bad_return[0]['returncode']}"

        else:
            status = "FULL_PREREQUISITE_CHAIN_REACHED_END_NO_ACTION_EXECUTED"
            severity = "ATTENTION"
            next_action = "RUN_FINAL_ACTION_PREREQUISITE_GUARD_REFRESH"
            reason = "all implemented read-only steps ran; no candidate/family/runtime/capital action executed"

    final_auth = read_authorization()

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "orchestrator_status": status,
        "severity": severity,
        "allowed_scope": "READ_ONLY_ORCHESTRATION",
        "next_action": next_action,
        "reason": reason,

        "root_guard_summary": root,
        "run_results": run_results,

        "implemented_step_count": len([r for r in run_results if r.get("status") == "PASS"]),
        "stopped_at": run_results[-1] if run_results else None,

        "final_authorization_state": final_auth,

        "action_policy": {
            "candidate_generation_allowed": False,
            "candidate_contract_allowed": False,
            "family_release_allowed": False,
            "runtime_change_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "note": (
                "This orchestrator intentionally does not execute action modules. It only completes prerequisites. "
                "Candidate/family/runtime/capital modules must remain separate and require final guard authorization."
            ),
        },

        "release_gate_feed": {
            "FULL_PREREQUISITE_CHAIN_ORCHESTRATOR_RAN": True,
            "ORCHESTRATOR_STATUS": status,
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "ACTIVE_PAPER_ALLOWED": False,
            "LIVE_ALLOWED": False,
            "REAL_ORDERS_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_ORCHESTRATOR": False,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "active_paper_recommended": False,
            "live_or_real_order_recommended": False,
            "next_module": next_action,
        },

        "safety": {
            "read_only": True,
            "offline_only": True,
            "mutate_runtime_allowed": False,
            "launcher_allowed": False,
            "patch_runtime_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "family_disable_allowed": False,
            "real_orders_allowed": False,
            "execution_performed": True if run_results else False,
            "action_execution_performed": False,
        },

        "critical": critical,
        "attention": attention,
    }

    out_json = RUN_DIR / "full_prerequisite_chain_orchestrator_v1_state.json"
    out_md = RUN_DIR / "full_prerequisite_chain_orchestrator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FULL PREREQUISITE CHAIN ORCHESTRATOR v1

orchestrator_status: {status}  
severity: {severity}  
allowed_scope: READ_ONLY_ORCHESTRATION  
next_action: {next_action}  
reason: {reason}

## Root Guard Summary

{json.dumps(root, indent=2, default=str)}

## Run Results

{json.dumps(run_results, indent=2, default=str)[:30000]}

## Final Authorization State

{json.dumps(final_auth, indent=2, default=str)}

## Release Gate Feed

{json.dumps(result["release_gate_feed"], indent=2, default=str)}

## Decision

{json.dumps(result["decision"], indent=2, default=str)}

## Safety

read_only: True  
offline_only: True  
mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: {result["safety"]["execution_performed"]}  
action_execution_performed: False

critical: {critical}  
attention: {attention}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS FULL PREREQUISITE CHAIN ORCHESTRATOR v1")
    print("=" * 100)
    print(f"orchestrator_status: {status}")
    print(f"severity: {severity}")
    print("allowed_scope: READ_ONLY_ORCHESTRATION")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("ROOT GUARDS")
    print("-" * 100)
    print(json.dumps(root, indent=2, default=str)[:5000])
    print()
    print("RUN RESULTS")
    print("-" * 100)
    for row in run_results:
        print({
            "step_key": row.get("step_key"),
            "script": row.get("script"),
            "status": row.get("status"),
            "returncode": row.get("returncode"),
            "latest_status_fields": row.get("latest_status_fields"),
        })
    print()
    print("FINAL AUTHORIZATION")
    print("-" * 100)
    print(json.dumps(final_auth, indent=2, default=str))
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result["release_gate_feed"])
    print()
    print("DECISION")
    print("-" * 100)
    print(json.dumps(result["decision"], indent=2, default=str))
    print()
    print("SAFETY")
    print("-" * 100)
    print("read_only: True")
    print("offline_only: True")
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print(f"execution_performed: {result['safety']['execution_performed']}")
    print("action_execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
