#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Offline Research Result Synthesizer v1

Purpose:
- Synthesize failed offline research branches.
- Detect repeated strict month-stability failures.
- Decide whether to queue a materially different research direction.
- Keep all action flags blocked.

This module does NOT:
- generate candidates
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
from typing import Any, Dict, List, Optional, Tuple


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

OUT_DIR = BASE_DIR / "edge_factory_os_offline_research_result_synthesizer"
OUT_JSON = OUT_DIR / "offline_research_result_synthesizer_latest.json"
OUT_TXT = OUT_DIR / "offline_research_result_synthesizer_latest.txt"
QUEUE_JSON = OUT_DIR / "offline_research_next_direction_queue_latest.json"

LESSON_DIR = BASE_DIR / "edge_factory_os_lesson_memory"
LESSON_INDEX_PATH = LESSON_DIR / "lesson_memory_index.json"
BLOCKLIST_PATH = LESSON_DIR / "candidate_route_blocklist.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

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


KNOWN_EVALUATOR_PATHS = [
    BASE_DIR / "edge_factory_os_market_neutral_relative_value_archetype_evaluator" / "market_neutral_relative_value_archetype_evaluator_latest.json",
    BASE_DIR / "edge_factory_os_calm_market_low_vol_continuation_archetype_evaluator" / "calm_market_low_vol_continuation_archetype_evaluator_latest.json",
    BASE_DIR / "edge_factory_os_month_stability_repair_evaluator" / "month_stability_repair_evaluator_latest.json",
    BASE_DIR / "edge_factory_os_market_neutral_relative_value_archetype_evaluator" / "market_neutral_relative_value_archetype_evaluator_latest.json",
]

KNOWN_LESSON_PATHS = [
    LESSON_DIR / "market_neutral_relative_value_no_strict_12_lesson_latest.json",
    LESSON_DIR / "calm_market_low_vol_continuation_no_strict_12_lesson_latest.json",
    LESSON_DIR / "market_neutral_relative_value_no_strict_12_lesson_latest.json",
    LESSON_DIR / "month_stability_repair_no_strict_12_lesson_latest.json",
    LESSON_DIR / "broader_month_feature_no_strict_12_lesson_latest.json",
]


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


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default


def collect_json_paths() -> List[Path]:
    paths: List[Path] = []

    for p in KNOWN_EVALUATOR_PATHS + KNOWN_LESSON_PATHS:
        if p.exists():
            paths.append(p)

    # Add relevant latest evaluator/lesson JSONs without crawling huge parquet/data areas.
    roots = [
        BASE_DIR / "edge_factory_os_lesson_memory",
        BASE_DIR / "edge_factory_os_market_neutral_relative_value_archetype_evaluator",
        BASE_DIR / "edge_factory_os_calm_market_low_vol_continuation_archetype_evaluator",
        BASE_DIR / "edge_factory_os_month_stability_repair_evaluator",
        BASE_DIR / "edge_factory_os_broader_month_feature_engine",
        BASE_DIR / "edge_factory_os_non_impulse_mean_reversion_archetype_evaluator",
    ]

    for root in roots:
        if not root.exists():
            continue
        try:
            for p in root.glob("*.json"):
                name = p.name.lower()
                if "latest" in name or "lesson" in name or "evaluator" in name:
                    paths.append(p)
        except Exception:
            pass

    # Deduplicate preserving sort order.
    uniq = []
    seen = set()
    for p in sorted(paths, key=lambda x: str(x).lower()):
        s = str(p)
        if s not in seen:
            seen.add(s)
            uniq.append(p)

    return uniq


def normalize_record(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    status = (
        obj.get("evaluator_status")
        or obj.get("runner_status")
        or obj.get("builder_status")
        or obj.get("lesson_type")
        or obj.get("status")
    )

    branch = (
        obj.get("research_branch")
        or obj.get("research_key")
        or obj.get("direction_queue_key")
        or obj.get("evaluator_name")
        or obj.get("runner_name")
        or path.parent.name
    )

    strict_count = to_int(obj.get("strict_12_subset_pass_count"), 0)
    valid_count = to_int(obj.get("valid_rule_count"), 0)
    rules_tested = to_int(obj.get("rules_tested"), 0)
    canonical_months = to_int(obj.get("canonical_policy_month_count"), 12)

    branch_closed = bool(obj.get("branch_closed"))
    lesson_written = bool(obj.get("lesson_written") or obj.get("lesson_id"))

    strict_failure = (
        canonical_months == 12
        and (
            strict_count == 0
            and (
                branch_closed
                or valid_count > 0
                or "NO_STRICT" in str(status).upper()
                or "BRANCH_FAILURE" in str(status).upper()
                or "BRANCH_CLOSED" in str(status).upper()
            )
        )
    )

    return {
        "source_path": str(path),
        "source_file": path.name,
        "source_dir": path.parent.name,
        "status": status,
        "branch": branch,
        "branch_closed": branch_closed,
        "lesson_written": lesson_written,
        "lesson_id": obj.get("lesson_id"),
        "route_hash": obj.get("route_hash"),
        "contract_id": obj.get("contract_id"),
        "contract_hash": obj.get("contract_hash"),
        "strict_policy_key": obj.get("strict_policy_key") or STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_months,
        "rules_tested": rules_tested,
        "valid_rule_count": valid_count,
        "strict_12_subset_pass_count": strict_count,
        "raw_calendar_month_count": obj.get("raw_calendar_month_count"),
        "symbol_count": obj.get("symbol_count"),
        "row_count": obj.get("row_count"),
        "strict_failure": strict_failure,
        "next_recommended_research_key": obj.get("next_recommended_research_key"),
        "next_module": obj.get("next_module"),
    }


def load_records() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    for path in collect_json_paths():
        obj = load_json(path, default={})
        if isinstance(obj, dict):
            records.append(normalize_record(path, obj))

    # Also parse lesson index if present.
    lesson_index = load_json(LESSON_INDEX_PATH, default={})
    lessons = []
    if isinstance(lesson_index, dict) and isinstance(lesson_index.get("lessons"), list):
        lessons = lesson_index["lessons"]
    elif isinstance(lesson_index, list):
        lessons = lesson_index

    for idx, lesson in enumerate(lessons):
        if isinstance(lesson, dict):
            pseudo = normalize_record(LESSON_INDEX_PATH, lesson)
            pseudo["source_file"] = f"lesson_memory_index[{idx}]"
            records.append(pseudo)

    # Deduplicate by lesson/route/source-ish identity.
    seen = set()
    uniq = []
    for r in records:
        key = (
            r.get("lesson_id"),
            r.get("route_hash"),
            r.get("branch"),
            r.get("status"),
            r.get("source_file"),
        )
        skey = json.dumps(key, sort_keys=True, default=str)
        if skey not in seen:
            seen.add(skey)
            uniq.append(r)

    return uniq


def build_next_directions(strict_failure_count: int, closed_branch_count: int) -> List[Dict[str, Any]]:
    """
    Queue materially different research directions.
    These are NOT candidate contracts and NOT family releases.
    """

    directions = [
        {
            "research_key": "RD4_01_REGIME_FIRST_UNSUPERVISED_CLUSTER_SEARCH",
            "priority": 100,
            "title": "Regime-first unsupervised cluster search",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Multiple hand-designed archetypes failed strict 12/12. "
                "Next route should first cluster market/month regimes without assuming impulse, continuation, "
                "mean reversion, or market-neutral structure."
            ),
            "requirements": [
                "full 1Y 285-symbol OKX swap panel",
                "canonical_policy_month_count == 12",
                "no manual month blacklist",
                "no candidate generation from cluster diagnostics",
                "must emit new route hash",
                "must feed strict release gate only after full validation chain",
            ],
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "next_module_recommendation": "edge_factory_os_regime_first_cluster_contract_builder_v1.py",
        },
        {
            "research_key": "RD4_02_LABEL_FREE_EVENT_MOTIF_MINING",
            "priority": 92,
            "title": "Label-free event motif mining",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Failed branches suggest predefined signal families may be too narrow. "
                "Mine recurring event motifs from returns/range/vol/liquidity tensors before defining rules."
            ),
            "requirements": [
                "full panel only",
                "motif discovery must be offline-only",
                "strict 12/12 remains mandatory",
                "no release from motif preview",
            ],
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "next_module_recommendation": "edge_factory_os_label_free_event_motif_contract_builder_v1.py",
        },
        {
            "research_key": "RD4_03_EXIT_AND_RISK_SHAPE_SEARCH_INSTEAD_OF_ENTRY_SEARCH",
            "priority": 84,
            "title": "Exit/risk-shape search instead of new entry archetype",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Many entry families produce partial promise but fail month stability. "
                "Search whether exits, hold logic, stop/time decay, and adverse excursion controls are the missing dimension."
            ),
            "requirements": [
                "must reuse full-universe evidence",
                "must not resurrect blocked entry route without new route hash",
                "must report MAE/MFE and month stability",
            ],
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "next_module_recommendation": "edge_factory_os_exit_risk_shape_contract_builder_v1.py",
        },
        {
            "research_key": "RD4_04_SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH",
            "priority": 76,
            "title": "Symbol-cluster and microstructure segment search",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "why": (
                "Full-universe broad rules may hide symbol-cluster specific effects. "
                "Search stable clusters by liquidity/range/vol/listing behavior without manually cherry-picking symbols."
            ),
            "requirements": [
                "cluster definition must be pre-outcome",
                "symbol concentration guard required",
                "strict 12/12 required",
                "no manual symbol whitelist release",
            ],
            "candidate_generation_allowed_now": False,
            "family_release_allowed_now": False,
            "next_module_recommendation": "edge_factory_os_symbol_cluster_segment_contract_builder_v1.py",
        },
    ]

    if strict_failure_count >= 3 or closed_branch_count >= 3:
        directions[0]["priority"] = 110
        directions[0]["why"] += " Failure count is high enough that regime-first reset is now preferred."

    return sorted(directions, key=lambda x: int(x["priority"]), reverse=True)


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []

    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS OFFLINE RESEARCH RESULT SYNTHESIZER v1")
    lines.append("=" * 100)

    for k in [
        "synthesizer_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "strict_policy_key",
        "record_count",
        "strict_failure_record_count",
        "closed_branch_count",
        "materially_different_direction_required",
        "top_next_research_key",
        "top_next_module",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("FAILED BRANCH SUMMARY")
    lines.append("-" * 100)
    for r in result.get("strict_failure_records", [])[:20]:
        lines.append(
            f"{r.get('branch')} | status={r.get('status')} | "
            f"rules={r.get('rules_tested')} valid={r.get('valid_rule_count')} "
            f"strict12={r.get('strict_12_subset_pass_count')} | source={r.get('source_file')}"
        )

    lines.append("")
    lines.append("NEXT DIRECTIONS")
    lines.append("-" * 100)
    for d in result.get("next_direction_queue", []):
        lines.append(
            f"{d.get('priority')} | {d.get('research_key')} | "
            f"{d.get('title')} | module={d.get('next_module_recommendation')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT")
    lines.append("-" * 100)
    lines.append(f"output_json: {result.get('output_json')}")
    lines.append(f"output_txt: {result.get('output_txt')}")
    lines.append(f"queue_json: {result.get('queue_json')}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS OFFLINE RESEARCH RESULT SYNTHESIZER v1")
    print("=" * 100)
    print(f"synthesizer_status: {result.get('synthesizer_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"record_count: {result.get('record_count')}")
    print(f"strict_failure_record_count: {result.get('strict_failure_record_count')}")
    print(f"closed_branch_count: {result.get('closed_branch_count')}")
    print(f"materially_different_direction_required: {result.get('materially_different_direction_required')}")
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

    records = load_records()

    strict_failure_records = [
        r for r in records
        if r.get("strict_failure") is True
        and int(r.get("canonical_policy_month_count") or 0) == 12
    ]

    closed_records = [
        r for r in strict_failure_records
        if r.get("branch_closed") is True or "BRANCH_CLOSED" in str(r.get("status")).upper()
    ]

    strict_failure_count = len(strict_failure_records)
    closed_branch_count = len(closed_records)

    materially_different_required = strict_failure_count >= 2 or closed_branch_count >= 2

    next_queue = build_next_directions(strict_failure_count, closed_branch_count)
    top = next_queue[0] if next_queue else {}

    synthesis_hash = stable_hash({
        "strict_policy_key": STRICT_POLICY_KEY,
        "strict_failure_count": strict_failure_count,
        "closed_branch_count": closed_branch_count,
        "top_next_research_key": top.get("research_key"),
        "failure_branches": [r.get("branch") for r in strict_failure_records],
    })

    if materially_different_required:
        synthesizer_status = "OFFLINE_RESEARCH_SYNTHESIZER_NEW_DIRECTION_QUEUED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "BUILD_REGIME_FIRST_CLUSTER_CONTRACT_NO_RUNTIME_ACTION"
        reason = (
            f"strict_failure_record_count={strict_failure_count}; "
            f"closed_branch_count={closed_branch_count}; "
            "materially_different_direction_required=True"
        )
    elif strict_failure_count > 0:
        synthesizer_status = "OFFLINE_RESEARCH_SYNTHESIZER_MORE_EVIDENCE_NEEDED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "CONTINUE_READ_ONLY_RESEARCH_OR_ADD_MORE_BRANCH_EVIDENCE"
        reason = (
            f"strict_failure_record_count={strict_failure_count}; "
            f"closed_branch_count={closed_branch_count}; "
            "insufficient_failure_count_for_full_direction_reset"
        )
    else:
        synthesizer_status = "OFFLINE_RESEARCH_SYNTHESIZER_NO_STRICT_FAILURES_FOUND"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_INPUT_PATHS_NO_RELEASE"
        reason = "No strict 12/12 failure records found in known evaluator/lesson paths."

    result = {
        "synthesizer_name": "edge_factory_os_offline_research_result_synthesizer_v1",
        "created_at_utc": utc_now_iso(),
        "synthesizer_status": synthesizer_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "strict_policy_key": STRICT_POLICY_KEY,
        "synthesis_hash": synthesis_hash,
        "record_count": len(records),
        "strict_failure_record_count": strict_failure_count,
        "closed_branch_count": closed_branch_count,
        "materially_different_direction_required": materially_different_required,
        "top_next_research_key": top.get("research_key"),
        "top_next_module": top.get("next_module_recommendation"),
        "strict_failure_records": strict_failure_records,
        "closed_branch_records": closed_records,
        "next_direction_queue": next_queue,
        "release_gate_feed": {
            "OFFLINE_RESEARCH_SYNTHESIS_READY": materially_different_required,
            "STRICT_MONTH_STABILITY_12_OF_12": True,
            "MATERIALLY_DIFFERENT_DIRECTION_REQUIRED": materially_different_required,
            "CANDIDATE_GENERATION_ALLOWED_FROM_SYNTHESIS": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_SYNTHESIS": False,
            "FAMILY_RELEASE_ALLOWED_FROM_SYNTHESIS": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_SYNTHESIS": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_SYNTHESIS": False,
            "ACTIVE_PAPER_ALLOWED_FROM_SYNTHESIS": False,
            "LIVE_ALLOWED_FROM_SYNTHESIS": False,
            "REAL_ORDERS_ALLOWED_FROM_SYNTHESIS": False,
        },
        "input_paths": {
            "lesson_index_path": str(LESSON_INDEX_PATH),
            "blocklist_path": str(BLOCKLIST_PATH),
            "known_evaluator_paths": [str(p) for p in KNOWN_EVALUATOR_PATHS],
            "known_lesson_paths": [str(p) for p in KNOWN_LESSON_PATHS],
        },
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "queue_json": str(QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    queue_payload = {
        "created_at_utc": utc_now_iso(),
        "queue_status": "OFFLINE_RESEARCH_NEXT_DIRECTION_QUEUE_READY" if next_queue else "OFFLINE_RESEARCH_NEXT_DIRECTION_QUEUE_EMPTY",
        "source_synthesis_hash": synthesis_hash,
        "strict_policy_key": STRICT_POLICY_KEY,
        "next_direction_queue": next_queue,
        "top_next_research_key": top.get("research_key"),
        "top_next_module": top.get("next_module_recommendation"),
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
    }

    write_json(OUT_JSON, result)
    write_json(QUEUE_JSON, queue_payload)
    write_text_summary(OUT_TXT, result)
    print_summary(result)

    return 0 if strict_failure_count > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
