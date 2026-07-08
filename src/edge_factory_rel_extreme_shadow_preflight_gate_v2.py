#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

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

def inspect_engine_text(engine_path: Path) -> dict[str, Any]:
    text = engine_path.read_text(encoding="utf-8", errors="replace") if engine_path.exists() else ""

    flags = {
        "has_self_test": "--self_test" in text,
        "has_shadow_runtime_arg": "--shadow_runtime" in text,
        "has_candle_dir_arg": "--candle_dir" in text,
        "has_once_arg": "--once" in text,
        "has_poll_seconds_arg": "--poll_seconds" in text,
        "has_loop_runtime": "while True" in text and "time.sleep" in text,
        "has_run_shadow_runtime_once": "def run_shadow_runtime_once" in text,
        "writes_heartbeat": "rel_extreme_shadow_heartbeat.json" in text,
        "writes_signals_csv": "rel_extreme_shadow_signals.csv" in text,
        "writes_closed_csv": "rel_extreme_shadow_closed_trades.csv" in text,
        "writes_result_json": "rel_extreme_shadow_runtime_result.json" in text,
        "writes_audit_csv": "rel_extreme_shadow_candle_file_audit.csv" in text,
        "live_flag_false": "LIVE_ALLOWED = False" in text,
        "active_paper_flag_false": "ACTIVE_PAPER_ALLOWED = False" in text,
        "order_flag_false": "ORDER_PLACEMENT_ALLOWED = False" in text,
        "private_api_flag_false": "PRIVATE_EXCHANGE_API_ALLOWED = False" in text,
    }

    flags["real_market_runtime_available"] = bool(
        flags["has_shadow_runtime_arg"]
        and flags["has_candle_dir_arg"]
        and flags["has_once_arg"]
        and flags["has_loop_runtime"]
        and flags["has_run_shadow_runtime_once"]
        and flags["writes_heartbeat"]
        and flags["writes_signals_csv"]
        and flags["writes_result_json"]
        and flags["writes_audit_csv"]
    )

    flags["safety_flags_ok"] = bool(
        flags["live_flag_false"]
        and flags["active_paper_flag_false"]
        and flags["order_flag_false"]
        and flags["private_api_flag_false"]
    )

    return flags

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_preflight_gate_v2" / f"rel_extreme_shadow_preflight_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_spec_review_v1", "rel_extreme_shadow_spec_")
    adapter_audit_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_adapter_implementation_auditor_v1", "rel_extreme_adapter_audit_")
    engine_builder_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_builder_v2", "rel_extreme_runtime_engine_builder_v2_")
    engine_audit_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_auditor_v2", "rel_extreme_runtime_audit_v2_")

    spec_path = spec_dir / "rel_extreme_shadow_spec.json" if spec_dir else None
    adapter_audit_path = adapter_audit_dir / "rel_extreme_shadow_adapter_implementation_audit_state.json" if adapter_audit_dir else None
    engine_builder_state_path = engine_builder_dir / "rel_extreme_shadow_runtime_engine_builder_v2_state.json" if engine_builder_dir else None
    engine_audit_path = engine_audit_dir / "rel_extreme_shadow_runtime_engine_audit_v2_state.json" if engine_audit_dir else None

    spec = read_json(spec_path)
    adapter_audit = read_json(adapter_audit_path)
    engine_builder = read_json(engine_builder_state_path)
    engine_audit = read_json(engine_audit_path)

    engine_path = Path(str(engine_builder.get("runtime_engine_path", ""))) if engine_builder.get("runtime_engine_path") else None
    adapter_path = Path(str(engine_builder.get("adapter_path", ""))) if engine_builder.get("adapter_path") else None

    engine_flags = inspect_engine_text(engine_path) if engine_path and engine_path.exists() else {}

    runtime_once = engine_audit.get("shadow_runtime_once", {}).get("result", {})
    self_test = engine_audit.get("self_test", {}).get("result", {})

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

    gate("engine_builder_v2_exists", True, bool(engine_builder_state_path and engine_builder_state_path.exists()), engine_builder_state_path)
    gate("engine_exists", True, bool(engine_path and engine_path.exists()), engine_path)
    gate("engine_builder_v2_self_test_ok", True, engine_builder.get("self_test_ok") is True, engine_builder.get("self_test_ok"))
    gate("engine_builder_v2_runtime_once_ok", True, engine_builder.get("shadow_runtime_once_test_ok") is True, engine_builder.get("shadow_runtime_once_test_ok"))

    gate("engine_audit_v2_exists", True, bool(engine_audit_path and engine_audit_path.exists()), engine_audit_path)
    gate("engine_audit_v2_passed", True, engine_audit.get("runtime_engine_v2_audit_passed") is True, engine_audit.get("audit_status"))
    gate("engine_audit_v2_gates_all_passed", True, int(engine_audit.get("gates_passed") or 0) == int(engine_audit.get("gates_total") or -1), f"{engine_audit.get('gates_passed')}/{engine_audit.get('gates_total')}")

    gate("engine_has_real_market_runtime", True, bool(engine_flags.get("real_market_runtime_available")), engine_flags)
    gate("engine_safety_flags_ok", True, bool(engine_flags.get("safety_flags_ok")), engine_flags)

    gate("runtime_once_result_ok", True, runtime_once.get("ok") is True and runtime_once.get("status") == "OK", runtime_once)
    gate("runtime_once_panel_nonempty", True, int(runtime_once.get("close_rows") or 0) > 0 and int(runtime_once.get("close_symbols") or 0) > 0, runtime_once)
    gate("runtime_once_no_live", True, runtime_once.get("live_allowed") is False, runtime_once.get("live_allowed"))
    gate("runtime_once_no_active_paper", True, runtime_once.get("active_paper_allowed") is False, runtime_once.get("active_paper_allowed"))

    gate("self_test_result_ok", True, self_test.get("ok") is True, self_test)
    gate("self_test_no_live", True, self_test.get("live_allowed") is False, self_test.get("live_allowed"))
    gate("self_test_no_active_paper", True, self_test.get("active_paper_allowed") is False, self_test.get("active_paper_allowed"))

    required_passed = sum(1 for g in gates if g["required"] and g["passed"])
    required_total = sum(1 for g in gates if g["required"])
    preflight_passed = required_passed == required_total

    reference_command = None
    if preflight_passed and engine_path:
        reference_command = (
            f'python -u "{engine_path}" '
            f'--shadow_runtime '
            f'--out_dir "{SANDBOX_ROOT}" '
            f'--candle_dir "{WORKSPACE}" '
            f'--market_method median '
            f'--poll_seconds 300'
        )

    status = (
        "REL_EXTREME_SHADOW_PREFLIGHT_V2_PASS_READY_FOR_MANUAL_APPROVAL"
        if preflight_passed
        else "REL_EXTREME_SHADOW_PREFLIGHT_V2_BLOCKED"
    )

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "candidate": CANDIDATE,
        "output_dir": str(out_dir),
        "status": status,
        "preflight_passed": preflight_passed,
        "ready_for_manual_shadow_approval": preflight_passed,
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
        "next_action": "BUILD_REL_EXTREME_MANUAL_SHADOW_APPROVAL_PACKET" if preflight_passed else "FIX_PREFLIGHT_V2_BLOCKERS",
        "hard_rules": [
            "This preflight does not start shadow.",
            "This preflight does not start active paper.",
            "This preflight does not start live.",
            "Manual approval is required before shadow runtime.",
            "MASTER_UPPER_SYSTEM must not be modified by this candidate shadow path.",
        ],
    }

    write_json(out_dir / "rel_extreme_shadow_preflight_gate_v2_state.json", state)
    pd.DataFrame(gates).to_csv(out_dir / "rel_extreme_shadow_preflight_v2_gates.csv", index=False)

    reference_path = out_dir / "rel_extreme_shadow_start_REFERENCE_ONLY.ps1"
    ref = []
    ref.append("# REFERENCE ONLY - DO NOT AUTO-RUN")
    ref.append("# rel_extreme shadow runtime candidate")
    ref.append("# live_allowed: False")
    ref.append("# active_paper_allowed: False")
    ref.append("# requires manual approval record before use")
    ref.append("")
    if reference_command:
        ref.append(reference_command)
    else:
        ref.append("# BLOCKED - preflight did not pass")
    reference_path.write_text("\n".join(ref) + "\n", encoding="utf-8")

    print("EDGE FACTORY REL EXTREME SHADOW PREFLIGHT GATE v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"required_gates: {required_passed}/{required_total}")
    print(f"ready_for_manual_shadow_approval: {preflight_passed}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("ENGINE ENTRYPOINT FLAGS")
    print("-" * 100)
    print(json.dumps(engine_flags, indent=2, ensure_ascii=False))
    print()
    print("REFERENCE COMMAND")
    print("-" * 100)
    print(reference_command or "BLOCKED")
    print()
    print("GATES")
    print("-" * 100)
    print(pd.DataFrame(gates).to_string(index=False))
    print()
    print(f"State    : {out_dir / 'rel_extreme_shadow_preflight_gate_v2_state.json'}")
    print(f"Gates    : {out_dir / 'rel_extreme_shadow_preflight_v2_gates.csv'}")
    print(f"Reference: {reference_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
