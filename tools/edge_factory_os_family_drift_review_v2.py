from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


MODULE = "edge_factory_os_family_drift_review_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"family_drift_review_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "family_drift_review_v2_latest.json"
LATEST_MD = OUT_ROOT / "family_drift_review_v2_latest.md"

V4_LATEST = BASE_DIR / "edge_factory_os_cycle_operator_v4" / "cycle_operator_v4_latest.json"

FAMILIES = [
    "impulse_long",
    "old_short",
    "market_relative_short",
    "weak_market_short",
]

BAD_SOURCE_MARKERS = [
    "cycle_operator",
    "error_acknowledgement",
    "error_inventory",
    "family_drift_review",
    "monitoring_stack",
    "state_transition_journal",
    "sample_maturity",
    "trigger_engine",
]

GOOD_SOURCE_MARKERS = [
    "family_performance",
    "performance_profiler",
    "performance_discipline",
    "discipline",
    "profiler",
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


def direct_value(d: Dict[str, Any], names: List[str]) -> Any:
    wanted = {n.lower() for n in names}
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
            m = re.search(r"-?\d+", v.replace(",", ""))
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
            s = v.strip().replace(",", "").replace("%", "")
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


def path_score(path: Path, text: str) -> int:
    p = str(path).lower()
    score = 0

    for marker in BAD_SOURCE_MARKERS:
        if marker in p:
            score -= 100

    for marker in GOOD_SOURCE_MARKERS:
        if marker in p:
            score += 30

    for fam in FAMILIES:
        if fam in text:
            score += 10

    useful_terms = [
        "win_rate",
        "realized",
        "unrealized",
        "total",
        "closed",
        "FAMILY_PERFORMANCE",
        "FAMILY_PERFORMANCE_DISCIPLINE",
        "FAMILY_EARLY_NEGATIVE_WATCH",
        "FAMILY_EARLY_POSITIVE_INFO",
    ]

    for term in useful_terms:
        if term in text:
            score += 5

    return score


def find_best_performance_sources() -> List[Tuple[int, Path, Dict[str, Any]]]:
    hits: List[Tuple[int, float, Path, Dict[str, Any]]] = []

    for p in BASE_DIR.rglob("*.json"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if "impulse_long" not in text:
            continue

        score = path_score(p, text)

        if score <= 0:
            continue

        obj = load_json(p)
        if not obj:
            continue

        try:
            mtime = p.stat().st_mtime
        except Exception:
            mtime = 0.0

        hits.append((score, mtime, p, obj))

    hits.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [(score, path, obj) for score, _, path, obj in hits[:10]]


def is_family_label(v: Any, family: str) -> bool:
    return isinstance(v, str) and v.strip() == family


def metric_presence_score(d: Dict[str, Any]) -> int:
    keys = {str(k).lower() for k in d.keys()}

    metric_aliases = {
        "closed",
        "closed_trades",
        "trade_count",
        "family_closed",
        "win_rate",
        "wr",
        "winrate",
        "realized",
        "realized_pnl",
        "unrealized",
        "unrealized_pnl",
        "total",
        "total_pnl",
        "family_total",
        "pnl",
        "status",
        "decision",
        "family_status",
        "watch_status",
        "label",
    }

    return len(keys.intersection(metric_aliases))


def collect_family_profile_candidates(obj: Any, family: str) -> List[Tuple[int, Dict[str, Any]]]:
    candidates: List[Tuple[int, Dict[str, Any]]] = []

    # Case 1: direct map: {"impulse_long": {...}}
    for d in walk(obj):
        if family in d and isinstance(d[family], dict):
            raw = d[family]
            score = 100 + metric_presence_score(raw)
            candidates.append((score, raw))

    # Case 2: dict contains explicit family field.
    family_keys = [
        "family",
        "family_key",
        "family_name",
        "strategy_family",
        "name",
        "key",
    ]

    for d in walk(obj):
        if not isinstance(d, dict):
            continue

        explicit = False
        for fk in family_keys:
            if is_family_label(d.get(fk), family):
                explicit = True
                break

        if not explicit:
            continue

        score = 80 + metric_presence_score(d)
        candidates.append((score, d))

    # Case 3: compact dict mentions family and has metrics.
    for d in walk(obj):
        if not isinstance(d, dict):
            continue

        try:
            text = json.dumps(d, default=str)
        except Exception:
            continue

        if family not in text:
            continue

        mscore = metric_presence_score(d)
        if mscore <= 0:
            continue

        # Lower priority because this can accidentally catch parent containers.
        score = 20 + mscore

        # Penalize huge parent objects.
        if len(text) > 5000:
            score -= 10

        candidates.append((score, d))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates


def normalize_profile(raw: Dict[str, Any], family: str, source_path: Optional[Path], source_score: int, candidate_score: int) -> Dict[str, Any]:
    closed = to_int(direct_value(raw, ["closed", "closed_trades", "closed_count", "family_closed", "trade_count"]), 0)
    open_ = to_int(direct_value(raw, ["open", "open_positions", "open_count", "family_open"]), 0)
    pending = to_int(direct_value(raw, ["pending", "pending_entries", "pending_count", "family_pending"]), 0)

    win_rate = to_float(direct_value(raw, ["win_rate", "wr", "winrate"]), None)
    if win_rate is not None and win_rate > 1.0:
        win_rate = win_rate / 100.0

    realized = to_float(direct_value(raw, ["realized", "realized_pnl", "total_realized", "realized_total"]), None)
    unrealized = to_float(direct_value(raw, ["unrealized", "unrealized_pnl", "total_unrealized", "unrealized_total"]), None)
    total = to_float(direct_value(raw, ["total", "total_pnl", "family_total", "pnl", "net_pnl"]), None)

    if total is None:
        parts = []
        if realized is not None:
            parts.append(realized)
        if unrealized is not None:
            parts.append(unrealized)
        if parts:
            total = sum(parts)

    status = direct_value(raw, ["status", "decision", "label", "profile_status", "watch_status", "family_status"])

    raw_compact = {}
    for k, v in raw.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            raw_compact[str(k)] = v
        if len(raw_compact) >= 40:
            break

    return {
        "family": family,
        "found": True,
        "source_path": str(source_path) if source_path else None,
        "source_score": source_score,
        "candidate_score": candidate_score,
        "status": status,
        "closed": closed,
        "open": open_,
        "pending": pending,
        "win_rate": win_rate,
        "realized": realized,
        "unrealized": unrealized,
        "total": total,
        "raw_compact": raw_compact,
    }


def extract_family_profile(family: str, sources: List[Tuple[int, Path, Dict[str, Any]]]) -> Dict[str, Any]:
    best: Optional[Tuple[int, int, Path, Dict[str, Any]]] = None

    for source_score, path, obj in sources:
        candidates = collect_family_profile_candidates(obj, family)

        if not candidates:
            continue

        cand_score, raw = candidates[0]
        total_score = source_score + cand_score

        if best is None or total_score > best[0]:
            best = (total_score, cand_score, path, raw)

    if best is None:
        return {
            "family": family,
            "found": False,
            "source_path": None,
            "source_score": 0,
            "candidate_score": 0,
            "status": "PROFILE_NOT_FOUND",
            "closed": 0,
            "open": 0,
            "pending": 0,
            "win_rate": None,
            "realized": None,
            "unrealized": None,
            "total": None,
            "raw_compact": {},
        }

    total_score, cand_score, path, raw = best
    source_score = total_score - cand_score
    return normalize_profile(raw, family, path, source_score, cand_score)


def judge_family(profile: Dict[str, Any]) -> Dict[str, Any]:
    family = profile["family"]
    found = profile.get("found") is True
    closed = to_int(profile.get("closed"), 0)
    win_rate = profile.get("win_rate")
    total = profile.get("total")
    realized = profile.get("realized")
    unrealized = profile.get("unrealized")
    status_text = str(profile.get("status") or "")

    reasons = []
    risk_score = 0

    if not found:
        return {
            "family": family,
            "judgement": "WAIT_PROFILE_NOT_FOUND",
            "severity": "INFO",
            "risk_score": 0,
            "reason": "profile_not_found",
            "review_priority": 50 if family == "impulse_long" else 20,
        }

    if closed <= 0:
        return {
            "family": family,
            "judgement": "WAIT_NO_CLOSED_SAMPLE",
            "severity": "INFO",
            "risk_score": 0,
            "reason": "no_closed_sample",
            "review_priority": 60 if family == "impulse_long" else 25,
        }

    if closed < 5:
        return {
            "family": family,
            "judgement": "EARLY_INCONCLUSIVE",
            "severity": "INFO",
            "risk_score": 1,
            "reason": f"closed_sample_too_small:{closed}",
            "review_priority": 70 if family == "impulse_long" else 35,
        }

    if win_rate is not None:
        if win_rate < 0.35:
            risk_score += 3
            reasons.append(f"low_win_rate:{win_rate:.4f}")
        elif win_rate < 0.45:
            risk_score += 1
            reasons.append(f"soft_low_win_rate:{win_rate:.4f}")

    if total is not None:
        if total < 0:
            risk_score += 3
            reasons.append(f"negative_total:{total:.4f}")
        elif total > 0:
            reasons.append(f"positive_total:{total:.4f}")

    if realized is not None and realized < 0:
        risk_score += 1
        reasons.append(f"negative_realized:{realized:.4f}")

    if unrealized is not None and unrealized < 0:
        risk_score += 1
        reasons.append(f"negative_unrealized:{unrealized:.4f}")

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
        "risk_score": risk_score,
        "reason": "; ".join(reasons) if reasons else "no_material_drift_flag",
        "review_priority": priority,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    v4 = load_json(V4_LATEST)

    if v4 is None:
        critical.append("cycle_operator_v4_latest_json_not_found")

    operator_status = find_key(v4, ["operator_status"])
    v4_severity = find_key(v4, ["severity"])
    v4_allowed_scope = find_key(v4, ["allowed_scope"])
    v4_recommended_action = find_key(v4, ["recommended_action"])

    closed = to_int(find_key(v4, ["closed", "closed_trades", "total_closed"]), 0)
    drift_remaining = to_int(find_key(v4, ["drift_remaining"]), 999999)
    capital_remaining = to_int(find_key(v4, ["capital_remaining"]), 999999)

    error_ack_applied = to_bool(find_key(v4, ["error_ack_applied"]))
    error_blocker_effective = to_bool(find_key(v4, ["error_blocker_effective"]))

    runtime_ok = to_bool(find_key(v4, ["runtime_ok"]))
    process_ok = to_bool(find_key(v4, ["process_ok"]))
    health_ok = to_bool(find_key(v4, ["health_ok"]))
    snapshot_mismatch = to_bool(find_key(v4, ["snapshot_mismatch"]))

    runtime_clean = runtime_ok is True and process_ok is True and health_ok is True
    snapshot_clean = snapshot_mismatch is False or snapshot_mismatch is None
    drift_gate_ready = closed >= 20 or drift_remaining <= 0

    if error_blocker_effective is True:
        attention.append("error_blocker_effective_true_review_blocked")

    if not runtime_clean:
        critical.append("runtime_process_health_not_clean")

    if not snapshot_clean:
        attention.append("snapshot_mismatch_not_clean")

    sources = find_best_performance_sources()

    if not sources:
        attention.append("no_valid_family_performance_source_found")

    source_list = [
        {
            "score": score,
            "path": str(path),
        }
        for score, path, _ in sources
    ]

    family_profiles: Dict[str, Dict[str, Any]] = {}
    family_judgements: Dict[str, Dict[str, Any]] = {}

    for family in FAMILIES:
        profile = extract_family_profile(family, sources)
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
        review_status = "FAMILY_DRIFT_REVIEW_V2_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CRITICAL_STATE_BEFORE_DRIFT_REVIEW"
        reason = "; ".join(critical)

    elif not drift_gate_ready:
        review_status = "FAMILY_DRIFT_REVIEW_V2_WAIT_SAMPLE_THRESHOLD"
        severity = "INFO"
        allowed_review_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNING_UNTIL_CLOSED_20_OR_DRIFT_REMAINING_0"
        reason = f"closed={closed}; drift_remaining={drift_remaining}; threshold_not_ready"

    elif error_blocker_effective is True:
        review_status = "FAMILY_DRIFT_REVIEW_V2_WAIT_ERROR_BLOCKER"
        severity = "ATTENTION"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "RESOLVE_UNACKNOWLEDGED_ERROR_BLOCKER_FIRST"
        reason = "error_blocker_effective=True"

    elif impulse_judgement.get("judgement") in {"DRIFT_REVIEW_ATTENTION", "DRIFT_REVIEW_WATCH"}:
        review_status = "FAMILY_DRIFT_REVIEW_V2_IMPULSE_LONG_ATTENTION"
        severity = "ATTENTION"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "READ_ONLY_INVESTIGATE_IMPULSE_LONG_DRIFT_NO_CAPITAL_CHANGE"
        reason = impulse_judgement.get("reason")

    else:
        review_status = "FAMILY_DRIFT_REVIEW_V2_READY_NO_HARD_ACTION"
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
        "v4_allowed_scope": v4_allowed_scope,
        "v4_recommended_action": v4_recommended_action,

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

        "performance_source_candidates": source_list,

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

    out_json = RUN_DIR / "family_drift_review_v2_state.json"
    out_md = RUN_DIR / "family_drift_review_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS FAMILY DRIFT REVIEW v2",
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
        "## Performance Source Candidates",
        "",
    ]

    for src in source_list[:10]:
        md_lines.append(str(src))

    md_lines.extend(
        [
            "",
            "## Primary Focus: impulse_long",
            "",
            f"impulse_long_profile: {impulse_profile}",
            f"impulse_long_judgement: {impulse_judgement}",
            "",
            "## Review Priority",
            "",
        ]
    )

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
    print("EDGE FACTORY OS FAMILY DRIFT REVIEW v2")
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
    print("PERFORMANCE SOURCE CANDIDATES")
    print("-" * 100)
    for src in source_list[:10]:
        print(src)
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
