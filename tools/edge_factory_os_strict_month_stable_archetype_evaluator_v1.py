from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_strict_month_stable_archetype_evaluator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

SCANNER_LATEST = (
    BASE_DIR
    / "edge_factory_os_strict_month_stable_archetype_scanner_v1"
    / "strict_month_stable_archetype_scanner_latest.json"
)

QUEUE_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_new_research_direction_queue_v2"
    / "new_research_direction_queue_v2_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"strict_month_stable_archetype_evaluator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "strict_month_stable_archetype_evaluator_latest.json"
LATEST_MD = OUT_ROOT / "strict_month_stable_archetype_evaluator_latest.md"


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


def fnum(v: Any, default=None):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def inum(v: Any, default=0):
    try:
        if v is None:
            return default
        return int(float(v))
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def pick_next_direction(queue_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    directions = queue_state.get("directions")
    if not isinstance(directions, list):
        return None

    # RD2_01 was just tried. Prefer RD2_02 next: month-first feature discovery.
    for d in directions:
        if isinstance(d, dict) and d.get("research_key") == "RD2_02_MONTH_FIRST_FEATURE_DISCOVERY":
            return d

    valid = [
        d for d in directions
        if isinstance(d, dict)
        and d.get("status") == "QUEUED_READ_ONLY_RESEARCH"
        and d.get("candidate_generation_allowed_now") is False
    ]

    valid.sort(key=lambda x: int(x.get("priority") or 0), reverse=True)
    return valid[0] if valid else None


def summarize_top_failures(top_scoreboard: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = [x for x in top_scoreboard if isinstance(x, dict)]

    if not rows:
        return {
            "available": False,
            "reason": "top_scoreboard_empty",
        }

    top = rows[0]
    positive_month_counts = [
        inum(safe_get(r, ["all", "positive_month_count"]))
        for r in rows
    ]
    mean_net_values = [
        fnum(safe_get(r, ["all", "mean_net_bps"]))
        for r in rows
        if fnum(safe_get(r, ["all", "mean_net_bps"])) is not None
    ]
    pf_values = [
        fnum(safe_get(r, ["all", "profit_factor"]))
        for r in rows
        if fnum(safe_get(r, ["all", "profit_factor"])) is not None
    ]

    return {
        "available": True,
        "top_archetype": top.get("archetype_key"),
        "top_route_hash": top.get("route_hash"),
        "top_scanner_score": top.get("scanner_score"),
        "top_trade_count": safe_get(top, ["all", "trade_count"]),
        "top_month_count": safe_get(top, ["all", "month_count"]),
        "top_positive_month_count": safe_get(top, ["all", "positive_month_count"]),
        "top_positive_month_rate": safe_get(top, ["all", "positive_month_rate"]),
        "top_mean_net_bps": safe_get(top, ["all", "mean_net_bps"]),
        "top_profit_factor": safe_get(top, ["all", "profit_factor"]),
        "top_failed_checks": top.get("failed_checks"),
        "max_positive_month_count_in_top_rows": max(positive_month_counts) if positive_month_counts else None,
        "best_mean_net_bps_in_top_rows": max(mean_net_values) if mean_net_values else None,
        "best_profit_factor_in_top_rows": max(pf_values) if pf_values else None,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    scanner = load_json(SCANNER_LATEST)
    queue_state = load_json(QUEUE_V2_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)

    if not isinstance(scanner, dict):
        critical.append("strict_month_stable_archetype_scanner_latest_missing")
        scanner = {}

    if not isinstance(queue_state, dict):
        attention.append("new_research_direction_queue_v2_latest_missing")
        queue_state = {}

    if not isinstance(strict_policy, dict):
        attention.append("strict_month_stability_policy_latest_missing")
        strict_policy = {}

    if scanner.get("scanner_status") != "STRICT_MONTH_STABLE_ARCHETYPE_SCANNER_COMPLETE":
        critical.append(f"scanner_not_complete:{scanner.get('scanner_status')}")

    if scanner.get("strict_month_pass_count") != 0:
        attention.append(f"strict_month_pass_count_nonzero:{scanner.get('strict_month_pass_count')}")

    if scanner.get("full_preview_pass_count") != 0:
        attention.append(f"full_preview_pass_count_nonzero:{scanner.get('full_preview_pass_count')}")

    if safe_get(scanner, ["release_gate_feed", "RELEASE_PASS_FROM_THIS_SCANNER"]) is not False:
        critical.append("scanner_claimed_release_pass_unexpectedly")

    top_scoreboard = scanner.get("top_scoreboard")
    if not isinstance(top_scoreboard, list):
        top_scoreboard = []

    top_failure_summary = summarize_top_failures(top_scoreboard)

    next_direction = pick_next_direction(queue_state)

    no_strict_found = (
        scanner.get("strict_month_pass_count") == 0
        and scanner.get("full_preview_pass_count") == 0
    )

    findings = []

    if no_strict_found:
        findings.append({
            "finding_id": "SMSA_EVAL_F1_NO_STRICT_ARCHETYPE_FOUND",
            "severity": "HIGH",
            "claim": "Scanner v1 found no archetype template satisfying strict 12-active-month / 11-positive-month stability.",
            "evidence": {
                "rules_tested": scanner.get("rules_tested"),
                "strict_month_pass_count": scanner.get("strict_month_pass_count"),
                "full_preview_pass_count": scanner.get("full_preview_pass_count"),
                "blocked_hash_hit_count": scanner.get("blocked_hash_hit_count"),
            },
        })

    findings.append({
        "finding_id": "SMSA_EVAL_F2_TOP_SCOREBOARD_NOT_CLOSE_TO_RELEASE",
        "severity": "HIGH",
        "claim": "Top scanner rows are not merely failing strict stability; they also show weak/negative economics.",
        "evidence": top_failure_summary,
    })

    findings.append({
        "finding_id": "SMSA_EVAL_F3_MOVE_TO_MONTH_FIRST_OR_EXPAND_SEARCH",
        "severity": "CONTROL",
        "claim": "Next research should not generate a candidate. It should either move to month-first feature discovery or expand the scanner search space.",
        "evidence": {
            "next_recommended_direction": next_direction,
        },
    })

    if critical:
        evaluator_status = "STRICT_MONTH_STABLE_ARCHETYPE_EVALUATOR_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_SCANNER_INPUT"
        reason = "; ".join(critical)

    elif no_strict_found:
        evaluator_status = "STRICT_MONTH_STABLE_ARCHETYPE_EVALUATOR_NO_STRICT_ARCHETYPE_FOUND"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_MONTH_FIRST_FEATURE_DISCOVERY_CONTRACT_OR_EXPAND_SCANNER_V2"
        reason = (
            f"rules_tested={scanner.get('rules_tested')}; "
            f"strict_month_pass_count=0; full_preview_pass_count=0"
        )

    else:
        evaluator_status = "STRICT_MONTH_STABLE_ARCHETYPE_EVALUATOR_REVIEW_STRICT_PASSING_ROWS"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "REVIEW_STRICT_PASSING_ROWS_NO_CANDIDATE_RELEASE"
        reason = (
            f"strict_month_pass_count={scanner.get('strict_month_pass_count')}; "
            f"full_preview_pass_count={scanner.get('full_preview_pass_count')}"
        )

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "evaluator_status": evaluator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "scanner_source": str(SCANNER_LATEST),
        "queue_v2_source": str(QUEUE_V2_LATEST),
        "strict_policy_source": str(STRICT_POLICY_LATEST),

        "scanner_summary": {
            "scanner_status": scanner.get("scanner_status"),
            "rules_tested": scanner.get("rules_tested"),
            "strict_month_pass_count": scanner.get("strict_month_pass_count"),
            "full_preview_pass_count": scanner.get("full_preview_pass_count"),
            "blocked_hash_hit_count": scanner.get("blocked_hash_hit_count"),
            "release_gate_feed": scanner.get("release_gate_feed"),
        },

        "strict_policy": {
            "policy_key": strict_policy.get("policy_key"),
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"], 11),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"], 11 / 12),
            "loose_055_month_rate_deprecated_for_release": safe_get(
                strict_policy,
                ["explicitly_deprecated_for_release", "positive_month_rate_gte_0_55_only"],
                True,
            ),
        },

        "top_failure_summary": top_failure_summary,
        "top_scoreboard_sample": top_scoreboard[:10],
        "findings": findings,

        "next_research_direction": next_direction,

        "release_gate_feed": {
            "STRICT_MONTH_STABLE_ARCHETYPE_EVALUATED": True,
            "STRICT_MONTH_STABLE_ARCHETYPE_FOUND": False if no_strict_found else bool(scanner.get("strict_month_pass_count")),
            "FULL_PREVIEW_PASS_ARCHETYPE_FOUND": False if no_strict_found else bool(scanner.get("full_preview_pass_count")),
            "RELEASE_PASS_FROM_THIS_EVALUATOR": False,
            "status": evaluator_status,
        },

        "decision": {
            "candidate_generation_recommended_now": False,
            "candidate_contract_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "repeat_blocked_routes_recommended": False,
            "scanner_v1_archive_recommended": bool(no_strict_found),
            "next_recommended_research_key": next_direction.get("research_key") if isinstance(next_direction, dict) else None,
            "next_module": "edge_factory_os_month_first_feature_discovery_contract_builder_v1.py" if no_strict_found else None,
            "why_no_action": [
                "scanner_v1_found_no_strict_11_of_12_archetype",
                "top_scoreboard_negative_or_far_from_release",
                "candidate_contract_not_allowed_from_this_evaluator",
                "release_gate_required",
                "no_runtime_or_capital_action_allowed",
            ],
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

    out_json = RUN_DIR / "strict_month_stable_archetype_evaluator_v1_state.json"
    out_md = RUN_DIR / "strict_month_stable_archetype_evaluator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS STRICT MONTH STABLE ARCHETYPE EVALUATOR v1

evaluator_status: {evaluator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

## Scanner Summary

{json.dumps(result["scanner_summary"], indent=2, default=str)}

## Strict Policy

{json.dumps(result["strict_policy"], indent=2, default=str)}

## Top Failure Summary

{json.dumps(top_failure_summary, indent=2, default=str)}

## Next Research Direction

{json.dumps(next_direction, indent=2, default=str)[:12000]}

## Findings

{json.dumps(findings, indent=2, default=str)}

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
    print("EDGE FACTORY OS STRICT MONTH STABLE ARCHETYPE EVALUATOR v1")
    print("=" * 100)
    print(f"evaluator_status: {evaluator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("SCANNER SUMMARY")
    print("-" * 100)
    print(result["scanner_summary"])
    print()
    print("TOP FAILURE SUMMARY")
    print("-" * 100)
    print(json.dumps(top_failure_summary, indent=2, default=str))
    print()
    print("NEXT RESEARCH DIRECTION")
    print("-" * 100)
    if isinstance(next_direction, dict):
        print(f"research_key: {next_direction.get('research_key')}")
        print(f"direction_id: {next_direction.get('direction_id')}")
        print(f"priority: {next_direction.get('priority')}")
        print(f"primary_question: {next_direction.get('primary_question')}")
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
