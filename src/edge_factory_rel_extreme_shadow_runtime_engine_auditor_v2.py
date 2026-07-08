#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    "infer_symbol",
    "robust_time_parse",
    "find_candle_files",
    "read_hourly_close",
    "build_close_panel",
    "run_shadow_runtime_once",
    "write_heartbeat",
    "self_test",
]

REQUIRED_TEXT = [
    "--shadow_runtime",
    "--candle_dir",
    "--once",
    "--poll_seconds",
    "while True",
    "rel_extreme_shadow_heartbeat.json",
    "rel_extreme_shadow_runtime_result.json",
    "rel_extreme_shadow_candle_file_audit.csv",
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

def csv_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open("r", newline="", encoding="utf-8") as f:
            return max(0, sum(1 for _ in csv.reader(f)) - 1)
    except Exception:
        return 0

def assigned_constants(tree: ast.AST) -> dict[str, Any]:
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

def function_names(tree: ast.AST) -> set[str]:
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_auditor_v2" / f"rel_extreme_runtime_audit_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    builder_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_builder_v2",
        "rel_extreme_runtime_engine_builder_v2_",
    )
    builder_state_path = builder_dir / "rel_extreme_shadow_runtime_engine_builder_v2_state.json" if builder_dir else None
    builder_state = read_json(builder_state_path)

    engine_path = Path(str(builder_state.get("runtime_engine_path", ""))) if builder_state.get("runtime_engine_path") else None
    adapter_path = Path(str(builder_state.get("adapter_path", ""))) if builder_state.get("adapter_path") else None

    if not engine_path or not engine_path.exists():
        raise SystemExit("runtime engine v2 not found; run builder v2 first")

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

    text = engine_path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text) if comp_ok else None

    constants = assigned_constants(tree) if tree else {}
    functions = function_names(tree) if tree else set()

    missing_constants = [c for c in REQUIRED_CONSTANTS if c not in constants]
    missing_functions = [f for f in REQUIRED_FUNCTIONS if f not in functions]

    gate("required_constants_present", not missing_constants, missing_constants)
    gate("required_functions_present", not missing_functions, missing_functions)

    expected = {
        "CANDIDATE_KEY": CANDIDATE,
        "SANDBOX_ONLY": True,
        "LIVE_ALLOWED": False,
        "ACTIVE_PAPER_ALLOWED": False,
        "SHADOW_START_ALLOWED_BY_THIS_FILE": False,
        "PRIVATE_EXCHANGE_API_ALLOWED": False,
        "ORDER_PLACEMENT_ALLOWED": False,
    }

    mismatches = []
    for k, v in expected.items():
        actual = constants.get(k, "<missing>")
        if actual != v:
            mismatches.append({"constant": k, "expected": v, "actual": actual})

    gate("safety_constant_values_match", not mismatches, mismatches)

    missing_text = [x for x in REQUIRED_TEXT if x not in text]
    forbidden_hits = [x for x in FORBIDDEN_TEXT if x.lower() in text.lower()]

    gate("required_runtime_text_present", not missing_text, missing_text)
    gate("no_forbidden_text", not forbidden_hits, forbidden_hits)

    self_dir = out_dir / "self_test"
    proc_self = subprocess.run(
        [sys.executable, str(engine_path), "--self_test", "--out_dir", str(self_dir)],
        capture_output=True,
        text=True,
        timeout=60,
    )

    self_result_path = self_dir / "rel_extreme_shadow_runtime_self_test_result.json"
    self_result = read_json(self_result_path)
    self_signals = self_dir / "rel_extreme_shadow_signals.csv"
    self_closed = self_dir / "rel_extreme_shadow_closed_trades.csv"
    self_heartbeat = self_dir / "rel_extreme_shadow_heartbeat.json"

    gate("self_test_returncode_ok", proc_self.returncode == 0, proc_self.returncode)
    gate("self_test_result_ok", self_result.get("ok") is True, self_result)
    gate("self_test_signals_written", csv_rows(self_signals) == 1, f"rows={csv_rows(self_signals)}")
    gate("self_test_closed_written", csv_rows(self_closed) == 1, f"rows={csv_rows(self_closed)}")
    gate("self_test_heartbeat_written", self_heartbeat.exists(), self_heartbeat)

    runtime_dir = out_dir / "shadow_runtime_once"
    proc_runtime = subprocess.run(
        [
            sys.executable,
            str(engine_path),
            "--shadow_runtime",
            "--once",
            "--out_dir",
            str(runtime_dir),
            "--candle_dir",
            str(WORKSPACE),
            "--max_files",
            "40",
            "--max_rows_per_file",
            "50000",
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )

    runtime_result_path = runtime_dir / "rel_extreme_shadow_runtime_result.json"
    runtime_result = read_json(runtime_result_path)
    runtime_heartbeat = runtime_dir / "rel_extreme_shadow_heartbeat.json"
    runtime_audit = runtime_dir / "rel_extreme_shadow_candle_file_audit.csv"

    runtime_ok = (
        proc_runtime.returncode == 0
        and runtime_result.get("ok") is True
        and runtime_result.get("status") == "OK"
    )

    gate("shadow_runtime_once_returncode_ok", proc_runtime.returncode == 0, proc_runtime.returncode)
    gate("shadow_runtime_once_result_ok", runtime_ok, runtime_result)
    gate("shadow_runtime_heartbeat_written", runtime_heartbeat.exists(), runtime_heartbeat)
    gate("shadow_runtime_audit_written", runtime_audit.exists(), runtime_audit)
    gate("shadow_runtime_panel_nonempty", int(runtime_result.get("close_symbols") or 0) > 0 and int(runtime_result.get("close_rows") or 0) > 0, runtime_result)

    hb = read_json(runtime_heartbeat)
    gate(
        "runtime_safety_flags_false",
        hb.get("live_allowed") is False
        and hb.get("active_paper_allowed") is False
        and hb.get("shadow_start_allowed_by_this_file") is False,
        hb,
    )

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)
    audit_passed = passed == total

    status = (
        "REL_EXTREME_SHADOW_RUNTIME_ENGINE_V2_AUDIT_PASS_REAL_RUNTIME_ONCE"
        if audit_passed
        else "REL_EXTREME_SHADOW_RUNTIME_ENGINE_V2_AUDIT_FAIL"
    )

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "builder_state_path": str(builder_state_path) if builder_state_path else None,
        "engine_path": str(engine_path),
        "adapter_path": str(adapter_path) if adapter_path else None,
        "audit_status": status,
        "runtime_engine_v2_audit_passed": audit_passed,
        "engine_compiles": comp_ok,
        "compile_error": comp_err,
        "constants": constants,
        "functions": sorted(functions),
        "missing_constants": missing_constants,
        "missing_functions": missing_functions,
        "constant_mismatches": mismatches,
        "missing_required_text": missing_text,
        "forbidden_hits": forbidden_hits,
        "self_test": {
            "return_code": proc_self.returncode,
            "result": self_result,
            "stdout_tail": proc_self.stdout[-3000:],
            "stderr_tail": proc_self.stderr[-3000:],
        },
        "shadow_runtime_once": {
            "return_code": proc_runtime.returncode,
            "result": runtime_result,
            "stdout_tail": proc_runtime.stdout[-3000:],
            "stderr_tail": proc_runtime.stderr[-3000:],
        },
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_REL_EXTREME_SHADOW_PREFLIGHT_GATE_V2" if audit_passed else "FIX_RUNTIME_ENGINE_V2",
    }

    write_json(out_dir / "rel_extreme_shadow_runtime_engine_audit_v2_state.json", state)

    import pandas as pd
    pd.DataFrame(gates).to_csv(out_dir / "rel_extreme_shadow_runtime_engine_audit_v2_gates.csv", index=False)

    print("EDGE FACTORY REL EXTREME SHADOW RUNTIME ENGINE AUDITOR v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"engine_path: {engine_path}")
    print(f"audit_status: {status}")
    print(f"runtime_engine_v2_audit_passed: {audit_passed}")
    print(f"engine_compiles: {comp_ok}")
    print(f"gates: {passed}/{total}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("RUNTIME ONCE RESULT")
    print("-" * 100)
    print(json.dumps(runtime_result, indent=2, ensure_ascii=False, default=str))

    if not audit_passed:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print(f"State: {out_dir / 'rel_extreme_shadow_runtime_engine_audit_v2_state.json'}")
    print(f"Gates: {out_dir / 'rel_extreme_shadow_runtime_engine_audit_v2_gates.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
