from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_broader_month_feature_engine_contract_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

FEATURE_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_feature_conditioned_research_evaluator_v1"
    / "feature_conditioned_research_evaluator_latest.json"
)

CANONICAL_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_canonical_month_window_guard_v1"
    / "canonical_month_window_guard_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

ACTION_GUARD_LATEST = (
    BASE_DIR
    / "edge_factory_os_action_prerequisite_guard_v1"
    / "action_prerequisite_guard_latest.json"
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

LESSON_INDEX_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "lesson_memory_index.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"broader_month_feature_engine_contract_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "broader_month_feature_engine_contract_builder_latest.json"
LATEST_MD = OUT_ROOT / "broader_month_feature_engine_contract_builder_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "broader_month_feature_engine_contract_latest.json"


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


def stable_hash(obj: Any) -> str:
    text = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


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


def extract_lesson_ids(lesson_index: Dict[str, Any]) -> List[str]:
    lessons = lesson_index.get("lessons")
    if not isinstance(lessons, list):
        return []

    out = []
    for lesson in lessons:
        if isinstance(lesson, dict) and lesson.get("lesson_id"):
            out.append(str(lesson["lesson_id"]))

    return sorted(set(out))


def build_contract(
    feature_eval: Dict[str, Any],
    canonical_guard: Dict[str, Any],
    strict_policy: Dict[str, Any],
    action_guard: Dict[str, Any],
    feature_contract: Dict[str, Any],
    blocklist: Dict[str, Any],
    lesson_index: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_hashes = extract_blocked_hashes(blocklist)
    lesson_ids = extract_lesson_ids(lesson_index)

    contract_core = {
        "research_key": "BROADER_MONTH_FEATURE_ENGINE_V1",
        "source_eval_status": feature_eval.get("evaluator_status"),
        "policy_key": strict_policy.get("policy_key"),
        "canonical_months": safe_get(canonical_guard, ["month_window", "canonical_policy_months"], []),
        "blocked_hashes": blocked_hashes,
    }

    contract_hash = stable_hash(contract_core)
    contract_id = f"BROADER_MONTH_FEATURE_ENGINE_CONTRACT_V1_{contract_hash}_{NOW.strftime('%Y%m%d_%H%M%S')}"

    source_month_table = safe_get(feature_contract, ["input_artifacts", "month_feature_table_csv"])
    source_panel = safe_get(feature_contract, ["input_artifacts", "panel_path"])

    contract = {
        "contract_schema": "edge_factory_os_research_direction_contract_v2",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "created_at_utc": NOW.isoformat(),

        "research_key": "BROADER_MONTH_FEATURE_ENGINE_V1",
        "contract_type": "DIAGNOSTIC_ONLY_BROADER_MONTH_FEATURE_ENGINE",

        "purpose": (
            "Build a broader pre-outcome month feature engine because feature-conditioned research found no canonical "
            "STRICT_MONTH_STABILITY_12_OF_12 signal. This contract expands the feature space and label design without "
            "creating candidates, families, runtime patches, active paper routes, live actions, or capital changes."
        ),

        "source_failure_context": {
            "feature_conditioned_evaluator_status": feature_eval.get("evaluator_status"),
            "feature_conditioned_reason": feature_eval.get("reason"),
            "evaluation_summary": feature_eval.get("evaluation_summary"),
            "best_canonical_result": feature_eval.get("best_canonical_result"),
            "canonical_strict_12_of_12_passes": feature_eval.get("canonical_strict_12_of_12_passes"),
            "release_gate_feed": feature_eval.get("release_gate_feed"),
        },

        "canonical_month_policy_context": {
            "canonical_guard_status": canonical_guard.get("guard_status"),
            "raw_calendar_month_count": safe_get(canonical_guard, ["month_window", "raw_calendar_month_count"]),
            "canonical_policy_month_count": safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"]),
            "canonical_policy_months": safe_get(canonical_guard, ["month_window", "canonical_policy_months"]),
            "boundary_partial_months": safe_get(canonical_guard, ["month_window", "boundary_partial_months"]),
            "canonicalization_method": safe_get(canonical_guard, ["month_window", "canonicalization_method"]),
            "hard_requirement": "Use canonical_policy_month_count==12, never raw_calendar_month_count, for any strict month-stability judgement.",
        },

        "strict_month_policy_context": {
            "policy_key": strict_policy.get("policy_key"),
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"], 12),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"], 1.0),
            "strict_11_of_12_deprecated_for_release": safe_get(
                strict_policy,
                ["explicitly_deprecated_for_release", "strict_11_of_12_policy"],
                True,
            ),
        },

        "action_prerequisite_context": {
            "guard_status": action_guard.get("guard_status"),
            "authorization": action_guard.get("authorization"),
            "failed_or_not_run_checks": action_guard.get("failed_or_not_run_checks"),
            "all_actions_blocked": True,
        },

        "lesson_memory_context": {
            "blocked_route_hashes": blocked_hashes,
            "known_lesson_ids": lesson_ids,
            "blocked_route_reuse_allowed": False,
            "must_not_repeat": [
                "90466e4144914fbc full-universe failure route",
                "85f9e6a4accb14c7 strict month-stability failure route",
                "route-first impulse repairs",
                "strict scanner v1 failed templates as release candidates",
                "feature-conditioned v1 splits that failed canonical 12/12",
                "positive_month_rate >= 0.55",
                "11/12 positive months",
                "13 raw calendar buckets treated as release months",
                "manual bad-month blacklist",
                "manual symbol blacklist",
                "paper-ledger-only validation",
            ],
        },

        "input_artifacts": {
            "source_month_feature_table_csv": source_month_table,
            "source_panel_path": source_panel,
            "source_feature_contract_latest": str(FEATURE_CONTRACT_LATEST),
            "source_feature_eval_latest": str(FEATURE_EVAL_LATEST),
            "must_use_full_1y_okx_swap_panel": True,
            "must_use_canonical_month_window": True,
        },

        "expanded_feature_engine_scope": {
            "goal": (
                "Generate a richer month-level and regime-level pre-outcome feature table that may explain canonical "
                "12/12 stability before any candidate construction."
            ),
            "new_feature_groups": [
                "rolling_3_month_feature_trends",
                "rolling_6_month_feature_trends",
                "month_to_month_feature_change",
                "feature_volatility_of_volatility",
                "breadth_acceleration_and_deceleration",
                "dispersion_compression_expansion",
                "liquidity_regime_change",
                "range_stress_persistence",
                "cross_sectional_tail_risk",
                "symbol_survival_and_universe_health",
                "coin_ret_quantile_structure",
                "market_return_context_interactions",
                "volatility_range_liquidity_interactions",
                "good_month_anti_features",
                "bad_month_avoidance_features",
            ],
            "label_design": [
                "canonical_12_month_diagnostic_labels",
                "per_month_broad_template_labels",
                "bad_month_risk_labels",
                "feature_stability_labels",
                "do_not_use_future_pnl_as_live_feature",
            ],
            "explicitly_disallowed": [
                "future return or PnL as input feature",
                "manual bad-month blacklist",
                "manual symbol blacklist",
                "post-outcome labels as live/paper features",
                "candidate generation from this contract",
                "runtime/capital/live actions from this contract",
            ],
        },

        "required_runner_behavior": {
            "future_module": "edge_factory_os_broader_month_feature_engine_runner_v1.py",
            "diagnostic_or_research_only": True,
            "candidate_generation_allowed_now": False,
            "candidate_contract_allowed_now": False,
            "family_release_allowed_now": False,
            "promotion_allowed_now": False,
            "runtime_change_allowed_now": False,
            "capital_change_allowed_now": False,
            "must_consume_canonical_month_window_guard": True,
            "must_consume_strict_12_of_12_policy": True,
            "must_output_expanded_month_feature_table": True,
            "must_output_feature_family_scoreboard": True,
            "must_output_overfit_warnings": True,
            "must_not_patch_runtime": True,
        },

        "required_validation_policy_for_any_future_candidate": {
            "this_contract_can_not_create_candidate": True,
            "future_candidate_requires_separate_preflight": True,
            "policy_key_required": "STRICT_MONTH_STABILITY_12_OF_12",
            "canonical_policy_month_count_required": 12,
            "canonical_positive_month_count_required": 12,
            "canonical_negative_month_count_required": 0,
            "route_hash_not_in_blocklist": True,
            "full_universe_backtest_required": True,
            "train_oos_validation_required": True,
            "cost_slippage_sensitivity_required": True,
            "symbol_concentration_required": True,
            "risk_and_capital_safety_required": True,
            "final_release_gate_required": True,
        },

        "expected_next_module": {
            "module_name": "edge_factory_os_broader_month_feature_engine_runner_v1.py",
            "purpose": (
                "Build expanded canonical-month feature table and rank broader feature families under strict 12/12. "
                "Runner cannot create candidates/families or mutate runtime/capital."
            ),
            "execution_allowed_after_contract": True,
            "candidate_generation_allowed_after_contract": False,
            "candidate_contract_allowed_after_contract": False,
            "family_release_allowed_after_contract": False,
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
    }

    return contract


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    feature_eval = load_json(FEATURE_EVAL_LATEST)
    canonical_guard = load_json(CANONICAL_GUARD_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    action_guard = load_json(ACTION_GUARD_LATEST)
    feature_contract = load_json(FEATURE_CONTRACT_LATEST)
    blocklist = load_json(BLOCKLIST_PATH)
    lesson_index = load_json(LESSON_INDEX_PATH)

    if not isinstance(feature_eval, dict):
        critical.append("feature_conditioned_research_evaluator_latest_missing")
        feature_eval = {}

    if not isinstance(canonical_guard, dict):
        critical.append("canonical_month_window_guard_latest_missing")
        canonical_guard = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_month_policy_latest_missing")
        strict_policy = {}

    if not isinstance(action_guard, dict):
        critical.append("action_prerequisite_guard_latest_missing")
        action_guard = {}

    if not isinstance(feature_contract, dict):
        critical.append("feature_conditioned_research_contract_latest_missing")
        feature_contract = {}

    if not isinstance(blocklist, dict):
        critical.append("candidate_route_blocklist_missing")
        blocklist = {}

    if not isinstance(lesson_index, dict):
        attention.append("lesson_index_missing")
        lesson_index = {}

    if feature_eval.get("evaluator_status") != "FEATURE_CONDITIONED_RESEARCH_EVALUATOR_NO_CANONICAL_12_OF_12_SIGNAL_FOUND":
        critical.append(f"unexpected_feature_eval_status:{feature_eval.get('evaluator_status')}")

    if safe_get(feature_eval, ["release_gate_feed", "CANONICAL_MONTH_WINDOW_GUARD_CONSUMED"]) is not True:
        critical.append("feature_eval_did_not_consume_canonical_guard")

    if safe_get(feature_eval, ["release_gate_feed", "CANONICAL_STRICT_12_OF_12_SIGNAL_FOUND"]) is not False:
        critical.append("feature_eval_did_not_confirm_no_canonical_12_of_12_signal")

    if safe_get(feature_eval, ["release_gate_feed", "RELEASE_PASS_FROM_THIS_EVALUATOR"]) is not False:
        critical.append("feature_eval_claimed_release_pass_unexpectedly")

    if canonical_guard.get("guard_status") != "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE":
        critical.append(f"canonical_guard_not_active:{canonical_guard.get('guard_status')}")

    if safe_get(canonical_guard, ["month_window", "canonical_policy_month_count"]) != 12:
        critical.append("canonical_policy_month_count_not_12")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if action_guard.get("guard_status") != "ACTION_PREREQUISITE_GUARD_ACTIVE_ACTIONS_BLOCKED":
        critical.append(f"action_guard_not_blocking:{action_guard.get('guard_status')}")

    authorization = action_guard.get("authorization") or {}
    for k, v in authorization.items():
        if v is not False:
            critical.append(f"authorization_not_false:{k}={v}")

    contract = None
    contract_written = False

    if critical:
        builder_status = "BROADER_MONTH_FEATURE_ENGINE_CONTRACT_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_BROADER_FEATURE_ENGINE_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract = build_contract(
            feature_eval=feature_eval,
            canonical_guard=canonical_guard,
            strict_policy=strict_policy,
            action_guard=action_guard,
            feature_contract=feature_contract,
            blocklist=blocklist,
            lesson_index=lesson_index,
        )

        contract_path = RUN_DIR / f"{contract['contract_id']}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "BROADER_MONTH_FEATURE_ENGINE_CONTRACT_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_BROADER_MONTH_FEATURE_ENGINE_RUNNER"
        reason = (
            f"contract_id={contract['contract_id']}; "
            "no_canonical_12_of_12_signal_found_in_feature_conditioned_research"
        )
        contract_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "builder_status": builder_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "contract": contract,
        "contract_written": contract_written,
        "contract_latest_path": str(CONTRACT_LATEST),

        "release_gate_feed": {
            "BROADER_MONTH_FEATURE_ENGINE_CONTRACT_BUILT": contract_written,
            "CANONICAL_MONTH_WINDOW_REQUIRED": True,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12" if contract_written else None,
            "CANDIDATE_GENERATION_ALLOWED": False,
            "CANDIDATE_CONTRACT_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_CONTRACT": False,
            "status": builder_status,
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
            "next_module": "edge_factory_os_broader_month_feature_engine_runner_v1.py" if contract_written else None,
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

    out_json = RUN_DIR / "broader_month_feature_engine_contract_builder_v1_state.json"
    out_md = RUN_DIR / "broader_month_feature_engine_contract_builder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS BROADER MONTH FEATURE ENGINE CONTRACT BUILDER v1

builder_status: {builder_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

contract_written: {contract_written}  
contract_latest_path: {CONTRACT_LATEST}

## Contract Summary

contract_id: {contract.get("contract_id") if contract else None}  
research_key: {contract.get("research_key") if contract else None}  
contract_hash: {contract.get("contract_hash") if contract else None}  
canonical_policy_month_count: {safe_get(contract or {}, ["canonical_month_policy_context", "canonical_policy_month_count"])}  
strict_policy_key: {safe_get(contract or {}, ["strict_month_policy_context", "policy_key"])}  
candidate_generation_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "candidate_generation_allowed_now"])}  
candidate_contract_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "candidate_contract_allowed_now"])}  
family_release_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "family_release_allowed_now"])}  
next_module: {safe_get(contract or {}, ["expected_next_module", "module_name"])}

## Expanded Feature Groups

{json.dumps(safe_get(contract or {}, ["expanded_feature_engine_scope", "new_feature_groups"]), indent=2, default=str)}

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
    print("EDGE FACTORY OS BROADER MONTH FEATURE ENGINE CONTRACT BUILDER v1")
    print("=" * 100)
    print(f"builder_status: {builder_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("CONTRACT")
    print("-" * 100)
    if contract:
        print(f"contract_id: {contract.get('contract_id')}")
        print(f"research_key: {contract.get('research_key')}")
        print(f"contract_hash: {contract.get('contract_hash')}")
        print(f"contract_latest_path: {CONTRACT_LATEST}")
        print(f"canonical_policy_month_count: {safe_get(contract, ['canonical_month_policy_context', 'canonical_policy_month_count'])}")
        print(f"strict_policy_key: {safe_get(contract, ['strict_month_policy_context', 'policy_key'])}")
        print(f"candidate_generation_allowed_now: {safe_get(contract, ['required_runner_behavior', 'candidate_generation_allowed_now'])}")
        print(f"candidate_contract_allowed_now: {safe_get(contract, ['required_runner_behavior', 'candidate_contract_allowed_now'])}")
        print(f"family_release_allowed_now: {safe_get(contract, ['required_runner_behavior', 'family_release_allowed_now'])}")
        print(f"next_module: {safe_get(contract, ['expected_next_module', 'module_name'])}")
    else:
        print(None)
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
