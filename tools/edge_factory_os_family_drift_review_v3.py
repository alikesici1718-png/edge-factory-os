from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


MODULE = "edge_factory_os_family_drift_review_v3"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_drift_review_v2"
    / "family_drift_review_v2_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"family_drift_review_v3_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "family_drift_review_v3_latest.json"
LATEST_MD = OUT_ROOT / "family_drift_review_v3_latest.md"

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


def to_float(v: Any, default=None):
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return float(int(v))
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            return float(v.strip().replace("%", ""))
    except Exception:
        return default
    return default


def to_int(v: Any, default=0):
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
            return int(float(v.strip()))
    except Exception:
        return default
    return default


def normalize_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(profile)
    raw = p.get("raw_compact") or {}

    # Fix win rate aliases.
    win_rate = p.get("win_rate")
    if win_rate is None:
        for key in [
            "win_rate_closed",
            "closed_win_rate",
            "family_win_rate",
            "winrate_closed",
            "wr_closed",
        ]:
            if key in raw:
                win_rate = raw.get(key)
                break

    win_rate = to_float(win_rate, None)
    if win_rate is not None and win_rate > 1.0:
        win_rate = win_rate / 100.0

    # Fix status aliases.
    status = p.get("status")
    if not status:
        status_parts = []
        for key in [
            "profile_key",
            "profile_severity",
            "discipline_key",
            "discipline_severity",
            "allowed_scope",
            "recommended_action",
        ]:
            value = raw.get(key)
            if value:
                status_parts.append(f"{key}={value}")
        status = "; ".join(status_parts) if status_parts else None

    # Fix metrics aliases if missing.
    realized = p.get("realized")
    if realized is None:
        realized = raw.get("realized_pnl")

    unrealized = p.get("unrealized")
    if unrealized is None:
        unrealized = raw.get("unrealized_pnl")

    total = p.get("total")
    if total is None:
        total = raw.get("total_pnl")

    realized = to_float(realized, None)
    unrealized = to_float(unrealized, None)
    total = to_float(total, None)

    if total is None:
        parts = []
        if realized is not None:
            parts.append(realized)
        if unrealized is not None:
            parts.append(unrealized)
        if parts:
            total = sum(parts)

    p["win_rate"] = win_rate
    p["status"] = status
    p["realized"] = realized
    p["unrealized"] = unrealized
    p["total"] = total

    p["closed"] = to_int(p.get("closed"), 0)
    p["open"] = to_int(p.get("open"), 0)
    p["pending"] = to_int(p.get("pending"), 0)

    return p


def judge_family(profile: Dict[str, Any]) -> Dict[str, Any]:
    family = profile.get("family")
    found = profile.get("found") is True

    if not found:
        return {
            "family": family,
            "judgement": "WAIT_PROFILE_NOT_FOUND",
            "severity": "INFO",
            "risk_score": 0,
            "reason": "profile_not_found",
            "review_priority": 50 if family == "impulse_long" else 20,
        }

    closed = to_int(profile.get("closed"), 0)
    win_rate = profile.get("win_rate")
    realized = profile.get("realized")
    unrealized = profile.get("unrealized")
    total = profile.get("total")
    status_text = str(profile.get("status") or "")

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

    risk_score = 0
    reasons = []

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
        else:
            reasons.append(f"positive_total:{total:.4f}")

    if realized is not None and realized < 0:
        risk_score += 1
        reasons.append(f"negative_realized:{realized:.4f}")

    if unrealized is not None and unrealized < 0:
        risk_score += 1
        reasons.append(f"negative_unrealized:{unrealized:.4f}")

    upper_status = status_text.upper()
    if "WATCH" in upper_status or "NEGATIVE" in upper_status:
        risk_score += 2
        reasons.append("negative_watch_status")

    if family == "impulse_long":
        risk_score += 1
        reasons.append("primary_drift_focus_family")

    if risk_score >= 7:
        judgement = "DRIFT_REVIEW_ATTENTION"
        severity = "ATTENTION"
        priority = 100
    elif risk_score >= 4:
        judgement = "DRIFT_REVIEW_WATCH"
        severity = "ATTENTION"
        priority = 85
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

    v2 = load_json(V2_LATEST)

    critical = []
    attention = []
    info = []

    if v2 is None:
        critical.append("family_drift_review_v2_latest_json_not_found")
        v2 = {}

    closed = to_int(v2.get("closed"), 0)
    drift_remaining = to_int(v2.get("drift_remaining"), 999999)
    capital_remaining = to_int(v2.get("capital_remaining"), 999999)
    drift_gate_ready = bool(closed >= 20 or drift_remaining <= 0)

    error_ack_applied = v2.get("error_ack_applied")
    error_blocker_effective = v2.get("error_blocker_effective")

    raw_profiles = v2.get("family_profiles") or {}

    family_profiles = {}
    family_judgements = {}

    for family in FAMILIES:
        profile = raw_profiles.get(family) or {
            "family": family,
            "found": False,
            "status": "PROFILE_NOT_FOUND",
        }
        normalized = normalize_profile(profile)
        family_profiles[family] = normalized
        family_judgements[family] = judge_family(normalized)

    sorted_judgements = sorted(
        family_judgements.values(),
        key=lambda x: x.get("review_priority", 0),
        reverse=True,
    )

    impulse_profile = family_profiles.get("impulse_long", {})
    impulse_judgement = family_judgements.get("impulse_long", {})

    if critical:
        review_status = "FAMILY_DRIFT_REVIEW_V3_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_V2_INPUT"
        reason = "; ".join(critical)

    elif error_blocker_effective is True:
        review_status = "FAMILY_DRIFT_REVIEW_V3_WAIT_ERROR_BLOCKER"
        severity = "ATTENTION"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "RESOLVE_ERROR_BLOCKER_FIRST"
        reason = "error_blocker_effective=True"

    elif not drift_gate_ready and impulse_judgement.get("severity") == "ATTENTION":
        review_status = "FAMILY_DRIFT_REVIEW_V3_WAIT_THRESHOLD_WITH_IMPULSE_LONG_WATCH"
        severity = "ATTENTION"
        allowed_review_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNING_UNTIL_CLOSED_20_NO_CAPITAL_CHANGE"
        reason = (
            f"closed={closed}; drift_remaining={drift_remaining}; "
            f"impulse_long_pre_threshold_watch={impulse_judgement.get('reason')}"
        )

    elif not drift_gate_ready:
        review_status = "FAMILY_DRIFT_REVIEW_V3_WAIT_SAMPLE_THRESHOLD"
        severity = "INFO"
        allowed_review_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNING_UNTIL_CLOSED_20_OR_DRIFT_REMAINING_0"
        reason = f"closed={closed}; drift_remaining={drift_remaining}; threshold_not_ready"

    elif impulse_judgement.get("severity") == "ATTENTION":
        review_status = "FAMILY_DRIFT_REVIEW_V3_IMPULSE_LONG_ATTENTION"
        severity = "ATTENTION"
        allowed_review_scope = "READ_ONLY_REVIEW"
        next_action = "READ_ONLY_INVESTIGATE_IMPULSE_LONG_DRIFT_NO_CAPITAL_CHANGE"
        reason = impulse_judgement.get("reason")

    else:
        review_status = "FAMILY_DRIFT_REVIEW_V3_READY_NO_HARD_ACTION"
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

        "v2_source": str(V2_LATEST),

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "error_ack_applied": error_ack_applied,
        "error_blocker_effective": error_blocker_effective,

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

    out_json = RUN_DIR / "family_drift_review_v3_state.json"
    out_md = RUN_DIR / "family_drift_review_v3_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FAMILY DRIFT REVIEW v3

review_status: {review_status}  
severity: {severity}  
allowed_review_scope: {allowed_review_scope}  
next_action: {next_action}  
reason: {reason}

closed: {closed}  
drift_remaining: {drift_remaining}  
capital_remaining: {capital_remaining}  
drift_gate_ready: {drift_gate_ready}

error_ack_applied: {error_ack_applied}  
error_blocker_effective: {error_blocker_effective}

impulse_long_profile: {impulse_profile}  
impulse_long_judgement: {impulse_judgement}

review_priority_order: {sorted_judgements}

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
    print("EDGE FACTORY OS FAMILY DRIFT REVIEW v3")
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
