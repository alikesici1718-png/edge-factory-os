#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Builds a sandbox-only logger adapter Python file for the rel_extreme_reversion_short shadow run by reading the spec review JSON and code-generating a fully parameterized adapter with all live/order flags set to False. Outputs the generated adapter script and a manifest JSON to the edge_factory_rel_extreme_shadow_logger_adapter_builder_v1 directory.
"""
from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"

def stamp():
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

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def compile_ok(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, repr(e)

def main():
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_logger_adapter_builder_v1" / f"rel_extreme_adapter_builder_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_shadow_spec_review_v1", "rel_extreme_shadow_spec_")
    spec_path = spec_dir / "rel_extreme_shadow_spec.json" if spec_dir else None
    spec = read_json(spec_path)

    if not spec:
        raise SystemExit("rel_extreme_shadow_spec.json not found; run shadow spec review first")

    if spec.get("live_allowed") is not False or spec.get("active_paper_allowed") is not False:
        raise SystemExit("unsafe spec: active/live flags not false")

    rule = spec.get("rule", {})
    alloc = spec.get("allocator_constraints", {})

    adapter_path = out_dir / "rel_extreme_shadow_adapter.py"

    adapter_code = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

CANDIDATE_KEY = "{CANDIDATE}"
SIDE = "short"
LOOKBACK_HOURS = {int(rule.get("lookback_hours") or 6)}
COIN_THRESHOLD_BPS = {float(rule.get("coin_threshold_bps") or 300.0)}
REL_THRESHOLD_BPS = {float(rule.get("relative_threshold_bps") or 600.0)}
HOLD_HOURS = {int(rule.get("hold_hours") or 24)}
COST_BPS = {float(rule.get("cost_bps_reference") or 25.0)}
CAP_SIGNALS_PER_HOUR = {int(alloc.get("cap_signals_per_hour") or 1)}
SHADOW_MAX_OPEN_POSITIONS_SUGGESTED = {int(alloc.get("shadow_max_open_positions_suggested") or 24)}

SANDBOX_ONLY = True
LIVE_ALLOWED = False
ACTIVE_PAPER_ALLOWED = False
SHADOW_START_ALLOWED_BY_THIS_FILE = False
PRIVATE_EXCHANGE_API_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def compute_coin_return_bps(current_close: float, prior_close: float) -> float:
    if prior_close <= 0:
        return float("nan")
    return (current_close / prior_close - 1.0) * 10000.0

def compute_short_return_bps(entry_close: float, exit_close: float, cost_bps: float = COST_BPS) -> float:
    if entry_close <= 0 or exit_close <= 0:
        return float("nan")
    gross = (entry_close / exit_close - 1.0) * 10000.0
    return gross - cost_bps

def rel_rule_pass(coin_ret_bps: float, market_ret_bps: float) -> bool:
    rel_ret_bps = coin_ret_bps - market_ret_bps
    return coin_ret_bps >= COIN_THRESHOLD_BPS and rel_ret_bps >= REL_THRESHOLD_BPS

def build_signal_row(symbol: str, signal_time: Any, coin_ret_bps: float, market_ret_bps: float, entry_close: float) -> dict[str, Any]:
    rel_ret_bps = coin_ret_bps - market_ret_bps
    return {{
        "candidate": CANDIDATE_KEY,
        "symbol": symbol,
        "side": SIDE,
        "signal_time": str(signal_time),
        "entry_time": str(signal_time),
        "planned_exit_time": str(pd.to_datetime(signal_time, utc=True) + pd.Timedelta(hours=HOLD_HOURS)),
        "coin_ret_bps": float(coin_ret_bps),
        "market_ret_bps": float(market_ret_bps),
        "rel_ret_bps": float(rel_ret_bps),
        "entry_close": float(entry_close),
        "lookback_hours": LOOKBACK_HOURS,
        "hold_hours": HOLD_HOURS,
        "cost_bps": COST_BPS,
        "cap_signals_per_hour": CAP_SIGNALS_PER_HOUR,
        "live_allowed": False,
        "active_paper_allowed": False,
        "created_at": utc_now_iso(),
    }}

def rank_and_cap_signals(rows: list[dict[str, Any]], cap: int = CAP_SIGNALS_PER_HOUR) -> list[dict[str, Any]]:
    rows = sorted(
        rows,
        key=lambda r: (float(r.get("rel_ret_bps", 0.0)), float(r.get("coin_ret_bps", 0.0))),
        reverse=True,
    )
    return rows[:max(0, int(cap))]

def append_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)

def write_heartbeat(path: Path, extra: dict[str, Any] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    obj = {{
        "candidate": CANDIDATE_KEY,
        "timestamp": utc_now_iso(),
        "sandbox_only": True,
        "live_allowed": False,
        "active_paper_allowed": False,
        "shadow_start_allowed_by_this_file": False,
    }}
    if extra:
        obj.update(extra)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def self_test(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Synthetic mini test:
    # coin A jumps 10%, market 2% => rel 800 bps, passes.
    # coin B jumps 4%, market 2% => rel 200 bps, fails.
    rows = []
    test_time = pd.Timestamp("2026-01-01T12:00:00Z")

    examples = [
        ("AAA", 1000.0, 1100.0, 200.0),
        ("BBB", 1000.0, 1040.0, 200.0),
    ]

    for sym, prior_close, current_close, market_ret in examples:
        coin_ret = compute_coin_return_bps(current_close, prior_close)
        if rel_rule_pass(coin_ret, market_ret):
            rows.append(build_signal_row(sym, test_time, coin_ret, market_ret, current_close))

    capped = rank_and_cap_signals(rows)
    signal_csv = out_dir / "rel_extreme_shadow_adapter_self_test_signals.csv"
    heartbeat = out_dir / "rel_extreme_shadow_adapter_self_test_heartbeat.json"

    append_csv(signal_csv, capped)
    write_heartbeat(heartbeat, {{
        "self_test": True,
        "raw_signal_count": len(rows),
        "capped_signal_count": len(capped),
    }})

    result = {{
        "ok": len(capped) == 1 and capped[0]["symbol"] == "AAA",
        "raw_signal_count": len(rows),
        "capped_signal_count": len(capped),
        "signal_csv": str(signal_csv),
        "heartbeat_json": str(heartbeat),
        "live_allowed": False,
        "active_paper_allowed": False,
    }}

    (out_dir / "rel_extreme_shadow_adapter_self_test_result.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result

def main():
    ap = argparse.ArgumentParser(description="Rel extreme shadow adapter core. Self-test only unless future runtime uses it.")
    ap.add_argument("--self_test", action="store_true")
    ap.add_argument("--out_dir", default="rel_extreme_shadow_adapter_self_test")
    args = ap.parse_args()

    if args.self_test:
        result = self_test(Path(args.out_dir))
        print("REL EXTREME SHADOW ADAPTER SELF TEST")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result.get("ok") else 1)

    print("This adapter is sandbox/shadow core only. Use --self_test for validation.")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("shadow_start_allowed_by_this_file: False")

if __name__ == "__main__":
    main()
'''

    adapter_path.write_text(adapter_code, encoding="utf-8")

    ok, err = compile_ok(adapter_path)

    self_test_dir = out_dir / "self_test"
    import subprocess, sys
    proc = subprocess.run(
        [sys.executable, str(adapter_path), "--self_test", "--out_dir", str(self_test_dir)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    self_test_ok = proc.returncode == 0

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "candidate": CANDIDATE,
        "builder_status": "REL_EXTREME_SHADOW_ADAPTER_WRITTEN_NOT_APPROVED_TO_RUN",
        "adapter_path": str(adapter_path),
        "spec_path": str(spec_path),
        "adapter_compiles": ok,
        "compile_error": err,
        "self_test_ok": self_test_ok,
        "self_test_stdout": proc.stdout[-3000:],
        "self_test_stderr": proc.stderr[-3000:],
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_REL_EXTREME_ADAPTER_IMPLEMENTATION_AUDITOR",
    }

    write_json(out_dir / "rel_extreme_shadow_adapter_manifest.json", manifest)

    print("EDGE FACTORY REL EXTREME SHADOW LOGGER ADAPTER BUILDER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"adapter_path: {adapter_path}")
    print(f"adapter_compiles: {ok}")
    print(f"self_test_ok: {self_test_ok}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    if not ok:
        print("COMPILE ERROR")
        print(err)
    if proc.stdout:
        print("SELF TEST STDOUT")
        print("-" * 100)
        print(proc.stdout)
    if proc.stderr:
        print("SELF TEST STDERR")
        print("-" * 100)
        print(proc.stderr)
    print(f"Manifest: {out_dir / 'rel_extreme_shadow_adapter_manifest.json'}")
    print(f"Adapter : {adapter_path}")

if __name__ == "__main__":
    main()
