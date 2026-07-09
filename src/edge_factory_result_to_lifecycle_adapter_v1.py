#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converts a candidate result state JSON into a lifecycle transition decision (ARCHIVE, REJECT, WATCHLIST, KEEP_WAITING, etc.) by reading the candidate lifecycle registry and OS interface specs alongside the provided result artifact. Outputs an adapter state JSON with the previous and new lifecycle status to the edge_factory_result_to_lifecycle_adapter_v1 directory.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_result_to_lifecycle_adapter_v1"

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def read_csv(path: Path | None) -> pd.DataFrame:
    if not path or not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def main() -> int:
    ap = argparse.ArgumentParser(description="Convert result artifacts into lifecycle decision.")
    ap.add_argument("--result_state", default="", help="Optional result_state_json path.")
    ap.add_argument("--candidate", default="", help="Optional candidate key.")
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"result_to_lifecycle_adapter_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    registry_dir = latest_dir(WORKSPACE / "edge_factory_candidate_lifecycle_registry_v1", "candidate_lifecycle_registry_v1_")
    registry = read_json(registry_dir / "candidate_lifecycle_registry_v1_state.json" if registry_dir else None)

    interface_dir = latest_dir(WORKSPACE / "edge_factory_os_interface_specs_v1", "os_interface_specs_v1_")
    lifecycle_spec = read_json(interface_dir / "result_to_lifecycle_adapter_spec_v1.json" if interface_dir else None)

    result_state_path = Path(args.result_state) if args.result_state else None
    result_state = read_json(result_state_path) if result_state_path else {}

    candidate_key = args.candidate or result_state.get("candidate_key", "")

    known_candidates = registry.get("candidates", [])
    known = None
    for c in known_candidates:
        if c.get("candidate") == candidate_key:
            known = c
            break

    blockers = []
    reasons = []
    decision = "KEEP_WAITING"
    previous_status = None
    new_status = None

    if not candidate_key:
        blockers.append("NO_CANDIDATE_KEY")
        decision = "NO_DECISION"
        new_status = "UNKNOWN"
    elif not result_state_path or not result_state_path.exists():
        blockers.append("NO_RESULT_STATE_JSON")
        decision = "NO_DECISION"
        new_status = known.get("lifecycle_status") if known else "UNKNOWN"
    elif "__read_error__" in result_state:
        blockers.append("RESULT_STATE_READ_ERROR")
        decision = "NO_DECISION"
        new_status = known.get("lifecycle_status") if known else "UNKNOWN"
    else:
        previous_status = known.get("lifecycle_status") if known else result_state.get("previous_status", "UNKNOWN")

        # Conservative first version: only block/archive/reject/read result; no promotion without manual approval.
        validation_status = result_state.get("validation_status", "")
        result_status = result_state.get("result_status", "")
        duplicate_shadow = bool(result_state.get("duplicate_or_stale_shadow", False))
        live_allowed = bool(result_state.get("live_allowed", False))
        active_paper_allowed = bool(result_state.get("active_paper_allowed", False))

        if live_allowed or active_paper_allowed:
            blockers.append("RESULT_ARTIFACT_TRIED_TO_ENABLE_LIVE_OR_ACTIVE_PAPER")
            decision = "REJECT"
            new_status = "REJECTED"
        elif duplicate_shadow:
            blockers.append("DUPLICATE_OR_STALE_SHADOW")
            decision = "ARCHIVE_WAIT"
            new_status = "ARCHIVE_WAIT"
        elif validation_status in {"TIME_OOS_FAIL", "MARKET_REPLAY_FAIL"} or result_status in {"FAIL", "REJECT"}:
            blockers.append("FAILED_VALIDATION_OR_REPLAY")
            decision = "REJECT"
            new_status = "REJECTED"
        elif validation_status in {"TIME_OOS_PASS", "MARKET_REPLAY_PASS"} or result_status == "PASS":
            blockers.append("MANUAL_APPROVAL_REQUIRED_BEFORE_PROMOTION")
            decision = "KEEP_TESTING"
            new_status = previous_status or "OFFLINE_PASS"
            reasons.append("automated pass is not enough for promotion")
        else:
            blockers.append("UNRECOGNIZED_RESULT_STATUS")
            decision = "KEEP_WAITING"
            new_status = previous_status or "UNKNOWN"

    # Explicitly preserve current rel_extreme archival decision.
    rel_extreme_current = None
    for c in known_candidates:
        if c.get("candidate") == "rel_extreme_reversion_short":
            rel_extreme_current = c
            break

    if candidate_key in {"", "rel_extreme_reversion_short"} and rel_extreme_current:
        previous_status = rel_extreme_current.get("lifecycle_status")
        new_status = "ARCHIVE_WAIT"
        decision = "ARCHIVE_WAIT"
        if "REL_EXTREME_CURRENTLY_ARCHIVE_WAIT" not in blockers:
            blockers.append("REL_EXTREME_CURRENTLY_ARCHIVE_WAIT")
        reasons.extend(rel_extreme_current.get("reasons", []))

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "adapter_status": "RESULT_TO_LIFECYCLE_DECISION_READY",
        "candidate_key": candidate_key or "UNKNOWN",
        "result_state_path": str(result_state_path) if result_state_path else None,
        "previous_status": previous_status,
        "new_status": new_status,
        "decision": decision,
        "reasons": reasons,
        "blockers": blockers,
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Adapter does not modify MASTER_UPPER_SYSTEM.",
            "Adapter does not promote without manual approval.",
            "Adapter does not enable live trading.",
            "Adapter does not change capital.",
            "Adapter only writes lifecycle decision artifacts.",
        ],
        "lifecycle_spec_loaded": bool(lifecycle_spec),
    }

    state_path = out_dir / "result_to_lifecycle_adapter_v1_state.json"
    decision_path = out_dir / "result_to_lifecycle_decision_v1.json"
    report_path = out_dir / "result_to_lifecycle_adapter_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    decision_path.write_text(json.dumps({
        "candidate_key": state["candidate_key"],
        "previous_status": previous_status,
        "new_status": new_status,
        "decision": decision,
        "reasons": reasons,
        "blockers": blockers,
        "manual_approval_required": True,
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Result-to-Lifecycle Adapter v1")
    md.append("")
    md.append(f"Candidate: `{state['candidate_key']}`")
    md.append(f"Decision: `{decision}`")
    md.append(f"Previous status: `{previous_status}`")
    md.append(f"New status: `{new_status}`")
    md.append("")
    md.append("## Blockers")
    if blockers:
        for b in blockers:
            md.append(f"- `{b}`")
    else:
        md.append("- None")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY RESULT TO LIFECYCLE ADAPTER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print("adapter_status: RESULT_TO_LIFECYCLE_DECISION_READY")
    print(f"candidate : {state['candidate_key']}")
    print(f"decision  : {decision}")
    print(f"previous_status: {previous_status}")
    print(f"new_status     : {new_status}")
    print(f"blockers       : {blockers}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print(f"State   : {state_path}")
    print(f"Decision: {decision_path}")
    print(f"Report  : {report_path}")

if __name__ == "__main__":
    main()
