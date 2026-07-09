from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


MODULE = "edge_factory_os_family_drift_review_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"family_drift_review_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "family_drift_review_latest.json"
LATEST_MD = OUT_ROOT / "family_drift_review_latest.md"

V4_LATEST = BASE_DIR / "edge_factory_os_cycle_operator_v4" / "cycle_operator_v4_latest.json"

FAMILIES = [
    "impulse_long",
    "old_short",
    "market_relative_short",
    "weak_market_short",
]


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk(x)


def find_key(obj: Any, names: List[str]) -> Any:
    if obj is None:
        return None
    wanted = {n.lower() for n in names}
    for d in walk(obj):
        for k, v in d.items():
            if str(k).lower() in wanted:
                return v
    return None


def to_int(v: Any, default: int = 0) -> int:
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            return int(v)
        if isinstance(v, str):
            m = re.search(r"-?\d+", v)
            return int(m.group(0)) if m else default
    except Exception:
        return default
    return default


def to_float(v: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return float(int(v))
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = v.strip().replace("%", "")
            m = re.search(r"-?\d+(?:\.\d+)?", s)
            return float(m.group(0)) if m else default
    except Exception:
        return default
    return default


def to_bool(v: Any) -> Optional[bool]:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"true", "1", "yes", "ok", "pass"}:
            return True
        if s in {"false", "0", "no", "fail"}:
            return False
    return None


def find_latest_json_containing(root: Path, required_terms: List[str]) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
    hits = []
    if not root.exists():
        return None, None

    for p in root.rglob("*.json"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if all(term in text for term in required_terms):
            try:
                hits.append((p.stat().st_mtime, p))
            except Exception:
                pass

    if not hits:
        return None, None

    hits.sort(reverse=True)
    path = hits[0][1]
    return path, load_json(path)


def direct_child_value(d: Dict[str, Any], names: List[str]) -> Any:
    wanted = {n.lower() for n in names}
    for k, v in d.items():
        if str(k).lower() in wanted:
            return v
    return None


def collect_family_candidates(obj: Any, family: str) -> List[Dict[str, Any]]:
    candidates = []

    for d in walk(obj):
        text = json.dumps(d, default=str)
        if family not in text:
            continue

        score = 0

        local_family = direct_child_value(
            d,
            ["family", "family_key", "family_name", "name", "key", "strategy_family"],
        )

        if local_family == family:
            score += 10

        metric_keys = {
            "closed",
            "closed_trades",
            "open",
            "open_positions",
            "pending",
            "pending_entries",
            "win_rate",
            "wr",
            "total",
            "total_pnl",
            "realized",
            "realized_pnl",
            "unrealized",
            "unrealized_pnl",
            "status",
            "decision",
            "label",
        }

        present = {str(k).lower() for k in d.keys()}
        score += len(present.intersection(metric_keys))

        if score <= 0:
            continue

        candidates.append(
            {
                "score": score,
                "size": len(text),
                "data": d,
            }
        )

    candidates.sort(key=lambda x: (-x["score"], x["size"]))
    return [c["data"] for c in candidates]


def extract_family_profile(obj: Any, family: str) -> Dict[str, Any]:
    # First try direct dictionary mapping: {"impulse_long": {...}}
    for d in walk(obj):
        if family in d and isinstance(d[family], dict):
            raw = d[family]
            return normalize_family_profile(raw, family, source_mode="direct_map")

    candidates = collect_family_candidates(obj, family)

    if not candidates:
        return {
            "family": family,
            "found": False,
            "source_mode": "not_found",
            "status": "MISSING",
            "closed": 0,
            "open": 0,
            "pending": 0,
            "win_rate": None,
            "realized": None,
            "unrealized": None,
            "total": None,
        }

    return normalize_family_profile(candidates[0], family, source_mode="candidate_scan")


def normalize_family_profile(raw: Dict[str, Any], family: str, source_mode: str) -> Dict[str, Any]:
    closed = to_int(direct_child_value(raw, ["closed", "closed_trades", "closed_count", "trade_count"]), 0)
    open_ = to_int(direct_child_value(raw, ["open", "open_positions", "open_count"]), 0)
    pending = to_int(direct_child_value(raw, ["pending", "pending_entries", "pending_count"]), 0)

    win_rate = to_float(direct_child_value(raw, ["win_rate", "wr", "winrate"]), None)
    if win_rate is not None and win_rate > 1.0:
        win_rate = win_rate / 100.0

    realized = to_float(direct_child_value(raw, ["realized", "realized_pnl", "total_realized", "realized_total"]), None)
    unrealized = to_float(direct_child_value(raw, ["unrealized", "unrealized_pnl", "total_unrealized", "unrealized_total"]), None)
    total = to_float(direct_child_value(raw, ["total", "total_pnl", "family_total", "pnl", "net_pnl"]), None)

    if total is None:
        parts = []
        if realized is not None:
            parts.append(realized)
        if unrealized is not None:
            parts.append(unrealized)
        if parts:
            total = sum(parts)

    status = direct_child_value(raw, ["status", "decision", "label", "profile_status", "watch_status"])

    return {
        "family": family,
        "found": True,
        "source_mode": source_mode,
        "status": status,
        "closed": closed,
        "open": open_,
        "pending": pending,
        "win_rate": win_rate,
        "realized": realized,
        "unrealized": unrealized,
        "total": total,
        "raw_compact": {
            k: raw[k]
            for k in list(raw.keys())[:30]
            if isinstance(raw.get(k), (str, int, float, bool, type(None)))
        },
    }


def judge_family(profile: Dict[str, Any]) -> Dict[str, Any]:
    family = profile["family"]
    found = profile.get("found") is True
    closed = to_int(profile.get("closed"), 0)
    win_rate = profile.get("win_rate")
    total = profile.get("total")
    status_text = str(profile.get("status") or "")

    reasons = []

    if not found:
        return {
            "family": family,
            "judgement": "WAIT",
            "severity": "INFO",
            "reason": "profile_not_found",
            "review_priority": 50 if family == "impulse_long" else 20,
        }

    if closed <= 0:
        return {
            "family": family,
            "judgement": "WAIT",
            "severity": "INFO",
            "reason": "no_closed_sample",
            "review_priority": 60 if family == "impulse_long" else 25,
        }

    if closed < 5:
        return {
            "family": family,
            "judgement": "EARLY_INCONCLUSIVE",
            "severity": "INFO",
            "reason": f"closed_sample_too_small:{closed}",
            "review_priority": 70 if family == "impulse_long" else 35,
        }

    risk_score = 0

    if win_rate is not None and win_rate < 0.35:
        risk_score += 3
        reasons.append(f"low_win_rate:{win_rate:.4f}")

    if total is not None and total < 0:
        risk_score += 3
        reasons.append(f"negative_total:{total:.4f}")

    if "WATCH" in status_text.upper() or "NEGATIVE" in status_text.upper():
        risk_score += 2
        reasons.append(f"watch_status:{status_text}")

    if family == "impulse_long":
        risk_score += 1
        reasons.append("primary_drift_focus_family")

    if risk_score >= 6:
        judgement = "DRIFT_REVIEW_ATTENTION"
        severity = "ATTENTION"
        priority = 100
    elif risk_score >= 3:
        judgement = "DRIFT_REVIEW_WATCH"
        severity = "ATTENTION"
        priority = 80
    else:
        judgement = "DRIFT_REVIEW_INFO"
        severity = "INFO"
        priority = 40

    return {
        "family": family,
        "judgement": judgement,
        "severity": severity,
        "reason": "; ".join(reasons) if reasons else "no_material_drift_flag",
        "review_priority": priority,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical = []
    attention = []
    info = []

    v4 = load_json(V4_LATEST)

    if v4 is None:
        critical.append("cycle_operator_v4_latest_json_not_found")

    operator_status = find_key(v4, ["operator_status"])
    v4_severity = find_key(v4, ["severity"])
    allowed_scope = find_key(v4, ["allowed_scope"])
    recommended_action = find_key(v4, ["recommended_action"])
    error_blocker_effective = to_bool(find_key(v4, ["error_blocker_effective"]))
    error_ack_applied = to_bool(find_key(v4, ["error_ack_applied"]))

    closed = to_int(find_key(v4, ["closed", "closed_trades", "total_closed"]), 0)
    drift_remaining = to_int(find_key(v4, ["drift_remaining"]), 999999)
    capital_remaining = to_int(find_key(v4, ["capital_remaining"]), 999999)

    runtime_ok = to_bool(find_key(v4, ["runtime_ok"]))
    process_ok = to_bool(find_key(v4, ["process_ok"]))
    health_ok = to_bool(find_key(v4, ["health_ok"]))
    snapshot_mismatch = to_bool(find_key(v4, ["snapshot_mismatch"]))

    perf_path, perf = find_latest_json_containing(
        BASE_DIR,
        [
            "FAMILY_PERFORMANCE",
            "impulse_long",
        ],
    )

    if perf is None:
        attention.append("family_performance_profiler_json_not_found")
        perf = {}

    discipline_path, discipline = find_latest_json_containing(
        BASE_DIR,
        [
            "FAMILY_PERFORMANCE_DISCIPLINE",
            "impulse_long",
        ],
    )

    if discipline is None:
        info.append("family_performance_discipline_json_not_found_or_not_required")
        discipline = {}

    runtime_clean = runtime_ok is True and process_ok is True and health_ok is True
    snapshot_clean = snapshot_mismatch is False or snapshot_mismatch is None
    drift_gate_ready = closed >= 20 or drift_remaining <= 0

    if error_blocker_effective is True:
        attention.append("error_blocker_effective_true_review_blocked")

    if not runtime_clean:
        critical.append("runtime_process_health_not_clean")

    if not snapshot_clean:
        attention.append("snapshot_mismatch_not_clean")

    family_profiles = {}
    family_judgements = {}

    for family in FAMILIES:
        profile = extract_family_profile(perf, family)
        family_profiles[family] = profile
        family_judgements[family] = judge_family(profile)

    sorted_judgements = sorted(
        family_judgements.values(),
        key=lambda x: x.get("review_priority", 0),
        reverse=True,
    )

    impulse_profile = family_profiles.get("impulse_long", {})
    impulse_judgement = family_judgements.get("impulse_long", {})

    if critical:
        review_status = "FAMILY_DRIFT_REVIEW_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CRITICAL_STATE_BEFORE_DRIFT_REVIEW"
        reason = "; ".join(critical)

    elif not drift_gate_ready:
        review_status = "FAMILY_DRIFT_REVIEW_WAIT_SAMPLE_THRESHOLD"
        severity = "INFO"
        allowed_review_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNING_UNTIL_CLOSED_20_OR_DRIFT_REMAINING_0"
        reason = f"closed={closed}; drift_remaining={drift_remaining}; threshold_not_ready"

    elif error_blocker_effective is True:
        review_status = "FAMILY_DRIFT_REVIEW_WAIT_ERROR_BLOCKER"
        severity = "ATTENTION"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "RESOLVE_UNACKNOWLEDGED_ERROR_BLOCKER_FIRST"
        reason = "error_blocker_effective=True"

    elif impulse_judgement.get("judgement") in {"DRIFT_REVIEW_ATTENTION", "DRIFT_REVIEW_WATCH"}:
        review_status = "FAMILY_DRIFT_REVIEW_IMPULSE_LONG_ATTENTION"
        severity = "ATTENTION"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "READ_ONLY_INVESTIGATE_IMPULSE_LONG_DRIFT_NO_CAPITAL_CHANGE"
        reason = impulse_judgement.get("reason")

    else:
        review_status = "FAMILY_DRIFT_REVIEW_READY_NO_HARD_ACTION"
        severity = "INFO"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "CONTINUE_READ_ONLY_FAMILY_REVIEW_NO_CAPITAL_CHANGE"
        reason = "drift_gate_ready_but_no_hard_action_allowed"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "review_status": review_status,
        "severity": severity,
        "allowed_review_scope": allowed_review_scope,
        "next_action": next_action,
        "reason": reason,

        "cycle_operator_v4_source": str(V4_LATEST),
        "v4_operator_status": operator_status,
        "v4_severity": v4_severity,
        "v4_allowed_scope": allowed_scope,
        "v4_recommended_action": recommended_action,

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "error_ack_applied": error_ack_applied,
        "error_blocker_effective": error_blocker_effective,

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "snapshot_mismatch": snapshot_mismatch,

        "performance_source": str(perf_path) if perf_path else None,
        "discipline_source": str(discipline_path) if discipline_path else None,

        "primary_focus_family": "impulse_long",
        "family_profiles": family_profiles,
        "family_judgements": family_judgements,
        "review_priority_order": sorted_judgements,

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "family_disable_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "family_drift_review_v1_state.json"
    out_md = RUN_DIR / "family_drift_review_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS FAMILY DRIFT REVIEW v1",
        "",
        f"review_status: {review_status}",
        f"severity: {severity}",
        f"allowed_review_scope: {allowed_review_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Gate",
        "",
        f"closed: {closed}",
        f"drift_remaining: {drift_remaining}",
        f"capital_remaining: {capital_remaining}",
        f"drift_gate_ready: {drift_gate_ready}",
        "",
        "## Error / Runtime",
        "",
        f"error_ack_applied: {error_ack_applied}",
        f"error_blocker_effective: {error_blocker_effective}",
        f"runtime_ok: {runtime_ok}",
        f"process_ok: {process_ok}",
        f"health_ok: {health_ok}",
        f"snapshot_mismatch: {snapshot_mismatch}",
        "",
        "## Primary Focus",
        "",
        f"impulse_long_profile: {impulse_profile}",
        f"impulse_long_judgement: {impulse_judgement}",
        "",
        "## Review Priority",
        "",
    ]

    for row in sorted_judgements:
        md_lines.append(str(row))

    md_lines.extend(
        [
            "",
            "## Safety",
            "",
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
        ]
    )

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS FAMILY DRIFT REVIEW v1")
    print("=" * 100)
    print(f"review_status: {review_status}")
    print(f"severity: {severity}")
    print(f"allowed_review_scope: {allowed_review_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("GATE")
    print("-" * 100)
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print()
    print("ERROR / RUNTIME")
    print("-" * 100)
    print(f"error_ack_applied: {error_ack_applied}")
    print(f"error_blocker_effective: {error_blocker_effective}")
    print(f"runtime_ok: {runtime_ok}")
    print(f"process_ok: {process_ok}")
    print(f"health_ok: {health_ok}")
    print(f"snapshot_mismatch: {snapshot_mismatch}")
    print()
    print("PRIMARY FOCUS: impulse_long")
    print("-" * 100)
    print(f"profile: {impulse_profile}")
    print(f"judgement: {impulse_judgement}")
    print()
    print("REVIEW PRIORITY ORDER")
    print("-" * 100)
    for row in sorted_judgements:
        print(row)
    print()
    print("SAFETY")
    print("-" * 100)
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
