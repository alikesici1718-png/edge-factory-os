#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Preflight gate (v1) for the rel_extreme_reversion_short shadow run that validates the spec review, adapter audit, engine builder state, and engine audit results before allowing shadow startup. Reads artifacts from previous pipeline stages and writes a preflight gate state JSON with a pass/block verdict to the edge_factory_rel_extreme_shadow_preflight_gate_v1 directory.
"""
from __future__ import annotations

import ast
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"
SANDBOX_ROOT = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def inspect_engine_entrypoints(engine_path: Path) -> dict[str, Any]:
    text = engine_path.read_text(encoding="utf-8", errors="replace") if engine_path.exists() else ""
    flags = {
        "has_self_test": "--self_test" in text,
        "has_shadow_runtime_arg": "--shadow_runtime" in text,
        "has_candle_input_arg": any(x in text for x in ["--candle_dir", "--candle_csv", "--input_csv", "--market_data_dir"]),
        "has_loop_runtime": any(x in text for x in ["while True", "poll_seconds", "sleep("]),
        "writes_heartbeat": "rel_extreme_shadow_heartbeat.json" in text,
        "writes_signals_csv": "rel_extreme_shadow_signals.csv" in text,
        "writes_closed_csv": "rel_extreme_shadow_closed_trades.csv" in text,
        "explicit_start_block": "shadow start is not allowed" in text.lower() or "shadow_start_allowed_by_this_file: False" in text,
    }

    flags["real_market_runtime_available"] = bool(
        flags["has_shadow_runtime_arg"]
        and flags["has_candle_input_arg"]
        and flags["writes_heartbeat"]
        and flags["writes_signals_csv"]
    )

    return flags

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_preflight_gate_v1" / f"rel_extreme_shadow_preflight_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_spec_review_v1", "rel_extreme_shadow_spec_")
    adapter_audit_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_adapter_implementation_auditor_v1", "rel_extreme_adapter_audit_")
    engine_builder_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_builder_v1", "rel_extreme_runtime_engine_builder_")
    engine_audit_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_auditor_v1", "rel_extreme_runtime_audit_")

    spec_path = spec_dir / "rel_extreme_shadow_spec.json" if spec_dir else None
    adapter_audit_path = adapter_audit_dir / "rel_extreme_shadow_adapter_implementation_audit_state.json" if adapter_audit_dir else None
    engine_builder_state_path = engine_builder_dir / "rel_extreme_shadow_runtime_engine_builder_state.json" if engine_builder_dir else None
    engine_audit_path = engine_audit_dir / "rel_extreme_shadow_runtime_engine_audit_state.json" if engine_audit_dir else None

    spec = read_json(spec_path)
    adapter_audit = read_json(adapter_audit_path)
    engine_builder = read_json(engine_builder_state_path)
    engine_audit = read_json(engine_audit_path)

    engine_path = Path(str(engine_builder.get("runtime_engine_path", ""))) if engine_builder.get("runtime_engine_path") else None
    adapter_path = Path(str(engine_builder.get("adapter_path", ""))) if engine_builder.get("adapter_path") else None

    engine_flags = inspect_engine_entrypoints(engine_path) if engine_path and engine_path.exists() else {}

    gates = []

    def gate(name: str, required: bool, passed: bool, reason: Any):
        gates.append({
            "gate": name,
            "required": bool(required),
            "passed": bool(passed),
            "reason": str(reason),
        })

    gate("spec_exists", True, bool(spec_path and spec_path.exists()), spec_path)
    gate("spec_review_ready", True, spec.get("mode") == "SHADOW_REVIEW_ONLY", spec.get("mode"))
    gate("spec_no_live", True, spec.get("live_allowed") is False, spec.get("live_allowed"))
    gate("spec_no_active_paper", True, spec.get("active_paper_allowed") is False, spec.get("active_paper_allowed"))
    gate("adapter_audit_exists", True, bool(adapter_audit_path and adapter_audit_path.exists()), adapter_audit_path)
    gate("adapter_audit_passed", True, adapter_audit.get("implementation_audit_passed") is True, adapter_audit.get("audit_status"))
    gate("engine_exists", True, bool(engine_path and engine_path.exists()), engine_path)
    gate("engine_audit_exists", True, bool(engine_audit_path and engine_audit_path.exists()), engine_audit_path)
    gate("engine_audit_passed", True, engine_audit.get("runtime_engine_audit_passed") is True, engine_audit.get("audit_status"))
    gate("engine_no_live", True, engine_audit.get("live_allowed") is False, engine_audit.get("live_allowed"))
    gate("engine_no_active_paper", True, engine_audit.get("active_paper_allowed") is False, engine_audit.get("active_paper_allowed"))

    # Critical blocker: current engine is self-test only.
    gate(
        "real_market_runtime_entrypoint",
        True,
        bool(engine_flags.get("real_market_runtime_available")),
        engine_flags,
    )

    gate(
        "runtime_not_explicitly_blocking_start",
        True,
        not bool(engine_flags.get("explicit_start_block")),
        engine_flags,
    )

    required_passed = sum(1 for g in gates if g["required"] and g["passed"])
    required_total = sum(1 for g in gates if g["required"])

    real_runtime_ok = bool(engine_flags.get("real_market_runtime_available")) and not bool(engine_flags.get("explicit_start_block"))

    if required_passed == required_total and real_runtime_ok:
        status = "REL_EXTREME_SHADOW_PREFLIGHT_PASS_READY_FOR_MANUAL_APPROVAL"
        ready_for_manual_approval = True
        next_action = "BUILD_MANUAL_SHADOW_APPROVAL_PACKET"
    else:
        status = "REL_EXTREME_SHADOW_PREFLIGHT_BLOCKED_REAL_RUNTIME_NOT_IMPLEMENTED"
        ready_for_manual_approval = False
        next_action = "BUILD_REL_EXTREME_REAL_MARKET_SHADOW_RUNTIME_ENGINE_V2"

    reference_command = None
    if ready_for_manual_approval and engine_path:
        reference_command = f'python -u "{engine_path}" --shadow_runtime --out_dir "{SANDBOX_ROOT}"'

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "candidate": CANDIDATE,
        "output_dir": str(out_dir),
        "status": status,
        "ready_for_manual_shadow_approval": ready_for_manual_approval,
        "required_gates_passed": required_passed,
        "required_gates_total": required_total,
        "spec_path": str(spec_path) if spec_path else None,
        "adapter_audit_path": str(adapter_audit_path) if adapter_audit_path else None,
        "engine_builder_state_path": str(engine_builder_state_path) if engine_builder_state_path else None,
        "engine_audit_path": str(engine_audit_path) if engine_audit_path else None,
        "engine_path": str(engine_path) if engine_path else None,
        "adapter_path": str(adapter_path) if adapter_path else None,
        "sandbox_root": str(SANDBOX_ROOT),
        "engine_entrypoint_flags": engine_flags,
        "reference_command": reference_command,
        "gates": gates,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(timespec="seconds"),
        "next_action": next_action,
        "hard_rules": [
            "This preflight does not start shadow.",
            "This preflight does not start active paper.",
            "This preflight does not start live.",
            "Manual approval is impossible until real market runtime entrypoint exists.",
            "Self-test-only engine is not enough for shadow runtime.",
        ],
    }

    write_json(out_dir / "rel_extreme_shadow_preflight_gate_state.json", state)
    pd.DataFrame(gates).to_csv(out_dir / "rel_extreme_shadow_preflight_gates.csv", index=False)

    report_path = out_dir / "rel_extreme_shadow_preflight_report.md"
    report = []
    report.append("# REL EXTREME SHADOW PREFLIGHT GATE v1")
    report.append("")
    report.append(f"status: `{status}`")
    report.append(f"required gates: `{required_passed}/{required_total}`")
    report.append("")
    report.append("## Engine flags")
    for k, v in engine_flags.items():
        report.append(f"- {k}: `{v}`")
    report.append("")
    report.append("## Safety")
    report.append("- shadow_start_allowed: `False`")
    report.append("- active_paper_allowed: `False`")
    report.append("- live_allowed: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("EDGE FACTORY REL EXTREME SHADOW PREFLIGHT GATE v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"required_gates: {required_passed}/{required_total}")
    print(f"ready_for_manual_shadow_approval: {ready_for_manual_approval}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("ENGINE ENTRYPOINT FLAGS")
    print("-" * 100)
    print(json.dumps(engine_flags, indent=2, ensure_ascii=False))
    print()
    print("GATES")
    print("-" * 100)
    print(pd.DataFrame(gates).to_string(index=False))
    print()
    print(f"State : {out_dir / 'rel_extreme_shadow_preflight_gate_state.json'}")
    print(f"Gates : {out_dir / 'rel_extreme_shadow_preflight_gates.csv'}")
    print(f"Report: {report_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
