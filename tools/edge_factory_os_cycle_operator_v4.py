from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


MODULE = "edge_factory_os_cycle_operator_v4"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

V3_SCRIPT = REPO_DIR / "tools" / "edge_factory_os_cycle_operator_v3.py"

ACK_LATEST = (
    BASE_DIR
    / "edge_factory_os_error_acknowledgement_policy_v1"
    / "error_acknowledgement_policy_latest.json"
)

V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_cycle_operator_v3"
    / "cycle_operator_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"cycle_operator_v4_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "cycle_operator_v4_latest.json"
LATEST_MD = OUT_ROOT / "cycle_operator_v4_latest.md"


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


def find_key(obj: Any, names):
    if obj is None:
        return None
    wanted = {n.lower() for n in names}
    for d in walk(obj):
        for k, v in d.items():
            if str(k).lower() in wanted:
                return v
    return None


def to_int(v, default=0):
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
            import re
            m = re.search(r"-?\d+", v)
            return int(m.group(0)) if m else default
    except Exception:
        return default
    return default


def to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"true", "1", "yes", "ok", "pass"}:
            return True
        if s in {"false", "0", "no", "fail"}:
            return False
    return None


def run_v3() -> Dict[str, Any]:
    if not V3_SCRIPT.exists():
        return {
            "ran": False,
            "returncode": 2,
            "stdout": "",
            "stderr": f"missing script: {V3_SCRIPT}",
        }

    proc = subprocess.run(
        [sys.executable, "-u", str(V3_SCRIPT)],
        cwd=str(REPO_DIR),
        capture_output=True,
        text=True,
    )

    return {
        "ran": True,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    v3_run = run_v3()

    (RUN_DIR / "cycle_operator_v3_stdout.txt").write_text(
        v3_run.get("stdout") or "",
        encoding="utf-8",
    )
    (RUN_DIR / "cycle_operator_v3_stderr.txt").write_text(
        v3_run.get("stderr") or "",
        encoding="utf-8",
    )

    v3 = load_json(V3_LATEST)
    ack = load_json(ACK_LATEST)

    critical = []
    attention = []
    info = []

    if v3 is None:
        critical.append("cycle_operator_v3_latest_json_not_found")

    if ack is None:
        critical.append("error_acknowledgement_policy_latest_json_not_found")

    v3_operator_status = find_key(v3, ["operator_status", "cycle_status", "control_tower_status"])
    v3_severity = find_key(v3, ["severity"])
    v3_allowed_scope = find_key(v3, ["allowed_scope"])
    v3_recommended_action = find_key(v3, ["recommended_action", "next_action"])
    v3_reason = find_key(v3, ["reason"])

    ack_policy_status = find_key(ack, ["policy_status"])
    ack_applied = to_bool(find_key(ack, ["acknowledgement_applied"]))
    ack_error_blocker_should_block = to_bool(
        find_key(ack, ["cycle_operator_error_blocker_should_block"])
    )

    new_errors_since_ack_original = to_bool(
        find_key(ack, ["new_errors_since_ack_original"])
    )
    new_errors_since_ack_effective_from_ack = to_bool(
        find_key(ack, ["new_errors_since_ack_effective"])
    )

    errors_original = to_int(find_key(ack, ["errors_original"]))
    if errors_original == 0:
        errors_original = to_int(find_key(v3, ["errors", "error_count", "total_errors"]))

    closed = to_int(find_key(v3, ["closed", "closed_trades", "total_closed"]))
    if closed == 0:
        closed = to_int(find_key(ack, ["closed", "closed_trades", "total_closed"]))

    drift_remaining = to_int(find_key(v3, ["drift_remaining"]))
    if drift_remaining == 0:
        drift_remaining = to_int(find_key(ack, ["drift_remaining"]))

    capital_remaining = to_int(find_key(v3, ["capital_remaining"]))
    if capital_remaining == 0:
        capital_remaining = to_int(find_key(ack, ["capital_remaining"]))

    performance_status = find_key(
        v3,
        [
            "performance_discipline_status",
            "family_performance_discipline_status",
            "performance_status",
        ],
    )

    negative_watch_families = find_key(v3, ["negative_watch_families"])
    if negative_watch_families is None:
        negative_watch_families = []

    error_ack_valid = (
        ack_policy_status == "ERROR_ACK_POLICY_ACKNOWLEDGED_NON_BLOCKING"
        and ack_applied is True
        and ack_error_blocker_should_block is False
        and new_errors_since_ack_effective_from_ack is False
    )

    if error_ack_valid:
        error_blocker_effective = False
        new_errors_since_ack_effective = False
        info.append("error_ack_overlay_applied")
        info.append("errors_preserved_not_deleted")
    else:
        error_blocker_effective = bool(new_errors_since_ack_original) and errors_original > 0
        new_errors_since_ack_effective = bool(new_errors_since_ack_original)
        attention.append("error_ack_overlay_missing_or_not_valid")

    runtime_ok = to_bool(find_key(v3, ["runtime_ok"]))
    process_ok = to_bool(find_key(v3, ["process_ok"]))
    health_ok = to_bool(find_key(v3, ["health_ok"]))
    snapshot_mismatch = to_bool(find_key(v3, ["snapshot_mismatch"]))

    runtime_clean = runtime_ok is True and process_ok is True and health_ok is True
    snapshot_clean = snapshot_mismatch is False or snapshot_mismatch is None

    if not runtime_clean:
        critical.append("runtime_process_health_not_clean")

    if not snapshot_clean:
        attention.append("snapshot_mismatch_not_clean")

    drift_ready = closed >= 20 or drift_remaining <= 0
    capital_review_ready = closed >= 50 or capital_remaining <= 0

    if critical:
        operator_status = "CYCLE_OPERATOR_V4_CRITICAL_REVIEW"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        recommended_action = "REVIEW_MISSING_INPUTS_OR_RUNTIME_HEALTH"
        reason = "; ".join(critical)
    elif error_blocker_effective:
        operator_status = "CYCLE_OPERATOR_V4_JOURNAL_OR_ERROR_ATTENTION"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        recommended_action = "REVIEW_UNACKNOWLEDGED_ERROR_STATE"
        reason = (
            f"unacknowledged_errors_effective=True; "
            f"errors={errors_original}; "
            f"new_errors_since_ack_effective={new_errors_since_ack_effective}"
        )
    elif drift_ready:
        operator_status = "CYCLE_OPERATOR_V4_READ_ONLY_FAMILY_DRIFT_REVIEW_READY"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        recommended_action = "RUN_READ_ONLY_FAMILY_DRIFT_REVIEW_FOCUS_IMPULSE_LONG"
        reason = (
            f"error_ack_overlay_cleared_error_blocker; "
            f"closed={closed}; drift_remaining={drift_remaining}; "
            f"primary_focus=impulse_long"
        )
    elif performance_status and "WATCH" in str(performance_status).upper():
        operator_status = "CYCLE_OPERATOR_V4_COLLECT_ONLY_PERFORMANCE_WATCH"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        recommended_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_CHANGE_CAPITAL"
        reason = (
            f"error_ack_overlay_cleared_error_blocker; "
            f"closed={closed}; drift_remaining={drift_remaining}; "
            f"performance_status={performance_status}"
        )
    else:
        operator_status = "CYCLE_OPERATOR_V4_COLLECT_ONLY"
        severity = "OK"
        allowed_scope = "COLLECT_ONLY"
        recommended_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"
        reason = (
            f"error_ack_overlay_cleared_error_blocker; "
            f"closed={closed}; drift_remaining={drift_remaining}; "
            f"capital_remaining={capital_remaining}"
        )

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "operator_status": operator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "recommended_action": recommended_action,
        "reason": reason,

        "v3_executed": v3_run.get("ran"),
        "v3_returncode": v3_run.get("returncode"),
        "v3_latest_source": str(V3_LATEST),
        "v3_operator_status": v3_operator_status,
        "v3_severity": v3_severity,
        "v3_allowed_scope": v3_allowed_scope,
        "v3_recommended_action": v3_recommended_action,
        "v3_reason": v3_reason,

        "error_ack_source": str(ACK_LATEST),
        "error_ack_policy_status": ack_policy_status,
        "error_ack_applied": error_ack_valid,
        "errors_original": errors_original,
        "errors_preserved": True,
        "delete_errors_csv_allowed": False,
        "new_errors_since_ack_original": new_errors_since_ack_original,
        "new_errors_since_ack_effective": new_errors_since_ack_effective,
        "error_blocker_effective": error_blocker_effective,

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_ready": drift_ready,
        "capital_review_ready": capital_review_ready,

        "performance_status": performance_status,
        "negative_watch_families": negative_watch_families,

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "snapshot_mismatch": snapshot_mismatch,

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "cycle_operator_v4_state.json"
    out_md = RUN_DIR / "cycle_operator_v4_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS CYCLE OPERATOR v4

operator_status: {operator_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
recommended_action: {recommended_action}  
reason: {reason}

## Error Overlay

error_ack_policy_status: {ack_policy_status}  
error_ack_applied: {error_ack_valid}  
errors_original: {errors_original}  
errors_preserved: True  
delete_errors_csv_allowed: False  
new_errors_since_ack_original: {new_errors_since_ack_original}  
new_errors_since_ack_effective: {new_errors_since_ack_effective}  
error_blocker_effective: {error_blocker_effective}

## Sample

closed: {closed}  
drift_remaining: {drift_remaining}  
capital_remaining: {capital_remaining}  
drift_ready: {drift_ready}  
capital_review_ready: {capital_review_ready}

## v3

v3_operator_status: {v3_operator_status}  
v3_severity: {v3_severity}  
v3_allowed_scope: {v3_allowed_scope}  
v3_recommended_action: {v3_recommended_action}  
v3_reason: {v3_reason}

## Performance

performance_status: {performance_status}  
negative_watch_families: {negative_watch_families}

## Runtime

runtime_ok: {runtime_ok}  
process_ok: {process_ok}  
health_ok: {health_ok}  
snapshot_mismatch: {snapshot_mismatch}

## Safety

mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
real_orders_allowed: False  
execution_performed: False

critical: {critical}  
attention: {attention}  
info: {info}
"""
    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS CYCLE OPERATOR v4")
    print("=" * 100)
    print(f"operator_status: {operator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"recommended_action: {recommended_action}")
    print(f"reason: {reason}")
    print()
    print("ERROR OVERLAY")
    print("-" * 100)
    print(f"error_ack_policy_status: {ack_policy_status}")
    print(f"error_ack_applied: {error_ack_valid}")
    print(f"errors_original: {errors_original}")
    print(f"errors_preserved: True")
    print(f"delete_errors_csv_allowed: False")
    print(f"new_errors_since_ack_original: {new_errors_since_ack_original}")
    print(f"new_errors_since_ack_effective: {new_errors_since_ack_effective}")
    print(f"error_blocker_effective: {error_blocker_effective}")
    print()
    print("SAMPLE")
    print("-" * 100)
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print(f"drift_ready: {drift_ready}")
    print(f"capital_review_ready: {capital_review_ready}")
    print()
    print("v3")
    print("-" * 100)
    print(f"v3_operator_status: {v3_operator_status}")
    print(f"v3_reason: {v3_reason}")
    print()
    print("SAFETY")
    print("-" * 100)
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("real_orders_allowed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
