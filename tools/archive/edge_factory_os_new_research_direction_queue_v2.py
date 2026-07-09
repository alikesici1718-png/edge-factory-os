from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_new_research_direction_queue_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

LESSON_INDEX_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "lesson_memory_index.json"
)

BLOCKLIST_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "candidate_route_blocklist.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

STRICT_FAILURE_RECORDER_LATEST = (
    BASE_DIR
    / "edge_factory_os_strict_month_stability_failure_lesson_recorder_v1"
    / "strict_month_stability_failure_lesson_recorder_latest.json"
)

RELEASE_GATE_V4_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_candidate_release_gate_v4"
    / "family_candidate_release_gate_v4_latest.json"
)

UNIVERSE_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"new_research_direction_queue_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "new_research_direction_queue_v2_latest.json"
LATEST_MD = OUT_ROOT / "new_research_direction_queue_v2_latest.md"

RESEARCH_QUEUE_ROOT = BASE_DIR / "edge_factory_os_research_queue"
RESEARCH_QUEUE_INDEX = RESEARCH_QUEUE_ROOT / "research_direction_queue_index_v2.json"


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


def load_queue_index() -> Dict[str, Any]:
    obj = load_json(RESEARCH_QUEUE_INDEX)

    if isinstance(obj, dict):
        if not isinstance(obj.get("directions"), list):
            obj["directions"] = []
        return obj

    return {
        "schema": "edge_factory_os_research_direction_queue_index_v2",
        "created_at_utc": NOW.isoformat(),
        "updated_at_utc": NOW.isoformat(),
        "directions": [],
    }


def direction_id(payload: Dict[str, Any]) -> str:
    key = {
        "research_key": payload.get("research_key"),
        "family_scope": payload.get("family_scope"),
        "primary_question": payload.get("primary_question"),
        "strict_month_policy_required": payload.get("strict_month_policy_required"),
    }
    return f"RD2_{stable_hash(key)}"


def extract_blocked_routes(blocklist: Dict[str, Any]) -> List[Dict[str, Any]]:
    routes = blocklist.get("blocked_routes")
    if not isinstance(routes, list):
        return []
    return [r for r in routes if isinstance(r, dict)]


def build_directions(
    lesson_index: Dict[str, Any],
    blocklist: Dict[str, Any],
    strict_policy: Dict[str, Any],
    strict_recorder: Dict[str, Any],
    universe: Dict[str, Any],
) -> List[Dict[str, Any]]:
    blocked_routes = extract_blocked_routes(blocklist)
    blocked_hashes = [r.get("route_hash") for r in blocked_routes if r.get("route_hash")]

    lessons = lesson_index.get("lessons") if isinstance(lesson_index.get("lessons"), list) else []
    lesson_ids = [x.get("lesson_id") for x in lessons if isinstance(x, dict) and x.get("lesson_id")]

    panel_path = safe_get(universe, ["best_universe_manifest", "panel_path"])
    panel_symbol_count = safe_get(universe, ["best_universe_manifest", "symbol_count"])
    panel_row_count = safe_get(universe, ["best_universe_manifest", "row_count"])
    panel_day_span = safe_get(universe, ["best_universe_manifest", "day_span"])

    strict_rule = strict_policy.get("release_requirement") or {
        "min_active_months": 12,
        "min_positive_months": 11,
        "min_positive_month_rate": 11 / 12,
    }

    common_context = {
        "blocked_route_hashes": blocked_hashes,
        "known_lessons": lesson_ids,
        "strict_month_policy": strict_rule,
        "strict_failure_recorder_status": strict_recorder.get("recorder_status"),
        "panel_path": panel_path,
        "panel_symbol_count": panel_symbol_count,
        "panel_row_count": panel_row_count,
        "panel_day_span": panel_day_span,
        "global_constraints": [
            "do_not_repeat_blocked_route_hashes",
            "do_not_release_from_positive_month_rate_0_55",
            "future_release_requires_12_active_months_and_11_positive_months",
            "must_use_full_1y_okx_swap_universe",
            "paper_ledger_only_not_allowed",
            "manual_month_blacklist_not_allowed",
            "manual_symbol_blacklist_not_allowed",
            "runtime_capital_live_actions_forbidden_until_release_gate_pass",
        ],
    }

    directions = [
        {
            "research_key": "RD2_01_STRICT_MONTH_STABLE_NEW_ARCHETYPE_SEARCH",
            "priority": 100,
            "severity": "HIGH",
            "family_scope": "new_archetype_search",
            "primary_question": (
                "Which completely new strategy archetypes can satisfy strict 12-active-month / 11-positive-month stability "
                "on the full 1Y OKX swap universe?"
            ),
            "hypothesis": (
                "The current impulse-continuation route is structurally unstable by month. The OS should rotate to new archetypes "
                "and evaluate them with strict 11-of-12 month stability from the start."
            ),
            "why_now": [
                "original impulse route failed full-universe release validation",
                "regime-filtered impulse route failed strict month stability",
                "169 repair filters failed 11-of-12 month rule",
                "strict month policy is now global release policy",
            ],
            "forbidden_route_hashes": blocked_hashes,
            "required_new_evidence": [
                "new route hash not in blocklist",
                "full 285-symbol 1Y universe",
                "12 active months minimum",
                "11 positive months minimum",
                "train/OOS pass",
                "cost/slippage pass",
                "symbol concentration pass",
            ],
            "suggested_archetypes": [
                "relative_weakness_snapback_long",
                "panic_rebound_with_strict_regime_guard",
                "failed_breakout_reversion_short",
                "market_relative_continuation_short",
                "liquidity_shock_mean_reversion",
                "breadth_extreme_reversal",
            ],
            "strict_month_policy_required": True,
            "candidate_generation_allowed_now": False,
            "offline_only": True,
        },
        {
            "research_key": "RD2_02_MONTH_FIRST_FEATURE_DISCOVERY",
            "priority": 94,
            "severity": "HIGH",
            "family_scope": "feature_research",
            "primary_question": (
                "Can the OS discover pre-outcome features that predict month-level stability before candidate construction?"
            ),
            "hypothesis": (
                "Instead of creating candidate rules first and then discovering bad months, the system should build month-stability "
                "features first and only allow candidate contracts that pass those features prospectively."
            ),
            "why_now": [
                "candidate had strong PF/OOS but failed month stability",
                "month stability must become an input constraint, not a late-stage patch",
            ],
            "forbidden_route_hashes": blocked_hashes,
            "required_new_evidence": [
                "month-level feature table over full panel",
                "pre-outcome stability labels",
                "no use of outcome PnL as a live feature",
                "candidate contracts must include strict month stability guard",
            ],
            "suggested_feature_groups": [
                "cross_sectional_dispersion",
                "market_breadth",
                "liquidity_regime",
                "range_stress",
                "BTC_ETH_context_if_available",
                "volatility_compression_expansion",
                "symbol_universe_health",
            ],
            "strict_month_policy_required": True,
            "candidate_generation_allowed_now": False,
            "offline_only": True,
        },
        {
            "research_key": "RD2_03_EXIT_LOGIC_RESEARCH_NOT_FIXED_HOLD_REPAIR",
            "priority": 88,
            "severity": "MEDIUM_HIGH",
            "family_scope": "exit_logic_research",
            "primary_question": (
                "Can materially different exit logic improve strict month stability without reusing the blocked fixed-hold impulse route?"
            ),
            "hypothesis": (
                "The fixed 12h hold may convert unstable months into losses. Volatility-adaptive exits, MFE/MAE exits, "
                "or regime-based timeouts may be required, but only if they create a new route hash and strict 11-of-12 stability."
            ),
            "why_now": [
                "blocked routes used fixed hold logic",
                "repair filters failed strict month stability",
                "different exit mechanics may be the only way to reopen impulse-family research safely",
            ],
            "forbidden_route_hashes": blocked_hashes,
            "required_new_evidence": [
                "exit logic materially different from fixed hold grid",
                "MFE/MAE diagnostics on full panel",
                "new route hash",
                "strict month stability",
                "cost sensitivity under exits",
            ],
            "suggested_experiments": [
                "MFE/MAE path diagnostic",
                "profit-protect exit",
                "volatility-adaptive timeout",
                "market-breadth deterioration exit",
                "max-adverse-excursion stop logic",
            ],
            "strict_month_policy_required": True,
            "candidate_generation_allowed_now": False,
            "offline_only": True,
        },
        {
            "research_key": "RD2_04_FAILED_IMPULSE_REVERSAL_SHORT",
            "priority": 82,
            "severity": "MEDIUM_HIGH",
            "family_scope": "new_family_direction",
            "primary_question": (
                "Do the failed impulse-long conditions produce a more month-stable short/reversion edge instead of continuation?"
            ),
            "hypothesis": (
                "If high impulse continuation is unstable, the better edge may be in failed impulse / exhaustion reversal, "
                "especially under volatility or range-stress regimes."
            ),
            "why_now": [
                "long continuation route failed full-universe and strict stability",
                "bad regimes may encode exhaustion rather than continuation",
            ],
            "forbidden_route_hashes": blocked_hashes,
            "required_new_evidence": [
                "short/reversion route hash not in blocklist",
                "strict month stability",
                "short-side risk and cost model",
                "symbol concentration control",
            ],
            "suggested_experiments": [
                "post_impulse_reversal_short",
                "range_exhaustion_short",
                "failed_followthrough_short",
                "market_relative_overextension_short",
            ],
            "strict_month_policy_required": True,
            "candidate_generation_allowed_now": False,
            "offline_only": True,
        },
        {
            "research_key": "RD2_05_META_RESEARCH_GATE_UPGRADE",
            "priority": 76,
            "severity": "MEDIUM",
            "family_scope": "os_policy_and_release_gate",
            "primary_question": (
                "Should all future candidate builders and release gates be upgraded to consume strict month policy and route blocklist automatically?"
            ),
            "hypothesis": (
                "The OS should not rely on late manual correction for month stability. All future modules should read the strict month policy "
                "and lesson blocklist before emitting candidate contracts or release decisions."
            ),
            "why_now": [
                "loose 0.55 month-rate almost allowed misleading preview",
                "strict policy guard now exists",
                "lesson memory now has multiple blocked route hashes",
            ],
            "forbidden_route_hashes": blocked_hashes,
            "required_new_evidence": [
                "release gate v5 reads strict month policy",
                "candidate contract builders read blocklist",
                "preview checks display positive_month_count, not only rate",
                "no candidate can pass without 12 active / 11 positive months",
            ],
            "suggested_modules": [
                "family_candidate_release_gate_v5",
                "candidate_contract_preflight_guard_v1",
                "strict_month_policy_adapter_v1",
                "route_blocklist_preflight_v1",
            ],
            "strict_month_policy_required": True,
            "candidate_generation_allowed_now": False,
            "offline_only": True,
        },
    ]

    out = []
    for d in directions:
        d = dict(d)
        d["direction_id"] = direction_id(d)
        d["created_at_utc"] = NOW.isoformat()
        d["status"] = "QUEUED_READ_ONLY_RESEARCH"
        d["source_module"] = MODULE
        d["context"] = common_context
        d["safety"] = {
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
        }
        out.append(d)

    return out


def upsert_queue(index: Dict[str, Any], directions: List[Dict[str, Any]]) -> Dict[str, Any]:
    existing = index.get("directions")
    if not isinstance(existing, list):
        existing = []

    by_id = {}
    for row in existing:
        if isinstance(row, dict) and row.get("direction_id"):
            by_id[row["direction_id"]] = row

    for direction in directions:
        by_id[direction["direction_id"]] = direction

    merged = list(by_id.values())
    merged.sort(key=lambda x: int(x.get("priority") or 0), reverse=True)

    index["directions"] = merged
    index["updated_at_utc"] = NOW.isoformat()
    return index


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    RESEARCH_QUEUE_ROOT.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    lesson_index = load_json(LESSON_INDEX_PATH)
    blocklist = load_json(BLOCKLIST_PATH)
    strict_policy = load_json(STRICT_POLICY_LATEST)
    strict_recorder = load_json(STRICT_FAILURE_RECORDER_LATEST)
    release_gate = load_json(RELEASE_GATE_V4_LATEST)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)

    if not isinstance(lesson_index, dict):
        critical.append("lesson_memory_index_missing")
        lesson_index = {}

    if not isinstance(blocklist, dict):
        critical.append("candidate_route_blocklist_missing")
        blocklist = {}

    if not isinstance(strict_policy, dict):
        critical.append("strict_month_stability_policy_missing")
        strict_policy = {}

    if not isinstance(strict_recorder, dict):
        critical.append("strict_month_stability_failure_recorder_missing")
        strict_recorder = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_missing")
        universe = {}

    if not isinstance(release_gate, dict):
        attention.append("release_gate_v4_missing")
        release_gate = {}

    if strict_recorder.get("recorder_status") != "STRICT_MONTH_STABILITY_FAILURE_LESSON_RECORDED":
        critical.append(f"strict_failure_lesson_not_recorded:{strict_recorder.get('recorder_status')}")

    if strict_policy.get("policy_key") != "STRICT_MONTH_STABILITY_11_OF_12":
        critical.append(f"strict_policy_key_unexpected:{strict_policy.get('policy_key')}")

    blocked_routes = extract_blocked_routes(blocklist)
    blocked_hashes = [r.get("route_hash") for r in blocked_routes if r.get("route_hash")]

    required_blocked = {"90466e4144914fbc", "85f9e6a4accb14c7"}
    missing_required = sorted([h for h in required_blocked if h not in set(blocked_hashes)])

    if missing_required:
        attention.append(f"expected_blocked_hashes_missing:{missing_required}")

    if universe.get("universe_status") != "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY":
        critical.append(f"universe_not_full_pass:{universe.get('universe_status')}")

    if critical:
        queue_status = "NEW_RESEARCH_DIRECTION_QUEUE_V2_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_QUEUE"
        reason = "; ".join(critical)
        directions = []
        index_written = False

    else:
        directions = build_directions(lesson_index, blocklist, strict_policy, strict_recorder, universe)

        queue_index = load_queue_index()
        queue_index = upsert_queue(queue_index, directions)
        dump_json(RESEARCH_QUEUE_INDEX, queue_index)

        for d in directions:
            direction_path = RUN_DIR / f"{d['direction_id']}_{d['research_key']}.json"
            dump_json(direction_path, d)

        queue_status = "NEW_RESEARCH_DIRECTIONS_V2_QUEUED_LESSON_AWARE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "SELECT_TOP_STRICT_MONTH_STABLE_RESEARCH_DIRECTION_AND_BUILD_CONTRACT"
        reason = f"direction_count={len(directions)}; blocked_route_count={len(blocked_hashes)}; strict_11_of_12_active=True"
        index_written = True

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "queue_status": queue_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "source_status": {
            "strict_failure_recorder_status": strict_recorder.get("recorder_status"),
            "strict_policy_key": strict_policy.get("policy_key"),
            "release_gate_v4_status": release_gate.get("release_status"),
            "universe_status": universe.get("universe_status"),
            "blocked_route_hashes": blocked_hashes,
            "blocked_route_count": len(blocked_hashes),
        },

        "strict_month_policy": {
            "min_active_months": safe_get(strict_policy, ["release_requirement", "min_active_months"], 12),
            "min_positive_months": safe_get(strict_policy, ["release_requirement", "min_positive_months"], 11),
            "min_positive_month_rate": safe_get(strict_policy, ["release_requirement", "min_positive_month_rate"], 11 / 12),
            "loose_055_month_rate_deprecated_for_release": safe_get(strict_policy, ["explicitly_deprecated_for_release", "positive_month_rate_gte_0_55_only"], True),
        },

        "research_queue_index_path": str(RESEARCH_QUEUE_INDEX),
        "index_written": index_written,
        "direction_count": len(directions),
        "directions": directions,

        "decision": {
            "repeat_blocked_routes_recommended": False,
            "candidate_generation_recommended_now": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "next_recommended_research_key": directions[0]["research_key"] if directions else None,
            "next_module": "edge_factory_os_research_direction_contract_builder_v2.py" if directions else None,
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

    out_json = RUN_DIR / "new_research_direction_queue_v2_state.json"
    out_md = RUN_DIR / "new_research_direction_queue_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS NEW RESEARCH DIRECTION QUEUE v2",
        "",
        f"queue_status: {queue_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Source Status",
        "",
        json.dumps(result["source_status"], indent=2, default=str),
        "",
        "## Strict Month Policy",
        "",
        json.dumps(result["strict_month_policy"], indent=2, default=str),
        "",
        "## Decision",
        "",
        json.dumps(result["decision"], indent=2, default=str),
        "",
        "## Directions",
        "",
    ]

    for d in directions:
        md_lines.extend([
            f"### {d['research_key']}",
            "",
            f"direction_id: {d['direction_id']}",
            f"priority: {d['priority']}",
            f"status: {d['status']}",
            f"primary_question: {d['primary_question']}",
            f"strict_month_policy_required: {d['strict_month_policy_required']}",
            f"candidate_generation_allowed_now: {d['candidate_generation_allowed_now']}",
            "",
        ])

    md_lines.extend([
        "## Safety",
        "",
        "read_only: True",
        "offline_only: True",
        "mutate_runtime_allowed: False",
        "launcher_allowed: False",
        "patch_runtime_allowed: False",
        "active_paper_allowed: False",
        "live_allowed: False",
        "capital_change_allowed: False",
        "family_disable_allowed: False",
        "real_orders_allowed: False",
        "execution_performed: False",
        "",
        f"critical: {critical}",
        f"attention: {attention}",
        f"info: {info}",
    ])

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS NEW RESEARCH DIRECTION QUEUE v2")
    print("=" * 100)
    print(f"queue_status: {queue_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("SOURCE STATUS")
    print("-" * 100)
    print(json.dumps(result["source_status"], indent=2, default=str))
    print()
    print("STRICT MONTH POLICY")
    print("-" * 100)
    print(json.dumps(result["strict_month_policy"], indent=2, default=str))
    print()
    print("DIRECTIONS")
    print("-" * 100)
    for d in directions:
        print(f"{d['priority']} | {d['research_key']} | {d['direction_id']}")
        print(f"  {d['primary_question']}")
        print(f"  strict_month_policy_required: {d['strict_month_policy_required']}")
        print(f"  candidate_generation_allowed_now: {d['candidate_generation_allowed_now']}")
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
