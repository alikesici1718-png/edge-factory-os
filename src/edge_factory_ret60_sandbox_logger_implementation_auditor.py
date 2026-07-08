#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 SANDBOX LOGGER IMPLEMENTATION AUDITOR v1
===========================================================

Purpose
-------
Audit the generated ret60 sandbox shadow logger adapter implementation.

This module is the next safe step after:
    edge_factory_ret60_sandbox_logger_adapter_builder.py

It verifies that the generated adapter:
    - exists
    - compiles
    - is sandbox-only
    - contains no dangerous imports/calls
    - exposes required constants/functions
    - passes its own self-test
    - emits a native logging CSV with required fields
    - keeps live/active/shadow runtime blocked

It DOES NOT:
    - start paper
    - start live
    - connect to exchange APIs
    - send orders
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It MAY:
    - execute the generated adapter with --self_test only

Run:
    python "C:\Users\alike\edge_factory_ret60_sandbox_logger_implementation_auditor.py"

Core rule
---------
Audit pass is not shadow-start approval. Shadow start still requires sandbox preflight and manual approval.
"""

from __future__ import annotations

import argparse
import ast
import csv
import importlib.util
import json
import py_compile
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"

REQUIRED_CONSTANTS = {
    "CANDIDATE_KEY": DEFAULT_CANDIDATE,
    "SIDE": "short",
    "HOUR_UTC": 8,
    "M_PARAM": 75,
    "DELAY_MINUTES": 1,
    "HOLD_MINUTES": 720,
    "EXTRA_SLIP_BPS": 0,
    "SANDBOX_ONLY": True,
    "LIVE_ALLOWED": False,
    "ACTIVE_PAPER_ALLOWED": False,
    "SHADOW_START_ALLOWED_BY_THIS_FILE": False,
    "PRIVATE_EXCHANGE_API_ALLOWED": False,
    "ORDER_PLACEMENT_ALLOWED": False,
}

REQUIRED_FUNCTIONS = [
    "compute_signal_ret60_bps",
    "ret60_rule_pass",
    "decide",
    "short_gross_return_bps",
    "net_return_bps",
    "pnl_usdt",
    "build_log_row",
    "append_csv",
    "self_test",
]

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

FORBIDDEN_IMPORT_ROOTS = {
    "ccxt",
    "okx",
    "requests",
    "websocket",
    "websockets",
    "aiohttp",
    "httpx",
    "urllib",
    "socket",
}

FORBIDDEN_CALL_NAMES = {
    "create_order",
    "place_order",
    "order",
    "market_order",
    "limit_order",
    "send_order",
    "private_get",
    "private_post",
    "fetch_balance",
    "fetch_positions",
    "fetch_open_orders",
}

DANGEROUS_LITERAL_HINTS = [
    "api_key=",
    "apiSecret",
    "secretKey",
    "create_order(",
    "place_order(",
]


@dataclass
class AdapterManifest:
    manifest_path: Optional[str]
    adapter_path: Optional[str]
    builder_status: str
    adapter_written: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    warnings: List[str]


@dataclass
class AuditGate:
    gate_id: str
    category: str
    required_for_audit_pass: bool
    required_for_future_shadow_start: bool
    passed: bool
    status: str
    reason: str
    details: str


@dataclass
class SelfTestResult:
    executed: bool
    ok: bool
    return_code: Optional[int]
    stdout_tail: str
    stderr_tail: str
    result_json_path: Optional[str]
    csv_path: Optional[str]
    csv_rows: int
    csv_has_required_fields: bool
    live_allowed_false: bool
    active_paper_allowed_false: bool
    shadow_start_allowed_false: bool
    warnings: List[str]


@dataclass
class ImplementationAuditState:
    generated_at: str
    workspace: str
    candidate: str
    output_dir: str
    manifest_path: Optional[str]
    adapter_path: Optional[str]
    audit_status: str
    adapter_compiles: bool
    self_test_ok: bool
    native_log_ok: bool
    dangerous_code_detected: bool
    implementation_audit_passed: bool
    sandbox_preflight_required: bool
    manual_approval_required: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    gates_passed_for_audit: int
    gates_required_for_audit: int
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


def latest_adapter_builder_dir(workspace: Path) -> Optional[Path]:
    return latest_child_dir(workspace / "edge_factory_ret60_sandbox_logger_adapter_builder", "ret60_adapter_builder_")


def load_manifest(workspace: Path, explicit_manifest: Optional[str], explicit_adapter: Optional[str]) -> AdapterManifest:
    warnings: List[str] = []
    manifest_path = Path(explicit_manifest) if explicit_manifest else None
    if manifest_path is None:
        d = latest_adapter_builder_dir(workspace)
        if d:
            manifest_path = d / "ret60_sandbox_logger_adapter_manifest.json"
    obj = read_json_optional(manifest_path)
    state = obj.get("state", {}) if isinstance(obj.get("state"), dict) else {}

    adapter_path = explicit_adapter or state.get("adapter_path") or obj.get("adapter_path")
    if not manifest_path or not manifest_path.exists():
        warnings.append("adapter manifest missing")
    if not adapter_path:
        warnings.append("adapter path missing in manifest")

    return AdapterManifest(
        manifest_path=str(manifest_path) if manifest_path else None,
        adapter_path=str(adapter_path) if adapter_path else None,
        builder_status=str(state.get("builder_status") or "UNKNOWN"),
        adapter_written=bool(state.get("adapter_written", False)),
        shadow_start_allowed=bool(state.get("shadow_start_allowed", False)),
        active_paper_allowed=bool(state.get("active_paper_allowed", False)),
        live_allowed=bool(state.get("live_allowed", False)),
        warnings=warnings,
    )


def parse_ast(path: Path) -> Tuple[Optional[ast.AST], List[str]]:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        return ast.parse(src), []
    except Exception as e:
        return None, [f"ast parse failed: {e}"]


def compile_check(path: Optional[str]) -> Tuple[bool, str]:
    if not path or not Path(path).exists():
        return False, "adapter file missing"
    try:
        py_compile.compile(path, doraise=True)
        return True, "compile ok"
    except Exception as e:
        return False, repr(e)


def inspect_imports_and_calls(path: Optional[str]) -> Tuple[bool, List[str], List[str], List[str]]:
    warnings: List[str] = []
    imports: List[str] = []
    calls: List[str] = []
    if not path or not Path(path).exists():
        return True, imports, calls, ["adapter missing"]
    tree, parse_warnings = parse_ast(Path(path))
    warnings.extend(parse_warnings)
    dangerous = False
    if tree is None:
        return True, imports, calls, warnings

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                imports.append(alias.name)
                if root in FORBIDDEN_IMPORT_ROOTS:
                    dangerous = True
                    warnings.append(f"forbidden import detected: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            root = mod.split(".")[0]
            imports.append(mod)
            if root in FORBIDDEN_IMPORT_ROOTS:
                dangerous = True
                warnings.append(f"forbidden import-from detected: {mod}")
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name:
                calls.append(name)
                if name in FORBIDDEN_CALL_NAMES:
                    dangerous = True
                    warnings.append(f"forbidden call detected: {name}")

    # Literal scan for high-risk hardcoded API/order strings. Avoid flagging harmless comments about bans unless exact high-risk pattern appears.
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    for hint in DANGEROUS_LITERAL_HINTS:
        if hint in text:
            dangerous = True
            warnings.append(f"dangerous literal hint detected: {hint}")
    return dangerous, sorted(set(imports)), sorted(set(calls)), warnings


def import_adapter(path: Optional[str]) -> Tuple[Optional[Any], List[str]]:
    warnings: List[str] = []
    if not path or not Path(path).exists():
        return None, ["adapter file missing"]
    try:
        spec = importlib.util.spec_from_file_location("ret60_sandbox_shadow_logger_audit", path)
        if spec is None or spec.loader is None:
            return None, ["import spec failed"]
        module = importlib.util.module_from_spec(spec)
        # Required for dataclasses and modules that inspect sys.modules during import.
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        return module, []
    except Exception as e:
        return None, [f"adapter import failed: {e}"]


def check_constants_and_functions(module: Optional[Any]) -> Tuple[Dict[str, bool], Dict[str, bool], List[str]]:
    warnings: List[str] = []
    const_results: Dict[str, bool] = {}
    func_results: Dict[str, bool] = {}
    if module is None:
        for k in REQUIRED_CONSTANTS:
            const_results[k] = False
        for f in REQUIRED_FUNCTIONS:
            func_results[f] = False
        return const_results, func_results, ["module unavailable"]

    for key, expected in REQUIRED_CONSTANTS.items():
        actual = getattr(module, key, None)
        const_results[key] = actual == expected
        if actual != expected:
            warnings.append(f"constant mismatch {key}: expected {expected!r}, got {actual!r}")
    for fn in REQUIRED_FUNCTIONS:
        func_results[fn] = callable(getattr(module, fn, None))
        if not func_results[fn]:
            warnings.append(f"missing function: {fn}")
    return const_results, func_results, warnings


def run_self_test(adapter_path: Optional[str], out_dir: Path, timeout_sec: int = 30) -> SelfTestResult:
    warnings: List[str] = []
    if not adapter_path or not Path(adapter_path).exists():
        return SelfTestResult(False, False, None, "", "", None, None, 0, False, False, False, False, ["adapter missing"])

    st_dir = out_dir / "adapter_self_test"
    st_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, adapter_path, "--self_test", "--out_dir", str(st_dir)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        stdout = proc.stdout[-4000:]
        stderr = proc.stderr[-4000:]
        ok = proc.returncode == 0
    except Exception as e:
        return SelfTestResult(True, False, None, "", repr(e), None, None, 0, False, False, False, False, [f"self-test execution failed: {e}"])

    result_path = st_dir / "ret60_sandbox_adapter_self_test_result.json"
    result = read_json_optional(result_path)
    csv_path = result.get("csv_path") if isinstance(result, dict) else None
    csv_rows = 0
    csv_has_required = False
    if csv_path and Path(csv_path).exists():
        try:
            df = pd.read_csv(csv_path)
            csv_rows = int(len(df))
            csv_has_required = all(c in df.columns for c in REQUIRED_LOG_FIELDS)
            if not csv_has_required:
                missing = [c for c in REQUIRED_LOG_FIELDS if c not in df.columns]
                warnings.append("self-test CSV missing fields: " + ", ".join(missing))
        except Exception as e:
            warnings.append(f"failed reading self-test CSV: {e}")
    else:
        warnings.append("self-test CSV path missing or not found")

    live_false = bool(result.get("live_allowed") is False) if isinstance(result, dict) else False
    active_false = bool(result.get("active_paper_allowed") is False) if isinstance(result, dict) else False
    shadow_false = bool(result.get("shadow_start_allowed_by_this_file") is False) if isinstance(result, dict) else False
    if not live_false:
        warnings.append("self-test result does not confirm live_allowed False")
    if not active_false:
        warnings.append("self-test result does not confirm active_paper_allowed False")
    if not shadow_false:
        warnings.append("self-test result does not confirm shadow_start_allowed False")

    return SelfTestResult(
        executed=True,
        ok=ok and bool(result.get("ok", False)) and csv_has_required and live_false and active_false and shadow_false,
        return_code=proc.returncode,
        stdout_tail=stdout,
        stderr_tail=stderr,
        result_json_path=str(result_path) if result_path.exists() else None,
        csv_path=str(csv_path) if csv_path else None,
        csv_rows=csv_rows,
        csv_has_required_fields=csv_has_required,
        live_allowed_false=live_false,
        active_paper_allowed_false=active_false,
        shadow_start_allowed_false=shadow_false,
        warnings=warnings,
    )


def build_gates(
    manifest: AdapterManifest,
    compiles: bool,
    compile_msg: str,
    dangerous: bool,
    const_results: Dict[str, bool],
    func_results: Dict[str, bool],
    self_test: SelfTestResult,
) -> List[AuditGate]:
    gates: List[AuditGate] = []

    def add(gate_id: str, category: str, audit_req: bool, shadow_req: bool, passed: bool, reason: str, details: str = "") -> None:
        gates.append(AuditGate(
            gate_id=gate_id,
            category=category,
            required_for_audit_pass=audit_req,
            required_for_future_shadow_start=shadow_req,
            passed=bool(passed),
            status="PASS" if passed else "FAIL",
            reason=reason,
            details=details,
        ))

    add("manifest_exists", "artifact", True, True, bool(manifest.manifest_path and Path(manifest.manifest_path).exists()), "adapter manifest must exist")
    add("adapter_written", "artifact", True, True, manifest.adapter_written, "adapter builder must report adapter_written=True")
    add("adapter_file_exists", "artifact", True, True, bool(manifest.adapter_path and Path(manifest.adapter_path).exists()), "adapter file must exist")
    add("builder_live_blocked", "safety", True, True, not manifest.live_allowed, "builder manifest must block live")
    add("builder_active_paper_blocked", "safety", True, True, not manifest.active_paper_allowed, "builder manifest must block active paper")
    add("builder_shadow_blocked", "safety", True, False, not manifest.shadow_start_allowed, "builder manifest must block shadow start at this stage")
    add("adapter_compiles", "syntax", True, True, compiles, "adapter must compile", compile_msg)
    add("no_dangerous_code", "safety", True, True, not dangerous, "adapter must not contain dangerous imports/calls/literals")

    missing_consts = [k for k, ok in const_results.items() if not ok]
    missing_funcs = [k for k, ok in func_results.items() if not ok]
    add("required_constants", "contract", True, True, not missing_consts, "required constants must match", "missing/mismatch: " + ", ".join(missing_consts))
    add("required_functions", "contract", True, True, not missing_funcs, "required functions must exist", "missing: " + ", ".join(missing_funcs))
    add("self_test_executed", "self_test", True, True, self_test.executed, "adapter self-test must execute")
    add("self_test_ok", "self_test", True, True, self_test.ok, "adapter self-test must pass")
    add("native_log_csv", "logging", True, True, self_test.csv_rows > 0 and self_test.csv_has_required_fields, "self-test must emit native log CSV with required fields")
    add("self_test_live_false", "safety", True, True, self_test.live_allowed_false, "self-test must confirm live_allowed False")
    add("self_test_active_false", "safety", True, True, self_test.active_paper_allowed_false, "self-test must confirm active_paper_allowed False")
    add("self_test_shadow_false", "safety", True, False, self_test.shadow_start_allowed_false, "self-test must confirm shadow_start_allowed False")
    add("sandbox_preflight_not_done", "preflight", False, True, False, "future shadow start requires sandbox preflight")
    add("manual_shadow_approval_not_done", "approval", False, True, False, "future shadow start requires manual approval")
    return gates


def synthesize_state(workspace: Path, out_dir: Path, manifest: AdapterManifest, gates: List[AuditGate], compiles: bool, self_test: SelfTestResult, dangerous: bool, warnings: List[str]) -> ImplementationAuditState:
    audit_required = [g for g in gates if g.required_for_audit_pass]
    audit_passed = [g for g in audit_required if g.passed]
    shadow_required = [g for g in gates if g.required_for_future_shadow_start]
    shadow_passed = [g for g in shadow_required if g.passed]

    implementation_passed = len(audit_passed) == len(audit_required)
    reasons: List[str] = []
    blockers: List[str] = []

    if implementation_passed:
        status = "RET60_ADAPTER_IMPLEMENTATION_AUDIT_PASS_SELF_TEST_ONLY"
        next_action = "BUILD_RET60_SANDBOX_PREFLIGHT_GATE"
        reasons.append("adapter implementation audit passed")
        reasons.append("adapter compiled, passed self-test, emitted native log CSV, and kept live/active/shadow blocked")
    else:
        status = "RET60_ADAPTER_IMPLEMENTATION_AUDIT_FAIL"
        next_action = "REPAIR_ADAPTER_IMPLEMENTATION"
        blockers.extend([f"{g.gate_id}: {g.reason} {g.details}" for g in audit_required if not g.passed])

    missing_shadow = [g.gate_id for g in shadow_required if not g.passed]
    if missing_shadow:
        warnings.append("future shadow start remains blocked by: " + ", ".join(missing_shadow))

    return ImplementationAuditState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=DEFAULT_CANDIDATE,
        output_dir=str(out_dir),
        manifest_path=manifest.manifest_path,
        adapter_path=manifest.adapter_path,
        audit_status=status,
        adapter_compiles=compiles,
        self_test_ok=self_test.ok,
        native_log_ok=self_test.csv_rows > 0 and self_test.csv_has_required_fields,
        dangerous_code_detected=dangerous,
        implementation_audit_passed=implementation_passed,
        sandbox_preflight_required=True,
        manual_approval_required=True,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        gates_passed_for_audit=len(audit_passed),
        gates_required_for_audit=len(audit_required),
        gates_passed_for_shadow_start=len(shadow_passed),
        gates_required_for_shadow_start=len(shadow_required),
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        hard_rules=[
            "Implementation auditor never starts paper/live.",
            "Implementation auditor may run adapter --self_test only.",
            "Implementation auditor never mutates active config.",
            "Implementation auditor never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Audit pass is not shadow-start approval.",
            "Shadow start still requires sandbox preflight and manual approval.",
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
        rows.append(d)
    return pd.DataFrame(rows)


def write_outputs(out_dir: Path, state: ImplementationAuditState, manifest: AdapterManifest, gates: List[AuditGate], self_test: SelfTestResult, imports: List[str], calls: List[str], const_results: Dict[str, bool], func_results: Dict[str, bool]) -> None:
    payload = {
        "state": asdict(state),
        "manifest": asdict(manifest),
        "gates": [asdict(g) for g in gates],
        "self_test": asdict(self_test),
        "imports": imports,
        "calls": calls,
        "constant_results": const_results,
        "function_results": func_results,
    }
    write_json(out_dir / "ret60_sandbox_logger_implementation_audit_state.json", payload)
    records_df(gates).to_csv(out_dir / "ret60_sandbox_logger_implementation_audit_gates.csv", index=False)
    pd.DataFrame([{"import": x} for x in imports]).to_csv(out_dir / "ret60_adapter_imports.csv", index=False)
    pd.DataFrame([{"call": x} for x in calls]).to_csv(out_dir / "ret60_adapter_calls.csv", index=False)

    md = f"""# Ret60 Sandbox Logger Implementation Audit

Status: **{state.audit_status}**

- Adapter: `{state.adapter_path}`
- Compiles: `{state.adapter_compiles}`
- Self-test OK: `{state.self_test_ok}`
- Native log OK: `{state.native_log_ok}`
- Dangerous code detected: `{state.dangerous_code_detected}`
- Implementation audit passed: `{state.implementation_audit_passed}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Next action

`{state.next_action}`

## Self-test

- Executed: `{self_test.executed}`
- OK: `{self_test.ok}`
- Return code: `{self_test.return_code}`
- CSV path: `{self_test.csv_path}`
- CSV rows: `{self_test.csv_rows}`
- Required fields: `{self_test.csv_has_required_fields}`

## Blockers

```text
{chr(10).join(state.blockers) if state.blockers else 'none'}
```

## Warnings

```text
{chr(10).join(state.warnings) if state.warnings else 'none'}
```
"""
    write_text(out_dir / "ret60_sandbox_logger_implementation_audit_report.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Audit ret60 sandbox logger adapter implementation")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--manifest", default=None)
    p.add_argument("--adapter", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--skip_self_test", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_sandbox_logger_implementation_auditor"
    out_dir = out_root / f"ret60_implementation_audit_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(workspace, args.manifest, args.adapter)
    warnings: List[str] = list(manifest.warnings)
    compiles, compile_msg = compile_check(manifest.adapter_path)
    dangerous, imports, calls, danger_warnings = inspect_imports_and_calls(manifest.adapter_path)
    warnings.extend(danger_warnings)
    module, import_warnings = import_adapter(manifest.adapter_path) if compiles and not dangerous else (None, [])
    warnings.extend(import_warnings)
    const_results, func_results, cf_warnings = check_constants_and_functions(module)
    warnings.extend(cf_warnings)

    if args.skip_self_test:
        self_test = SelfTestResult(False, False, None, "", "", None, None, 0, False, False, False, False, ["self-test skipped by argument"])
        warnings.append("self-test skipped; audit cannot pass")
    else:
        self_test = run_self_test(manifest.adapter_path, out_dir)
        warnings.extend(self_test.warnings)

    gates = build_gates(manifest, compiles, compile_msg, dangerous, const_results, func_results, self_test)
    state = synthesize_state(workspace, out_dir, manifest, gates, compiles, self_test, dangerous, warnings)
    write_outputs(out_dir, state, manifest, gates, self_test, imports, calls, const_results, func_results)

    print("EDGE FACTORY RET60 SANDBOX LOGGER IMPLEMENTATION AUDITOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"manifest : {manifest.manifest_path}")
    print(f"adapter  : {manifest.adapter_path}")
    print(f"audit_status: {state.audit_status}")
    print(f"adapter_compiles: {state.adapter_compiles}")
    print(f"self_test_ok: {state.self_test_ok}")
    print(f"native_log_ok: {state.native_log_ok}")
    print(f"dangerous_code_detected: {state.dangerous_code_detected}")
    print(f"implementation_audit_passed: {state.implementation_audit_passed}")
    print(f"audit_gates: {state.gates_passed_for_audit}/{state.gates_required_for_audit}")
    print(f"future_shadow_gates: {state.gates_passed_for_shadow_start}/{state.gates_required_for_shadow_start}")
    print("sandbox_preflight_required: True")
    print("manual_approval_required: True")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("")
    print("SELF TEST")
    print("-" * 100)
    print(f"executed={self_test.executed} ok={self_test.ok} rc={self_test.return_code} csv_rows={self_test.csv_rows} csv_required_fields={self_test.csv_has_required_fields}")
    print(f"result_json={self_test.result_json_path}")
    print(f"csv_path={self_test.csv_path}")
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
    print(f"Report : {out_dir / 'ret60_sandbox_logger_implementation_audit_report.md'}")
    print(f"State  : {out_dir / 'ret60_sandbox_logger_implementation_audit_state.json'}")
    print(f"Gates  : {out_dir / 'ret60_sandbox_logger_implementation_audit_gates.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
