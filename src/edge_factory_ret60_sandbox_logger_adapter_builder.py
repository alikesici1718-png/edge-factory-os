#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 SANDBOX LOGGER ADAPTER BUILDER v1
====================================================

Purpose
-------
Create a sandbox-only ret60 shadow logger adapter implementation file from the approved
ret60 sandbox logger blueprint.

This is the step after:
    edge_factory_ret60_sandbox_logger_blueprint.py

Important distinction
---------------------
This builder writes a sandbox-only adapter file, but DOES NOT run it.
The produced adapter is still blocked from shadow runtime until:
    1. implementation audit passes
    2. sandbox preflight passes
    3. manual shadow approval is recorded

It DOES NOT:
    - start paper
    - start live
    - run the logger
    - connect to private exchange APIs
    - send orders
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - read latest ret60 sandbox logger blueprint
    - verify blueprint gates are ready
    - write a sandbox-only adapter source file
    - write adapter manifest and implementation gate packet
    - write reference-only self-test command

Run:
    python "C:\Users\alike\edge_factory_ret60_sandbox_logger_adapter_builder.py"

Core rule
---------
Adapter generation is not runtime. Shadow start remains blocked.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"


@dataclass
class BlueprintLoad:
    blueprint_dir: Optional[str]
    blueprint_state_path: Optional[str]
    signal_contract_path: Optional[str]
    native_logging_contract_path: Optional[str]
    blueprint_status: str
    blueprint_ready: bool
    implementation_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    signal_contract: Dict[str, Any]
    warnings: List[str]


@dataclass
class AdapterGate:
    gate_id: str
    category: str
    required_for_adapter_write: bool
    required_for_future_shadow_start: bool
    passed: bool
    status: str
    reason: str


@dataclass
class AdapterBuilderState:
    generated_at: str
    workspace: str
    candidate: str
    output_dir: str
    adapter_path: Optional[str]
    manifest_path: Optional[str]
    builder_status: str
    adapter_written: bool
    implementation_audit_required: bool
    preflight_required: bool
    manual_approval_required: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    gates_passed_for_write: int
    gates_required_for_write: int
    gates_passed_for_shadow_start: int
    gates_required_for_shadow_start: int
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


def latest_blueprint_dir(workspace: Path) -> Optional[Path]:
    return latest_child_dir(workspace / "edge_factory_ret60_sandbox_logger_blueprint", "ret60_logger_blueprint_")


def load_blueprint(workspace: Path, explicit_dir: Optional[str]) -> BlueprintLoad:
    warnings: List[str] = []
    d = Path(explicit_dir) if explicit_dir else latest_blueprint_dir(workspace)
    if not d or not d.exists():
        return BlueprintLoad(None, None, None, None, "MISSING", False, False, False, False, False, {}, ["blueprint dir missing"])

    state_path = d / "ret60_sandbox_logger_blueprint_state.json"
    contract_path = d / "ret60_signal_contract.json"
    native_path = d / "ret60_native_logging_contract.json"
    obj = read_json_optional(state_path)
    contract_obj = read_json_optional(contract_path)
    state = obj.get("state", {}) if isinstance(obj.get("state"), dict) else {}
    signal_contract = contract_obj.get("signal_contract", {}) if isinstance(contract_obj.get("signal_contract"), dict) else {}

    if not signal_contract:
        signal_contract = obj.get("signal_contract", {}) if isinstance(obj.get("signal_contract"), dict) else {}
    if not signal_contract:
        warnings.append("signal contract missing or unreadable")

    return BlueprintLoad(
        blueprint_dir=str(d),
        blueprint_state_path=str(state_path) if state_path.exists() else None,
        signal_contract_path=str(contract_path) if contract_path.exists() else None,
        native_logging_contract_path=str(native_path) if native_path.exists() else None,
        blueprint_status=str(state.get("blueprint_status") or "UNKNOWN"),
        blueprint_ready=bool(state.get("blueprint_ready", False)),
        implementation_allowed=bool(state.get("sandbox_logger_implementation_allowed", False)),
        shadow_start_allowed=bool(state.get("shadow_start_allowed", False)),
        active_paper_allowed=bool(state.get("active_paper_allowed", False)),
        live_allowed=bool(state.get("live_allowed", False)),
        signal_contract=signal_contract,
        warnings=warnings,
    )


def build_gates(bp: BlueprintLoad) -> List[AdapterGate]:
    gates: List[AdapterGate] = []

    def add(gate_id: str, category: str, write_req: bool, shadow_req: bool, passed: bool, reason: str) -> None:
        gates.append(AdapterGate(
            gate_id=gate_id,
            category=category,
            required_for_adapter_write=write_req,
            required_for_future_shadow_start=shadow_req,
            passed=bool(passed),
            status="PASS" if passed else "FAIL",
            reason=reason,
        ))

    c = bp.signal_contract
    add("blueprint_exists", "artifact", True, True, bool(bp.blueprint_dir), "blueprint directory must exist")
    add("blueprint_ready", "artifact", True, True, bp.blueprint_ready, "blueprint must be ready")
    add("implementation_allowed_by_blueprint", "approval", True, True, bp.implementation_allowed, "blueprint must allow adapter implementation")
    add("signal_contract_exists", "signal", True, True, bool(c), "signal contract must exist")
    add("candidate_key", "signal", True, True, c.get("candidate_key") == DEFAULT_CANDIDATE, "candidate key must match ret60_reversal_short")
    add("side_short", "signal", True, True, str(c.get("side", "")).lower() == "short", "side must be short")
    add("ret60_rule_defined", "signal", True, True, "signal_ret60_bps" in str(c.get("ret60_rule", "")), "ret60 rule must be defined")
    add("hour_defined", "signal", True, True, isinstance(c.get("hour_utc"), int), "hour_utc must be defined")
    add("delay_defined", "signal", True, True, isinstance(c.get("delay_minutes"), int), "delay must be defined")
    add("hold_defined", "signal", True, True, isinstance(c.get("hold_minutes"), int) and int(c.get("hold_minutes")) > 0, "hold must be defined")
    add("extra_defined", "signal", True, True, isinstance(c.get("extra_slip_bps"), int), "extra_slip_bps must be defined")
    add("native_logging_contract_exists", "logging", True, True, bool(bp.native_logging_contract_path), "native logging contract must exist")
    add("live_blocked", "safety", True, True, not bp.live_allowed, "live must be blocked")
    add("active_paper_blocked", "safety", True, True, not bp.active_paper_allowed, "active paper must be blocked")
    add("shadow_start_blocked_now", "safety", True, False, not bp.shadow_start_allowed, "shadow start must still be blocked at adapter build stage")
    add("implementation_audit_not_done", "audit", False, True, False, "future shadow start requires implementation audit")
    add("sandbox_preflight_not_done", "preflight", False, True, False, "future shadow start requires sandbox preflight")
    add("manual_shadow_approval_not_done", "approval", False, True, False, "future shadow start requires manual approval")
    return gates


def adapter_source(contract: Dict[str, Any]) -> str:
    candidate = contract.get("candidate_key", DEFAULT_CANDIDATE)
    version = contract.get("signal_version", "ret60_reversal_short_blueprint_v1")
    side = contract.get("side", "short")
    hour = int(contract.get("hour_utc", 8))
    m = int(contract.get("m_param", 75))
    delay = int(contract.get("delay_minutes", 1))
    hold = int(contract.get("hold_minutes", 720))
    extra = int(contract.get("extra_slip_bps", 0))
    rule = str(contract.get("ret60_rule", f"signal_ret60_bps >= {m}"))

    return f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
RET60 SANDBOX SHADOW LOGGER ADAPTER - GENERATED BLUEPRINT IMPLEMENTATION
========================================================================

Generated by: edge_factory_ret60_sandbox_logger_adapter_builder.py
Candidate   : {candidate}
Version     : {version}

This file is sandbox-only. It contains core signal/return/logging functions and a self-test.
It is NOT approved to run shadow paper until implementation audit, sandbox preflight, and
manual approval pass.

Hard bans:
    - no live trading
    - no private exchange API
    - no order placement
    - no MASTER_UPPER_SYSTEM edits
    - no position sizing contract edits
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


CANDIDATE_KEY = {candidate!r}
SIGNAL_VERSION = {version!r}
SIDE = {side!r}
HOUR_UTC = {hour}
M_PARAM = {m}
RET60_RULE = {rule!r}
DELAY_MINUTES = {delay}
HOLD_MINUTES = {hold}
EXTRA_SLIP_BPS = {extra}

SANDBOX_ONLY = True
LIVE_ALLOWED = False
ACTIVE_PAPER_ALLOWED = False
SHADOW_START_ALLOWED_BY_THIS_FILE = False
PRIVATE_EXCHANGE_API_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False

REQUIRED_LOG_FIELDS = [
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
class SignalDecision:
    candidate_key: str
    signal_version: str
    symbol: str
    side: str
    signal_time_utc: str
    hour_utc: int
    signal_ret60_bps: float
    ret60_rule_passed: bool
    enter_short: bool
    delay_minutes: int
    planned_entry_time_utc: str
    hold_minutes: int
    planned_exit_time_utc: str
    reason: str


def parse_utc(ts: Any) -> datetime:
    if isinstance(ts, datetime):
        dt = ts
    else:
        s = str(ts).strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def compute_signal_ret60_bps(current_ref_price: float, price_60m_ago: float) -> float:
    if price_60m_ago <= 0:
        raise ValueError("price_60m_ago must be positive")
    if current_ref_price <= 0:
        raise ValueError("current_ref_price must be positive")
    return (current_ref_price / price_60m_ago - 1.0) * 10000.0


def ret60_rule_pass(signal_ret60_bps: float) -> bool:
    # Resolved by m-semantic resolver: signal_ret60_bps >= M_PARAM
    return float(signal_ret60_bps) >= float(M_PARAM)


def decide(symbol: str, signal_time_utc: Any, signal_ret60_bps: float) -> SignalDecision:
    signal_time = parse_utc(signal_time_utc)
    hour_ok = int(signal_time.hour) == int(HOUR_UTC)
    ret_ok = ret60_rule_pass(signal_ret60_bps)
    enter = bool(hour_ok and ret_ok)
    entry_time = signal_time + timedelta(minutes=DELAY_MINUTES)
    exit_time = entry_time + timedelta(minutes=HOLD_MINUTES)
    if not hour_ok:
        reason = f"BLOCK_HOUR hour={{signal_time.hour}} required={{HOUR_UTC}}"
    elif not ret_ok:
        reason = f"BLOCK_RET60 signal_ret60_bps={{signal_ret60_bps}} required>={{M_PARAM}}"
    else:
        reason = "ENTER_SHORT_RULE_PASS"
    return SignalDecision(
        candidate_key=CANDIDATE_KEY,
        signal_version=SIGNAL_VERSION,
        symbol=str(symbol),
        side=SIDE,
        signal_time_utc=iso_utc(signal_time),
        hour_utc=int(signal_time.hour),
        signal_ret60_bps=float(signal_ret60_bps),
        ret60_rule_passed=bool(ret_ok),
        enter_short=enter,
        delay_minutes=DELAY_MINUTES,
        planned_entry_time_utc=iso_utc(entry_time),
        hold_minutes=HOLD_MINUTES,
        planned_exit_time_utc=iso_utc(exit_time),
        reason=reason,
    )


def short_gross_return_bps(entry_price: float, exit_price: float) -> float:
    if entry_price <= 0 or exit_price <= 0:
        raise ValueError("entry_price and exit_price must be positive")
    # Short return in bps. Equivalent to price falling from entry to exit.
    return (entry_price / exit_price - 1.0) * 10000.0


def net_return_bps(gross_return_bps: float, fee_bps: float, spread_bps: float, slippage_bps: float, extra_slip_bps: float = EXTRA_SLIP_BPS) -> float:
    return float(gross_return_bps) - float(fee_bps) - float(spread_bps) - float(slippage_bps) - float(extra_slip_bps)


def pnl_usdt(return_bps: float, notional_usdt: float) -> float:
    return float(notional_usdt) * float(return_bps) / 10000.0


def build_log_row(
    event_id: str,
    decision: SignalDecision,
    actual_paper_entry_time_utc: Any,
    actual_paper_exit_time_utc: Any,
    entry_reference_price: float,
    exit_reference_price: float,
    notional_usdt: float,
    fee_bps_assumption: float,
    spread_bps_at_signal: float,
    slippage_bps_assumption: float,
    source_candle_basis: str,
    feature_calculation_version: str = "ret60_bps_v1",
    logger_version: str = "ret60_sandbox_shadow_logger_v1",
    runtime_mode: str = "self_test_or_shadow_sandbox",
) -> Dict[str, Any]:
    if runtime_mode.lower() == "live":
        raise RuntimeError("LIVE runtime_mode is forbidden in sandbox adapter")
    gross_bps = short_gross_return_bps(entry_reference_price, exit_reference_price)
    net_bps = net_return_bps(gross_bps, fee_bps_assumption, spread_bps_at_signal, slippage_bps_assumption, EXTRA_SLIP_BPS)
    row = {{
        "event_id": str(event_id),
        "candidate_key": CANDIDATE_KEY,
        "signal_version": SIGNAL_VERSION,
        "symbol": decision.symbol,
        "side": SIDE,
        "signal_time_utc": decision.signal_time_utc,
        "hour_utc": decision.hour_utc,
        "signal_ret60_bps": decision.signal_ret60_bps,
        "ret60_rule_passed": decision.ret60_rule_passed,
        "delay_minutes": DELAY_MINUTES,
        "planned_entry_time_utc": decision.planned_entry_time_utc,
        "actual_paper_entry_time_utc": iso_utc(parse_utc(actual_paper_entry_time_utc)),
        "entry_reference_price": float(entry_reference_price),
        "hold_minutes": HOLD_MINUTES,
        "planned_exit_time_utc": decision.planned_exit_time_utc,
        "actual_paper_exit_time_utc": iso_utc(parse_utc(actual_paper_exit_time_utc)),
        "exit_reference_price": float(exit_reference_price),
        "gross_return_bps_native": float(gross_bps),
        "fee_bps_assumption": float(fee_bps_assumption),
        "spread_bps_at_signal": float(spread_bps_at_signal),
        "slippage_bps_assumption": float(slippage_bps_assumption),
        "extra_slip_bps": float(EXTRA_SLIP_BPS),
        "net_return_bps_native": float(net_bps),
        "gross_pnl_usdt": float(pnl_usdt(gross_bps, notional_usdt)),
        "net_pnl_usdt": float(pnl_usdt(net_bps, notional_usdt)),
        "notional_usdt": float(notional_usdt),
        "source_candle_basis": str(source_candle_basis),
        "feature_calculation_version": str(feature_calculation_version),
        "logger_version": str(logger_version),
        "runtime_mode": str(runtime_mode),
    }}
    missing = [f for f in REQUIRED_LOG_FIELDS if f not in row]
    if missing:
        raise RuntimeError(f"missing required log fields: {{missing}}")
    return row


def append_csv(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_LOG_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({{k: row.get(k) for k in REQUIRED_LOG_FIELDS}})


def self_test(out_dir: Path) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    signal_time = datetime(2026, 5, 10, HOUR_UTC, 0, tzinfo=timezone.utc)
    decision = decide("BTC-USDT-SWAP", signal_time, M_PARAM + 10.0)
    assert decision.enter_short is True, decision
    entry_time = parse_utc(decision.planned_entry_time_utc)
    exit_time = parse_utc(decision.planned_exit_time_utc)
    assert (entry_time - signal_time).total_seconds() == DELAY_MINUTES * 60
    assert (exit_time - entry_time).total_seconds() == HOLD_MINUTES * 60
    row = build_log_row(
        event_id="self_test_001",
        decision=decision,
        actual_paper_entry_time_utc=entry_time,
        actual_paper_exit_time_utc=exit_time,
        entry_reference_price=100.0,
        exit_reference_price=99.0,
        notional_usdt=50.0,
        fee_bps_assumption=5.0,
        spread_bps_at_signal=2.0,
        slippage_bps_assumption=3.0,
        source_candle_basis="synthetic_self_test",
        runtime_mode="self_test",
    )
    assert row["net_return_bps_native"] > 0
    csv_path = out_dir / "ret60_sandbox_adapter_self_test_log.csv"
    append_csv(csv_path, row)
    result = {{
        "ok": True,
        "csv_path": str(csv_path),
        "decision": asdict(decision),
        "row": row,
        "live_allowed": LIVE_ALLOWED,
        "active_paper_allowed": ACTIVE_PAPER_ALLOWED,
        "shadow_start_allowed_by_this_file": SHADOW_START_ALLOWED_BY_THIS_FILE,
    }}
    (out_dir / "ret60_sandbox_adapter_self_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ret60 sandbox adapter self-test only")
    p.add_argument("--self_test", action="store_true")
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if not args.self_test:
        print("RET60 sandbox adapter generated. Runtime is blocked. Use --self_test only until audit/preflight/manual approval.")
        print("live_allowed: False")
        print("active_paper_allowed: False")
        print("shadow_start_allowed_by_this_file: False")
        return 0
    out_dir = Path(args.out_dir) if args.out_dir else Path.cwd() / "ret60_sandbox_adapter_self_test"
    result = self_test(out_dir)
    print("RET60 SANDBOX ADAPTER SELF TEST")
    print("=" * 80)
    print(f"ok: {{result['ok']}}")
    print(f"csv_path: {{result['csv_path']}}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("shadow_start_allowed_by_this_file: False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def records_df(items: List[Any]) -> pd.DataFrame:
    rows = []
    for x in items:
        d = asdict(x)
        for k, v in list(d.items()):
            if isinstance(v, list):
                d[k] = " | ".join(str(i) for i in v)
        rows.append(d)
    return pd.DataFrame(rows)


def write_outputs(workspace: Path, out_dir: Path, state: AdapterBuilderState, bp: BlueprintLoad, gates: List[AdapterGate], adapter_code: Optional[str]) -> None:
    persistent = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes" / DEFAULT_CANDIDATE / "logger_adapter"
    persistent.mkdir(parents=True, exist_ok=True)

    if adapter_code and state.adapter_path:
        write_text(Path(state.adapter_path), adapter_code)
        write_text(persistent / "ret60_sandbox_shadow_logger.py", adapter_code)

    manifest = {
        "state": asdict(state),
        "blueprint": asdict(bp),
        "gates": [asdict(g) for g in gates],
        "adapter_path": state.adapter_path,
        "permissions": {
            "adapter_written": state.adapter_written,
            "shadow_start_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "mutates_active_config": False,
            "changes_sizing_contract": False,
        },
    }
    for d in [out_dir, persistent]:
        write_json(d / "ret60_sandbox_logger_adapter_manifest.json", manifest)
        records_df(gates).to_csv(d / "ret60_sandbox_logger_adapter_gates.csv", index=False)

    reference = f'''# REFERENCE ONLY - self-test only, not runtime
python "{state.adapter_path}" --self_test --out_dir "{out_dir / 'adapter_self_test'}"
'''
    for d in [out_dir, persistent]:
        write_text(d / "ret60_adapter_self_test_REFERENCE_ONLY.ps1", reference)

    md = f"""# Ret60 Sandbox Logger Adapter Builder

Status: **{state.builder_status}**

- Adapter written: `{state.adapter_written}`
- Adapter path: `{state.adapter_path}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Next action

`{state.next_action}`

## Important

The adapter is generated but not approved for runtime. The only safe command is the reference self-test command.
"""
    for d in [out_dir, persistent]:
        write_text(d / "ret60_sandbox_logger_adapter_builder_report.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build ret60 sandbox logger adapter file")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    p.add_argument("--blueprint_dir", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    candidate = safe_key(args.candidate)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_sandbox_logger_adapter_builder"
    out_dir = out_root / f"ret60_adapter_builder_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    bp = load_blueprint(workspace, args.blueprint_dir)
    gates = build_gates(bp)
    req_write = [g for g in gates if g.required_for_adapter_write]
    pass_write = [g for g in req_write if g.passed]
    req_shadow = [g for g in gates if g.required_for_future_shadow_start]
    pass_shadow = [g for g in req_shadow if g.passed]

    blockers: List[str] = []
    reasons: List[str] = []
    warnings: List[str] = list(bp.warnings)
    can_write = len(pass_write) == len(req_write)

    adapter_path = out_dir / "ret60_sandbox_shadow_logger.py"
    adapter_code = None
    if can_write:
        adapter_code = adapter_source(bp.signal_contract)
        status = "RET60_SANDBOX_LOGGER_ADAPTER_WRITTEN_NOT_APPROVED_TO_RUN"
        next_action = "RUN_RET60_SANDBOX_LOGGER_IMPLEMENTATION_AUDIT"
        reasons.append("all adapter-write gates passed")
        reasons.append("sandbox-only adapter source was generated from blueprint")
    else:
        status = "RET60_ADAPTER_BUILD_BLOCKED"
        next_action = "REPAIR_FAILED_ADAPTER_WRITE_GATES"
        blockers.extend([f"{g.gate_id}: {g.reason}" for g in req_write if not g.passed])
        adapter_path = None

    shadow_missing = [g.gate_id for g in req_shadow if not g.passed]
    if shadow_missing:
        warnings.append("future shadow start remains blocked by: " + ", ".join(shadow_missing))

    state = AdapterBuilderState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=candidate,
        output_dir=str(out_dir),
        adapter_path=str(adapter_path) if adapter_path else None,
        manifest_path=str(out_dir / "ret60_sandbox_logger_adapter_manifest.json"),
        builder_status=status,
        adapter_written=can_write,
        implementation_audit_required=True,
        preflight_required=True,
        manual_approval_required=True,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        gates_passed_for_write=len(pass_write),
        gates_required_for_write=len(req_write),
        gates_passed_for_shadow_start=len(pass_shadow),
        gates_required_for_shadow_start=len(req_shadow),
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        hard_rules=[
            "Adapter builder never starts paper/live.",
            "Adapter builder never runs the generated adapter except user-triggered future self-test.",
            "Generated adapter forbids live/private API/order placement.",
            "Adapter builder never mutates active config.",
            "Adapter builder never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Shadow start remains blocked until audit, preflight, and manual approval.",
        ],
    )

    write_outputs(workspace, out_dir, state, bp, gates, adapter_code)

    print("EDGE FACTORY RET60 SANDBOX LOGGER ADAPTER BUILDER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"builder_status: {state.builder_status}")
    print(f"adapter_written: {state.adapter_written}")
    print(f"adapter_path: {state.adapter_path}")
    print(f"write_gates: {state.gates_passed_for_write}/{state.gates_required_for_write}")
    print(f"future_shadow_gates: {state.gates_passed_for_shadow_start}/{state.gates_required_for_shadow_start}")
    print("implementation_audit_required: True")
    print("preflight_required: True")
    print("manual_approval_required: True")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
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
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'ret60_sandbox_logger_adapter_builder_report.md'}")
    print(f"Manifest: {out_dir / 'ret60_sandbox_logger_adapter_manifest.json'}")
    print(f"Adapter : {state.adapter_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
