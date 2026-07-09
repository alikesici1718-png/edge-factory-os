#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code-generates the rel_extreme shadow runtime engine Python script (v1) from the adapter manifest, implementation audit, and spec review, embedding all rule parameters and sandbox-only safety flags directly into the generated file. Outputs the runtime engine script and a builder state JSON to the edge_factory_rel_extreme_shadow_runtime_engine_builder_v1 directory.
"""
from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

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

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def compile_ok(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, repr(e)

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_builder_v1" / f"rel_extreme_runtime_engine_builder_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    adapter_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_logger_adapter_builder_v1",
        "rel_extreme_adapter_builder_",
    )
    audit_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_adapter_implementation_auditor_v1",
        "rel_extreme_adapter_audit_",
    )
    spec_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_spec_review_v1",
        "rel_extreme_shadow_spec_",
    )

    manifest_path = adapter_dir / "rel_extreme_shadow_adapter_manifest.json" if adapter_dir else None
    audit_state_path = audit_dir / "rel_extreme_shadow_adapter_implementation_audit_state.json" if audit_dir else None
    spec_path = spec_dir / "rel_extreme_shadow_spec.json" if spec_dir else None

    manifest = read_json(manifest_path)
    audit_state = read_json(audit_state_path)
    spec = read_json(spec_path)

    adapter_path = Path(str(manifest.get("adapter_path", ""))) if manifest.get("adapter_path") else None

    if not adapter_path or not adapter_path.exists():
        raise SystemExit("adapter missing; run adapter builder first")
    if audit_state.get("implementation_audit_passed") is not True:
        raise SystemExit("adapter implementation audit has not passed")
    if spec.get("live_allowed") is not False or spec.get("active_paper_allowed") is not False:
        raise SystemExit("unsafe spec flags")

    engine_path = out_dir / "rel_extreme_shadow_runtime_engine.py"
    sandbox_root = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"

    engine_code = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ADAPTER_PATH = Path(r"{adapter_path}")
SANDBOX_ROOT_DEFAULT = Path(r"{sandbox_root}")

CANDIDATE_KEY = "rel_extreme_reversion_short"
SANDBOX_ONLY = True
LIVE_ALLOWED = False
ACTIVE_PAPER_ALLOWED = False
SHADOW_START_ALLOWED_BY_THIS_FILE = False
PRIVATE_EXCHANGE_API_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_adapter():
    spec = importlib.util.spec_from_file_location("rel_extreme_shadow_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import adapter: {{ADAPTER_PATH}}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")

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

def write_heartbeat(out_dir: Path, extra: dict[str, Any] | None = None) -> Path:
    hb = {{
        "candidate": CANDIDATE_KEY,
        "timestamp": utc_now_iso(),
        "sandbox_only": True,
        "live_allowed": False,
        "active_paper_allowed": False,
        "shadow_start_allowed_by_this_file": False,
        "private_exchange_api_allowed": False,
        "order_placement_allowed": False,
    }}
    if extra:
        hb.update(extra)
    p = out_dir / "rel_extreme_shadow_heartbeat.json"
    write_json(p, hb)
    return p

def self_test(out_dir: Path) -> dict[str, Any]:
    adapter = load_adapter()
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_rows = [
        adapter.build_signal_row("AAA", pd.Timestamp("2026-01-01T12:00:00Z"), 1000.0, 200.0, 1100.0),
        adapter.build_signal_row("BBB", pd.Timestamp("2026-01-01T12:00:00Z"), 900.0, 200.0, 1040.0),
        adapter.build_signal_row("CCC", pd.Timestamp("2026-01-01T12:00:00Z"), 800.0, 100.0, 1030.0),
    ]

    capped = adapter.rank_and_cap_signals(raw_rows)
    signals_csv = out_dir / "rel_extreme_shadow_signals.csv"
    closed_csv = out_dir / "rel_extreme_shadow_closed_trades.csv"

    append_csv(signals_csv, capped)

    closed_rows = []
    for r in capped:
        entry = float(r["entry_close"])
        # synthetic exit lower than entry for short win
        exit_close = entry * 0.97
        net_bps = adapter.compute_short_return_bps(entry, exit_close)
        closed_rows.append({{
            **r,
            "exit_close": exit_close,
            "net_return_bps": net_bps,
            "closed_at": utc_now_iso(),
            "runtime_mode": "self_test_shadow_runtime",
            "live_allowed": False,
            "active_paper_allowed": False,
        }})

    append_csv(closed_csv, closed_rows)

    heartbeat = write_heartbeat(out_dir, {{
        "runtime_mode": "self_test_shadow_runtime",
        "raw_signal_count": len(raw_rows),
        "capped_signal_count": len(capped),
        "closed_count": len(closed_rows),
    }})

    result = {{
        "ok": len(capped) == 1 and len(closed_rows) == 1,
        "raw_signal_count": len(raw_rows),
        "capped_signal_count": len(capped),
        "closed_count": len(closed_rows),
        "signals_csv": str(signals_csv),
        "closed_trades_csv": str(closed_csv),
        "heartbeat_json": str(heartbeat),
        "live_allowed": False,
        "active_paper_allowed": False,
    }}

    write_json(out_dir / "rel_extreme_shadow_runtime_self_test_result.json", result)
    return result

def main():
    ap = argparse.ArgumentParser(description="Rel extreme shadow runtime engine. Self-test/local shadow only.")
    ap.add_argument("--self_test", action="store_true")
    ap.add_argument("--out_dir", default=str(SANDBOX_ROOT_DEFAULT))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)

    if args.self_test:
        result = self_test(out_dir)
        print("REL EXTREME SHADOW RUNTIME ENGINE SELF TEST")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result.get("ok") else 1)

    print("Runtime engine exists but shadow start is not allowed by this file.")
    print("Run --self_test only until preflight + manual approval.")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("shadow_start_allowed_by_this_file: False")

if __name__ == "__main__":
    main()
'''

    engine_path.write_text(engine_code, encoding="utf-8")

    ok, err = compile_ok(engine_path)

    self_test_dir = out_dir / "self_test"
    proc = subprocess.run(
        [sys.executable, str(engine_path), "--self_test", "--out_dir", str(self_test_dir)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    self_test_result_path = self_test_dir / "rel_extreme_shadow_runtime_self_test_result.json"
    self_test_result = read_json(self_test_result_path)
    self_test_ok = proc.returncode == 0 and self_test_result.get("ok") is True

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "builder_status": "REL_EXTREME_SHADOW_RUNTIME_ENGINE_WRITTEN_NOT_APPROVED_TO_RUN",
        "runtime_engine_written": True,
        "runtime_engine_path": str(engine_path),
        "adapter_path": str(adapter_path),
        "adapter_audit_state": str(audit_state_path),
        "spec_path": str(spec_path),
        "engine_compiles": ok,
        "compile_error": err,
        "self_test_ok": self_test_ok,
        "self_test_stdout": proc.stdout[-3000:],
        "self_test_stderr": proc.stderr[-3000:],
        "self_test_result": self_test_result,
        "sandbox_root": str(sandbox_root),
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_REL_EXTREME_SHADOW_RUNTIME_ENGINE_AUDITOR",
    }

    write_json(out_dir / "rel_extreme_shadow_runtime_engine_builder_state.json", state)

    print("EDGE FACTORY REL EXTREME SHADOW RUNTIME ENGINE BUILDER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"runtime_engine_path: {engine_path}")
    print(f"engine_compiles: {ok}")
    print(f"self_test_ok: {self_test_ok}")
    print(f"sandbox_root: {sandbox_root}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if not ok:
        print()
        print("COMPILE ERROR")
        print(err)

    if proc.stdout:
        print()
        print("SELF TEST STDOUT")
        print("-" * 100)
        print(proc.stdout)
    if proc.stderr:
        print()
        print("SELF TEST STDERR")
        print("-" * 100)
        print(proc.stderr)

    print()
    print(f"State : {out_dir / 'rel_extreme_shadow_runtime_engine_builder_state.json'}")
    print(f"Engine: {engine_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
