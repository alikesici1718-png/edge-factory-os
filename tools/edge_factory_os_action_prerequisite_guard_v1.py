from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_action_prerequisite_guard_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

FEATURE_CONTRACT_BUILDER_LATEST = (
    BASE_DIR
    / "edge_factory_os_feature_conditioned_research_contract_builder_v1"
    / "feature_conditioned_research_contract_builder_latest.json"
)

FEATURE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "feature_conditioned_research_contract_latest.json"
)

BLOCKLIST_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "candidate_route_blocklist.json"
)

UNIVERSE_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"action_prerequisite_guard_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "action_prerequisite_guard_latest.json"
LATEST_MD = OUT_ROOT / "action_prerequisite_guard_latest.md"

POLICY_OUT = BASE_DIR / "edge_factory_os_policy_guards" / "action_prerequisite_policy_latest.json"


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


def extract_blocked_hashes(blocklist: Dict[str, Any]) -> List[str]:
    routes = blocklist.get("blocked_routes")
    if not isinstance(routes, list):
        return []

    out = []
    for row in routes:
        if isinstance(row, dict) and row.get("route_hash"):
            out.append(str(row["route_hash"]))

    return sorted(set(out))


def make_required_chain() -> List[Dict[str, Any]]:
    return [
        {
            "step_key": "STRICT_MONTH_STABILITY_12_OF_12_POLICY_ACTIVE",
            "description": "Strict month-stability policy must require 12 active months and 12 positive months.",
            "required_before": [
                "candidate_generation",
                "candidate_contract",
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
                "real_orders",
            ],
        },
        {
            "step_key": "LESSON_MEMORY_AND_BLOCKLIST_PREFLIGHT_PASS",
            "description": "New route hash must not repeat blocked routes or known failure lessons.",
            "required_before": [
                "candidate_generation",
                "candidate_contract",
                "family_release",
                "runtime_change",
                "capital_change",
            ],
        },
        {
            "step_key": "FULL_1Y_OKX_SWAP_UNIVERSE_PASS",
            "description": "Research and validation must use full available 1Y OKX swap universe, not paper ledger only.",
            "required_before": [
                "candidate_generation",
                "candidate_contract",
                "family_release",
                "runtime_change",
                "capital_change",
            ],
        },
        {
            "step_key": "FEATURE_CONDITIONED_RESEARCH_RUNNER_PASS",
            "description": "Feature-conditioned research runner must test hypotheses under 12/12 policy.",
            "required_before": [
                "candidate_contract",
                "family_release",
                "runtime_change",
                "capital_change",
            ],
        },
        {
            "step_key": "FEATURE_CONDITIONED_RESEARCH_EVALUATOR_PASS",
            "description": "Evaluator must explicitly recommend whether a new candidate contract is justified.",
            "required_before": [
                "candidate_contract",
                "family_release",
                "runtime_change",
                "capital_change",
            ],
        },
        {
            "step_key": "NEW_CANDIDATE_CONTRACT_PREFLIGHT_PASS",
            "description": "Any future candidate contract must have new route hash, no blocked route reuse, and candidate generation still gated.",
            "required_before": [
                "candidate_generation",
                "family_release",
                "runtime_change",
                "capital_change",
            ],
        },
        {
            "step_key": "FULL_UNIVERSE_BACKTEST_PASS",
            "description": "Candidate must pass full-universe offline backtest.",
            "required_before": [
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
            ],
        },
        {
            "step_key": "TRAIN_OOS_VALIDATION_PASS",
            "description": "Candidate must pass train/OOS validation with positive train and OOS economics.",
            "required_before": [
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
            ],
        },
        {
            "step_key": "STRICT_12_OF_12_MONTH_STABILITY_PASS",
            "description": "Candidate must have at least 12 active months and all 12 positive.",
            "required_before": [
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
            ],
        },
        {
            "step_key": "COST_SLIPPAGE_SENSITIVITY_PASS",
            "description": "Candidate must survive cost and slippage sensitivity.",
            "required_before": [
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
            ],
        },
        {
            "step_key": "SYMBOL_CONCENTRATION_RISK_PASS",
            "description": "Candidate must not depend on a tiny symbol subset or single lucky symbol.",
            "required_before": [
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
            ],
        },
        {
            "step_key": "REGIME_BUCKET_DIAGNOSTIC_PASS",
            "description": "Candidate must not hide catastrophic regime buckets.",
            "required_before": [
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
            ],
        },
        {
            "step_key": "RISK_AND_CAPITAL_SAFETY_PASS",
            "description": "Capital/risk governor must explicitly approve any sizing/capital action.",
            "required_before": [
                "capital_change",
                "active_paper",
                "live",
                "real_orders",
            ],
        },
        {
            "step_key": "MANUAL_OR_AI_REVIEW_PASS_NON_OVERRIDE",
            "description": "Manual/AI review may add comments but cannot override failed tests.",
            "required_before": [
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
            ],
        },
        {
            "step_key": "FINAL_RELEASE_GATE_PASS",
            "description": "Final release gate must pass after all evidence modules are complete.",
            "required_before": [
                "candidate_generation",
                "family_release",
                "runtime_change",
                "capital_change",
                "active_paper",
                "live",
                "real_orders",
            ],
        },
    ]


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    policy = load_json(POLICY_LATEST)
    feature_builder = load_json(FEATURE_CONTRACT_BUILDER_LATEST)
    feature_contract = load_json(FEATURE_CONTRACT_LATEST)
    blocklist = load_json(BLOCKLIST_PATH)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)

    if not isinstance(policy, dict):
        critical.append("strict_month_stability_policy_latest_missing")
        policy = {}

    if not isinstance(feature_builder, dict):
        attention.append("feature_conditioned_contract_builder_latest_missing")
        feature_builder = {}

    if not isinstance(feature_contract, dict):
        attention.append("feature_conditioned_research_contract_latest_missing")
        feature_contract = {}

    if not isinstance(blocklist, dict):
        critical.append("candidate_route_blocklist_missing")
        blocklist = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_missing")
        universe = {}

    blocked_hashes = extract_blocked_hashes(blocklist)

    required_blocked = {
        "90466e4144914fbc",
        "85f9e6a4accb14c7",
    }

    missing_blocked = sorted([h for h in required_blocked if h not in set(blocked_hashes)])
    if missing_blocked:
        attention.append(f"expected_blocked_hashes_missing:{missing_blocked}")

    check_results: Dict[str, Dict[str, Any]] = {}

    policy_ok = (
        policy.get("policy_key") == "STRICT_MONTH_STABILITY_12_OF_12"
        and safe_get(policy, ["release_requirement", "min_active_months"]) == 12
        and safe_get(policy, ["release_requirement", "min_positive_months"]) == 12
        and float(safe_get(policy, ["release_requirement", "min_positive_month_rate"], 0.0)) == 1.0
    )

    check_results["STRICT_MONTH_STABILITY_12_OF_12_POLICY_ACTIVE"] = {
        "pass": policy_ok,
        "status": policy.get("policy_key"),
        "details": {
            "min_active_months": safe_get(policy, ["release_requirement", "min_active_months"]),
            "min_positive_months": safe_get(policy, ["release_requirement", "min_positive_months"]),
            "min_positive_month_rate": safe_get(policy, ["release_requirement", "min_positive_month_rate"]),
        },
    }

    lesson_ok = len(missing_blocked) == 0 and len(blocked_hashes) >= 2
    check_results["LESSON_MEMORY_AND_BLOCKLIST_PREFLIGHT_PASS"] = {
        "pass": lesson_ok,
        "status": "BLOCKLIST_READY" if lesson_ok else "BLOCKLIST_INCOMPLETE",
        "details": {
            "blocked_route_hashes": blocked_hashes,
            "missing_required_blocked_hashes": missing_blocked,
        },
    }

    universe_ok = universe.get("universe_status") == "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY"
    check_results["FULL_1Y_OKX_SWAP_UNIVERSE_PASS"] = {
        "pass": universe_ok,
        "status": universe.get("universe_status"),
        "details": {
            "symbol_count": safe_get(universe, ["best_universe_manifest", "symbol_count"]),
            "row_count": safe_get(universe, ["best_universe_manifest", "row_count"]),
            "day_span": safe_get(universe, ["best_universe_manifest", "day_span"]),
            "panel_path": safe_get(universe, ["best_universe_manifest", "panel_path"]),
        },
    }

    feature_contract_ok = (
        feature_builder.get("builder_status") == "FEATURE_CONDITIONED_RESEARCH_CONTRACT_READY_12_OF_12"
        and safe_get(feature_builder, ["decision", "candidate_generation_recommended_now"]) is False
        and safe_get(feature_builder, ["decision", "family_release_recommended"]) is False
        and safe_get(feature_builder, ["decision", "runtime_change_recommended"]) is False
        and safe_get(feature_builder, ["decision", "capital_change_recommended"]) is False
    )

    check_results["FEATURE_CONDITIONED_RESEARCH_CONTRACT_READY_12_OF_12"] = {
        "pass": feature_contract_ok,
        "status": feature_builder.get("builder_status"),
        "details": {
            "contract_id": safe_get(feature_builder, ["contract", "contract_id"]),
            "policy_key": safe_get(feature_builder, ["contract", "policy_context", "policy_key"]),
            "candidate_generation_allowed_now": safe_get(feature_builder, ["contract", "required_runner_behavior", "candidate_generation_allowed_now"]),
            "family_release_allowed_now": safe_get(feature_builder, ["contract", "required_runner_behavior", "family_release_allowed_now"]),
        },
    }

    # Future chain: expected but not yet run.
    future_required_steps = [
        "FEATURE_CONDITIONED_RESEARCH_RUNNER_PASS",
        "FEATURE_CONDITIONED_RESEARCH_EVALUATOR_PASS",
        "NEW_CANDIDATE_CONTRACT_PREFLIGHT_PASS",
        "FULL_UNIVERSE_BACKTEST_PASS",
        "TRAIN_OOS_VALIDATION_PASS",
        "STRICT_12_OF_12_MONTH_STABILITY_PASS",
        "COST_SLIPPAGE_SENSITIVITY_PASS",
        "SYMBOL_CONCENTRATION_RISK_PASS",
        "REGIME_BUCKET_DIAGNOSTIC_PASS",
        "RISK_AND_CAPITAL_SAFETY_PASS",
        "MANUAL_OR_AI_REVIEW_PASS_NON_OVERRIDE",
        "FINAL_RELEASE_GATE_PASS",
    ]

    for step in future_required_steps:
        check_results[step] = {
            "pass": False,
            "status": "NOT_RUN_YET",
            "details": {
                "required_before_any_candidate_family_runtime_capital_action": True,
            },
        }

    required_chain = make_required_chain()
    failed_checks = [k for k, v in check_results.items() if v.get("pass") is not True]
    passed_checks = [k for k, v in check_results.items() if v.get("pass") is True]

    candidate_generation_allowed = False
    candidate_contract_allowed = False
    family_release_allowed = False
    runtime_change_allowed = False
    capital_change_allowed = False
    active_paper_allowed = False
    live_allowed = False
    real_orders_allowed = False

    if critical:
        guard_status = "ACTION_PREREQUISITE_GUARD_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_PREREQUISITE_INPUTS"
        reason = "; ".join(critical)
    else:
        guard_status = "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "RUN_FEATURE_CONDITIONED_RESEARCH_RUNNER_NEXT_KEEP_ALL_ACTIONS_BLOCKED"
        reason = f"passed_checks={len(passed_checks)}; failed_or_not_run_checks={len(failed_checks)}; all_actions_blocked=True"

    prerequisite_policy = {
        "policy_schema": "edge_factory_os_action_prerequisite_policy_v1",
        "created_at_utc": NOW.isoformat(),
        "policy_key": "ACTION_PREREQUISITE_FULL_CHAIN_REQUIRED_V1",
        "meaning": (
            "No candidate generation, candidate contract, family release, runtime mutation, capital change, active paper, "
            "live action, or real order is allowed until the full prerequisite chain passes."
        ),
        "required_chain": required_chain,
        "hard_rule": {
            "single_good_result_never_enough": True,
            "feature_signal_never_enough": True,
            "backtest_alone_never_enough": True,
            "ai_or_manual_review_never_overrides_failed_tests": True,
            "strict_12_of_12_required_but_not_alone_sufficient": True,
        },
        "current_authorization": {
            "candidate_generation_allowed": candidate_generation_allowed,
            "candidate_contract_allowed": candidate_contract_allowed,
            "family_release_allowed": family_release_allowed,
            "runtime_change_allowed": runtime_change_allowed,
            "capital_change_allowed": capital_change_allowed,
            "active_paper_allowed": active_paper_allowed,
            "live_allowed": live_allowed,
            "real_orders_allowed": real_orders_allowed,
        },
    }

    dump_json(POLICY_OUT, prerequisite_policy)

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "guard_status": guard_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "policy_written": True,
        "policy_latest_path": str(POLICY_OUT),

        "passed_checks": passed_checks,
        "failed_or_not_run_checks": failed_checks,
        "check_results": check_results,
        "required_chain": required_chain,

        "authorization": {
            "candidate_generation_allowed": candidate_generation_allowed,
            "candidate_contract_allowed": candidate_contract_allowed,
            "family_release_allowed": family_release_allowed,
            "runtime_change_allowed": runtime_change_allowed,
            "capital_change_allowed": capital_change_allowed,
            "active_paper_allowed": active_paper_allowed,
            "live_allowed": live_allowed,
            "real_orders_allowed": real_orders_allowed,
        },

        "next_required_work_order": [
            "Run feature-conditioned research runner under STRICT_MONTH_STABILITY_12_OF_12.",
            "Evaluate feature-conditioned research results.",
            "Only if evaluator justifies it, build a new candidate contract preflight guard.",
            "Then full-universe backtest, train/OOS, strict 12/12, cost/slippage, symbol concentration, regime buckets, risk/capital, manual/AI review, final release gate.",
            "Until all of that passes, all action flags remain false.",
        ],

        "release_gate_feed": {
            "ACTION_PREREQUISITE_GUARD_ACTIVE": severity != "CRITICAL",
            "FULL_CHAIN_REQUIRED_BEFORE_ACTION": True,
            "PASSED_CHECK_COUNT": len(passed_checks),
            "FAILED_OR_NOT_RUN_CHECK_COUNT": len(failed_checks),
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "ACTIVE_PAPER_ALLOWED": False,
            "LIVE_ALLOWED": False,
            "REAL_ORDERS_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_GUARD": False,
            "status": guard_status,
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
            "next_module": "edge_factory_os_feature_conditioned_research_runner_v1.py",
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
            "execution_performed": False,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "action_prerequisite_guard_v1_state.json"
    out_md = RUN_DIR / "action_prerequisite_guard_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS ACTION PREREQUISITE GUARD v1

guard_status: {guard_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

policy_written: True  
policy_latest_path: {POLICY_OUT}

## Authorization

{json.dumps(result["authorization"], indent=2, default=str)}

## Passed Checks

{json.dumps(passed_checks, indent=2, default=str)}

## Failed Or Not Run Checks

{json.dumps(failed_checks, indent=2, default=str)}

## Next Required Work Order

{json.dumps(result["next_required_work_order"], indent=2, default=str)}

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
execution_performed: False

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS ACTION PREREQUISITE GUARD v1")
    print("=" * 100)
    print(f"guard_status: {guard_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("AUTHORIZATION")
    print("-" * 100)
    print(json.dumps(result["authorization"], indent=2, default=str))
    print()
    print("CHECK SUMMARY")
    print("-" * 100)
    print(f"passed_check_count: {len(passed_checks)}")
    print(f"failed_or_not_run_check_count: {len(failed_checks)}")
    print("passed_checks:")
    for x in passed_checks:
        print(f"  {x}")
    print("failed_or_not_run_checks:")
    for x in failed_checks:
        print(f"  {x}")
    print()
    print("NEXT REQUIRED WORK ORDER")
    print("-" * 100)
    for x in result["next_required_work_order"]:
        print(f"- {x}")
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
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
