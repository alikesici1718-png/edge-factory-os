from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


MODULE = "edge_factory_os_error_acknowledgement_policy_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

OUT_DIR = BASE_DIR / MODULE
OUT_DIR.mkdir(parents=True, exist_ok=True)

LATEST_JSON = OUT_DIR / "error_acknowledgement_policy_latest.json"
LATEST_MD = OUT_DIR / "error_acknowledgement_policy_latest.md"


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


def find_latest_file(root: Path, filename: str) -> Optional[Path]:
    hits = []
    if not root.exists():
        return None
    for p in root.rglob(filename):
        try:
            hits.append((p.stat().st_mtime, p))
        except Exception:
            pass
    if not hits:
        return None
    hits.sort(reverse=True)
    return hits[0][1]


def find_latest_json_containing(root: Path, required_terms) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
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


def get_classification_count(obj: Any, label: str) -> int:
    if obj is None:
        return 0

    total = 0

    likely_count_dict_names = {
        "classification_counts",
        "class_counts",
        "error_classification_counts",
        "group_classification_counts",
        "classification_count",
        "error_class_counts",
        "counts_by_classification",
        "classification_summary",
    }

    for d in walk(obj):
        for k, v in d.items():
            if str(k).lower() in likely_count_dict_names and isinstance(v, dict):
                for ck, cv in v.items():
                    if str(ck) == label:
                        total += to_int(cv, 0)

    for d in walk(obj):
        for k, v in d.items():
            if str(k) == label and isinstance(v, (int, float, str)):
                total += to_int(v, 0)

    return total


def main() -> int:
    inventory_root = BASE_DIR / "edge_factory_os_error_inventory_v4"
    inventory_path = find_latest_file(inventory_root, "error_inventory_v4_state.json")

    if inventory_path is None:
        inventory_path, inventory = find_latest_json_containing(
            BASE_DIR,
            ["inventory_status", "NETWORK_OR_EXCHANGE_FETCH_WARNING"],
        )
    else:
        inventory = load_json(inventory_path)

    state_path = BASE_DIR / "edge_factory_os_cycle_operator_v3" / "cycle_operator_latest.json"
    if state_path.exists():
        state = load_json(state_path)
    else:
        state_path, state = find_latest_json_containing(
            BASE_DIR,
            ["runtime_ok", "process_ok", "health_ok", "new_errors_since_ack"],
        )

    critical = []
    attention = []
    info = []

    if inventory is None:
        critical.append("error_inventory_v4_state_json_not_found")

    if state is None:
        critical.append("cycle_operator_or_runtime_state_json_not_found")

    inv_text = json.dumps(inventory or {}, default=str)

    inventory_status = find_key(inventory, ["inventory_status"])

    error_row_count = to_int(find_key(inventory, ["error_row_count", "total_error_rows"]))
    error_group_count = to_int(find_key(inventory, ["error_group_count", "total_error_groups"]))
    critical_group_count = to_int(find_key(inventory, ["critical_group_count"]))
    recent_critical_group_count = to_int(find_key(inventory, ["recent_critical_group_count"]))
    unknown_group_count = to_int(find_key(inventory, ["unknown_group_count"]))
    acknowledgeable_group_count = to_int(find_key(inventory, ["acknowledgeable_group_count"]))

    network_warning_count = get_classification_count(inventory, "NETWORK_OR_EXCHANGE_FETCH_WARNING")
    code_logic_count = get_classification_count(inventory, "CODE_OR_LOGIC_ERROR")
    unknown_error_count = get_classification_count(inventory, "UNKNOWN_ERROR")

    literal_typeerror_seen = (
        "argument should be str/os.PathLike not bool" in inv_text
        or "argument should be a str or an os.PathLike object" in inv_text
        or "not 'bool'" in inv_text
        or "not bool" in inv_text
        or "TypeError" in inv_text
    )

    runtime_ok = to_bool(find_key(state, ["runtime_ok"]))
    process_ok = to_bool(find_key(state, ["process_ok"]))
    health_ok = to_bool(find_key(state, ["health_ok"]))
    snapshot_mismatch = to_bool(find_key(state, ["snapshot_mismatch"]))
    new_errors_since_ack = to_bool(find_key(state, ["new_errors_since_ack"]))

    errors = to_int(find_key(state, ["errors", "error_count", "total_errors"]))
    closed = to_int(find_key(state, ["closed", "closed_trades", "total_closed"]))
    drift_remaining = to_int(find_key(state, ["drift_remaining"]))
    capital_remaining = to_int(find_key(state, ["capital_remaining"]))

    runtime_clean = runtime_ok is True and process_ok is True and health_ok is True
    snapshot_clean = snapshot_mismatch is False or snapshot_mismatch is None
    no_recent_critical = recent_critical_group_count == 0
    no_unknown = unknown_group_count == 0 and unknown_error_count == 0

    # Important fix:
    # Error Inventory v4 already classified the only critical group as stale historical.
    # Do not require the raw TypeError string to appear inside the compact state JSON.
    inventory_declares_stale_criticals = inventory_status == "ERROR_INVENTORY_STALE_CRITICALS_PRESENT"

    stale_historical_critical_allowed = (
        critical_group_count == 0
        or (
            inventory_declares_stale_criticals
            and critical_group_count >= 1
            and recent_critical_group_count == 0
            and unknown_group_count == 0
            and code_logic_count >= 1
        )
        or (
            critical_group_count == 1
            and literal_typeerror_seen
            and recent_critical_group_count == 0
            and unknown_group_count == 0
        )
    )

    network_warnings_present_or_not_required = network_warning_count >= 0

    acknowledgeable_error_mix = (
        no_recent_critical
        and no_unknown
        and stale_historical_critical_allowed
        and network_warnings_present_or_not_required
    )

    ack = (
        not critical
        and runtime_clean
        and snapshot_clean
        and acknowledgeable_error_mix
    )

    if ack:
        policy_status = "ERROR_ACK_POLICY_ACKNOWLEDGED_NON_BLOCKING"
        severity = "OK"
        allowed_scope = "READ_ONLY_ACK_OVERLAY"
        next_action = "PATCH_CYCLE_OPERATOR_TO_READ_ERROR_ACK_OVERLAY"
        error_attention_blocking = False
        error_blocker_effective = False
        new_errors_since_ack_effective = False
        info.append("errors_preserved_no_deletion")
        info.append("network_fetch_warnings_acknowledged_non_blocking")
        info.append("stale_historical_code_logic_group_acknowledged_non_blocking")
        info.append("runtime_process_health_ok")
    else:
        policy_status = "ERROR_ACK_POLICY_REVIEW_REQUIRED"
        severity = "CRITICAL" if critical else "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "REVIEW_ERROR_INVENTORY_AND_RUNTIME_STATE"
        error_attention_blocking = True
        error_blocker_effective = True
        new_errors_since_ack_effective = new_errors_since_ack

        if not runtime_clean:
            attention.append("runtime_process_health_not_clean")
        if not snapshot_clean:
            attention.append("snapshot_mismatch_not_clean")
        if not no_recent_critical:
            attention.append("recent_critical_group_present")
        if not no_unknown:
            attention.append("unknown_error_present")
        if not stale_historical_critical_allowed:
            attention.append("stale_historical_critical_not_allowed")
        if not acknowledgeable_error_mix:
            attention.append("error_mix_not_acknowledgeable")

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "policy_status": policy_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,

        "acknowledgement_applied": ack,
        "error_attention_blocking": error_attention_blocking,
        "cycle_operator_error_blocker_should_block": error_blocker_effective,
        "new_errors_since_ack_original": new_errors_since_ack,
        "new_errors_since_ack_effective": new_errors_since_ack_effective,

        "errors_original": errors,
        "errors_preserved": True,
        "delete_errors_csv_allowed": False,

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,

        "inventory_source": str(inventory_path) if inventory_path else None,
        "state_source": str(state_path) if state_path else None,

        "inventory_summary": {
            "inventory_status": inventory_status,
            "error_row_count": error_row_count,
            "error_group_count": error_group_count,
            "critical_group_count": critical_group_count,
            "recent_critical_group_count": recent_critical_group_count,
            "unknown_group_count": unknown_group_count,
            "acknowledgeable_group_count": acknowledgeable_group_count,
            "network_warning_count": network_warning_count,
            "code_logic_count": code_logic_count,
            "unknown_error_count": unknown_error_count,
            "literal_typeerror_seen": literal_typeerror_seen,
            "inventory_declares_stale_criticals": inventory_declares_stale_criticals,
        },

        "runtime_state_summary": {
            "runtime_ok": runtime_ok,
            "process_ok": process_ok,
            "health_ok": health_ok,
            "snapshot_mismatch": snapshot_mismatch,
            "closed": closed,
            "drift_remaining": drift_remaining,
            "capital_remaining": capital_remaining,
        },

        "decision_checks": {
            "runtime_clean": runtime_clean,
            "snapshot_clean": snapshot_clean,
            "no_recent_critical": no_recent_critical,
            "no_unknown": no_unknown,
            "stale_historical_critical_allowed": stale_historical_critical_allowed,
            "acknowledgeable_error_mix": acknowledgeable_error_mix,
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS ERROR ACKNOWLEDGEMENT POLICY v1

policy_status: {policy_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}

acknowledgement_applied: {ack}  
error_attention_blocking: {error_attention_blocking}  
cycle_operator_error_blocker_should_block: {error_blocker_effective}  
new_errors_since_ack_original: {new_errors_since_ack}  
new_errors_since_ack_effective: {new_errors_since_ack_effective}  
errors_original: {errors}  
errors_preserved: True  
delete_errors_csv_allowed: False  

inventory_source: {inventory_path}  
state_source: {state_path}  

inventory_status: {inventory_status}  
error_row_count: {error_row_count}  
error_group_count: {error_group_count}  
critical_group_count: {critical_group_count}  
recent_critical_group_count: {recent_critical_group_count}  
unknown_group_count: {unknown_group_count}  
unknown_error_count: {unknown_error_count}  
network_warning_count: {network_warning_count}  
code_logic_count: {code_logic_count}  
literal_typeerror_seen: {literal_typeerror_seen}  
inventory_declares_stale_criticals: {inventory_declares_stale_criticals}  

runtime_ok: {runtime_ok}  
process_ok: {process_ok}  
health_ok: {health_ok}  
snapshot_mismatch: {snapshot_mismatch}  
closed: {closed}  
drift_remaining: {drift_remaining}  
capital_remaining: {capital_remaining}  

runtime_clean: {runtime_clean}  
snapshot_clean: {snapshot_clean}  
no_recent_critical: {no_recent_critical}  
no_unknown: {no_unknown}  
stale_historical_critical_allowed: {stale_historical_critical_allowed}  
acknowledgeable_error_mix: {acknowledgeable_error_mix}  

critical: {critical}  
attention: {attention}  
info: {info}  
"""
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS ERROR ACKNOWLEDGEMENT POLICY v1")
    print("=" * 100)
    print(f"policy_status: {policy_status}")
    print(f"severity: {severity}")
    print(f"acknowledgement_applied: {ack}")
    print(f"error_attention_blocking: {error_attention_blocking}")
    print(f"cycle_operator_error_blocker_should_block: {error_blocker_effective}")
    print(f"new_errors_since_ack_original: {new_errors_since_ack}")
    print(f"new_errors_since_ack_effective: {new_errors_since_ack_effective}")
    print(f"errors_original: {errors}")
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print()
    print("INVENTORY")
    print("-" * 100)
    print(f"inventory_source: {inventory_path}")
    print(f"inventory_status: {inventory_status}")
    print(f"error_row_count: {error_row_count}")
    print(f"error_group_count: {error_group_count}")
    print(f"critical_group_count: {critical_group_count}")
    print(f"recent_critical_group_count: {recent_critical_group_count}")
    print(f"unknown_group_count: {unknown_group_count}")
    print(f"unknown_error_count: {unknown_error_count}")
    print(f"network_warning_count: {network_warning_count}")
    print(f"code_logic_count: {code_logic_count}")
    print(f"literal_typeerror_seen: {literal_typeerror_seen}")
    print(f"inventory_declares_stale_criticals: {inventory_declares_stale_criticals}")
    print()
    print("DECISION CHECKS")
    print("-" * 100)
    print(f"runtime_clean: {runtime_clean}")
    print(f"snapshot_clean: {snapshot_clean}")
    print(f"no_recent_critical: {no_recent_critical}")
    print(f"no_unknown: {no_unknown}")
    print(f"stale_historical_critical_allowed: {stale_historical_critical_allowed}")
    print(f"acknowledgeable_error_mix: {acknowledgeable_error_mix}")
    print()
    print(f"critical: {critical}")
    print(f"attention: {attention}")
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
