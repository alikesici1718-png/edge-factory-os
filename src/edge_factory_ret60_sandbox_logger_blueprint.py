#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 SANDBOX LOGGER BLUEPRINT v1
==============================================

Purpose
-------
Build a sandbox-only logger blueprint for ret60_reversal_short after the semantic
contract chain reached blueprint readiness.

Upstream evidence expected:
    - ret60 rule artifact parser v2
    - ret60 semantic contract auditor
    - ret60 m-semantic resolver

Current resolved selected rule, if latest artifacts agree:
    candidate       = ret60_reversal_short
    side            = short
    hour_utc        = 8
    signal rule     = signal_ret60_bps >= 75
    delay           = 1 minute/bar, confirmed as timestamp delta in semantic audit
    hold            = 720 minutes, confirmed as timestamp delta in semantic audit
    extra_slip_bps  = 0

This module DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - read latest parser v2, semantic audit, and m-semantic resolver outputs
    - synthesize a sandbox-only logger blueprint
    - define exact signal contract and native logging contract
    - define required preflight gates before any future sandbox runtime
    - write reference-only interface / pseudocode files
    - mark active paper/live as blocked

Run:
    python "C:\Users\alike\edge_factory_ret60_sandbox_logger_blueprint.py"

Core rule
---------
Blueprint is not runtime. It only permits writing a sandbox-only logger adapter later.
Shadow start still requires implementation audit, preflight, and manual approval.
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
class UpstreamArtifact:
    name: str
    path: Optional[str]
    exists: bool
    status: str
    key_fields: Dict[str, Any]
    warnings: List[str]


@dataclass
class Ret60SignalContract:
    candidate_key: str
    signal_version: str
    side: str
    selected_variant_key: str
    hour_utc: int
    m_param: int
    ret60_rule: str
    delay_minutes: int
    hold_minutes: int
    extra_slip_bps: int
    cost_model: str
    entry_reference: str
    exit_reference: str
    required_input_fields: List[str]
    required_calculations: List[str]
    forbidden_runtime_actions: List[str]


@dataclass
class BlueprintGate:
    gate_id: str
    category: str
    required_for_blueprint: bool
    required_for_future_shadow_start: bool
    passed: bool
    status: str
    reason: str


@dataclass
class BlueprintState:
    generated_at: str
    workspace: str
    candidate: str
    blueprint_status: str
    selected_variant_key: Optional[str]
    blueprint_ready: bool
    sandbox_logger_implementation_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    gates_passed_for_blueprint: int
    gates_required_for_blueprint: int
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


def latest_parser_v2_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_rule_artifact_parser_v2", "ret60_rule_artifacts_v2_")
    if not d:
        return None
    p = d / "ret60_rule_artifact_parser_v2_state.json"
    return p if p.exists() else None


def latest_semantic_audit_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_semantic_contract_auditor", "ret60_semantic_audit_")
    if not d:
        return None
    p = d / "ret60_semantic_contract_audit_state.json"
    return p if p.exists() else None


def latest_m_resolver_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_m_semantic_resolver", "ret60_m_semantics_")
    if not d:
        return None
    p = d / "ret60_m_semantic_resolver_state.json"
    return p if p.exists() else None


def artifact_status(name: str, path: Optional[Path], obj: Dict[str, Any]) -> UpstreamArtifact:
    warnings: List[str] = []
    status = "MISSING"
    key_fields: Dict[str, Any] = {}

    if not path or not path.exists():
        return UpstreamArtifact(name, str(path) if path else None, False, status, key_fields, ["artifact missing"])

    if name == "parser_v2":
        state = obj.get("state", {}) if isinstance(obj.get("state"), dict) else {}
        contract = obj.get("contract", {}) if isinstance(obj.get("contract"), dict) else {}
        status = str(state.get("parser_status") or state.get("contract_status") or contract.get("contract_status") or "UNKNOWN")
        key_fields = {
            "parser_status": state.get("parser_status"),
            "contract_status": contract.get("contract_status") or state.get("contract_status"),
            "selected_variant_key": contract.get("selected_variant_key") or state.get("selected_variant"),
            "selected_artifact_path": contract.get("selected_artifact_path"),
            "entry_rule_hypothesis": contract.get("entry_rule_hypothesis"),
            "exit_rule_hypothesis": contract.get("exit_rule_hypothesis"),
            "positive_variants": state.get("positive_variants"),
        }
    elif name == "semantic_audit":
        result = obj.get("semantic_audit_result", {}) if isinstance(obj.get("semantic_audit_result"), dict) else {}
        selected = obj.get("selected_contract", {}) if isinstance(obj.get("selected_contract"), dict) else {}
        status = str(result.get("audit_status") or "UNKNOWN")
        key_fields = {
            "audit_status": result.get("audit_status"),
            "confirmed_components": result.get("confirmed_components"),
            "total_components": result.get("total_components"),
            "blueprint_allowed": result.get("blueprint_allowed"),
            "selected_variant_key": selected.get("selected_variant_key") or result.get("selected_variant_key"),
        }
    elif name == "m_resolver":
        verdict = obj.get("m_semantic_verdict", {}) if isinstance(obj.get("m_semantic_verdict"), dict) else {}
        state = obj.get("state", {}) if isinstance(obj.get("state"), dict) else {}
        status = str(verdict.get("verdict_status") or state.get("verdict_status") or "UNKNOWN")
        key_fields = {
            "verdict_status": verdict.get("verdict_status") or state.get("verdict_status"),
            "selected_rule_expression": verdict.get("selected_rule_expression"),
            "selected_pass_share": verdict.get("selected_pass_share"),
            "m_semantics_confidence": verdict.get("m_semantics_confidence"),
            "blueprint_allowed": verdict.get("blueprint_allowed") or state.get("blueprint_allowed"),
            "variant_key": verdict.get("variant_key") or state.get("variant_key"),
        }
    else:
        status = "UNKNOWN"

    return UpstreamArtifact(name, str(path), True, status, key_fields, warnings)


def load_upstreams(workspace: Path, parser_state: Optional[str], semantic_state: Optional[str], m_state: Optional[str]) -> List[UpstreamArtifact]:
    p_parser = Path(parser_state) if parser_state else latest_parser_v2_state(workspace)
    p_semantic = Path(semantic_state) if semantic_state else latest_semantic_audit_state(workspace)
    p_m = Path(m_state) if m_state else latest_m_resolver_state(workspace)
    return [
        artifact_status("parser_v2", p_parser, read_json_optional(p_parser)),
        artifact_status("semantic_audit", p_semantic, read_json_optional(p_semantic)),
        artifact_status("m_resolver", p_m, read_json_optional(p_m)),
    ]


def get_field(arts: List[UpstreamArtifact], artifact_name: str, field: str, default: Any = None) -> Any:
    for a in arts:
        if a.name == artifact_name:
            return a.key_fields.get(field, default)
    return default


def build_signal_contract(candidate: str, arts: List[UpstreamArtifact]) -> Ret60SignalContract:
    variant = get_field(arts, "parser_v2", "selected_variant_key") or get_field(arts, "semantic_audit", "selected_variant_key") or get_field(arts, "m_resolver", "variant_key")
    selected_rule = get_field(arts, "m_resolver", "selected_rule_expression") or "signal_ret60_bps >= 75"

    # Parse known variant fields. Fallbacks reflect current resolved contract.
    h = 8
    m = 75
    hold = 720
    delay = 1
    extra = 0
    if isinstance(variant, str):
        import re
        mm = re.search(r"_h(\d+)_m(\d+)_hold(\d+)_delay(\d+)_extra(\d+)", variant)
        if mm:
            h = int(mm.group(1))
            m = int(mm.group(2))
            hold = int(mm.group(3))
            delay = int(mm.group(4))
            extra = int(mm.group(5))

    return Ret60SignalContract(
        candidate_key=candidate,
        signal_version="ret60_reversal_short_blueprint_v1",
        side="short",
        selected_variant_key=str(variant or f"{candidate}_h{h}_m{m}_hold{hold}_delay{delay}_extra{extra}"),
        hour_utc=h,
        m_param=m,
        ret60_rule=str(selected_rule),
        delay_minutes=delay,
        hold_minutes=hold,
        extra_slip_bps=extra,
        cost_model="Use artifact-compatible cost assumptions: cost_bps from backtest artifacts, extra_slip_bps from variant extra param; live/paper logs must record fee_bps, spread_bps, slippage_bps, and net/native bps separately.",
        entry_reference="At signal_time UTC hour == h_param, require ret60 rule; enter after delay_minutes using entry reference price from sandbox logger candle/execution simulator.",
        exit_reference="Fixed hold_minutes after entry_time; exit reference price must be recorded; no TP/SL unless future sandbox variant explicitly tests it.",
        required_input_fields=[
            "symbol",
            "event_time_utc_or_signal_time_utc",
            "hour_utc",
            "signal_ret60_bps",
            "entry_reference_price",
            "source_candle_close_or_mark_price",
            "spread_bps_at_signal",
            "fee_bps_assumption",
            "slippage_bps_assumption",
        ],
        required_calculations=[
            "Compute hour_utc from signal_time_utc if hour_utc is not directly available.",
            "Compute signal_ret60_bps from current/reference price versus 60-minute prior reference price using the same candle basis as scanner.",
            "Apply ret60_rule exactly as resolved by m-semantic resolver.",
            "Delay entry by delay_minutes after signal_time_utc.",
            "Hold exactly hold_minutes after entry_time.",
            "For short: gross_return_bps = (entry_price / exit_price - 1) * 10000, or equivalent scanner-compatible formula; store formula version.",
            "Net return must subtract explicit fee/spread/slippage assumptions and record all components separately.",
        ],
        forbidden_runtime_actions=[
            "No live orders.",
            "No edits to MASTER_UPPER_SYSTEM launcher.",
            "No edits to active position sizing contract.",
            "No inclusion in active paper portfolio before sandbox preflight and manual approval.",
            "No silent fallback to approximate ret60 feature if exact candle basis is unavailable.",
        ],
    )


def build_gates(arts: List[UpstreamArtifact], contract: Ret60SignalContract) -> List[BlueprintGate]:
    gates: List[BlueprintGate] = []

    def add(gate_id: str, category: str, bp_req: bool, shadow_req: bool, passed: bool, reason: str) -> None:
        gates.append(BlueprintGate(
            gate_id=gate_id,
            category=category,
            required_for_blueprint=bp_req,
            required_for_future_shadow_start=shadow_req,
            passed=bool(passed),
            status="PASS" if passed else "FAIL",
            reason=reason,
        ))

    parser_status = str(get_field(arts, "parser_v2", "contract_status") or "")
    parser_positive = get_field(arts, "parser_v2", "positive_variants")
    semantic_status = str(get_field(arts, "semantic_audit", "audit_status") or "")
    semantic_confirmed = get_field(arts, "semantic_audit", "confirmed_components")
    semantic_total = get_field(arts, "semantic_audit", "total_components")
    m_status = str(get_field(arts, "m_resolver", "verdict_status") or "")
    m_rule = str(get_field(arts, "m_resolver", "selected_rule_expression") or "")
    m_share = get_field(arts, "m_resolver", "selected_pass_share")
    m_conf = get_field(arts, "m_resolver", "m_semantics_confidence")

    add("parser_v2_exists", "artifact", True, True, any(a.name == "parser_v2" and a.exists for a in arts), "parser v2 state must exist")
    add("parser_v2_pnl_ranked", "evidence", True, True, "READY_FOR_LOGGER_BLUEPRINT" in parser_status or "RULE_CONTRACT_READY" in parser_status, "parser v2 must rank variants with PnL-aware contract")
    add("parser_v2_positive_variants", "evidence", True, True, isinstance(parser_positive, int) and parser_positive > 0, "parser v2 must find positive variants")
    add("semantic_audit_exists", "artifact", True, True, any(a.name == "semantic_audit" and a.exists for a in arts), "semantic audit state must exist")
    add("semantic_audit_mostly_confirmed", "evidence", True, True, isinstance(semantic_confirmed, int) and isinstance(semantic_total, int) and semantic_confirmed >= 4 and semantic_total >= 5, "semantic audit should confirm at least 4/5 components")
    add("m_resolver_exists", "artifact", True, True, any(a.name == "m_resolver" and a.exists for a in arts), "m semantic resolver state must exist")
    add("m_semantics_resolved", "evidence", True, True, m_status == "M_SEMANTICS_RESOLVED_DIRECT_SIGNAL_RULE", "m resolver must resolve direct signal rule")
    add("m_rule_exact_pass", "evidence", True, True, isinstance(m_share, (int, float)) and float(m_share) >= 0.999 and isinstance(m_conf, (int, float)) and float(m_conf) >= 0.80, "selected m-rule must pass selected rows with high confidence")
    add("ret60_rule_defined", "signal", True, True, bool(contract.ret60_rule and "signal_ret60_bps" in contract.ret60_rule), "blueprint must define signal_ret60_bps rule")
    add("hour_defined", "signal", True, True, isinstance(contract.hour_utc, int), "blueprint must define hour_utc")
    add("delay_defined", "signal", True, True, isinstance(contract.delay_minutes, int) and contract.delay_minutes >= 0, "blueprint must define delay")
    add("hold_defined", "signal", True, True, isinstance(contract.hold_minutes, int) and contract.hold_minutes > 0, "blueprint must define hold")
    add("native_logging_contract_required", "logging", True, True, True, "blueprint defines native logging contract")
    add("sandbox_logger_not_built_yet", "implementation", False, True, False, "future shadow start requires sandbox logger implementation")
    add("sandbox_preflight_not_run_yet", "preflight", False, True, False, "future shadow start requires sandbox preflight")
    add("manual_shadow_approval_required", "approval", False, True, False, "future shadow start requires explicit manual approval")
    add("active_paper_blocked", "safety", True, True, True, "active paper remains blocked")
    add("live_blocked", "safety", True, True, True, "live remains blocked")
    return gates


def synthesize_state(workspace: Path, candidate: str, arts: List[UpstreamArtifact], contract: Ret60SignalContract, gates: List[BlueprintGate]) -> BlueprintState:
    req_bp = [g for g in gates if g.required_for_blueprint]
    pass_bp = [g for g in req_bp if g.passed]
    req_shadow = [g for g in gates if g.required_for_future_shadow_start]
    pass_shadow = [g for g in req_shadow if g.passed]

    blockers: List[str] = []
    warnings: List[str] = []
    reasons: List[str] = []

    blueprint_ready = len(pass_bp) == len(req_bp)
    sandbox_logger_implementation_allowed = blueprint_ready
    shadow_start_allowed = False
    active_paper_allowed = False
    live_allowed = False

    if blueprint_ready:
        status = "RET60_SANDBOX_LOGGER_BLUEPRINT_READY"
        next_action = "BUILD_SANDBOX_ONLY_RET60_LOGGER_ADAPTER"
        reasons.append("all required blueprint gates passed")
        reasons.append("ret60 signal contract is now specific enough for sandbox-only logger implementation planning")
    else:
        status = "RET60_BLUEPRINT_BLOCKED"
        next_action = "REPAIR_FAILED_BLUEPRINT_GATES"
        blockers.extend([f"{g.gate_id}: {g.reason}" for g in req_bp if not g.passed])

    # Future shadow gates are intentionally not all passed.
    missing_shadow = [g.gate_id for g in req_shadow if not g.passed]
    if missing_shadow:
        warnings.append("future shadow start remains blocked by: " + ", ".join(missing_shadow))

    for a in arts:
        warnings.extend([f"{a.name}: {w}" for w in a.warnings])

    return BlueprintState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=candidate,
        blueprint_status=status,
        selected_variant_key=contract.selected_variant_key,
        blueprint_ready=blueprint_ready,
        sandbox_logger_implementation_allowed=sandbox_logger_implementation_allowed,
        shadow_start_allowed=shadow_start_allowed,
        active_paper_allowed=active_paper_allowed,
        live_allowed=live_allowed,
        gates_passed_for_blueprint=len(pass_bp),
        gates_required_for_blueprint=len(req_bp),
        gates_passed_for_shadow_start=len(pass_shadow),
        gates_required_for_shadow_start=len(req_shadow),
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        hard_rules=[
            "Blueprint never starts paper/live.",
            "Blueprint never mutates active config.",
            "Blueprint never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Blueprint may allow writing a sandbox-only logger adapter, not running it.",
            "Shadow start requires sandbox logger implementation, implementation audit, preflight, and manual approval.",
            "Active paper and live remain blocked.",
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


def write_blueprint_files(workspace: Path, out_dir: Path, state: BlueprintState, contract: Ret60SignalContract, gates: List[BlueprintGate], arts: List[UpstreamArtifact]) -> None:
    persistent = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes" / contract.candidate_key / "logger_blueprint"
    persistent.mkdir(parents=True, exist_ok=True)

    native_logging_contract = {
        "required_fields": [
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
        ],
        "forbidden_fields_or_values": {
            "runtime_mode": ["live"],
            "exchange_order_id": "forbidden in sandbox shadow logger",
            "api_secret": "forbidden",
        },
    }

    payload = {
        "state": asdict(state),
        "signal_contract": asdict(contract),
        "native_logging_contract": native_logging_contract,
        "gates": [asdict(g) for g in gates],
        "upstream_artifacts": [asdict(a) for a in arts],
        "permissions": {
            "sandbox_logger_implementation_allowed": state.sandbox_logger_implementation_allowed,
            "shadow_start_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "mutates_active_config": False,
            "changes_sizing_contract": False,
        },
    }

    for d in [out_dir, persistent]:
        write_json(d / "ret60_sandbox_logger_blueprint_state.json", payload)
        write_json(d / "ret60_signal_contract.json", {"signal_contract": asdict(contract)})
        write_json(d / "ret60_native_logging_contract.json", native_logging_contract)
        records_df(gates).to_csv(d / "ret60_blueprint_gates.csv", index=False)
        records_df(arts).to_csv(d / "ret60_blueprint_upstream_artifacts.csv", index=False)

    pseudocode = f'''# REFERENCE ONLY - Ret60 sandbox logger blueprint
# This is not a runnable logger and must not be connected to live or active paper.

CANDIDATE_KEY = "{contract.candidate_key}"
SIGNAL_VERSION = "{contract.signal_version}"
SIDE = "{contract.side}"
HOUR_UTC = {contract.hour_utc}
RET60_RULE = "{contract.ret60_rule}"
DELAY_MINUTES = {contract.delay_minutes}
HOLD_MINUTES = {contract.hold_minutes}
EXTRA_SLIP_BPS = {contract.extra_slip_bps}
ACTIVE_PAPER_ALLOWED = False
LIVE_ALLOWED = False


def compute_signal_ret60_bps(current_ref_price: float, price_60m_ago: float) -> float:
    """Return 60-minute return in bps.

    The exact candle/reference basis must match the scanner before runtime.
    """
    if price_60m_ago <= 0:
        raise ValueError("price_60m_ago must be positive")
    return (current_ref_price / price_60m_ago - 1.0) * 10000.0


def should_enter_short(signal_time_utc, signal_ret60_bps: float) -> bool:
    """Blueprint signal gate. Runtime implementation requires preflight."""
    hour_ok = int(signal_time_utc.hour) == HOUR_UTC
    ret60_ok = signal_ret60_bps >= {contract.m_param}
    return bool(hour_ok and ret60_ok)


def planned_times(signal_time_utc):
    from datetime import timedelta
    entry_time = signal_time_utc + timedelta(minutes=DELAY_MINUTES)
    exit_time = entry_time + timedelta(minutes=HOLD_MINUTES)
    return entry_time, exit_time
'''

    readme = f"""# Ret60 Sandbox Logger Blueprint

Status: **{state.blueprint_status}**

## Signal contract

- Candidate: `{contract.candidate_key}`
- Version: `{contract.signal_version}`
- Selected variant: `{contract.selected_variant_key}`
- Side: `{contract.side}`
- Hour UTC: `{contract.hour_utc}`
- Ret60 rule: `{contract.ret60_rule}`
- Delay: `{contract.delay_minutes}` minute(s)
- Hold: `{contract.hold_minutes}` minute(s)
- Extra slip: `{contract.extra_slip_bps}` bps

## Permissions

- Blueprint ready: `{state.blueprint_ready}`
- Sandbox logger implementation allowed: `{state.sandbox_logger_implementation_allowed}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Next action

`{state.next_action}`

## Hard rule

This blueprint is not runtime. The next module may write a sandbox-only logger adapter, but it still must not start it.
"""

    for d in [out_dir, persistent]:
        write_text(d / "ret60_sandbox_logger_blueprint.md", readme)
        write_text(d / "ret60_sandbox_logger_blueprint_REFERENCE_ONLY.py", pseudocode)


def write_report(path: Path, state: BlueprintState, contract: Ret60SignalContract, gates: List[BlueprintGate]) -> None:
    lines = [
        "# Edge Factory Ret60 Sandbox Logger Blueprint Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Blueprint status: **{state.blueprint_status}**",
        f"Selected variant: `{state.selected_variant_key}`",
        f"Blueprint ready: **{state.blueprint_ready}**",
        f"Sandbox logger implementation allowed: **{state.sandbox_logger_implementation_allowed}**",
        f"Shadow start allowed: **{state.shadow_start_allowed}**",
        f"Active paper allowed: **{state.active_paper_allowed}**",
        f"Live allowed: **{state.live_allowed}**",
        f"Blueprint gates: **{state.gates_passed_for_blueprint}/{state.gates_required_for_blueprint}**",
        f"Future shadow gates: **{state.gates_passed_for_shadow_start}/{state.gates_required_for_shadow_start}**",
        "",
        "## Signal contract",
        "",
        f"- Candidate: `{contract.candidate_key}`",
        f"- Version: `{contract.signal_version}`",
        f"- Side: `{contract.side}`",
        f"- Hour UTC: `{contract.hour_utc}`",
        f"- Ret60 rule: `{contract.ret60_rule}`",
        f"- Delay: `{contract.delay_minutes}`",
        f"- Hold: `{contract.hold_minutes}`",
        f"- Extra slip bps: `{contract.extra_slip_bps}`",
        "",
        "## Gates",
        "",
        "| Gate | Category | Blueprint req | Shadow req | Status | Reason |",
        "|---|---|---:|---:|---:|---|",
    ]
    for g in gates:
        lines.append(f"| {g.gate_id} | {g.category} | {g.required_for_blueprint} | {g.required_for_future_shadow_start} | {g.status} | {g.reason} |")
    lines += ["", "## Reasons", ""]
    for r in state.reasons:
        lines.append(f"- {r}")
    if state.blockers:
        lines += ["", "## Blockers", ""]
        for b in state.blockers:
            lines.append(f"- {b}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for h in state.hard_rules:
        lines.append(f"- {h}")
    write_text(path, "\n".join(lines))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build ret60 sandbox logger blueprint")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    p.add_argument("--parser_state", default=None)
    p.add_argument("--semantic_state", default=None)
    p.add_argument("--m_state", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    candidate = safe_key(args.candidate)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_sandbox_logger_blueprint"
    out_dir = out_root / f"ret60_logger_blueprint_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    arts = load_upstreams(workspace, args.parser_state, args.semantic_state, args.m_state)
    contract = build_signal_contract(candidate, arts)
    gates = build_gates(arts, contract)
    state = synthesize_state(workspace, candidate, arts, contract, gates)

    write_blueprint_files(workspace, out_dir, state, contract, gates, arts)
    write_report(out_dir / "ret60_sandbox_logger_blueprint_report.md", state, contract, gates)

    print("EDGE FACTORY RET60 SANDBOX LOGGER BLUEPRINT v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"blueprint_status: {state.blueprint_status}")
    print(f"selected_variant: {state.selected_variant_key}")
    print(f"ret60_rule: {contract.ret60_rule}")
    print(f"hour_utc: {contract.hour_utc}")
    print(f"delay_minutes: {contract.delay_minutes}")
    print(f"hold_minutes: {contract.hold_minutes}")
    print(f"extra_slip_bps: {contract.extra_slip_bps}")
    print(f"blueprint_ready: {state.blueprint_ready}")
    print(f"sandbox_logger_implementation_allowed: {state.sandbox_logger_implementation_allowed}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print(f"blueprint_gates: {state.gates_passed_for_blueprint}/{state.gates_required_for_blueprint}")
    print(f"future_shadow_gates: {state.gates_passed_for_shadow_start}/{state.gates_required_for_shadow_start}")
    print("")
    print("UPSTREAMS")
    print("-" * 100)
    for a in arts:
        print(f"{a.name:16s} exists={a.exists} status={a.status} path={a.path}")
        if a.key_fields:
            print(f"     key_fields={json.dumps(a.key_fields, ensure_ascii=False, default=str)}")
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
    print(f"Report : {out_dir / 'ret60_sandbox_logger_blueprint_report.md'}")
    print(f"State  : {out_dir / 'ret60_sandbox_logger_blueprint_state.json'}")
    print(f"Contract: {out_dir / 'ret60_signal_contract.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
