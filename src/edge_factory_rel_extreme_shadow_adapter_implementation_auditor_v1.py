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
    "SIDE",
    "LOOKBACK_HOURS",
    "COIN_THRESHOLD_BPS",
    "REL_THRESHOLD_BPS",
    "HOLD_HOURS",
    "COST_BPS",
    "CAP_SIGNALS_PER_HOUR",
    "SANDBOX_ONLY",
    "LIVE_ALLOWED",
    "ACTIVE_PAPER_ALLOWED",
    "SHADOW_START_ALLOWED_BY_THIS_FILE",
    "PRIVATE_EXCHANGE_API_ALLOWED",
    "ORDER_PLACEMENT_ALLOWED",
]

REQUIRED_FUNCTIONS = [
    "compute_coin_return_bps",
    "compute_short_return_bps",
    "rel_rule_pass",
    "build_signal_row",
    "rank_and_cap_signals",
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
    "order_placement_allowed = True",
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

def parse_ast(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return ast.parse(text), text

def get_assigned_constants(tree: ast.AST) -> dict[str, Any]:
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    try:
                        out[name] = ast.literal_eval(node.value)
                    except Exception:
                        out[name] = "<non_literal>"
    return out

def get_functions(tree: ast.AST) -> set[str]:
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }

def read_csv_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open("r", newline="", encoding="utf-8") as f:
            return max(0, sum(1 for _ in csv.reader(f)) - 1)
    except Exception:
        return 0

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_adapter_implementation_auditor_v1" / f"rel_extreme_adapter_audit_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    builder_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_logger_adapter_builder_v1",
        "rel_extreme_adapter_builder_",
    )
    manifest_path = builder_dir / "rel_extreme_shadow_adapter_manifest.json" if builder_dir else None
    manifest = read_json(manifest_path)

    adapter_path = Path(str(manifest.get("adapter_path", ""))) if manifest.get("adapter_path") else None
    if not adapter_path or not adapter_path.exists():
        raise SystemExit("adapter not found; run rel_extreme shadow adapter builder first")

    comp_ok, comp_err = compile_ok(adapter_path)

    gates = []

    def gate(name: str, passed: bool, reason: str):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("adapter_exists", adapter_path.exists(), adapter_path)
    gate("adapter_compiles", comp_ok, comp_err)

    tree = None
    text = ""
    constants = {}
    functions = set()

    if comp_ok:
        try:
            tree, text = parse_ast(adapter_path)
            constants = get_assigned_constants(tree)
            functions = get_functions(tree)
            gate("adapter_ast_parse", True, "AST parsed")
        except Exception as e:
            gate("adapter_ast_parse", False, repr(e))
    else:
        gate("adapter_ast_parse", False, "compile failed")

    missing_constants = [c for c in REQUIRED_CONSTANTS if c not in constants]
    missing_functions = [f for f in REQUIRED_FUNCTIONS if f not in functions]

    gate("required_constants_present", not missing_constants, missing_constants)
    gate("required_functions_present", not missing_functions, missing_functions)

    expected_constants = {
        "CANDIDATE_KEY": CANDIDATE,
        "SIDE": "short",
        "LOOKBACK_HOURS": 6,
        "COIN_THRESHOLD_BPS": 300.0,
        "REL_THRESHOLD_BPS": 600.0,
        "HOLD_HOURS": 24,
        "CAP_SIGNALS_PER_HOUR": 1,
        "SANDBOX_ONLY": True,
        "LIVE_ALLOWED": False,
        "ACTIVE_PAPER_ALLOWED": False,
        "SHADOW_START_ALLOWED_BY_THIS_FILE": False,
        "PRIVATE_EXCHANGE_API_ALLOWED": False,
        "ORDER_PLACEMENT_ALLOWED": False,
    }

    mismatch = []
    for k, expected in expected_constants.items():
        actual = constants.get(k, "<missing>")
        if isinstance(expected, float):
            try:
                ok = abs(float(actual) - expected) < 1e-9
            except Exception:
                ok = False
        else:
            ok = actual == expected
        if not ok:
            mismatch.append({"constant": k, "expected": expected, "actual": actual})

    gate("required_constant_values_match", not mismatch, mismatch)

    forbidden_hits = []
    low_text = text.lower()
    for marker in FORBIDDEN_TEXT:
        if marker.lower() in low_text:
            forbidden_hits.append(marker)

    gate("no_forbidden_text", not forbidden_hits, forbidden_hits)

    # Run self-test freshly.
    self_test_dir = out_dir / "adapter_self_test"
    proc = subprocess.run(
        [sys.executable, str(adapter_path), "--self_test", "--out_dir", str(self_test_dir)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    result_json = self_test_dir / "rel_extreme_shadow_adapter_self_test_result.json"
    signal_csv = self_test_dir / "rel_extreme_shadow_adapter_self_test_signals.csv"
    heartbeat_json = self_test_dir / "rel_extreme_shadow_adapter_self_test_heartbeat.json"

    result = read_json(result_json)
    signal_rows = read_csv_rows(signal_csv)

    gate("self_test_returncode_ok", proc.returncode == 0, proc.returncode)
    gate("self_test_result_ok", result.get("ok") is True, result)
    gate("self_test_signal_csv_written", signal_csv.exists() and signal_rows == 1, f"exists={signal_csv.exists()} rows={signal_rows}")
    gate("self_test_heartbeat_written", heartbeat_json.exists(), heartbeat_json)

    hb = read_json(heartbeat_json)
    gate("heartbeat_safety_flags_false", hb.get("live_allowed") is False and hb.get("active_paper_allowed") is False, hb)

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)

    audit_passed = passed == total

    audit_status = (
        "REL_EXTREME_ADAPTER_IMPLEMENTATION_AUDIT_PASS_SELF_TEST_ONLY"
        if audit_passed
        else "REL_EXTREME_ADAPTER_IMPLEMENTATION_AUDIT_FAIL"
    )

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "adapter_path": str(adapter_path),
        "audit_status": audit_status,
        "implementation_audit_passed": audit_passed,
        "adapter_compiles": comp_ok,
        "compile_error": comp_err,
        "constants": constants,
        "functions": sorted(functions),
        "missing_constants": missing_constants,
        "missing_functions": missing_functions,
        "constant_mismatches": mismatch,
        "forbidden_hits": forbidden_hits,
        "self_test": {
            "return_code": proc.returncode,
            "stdout_tail": proc.stdout[-3000:],
            "stderr_tail": proc.stderr[-3000:],
            "result_json": str(result_json),
            "signal_csv": str(signal_csv),
            "signal_rows": signal_rows,
            "heartbeat_json": str(heartbeat_json),
            "result": result,
        },
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "BUILD_REL_EXTREME_SHADOW_RUNTIME_ENGINE_OR_PREFLIGHT" if audit_passed else "FIX_ADAPTER_IMPLEMENTATION",
    }

    write_json(out_dir / "rel_extreme_shadow_adapter_implementation_audit_state.json", state)
    pd = __import__("pandas")
    pd.DataFrame(gates).to_csv(out_dir / "rel_extreme_shadow_adapter_implementation_audit_gates.csv", index=False)

    print("EDGE FACTORY REL EXTREME SHADOW ADAPTER IMPLEMENTATION AUDITOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"adapter  : {adapter_path}")
    print(f"audit_status: {audit_status}")
    print(f"adapter_compiles: {comp_ok}")
    print(f"implementation_audit_passed: {audit_passed}")
    print(f"gates: {passed}/{total}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()

    if not audit_passed:
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")
        print()

    print("SELF TEST")
    print("-" * 100)
    print(f"return_code: {proc.returncode}")
    print(f"signal_rows: {signal_rows}")
    print(f"result_json: {result_json}")
    print(f"signal_csv : {signal_csv}")
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
    print(f"State: {out_dir / 'rel_extreme_shadow_adapter_implementation_audit_state.json'}")
    print(f"Gates: {out_dir / 'rel_extreme_shadow_adapter_implementation_audit_gates.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
