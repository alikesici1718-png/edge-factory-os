#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Audits the generated rel_extreme shadow runtime engine (v1) by checking required constants, required functions, forbidden live/API tokens, and required CLI argument strings via AST parsing and py_compile. Reads the engine path from the latest engine builder v1 state and writes an audit state JSON to the edge_factory_rel_extreme_shadow_runtime_engine_auditor_v1 directory.
"""
from __future__ import annotations

import ast
import csv
import json
import py_compile
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"

REQUIRED_CONSTANTS = [
    "CANDIDATE_KEY",
    "SANDBOX_ONLY",
    "LIVE_ALLOWED",
    "ACTIVE_PAPER_ALLOWED",
    "SHADOW_START_ALLOWED_BY_THIS_FILE",
    "PRIVATE_EXCHANGE_API_ALLOWED",
    "ORDER_PLACEMENT_ALLOWED",
]

REQUIRED_FUNCTIONS = [
    "load_adapter",
    "write_json",
    "append_csv",
    "write_heartbeat",
    "self_test",
]

FORBIDDEN_TEXT = [
    "create_order",
    "private_post",
    "private_get",
    "fetch_balance",
    "apiKey",
    "apiSecret",
    "secretKey",
    "place_order",
    "LIVE_ALLOWED = True",
    "ACTIVE_PAPER_ALLOWED = True",
    "SHADOW_START_ALLOWED_BY_THIS_FILE = True",
    "PRIVATE_EXCHANGE_API_ALLOWED = True",
    "ORDER_PLACEMENT_ALLOWED = True",
]

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

def compile_ok(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, repr(e)

def read_csv_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open("r", newline="", encoding="utf-8") as f:
            return max(0, sum(1 for _ in csv.reader(f)) - 1)
    except Exception:
        return 0

def get_assigned_constants(tree: ast.AST) -> dict[str, Any]:
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        out[target.id] = ast.literal_eval(node.value)
                    except Exception:
                        out[target.id] = "<non_literal>"
    return out

def get_functions(tree: ast.AST) -> set[str]:
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_auditor_v1" / f"rel_extreme_runtime_audit_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    builder_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_builder_v1",
        "rel_extreme_runtime_engine_builder_",
    )
    builder_state_path = builder_dir / "rel_extreme_shadow_runtime_engine_builder_state.json" if builder_dir else None
    builder_state = read_json(builder_state_path)

    engine_path = Path(str(builder_state.get("runtime_engine_path", ""))) if builder_state.get("runtime_engine_path") else None
    adapter_path = Path(str(builder_state.get("adapter_path", ""))) if builder_state.get("adapter_path") else None

    if not engine_path or not engine_path.exists():
        raise SystemExit("runtime engine not found; run runtime engine builder first")

    gates = []

    def gate(name: str, passed: bool, reason: Any):
        gates.append({
            "gate": name,
            "passed": bool(passed),
            "reason": str(reason),
        })

    gate("engine_exists", engine_path.exists(), engine_path)
    gate("adapter_exists", bool(adapter_path and adapter_path.exists()), adapter_path)

    comp_ok, comp_err = compile_ok(engine_path)
    gate("engine_compiles", comp_ok, comp_err)

    constants = {}
    functions = set()
    text = ""

    if comp_ok:
        try:
            text = engine_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(text)
            constants = get_assigned_constants(tree)
            functions = get_functions(tree)
            gate("engine_ast_parse", True, "AST parsed")
        except Exception as e:
            gate("engine_ast_parse", False, repr(e))
    else:
        gate("engine_ast_parse", False, "compile failed")

    missing_constants = [c for c in REQUIRED_CONSTANTS if c not in constants]
    missing_functions = [f for f in REQUIRED_FUNCTIONS if f not in functions]

    gate("required_constants_present", not missing_constants, missing_constants)
    gate("required_functions_present", not missing_functions, missing_functions)

    expected_constants = {
        "CANDIDATE_KEY": CANDIDATE,
        "SANDBOX_ONLY": True,
        "LIVE_ALLOWED": False,
        "ACTIVE_PAPER_ALLOWED": False,
        "SHADOW_START_ALLOWED_BY_THIS_FILE": False,
        "PRIVATE_EXCHANGE_API_ALLOWED": False,
        "ORDER_PLACEMENT_ALLOWED": False,
    }

    mismatches = []
    for k, expected in expected_constants.items():
        actual = constants.get(k, "<missing>")
        if actual != expected:
            mismatches.append({
                "constant": k,
                "expected": expected,
                "actual": actual,
            })

    gate("required_constant_values_match", not mismatches, mismatches)

    forbidden_hits = []
    low = text.lower()
    for marker in FORBIDDEN_TEXT:
        if marker.lower() in low:
            forbidden_hits.append(marker)

    gate("no_forbidden_text", not forbidden_hits, forbidden_hits)

    self_test_dir = out_dir / "runtime_self_test"
    proc = subprocess.run(
        [sys.executable, str(engine_path), "--self_test", "--out_dir", str(self_test_dir)],
        capture_output=True,
        text=True,
        timeout=45,
    )

    result_path = self_test_dir / "rel_extreme_shadow_runtime_self_test_result.json"
    signals_csv = self_test_dir / "rel_extreme_shadow_signals.csv"
    closed_csv = self_test_dir / "rel_extreme_shadow_closed_trades.csv"
    heartbeat_json = self_test_dir / "rel_extreme_shadow_heartbeat.json"

    result = read_json(result_path)
    signals_rows = read_csv_rows(signals_csv)
    closed_rows = read_csv_rows(closed_csv)
    heartbeat = read_json(heartbeat_json)

    gate("self_test_returncode_ok", proc.returncode == 0, proc.returncode)
    gate("self_test_result_ok", result.get("ok") is True, result)
    gate("signals_csv_written", signals_csv.exists() and signals_rows == 1, f"exists={signals_csv.exists()} rows={signals_rows}")
    gate("closed_csv_written", closed_csv.exists() and closed_rows == 1, f"exists={closed_csv.exists()} rows={closed_rows}")
    gate("heartbeat_written", heartbeat_json.exists(), heartbeat_json)
    gate(
        "heartbeat_safety_flags_false",
        heartbeat.get("live_allowed") is False
        and heartbeat.get("active_paper_allowed") is False
        and heartbeat.get("shadow_start_allowed_by_this_file") is False,
        heartbeat,
    )
    gate(
        "result_safety_flags_false",
        result.get("live_allowed") is False and result.get("active_paper_allowed") is False,
        result,
    )

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)
    audit_passed = passed == total

    audit_status = (
        "REL_EXTREME_SHADOW_RUNTIME_ENGINE_AUDIT_PASS_SELF_TEST_ONLY"
        if audit_passed
        else "REL_EXTREME_SHADOW_RUNTIME_ENGINE_AUDIT_FAIL"
    )

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "builder_state_path": str(builder_state_path) if builder_state_path else None,
        "engine_path": str(engine_path),
        "adapter_path": str(adapter_path) if adapter_path else None,
        "audit_status": audit_status,
        "runtime_engine_audit_passed": audit_passed,
        "engine_compiles": comp_ok,
        "compile_error": comp_err,
        "constants": constants,
        "functions": sorted(functions),
        "missing_constants": missing_constants,
        "missing_functions": missing_functions,
        "constant_mismatches": mismatches,
        "forbidden_hits": forbidden_hits,
        "self_test": {
            "return_code": proc.returncode,
            "stdout_tail": proc.stdout[-3000:],
            "stderr_tail": proc.stderr[-3000:],
            "result_path": str(result_path),
            "signals_csv": str(signals_csv),
            "closed_csv": str(closed_csv),
            "heartbeat_json": str(heartbeat_json),
            "signals_rows": signals_rows,
            "closed_rows": closed_rows,
            "result": result,
            "heartbeat": heartbeat,
        },
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "BUILD_REL_EXTREME_SHADOW_PREFLIGHT_GATE" if audit_passed else "FIX_RUNTIME_ENGINE",
    }

    write_json(out_dir / "rel_extreme_shadow_runtime_engine_audit_state.json", state)

    import pandas as pd
    pd.DataFrame(gates).to_csv(out_dir / "rel_extreme_shadow_runtime_engine_audit_gates.csv", index=False)

    print("EDGE FACTORY REL EXTREME SHADOW RUNTIME ENGINE AUDITOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"engine_path: {engine_path}")
    print(f"audit_status: {audit_status}")
    print(f"runtime_engine_audit_passed: {audit_passed}")
    print(f"engine_compiles: {comp_ok}")
    print(f"signals_rows: {signals_rows}")
    print(f"closed_rows: {closed_rows}")
    print(f"gates: {passed}/{total}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if not audit_passed:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print("SELF TEST")
    print("-" * 100)
    print(f"return_code: {proc.returncode}")
    print(f"result_path: {result_path}")
    print(f"signals_csv: {signals_csv}")
    print(f"closed_csv : {closed_csv}")
    print(f"heartbeat  : {heartbeat_json}")

    if proc.stdout:
        print()
        print("SELF TEST STDOUT")
        print("-" * 100)
        print(proc.stdout[-2000:])
    if proc.stderr:
        print()
        print("SELF TEST STDERR")
        print("-" * 100)
        print(proc.stderr[-2000:])

    print()
    print(f"State: {out_dir / 'rel_extreme_shadow_runtime_engine_audit_state.json'}")
    print(f"Gates: {out_dir / 'rel_extreme_shadow_runtime_engine_audit_gates.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
