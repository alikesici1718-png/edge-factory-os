#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 SHADOW START GATE v1
=======================================

Purpose
-------
Read the latest ret60 manual shadow approval record and decide whether shadow runtime
can be started.

Important
---------
This module DOES NOT start the logger. It only gates the transition.

It should normally find:
    - preflight passed
    - manual approval granted
    - active paper blocked
    - live blocked

But if the generated adapter only supports --self_test and does not yet include a real
shadow runtime loop, this gate must block start and route to a runtime engine builder.

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
    - verify manual approval record
    - verify preflight record
    - verify adapter path
    - verify safety blocks
    - detect whether a real shadow runtime entrypoint exists
    - write a start-gate decision
    - write a runtime engine requirements file if start is blocked

Run:
    python "C:\Users\alike\edge_factory_ret60_shadow_start_gate.py"

Core rule
---------
Even with manual approval, this gate cannot start if the runtime engine is not implemented.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"


@dataclass
class GateSource:
    name: str
    path: Optional[str]
    exists: bool
    status: str
    key_fields: Dict[str, Any]
    warnings: List[str]


@dataclass
class StartGateCheck:
    check_id: str
    category: str
    required_for_start_reference: bool
    passed: bool
    status: str
    reason: str
    evidence: str


@dataclass
class RuntimeEngineRequirement:
    requirement_id: str
    required: bool
    satisfied: bool
    reason: str


@dataclass
class ShadowStartDecision:
    candidate: str
    decision_status: str
    start_reference_allowed: bool
    shadow_runtime_start_executed: bool
    shadow_runtime_engine_available: bool
    approval_valid: bool
    preflight_valid: bool
    active_paper_allowed: bool
    live_allowed: bool
    next_action: str
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]


@dataclass
class ShadowStartGateState:
    generated_at: str
    workspace: str
    candidate: str
    output_dir: str
    approval_record_path: Optional[str]
    preflight_state_path: Optional[str]
    adapter_path: Optional[str]
    decision_status: str
    checks_passed: int
    checks_required: int
    requirements_satisfied: int
    requirements_total: int
    start_reference_allowed: bool
    shadow_runtime_start_executed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    next_action: str
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


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


def parse_time_maybe(s: Any) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def latest_preflight_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_sandbox_preflight_gate", "ret60_sandbox_preflight_")
    if not d:
        return None
    p = d / "ret60_sandbox_preflight_state.json"
    return p if p.exists() else None


def latest_approval_record(workspace: Path) -> Optional[Path]:
    root = workspace / "edge_factory_ret60_manual_shadow_approval_recorder"
    ledger = root / "master_ret60_manual_shadow_approval_ledger.jsonl"
    if ledger.exists():
        rows: List[Dict[str, Any]] = []
        with ledger.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
        granted = [r for r in rows if r.get("manual_approval_granted") is True and r.get("shadow_start_allowed_by_approval_record") is True]
        if granted:
            latest = granted[-1]
            rp = latest.get("record_path")
            if rp and Path(rp).exists():
                return Path(rp)
    d = latest_child_dir(root, "ret60_manual_approval_")
    if not d:
        return None
    p = d / "ret60_manual_shadow_approval_record.json"
    return p if p.exists() else None


def load_sources(workspace: Path, approval_record: Optional[str], preflight_state: Optional[str]) -> List[GateSource]:
    ap = Path(approval_record) if approval_record else latest_approval_record(workspace)
    pp = Path(preflight_state) if preflight_state else latest_preflight_state(workspace)
    approval = read_json_optional(ap)
    preflight = read_json_optional(pp)

    approval_state = approval.get("state", {}) if isinstance(approval.get("state"), dict) else {}
    preflight_state_obj = preflight.get("state", {}) if isinstance(preflight.get("state"), dict) else {}
    runtime_plan = preflight.get("runtime_plan", {}) if isinstance(preflight.get("runtime_plan"), dict) else {}

    return [
        GateSource(
            name="manual_approval",
            path=str(ap) if ap else None,
            exists=bool(ap and ap.exists()),
            status=str(approval_state.get("approval_status") or "MISSING"),
            key_fields={
                "manual_approval_granted": approval_state.get("manual_approval_granted"),
                "shadow_start_allowed_by_approval_record": approval_state.get("shadow_start_allowed_by_approval_record"),
                "active_paper_allowed": approval_state.get("active_paper_allowed"),
                "live_allowed": approval_state.get("live_allowed"),
                "expires_at": approval_state.get("expires_at"),
                "approval_id": approval_state.get("approval_id"),
            },
            warnings=[] if ap and ap.exists() else ["approval record missing"],
        ),
        GateSource(
            name="preflight",
            path=str(pp) if pp else None,
            exists=bool(pp and pp.exists()),
            status=str(preflight_state_obj.get("preflight_status") or "MISSING"),
            key_fields={
                "preflight_passed": preflight_state_obj.get("preflight_passed"),
                "ready_for_manual_shadow_approval": preflight_state_obj.get("ready_for_manual_shadow_approval"),
                "implementation_audit_passed": preflight_state_obj.get("implementation_audit_passed"),
                "native_log_verified": preflight_state_obj.get("native_log_verified"),
                "runtime_plan_created": preflight_state_obj.get("runtime_plan_created"),
                "shadow_start_allowed": preflight_state_obj.get("shadow_start_allowed"),
                "active_paper_allowed": preflight_state_obj.get("active_paper_allowed"),
                "live_allowed": preflight_state_obj.get("live_allowed"),
                "expires_at": preflight_state_obj.get("expires_at"),
                "adapter_path": runtime_plan.get("adapter_path"),
                "sandbox_root": runtime_plan.get("sandbox_root"),
                "expected_log_csv": runtime_plan.get("expected_log_csv"),
                "command_is_reference_only": runtime_plan.get("command_is_reference_only"),
            },
            warnings=[] if pp and pp.exists() else ["preflight state missing"],
        ),
    ]


def src(sources: List[GateSource], name: str) -> GateSource:
    for s in sources:
        if s.name == name:
            return s
    return GateSource(name, None, False, "MISSING", {}, ["source not loaded"])


def approval_valid(approval: GateSource) -> tuple[bool, List[str]]:
    warnings: List[str] = []
    exp = parse_time_maybe(approval.key_fields.get("expires_at"))
    if exp is None:
        warnings.append("approval expiration missing/unreadable")
        not_expired = False
    else:
        not_expired = datetime.now() <= exp
    valid = (
        approval.exists
        and approval.key_fields.get("manual_approval_granted") is True
        and approval.key_fields.get("shadow_start_allowed_by_approval_record") is True
        and approval.key_fields.get("active_paper_allowed") is False
        and approval.key_fields.get("live_allowed") is False
        and not_expired
    )
    if not not_expired:
        warnings.append("approval record expired or not verifiable")
    return valid, warnings


def preflight_valid(preflight: GateSource) -> tuple[bool, List[str]]:
    warnings: List[str] = []
    exp = parse_time_maybe(preflight.key_fields.get("expires_at"))
    if exp is None:
        warnings.append("preflight expiration missing/unreadable")
        not_expired = False
    else:
        not_expired = datetime.now() <= exp
    valid = (
        preflight.exists
        and preflight.key_fields.get("preflight_passed") is True
        and preflight.key_fields.get("ready_for_manual_shadow_approval") is True
        and preflight.key_fields.get("implementation_audit_passed") is True
        and preflight.key_fields.get("native_log_verified") is True
        and preflight.key_fields.get("runtime_plan_created") is True
        and preflight.key_fields.get("shadow_start_allowed") is False
        and preflight.key_fields.get("active_paper_allowed") is False
        and preflight.key_fields.get("live_allowed") is False
        and not_expired
    )
    if not not_expired:
        warnings.append("preflight expired or not verifiable")
    return valid, warnings


def inspect_runtime_engine(adapter_path: Optional[str]) -> tuple[bool, List[RuntimeEngineRequirement], List[str]]:
    warnings: List[str] = []
    requirements: List[RuntimeEngineRequirement] = []

    def add(rid: str, required: bool, satisfied: bool, reason: str) -> None:
        requirements.append(RuntimeEngineRequirement(rid, required, satisfied, reason))

    if not adapter_path or not Path(str(adapter_path)).exists():
        add("adapter_file_exists", True, False, "adapter file missing")
        return False, requirements, ["adapter path missing"]

    text = Path(str(adapter_path)).read_text(encoding="utf-8", errors="replace")
    add("adapter_file_exists", True, True, "adapter file exists")
    add("self_test_mode_exists", True, "--self_test" in text, "adapter supports self-test")

    runtime_markers = ["--shadow_runtime", "--run_shadow", "shadow_runtime_loop", "poll_candles", "run_forever", "heartbeat", "ret60_shadow_native_events.csv"]
    runtime_hits = [m for m in runtime_markers if m in text]
    has_runtime = len(runtime_hits) >= 3
    add("real_shadow_runtime_entrypoint", True, has_runtime, "adapter must expose real shadow runtime entrypoint, not only self-test")
    add("heartbeat_writer", True, "heartbeat" in text and "json" in text.lower(), "runtime should write heartbeat JSON")
    add("native_runtime_log_writer", True, "ret60_shadow_native_events.csv" in text or "expected_log_csv" in text, "runtime should write expected native log path")
    add("closed_trade_writer", True, "closed_trades" in text, "runtime should write closed trades file")

    if not has_runtime:
        warnings.append("adapter currently appears to be self-test/core-functions only; real shadow runtime engine is not implemented")
    return has_runtime, requirements, warnings


def build_checks(sources: List[GateSource], approval_ok: bool, preflight_ok: bool, runtime_engine_ok: bool, runtime_requirements: List[RuntimeEngineRequirement]) -> List[StartGateCheck]:
    checks: List[StartGateCheck] = []
    approval = src(sources, "manual_approval")
    preflight = src(sources, "preflight")

    def add(cid: str, category: str, required: bool, passed: bool, reason: str, evidence: str = "") -> None:
        checks.append(StartGateCheck(cid, category, required, bool(passed), "PASS" if passed else "FAIL", reason, evidence))

    add("approval_record_exists", "approval", True, approval.exists, "manual approval record must exist", str(approval.path))
    add("approval_valid", "approval", True, approval_ok, "manual approval must be granted, unexpired, and reference-only", json.dumps(approval.key_fields, ensure_ascii=False, default=str))
    add("preflight_state_exists", "preflight", True, preflight.exists, "preflight state must exist", str(preflight.path))
    add("preflight_valid", "preflight", True, preflight_ok, "preflight must be passed and unexpired", json.dumps(preflight.key_fields, ensure_ascii=False, default=str))
    add("adapter_file_exists", "runtime", True, bool(preflight.key_fields.get("adapter_path") and Path(str(preflight.key_fields.get("adapter_path"))).exists()), "adapter file must exist", str(preflight.key_fields.get("adapter_path")))
    add("active_paper_blocked", "safety", True, approval.key_fields.get("active_paper_allowed") is False and preflight.key_fields.get("active_paper_allowed") is False, "active paper must remain blocked")
    add("live_blocked", "safety", True, approval.key_fields.get("live_allowed") is False and preflight.key_fields.get("live_allowed") is False, "live must remain blocked")
    add("runtime_engine_available", "runtime", True, runtime_engine_ok, "real shadow runtime engine must exist before start reference can be allowed")
    for r in runtime_requirements:
        add(r.requirement_id, "runtime_requirement", r.required, r.satisfied, r.reason)
    return checks


def synthesize_decision(sources: List[GateSource], checks: List[StartGateCheck], requirements: List[RuntimeEngineRequirement], approval_ok: bool, preflight_ok: bool, runtime_engine_ok: bool, warnings: List[str]) -> ShadowStartDecision:
    req = [c for c in checks if c.required_for_start_reference]
    passed = [c for c in req if c.passed]
    blockers = [f"{c.check_id}: {c.reason}" for c in req if not c.passed]
    reasons: List[str] = []

    all_required = len(req) == len(passed)
    if all_required:
        status = "RET60_SHADOW_START_REFERENCE_READY_NOT_EXECUTED"
        start_ref = True
        next_action = "GENERATE_SHADOW_RUNTIME_START_COMMAND_OR_KEEP_SUPERVISED"
        reasons.append("all start gate checks passed; this module still did not execute runtime")
    elif approval_ok and preflight_ok and not runtime_engine_ok:
        status = "RET60_SHADOW_START_BLOCKED_RUNTIME_ENGINE_NOT_IMPLEMENTED"
        start_ref = False
        next_action = "BUILD_RET60_SHADOW_RUNTIME_ENGINE_THEN_AUDIT_AND_PREFLIGHT"
        reasons.append("approval and preflight are valid, but adapter does not yet expose a real shadow runtime engine")
    else:
        status = "RET60_SHADOW_START_BLOCKED_GATE_FAILURE"
        start_ref = False
        next_action = "REPAIR_FAILED_SHADOW_START_GATES"

    return ShadowStartDecision(
        candidate=DEFAULT_CANDIDATE,
        decision_status=status,
        start_reference_allowed=start_ref,
        shadow_runtime_start_executed=False,
        shadow_runtime_engine_available=runtime_engine_ok,
        approval_valid=approval_ok,
        preflight_valid=preflight_ok,
        active_paper_allowed=False,
        live_allowed=False,
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
    )


def records_df(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def write_outputs(out_dir: Path, state: ShadowStartGateState, decision: ShadowStartDecision, sources: List[GateSource], checks: List[StartGateCheck], requirements: List[RuntimeEngineRequirement]) -> None:
    payload = {
        "state": asdict(state),
        "decision": asdict(decision),
        "sources": [asdict(s) for s in sources],
        "checks": [asdict(c) for c in checks],
        "runtime_engine_requirements": [asdict(r) for r in requirements],
    }
    write_json(out_dir / "ret60_shadow_start_gate_state.json", payload)
    write_json(out_dir / "ret60_shadow_start_gate_decision.json", asdict(decision))
    write_json(out_dir / "ret60_shadow_runtime_engine_requirements.json", {"requirements": [asdict(r) for r in requirements]})
    records_df(checks).to_csv(out_dir / "ret60_shadow_start_gate_checks.csv", index=False)
    records_df(requirements).to_csv(out_dir / "ret60_shadow_runtime_engine_requirements.csv", index=False)
    records_df(sources).to_csv(out_dir / "ret60_shadow_start_gate_sources.csv", index=False)

    if decision.start_reference_allowed:
        cmd = "# REFERENCE ONLY - this gate did not execute anything\n# Real runtime command must be supervised and manually executed after this gate.\n"
    else:
        cmd = "# BLOCKED - no start command generated\n# Reason: " + decision.decision_status + "\n# Next: " + decision.next_action + "\n"
    write_text(out_dir / "ret60_shadow_start_COMMAND_REFERENCE_ONLY.ps1", cmd)

    md = f"""# Ret60 Shadow Start Gate

Decision: **{decision.decision_status}**

- Approval valid: `{decision.approval_valid}`
- Preflight valid: `{decision.preflight_valid}`
- Runtime engine available: `{decision.shadow_runtime_engine_available}`
- Start reference allowed: `{decision.start_reference_allowed}`
- Runtime executed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Next action

`{decision.next_action}`

## Blockers

```text
{chr(10).join(decision.blockers) if decision.blockers else 'none'}
```

## Interpretation

Approval and preflight can be valid while start is still blocked if the adapter has only self-test/core functions and no real shadow runtime loop.
"""
    write_text(out_dir / "ret60_shadow_start_gate_report.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ret60 shadow start gate")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--approval_record", default=None)
    p.add_argument("--preflight_state", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_shadow_start_gate"
    out_dir = out_root / f"ret60_shadow_start_gate_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources(workspace, args.approval_record, args.preflight_state)
    approval = src(sources, "manual_approval")
    preflight = src(sources, "preflight")
    approval_ok, approval_warnings = approval_valid(approval)
    preflight_ok, preflight_warnings = preflight_valid(preflight)
    adapter_path = preflight.key_fields.get("adapter_path")
    runtime_ok, requirements, runtime_warnings = inspect_runtime_engine(str(adapter_path) if adapter_path else None)
    warnings: List[str] = []
    for s in sources:
        warnings.extend([f"{s.name}: {w}" for w in s.warnings])
    warnings.extend(approval_warnings)
    warnings.extend(preflight_warnings)
    warnings.extend(runtime_warnings)

    checks = build_checks(sources, approval_ok, preflight_ok, runtime_ok, requirements)
    decision = synthesize_decision(sources, checks, requirements, approval_ok, preflight_ok, runtime_ok, warnings)
    req = [c for c in checks if c.required_for_start_reference]
    passed = [c for c in req if c.passed]
    sat = [r for r in requirements if r.required and r.satisfied]
    reqs = [r for r in requirements if r.required]

    state = ShadowStartGateState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=DEFAULT_CANDIDATE,
        output_dir=str(out_dir),
        approval_record_path=approval.path,
        preflight_state_path=preflight.path,
        adapter_path=str(adapter_path) if adapter_path else None,
        decision_status=decision.decision_status,
        checks_passed=len(passed),
        checks_required=len(req),
        requirements_satisfied=len(sat),
        requirements_total=len(reqs),
        start_reference_allowed=decision.start_reference_allowed,
        shadow_runtime_start_executed=False,
        shadow_start_allowed=decision.start_reference_allowed,
        active_paper_allowed=False,
        live_allowed=False,
        next_action=decision.next_action,
        reasons=decision.reasons,
        blockers=decision.blockers,
        warnings=decision.warnings,
        hard_rules=[
            "Shadow start gate never starts runtime by itself.",
            "Shadow start gate never starts active paper/live.",
            "Shadow start gate never mutates active config.",
            "Shadow start gate never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "A valid manual approval record is necessary but not sufficient; a real runtime engine must exist.",
            "Live remains blocked.",
        ],
    )

    write_outputs(out_dir, state, decision, sources, checks, requirements)

    print("EDGE FACTORY RET60 SHADOW START GATE v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {DEFAULT_CANDIDATE}")
    print(f"output_dir: {out_dir}")
    print(f"approval_record: {approval.path}")
    print(f"preflight_state: {preflight.path}")
    print(f"adapter_path: {adapter_path}")
    print(f"decision_status: {state.decision_status}")
    print(f"approval_valid: {approval_ok}")
    print(f"preflight_valid: {preflight_ok}")
    print(f"runtime_engine_available: {runtime_ok}")
    print(f"start_reference_allowed: {state.start_reference_allowed}")
    print("shadow_runtime_start_executed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print(f"checks: {state.checks_passed}/{state.checks_required}")
    print(f"runtime_requirements: {state.requirements_satisfied}/{state.requirements_total}")
    print("")
    print("RUNTIME REQUIREMENTS")
    print("-" * 100)
    for r in requirements:
        print(f"{r.requirement_id:36s} required={r.required} satisfied={r.satisfied} reason={r.reason}")
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
    print("This module did not start shadow/active paper/live, did not run logger runtime, and did not mutate active config.")
    print("")
    print(f"Report : {out_dir / 'ret60_shadow_start_gate_report.md'}")
    print(f"State  : {out_dir / 'ret60_shadow_start_gate_state.json'}")
    print(f"Decision: {out_dir / 'ret60_shadow_start_gate_decision.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
