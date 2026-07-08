from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_feature_conditioned_research_contract_builder_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

POLICY_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_strict_month_stability_policy_guard_v2"
    / "strict_month_stability_policy_guard_v2_latest.json"
)

MONTH_FIRST_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_first_feature_discovery_evaluator_v1"
    / "month_first_feature_discovery_evaluator_latest.json"
)

MONTH_FIRST_RUNNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_first_feature_discovery_runner_v1"
    / "month_first_feature_discovery_runner_latest.json"
)

MONTH_FIRST_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "month_first_feature_discovery_contract_latest.json"
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
RUN_DIR = OUT_ROOT / f"feature_conditioned_research_contract_builder_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "feature_conditioned_research_contract_builder_latest.json"
LATEST_MD = OUT_ROOT / "feature_conditioned_research_contract_builder_latest.md"

CONTRACT_ROOT = BASE_DIR / "edge_factory_os_research_direction_contracts"
CONTRACT_LATEST = CONTRACT_ROOT / "feature_conditioned_research_contract_latest.json"


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


def select_features(month_eval: Dict[str, Any]) -> Dict[str, Any]:
    summary = month_eval.get("feature_signal_summary") or {}
    top_scored = summary.get("top_scored_features") or []
    top_good = summary.get("top_good_regime_features") or []
    top_bad = summary.get("top_bad_regime_features") or []

    def clean_feature(row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "feature": row.get("feature"),
            "label": row.get("label"),
            "threshold": row.get("threshold"),
            "direction": row.get("direction"),
            "classification": row.get("classification"),
            "diagnostic_score": row.get("diagnostic_score"),
            "selected_month_count": row.get("selected_month_count"),
            "selected_positive_month_rate": row.get("selected_positive_month_rate"),
            "selected_mean_label": row.get("selected_mean_label"),
            "excluded_mean_label": row.get("excluded_mean_label"),
            "good_regime_signal": row.get("good_regime_signal"),
            "bad_regime_signal": row.get("bad_regime_signal"),
            "tiny_sample": row.get("tiny_sample"),
            "month_sample_ok": row.get("month_sample_ok"),
        }

    cleaned_top = [clean_feature(x) for x in top_scored if isinstance(x, dict)]
    cleaned_good = [clean_feature(x) for x in top_good if isinstance(x, dict)]
    cleaned_bad = [clean_feature(x) for x in top_bad if isinstance(x, dict)]

    # Keep diagnostic features only. The runner/evaluator must retest them, not assume validity.
    usable = []
    for row in cleaned_top:
        if not row.get("feature"):
            continue
        if row.get("tiny_sample") is True:
            # Tiny samples are allowed only as warnings, not as primary contract filters.
            continue
        if row.get("classification") in {"FEATURE_DIAGNOSTIC_SIGNAL_STRONG", "FEATURE_DIAGNOSTIC_SIGNAL_MODERATE"}:
            usable.append(row)

    # Deduplicate by feature + threshold + direction.
    seen = set()
    deduped = []
    for row in usable:
        key = (row.get("feature"), row.get("threshold"), row.get("direction"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    return {
        "top_scored_features": cleaned_top[:20],
        "top_good_regime_features": cleaned_good[:10],
        "top_bad_regime_features": cleaned_bad[:10],
        "usable_feature_conditions": deduped[:12],
    }


def build_contract(
    policy: Dict[str, Any],
    policy_guard: Dict[str, Any],
    month_eval: Dict[str, Any],
    month_runner: Dict[str, Any],
    month_contract: Dict[str, Any],
    blocklist: Dict[str, Any],
    lesson_index: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_hashes = extract_blocked_hashes(blocklist)
    lesson_ids = extract_lesson_ids(lesson_index)

    feature_pack = select_features(month_eval)

    contract_core = {
        "research_key": "FEATURE_CONDITIONED_RESEARCH_V1",
        "policy_key": policy.get("policy_key"),
        "blocked_hashes": blocked_hashes,
        "usable_feature_conditions": feature_pack.get("usable_feature_conditions"),
        "month_first_eval_status": month_eval.get("evaluator_status"),
    }

    contract_hash = stable_hash(contract_core)
    contract_id = f"FEATURE_CONDITIONED_RESEARCH_CONTRACT_V1_{contract_hash}_{NOW.strftime('%Y%m%d_%H%M%S')}"

    panel_path = month_runner.get("panel_path")
    outputs = month_runner.get("outputs") or {}

    contract = {
        "contract_schema": "edge_factory_os_research_direction_contract_v2",
        "contract_id": contract_id,
        "contract_hash": contract_hash,
        "created_at_utc": NOW.isoformat(),

        "research_key": "FEATURE_CONDITIONED_RESEARCH_V1",
        "contract_type": "DIAGNOSTIC_ONLY_FEATURE_CONDITIONED_RESEARCH",

        "purpose": (
            "Define a diagnostic-only research contract that retests month-first feature signals under the hardened "
            "STRICT_MONTH_STABILITY_12_OF_12 policy. This contract does not create a candidate, family, paper route, "
            "runtime patch, live action, or capital change."
        ),

        "policy_context": {
            "policy_key": policy.get("policy_key"),
            "policy_guard_status": policy_guard.get("guard_status"),
            "min_active_months": safe_get(policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(policy, ["release_requirement", "min_positive_months"], 12),
            "min_positive_month_rate": safe_get(policy, ["release_requirement", "min_positive_month_rate"], 1.0),
            "strict_11_of_12_deprecated_for_release": safe_get(
                policy,
                ["explicitly_deprecated_for_release", "strict_11_of_12_policy"],
                True,
            ),
            "loose_055_month_rate_deprecated_for_release": safe_get(
                policy,
                ["explicitly_deprecated_for_release", "positive_month_rate_gte_0_55_only"],
                True,
            ),
            "hard_requirement": (
                "Any future candidate or family release must have at least 12 active months and 12 positive months. "
                "11/12 is insufficient."
            ),
        },

        "source_month_first_evidence": {
            "month_first_contract_id": month_contract.get("contract_id"),
            "month_first_runner_status": month_runner.get("runner_status"),
            "month_first_evaluator_status": month_eval.get("evaluator_status"),
            "runner_summary": month_eval.get("runner_summary"),
            "feature_signal_summary": month_eval.get("feature_signal_summary"),
            "release_gate_feed": month_eval.get("release_gate_feed"),
            "important_warning": (
                "Strong feature signals are diagnostic only. Diagnostic labels are not live features and cannot be used "
                "directly as release/candidate evidence."
            ),
        },

        "lesson_memory_context": {
            "blocked_route_hashes": blocked_hashes,
            "known_lesson_ids": lesson_ids,
            "blocked_route_reuse_allowed": False,
            "must_not_repeat": [
                "90466e4144914fbc full-universe failure route",
                "85f9e6a4accb14c7 strict month-stability failure route",
                "strict scanner v1 failed templates as direct candidate/release routes",
                "positive_month_rate >= 0.55",
                "11/12 positive months",
                "manual bad-month blacklist",
                "manual symbol blacklist",
                "paper-ledger-only validation",
            ],
        },

        "input_artifacts": {
            "panel_path": panel_path,
            "month_feature_table_csv": outputs.get("month_feature_table_csv"),
            "feature_rankings_json": outputs.get("feature_rankings_json"),
            "panel_rows": month_runner.get("panel_rows"),
            "panel_symbol_count": month_runner.get("panel_symbol_count"),
            "panel_start": month_runner.get("panel_start"),
            "panel_end": month_runner.get("panel_end"),
            "must_use_full_1y_okx_swap_panel": True,
        },

        "feature_conditions_to_retest": {
            "usable_feature_conditions": feature_pack.get("usable_feature_conditions"),
            "top_scored_features": feature_pack.get("top_scored_features"),
            "top_good_regime_features": feature_pack.get("top_good_regime_features"),
            "top_bad_regime_features": feature_pack.get("top_bad_regime_features"),
            "rules": [
                "Each feature condition must be treated as a hypothesis, not a strategy.",
                "Tiny-sample feature groups cannot become primary filters.",
                "Bad-regime features can only be used as avoidance hypotheses after full retest.",
                "Good-regime features can only be used as inclusion hypotheses after full retest.",
                "No feature may use future PnL or post-outcome information as live input.",
            ],
        },

        "required_runner_behavior": {
            "future_module": "edge_factory_os_feature_conditioned_research_runner_v1.py",
            "diagnostic_or_research_only": True,
            "candidate_generation_allowed_now": False,
            "candidate_contract_allowed_now": False,
            "family_release_allowed_now": False,
            "promotion_allowed_now": False,
            "runtime_change_allowed_now": False,
            "capital_change_allowed_now": False,
            "must_retest_feature_conditions_on_full_panel": True,
            "must_report_month_count_and_positive_month_count": True,
            "must_require_12_of_12_for_any_future_candidate": True,
            "must_reject_11_of_12_as_release_quality": True,
            "must_output_research_scoreboard": True,
            "must_not_patch_runtime": True,
        },

        "required_validation_policy_for_any_future_candidate": {
            "policy_key_required": "STRICT_MONTH_STABILITY_12_OF_12",
            "min_active_months": 12,
            "min_positive_months": 12,
            "min_positive_month_rate": 1.0,
            "route_hash_not_in_blocklist": True,
            "full_universe_backtest_required": True,
            "train_oos_validation_required": True,
            "cost_slippage_sensitivity_required": True,
            "symbol_concentration_required": True,
            "manual_or_ai_review_cannot_override_failed_tests": True,
            "candidate_generation_still_not_allowed_by_this_contract": True,
        },

        "expected_next_module": {
            "module_name": "edge_factory_os_feature_conditioned_research_runner_v1.py",
            "purpose": (
                "Retest feature-conditioned hypotheses under STRICT_MONTH_STABILITY_12_OF_12 and output a research "
                "scoreboard. The runner cannot create/release/promote a candidate or mutate runtime/capital."
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

    policy = load_json(POLICY_LATEST)
    policy_guard = load_json(POLICY_GUARD_V2_LATEST)
    month_eval = load_json(MONTH_FIRST_EVAL_LATEST)
    month_runner = load_json(MONTH_FIRST_RUNNER_LATEST)
    month_contract = load_json(MONTH_FIRST_CONTRACT_LATEST)
    blocklist = load_json(BLOCKLIST_PATH)
    lesson_index = load_json(LESSON_INDEX_PATH)

    if not isinstance(policy, dict):
        critical.append("strict_month_stability_policy_latest_missing")
        policy = {}

    if not isinstance(policy_guard, dict):
        critical.append("strict_month_stability_policy_guard_v2_latest_missing")
        policy_guard = {}

    if not isinstance(month_eval, dict):
        critical.append("month_first_feature_discovery_evaluator_latest_missing")
        month_eval = {}

    if not isinstance(month_runner, dict):
        critical.append("month_first_feature_discovery_runner_latest_missing")
        month_runner = {}

    if not isinstance(month_contract, dict):
        critical.append("month_first_feature_discovery_contract_latest_missing")
        month_contract = {}

    if not isinstance(blocklist, dict):
        critical.append("candidate_route_blocklist_missing")
        blocklist = {}

    if not isinstance(lesson_index, dict):
        attention.append("lesson_index_missing")
        lesson_index = {}

    if policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"policy_not_12_of_12:{policy.get('policy_key')}")

    if safe_get(policy, ["release_requirement", "min_active_months"]) != 12:
        critical.append("policy_min_active_months_not_12")

    if safe_get(policy, ["release_requirement", "min_positive_months"]) != 12:
        critical.append("policy_min_positive_months_not_12")

    if float(safe_get(policy, ["release_requirement", "min_positive_month_rate"], 0.0)) != 1.0:
        critical.append("policy_min_positive_month_rate_not_1_0")

    if policy_guard.get("guard_status") != "STRICT_MONTH_STABILITY_POLICY_GUARD_V2_ACTIVE_12_OF_12":
        critical.append(f"policy_guard_v2_not_active:{policy_guard.get('guard_status')}")

    if month_eval.get("evaluator_status") != "MONTH_FIRST_FEATURE_DISCOVERY_EVALUATOR_FEATURE_CONTRACT_RECOMMENDED":
        critical.append(f"month_first_eval_not_feature_contract_recommended:{month_eval.get('evaluator_status')}")

    if safe_get(month_eval, ["decision", "candidate_generation_recommended_now"]) is not False:
        critical.append("month_first_eval_allows_candidate_generation_unexpectedly")

    if safe_get(month_eval, ["decision", "family_release_recommended"]) is not False:
        critical.append("month_first_eval_allows_family_release_unexpectedly")

    if month_runner.get("runner_status") != "MONTH_FIRST_FEATURE_DISCOVERY_RUNNER_COMPLETE":
        critical.append(f"month_first_runner_not_complete:{month_runner.get('runner_status')}")

    blocked_hashes = extract_blocked_hashes(blocklist)
    for h in ["90466e4144914fbc", "85f9e6a4accb14c7"]:
        if h not in blocked_hashes:
            attention.append(f"expected_blocked_hash_missing:{h}")

    contract = None
    contract_written = False

    if critical:
        builder_status = "FEATURE_CONDITIONED_RESEARCH_CONTRACT_BUILDER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_FEATURE_CONDITIONED_CONTRACT"
        reason = "; ".join(critical)

    else:
        contract = build_contract(
            policy=policy,
            policy_guard=policy_guard,
            month_eval=month_eval,
            month_runner=month_runner,
            month_contract=month_contract,
            blocklist=blocklist,
            lesson_index=lesson_index,
        )

        contract_path = RUN_DIR / f"{contract['contract_id']}.json"
        dump_json(contract_path, contract)
        dump_json(CONTRACT_LATEST, contract)

        contract["contract_path"] = str(contract_path)
        contract["contract_latest_path"] = str(CONTRACT_LATEST)

        builder_status = "FEATURE_CONDITIONED_RESEARCH_CONTRACT_READY_12_OF_12"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_FEATURE_CONDITIONED_RESEARCH_RUNNER"
        reason = (
            f"contract_id={contract['contract_id']}; "
            "policy=STRICT_MONTH_STABILITY_12_OF_12; "
            "candidate_generation_allowed=False"
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

        "sources": {
            "policy_latest": str(POLICY_LATEST),
            "policy_guard_v2_latest": str(POLICY_GUARD_V2_LATEST),
            "month_first_eval": str(MONTH_FIRST_EVAL_LATEST),
            "month_first_runner": str(MONTH_FIRST_RUNNER_LATEST),
            "month_first_contract": str(MONTH_FIRST_CONTRACT_LATEST),
            "blocklist": str(BLOCKLIST_PATH),
            "lesson_index": str(LESSON_INDEX_PATH),
        },

        "release_gate_feed": {
            "FEATURE_CONDITIONED_RESEARCH_CONTRACT_BUILT": contract_written,
            "STRICT_MONTH_STABILITY_POLICY_KEY": "STRICT_MONTH_STABILITY_12_OF_12" if contract_written else None,
            "MIN_ACTIVE_MONTHS": 12,
            "MIN_POSITIVE_MONTHS": 12,
            "MIN_POSITIVE_MONTH_RATE": 1.0,
            "CANDIDATE_GENERATION_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
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
            "repeat_blocked_routes_recommended": False,
            "next_module": "edge_factory_os_feature_conditioned_research_runner_v1.py" if contract_written else None,
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

    out_json = RUN_DIR / "feature_conditioned_research_contract_builder_v1_state.json"
    out_md = RUN_DIR / "feature_conditioned_research_contract_builder_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FEATURE CONDITIONED RESEARCH CONTRACT BUILDER v1

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
policy_key: {safe_get(contract or {}, ["policy_context", "policy_key"])}  
min_active_months: {safe_get(contract or {}, ["policy_context", "min_active_months"])}  
min_positive_months: {safe_get(contract or {}, ["policy_context", "min_positive_months"])}  
min_positive_month_rate: {safe_get(contract or {}, ["policy_context", "min_positive_month_rate"])}  
candidate_generation_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "candidate_generation_allowed_now"])}  
candidate_contract_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "candidate_contract_allowed_now"])}  
family_release_allowed_now: {safe_get(contract or {}, ["required_runner_behavior", "family_release_allowed_now"])}  
next_module: {safe_get(contract or {}, ["expected_next_module", "module_name"])}

## Feature Conditions To Retest

{json.dumps(safe_get(contract or {}, ["feature_conditions_to_retest", "usable_feature_conditions"]), indent=2, default=str)[:16000]}

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
    print("EDGE FACTORY OS FEATURE CONDITIONED RESEARCH CONTRACT BUILDER v1")
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
        print(f"policy_key: {safe_get(contract, ['policy_context', 'policy_key'])}")
        print(f"min_active_months: {safe_get(contract, ['policy_context', 'min_active_months'])}")
        print(f"min_positive_months: {safe_get(contract, ['policy_context', 'min_positive_months'])}")
        print(f"min_positive_month_rate: {safe_get(contract, ['policy_context', 'min_positive_month_rate'])}")
        print(f"usable_feature_condition_count: {len(safe_get(contract, ['feature_conditions_to_retest', 'usable_feature_conditions'], []) or [])}")
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
