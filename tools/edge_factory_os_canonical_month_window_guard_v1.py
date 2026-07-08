from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_canonical_month_window_guard_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

FEATURE_RUNNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_feature_conditioned_research_runner_v1"
    / "feature_conditioned_research_runner_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"canonical_month_window_guard_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "canonical_month_window_guard_latest.json"
LATEST_MD = OUT_ROOT / "canonical_month_window_guard_latest.md"

POLICY_ROOT = BASE_DIR / "edge_factory_os_policy_guards"
CANONICAL_POLICY_LATEST = POLICY_ROOT / "canonical_month_window_policy_latest.json"


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


def parse_month_key(month: str):
    try:
        y, m = str(month).split("-")
        return int(y), int(m)
    except Exception:
        return 9999, 99


def canonicalize_months(months: List[str]) -> Dict[str, Any]:
    clean = sorted(set(str(x) for x in months if x), key=parse_month_key)

    raw_count = len(clean)

    if raw_count <= 12:
        canonical = clean[:]
        boundary_partial = []
        method = "raw_count_lte_12_no_trim"
    else:
        # For 1Y rolling panels spanning partial boundary months, raw buckets are often 13.
        # Use the last 12 calendar buckets as canonical policy months, and mark the first as boundary partial.
        canonical = clean[-12:]
        boundary_partial = clean[:-12]
        method = "trim_oldest_boundary_months_to_last_12_calendar_buckets"

    return {
        "raw_calendar_months": clean,
        "raw_calendar_month_count": raw_count,
        "canonical_policy_months": canonical,
        "canonical_policy_month_count": len(canonical),
        "boundary_partial_months": boundary_partial,
        "canonicalization_method": method,
    }


def extract_months_from_runner(runner: Dict[str, Any]) -> Dict[str, Any]:
    months = set()

    best = runner.get("best_result")
    if isinstance(best, dict):
        for k in ["selected_months", "excluded_months"]:
            vals = best.get(k)
            if isinstance(vals, list):
                for v in vals:
                    months.add(str(v))

    for path in [
        ["best_result", "all_stats", "monthly_total_net_bps"],
        ["best_result", "selected_stats", "monthly_total_net_bps"],
        ["best_result", "excluded_stats", "monthly_total_net_bps"],
    ]:
        obj = safe_get(runner, path)
        if isinstance(obj, dict):
            for k in obj.keys():
                months.add(str(k))

    # Fallback: inspect top results.
    top = runner.get("top_results")
    if isinstance(top, list):
        for row in top[:30]:
            if not isinstance(row, dict):
                continue
            for k in ["selected_months", "excluded_months"]:
                vals = row.get(k)
                if isinstance(vals, list):
                    for v in vals:
                        months.add(str(v))

    return canonicalize_months(list(months))


def build_policy(strict_policy: Dict[str, Any], canonical: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "policy_schema": "edge_factory_os_canonical_month_window_policy_v1",
        "created_at_utc": NOW.isoformat(),
        "policy_key": "CANONICAL_MONTH_WINDOW_12_POLICY_MONTHS",
        "purpose": (
            "Separate raw calendar month buckets from canonical policy months. A full rolling 1Y panel may produce "
            "13 raw calendar buckets due partial boundary months, but strict month-stability validation must use exactly "
            "12 canonical policy months."
        ),
        "raw_calendar_month_count_is_not_release_month_count": True,
        "release_requirement": {
            "canonical_policy_month_count_must_equal": 12,
            "canonical_positive_month_count_must_equal": 12,
            "canonical_negative_month_count_must_equal": 0,
            "canonical_positive_month_rate_must_equal": 1.0,
            "strict_month_policy_key_required": "STRICT_MONTH_STABILITY_12_OF_12",
            "strict_month_policy_snapshot": {
                "policy_key": strict_policy.get("policy_key"),
                "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"]),
                "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"]),
                "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"]),
            },
        },
        "canonicalization_rule": {
            "if_raw_calendar_month_count_lte_12": "use_raw_months_as_canonical",
            "if_raw_calendar_month_count_gt_12": "trim_oldest_boundary_partial_months_to_last_12_calendar_buckets",
            "boundary_partial_months_must_be_reported": True,
            "13_raw_months_does_not_mean_13_policy_months": True,
            "13_raw_months_with_12_positive_months_is_not_automatic_pass": True,
        },
        "latest_observed_months": canonical,
        "hard_blocks": [
            "any_module_using_raw_calendar_month_count_as_release_month_count",
            "any_module_accepting_13_raw_months_as policy pass without canonicalization",
            "any_module_allowing_13_months_12_positive_1_negative_as strict 12/12 pass",
            "any_candidate_with_canonical_policy_month_count_not_equal_12",
            "any_candidate_with_canonical_positive_month_count_not_equal_12",
            "any_candidate_with_canonical_negative_month_count_not_equal_0",
        ],
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    runner = load_json(FEATURE_RUNNER_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)

    if not isinstance(runner, dict):
        critical.append("feature_conditioned_research_runner_latest_missing")
        runner = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_month_stability_policy_latest_missing")
        strict_policy = {}

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_12_OF_12":
        critical.append(f"strict_policy_not_12_of_12:{strict_policy.get('policy_key')}")

    if runner.get("runner_status") not in {
        "FEATURE_CONDITIONED_RESEARCH_RUNNER_NO_STRICT_12_OF_12_SIGNAL_FOUND",
        "FEATURE_CONDITIONED_RESEARCH_RUNNER_STRICT_12_OF_12_SIGNAL_FOUND",
    }:
        attention.append(f"unexpected_runner_status:{runner.get('runner_status')}")

    canonical = extract_months_from_runner(runner)

    raw_count = canonical["raw_calendar_month_count"]
    canonical_count = canonical["canonical_policy_month_count"]

    if raw_count == 0:
        critical.append("no_months_detected_from_feature_runner")

    if canonical_count != 12:
        attention.append(f"canonical_policy_month_count_not_12:{canonical_count}")

    policy = build_policy(strict_policy, canonical)

    if critical:
        guard_status = "CANONICAL_MONTH_WINDOW_GUARD_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MONTH_SOURCE_INPUTS"
        reason = "; ".join(critical)
        policy_written = False
    else:
        dump_json(CANONICAL_POLICY_LATEST, policy)

        guard_status = "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "PATCH_DOWNSTREAM_EVALUATORS_TO_REQUIRE_CANONICAL_12_MONTH_WINDOW"
        reason = (
            f"raw_calendar_month_count={raw_count}; "
            f"canonical_policy_month_count={canonical_count}; "
            f"boundary_partial_months={canonical['boundary_partial_months']}"
        )
        policy_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "guard_status": guard_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "feature_runner_source": str(FEATURE_RUNNER_LATEST),
        "strict_policy_source": str(STRICT_POLICY_LATEST),

        "policy_written": policy_written,
        "canonical_policy_latest_path": str(CANONICAL_POLICY_LATEST),
        "canonical_month_policy": policy,

        "month_window": canonical,

        "release_gate_feed": {
            "CANONICAL_MONTH_WINDOW_GUARD_ACTIVE": policy_written,
            "RAW_CALENDAR_MONTH_COUNT": raw_count,
            "CANONICAL_POLICY_MONTH_COUNT": canonical_count,
            "BOUNDARY_PARTIAL_MONTHS": canonical["boundary_partial_months"],
            "CANONICAL_12_MONTH_POLICY_REQUIRED": True,
            "CANDIDATE_GENERATION_ALLOWED": False,
            "FAMILY_RELEASE_ALLOWED": False,
            "RUNTIME_CHANGE_ALLOWED": False,
            "CAPITAL_CHANGE_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_GUARD": False,
            "status": guard_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "next_module": "edge_factory_os_feature_conditioned_research_evaluator_v1.py",
            "required_patch": "all downstream evaluators must use canonical_policy_month_count==12, not raw_calendar_month_count",
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

    out_json = RUN_DIR / "canonical_month_window_guard_v1_state.json"
    out_md = RUN_DIR / "canonical_month_window_guard_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS CANONICAL MONTH WINDOW GUARD v1

guard_status: {guard_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

policy_written: {policy_written}  
canonical_policy_latest_path: {CANONICAL_POLICY_LATEST}

## Month Window

{json.dumps(canonical, indent=2, default=str)}

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
    print("EDGE FACTORY OS CANONICAL MONTH WINDOW GUARD v1")
    print("=" * 100)
    print(f"guard_status: {guard_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("MONTH WINDOW")
    print("-" * 100)
    print(json.dumps(canonical, indent=2, default=str))
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
