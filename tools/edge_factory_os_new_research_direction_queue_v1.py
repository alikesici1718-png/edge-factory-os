from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_new_research_direction_queue_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RELEASE_GATE_V4_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_candidate_release_gate_v4"
    / "family_candidate_release_gate_v4_latest.json"
)

LESSON_CHECKER_LATEST = (
    BASE_DIR
    / "edge_factory_os_lesson_memory_checker_v1"
    / "lesson_memory_checker_latest.json"
)

FULL_UNIVERSE_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_full_universe_offline_backtest_evaluator_v1"
    / "full_universe_offline_backtest_evaluator_latest.json"
)

UNIVERSE_GUARD_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
)

LESSON_INDEX_PATH = (
    BASE_DIR
    / "edge_factory_os_lesson_memory"
    / "lesson_memory_index.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"new_research_direction_queue_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "new_research_direction_queue_latest.json"
LATEST_MD = OUT_ROOT / "new_research_direction_queue_latest.md"

RESEARCH_QUEUE_ROOT = BASE_DIR / "edge_factory_os_research_queue"
RESEARCH_QUEUE_INDEX = RESEARCH_QUEUE_ROOT / "research_direction_queue_index.json"


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
        return obj

    return {
        "schema": "edge_factory_os_research_direction_queue_index_v1",
        "created_at_utc": NOW.isoformat(),
        "updated_at_utc": NOW.isoformat(),
        "directions": [],
    }


def direction_id(payload: Dict[str, Any]) -> str:
    key = {
        "research_key": payload.get("research_key"),
        "family_scope": payload.get("family_scope"),
        "primary_question": payload.get("primary_question"),
    }
    return f"RD_{stable_hash(key)}"


def build_directions(
    release_gate: Dict[str, Any],
    lesson_checker: Dict[str, Any],
    full_eval: Dict[str, Any],
    universe: Dict[str, Any],
    lesson_index: Dict[str, Any],
) -> List[Dict[str, Any]]:
    route_hash = lesson_checker.get("route_hash")
    blocked_route = lesson_checker.get("blocked_route")
    matched_lesson = lesson_checker.get("matched_lesson") or {}

    panel_path = safe_get(universe, ["best_universe_manifest", "panel_path"])
    panel_symbol_count = safe_get(universe, ["best_universe_manifest", "symbol_count"])
    panel_row_count = safe_get(universe, ["best_universe_manifest", "row_count"])

    failed_reason_counts = full_eval.get("failed_reason_counts") or {}

    common_context = {
        "blocked_route_hash": route_hash,
        "blocked_route": blocked_route,
        "matched_lesson_id": matched_lesson.get("lesson_id"),
        "release_gate_status": release_gate.get("release_status"),
        "full_universe_status": full_eval.get("evaluator_status"),
        "failed_reason_counts": failed_reason_counts,
        "panel_path": panel_path,
        "panel_symbol_count": panel_symbol_count,
        "panel_row_count": panel_row_count,
        "important_constraints": [
            "do_not_repeat_ret3_threshold_hold_entry_range_market_filter_route_without_new_evidence",
            "do_not_use_paper_ledger_only_as_family_release_evidence",
            "must_use_full_1y_285_symbol_universe_for_family_or_candidate_generation",
            "must_pass_release_gate_before any runtime/capital/family action",
        ],
    }

    directions = [
        {
            "research_key": "RD1_MONTH_REGIME_INSTABILITY_FEATURES",
            "priority": 100,
            "severity": "HIGH",
            "family_scope": "cross_family_or_new_family",
            "primary_question": "Which market/month/regime features explain why the blocked impulse route failed monthly and train/OOS stability?",
            "hypothesis": (
                "The failed route did not lack raw impulse strength; it lacked regime discrimination. "
                "New features should explain bad months, not just ret3 strength."
            ),
            "why_now": [
                "all_positive_month_rate failed 108/108 full-universe candidates",
                "train_profit_factor failed 105/108",
                "oos_positive_month_rate failed 105/108",
                "best OOS candidate still failed train and month stability",
            ],
            "required_new_evidence": [
                "new features not used in the blocked route",
                "month/regime labels from full 1Y panel",
                "out-of-sample stability by month",
                "proof that candidate does not depend on the same blocked route hash",
            ],
            "suggested_feature_families": [
                "market breadth",
                "cross-sectional dispersion",
                "market volatility regime",
                "liquidity shock regime",
                "funding or volume stress proxy if available",
                "BTC/ETH market context if available",
                "rolling bad-month classifier",
            ],
            "blocked_route_reuse_allowed": False,
            "offline_only": True,
            "release_candidate_allowed_now": False,
        },
        {
            "research_key": "RD2_DIFFERENT_EXIT_LOGIC_NOT_HOLD_GRID",
            "priority": 92,
            "severity": "HIGH",
            "family_scope": "impulse_long_research_only",
            "primary_question": "Can a materially different exit logic improve impulse_long without repeating the failed fixed hold-hour grid?",
            "hypothesis": (
                "The route may fail because fixed 3/6/12h holds are unstable across months. "
                "A materially different exit, such as trailing stop, volatility exit, MFE/MAE based exit, or regime timeout, is required."
            ),
            "why_now": [
                "lesson block rule says same hold-hour grid is not enough to reopen",
                "best candidate OOS looked good but train/month stability failed",
                "current route cannot be rescued by ret3 threshold tuning alone",
            ],
            "required_new_evidence": [
                "exit logic not equivalent to current hold grid",
                "full-universe test on 285-symbol panel",
                "train/OOS and monthly stability evidence",
                "cost/slippage sensitivity under realistic assumptions",
            ],
            "suggested_experiments": [
                "MFE/MAE diagnostic on full panel",
                "volatility-adaptive exits",
                "profit-protect trailing exit",
                "bad-regime early exit",
                "time stop conditional on market breadth",
            ],
            "blocked_route_reuse_allowed": False,
            "offline_only": True,
            "release_candidate_allowed_now": False,
        },
        {
            "research_key": "RD3_SHORT_SIDE_OR_MEAN_REVERSION_AROUND_FAILED_IMPULSE",
            "priority": 85,
            "severity": "MEDIUM_HIGH",
            "family_scope": "new_family_direction",
            "primary_question": "Do failed impulse-long setups contain a better short/mean-reversion edge instead of continuation edge?",
            "hypothesis": (
                "The impulse continuation route may be wrong directionally in unstable months. "
                "The same event class may encode blowoff/reversion or failed-breakout behavior."
            ),
            "why_now": [
                "full-universe ret3 continuation route produced zero release candidates",
                "bad months and train instability suggest regime-dependent reversal risk",
                "do not keep tuning the same long continuation route",
            ],
            "required_new_evidence": [
                "candidate must not be same impulse_long ret3 hold route",
                "full-universe evidence",
                "short/mean-reversion risk model",
                "cost and month stability",
            ],
            "suggested_experiments": [
                "post-impulse reversal short after exhaustion",
                "failed breakout reversion",
                "high range / low follow-through short",
                "market-relative overextension reversion",
            ],
            "blocked_route_reuse_allowed": False,
            "offline_only": True,
            "release_candidate_allowed_now": False,
        },
        {
            "research_key": "RD4_SYMBOL_CLUSTER_AND_UNIVERSE_SEGMENTATION",
            "priority": 78,
            "severity": "MEDIUM_HIGH",
            "family_scope": "universe_research",
            "primary_question": "Are losses/wins explained by stable symbol clusters rather than single-symbol blacklist overfit?",
            "hypothesis": (
                "Symbol-level behavior may be clustered by liquidity, volatility, sector/meme status, or listing age. "
                "A robust universe segmentation may be safer than ad-hoc symbol blacklists."
            ),
            "why_now": [
                "symbol concentration risk was not cleared",
                "paper-sample symbol ablation was overfit-prone",
                "full-universe best candidate showed many symbol-level winners/losers but not release stability",
            ],
            "required_new_evidence": [
                "cluster definition available before evaluating PnL",
                "cluster stability across train/OOS",
                "not a manual blacklist based on one sample",
                "full-universe panel validation",
            ],
            "suggested_experiments": [
                "liquidity quantile segmentation",
                "volatility quantile segmentation",
                "listing age proxy if available",
                "major coin vs alt/meme segmentation",
                "symbol turnover robustness",
            ],
            "blocked_route_reuse_allowed": False,
            "offline_only": True,
            "release_candidate_allowed_now": False,
        },
        {
            "research_key": "RD5_RESEARCH_ARCHETYPE_ROTATION",
            "priority": 70,
            "severity": "MEDIUM",
            "family_scope": "new_archetype_search",
            "primary_question": "Should the research engine rotate away from impulse_long and test a different archetype from the idea bank?",
            "hypothesis": (
                "After a full-universe failure and lesson-memory block, the OS should avoid sunk-cost tuning and rotate to another family archetype."
            ),
            "why_now": [
                "lesson memory blocks same route",
                "release gate v4 says queue new research direction",
                "full-universe failure suggests not rescuing this route without new evidence",
            ],
            "required_new_evidence": [
                "new archetype contract",
                "universe coverage guard pass",
                "full-universe offline backtest",
                "OOS/month/cost/symbol/risk gates",
            ],
            "suggested_archetypes": [
                "market panic rebound long",
                "relative weakness snapback long",
                "extreme blowoff reversion short",
                "market-relative continuation short",
                "fresh candidate generated from failure modes",
            ],
            "blocked_route_reuse_allowed": False,
            "offline_only": True,
            "release_candidate_allowed_now": False,
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

    release_gate = load_json(RELEASE_GATE_V4_LATEST)
    lesson_checker = load_json(LESSON_CHECKER_LATEST)
    full_eval = load_json(FULL_UNIVERSE_EVAL_LATEST)
    universe = load_json(UNIVERSE_GUARD_V2_LATEST)
    lesson_index = load_json(LESSON_INDEX_PATH)

    if not isinstance(release_gate, dict):
        critical.append("release_gate_v4_latest_missing")
        release_gate = {}

    if not isinstance(lesson_checker, dict):
        critical.append("lesson_memory_checker_latest_missing")
        lesson_checker = {}

    if not isinstance(full_eval, dict):
        critical.append("full_universe_evaluator_latest_missing")
        full_eval = {}

    if not isinstance(universe, dict):
        critical.append("universe_guard_v2_latest_missing")
        universe = {}

    if not isinstance(lesson_index, dict):
        attention.append("lesson_index_missing_or_unreadable")
        lesson_index = {}

    release_status = release_gate.get("release_status")
    lesson_status = lesson_checker.get("checker_status")
    route_blocked = lesson_checker.get("route_blocked_by_lesson_memory") is True

    if release_status != "FAMILY_CANDIDATE_RELEASE_GATE_V4_BLOCKED_KNOWN_FAILURE_ROUTE":
        attention.append(f"release_gate_v4_not_known_failure_status:{release_status}")

    if lesson_status != "LESSON_MEMORY_ROUTE_BLOCKED_KNOWN_FAILURE":
        attention.append(f"lesson_checker_not_known_failure_status:{lesson_status}")

    if not route_blocked:
        attention.append("route_not_blocked_by_lesson_memory")

    if critical:
        queue_status = "NEW_RESEARCH_DIRECTION_QUEUE_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_INPUTS"
        reason = "; ".join(critical)
        directions = []
        index_written = False

    else:
        directions = build_directions(release_gate, lesson_checker, full_eval, universe, lesson_index)

        queue_index = load_queue_index()
        queue_index = upsert_queue(queue_index, directions)

        dump_json(RESEARCH_QUEUE_INDEX, queue_index)

        for d in directions:
            direction_path = RUN_DIR / f"{d['direction_id']}_{d['research_key']}.json"
            dump_json(direction_path, d)

        queue_status = "NEW_RESEARCH_DIRECTIONS_QUEUED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "SELECT_TOP_READ_ONLY_RESEARCH_DIRECTION_AND_BUILD_CONTRACT"
        reason = f"direction_count={len(directions)}; blocked_route_hash={lesson_checker.get('route_hash')}"
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
            "release_gate_v4_status": release_status,
            "lesson_checker_status": lesson_status,
            "route_blocked_by_lesson_memory": route_blocked,
            "route_hash": lesson_checker.get("route_hash"),
            "full_universe_status": full_eval.get("evaluator_status"),
            "universe_status": universe.get("universe_status"),
        },

        "research_queue_index_path": str(RESEARCH_QUEUE_INDEX),
        "index_written": index_written,
        "direction_count": len(directions),
        "directions": directions,

        "decision": {
            "repeat_same_route_recommended": False,
            "runtime_change_recommended": False,
            "capital_change_recommended": False,
            "family_disable_recommended": False,
            "live_or_real_order_recommended": False,
            "family_release_recommended": False,
            "promotion_recommended": False,
            "next_recommended_research_key": directions[0]["research_key"] if directions else None,
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

    out_json = RUN_DIR / "new_research_direction_queue_v1_state.json"
    out_md = RUN_DIR / "new_research_direction_queue_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS NEW RESEARCH DIRECTION QUEUE v1",
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
            f"release_candidate_allowed_now: {d['release_candidate_allowed_now']}",
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
    print("EDGE FACTORY OS NEW RESEARCH DIRECTION QUEUE v1")
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
    print("DIRECTIONS")
    print("-" * 100)
    for d in directions:
        print(f"{d['priority']} | {d['research_key']} | {d['direction_id']}")
        print(f"  {d['primary_question']}")
        print(f"  release_candidate_allowed_now: {d['release_candidate_allowed_now']}")
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
