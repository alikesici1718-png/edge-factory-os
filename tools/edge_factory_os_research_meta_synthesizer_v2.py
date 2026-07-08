#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Research Meta Synthesizer v2

Purpose:
- Consume Data Quality Guard Runner v1 output/feed.
- Consume lesson memory + route blocklist.
- Synthesize prior failed research branches after the data-quality guard.
- Select a materially different next research direction.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This module does NOT:
- run strategy research
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

GUARD_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_runner_latest.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_research_meta_synthesizer_v2"
OUT_JSON = OUT_DIR / "research_meta_synthesizer_v2_latest.json"
OUT_TXT = OUT_DIR / "research_meta_synthesizer_v2_latest.txt"
OUT_QUEUE_JSON = OUT_DIR / "guarded_research_direction_queue_v2_latest.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD5_01_GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH"
NEXT_MODULE = "edge_factory_os_guarded_feature_space_expansion_contract_builder_v1.py"

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def extract_lessons(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        lessons = obj.get("lessons")
        if isinstance(lessons, list):
            return [x for x in lessons if isinstance(x, dict)]
    return []


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        blocked = obj.get("blocked_routes")
        if isinstance(blocked, list):
            return [x for x in blocked if isinstance(x, dict)]
    return []


def classify_lesson(lesson: Dict[str, Any]) -> str:
    text = json.dumps(lesson, ensure_ascii=False).lower()

    if "data_quality" in text or "panel_bias" in text:
        return "data_quality_or_guard"
    if "symbol_cluster" in text or "microstructure" in text or "segment" in text:
        return "symbol_microstructure_segment"
    if "exit_risk" in text or "risk_shape" in text or "mae" in text or "mfe" in text:
        return "exit_risk_shape"
    if "label_free" in text or "motif" in text:
        return "label_free_motif"
    if "regime" in text or "cluster" in text:
        return "regime_cluster"
    if "market_neutral" in text or "relative_value" in text:
        return "market_neutral_relative_value"
    if "calm_market" in text or "low_vol" in text:
        return "calm_market_low_vol"
    if "strict_month" in text:
        return "strict_month_stability"
    if "impulse" in text:
        return "impulse_or_prior_route"
    return "other"


def summarize_lessons(lessons: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    strict_related = 0

    for lesson in lessons:
        cls = classify_lesson(lesson)
        counts[cls] = counts.get(cls, 0) + 1

        text = json.dumps(lesson, ensure_ascii=False).lower()
        if "strict_month" in text or "12_of_12" in text or "12/12" in text:
            strict_related += 1

    recent_lessons = lessons[-12:] if len(lessons) >= 12 else lessons

    return {
        "lesson_count": len(lessons),
        "strict_related_lesson_count": strict_related,
        "lesson_class_counts": counts,
        "recent_lesson_ids": [x.get("lesson_id") for x in recent_lessons if x.get("lesson_id")],
    }


def summarize_blocklist(blocked_routes: List[Dict[str, Any]]) -> Dict[str, Any]:
    reasons: Dict[str, int] = {}
    branches: Dict[str, int] = {}

    for route in blocked_routes:
        reason = str(route.get("blocked_reason", "UNKNOWN"))
        branch = str(route.get("research_branch", "UNKNOWN"))
        reasons[reason] = reasons.get(reason, 0) + 1
        branches[branch] = branches.get(branch, 0) + 1

    return {
        "blocked_route_count": len(blocked_routes),
        "blocked_reason_counts": reasons,
        "blocked_branch_counts": branches,
        "blocked_route_hashes": [x.get("route_hash") for x in blocked_routes if x.get("route_hash")],
    }


def choose_next_direction(
    guard_runner: Dict[str, Any],
    guard_feed: Dict[str, Any],
    lesson_summary: Dict[str, Any],
    block_summary: Dict[str, Any],
) -> Tuple[str, str, str, List[Dict[str, Any]]]:
    guard_pass = bool(guard_runner.get("guard_pass")) and bool(guard_feed.get("guard_pass"))
    meta_allowed = bool(guard_runner.get("research_meta_synthesis_allowed")) and bool(guard_feed.get("research_meta_synthesis_allowed"))

    if not guard_pass or not meta_allowed:
        return (
            "META_SYNTHESIS_BLOCKED_GUARD_NOT_READY",
            "edge_factory_os_data_quality_guard_runner_v1.py",
            "Data-quality guard did not pass or did not allow meta-synthesis.",
            [],
        )

    lesson_classes = lesson_summary.get("lesson_class_counts", {})
    blocked_branches = block_summary.get("blocked_branch_counts", {})

    failed_axes = [
        "impulse_or_prior_route",
        "market_neutral_relative_value",
        "calm_market_low_vol",
        "regime_cluster",
        "label_free_motif",
        "exit_risk_shape",
        "symbol_microstructure_segment",
    ]

    failed_axis_count = sum(1 for axis in failed_axes if int(lesson_classes.get(axis, 0)) > 0)

    # Materially different next direction:
    # not another direct entry/motif/segment/exit search.
    # It expands the feature space under guard and adds negative controls / null models first.
    queue = [
        {
            "research_key": "RD5_01_GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH",
            "priority": 100,
            "title": "Guarded feature-space expansion with negative controls",
            "next_module_recommendation": "edge_factory_os_guarded_feature_space_expansion_contract_builder_v1.py",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Multiple strategy archetypes failed strict 12/12, and data-quality guard now exists. "
                "Next research should not jump to another strategy; it should first build guarded feature-space expansion "
                "with null/negative controls to detect whether the panel can produce a real signal distinguishable from chance."
            ),
            "must_consume_guard_feed": True,
            "must_not_reopen_blocked_routes": True,
            "candidate_generation_allowed_now": False,
            "candidate_contract_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "capital_change_allowed_now": False,
            "active_paper_allowed_now": False,
            "live_allowed_now": False,
            "real_orders_allowed_now": False,
        },
        {
            "research_key": "RD5_02_NULL_MODEL_AND_PERMUTATION_BASELINE",
            "priority": 90,
            "title": "Null model and permutation baseline",
            "next_module_recommendation": "edge_factory_os_null_model_permutation_baseline_contract_builder_v1.py",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Before continuing new alpha search, quantify how often strict-like previews appear under randomized labels, "
                "symbol shuffles, month shuffles, and cost perturbations."
            ),
            "must_consume_guard_feed": True,
            "must_not_reopen_blocked_routes": True,
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
        },
        {
            "research_key": "RD5_03_FEATURE_IMPORTANCE_MAP_WITH_NO_RELEASE",
            "priority": 80,
            "title": "Feature importance map without candidate release",
            "next_module_recommendation": "edge_factory_os_feature_importance_map_contract_builder_v1.py",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Use guard-compliant features and diagnostic-only labels to map whether any feature family has stable explanatory power, "
                "without producing a candidate."
            ),
            "must_consume_guard_feed": True,
            "must_not_reopen_blocked_routes": True,
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
        },
    ]

    reason = (
        f"guard_pass=True; meta_allowed=True; failed_axis_count={failed_axis_count}; "
        "choosing guarded feature-space expansion with negative controls before any further strategy route."
    )

    return (
        "RD5_01_GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH",
        "edge_factory_os_guarded_feature_space_expansion_contract_builder_v1.py",
        reason,
        queue,
    )


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESEARCH META SYNTHESIZER v2")
    lines.append("=" * 100)

    for k in [
        "synthesizer_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "guard_status",
        "guard_pass",
        "research_meta_synthesis_allowed",
        "lesson_count",
        "blocked_route_count",
        "top_next_research_key",
        "top_next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("LESSON SUMMARY")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("lesson_summary", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("BLOCKLIST SUMMARY")
    lines.append("-" * 100)
    lines.append(json.dumps(result.get("blocklist_summary", {}), indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("NEXT QUEUE")
    lines.append("-" * 100)
    for item in result.get("next_direction_queue", []):
        lines.append(f"- {item.get('research_key')} priority={item.get('priority')} module={item.get('next_module_recommendation')}")
        lines.append(f"  why: {item.get('why')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in ["output_json", "output_txt", "queue_json"]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESEARCH META SYNTHESIZER v2")
    print("=" * 100)
    print(f"synthesizer_status: {result.get('synthesizer_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"guard_status: {result.get('guard_status')}")
    print(f"guard_pass: {result.get('guard_pass')}")
    print(f"research_meta_synthesis_allowed: {result.get('research_meta_synthesis_allowed')}")
    print(f"lesson_count: {result.get('lesson_count')}")
    print(f"blocked_route_count: {result.get('blocked_route_count')}")
    print(f"top_next_research_key: {result.get('top_next_research_key')}")
    print(f"top_next_module: {result.get('top_next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON : {result.get('output_json')}")
    print(f"TXT  : {result.get('output_txt')}")
    print(f"QUEUE: {result.get('queue_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    guard_runner = load_json(GUARD_RUNNER_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    lessons = extract_lessons(lesson_index)
    blocked_routes = extract_blocked_routes(blocklist)

    lesson_summary = summarize_lessons(lessons)
    block_summary = summarize_blocklist(blocked_routes)

    guard_status = guard_runner.get("guard_status")
    guard_pass = bool(guard_runner.get("guard_pass")) and bool(guard_feed.get("guard_pass"))
    research_meta_synthesis_allowed = (
        bool(guard_runner.get("research_meta_synthesis_allowed"))
        and bool(guard_feed.get("research_meta_synthesis_allowed"))
    )

    top_key, top_module, choose_reason, next_queue = choose_next_direction(
        guard_runner=guard_runner,
        guard_feed=guard_feed,
        lesson_summary=lesson_summary,
        block_summary=block_summary,
    )

    if guard_pass and research_meta_synthesis_allowed and top_key != "META_SYNTHESIS_BLOCKED_GUARD_NOT_READY":
        synthesizer_status = "RESEARCH_META_SYNTHESIZER_V2_NEW_GUARDED_DIRECTION_QUEUED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_GUARDED_FEATURE_SPACE_EXPANSION_CONTRACT_NO_RUNTIME_ACTION"
        reason = choose_reason
    else:
        synthesizer_status = "RESEARCH_META_SYNTHESIZER_V2_BLOCKED_BY_DATA_QUALITY_GUARD"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RERUN_OR_REPAIR_DATA_QUALITY_GUARD_BEFORE_RESEARCH"
        reason = choose_reason

    synthesis_hash_payload = {
        "guard_status": guard_status,
        "guard_pass": guard_pass,
        "research_meta_synthesis_allowed": research_meta_synthesis_allowed,
        "lesson_summary": lesson_summary,
        "block_summary": block_summary,
        "top_key": top_key,
        "top_module": top_module,
    }
    synthesis_hash = stable_hash(synthesis_hash_payload)

    queue_payload = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "GUARDED_RESEARCH_DIRECTION_QUEUE_READY" if top_key != "META_SYNTHESIS_BLOCKED_GUARD_NOT_READY" else "GUARDED_RESEARCH_DIRECTION_QUEUE_BLOCKED",
        "source_synthesizer": "edge_factory_os_research_meta_synthesizer_v2",
        "synthesis_hash": synthesis_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "guard_feed_path": str(GUARD_FEED_JSON),
        "guard_pass": guard_pass,
        "research_meta_synthesis_allowed": research_meta_synthesis_allowed,
        "top_next_research_key": top_key if top_key != "META_SYNTHESIS_BLOCKED_GUARD_NOT_READY" else None,
        "top_next_module": top_module if top_key != "META_SYNTHESIS_BLOCKED_GUARD_NOT_READY" else None,
        "next_direction_queue": next_queue,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    write_json(OUT_QUEUE_JSON, queue_payload)

    result = {
        "synthesizer_name": "edge_factory_os_research_meta_synthesizer_v2",
        "created_at_utc": utc_now_iso(),
        "synthesizer_status": synthesizer_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "synthesis_hash": synthesis_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "guard_status": guard_status,
        "guard_pass": guard_pass,
        "guard_requirement_count": guard_runner.get("guard_requirement_count"),
        "guard_warning_count": guard_runner.get("guard_warning_count"),
        "research_meta_synthesis_allowed": research_meta_synthesis_allowed,
        "lesson_count": lesson_summary.get("lesson_count"),
        "blocked_route_count": block_summary.get("blocked_route_count"),
        "lesson_summary": lesson_summary,
        "blocklist_summary": block_summary,
        "top_next_research_key": top_key if top_key != "META_SYNTHESIS_BLOCKED_GUARD_NOT_READY" else None,
        "top_next_module": top_module if top_key != "META_SYNTHESIS_BLOCKED_GUARD_NOT_READY" else None,
        "next_direction_queue": next_queue,
        "must_consume_guard_feed": True,
        "must_not_reopen_blocked_routes": True,
        "release_gate_feed": {
            "RESEARCH_META_SYNTHESIZER_V2_RAN": True,
            "DATA_QUALITY_GUARD_PASS": guard_pass,
            "RESEARCH_META_SYNTHESIS_ALLOWED": research_meta_synthesis_allowed,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "RELEASE_PASS_FROM_THIS_SYNTHESIZER": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_SYNTHESIZER": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_SYNTHESIZER": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_SYNTHESIZER": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_SYNTHESIZER": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_SYNTHESIZER": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_SYNTHESIZER": False,
            "LIVE_ALLOWED_FROM_THIS_SYNTHESIZER": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_SYNTHESIZER": False,
        },
        "input_paths": {
            "guard_runner_json": str(GUARD_RUNNER_JSON),
            "guard_feed_json": str(GUARD_FEED_JSON),
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "queue_json": str(OUT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return 0 if synthesizer_status == "RESEARCH_META_SYNTHESIZER_V2_NEW_GUARDED_DIRECTION_QUEUED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
