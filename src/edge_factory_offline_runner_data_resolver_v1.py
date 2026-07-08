#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
MASTER = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
OUT_ROOT = WORKSPACE / "edge_factory_offline_runner_data_resolver_v1"

EXCLUDE_DIR_PARTS = {
    "paper_run_gate_MASTER_UPPER_SYSTEM",
    "paper_run_shadow_rel_extreme_reversion_short",
    "edge_factory_os_autopilot_loop_v1",
    "edge_factory_os_autopilot_loop_v2",
    "edge_factory_os_autopilot_loop_v3",
    "edge_factory_os_autopilot_loop_v4",
    "edge_factory_os_command_center_v1",
    "edge_factory_os_state_index_v1",
    "edge_factory_os_state_index_v2",
    "edge_factory_os_recovery_manifest_v1",
    "edge_factory_os_recovery_manifest_v2",
}

DERIVED_FEATURE_RULES = {
    "coin_ret3_bps": "derive from close: 3h pct change * 10000 per symbol",
    "coin_ret6_bps": "derive from close: 6h pct change * 10000 per symbol",
    "coin_ret12_bps": "derive from close: 12h pct change * 10000 per symbol",
    "coin_ret24_bps": "derive from close: 24h pct change * 10000 per symbol",
    "mkt_ret3_bps": "derive from market median close index: 3h pct change * 10000",
    "mkt_ret6_bps": "derive from market median close index: 6h pct change * 10000",
    "mkt_ret12_bps": "derive from market median close index: 12h pct change * 10000",
    "mkt_ret24_bps": "derive from market median close index: 24h pct change * 10000",
    "rel_ret_bps": "derive as coin_ret_window_bps - mkt_ret_window_bps",
    "entry_range_bps": "derive from high/low/close if high and low available",
    "entry_vol_quote": "derive or map from volCcyQuote / volume quote column",
}

COLUMN_ALIASES = {
    "symbol": ["symbol", "coin", "instId", "inst_id", "instrument", "ticker"],
    "time": ["time", "timestamp", "datetime", "entry_time", "ts"],
    "close": ["close", "c", "close_price", "last"],
    "high": ["high", "h"],
    "low": ["low", "l"],
    "volCcyQuote": ["volCcyQuote", "vol_ccy_quote", "quote_volume", "volume_quote", "turnover"],
    "entry_vol_quote": ["entry_vol_quote", "volCcyQuote", "quote_volume", "volume_quote", "turnover"],
}

def latest_request() -> Path | None:
    root = WORKSPACE / "edge_factory_contract_to_runner_adapter_v1"
    files = list(root.rglob("offline_runner_request_v1.json"))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIR_PARTS)

def get_csv_columns(path: Path) -> list[str]:
    try:
        return list(pd.read_csv(path, nrows=5).columns)
    except Exception:
        return []

def get_parquet_columns(path: Path) -> list[str]:
    try:
        import pyarrow.parquet as pq
        return list(pq.ParquetFile(path).schema.names)
    except Exception:
        try:
            return list(pd.read_parquet(path).head(1).columns)
        except Exception:
            return []

def get_columns(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return get_csv_columns(path)
    if suffix == ".parquet":
        return get_parquet_columns(path)
    return []

def normalize_cols(cols: list[str]) -> dict[str, str]:
    return {str(c).lower(): str(c) for c in cols}

def has_column_or_alias(required: str, cols: list[str]) -> tuple[bool, str | None]:
    colmap = normalize_cols(cols)
    if required.lower() in colmap:
        return True, colmap[required.lower()]

    for alias in COLUMN_ALIASES.get(required, []):
        if alias.lower() in colmap:
            return True, colmap[alias.lower()]

    return False, None

def scan_files(max_files: int) -> list[dict[str, Any]]:
    candidates = []
    seen = 0

    for root, dirs, files in os.walk(WORKSPACE):
        root_path = Path(root)
        if is_excluded(root_path):
            dirs[:] = []
            continue

        for name in files:
            if not (name.lower().endswith(".csv") or name.lower().endswith(".parquet")):
                continue

            p = root_path / name

            # Avoid scanning huge generated logs first unless needed.
            if is_excluded(p):
                continue

            seen += 1
            if seen > max_files:
                break

            cols = get_columns(p)
            if not cols:
                continue

            try:
                size_mb = round(p.stat().st_size / (1024 * 1024), 3)
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
            except Exception:
                size_mb = None
                mtime = None

            candidates.append({
                "path": str(p),
                "suffix": p.suffix.lower(),
                "size_mb": size_mb,
                "mtime_utc": mtime,
                "columns": cols,
            })

        if seen > max_files:
            break

    return candidates

def score_file(file_info: dict[str, Any], required: list[str]) -> dict[str, Any]:
    cols = file_info["columns"]

    direct_or_alias = []
    missing = []
    derivable = []

    for r in required:
        has, actual = has_column_or_alias(r, cols)
        if has:
            direct_or_alias.append({"required": r, "actual": actual})
        elif r in DERIVED_FEATURE_RULES:
            derivable.append({"required": r, "rule": DERIVED_FEATURE_RULES[r]})
        else:
            missing.append(r)

    score = len(direct_or_alias) * 10 + len(derivable) * 4 - len(missing) * 8

    return {
        "path": file_info["path"],
        "suffix": file_info["suffix"],
        "size_mb": file_info["size_mb"],
        "mtime_utc": file_info["mtime_utc"],
        "score": score,
        "direct_or_alias_count": len(direct_or_alias),
        "derivable_count": len(derivable),
        "missing_count": len(missing),
        "direct_or_alias": direct_or_alias,
        "derivable": derivable,
        "missing": missing,
        "columns_sample": file_info["columns"][:80],
    }

def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve source files for an offline runner request.")
    ap.add_argument("--request", default="")
    ap.add_argument("--max_files", type=int, default=600)
    args = ap.parse_args()

    request_path = Path(args.request) if args.request else latest_request()

    out_dir = OUT_ROOT / f"offline_runner_data_resolver_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    req = read_json(request_path)
    required = req.get("required_columns", []) if isinstance(req.get("required_columns"), list) else []

    blockers = []
    if not request_path or not request_path.exists():
        blockers.append("RUNNER_REQUEST_NOT_FOUND")
    if "__read_error__" in req:
        blockers.append("RUNNER_REQUEST_READ_ERROR")
    if not required:
        blockers.append("REQUIRED_COLUMNS_MISSING")

    file_infos = [] if blockers else scan_files(args.max_files)
    scored = [score_file(x, required) for x in file_infos]
    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    top = scored[0] if scored else None

    all_required_direct = top is not None and top["missing_count"] == 0 and top["derivable_count"] == 0
    all_required_covered_or_derivable = top is not None and top["missing_count"] == 0

    resolved_request = None
    resolved_request_path = ""

    if blockers:
        resolver_status = "DATA_RESOLVER_BLOCKED"
        next_action = "FIX_RUNNER_REQUEST"
        runner_execution_allowed = False
    elif all_required_direct:
        resolver_status = "DATA_RESOLVER_PASS_DIRECT_SOURCE_READY"
        next_action = "RUN_PREFLIGHT_ON_RESOLVED_REQUEST"
        runner_execution_allowed = False
    elif all_required_covered_or_derivable:
        resolver_status = "DATA_RESOLVER_ATTENTION_FEATURE_BUILD_REQUIRED"
        next_action = "BUILD_FEATURE_PANEL_FROM_SOURCE_BEFORE_RUNNER"
        runner_execution_allowed = False
    elif top:
        resolver_status = "DATA_RESOLVER_ATTENTION_INSUFFICIENT_SOURCE_COVERAGE"
        next_action = "ADD_SOURCE_FILES_OR_FEATURE_BUILDER_SPEC"
        runner_execution_allowed = False
    else:
        resolver_status = "DATA_RESOLVER_NO_CANDIDATE_FILES_FOUND"
        next_action = "ADD_DATA_SOURCE_PATHS"
        runner_execution_allowed = False

    if top and not blockers:
        resolved_request = dict(req)
        resolved_request["source_files"] = [top["path"]]
        resolved_request["data_resolution"] = {
            "resolver_version": "offline_runner_data_resolver_v1",
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "source_file": top["path"],
            "direct_or_alias": top["direct_or_alias"],
            "derivable": top["derivable"],
            "missing": top["missing"],
            "resolver_status": resolver_status,
            "runner_execution_allowed": runner_execution_allowed,
        }
        resolved_request_path = str(out_dir / "offline_runner_request_v1_resolved.json")
        Path(resolved_request_path).write_text(json.dumps(resolved_request, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "request_path": str(request_path) if request_path else None,
        "candidate_key": req.get("candidate_key"),
        "family_key": req.get("family_key"),
        "required_columns": required,
        "resolver_status": resolver_status,
        "next_action": next_action,
        "runner_execution_allowed": runner_execution_allowed,
        "blockers": blockers,
        "files_scanned_with_columns": len(file_infos),
        "top_source": top,
        "resolved_request_path": resolved_request_path,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Resolver only scans local files and writes resolution artifacts.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading."
        ],
    }

    state_path = out_dir / "offline_runner_data_resolver_v1_state.json"
    ranked_path = out_dir / "offline_runner_data_resolver_v1_ranked_sources.json"
    csv_path = out_dir / "offline_runner_data_resolver_v1_ranked_sources.csv"
    report_path = out_dir / "offline_runner_data_resolver_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    ranked_path.write_text(json.dumps(scored[:100], indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(scored[:100]).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory Offline Runner Data Resolver v1")
    md.append("")
    md.append(f"Status: `{resolver_status}`")
    md.append(f"Candidate: `{req.get('candidate_key')}`")
    md.append(f"Files scanned: `{len(file_infos)}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    if top:
        md.append("## Top source")
        md.append(f"- `{top['path']}`")
        md.append(f"- direct/alias: `{top['direct_or_alias_count']}`")
        md.append(f"- derivable: `{top['derivable_count']}`")
        md.append(f"- missing: `{top['missing_count']}`")
    md.append("")
    md.append("## Safety")
    md.append("- runner_execution_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE RUNNER DATA RESOLVER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"request   : {request_path}")
    print(f"candidate : {req.get('candidate_key')}")
    print(f"resolver_status: {resolver_status}")
    print(f"files_scanned_with_columns: {len(file_infos)}")
    print(f"runner_execution_allowed: {runner_execution_allowed}")
    print(f"next_action: {next_action}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("TOP SOURCES")
    print("-" * 100)
    if scored:
        df = pd.DataFrame(scored[:20])
        print(df[["score","direct_or_alias_count","derivable_count","missing_count","path"]].to_string(index=False))
    else:
        print("No scored sources.")
    print()
    if top:
        print("TOP SOURCE DETAILS")
        print("-" * 100)
        print("path:", top["path"])
        print("direct_or_alias:", top["direct_or_alias"])
        print("derivable:", top["derivable"])
        print("missing:", top["missing"])
    print()
    print(f"State   : {state_path}")
    print(f"Ranked  : {ranked_path}")
    print(f"CSV     : {csv_path}")
    print(f"Report  : {report_path}")
    if resolved_request_path:
        print(f"ResolvedRequest: {resolved_request_path}")

if __name__ == "__main__":
    main()
