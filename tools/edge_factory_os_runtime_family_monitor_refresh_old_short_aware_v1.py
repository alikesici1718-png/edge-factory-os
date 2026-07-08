#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Runtime Family Monitor Refresh Old-Short Aware v1

Purpose:
- Read-only runtime/family monitor refresh.
- Consume runtime_family_registry_v1 and lesson enforcer.
- Scan latest OS JSON outputs for family metrics.
- Treat old_short separately from failed research routes.
- Classify old_short as:
    * NOT_INVALIDATED
    * monitoring-ready only if >=20 closed trades
    * capital-review-ready only if >=50 closed trades AND still no capital action here
- Keep all candidate/release/runtime/capital/active-paper/live/real-order actions blocked.

This module does NOT:
- start/stop runtime
- patch runtime
- place orders
- allocate capital
- enable active paper
- enable live trading
- generate candidates
- release families
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = BASE_DIR / "edge_factory_os_repo"

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
QUEUE_DIR = FRAMEWORK_DIR / "queues"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
STATUS_DIR = FRAMEWORK_DIR / "status"

FAMILY_REGISTRY_JSON = REGISTRY_DIR / "runtime_family_registry_v1.json"
LESSON_ENFORCER_JSON = POLICY_DIR / "lesson_memory_route_enforcer_v1.json"
FAMILY_REPAIR_STATE_JSON = POLICY_DIR / "family_registry_and_lesson_enforcer_repair_state_v1.json"

GOV_REPAIR_STATE_JSON = POLICY_DIR / "governance_repair_suite_ledger_alpha_prereg_state_v1.json"
HOLDOUT_REPAIR_STATE_JSON = POLICY_DIR / "holdout_trigger_and_vault_status_repair_state_v1.json"
ALPHA_ENFORCEMENT_JSON = POLICY_DIR / "global_alpha_accounting_enforcement_v1.json"
HOLDOUT_TRIGGER_JSON = POLICY_DIR / "holdout_trigger_protocol_enforced_v1.json"
VAULT_STATUS_JSON = POLICY_DIR / "promising_signal_vault_validation_status_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_runtime_family_monitor_refresh_old_short_aware"
OUT_JSON = OUT_DIR / "runtime_family_monitor_refresh_old_short_aware_latest.json"
OUT_TXT = OUT_DIR / "runtime_family_monitor_refresh_old_short_aware_latest.txt"
OUT_CSV = OUT_DIR / "runtime_family_monitor_refresh_old_short_aware_family_summary_latest.csv"
OUT_EVIDENCE_CSV = OUT_DIR / "runtime_family_monitor_refresh_old_short_aware_evidence_latest.csv"

REPO_REFRESH_STATE_JSON = POLICY_DIR / "runtime_family_monitor_refresh_old_short_aware_state_v1.json"
REPO_MONITOR_SUMMARY_JSON = STATUS_DIR / "runtime_family_monitor_refresh_old_short_aware_summary_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "runtime_family_monitor_refresh_old_short_aware_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD8_08_RUNTIME_FAMILY_MONITOR_EVALUATOR_NO_CAPITAL"
NEXT_MODULE = "edge_factory_os_runtime_family_monitor_evaluator_no_capital_v1.py"

FAMILY_KEYS = ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]

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
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")
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
        for key in row:
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        x = float(value)
        if math.isfinite(x):
            return x
    except Exception:
        return default
    return default


def safe_int(value: Any, default: int | None = None) -> int | None:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        return int(float(value))
    except Exception:
        return default


def get_git_status_short() -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(REPO_DIR),
            text=True,
            capture_output=True,
            timeout=30,
        )
        return [x for x in proc.stdout.splitlines() if x.strip()]
    except Exception as exc:
        return [f"GIT_STATUS_ERROR: {type(exc).__name__}: {exc}"]


def family_registry_row(registry: Dict[str, Any], family_key: str) -> Dict[str, Any]:
    rows = registry.get("runtime_family_rows", [])
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and row.get("family_key") == family_key:
                return row
    return {}


def iter_candidate_json_files() -> List[Path]:
    allowed_keywords = [
        "family",
        "monitor",
        "performance",
        "discipline",
        "profiler",
        "cycle",
        "control_tower",
        "sample",
        "operator",
        "status",
    ]

    excluded_parts = {
        ".git",
        "__pycache__",
        "edge_factory_feature_panels",
        "node_modules",
        ".venv",
        "venv",
    }

    paths: List[Path] = []
    for path in BASE_DIR.rglob("*.json"):
        parts = set(path.parts)
        if parts & excluded_parts:
            continue
        name_blob = (path.name + " " + path.parent.name).lower()
        if not any(k in name_blob for k in allowed_keywords):
            continue
        try:
            size = path.stat().st_size
        except Exception:
            continue
        if size > 10_000_000:
            continue
        paths.append(path)

    paths.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return paths[:300]


def obj_contains_family(obj: Any, family_key: str) -> bool:
    try:
        text = json.dumps(obj, ensure_ascii=False, default=str).lower()
        return family_key.lower() in text
    except Exception:
        return False


def find_family_dicts(obj: Any, family_key: str, path: str = "$") -> List[Tuple[str, Dict[str, Any]]]:
    matches: List[Tuple[str, Dict[str, Any]]] = []

    if isinstance(obj, dict):
        direct_hit = False
        for key_name in ["family_key", "family", "route_family", "strategy_family", "logger_family"]:
            val = obj.get(key_name)
            if isinstance(val, str) and val.lower() == family_key.lower():
                direct_hit = True

        if not direct_hit:
            key_text = " ".join(str(k).lower() for k in obj.keys())
            if family_key.lower() in key_text:
                direct_hit = True

        if direct_hit or obj_contains_family(obj, family_key):
            if len(json.dumps(obj, default=str)) < 20000:
                matches.append((path, obj))

        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                matches.extend(find_family_dicts(v, family_key, f"{path}.{k}"))

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                matches.extend(find_family_dicts(v, family_key, f"{path}[{i}]"))

    return matches


def extract_metric(row: Dict[str, Any], names: List[str]) -> Any:
    for name in names:
        if name in row:
            return row.get(name)

    lower_map = {str(k).lower(): k for k in row.keys()}
    for name in names:
        lk = name.lower()
        if lk in lower_map:
            return row.get(lower_map[lk])

    return None


def flatten_shallow_metrics(row: Dict[str, Any]) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}

    metrics["closed_trades"] = safe_int(extract_metric(row, [
        "closed", "closed_trades", "family_closed", "closed_trade_count", "trade_count_closed"
    ]))
    metrics["open_positions"] = safe_int(extract_metric(row, [
        "open", "open_positions", "family_open", "open_count"
    ]))
    metrics["pending_entries"] = safe_int(extract_metric(row, [
        "pending", "pending_entries", "family_pending", "pending_count"
    ]))
    metrics["win_rate"] = safe_float(extract_metric(row, [
        "win_rate", "family_win_rate", "wr"
    ]))
    metrics["realized_pnl"] = safe_float(extract_metric(row, [
        "realized", "realized_pnl", "total_realized_pnl", "family_realized"
    ]))
    metrics["unrealized_pnl"] = safe_float(extract_metric(row, [
        "unrealized", "unrealized_pnl", "total_unrealized_pnl", "family_unrealized"
    ]))
    metrics["total_pnl"] = safe_float(extract_metric(row, [
        "total", "total_pnl", "family_total", "estimated_total_pnl"
    ]))
    metrics["status"] = extract_metric(row, [
        "status", "family_status", "classification", "audit_classification", "decision_class", "state", "prior_status"
    ])
    metrics["allowed_scope"] = extract_metric(row, [
        "allowed_scope"
    ])
    metrics["next_action"] = extract_metric(row, [
        "next_action", "recommended_action"
    ])

    return metrics


def evidence_quality(metrics: Dict[str, Any], path: Path) -> int:
    score = 0
    for key in ["closed_trades", "open_positions", "pending_entries", "win_rate", "realized_pnl", "unrealized_pnl", "total_pnl"]:
        if metrics.get(key) is not None:
            score += 5
    if metrics.get("status") is not None:
        score += 4
    name = str(path).lower()
    for k in ["family_performance", "family_exposure", "discipline", "profiler", "control_tower", "cycle"]:
        if k in name:
            score += 3
    return score


def collect_family_evidence() -> Dict[str, List[Dict[str, Any]]]:
    evidence: Dict[str, List[Dict[str, Any]]] = {family: [] for family in FAMILY_KEYS}
    files = iter_candidate_json_files()

    for path in files:
        obj = load_json(path, {})
        if not obj or isinstance(obj, dict) and obj.get("_load_error"):
            continue

        for family in FAMILY_KEYS:
            if not obj_contains_family(obj, family):
                continue

            matches = find_family_dicts(obj, family)
            for match_path, row in matches[:20]:
                metrics = flatten_shallow_metrics(row)
                q = evidence_quality(metrics, path)
                if q <= 0:
                    continue

                evidence[family].append({
                    "family_key": family,
                    "source_file": str(path),
                    "source_mtime_utc": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(),
                    "json_path": match_path,
                    "quality_score": q,
                    **metrics,
                })

    for family in FAMILY_KEYS:
        evidence[family].sort(key=lambda r: (r.get("quality_score") or 0, r.get("source_mtime_utc") or ""), reverse=True)
        evidence[family] = evidence[family][:25]

    return evidence


def choose_best_evidence(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {}

    with_closed = [r for r in rows if r.get("closed_trades") is not None]
    if with_closed:
        with_closed.sort(
            key=lambda r: (
                int(r.get("closed_trades") or 0),
                int(r.get("quality_score") or 0),
                str(r.get("source_mtime_utc") or ""),
            ),
            reverse=True,
        )
        return with_closed[0]

    return rows[0]


def classify_family(family_key: str, registry_row: Dict[str, Any], best: Dict[str, Any]) -> Dict[str, Any]:
    closed = safe_int(best.get("closed_trades"), 0) or 0
    win_rate = safe_float(best.get("win_rate"))
    total_pnl = safe_float(best.get("total_pnl"))
    status_blob = " ".join(str(best.get(k) or "") for k in ["status", "next_action", "allowed_scope"]).lower()

    min_monitor = safe_int(registry_row.get("minimum_closed_trades_for_monitoring_decision"), 20) or 20
    min_capital = safe_int(registry_row.get("minimum_closed_trades_for_capital_review"), 50) or 50

    research_invalidation_applies = registry_row.get("research_route_failure_applies") is True
    capital_approved_by_registry = registry_row.get("capital_approved") is True

    if family_key == "old_short":
        if research_invalidation_applies:
            decision = "OLD_SHORT_REGISTRY_CONFLICT_REVIEW_REQUIRED"
            reason = "registry unexpectedly allows research route failure to invalidate old_short"
        elif closed >= min_capital:
            decision = "OLD_SHORT_MONITORING_SAMPLE_STRONG_CAPITAL_REVIEW_ONLY_NO_ACTION"
            reason = "old_short has enough closed trades for capital review threshold, but capital action still requires separate governor and is blocked here"
        elif closed >= min_monitor:
            decision = "OLD_SHORT_MONITORING_DECISION_READY_NO_CAPITAL_ACTION"
            reason = "old_short has enough closed trades for monitoring decision but not capital review"
        elif closed > 0:
            decision = "OLD_SHORT_NOT_INVALIDATED_COLLECT_MORE_SAMPLE"
            reason = "old_short has some evidence but below monitoring threshold"
        else:
            decision = "OLD_SHORT_NOT_INVALIDATED_NO_CURRENT_SAMPLE_FOUND"
            reason = "registry protects old_short but current scanner did not find enough current family metrics"

        negative_watch = any(x in status_blob for x in ["negative", "fail", "attention", "watch"])
        if negative_watch and closed >= min_monitor:
            decision = "OLD_SHORT_REVIEW_REQUIRED_NEGATIVE_STATUS_IN_CURRENT_EVIDENCE"
            reason = "current evidence contains attention/negative/watch language despite old_short protection"

    elif family_key == "impulse_long":
        decision = "IMPULSE_LONG_MONITORING_ATTENTION_NO_ACTION"
        reason = "impulse_long remains separate from old_short and should not be promoted without escaping negative/early watch"
    elif family_key == "market_relative_short":
        decision = "MARKET_RELATIVE_SHORT_EXPOSURE_SAMPLE_ATTENTION_NO_ACTION"
        reason = "market_relative_short requires closed sample and exposure review"
    elif family_key == "weak_market_short":
        decision = "WEAK_MARKET_SHORT_INCONCLUSIVE_COLLECT_SAMPLE_NO_ACTION"
        reason = "weak_market_short remains inconclusive until sufficient closed sample"
    else:
        decision = "UNKNOWN_FAMILY_REVIEW_REQUIRED"
        reason = "unknown family"

    return {
        "family_key": family_key,
        "decision": decision,
        "reason": reason,
        "closed_trades": closed,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "monitoring_threshold": min_monitor,
        "capital_review_threshold": min_capital,
        "monitoring_threshold_met": closed >= min_monitor,
        "capital_review_threshold_met": closed >= min_capital,
        "research_invalidation_applies": research_invalidation_applies,
        "capital_approved_by_registry": capital_approved_by_registry,
        "capital_action_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "best_source_file": best.get("source_file"),
        "best_source_mtime_utc": best.get("source_mtime_utc"),
        "best_evidence_quality_score": best.get("quality_score"),
        "best_status": best.get("status"),
    }


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RUNTIME FAMILY MONITOR REFRESH OLD-SHORT AWARE v1")
    lines.append("=" * 100)

    for key in [
        "refresh_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "family_registry_status",
        "lesson_enforcer_status",
        "old_short_decision",
        "old_short_closed_trades",
        "old_short_monitoring_threshold_met",
        "old_short_capital_review_threshold_met",
        "old_short_research_invalidation_applies",
        "old_short_capital_action_allowed",
        "family_count",
        "evidence_file_count",
        "evidence_row_count",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("FAMILY SUMMARY")
    lines.append("-" * 100)
    for row in result.get("family_summary_rows", []):
        lines.append(json.dumps(row, ensure_ascii=False))

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("old_short is separated from failed research routes.")
    lines.append("This refresh is read-only and cannot approve capital, release, active paper, live, or real orders.")
    lines.append("If old_short is below 20 closed trades, collect more sample.")
    lines.append("If old_short is above 20 but below 50, monitoring decision only.")
    lines.append("If old_short is above 50, still only capital-review candidate; separate capital governor required.")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RUNTIME FAMILY MONITOR REFRESH OLD-SHORT AWARE v1")
    print("=" * 100)
    print(f"refresh_status: {result.get('refresh_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"family_registry_status: {result.get('family_registry_status')}")
    print(f"lesson_enforcer_status: {result.get('lesson_enforcer_status')}")
    print(f"old_short_decision: {result.get('old_short_decision')}")
    print(f"old_short_closed_trades: {result.get('old_short_closed_trades')}")
    print(f"old_short_monitoring_threshold_met: {result.get('old_short_monitoring_threshold_met')}")
    print(f"old_short_capital_review_threshold_met: {result.get('old_short_capital_review_threshold_met')}")
    print(f"old_short_research_invalidation_applies: {result.get('old_short_research_invalidation_applies')}")
    print(f"old_short_capital_action_allowed: {result.get('old_short_capital_action_allowed')}")
    print(f"family_count: {result.get('family_count')}")
    print(f"evidence_file_count: {result.get('evidence_file_count')}")
    print(f"evidence_row_count: {result.get('evidence_row_count')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('summary_csv')}")
    print(f"EVIDENCE: {result.get('evidence_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    family_registry = load_json(FAMILY_REGISTRY_JSON, {})
    lesson_enforcer = load_json(LESSON_ENFORCER_JSON, {})
    family_repair = load_json(FAMILY_REPAIR_STATE_JSON, {})
    gov_repair = load_json(GOV_REPAIR_STATE_JSON, {})
    holdout_repair = load_json(HOLDOUT_REPAIR_STATE_JSON, {})
    alpha = load_json(ALPHA_ENFORCEMENT_JSON, {})
    holdout = load_json(HOLDOUT_TRIGGER_JSON, {})
    vault = load_json(VAULT_STATUS_JSON, {})

    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")

    evidence_by_family = collect_family_evidence()

    evidence_rows: List[Dict[str, Any]] = []
    for family, rows in evidence_by_family.items():
        evidence_rows.extend(rows)

    family_summary_rows: List[Dict[str, Any]] = []
    for family in FAMILY_KEYS:
        registry_row = family_registry_row(family_registry, family)
        best = choose_best_evidence(evidence_by_family.get(family, []))
        family_summary_rows.append(classify_family(family, registry_row, best))

    old_short = next(row for row in family_summary_rows if row["family_key"] == "old_short")

    evidence_file_count = len({row.get("source_file") for row in evidence_rows if row.get("source_file")})
    evidence_row_count = len(evidence_rows)

    prerequisites = {
        "FAMILY_REGISTRY_ACTIVE": family_registry.get("registry_status") == "RUNTIME_FAMILY_REGISTRY_ACTIVE_OLD_SHORT_AWARE",
        "LESSON_ENFORCER_ACTIVE": lesson_enforcer.get("policy_status") == "LESSON_MEMORY_ROUTE_ENFORCER_ACTIVE",
        "FAMILY_REPAIR_PASS": family_repair.get("repair_pass") is True,
        "GOV_REPAIR_PASS": gov_repair.get("repair_pass") is True,
        "HOLDOUT_REPAIR_PASS": holdout_repair.get("repair_pass") is True,
        "ALPHA_RESEARCH_PASS_FALSE": alpha.get("research_execution_alpha_pass") is False,
        "HOLDOUT_ACCESS_BLOCKED": holdout.get("holdout_access_allowed_now") is False,
        "VAULT_RELEASE_ZERO": vault.get("vault_release_allowed_count") == 0,
        "LESSONS_PRESENT": len(lessons) >= 1,
        "BLOCKLIST_PRESENT": len(blocked_routes) >= 1,
        "OLD_SHORT_NOT_INVALIDATED": old_short.get("research_invalidation_applies") is False,
        "OLD_SHORT_CAPITAL_ACTION_FALSE": old_short.get("capital_action_allowed") is False,
    }

    failed_prereq = [k for k, v in prerequisites.items() if v is not True]
    prereq_pass = len(failed_prereq) == 0

    if prereq_pass:
        refresh_status = "RUNTIME_FAMILY_MONITOR_REFRESH_OLD_SHORT_AWARE_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RUNTIME_MONITORING"
        next_action = "BUILD_RUNTIME_FAMILY_MONITOR_EVALUATOR_NO_CAPITAL"
        reason = "Runtime family monitor refresh completed; old_short separated from research failures and no capital action allowed."
        next_key = NEXT_RESEARCH_KEY
        next_module = NEXT_MODULE
        return_code = 0
    else:
        refresh_status = "RUNTIME_FAMILY_MONITOR_REFRESH_OLD_SHORT_AWARE_ATTENTION_REVIEW_REQUIRED"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "INSPECT_RUNTIME_FAMILY_MONITOR_REFRESH_PREREQUISITES"
        reason = f"failed_prerequisites={failed_prereq}"
        next_key = None
        next_module = None
        return_code = 2

    monitor_summary = {
        "summary_name": "edge_factory_os_runtime_family_monitor_refresh_old_short_aware_summary_v1",
        "created_at_utc": utc_now_iso(),
        "refresh_status": refresh_status,
        "family_summary_rows": family_summary_rows,
        "evidence_file_count": evidence_file_count,
        "evidence_row_count": evidence_row_count,
        "old_short_decision": old_short.get("decision"),
        "old_short_closed_trades": old_short.get("closed_trades"),
        "old_short_monitoring_threshold_met": old_short.get("monitoring_threshold_met"),
        "old_short_capital_review_threshold_met": old_short.get("capital_review_threshold_met"),
        "old_short_research_invalidation_applies": old_short.get("research_invalidation_applies"),
        "old_short_capital_action_allowed": False,
        "git_status_short": get_git_status_short(),
        "release_gate_feed": {
            "RUNTIME_FAMILY_MONITOR_REFRESH_READY": prereq_pass,
            "OLD_SHORT_INVALIDATED_BY_RESEARCH_FAILURES": False,
            "OLD_SHORT_CAPITAL_ACTION_ALLOWED": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_RUNTIME_MONITOR": False,
            "FAMILY_RELEASE_ALLOWED_FROM_RUNTIME_MONITOR": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_RUNTIME_MONITOR": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_RUNTIME_MONITOR": False,
            "ACTIVE_PAPER_ALLOWED_FROM_RUNTIME_MONITOR": False,
            "LIVE_ALLOWED_FROM_RUNTIME_MONITOR": False,
            "REAL_ORDERS_ALLOWED_FROM_RUNTIME_MONITOR": False,
        },
        **SAFETY_FLAGS,
    }

    refresh_state = {
        "state_name": "edge_factory_os_runtime_family_monitor_refresh_old_short_aware_state_v1",
        "created_at_utc": utc_now_iso(),
        "refresh_status": refresh_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "family_registry_status": family_registry.get("registry_status"),
        "lesson_enforcer_status": lesson_enforcer.get("policy_status"),
        "family_count": len(family_summary_rows),
        "evidence_file_count": evidence_file_count,
        "evidence_row_count": evidence_row_count,
        "old_short_decision": old_short.get("decision"),
        "old_short_closed_trades": old_short.get("closed_trades"),
        "old_short_monitoring_threshold_met": old_short.get("monitoring_threshold_met"),
        "old_short_capital_review_threshold_met": old_short.get("capital_review_threshold_met"),
        "old_short_research_invalidation_applies": old_short.get("research_invalidation_applies"),
        "old_short_capital_action_allowed": False,
        "failed_prerequisite_count": len(failed_prereq),
        "failed_prerequisites": failed_prereq,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_runtime_family_monitor_refresh_old_short_aware_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RUNTIME_FAMILY_MONITOR_REFRESH_NEXT_QUEUE_READY" if prereq_pass else "RUNTIME_FAMILY_MONITOR_REFRESH_QUEUE_BLOCKED",
        "top_next_research_key": next_key,
        "top_next_module": next_module,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Evaluate runtime family refresh and decide monitoring-only status; no capital/release/runtime/live action.",
                "old_short_decision": old_short.get("decision"),
                "old_short_closed_trades": old_short.get("closed_trades"),
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ] if prereq_pass else [],
        **SAFETY_FLAGS,
    }

    write_json(REPO_MONITOR_SUMMARY_JSON, monitor_summary)
    write_json(REPO_REFRESH_STATE_JSON, refresh_state)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)
    write_csv(OUT_CSV, family_summary_rows)
    write_csv(OUT_EVIDENCE_CSV, evidence_rows)

    result = {
        "module_name": "edge_factory_os_runtime_family_monitor_refresh_old_short_aware_v1",
        "created_at_utc": utc_now_iso(),
        "refresh_status": refresh_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "family_registry_status": family_registry.get("registry_status"),
        "lesson_enforcer_status": lesson_enforcer.get("policy_status"),
        "old_short_decision": old_short.get("decision"),
        "old_short_closed_trades": old_short.get("closed_trades"),
        "old_short_monitoring_threshold_met": old_short.get("monitoring_threshold_met"),
        "old_short_capital_review_threshold_met": old_short.get("capital_review_threshold_met"),
        "old_short_research_invalidation_applies": old_short.get("research_invalidation_applies"),
        "old_short_capital_action_allowed": False,
        "family_count": len(family_summary_rows),
        "evidence_file_count": evidence_file_count,
        "evidence_row_count": evidence_row_count,
        "failed_prerequisite_count": len(failed_prereq),
        "failed_prerequisites": failed_prereq,
        "family_summary_rows": family_summary_rows,
        "monitor_summary": monitor_summary,
        "refresh_state": refresh_state,
        "next_queue": next_queue,
        "next_recommended_research_key": next_key,
        "next_module": next_module,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "summary_csv": str(OUT_CSV),
        "evidence_csv": str(OUT_EVIDENCE_CSV),
        "repo_monitor_summary_json": str(REPO_MONITOR_SUMMARY_JSON),
        "repo_refresh_state_json": str(REPO_REFRESH_STATE_JSON),
        "repo_next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
