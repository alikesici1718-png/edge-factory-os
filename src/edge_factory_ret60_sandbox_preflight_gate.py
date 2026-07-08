#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 SANDBOX PREFLIGHT GATE v1
============================================

Purpose
-------
Build a supervised preflight gate for the ret60 sandbox shadow logger after the
implementation audit passed.

This module is the next safe step after:
    edge_factory_ret60_sandbox_logger_implementation_auditor.py

It checks that:
    - blueprint exists and is ready
    - adapter exists and was written
    - implementation audit passed
    - adapter self-test passed
    - native log contract exists and was emitted in self-test
    - active paper remains blocked
    - live remains blocked
    - sandbox runtime command can be referenced only, not executed
    - manual approval is still required before shadow start

It DOES NOT:
    - start shadow paper
    - start active paper
    - start live
    - run logger runtime
    - connect to exchange APIs
    - send orders
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - create a preflight decision packet
    - create commented REFERENCE_ONLY commands
    - create expected runtime/log file contract
    - keep shadow start blocked until manual approval is recorded

Run:
    python "C:\Users\alike\edge_factory_ret60_sandbox_preflight_gate.py"

Core rule
---------
Preflight pass is not start permission. It only allows moving to manual shadow approval.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"
DEFAULT_SANDBOX_ROOT_NAME = "paper_run_shadow_ret60_reversal_short"

REQUIRED_NATIVE_FIELDS = [
    "event_id",
    "candidate_key",
    "signal_version",
    "symbol",
    "side",
    "signal_time_utc",
    "hour_utc",
    "signal_ret60_bps",
    "ret60_rule_passed",
    "delay_minutes",
    "planned_entry_time_utc",
    "actual_paper_entry_time_utc",
    "entry_reference_price",
    "hold_minutes",
    "planned_exit_time_utc",
    "actual_paper_exit_time_utc",
    "exit_reference_price",
    "gross_return_bps_native",
    "fee_bps_assumption",
    "spread_bps_at_signal",
    "slippage_bps_assumption",
    "extra_slip_bps",
    "net_return_bps_native",
    "gross_pnl_usdt",
    "net_pnl_usdt",
    "notional_usdt",
    "source_candle_basis",
    "feature_calculation_version",
    "logger_version",
    "runtime_mode",
]


@dataclass
class SourceArtifact:
    name: str
    path: Optional[str]
    exists: bool
    status: str
    key_fields: Dict[str, Any]
    warnings: List[str]


@dataclass
class PreflightGate:
    gate_id: str
    category: str
    required_for_preflight: bool
    required_for_future_shadow_start: bool
    passed: bool
    status: str
    reason: str
    details: str


@dataclass
class RuntimePlan:
    candidate_key: str
    runtime_mode: str
    sandbox_root: str
    adapter_path: Optional[str]
    manifest_path: Optional[str]
    expected_log_csv: str
    expected_state_json: str
    expected_heartbeat_json: str
    expected_closed_trades_csv: str
    expected_native_fields: List[str]
    forbidden_actions: List[str]
    reference_command: str
    command_is_reference_only: bool


@dataclass
class PreflightState:
    generated_at: str
    workspace: str
    candidate: str
    output_dir: str
    preflight_status: str
    preflight_passed: bool
    ready_for_manual_shadow_approval: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    implementation_audit_passed: bool
    native_log_verified: bool
    runtime_plan_created: bool
    gates_passed_for_preflight: int
    gates_required_for_preflight: int
    gates_passed_for_shadow_start: int
    gates_required_for_shadow_start: int
    expires_at: str
    next_action: str
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_key(x: Any) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_json_optional(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def latest_blueprint_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_sandbox_logger_blueprint", "ret60_logger_blueprint_")
    if not d:
        return None
    p = d / "ret60_sandbox_logger_blueprint_state.json"
    return p if p.exists() else None


def latest_adapter_manifest(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_sandbox_logger_adapter_builder", "ret60_adapter_builder_")
    if not d:
        return None
    p = d / "ret60_sandbox_logger_adapter_manifest.json"
    return p if p.exists() else None


def latest_implementation_audit_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_sandbox_logger_implementation_auditor", "ret60_implementation_audit_")
    if not d:
        return None
    p = d / "ret60_sandbox_logger_implementation_audit_state.json"
    return p if p.exists() else None


def load_sources(workspace: Path, blueprint_state: Optional[str], adapter_manifest: Optional[str], implementation_audit_state: Optional[str]) -> List[SourceArtifact]:
    bp_path = Path(blueprint_state) if blueprint_state else latest_blueprint_state(workspace)
    mf_path = Path(adapter_manifest) if adapter_manifest else latest_adapter_manifest(workspace)
    audit_path = Path(implementation_audit_state) if implementation_audit_state else latest_implementation_audit_state(workspace)

    sources: List[SourceArtifact] = []

    bp_obj = read_json_optional(bp_path)
    bp_state = bp_obj.get("state", {}) if isinstance(bp_obj.get("state"), dict) else {}
    bp_contract = bp_obj.get("signal_contract", {}) if isinstance(bp_obj.get("signal_contract"), dict) else {}
    sources.append(SourceArtifact(
        name="blueprint",
        path=str(bp_path) if bp_path else None,
        exists=bool(bp_path and bp_path.exists()),
        status=str(bp_state.get("blueprint_status") or "MISSING"),
        key_fields={
            "blueprint_ready": bp_state.get("blueprint_ready"),
            "sandbox_logger_implementation_allowed": bp_state.get("sandbox_logger_implementation_allowed"),
            "shadow_start_allowed": bp_state.get("shadow_start_allowed"),
            "active_paper_allowed": bp_state.get("active_paper_allowed"),
            "live_allowed": bp_state.get("live_allowed"),
            "selected_variant_key": bp_state.get("selected_variant_key") or bp_contract.get("selected_variant_key"),
            "ret60_rule": bp_contract.get("ret60_rule"),
        },
        warnings=[] if bp_path and bp_path.exists() else ["blueprint state missing"],
    ))

    mf_obj = read_json_optional(mf_path)
    mf_state = mf_obj.get("state", {}) if isinstance(mf_obj.get("state"), dict) else {}
    sources.append(SourceArtifact(
        name="adapter_manifest",
        path=str(mf_path) if mf_path else None,
        exists=bool(mf_path and mf_path.exists()),
        status=str(mf_state.get("builder_status") or "MISSING"),
        key_fields={
            "adapter_written": mf_state.get("adapter_written"),
            "adapter_path": mf_state.get("adapter_path"),
            "manifest_path": mf_state.get("manifest_path"),
            "shadow_start_allowed": mf_state.get("shadow_start_allowed"),
            "active_paper_allowed": mf_state.get("active_paper_allowed"),
            "live_allowed": mf_state.get("live_allowed"),
        },
        warnings=[] if mf_path and mf_path.exists() else ["adapter manifest missing"],
    ))

    audit_obj = read_json_optional(audit_path)
    audit_state = audit_obj.get("state", {}) if isinstance(audit_obj.get("state"), dict) else {}
    self_test = audit_obj.get("self_test", {}) if isinstance(audit_obj.get("self_test"), dict) else {}
    sources.append(SourceArtifact(
        name="implementation_audit",
        path=str(audit_path) if audit_path else None,
        exists=bool(audit_path and audit_path.exists()),
        status=str(audit_state.get("audit_status") or "MISSING"),
        key_fields={
            "implementation_audit_passed": audit_state.get("implementation_audit_passed"),
            "adapter_compiles": audit_state.get("adapter_compiles"),
            "self_test_ok": audit_state.get("self_test_ok"),
            "native_log_ok": audit_state.get("native_log_ok"),
            "dangerous_code_detected": audit_state.get("dangerous_code_detected"),
            "shadow_start_allowed": audit_state.get("shadow_start_allowed"),
            "active_paper_allowed": audit_state.get("active_paper_allowed"),
            "live_allowed": audit_state.get("live_allowed"),
            "self_test_csv": self_test.get("csv_path"),
            "self_test_result_json": self_test.get("result_json_path"),
        },
        warnings=[] if audit_path and audit_path.exists() else ["implementation audit state missing"],
    ))

    return sources


def src(sources: List[SourceArtifact], name: str) -> SourceArtifact:
    for s in sources:
        if s.name == name:
            return s
    return SourceArtifact(name, None, False, "MISSING", {}, ["source not loaded"])


def verify_native_csv(path: Optional[str]) -> Dict[str, Any]:
    if not path or not Path(path).exists():
        return {"exists": False, "rows": 0, "required_fields_present": False, "missing_fields": REQUIRED_NATIVE_FIELDS}
    try:
        df = pd.read_csv(path)
        missing = [c for c in REQUIRED_NATIVE_FIELDS if c not in df.columns]
        return {
            "exists": True,
            "rows": int(len(df)),
            "required_fields_present": len(missing) == 0,
            "missing_fields": missing,
            "runtime_modes": sorted(df.get("runtime_mode", pd.Series(dtype=str)).astype(str).unique().tolist()) if "runtime_mode" in df.columns else [],
        }
    except Exception as e:
        return {"exists": True, "rows": 0, "required_fields_present": False, "missing_fields": REQUIRED_NATIVE_FIELDS, "error": str(e)}


def build_runtime_plan(workspace: Path, sources: List[SourceArtifact]) -> RuntimePlan:
    adapter = src(sources, "adapter_manifest")
    adapter_path = adapter.key_fields.get("adapter_path")
    manifest_path = adapter.key_fields.get("manifest_path") or adapter.path
    sandbox_root = workspace / DEFAULT_SANDBOX_ROOT_NAME
    expected_log = sandbox_root / "ret60_shadow_native_events.csv"
    expected_state = sandbox_root / "ret60_shadow_runtime_state.json"
    expected_heartbeat = sandbox_root / "ret60_shadow_heartbeat.json"
    expected_closed = sandbox_root / "ret60_shadow_closed_trades.csv"

    command = (
        f'# REFERENCE ONLY - DO NOT RUN UNTIL MANUAL APPROVAL GATE PASSES\n'
        f'# python "{adapter_path}" --self_test --out_dir "{sandbox_root / "adapter_self_test_only"}"\n'
        f'# Future real shadow runtime command must be generated by shadow_start_gate, not by preflight.\n'
    )

    return RuntimePlan(
        candidate_key=DEFAULT_CANDIDATE,
        runtime_mode="shadow_sandbox_reference_only",
        sandbox_root=str(sandbox_root),
        adapter_path=str(adapter_path) if adapter_path else None,
        manifest_path=str(manifest_path) if manifest_path else None,
        expected_log_csv=str(expected_log),
        expected_state_json=str(expected_state),
        expected_heartbeat_json=str(expected_heartbeat),
        expected_closed_trades_csv=str(expected_closed),
        expected_native_fields=REQUIRED_NATIVE_FIELDS,
        forbidden_actions=[
            "live orders",
            "private exchange API",
            "MASTER_UPPER_SYSTEM modification",
            "position sizing contract modification",
            "active paper inclusion",
            "automatic shadow start before manual approval",
        ],
        reference_command=command,
        command_is_reference_only=True,
    )


def build_gates(sources: List[SourceArtifact], native_check: Dict[str, Any], runtime_plan: RuntimePlan) -> List[PreflightGate]:
    gates: List[PreflightGate] = []

    def add(gate_id: str, category: str, pre_req: bool, shadow_req: bool, passed: bool, reason: str, details: str = "") -> None:
        gates.append(PreflightGate(
            gate_id=gate_id,
            category=category,
            required_for_preflight=pre_req,
            required_for_future_shadow_start=shadow_req,
            passed=bool(passed),
            status="PASS" if passed else "FAIL",
            reason=reason,
            details=details,
        ))

    bp = src(sources, "blueprint")
    mf = src(sources, "adapter_manifest")
    au = src(sources, "implementation_audit")

    add("blueprint_exists", "artifact", True, True, bp.exists, "blueprint state must exist")
    add("blueprint_ready", "blueprint", True, True, bool(bp.key_fields.get("blueprint_ready")), "blueprint must be ready")
    add("blueprint_allows_implementation", "blueprint", True, True, bool(bp.key_fields.get("sandbox_logger_implementation_allowed")), "blueprint must allow implementation")
    add("adapter_manifest_exists", "artifact", True, True, mf.exists, "adapter manifest must exist")
    add("adapter_written", "implementation", True, True, bool(mf.key_fields.get("adapter_written")), "adapter must be written")
    adapter_path = mf.key_fields.get("adapter_path")
    add("adapter_file_exists", "implementation", True, True, bool(adapter_path and Path(str(adapter_path)).exists()), "adapter file must exist", str(adapter_path))
    add("implementation_audit_exists", "artifact", True, True, au.exists, "implementation audit must exist")
    add("implementation_audit_passed", "audit", True, True, bool(au.key_fields.get("implementation_audit_passed")), "implementation audit must pass")
    add("adapter_compiles", "audit", True, True, bool(au.key_fields.get("adapter_compiles")), "adapter must compile")
    add("self_test_ok", "audit", True, True, bool(au.key_fields.get("self_test_ok")), "adapter self-test must pass")
    add("native_log_ok", "logging", True, True, bool(au.key_fields.get("native_log_ok")), "implementation audit must verify native log")
    add("native_csv_exists", "logging", True, True, bool(native_check.get("exists")), "self-test native CSV must exist")
    add("native_csv_has_required_fields", "logging", True, True, bool(native_check.get("required_fields_present")), "self-test native CSV must have required fields", "missing=" + ", ".join(native_check.get("missing_fields", [])))
    add("no_dangerous_code", "safety", True, True, not bool(au.key_fields.get("dangerous_code_detected")), "audit must not detect dangerous code")
    add("blueprint_live_blocked", "safety", True, True, not bool(bp.key_fields.get("live_allowed")), "blueprint live must be blocked")
    add("adapter_live_blocked", "safety", True, True, not bool(mf.key_fields.get("live_allowed")), "adapter builder live must be blocked")
    add("audit_live_blocked", "safety", True, True, not bool(au.key_fields.get("live_allowed")), "implementation audit live must be blocked")
    add("active_paper_blocked", "safety", True, True, not bool(bp.key_fields.get("active_paper_allowed")) and not bool(mf.key_fields.get("active_paper_allowed")) and not bool(au.key_fields.get("active_paper_allowed")), "active paper must be blocked across all sources")
    add("shadow_start_blocked_now", "safety", True, False, not bool(bp.key_fields.get("shadow_start_allowed")) and not bool(mf.key_fields.get("shadow_start_allowed")) and not bool(au.key_fields.get("shadow_start_allowed")), "shadow start must remain blocked before manual approval")
    add("runtime_plan_reference_only", "runtime_plan", True, True, bool(runtime_plan.command_is_reference_only), "preflight command must be reference only")
    add("manual_shadow_approval_missing", "approval", False, True, False, "future shadow start requires manual approval")
    return gates


def synthesize_state(workspace: Path, out_dir: Path, sources: List[SourceArtifact], gates: List[PreflightGate], native_check: Dict[str, Any]) -> PreflightState:
    req_pre = [g for g in gates if g.required_for_preflight]
    pass_pre = [g for g in req_pre if g.passed]
    req_shadow = [g for g in gates if g.required_for_future_shadow_start]
    pass_shadow = [g for g in req_shadow if g.passed]

    preflight_passed = len(pass_pre) == len(req_pre)
    blockers: List[str] = []
    warnings: List[str] = []
    reasons: List[str] = []

    for s in sources:
        warnings.extend([f"{s.name}: {w}" for w in s.warnings])

    if preflight_passed:
        status = "RET60_SANDBOX_PREFLIGHT_PASS_READY_FOR_MANUAL_SHADOW_APPROVAL"
        next_action = "BUILD_RET60_MANUAL_SHADOW_APPROVAL_PACKET"
        reasons.append("all required preflight gates passed")
        reasons.append("ret60 sandbox adapter is ready for human/manual shadow approval packet")
        ready_manual = True
    else:
        status = "RET60_SANDBOX_PREFLIGHT_BLOCKED"
        next_action = "REPAIR_FAILED_PREFLIGHT_GATES"
        blockers.extend([f"{g.gate_id}: {g.reason} {g.details}" for g in req_pre if not g.passed])
        ready_manual = False

    missing_shadow = [g.gate_id for g in req_shadow if not g.passed]
    if missing_shadow:
        warnings.append("future shadow start remains blocked by: " + ", ".join(missing_shadow))

    expires_at = (datetime.now() + timedelta(hours=24)).isoformat(timespec="seconds")

    return PreflightState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=DEFAULT_CANDIDATE,
        output_dir=str(out_dir),
        preflight_status=status,
        preflight_passed=preflight_passed,
        ready_for_manual_shadow_approval=ready_manual,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        implementation_audit_passed=bool(src(sources, "implementation_audit").key_fields.get("implementation_audit_passed")),
        native_log_verified=bool(native_check.get("required_fields_present")),
        runtime_plan_created=True,
        gates_passed_for_preflight=len(pass_pre),
        gates_required_for_preflight=len(req_pre),
        gates_passed_for_shadow_start=len(pass_shadow),
        gates_required_for_shadow_start=len(req_shadow),
        expires_at=expires_at,
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        hard_rules=[
            "Preflight gate never starts shadow paper, active paper, or live.",
            "Preflight gate never runs logger runtime.",
            "Preflight gate never mutates active config.",
            "Preflight gate never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Preflight pass only allows manual approval packet generation.",
            "Shadow start remains blocked until manual approval and shadow start gate pass.",
            "Live remains blocked.",
        ],
    )


def records_df(items: List[Any]) -> pd.DataFrame:
    rows = []
    for x in items:
        d = asdict(x)
        for k, v in list(d.items()):
            if isinstance(v, list):
                d[k] = " | ".join(str(i) for i in v)
            if isinstance(v, dict):
                d[k] = json.dumps(v, ensure_ascii=False, default=str)
        rows.append(d)
    return pd.DataFrame(rows)


def write_outputs(out_dir: Path, state: PreflightState, sources: List[SourceArtifact], gates: List[PreflightGate], runtime_plan: RuntimePlan, native_check: Dict[str, Any]) -> None:
    payload = {
        "state": asdict(state),
        "sources": [asdict(s) for s in sources],
        "gates": [asdict(g) for g in gates],
        "runtime_plan": asdict(runtime_plan),
        "native_check": native_check,
    }
    write_json(out_dir / "ret60_sandbox_preflight_state.json", payload)
    write_json(out_dir / "ret60_sandbox_runtime_plan_REFERENCE_ONLY.json", asdict(runtime_plan))
    records_df(gates).to_csv(out_dir / "ret60_sandbox_preflight_gates.csv", index=False)
    records_df(sources).to_csv(out_dir / "ret60_sandbox_preflight_sources.csv", index=False)

    write_text(out_dir / "ret60_shadow_start_REFERENCE_ONLY.ps1", runtime_plan.reference_command)

    md = f"""# Ret60 Sandbox Preflight Gate

Status: **{state.preflight_status}**

- Preflight passed: `{state.preflight_passed}`
- Ready for manual shadow approval: `{state.ready_for_manual_shadow_approval}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`
- Expires at: `{state.expires_at}`

## Runtime plan

- Sandbox root: `{runtime_plan.sandbox_root}`
- Adapter: `{runtime_plan.adapter_path}`
- Expected log CSV: `{runtime_plan.expected_log_csv}`
- Expected state JSON: `{runtime_plan.expected_state_json}`
- Expected heartbeat JSON: `{runtime_plan.expected_heartbeat_json}`

## Next action

`{state.next_action}`

## Blockers

```text
{chr(10).join(state.blockers) if state.blockers else 'none'}
```

## Warnings

```text
{chr(10).join(state.warnings) if state.warnings else 'none'}
```

## Important

This preflight did not start the adapter. Reference command is commented only.
"""
    write_text(out_dir / "ret60_sandbox_preflight_report.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ret60 sandbox preflight gate")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--blueprint_state", default=None)
    p.add_argument("--adapter_manifest", default=None)
    p.add_argument("--implementation_audit_state", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_sandbox_preflight_gate"
    out_dir = out_root / f"ret60_sandbox_preflight_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources(workspace, args.blueprint_state, args.adapter_manifest, args.implementation_audit_state)
    runtime_plan = build_runtime_plan(workspace, sources)
    audit = src(sources, "implementation_audit")
    native_check = verify_native_csv(audit.key_fields.get("self_test_csv"))
    gates = build_gates(sources, native_check, runtime_plan)
    state = synthesize_state(workspace, out_dir, sources, gates, native_check)
    write_outputs(out_dir, state, sources, gates, runtime_plan, native_check)

    print("EDGE FACTORY RET60 SANDBOX PREFLIGHT GATE v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {DEFAULT_CANDIDATE}")
    print(f"output_dir: {out_dir}")
    print(f"preflight_status: {state.preflight_status}")
    print(f"preflight_passed: {state.preflight_passed}")
    print(f"ready_for_manual_shadow_approval: {state.ready_for_manual_shadow_approval}")
    print(f"implementation_audit_passed: {state.implementation_audit_passed}")
    print(f"native_log_verified: {state.native_log_verified}")
    print(f"runtime_plan_created: {state.runtime_plan_created}")
    print(f"preflight_gates: {state.gates_passed_for_preflight}/{state.gates_required_for_preflight}")
    print(f"future_shadow_gates: {state.gates_passed_for_shadow_start}/{state.gates_required_for_shadow_start}")
    print(f"expires_at: {state.expires_at}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("")
    print("RUNTIME PLAN")
    print("-" * 100)
    print(f"sandbox_root: {runtime_plan.sandbox_root}")
    print(f"adapter_path: {runtime_plan.adapter_path}")
    print(f"expected_log_csv: {runtime_plan.expected_log_csv}")
    print(f"reference_command: {out_dir / 'ret60_shadow_start_REFERENCE_ONLY.ps1'}")
    if state.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in state.blockers:
            print(f"- {b}")
    if state.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start shadow/active paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'ret60_sandbox_preflight_report.md'}")
    print(f"State  : {out_dir / 'ret60_sandbox_preflight_state.json'}")
    print(f"Gates  : {out_dir / 'ret60_sandbox_preflight_gates.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
