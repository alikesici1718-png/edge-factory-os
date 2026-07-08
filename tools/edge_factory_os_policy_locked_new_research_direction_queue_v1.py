#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Policy Locked New Research Direction Queue v1

Purpose:
- Consume Framework Status Panel v1.
- Consume True Source Panel Empirical Null Baseline State v1.
- Consume research gate policy / validation / guard states.
- Consume lesson memory and route blocklist.
- Queue a materially different, policy-locked next research direction.
- Keep plugin expansion blocked.
- Keep candidate/family/runtime/capital/live/real-order actions blocked.

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
- delete/move/archive files
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

FRAMEWORK_STATUS_JSON = REPO_DIR / "edge_factory_os_framework" / "status" / "framework_status_panel_v1.json"
TRUE_PANEL_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "true_source_panel_empirical_null_baseline_state_v1.json"
POLICY_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_enforcement_policy_v1.json"
POLICY_VALIDATION_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_validation_state_v1.json"
POLICY_RUNTIME_STATE_JSON = REPO_DIR / "edge_factory_os_framework" / "policies" / "research_gate_policy_runtime_state_v1.json"
GUARD_FEED_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"
SPECIFIC_LESSON_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "policy_locked_new_research_direction_queue_lesson_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_policy_locked_new_research_direction_queue"
OUT_JSON = OUT_DIR / "policy_locked_new_research_direction_queue_latest.json"
OUT_TXT = OUT_DIR / "policy_locked_new_research_direction_queue_latest.txt"
OUT_CSV = OUT_DIR / "policy_locked_new_research_direction_candidates_latest.csv"

FRAMEWORK_QUEUE_DIR = REPO_DIR / "edge_factory_os_framework" / "queues"
REPO_QUEUE_JSON = FRAMEWORK_QUEUE_DIR / "policy_locked_new_research_direction_queue_v1.json"
REPO_QUEUE_TXT = FRAMEWORK_QUEUE_DIR / "policy_locked_new_research_direction_queue_v1.txt"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD6_01_SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS"
NEXT_MODULE = "edge_factory_os_source_panel_anomaly_discovery_contract_builder_v1.py"

ALT_RESEARCH_KEY = "RD6_02_OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH"
ALT_MODULE = "edge_factory_os_market_state_transition_contract_builder_v1.py"

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
    "file_delete_performed": False,
    "file_move_performed": False,
    "archive_performed": False,
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
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def extract_lessons(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return [x for x in obj["lessons"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def append_lesson_record(path: Path, lesson_record: Dict[str, Any]) -> Dict[str, Any]:
    obj = load_json(path, default={})

    if isinstance(obj, list):
        existing = {x.get("lesson_id") for x in obj if isinstance(x, dict)}
        if lesson_record["lesson_id"] not in existing:
            obj.append(lesson_record)
        write_json(path, obj)
        return {"append_mode": "list_root", "path": str(path)}

    if not isinstance(obj, dict):
        obj = {}

    lessons = obj.get("lessons")
    if not isinstance(lessons, list):
        lessons = []

    existing = {x.get("lesson_id") for x in lessons if isinstance(x, dict)}
    if lesson_record["lesson_id"] not in existing:
        lessons.append(lesson_record)

    obj["lessons"] = lessons
    obj["updated_at_utc"] = utc_now_iso()
    write_json(path, obj)
    return {"append_mode": "dict_lessons", "path": str(path)}


def route_fingerprint(candidate: Dict[str, Any]) -> str:
    payload = {
        "research_key": candidate.get("research_key"),
        "archetype": candidate.get("archetype"),
        "uses": candidate.get("uses"),
        "forbidden": candidate.get("forbidden"),
        "null_baseline": candidate.get("null_baseline"),
        "strict_policy_key": STRICT_POLICY_KEY,
    }
    return stable_hash(payload)


def blocked_hash_set(blocked_routes: List[Dict[str, Any]]) -> set:
    out = set()
    for item in blocked_routes:
        rh = item.get("route_hash")
        if rh:
            out.add(str(rh))
    return out


def build_candidate_directions(
    *,
    framework_status: Dict[str, Any],
    true_panel_state: Dict[str, Any],
    lesson_count: int,
    blocked_count: int,
) -> List[Dict[str, Any]]:
    base_requirements = [
        "must_consume_framework_status_panel_v1",
        "must_consume_true_source_panel_empirical_null_baseline_state_v1",
        "must_consume_research_gate_enforcement_policy_v1",
        "must_consume_data_quality_guard_feed",
        "must_consume_candidate_route_blocklist",
        "must_be_materially_different_from_blocked_routes",
        "must_keep_plugin_expansion_blocked",
        "must_keep_candidate_family_runtime_capital_live_blocked",
    ]

    return [
        {
            "research_key": NEXT_RESEARCH_KEY,
            "priority": 100,
            "next_module_recommendation": NEXT_MODULE,
            "archetype": "source_panel_anomaly_discovery_with_true_nulls",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Previous route failed because actual signal was absent. This direction starts from full source-panel anomaly discovery, "
                "uses true source-panel empirical nulls from the beginning, and avoids reopening closed impulse/feature/plugin routes."
            ),
            "uses": [
                "full_source_panel_rows",
                "canonical_12_policy_months",
                "true_source_panel_empirical_null_baseline",
                "unsupervised_or_outcome_agnostic_feature_discovery",
                "post_discovery_outcome_validation_only",
            ],
            "forbidden": [
                "summary_row_only_replay",
                "synthetic_month_generation_only",
                "manual_symbol_whitelist",
                "manual_month_blacklist",
                "future_return_as_feature",
                "post_outcome_filtering",
                "blocked_route_hash_reuse",
                "candidate_generation",
                "family_release",
                "runtime_touch",
                "capital_change",
                "live_or_real_orders",
            ],
            "null_baseline": "true_source_panel_empirical_null_required_before_any_signal_claim",
            "required_prerequisites": base_requirements,
            "material_difference_claim": (
                "New path is not entry-rule/feature-sweep first. It begins with source-panel anomaly discovery under true nulls, "
                "then only later may evaluate outcomes."
            ),
            "lesson_count_seen": lesson_count,
            "blocked_route_count_seen": blocked_count,
            "plugin_expansion_allowed_now": False,
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
            "research_key": ALT_RESEARCH_KEY,
            "priority": 90,
            "next_module_recommendation": ALT_MODULE,
            "archetype": "outcome_agnostic_market_state_transition_search",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Search for market-state transitions without using outcome labels first; then validate against true source-panel null baseline."
            ),
            "uses": [
                "market_state_features",
                "transition_clustering",
                "canonical_12_policy_months",
                "true_source_panel_empirical_null_baseline",
                "negative_controls",
            ],
            "forbidden": [
                "outcome_label_first_selection",
                "manual_month_blacklist",
                "blocked_route_hash_reuse",
                "candidate_generation",
                "family_release",
                "runtime_touch",
                "capital_change",
                "live_or_real_orders",
            ],
            "null_baseline": "true_source_panel_empirical_null_required_before_any_signal_claim",
            "required_prerequisites": base_requirements,
            "material_difference_claim": (
                "New path uses state transition discovery rather than directional entry search, symbol cluster segment search, or generic feature expansion."
            ),
            "lesson_count_seen": lesson_count,
            "blocked_route_count_seen": blocked_count,
            "plugin_expansion_allowed_now": False,
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
            "research_key": "RD6_03_PANEL_DATA_GENERATING_PROCESS_AUDIT",
            "priority": 75,
            "next_module_recommendation": "edge_factory_os_panel_data_generating_process_audit_v1.py",
            "archetype": "panel_data_generating_process_audit",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Before more alpha research, audit whether the panel's return/process structure has exploitable non-random structure under true nulls."
            ),
            "uses": [
                "source_panel_distribution_audit",
                "symbol_month_return_autocorrelation",
                "cross_sectional_dependence",
                "seasonality_check",
                "true_null_validation",
            ],
            "forbidden": [
                "candidate_generation",
                "family_release",
                "runtime_touch",
                "capital_change",
                "live_or_real_orders",
            ],
            "null_baseline": "true_source_panel_empirical_null_required",
            "required_prerequisites": base_requirements,
            "material_difference_claim": (
                "This is a data-generating-process audit, not a trading strategy search."
            ),
            "lesson_count_seen": lesson_count,
            "blocked_route_count_seen": blocked_count,
            "plugin_expansion_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "candidate_contract_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_touch_allowed_now": False,
            "capital_change_allowed_now": False,
            "active_paper_allowed_now": False,
            "live_allowed_now": False,
            "real_orders_allowed_now": False,
        },
    ]


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS POLICY LOCKED NEW RESEARCH DIRECTION QUEUE v1")
    lines.append("=" * 100)

    for key in [
        "queue_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "policy_active",
        "guard_pass",
        "validator_pass",
        "false_positive_methodology_repaired",
        "actual_signal_present",
        "plugin_expansion_allowed",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "live_allowed",
        "real_orders_allowed",
        "lesson_count",
        "blocked_route_count",
        "candidate_direction_count",
        "selected_research_key",
        "selected_route_hash",
        "selected_next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("SELECTED DIRECTION")
    lines.append("-" * 100)
    selected = result.get("selected_direction", {})
    lines.append(json.dumps(selected, indent=2, ensure_ascii=False))

    lines.append("")
    lines.append("DIRECTION CANDIDATES")
    lines.append("-" * 100)
    for row in result.get("candidate_rows", []):
        lines.append(
            f"{row.get('priority')} | {row.get('research_key')} | "
            f"route_hash={row.get('route_hash')} | blocked={row.get('route_hash_blocked')} | {row.get('why')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "output_csv",
        "repo_queue_json",
        "repo_queue_txt",
        "specific_lesson_path",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS POLICY LOCKED NEW RESEARCH DIRECTION QUEUE v1")
    print("=" * 100)
    print(f"queue_status: {result.get('queue_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"policy_active: {result.get('policy_active')}")
    print(f"guard_pass: {result.get('guard_pass')}")
    print(f"validator_pass: {result.get('validator_pass')}")
    print(f"false_positive_methodology_repaired: {result.get('false_positive_methodology_repaired')}")
    print(f"actual_signal_present: {result.get('actual_signal_present')}")
    print(f"plugin_expansion_allowed: {result.get('plugin_expansion_allowed')}")
    print(f"candidate_direction_count: {result.get('candidate_direction_count')}")
    print(f"selected_research_key: {result.get('selected_research_key')}")
    print(f"selected_route_hash: {result.get('selected_route_hash')}")
    print(f"selected_next_module: {result.get('selected_next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('output_csv')}")
    print(f"REPO_QUEUE: {result.get('repo_queue_json')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMEWORK_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    LESSON_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    lessons = extract_lessons(lesson_index)
    blocked_routes = extract_blocked_routes(blocklist)
    blocked_hashes = blocked_hash_set(blocked_routes)

    policy_active = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
    guard_pass = bool(guard_feed.get("guard_pass"))
    validator_pass = bool(validation_state.get("validator_pass"))
    false_positive_methodology_repaired = bool(true_panel_state.get("false_positive_methodology_repaired"))
    actual_signal_present = bool(true_panel_state.get("actual_signal_present"))

    framework_ready = (
        framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
        and bool(framework_status.get("false_positive_methodology_repaired"))
        and not bool(framework_status.get("actual_signal_present"))
        and framework_status.get("plugin_expansion_allowed") is False
    )

    runtime_blocks_plugin = runtime_state.get("plugin_expansion_allowed") is False

    prerequisites_pass = (
        framework_ready
        and policy_active
        and guard_pass
        and validator_pass
        and false_positive_methodology_repaired
        and not actual_signal_present
        and runtime_blocks_plugin
    )

    candidate_directions = build_candidate_directions(
        framework_status=framework_status,
        true_panel_state=true_panel_state,
        lesson_count=len(lessons),
        blocked_count=len(blocked_routes),
    )

    candidate_rows: List[Dict[str, Any]] = []
    for candidate in candidate_directions:
        route_hash = route_fingerprint(candidate)
        row = {
            **candidate,
            "route_hash": route_hash,
            "route_hash_blocked": route_hash in blocked_hashes,
            "materially_different_required": True,
            "policy_locked": True,
        }
        candidate_rows.append(row)

    candidate_rows = sorted(candidate_rows, key=lambda x: int(x.get("priority", 0)), reverse=True)
    available = [x for x in candidate_rows if not x.get("route_hash_blocked")]

    selected = available[0] if available else None

    if prerequisites_pass and selected:
        queue_status = "POLICY_LOCKED_NEW_RESEARCH_DIRECTION_QUEUE_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_SELECTED_POLICY_LOCKED_RESEARCH_CONTRACT_NO_RELEASE"
        reason = (
            f"framework_ready=True; false_positive_methodology_repaired=True; actual_signal_present=False; "
            f"selected={selected.get('research_key')}; route_hash_blocked=False"
        )
        return_code = 0
    else:
        queue_status = "POLICY_LOCKED_NEW_RESEARCH_DIRECTION_QUEUE_BLOCKED_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_POLICY_LOCKED_QUEUE_PREREQUISITES_NO_RELEASE"
        reason = (
            f"prerequisites_pass={prerequisites_pass}; framework_ready={framework_ready}; policy_active={policy_active}; "
            f"guard_pass={guard_pass}; validator_pass={validator_pass}; "
            f"false_positive_methodology_repaired={false_positive_methodology_repaired}; actual_signal_present={actual_signal_present}; "
            f"runtime_blocks_plugin={runtime_blocks_plugin}; available_direction_count={len(available)}"
        )
        return_code = 2

    selected_research_key = selected.get("research_key") if selected else None
    selected_next_module = selected.get("next_module_recommendation") if selected else None
    selected_route_hash = selected.get("route_hash") if selected else None

    queue_payload = {
        "created_at_utc": utc_now_iso(),
        "queue_status": queue_status,
        "source_module": "edge_factory_os_policy_locked_new_research_direction_queue_v1",
        "strict_policy_key": STRICT_POLICY_KEY,
        "policy_hash": policy.get("policy_hash"),
        "framework_status_panel_status": framework_status.get("panel_status"),
        "true_panel_state_status": true_panel_state.get("state_status"),
        "policy_active": policy_active,
        "guard_pass": guard_pass,
        "validator_pass": validator_pass,
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "selected_direction": selected,
        "candidate_rows": candidate_rows,
        "next_direction_queue": [
            {
                **selected,
                "priority": 100,
                "selected": True,
                "allowed_scope": "READ_ONLY_RESEARCH",
                "contract_builder_allowed_now": bool(prerequisites_pass and selected),
                "plugin_expansion_allowed_now": False,
                "candidate_generation_allowed_now": False,
                "candidate_contract_allowed_now": False,
                "family_release_allowed_now": False,
                "runtime_touch_allowed_now": False,
                "capital_change_allowed_now": False,
                "active_paper_allowed_now": False,
                "live_allowed_now": False,
                "real_orders_allowed_now": False,
            }
        ] if selected else [],
        "hard_requirements_for_next_contract": [
            "consume framework_status_panel_v1",
            "consume true_source_panel_empirical_null_baseline_state_v1",
            "consume research_gate_enforcement_policy_v1",
            "consume data_quality_guard_feed",
            "consume route blocklist",
            "prove route_hash not blocked",
            "prove materially different direction",
            "keep plugin expansion false",
            "keep candidate/family/runtime/capital/live false",
        ],
        **SAFETY_FLAGS,
    }

    status_hash = stable_hash({
        "queue_status": queue_status,
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "policy_hash": policy.get("policy_hash"),
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
    })

    lesson_id = f"LESSON_POLICY_LOCKED_QUEUE_{status_hash}"

    result = {
        "module_name": "edge_factory_os_policy_locked_new_research_direction_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": queue_status,
        "status_hash": status_hash,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "policy_hash": policy.get("policy_hash"),
        "policy_active": policy_active,
        "guard_pass": guard_pass,
        "validator_pass": validator_pass,
        "framework_ready": framework_ready,
        "runtime_blocks_plugin": runtime_blocks_plugin,
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "lesson_count": len(lessons),
        "blocked_route_count": len(blocked_routes),
        "candidate_direction_count": len(candidate_rows),
        "available_direction_count": len(available),
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "selected_direction": selected,
        "candidate_rows": candidate_rows,
        "queue_payload": queue_payload,
        "lesson_id": lesson_id,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "output_csv": str(OUT_CSV),
        "repo_queue_json": str(REPO_QUEUE_JSON),
        "repo_queue_txt": str(REPO_QUEUE_TXT),
        "specific_lesson_path": str(SPECIFIC_LESSON_PATH),
        "release_gate_feed": {
            "POLICY_LOCKED_NEW_RESEARCH_DIRECTION_QUEUE_READY": return_code == 0,
            "SELECTED_RESEARCH_KEY": selected_research_key,
            "SELECTED_ROUTE_HASH": selected_route_hash,
            "FRAMEWORK_READY": framework_ready,
            "FALSE_POSITIVE_METHODOLOGY_REPAIRED": false_positive_methodology_repaired,
            "ACTUAL_SIGNAL_PRESENT": actual_signal_present,
            "PLUGIN_EXPANSION_ALLOWED": False,
            "RELEASE_PASS_FROM_THIS_QUEUE": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_QUEUE": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_QUEUE": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_QUEUE": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_QUEUE": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_QUEUE": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_QUEUE": False,
            "LIVE_ALLOWED_FROM_THIS_QUEUE": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_QUEUE": False,
        },
        **SAFETY_FLAGS,
    }

    lesson_record = {
        "lesson_id": lesson_id,
        "created_at_utc": utc_now_iso(),
        "lesson_type": "POLICY_LOCKED_NEW_RESEARCH_DIRECTION_QUEUE_BUILT",
        "queue_status": queue_status,
        "selected_research_key": selected_research_key,
        "selected_route_hash": selected_route_hash,
        "selected_next_module": selected_next_module,
        "policy_hash": policy.get("policy_hash"),
        "false_positive_methodology_repaired": false_positive_methodology_repaired,
        "actual_signal_present": actual_signal_present,
        "plugin_expansion_allowed": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    write_json(SPECIFIC_LESSON_PATH, lesson_record)
    result["lesson_append_status"] = append_lesson_record(LESSON_INDEX_PATH, lesson_record)

    write_csv(OUT_CSV, candidate_rows)
    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))

    write_json(REPO_QUEUE_JSON, queue_payload)
    write_text(REPO_QUEUE_TXT, build_text(result))

    print_summary(result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
