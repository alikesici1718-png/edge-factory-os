#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_learning_aware_offline_candidate_pipeline_v1"

IDEA_LEDGER = WORKSPACE / "edge_factory_candidate_idea_bank_v1" / "candidate_idea_bank_master_ledger.jsonl"
SELECTOR_ROOT = WORKSPACE / "edge_factory_learning_aware_candidate_selector_v1"

GENERATOR = USERDIR / "edge_factory_candidate_contract_generator_v1.py"
ARTIFACT_PLANNER = USERDIR / "edge_factory_candidate_contract_artifact_planner_v1.py"
VALIDATOR = USERDIR / "edge_factory_offline_experiment_contract_validator_v1.py"
ADAPTER = USERDIR / "edge_factory_contract_to_runner_adapter_v1.py"
DATA_BINDING = USERDIR / "edge_factory_offline_runner_data_source_binding_v1.py"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def latest_file(root: Path, pattern: str, contains: str | None = None) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if contains:
        files = [p for p in files if contains.lower() in str(p).lower()]
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def run_py(script: Path, args: list[str]) -> dict[str, Any]:
    try:
        p = subprocess.run(
            [sys.executable, str(script)] + args,
            capture_output=True,
            text=True,
            timeout=900,
        )
        return {
            "script": str(script),
            "args": args,
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout_tail": p.stdout[-6000:],
            "stderr_tail": p.stderr[-3000:],
        }
    except Exception as e:
        return {
            "script": str(script),
            "args": args,
            "ok": False,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": repr(e),
        }

def latest_selector_state() -> dict[str, Any]:
    p = latest_file(SELECTOR_ROOT, "learning_aware_candidate_selector_v1_state.json")
    return read_json(p)

def split_csv(x: str) -> list[str]:
    return [a.strip() for a in str(x or "").split(",") if a.strip()]

def parse_windows(required_cols: list[str]) -> list[int]:
    windows = set()
    for c in required_cols:
        m = re.match(r"^(?:coin|mkt)_ret(\d+)_bps$", c)
        if m:
            windows.add(int(m.group(1)))
    return sorted(windows)

def infer_symbol(path: Path) -> str:
    name = path.name.upper()
    m = re.search(r"([A-Z0-9]+)-USDT-SWAP", name)
    if m:
        return m.group(1)
    return path.parent.parent.parent.name.upper()

def parse_time_series(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        clean = pd.to_numeric(s, errors="coerce").dropna()
        if len(clean):
            med = float(clean.median())
            if med > 1e12:
                return pd.to_datetime(s, unit="ms", utc=True, errors="coerce")
            if med > 1e9:
                return pd.to_datetime(s, unit="s", utc=True, errors="coerce")
    return pd.to_datetime(s, utc=True, errors="coerce")

def normalize_1m_file(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = ["time", "open", "high", "low", "close", "volCcyQuote"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns {missing}")

    symbol = infer_symbol(path)
    out = df[required].copy()
    out["time"] = parse_time_series(out["time"])

    for c in ["open", "high", "low", "close", "volCcyQuote"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out.dropna(subset=["time", "open", "high", "low", "close"])
    out = out.sort_values("time")
    out = out.drop_duplicates(subset=["time"], keep="last")
    out["symbol"] = symbol
    return out

def resample_to_1h(df_1m: pd.DataFrame) -> pd.DataFrame:
    symbol = str(df_1m["symbol"].iloc[0])
    x = df_1m.set_index("time").sort_index()

    h = x.resample("1h").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volCcyQuote": "sum",
    })

    h = h.dropna(subset=["open", "high", "low", "close"])
    h = h.reset_index()
    h["symbol"] = symbol
    h = h.rename(columns={"volCcyQuote": "entry_vol_quote"})
    h["entry_range_bps"] = ((h["high"] - h["low"]) / h["close"]) * 10000.0
    return h[["time", "symbol", "open", "high", "low", "close", "entry_vol_quote", "entry_range_bps"]]

def write_parquet_or_csv(df: pd.DataFrame, parquet_path: Path, csv_path: Path) -> tuple[str, bool]:
    try:
        df.to_parquet(parquet_path, index=False)
        return str(parquet_path), True
    except Exception:
        df.to_csv(csv_path, index=False)
        return str(csv_path), False

def build_generic_feature_panel(candidate_key: str, bound_request_path: Path, run_dir: Path) -> dict[str, Any]:
    req = read_json(bound_request_path)
    source_files = req.get("source_files", [])
    required_cols = req.get("required_columns", [])
    windows = parse_windows(required_cols)

    output_root = WORKSPACE / "edge_factory_feature_panels" / str(candidate_key)
    hourly_root = output_root / "hourly_by_symbol_dynamic"
    output_root.mkdir(parents=True, exist_ok=True)
    hourly_root.mkdir(parents=True, exist_ok=True)

    audit_rows = []
    hourly_paths = []

    for i, raw_path in enumerate(source_files, start=1):
        p = Path(raw_path)
        symbol = infer_symbol(p)
        try:
            raw = normalize_1m_file(p)
            hourly = resample_to_1h(raw)

            sym_parquet = hourly_root / f"{symbol}_1h.parquet"
            sym_csv = hourly_root / f"{symbol}_1h.csv"
            written_path, wrote_parquet = write_parquet_or_csv(hourly, sym_parquet, sym_csv)
            hourly_paths.append(written_path)

            audit_rows.append({
                "symbol": symbol,
                "path": str(p),
                "ok": True,
                "raw_rows": int(len(raw)),
                "hourly_rows": int(len(hourly)),
                "first_time": str(hourly["time"].min()) if len(hourly) else "",
                "last_time": str(hourly["time"].max()) if len(hourly) else "",
                "written_path": written_path,
                "error": "",
            })

            if i % 25 == 0:
                print(f"[feature_build] processed {i}/{len(source_files)} symbols")
        except Exception as e:
            audit_rows.append({
                "symbol": symbol,
                "path": str(p),
                "ok": False,
                "raw_rows": 0,
                "hourly_rows": 0,
                "first_time": "",
                "last_time": "",
                "written_path": "",
                "error": repr(e),
            })

    hourly_parts = []
    for hp in hourly_paths:
        hp_path = Path(hp)
        try:
            if hp_path.suffix.lower() == ".parquet":
                hourly_parts.append(pd.read_parquet(hp_path))
            else:
                hourly_parts.append(pd.read_csv(hp_path))
        except Exception as e:
            audit_rows.append({
                "symbol": hp_path.stem,
                "path": hp,
                "ok": False,
                "error": f"read_hourly_failed:{repr(e)}",
            })

    if not hourly_parts:
        return {
            "status": "FEATURE_PANEL_DYNAMIC_BUILD_NO_HOURLY_PARTS",
            "panel_path": "",
            "manifest_path": "",
            "audit_csv": "",
            "panel_rows": 0,
            "panel_symbols": 0,
            "failed_file_count": len([r for r in audit_rows if not r.get("ok")]),
            "windows": windows,
        }

    panel = pd.concat(hourly_parts, ignore_index=True)
    panel["time"] = pd.to_datetime(panel["time"], utc=True, errors="coerce")
    panel = panel.dropna(subset=["time", "symbol", "close"])
    panel = panel.sort_values(["symbol", "time"])

    for w in windows:
        panel[f"coin_ret{w}_bps"] = panel.groupby("symbol")["close"].pct_change(w) * 10000.0

    close_wide = panel.pivot(index="time", columns="symbol", values="close").sort_index()
    market_index = close_wide.median(axis=1, skipna=True)

    mkt = pd.DataFrame({
        "time": market_index.index,
        "mkt_close_median": market_index.values,
    })

    for w in windows:
        mkt[f"mkt_ret{w}_bps"] = mkt["mkt_close_median"].pct_change(w) * 10000.0

    merge_cols = ["time"] + [f"mkt_ret{w}_bps" for w in windows]
    panel = panel.merge(mkt[merge_cols], on="time", how="left")

    final_parquet = output_root / f"{candidate_key}_feature_panel_1h_dynamic.parquet"
    final_csv = output_root / f"{candidate_key}_feature_panel_1h_dynamic.csv"
    final_path, final_is_parquet = write_parquet_or_csv(panel, final_parquet, final_csv)

    audit_csv = run_dir / f"{candidate_key}_feature_panel_dynamic_file_audit.csv"
    pd.DataFrame(audit_rows).to_csv(audit_csv, index=False)

    missing_output_cols = [c for c in required_cols if c not in panel.columns]
    non_null_summary = {}
    for c in ["time", "symbol", "open", "high", "low", "close", "entry_vol_quote", "entry_range_bps"] + required_cols:
        if c in panel.columns:
            non_null_summary[c] = int(panel[c].notna().sum())

    manifest = {
        "manifest_version": "edge_factory_dynamic_feature_panel_manifest_v1",
        "created_at": now_iso(),
        "candidate_key": candidate_key,
        "source_file_count": len(source_files),
        "processed_symbol_count": int(panel["symbol"].nunique()),
        "panel_rows": int(len(panel)),
        "first_time": str(panel["time"].min()),
        "last_time": str(panel["time"].max()),
        "feature_panel_path": final_path,
        "final_is_parquet": final_is_parquet,
        "windows": windows,
        "required_columns": required_cols,
        "missing_output_cols": missing_output_cols,
        "non_null_summary": non_null_summary,
        "failed_file_count": len([r for r in audit_rows if not r.get("ok")]),
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
    }

    manifest_path = output_root / f"{candidate_key}_feature_panel_dynamic_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    if missing_output_cols:
        status = "FEATURE_PANEL_DYNAMIC_BUILD_MISSING_OUTPUT_COLUMNS"
    elif manifest["failed_file_count"] > 0:
        status = "FEATURE_PANEL_DYNAMIC_BUILD_PASS_WITH_FILE_WARNINGS"
    else:
        status = "FEATURE_PANEL_DYNAMIC_BUILD_PASS"

    return {
        "status": status,
        "panel_path": final_path,
        "manifest_path": str(manifest_path),
        "audit_csv": str(audit_csv),
        "panel_rows": int(len(panel)),
        "panel_symbols": int(panel["symbol"].nunique()),
        "first_time": str(panel["time"].min()),
        "last_time": str(panel["time"].max()),
        "failed_file_count": manifest["failed_file_count"],
        "missing_output_cols": missing_output_cols,
        "non_null_summary": non_null_summary,
        "windows": windows,
    }

def audit_generic_panel(panel_path: Path, required_cols: list[str]) -> dict[str, Any]:
    if panel_path.suffix.lower() == ".parquet":
        df = pd.read_parquet(panel_path)
    else:
        df = pd.read_csv(panel_path)

    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")

    missing = [c for c in required_cols if c not in df.columns]
    duplicate_count = int(df.duplicated(subset=["time", "symbol"]).sum())
    symbol_count = int(df["symbol"].nunique())
    row_count = int(len(df))

    numeric_cols = [c for c in df.columns if c not in {"time", "symbol"}]
    inf_counts = {}
    nan_ratios = {}
    for c in numeric_cols:
        s = pd.to_numeric(df[c], errors="coerce")
        inf_counts[c] = int(np.isinf(s).sum())
        nan_ratios[c] = float(s.isna().mean())

    critical = []
    attention = []

    if missing:
        critical.append(f"missing_required_cols:{missing}")
    if duplicate_count != 0:
        critical.append(f"duplicates:{duplicate_count}")
    if symbol_count < 200:
        critical.append(f"symbol_count_low:{symbol_count}")
    if row_count < 1_000_000:
        critical.append(f"row_count_low:{row_count}")
    if sum(inf_counts.values()) != 0:
        critical.append(f"inf_values:{inf_counts}")

    for c in required_cols:
        if c in nan_ratios and nan_ratios[c] > 0.02:
            attention.append(f"nan_ratio_high:{c}:{nan_ratios[c]}")

    if critical:
        status = "GENERIC_PANEL_QUALITY_CRITICAL_FAIL"
        allowed = False
    elif attention:
        status = "GENERIC_PANEL_QUALITY_PASS_WITH_WARNINGS"
        allowed = True
    else:
        status = "GENERIC_PANEL_QUALITY_PASS"
        allowed = True

    return {
        "status": status,
        "allowed": allowed,
        "row_count": row_count,
        "symbol_count": symbol_count,
        "duplicate_count": duplicate_count,
        "missing_required_cols": missing,
        "inf_total": sum(inf_counts.values()),
        "nan_ratios_required": {c: nan_ratios.get(c) for c in required_cols if c in nan_ratios},
        "critical": critical,
        "attention": attention,
    }

def selftest_selected_candidate(candidate_key: str, family_key: str, idea: dict[str, Any], panel_path: Path, run_dir: Path) -> dict[str, Any]:
    if panel_path.suffix.lower() == ".parquet":
        df = pd.read_parquet(panel_path)
    else:
        df = pd.read_csv(panel_path)

    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df = df.dropna(subset=["time", "symbol", "close"])
    df = df.sort_values(["symbol", "time"])

    # Bounded but broad self-test: recent 250k rows like prior controller.
    if len(df) > 250_000:
        df = df.sort_values("time").tail(250_000).sort_values(["symbol", "time"])

    required = split_csv(idea.get("required_columns", ""))
    for c in required:
        if c in df.columns and c not in {"symbol", "time"}:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    liq_series = pd.to_numeric(df["entry_vol_quote"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    liquidity_floor = float(liq_series.quantile(0.50)) if len(liq_series) else 0.0

    # Current selected candidate: post_impulse_drift_long_v1
    if candidate_key == "post_impulse_drift_long_v1":
        mask = (
            (df["coin_ret3_bps"] >= 250.0) &
            (df["mkt_ret3_bps"] >= 50.0) &
            (df["entry_vol_quote"] >= liquidity_floor)
        )
        hold_hours = 6
        side = "long"
    else:
        return {
            "status": "SELFTEST_UNSUPPORTED_CANDIDATE_RULE",
            "summary": {},
            "trades_csv": "",
            "blockers": ["unsupported_candidate_rule"],
        }

    signals = df.loc[mask, ["time", "symbol", "close", "entry_vol_quote"] + [c for c in required if c in df.columns and c not in {"time","symbol","close","entry_vol_quote"}]].copy()
    signals = signals.sort_values(["time", "symbol"]).head(10000)

    future = df[["time", "symbol", "close"]].copy()
    future = future.sort_values(["symbol", "time"])
    future["exit_time"] = future.groupby("symbol")["time"].shift(-hold_hours)
    future["exit_close"] = future.groupby("symbol")["close"].shift(-hold_hours)

    trades = signals.merge(
        future[["time", "symbol", "exit_time", "exit_close"]],
        on=["time", "symbol"],
        how="left",
    ).dropna(subset=["exit_time", "exit_close"]).copy()

    total_cost_bps = 25.0
    trades["candidate_key"] = candidate_key
    trades["family_key"] = family_key
    trades["side"] = side
    trades["entry_time"] = trades["time"]
    trades["entry_price"] = trades["close"]
    trades["raw_ret_bps"] = ((trades["exit_close"] / trades["entry_price"]) - 1.0) * 10000.0
    trades["cost_bps"] = total_cost_bps
    trades["net_ret_bps"] = trades["raw_ret_bps"] - total_cost_bps

    trades_csv = run_dir / f"{candidate_key}_selftest_trades.csv"
    trades.to_csv(trades_csv, index=False)

    if len(trades) == 0:
        return {
            "status": "OFFLINE_PIPELINE_SELFTEST_NO_CLOSED_TRADES",
            "summary": {
                "liquidity_floor": liquidity_floor,
                "signal_count": int(len(signals)),
                "closed_selftest_trades": 0,
            },
            "trades_csv": str(trades_csv),
            "blockers": [],
        }

    gross_profit = float(trades.loc[trades["net_ret_bps"] > 0, "net_ret_bps"].sum())
    gross_loss = float(-trades.loc[trades["net_ret_bps"] < 0, "net_ret_bps"].sum())
    pf = gross_profit / gross_loss if gross_loss > 0 else None

    summary = {
        "liquidity_floor": liquidity_floor,
        "tested_rows": int(len(df)),
        "tested_symbols": int(df["symbol"].nunique()),
        "signal_count": int(len(signals)),
        "closed_selftest_trades": int(len(trades)),
        "trade_symbol_count": int(trades["symbol"].nunique()),
        "win_rate": float((trades["net_ret_bps"] > 0).mean()),
        "mean_net_ret_bps": float(trades["net_ret_bps"].mean()),
        "median_net_ret_bps": float(trades["net_ret_bps"].median()),
        "profit_factor": pf,
        "total_cost_bps": total_cost_bps,
    }

    if summary["closed_selftest_trades"] < 50:
        status = "OFFLINE_PIPELINE_SELFTEST_LOW_SAMPLE"
    elif pf is not None and pf >= 1.05 and summary["mean_net_ret_bps"] > 0:
        status = "OFFLINE_PIPELINE_SELFTEST_PASS_PROMISING"
    elif pf is not None and pf < 0.75 and summary["mean_net_ret_bps"] < -25 and summary["median_net_ret_bps"] < 0:
        status = "OFFLINE_PIPELINE_SELFTEST_NEGATIVE_BLOCK_FULL_RUN"
    else:
        status = "OFFLINE_PIPELINE_SELFTEST_WEAK_OR_MIXED"

    return {
        "status": status,
        "summary": summary,
        "trades_csv": str(trades_csv),
        "blockers": [],
    }

def main() -> int:
    run_dir = OUT_ROOT / f"learning_aware_offline_pipeline_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    selector = latest_selector_state()
    top = selector.get("top_candidate") or {}

    candidate_key = top.get("candidate_key")
    if not candidate_key:
        state = {
            "pipeline_status": "PIPELINE_BLOCKED_NO_SELECTED_CANDIDATE",
            "blockers": ["no_top_candidate"],
            "generated_at": now_iso(),
        }
        state_path = run_dir / "learning_aware_offline_pipeline_v1_state.json"
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return

    ideas = read_jsonl(IDEA_LEDGER)
    idea = None
    for x in ideas:
        if x.get("candidate_key") == candidate_key:
            idea = x
            break

    if not idea:
        state = {
            "pipeline_status": "PIPELINE_BLOCKED_IDEA_NOT_FOUND",
            "candidate_key": candidate_key,
            "blockers": ["idea_not_found"],
            "generated_at": now_iso(),
        }
        state_path = run_dir / "learning_aware_offline_pipeline_v1_state.json"
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return

    family_key = idea.get("family_key", "")
    required_columns = split_csv(idea.get("required_columns", ""))

    steps = []
    blockers = []

    # 1. Contract generator
    gen_args = [
        "--candidate_key", candidate_key,
        "--family_key", family_key,
        "--side", str(idea.get("side", "long")),
        "--edge", str(idea.get("edge", "")),
        "--regime", str(idea.get("regime", "")),
        "--why", str(idea.get("why", "")),
        "--failure_modes", str(idea.get("failure_modes", "")),
        "--universe", str(idea.get("universe", "OKX USDT swaps ready universe")),
        "--timeframe", str(idea.get("timeframe", "1h candles")),
        "--lookback_window", str(idea.get("lookback_window", "")),
        "--source_files", "AUTO_DISCOVER_FROM_WORKSPACE",
        "--required_columns", str(idea.get("required_columns", "")),
        "--entry_rule", str(idea.get("entry_rule", "")),
        "--exit_rule", str(idea.get("exit_rule", "")),
        "--hold_time", str(idea.get("hold_time", "")),
        "--cooldown", str(idea.get("cooldown", "")),
        "--in_sample_period", "AUTO_SPLIT_REQUIRED",
        "--out_of_sample_period", "AUTO_SPLIT_REQUIRED",
        "--max_drawdown_proxy", "0",
    ]
    r = run_py(GENERATOR, gen_args)
    steps.append({"step": "contract_generator", **r})
    if not r["ok"]:
        blockers.append("contract_generator_failed")

    contract_path = latest_file(WORKSPACE / "edge_factory_candidate_contract_generator_v1", "*_offline_experiment_contract_v1.json", contains=candidate_key)

    # 2. Artifact planner
    if contract_path and not blockers:
        r = run_py(ARTIFACT_PLANNER, ["--contract", str(contract_path)])
        steps.append({"step": "artifact_planner", **r})
        if not r["ok"]:
            blockers.append("artifact_planner_failed")
    else:
        blockers.append("contract_path_missing")

    completed_contract = latest_file(WORKSPACE / "edge_factory_candidate_contract_artifact_planner_v1", "*_offline_experiment_contract_v1_completed.json", contains=candidate_key)

    # 3. Validator
    if completed_contract and not any(b.endswith("_failed") for b in blockers):
        r = run_py(VALIDATOR, ["--contract", str(completed_contract)])
        steps.append({"step": "validator", **r})
        if not r["ok"]:
            blockers.append("validator_failed")
    else:
        blockers.append("completed_contract_missing")

    validator_state = latest_file(WORKSPACE / "edge_factory_offline_experiment_contract_validator_v1", "offline_experiment_contract_validator_v1_state.json")
    validator = read_json(validator_state)
    if validator.get("validation_status") != "CONTRACT_VALID_READY_FOR_OFFLINE_TESTING" or validator.get("candidate_key") != candidate_key:
        blockers.append(f"validator_not_ready:{validator.get('validation_status')}:{validator.get('candidate_key')}")

    # 4. Adapter
    if completed_contract and not blockers:
        r = run_py(ADAPTER, ["--contract", str(completed_contract)])
        steps.append({"step": "contract_to_runner_adapter", **r})
        if not r["ok"]:
            blockers.append("adapter_failed")

    runner_request = latest_file(WORKSPACE / "edge_factory_contract_to_runner_adapter_v1", "offline_runner_request_v1.json")

    # 5. Data binding
    if runner_request and not blockers:
        r = run_py(DATA_BINDING, ["--request", str(runner_request)])
        steps.append({"step": "data_source_binding", **r})
        if not r["ok"]:
            blockers.append("data_binding_failed")

    bound_request = latest_file(WORKSPACE / "edge_factory_offline_runner_data_source_binding_v1", "offline_runner_request_v1_data_bound.json")

    # 6. Generic feature panel build
    feature_build = {}
    if bound_request and not blockers:
        feature_build = build_generic_feature_panel(candidate_key, bound_request, run_dir)
        if feature_build["status"] not in {"FEATURE_PANEL_DYNAMIC_BUILD_PASS", "FEATURE_PANEL_DYNAMIC_BUILD_PASS_WITH_FILE_WARNINGS"}:
            blockers.append(f"feature_build_not_pass:{feature_build['status']}")
    else:
        blockers.append("bound_request_missing")

    # 7. Generic quality audit
    quality = {}
    if feature_build.get("panel_path") and not blockers:
        quality = audit_generic_panel(Path(feature_build["panel_path"]), required_columns)
        if not quality["allowed"]:
            blockers.append(f"generic_quality_not_allowed:{quality['status']}")

    # 8. Self-test
    selftest = {}
    if feature_build.get("panel_path") and quality.get("allowed") and not blockers:
        selftest = selftest_selected_candidate(candidate_key, family_key, idea, Path(feature_build["panel_path"]), run_dir)

    if blockers:
        pipeline_status = "LEARNING_AWARE_PIPELINE_BLOCKED"
        next_action = "FIX_BLOCKERS"
        full_run_allowed = False
    else:
        st = selftest.get("status")
        if st == "OFFLINE_PIPELINE_SELFTEST_PASS_PROMISING":
            pipeline_status = "LEARNING_AWARE_PIPELINE_PASS_PROMISING"
            next_action = "FULL_OFFLINE_RUNNER_CAN_BE_PLANNED"
            full_run_allowed = True
        elif st == "OFFLINE_PIPELINE_SELFTEST_NEGATIVE_BLOCK_FULL_RUN":
            pipeline_status = "LEARNING_AWARE_PIPELINE_NEGATIVE_SELFTEST_RECORDED"
            next_action = "RECORD_LEARNING_AND_SELECT_NEXT_CANDIDATE"
            full_run_allowed = False
        elif st in {"OFFLINE_PIPELINE_SELFTEST_WEAK_OR_MIXED", "OFFLINE_PIPELINE_SELFTEST_LOW_SAMPLE"}:
            pipeline_status = "LEARNING_AWARE_PIPELINE_WEAK_SELFTEST"
            next_action = "TRIAGE_OR_THRESHOLD_DIAGNOSTIC"
            full_run_allowed = False
        else:
            pipeline_status = "LEARNING_AWARE_PIPELINE_SELFTEST_NOT_PROMISING"
            next_action = "TRIAGE_RESULT"
            full_run_allowed = False

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "pipeline_status": pipeline_status,
        "candidate_key": candidate_key,
        "family_key": family_key,
        "blockers": blockers,
        "steps": steps,
        "contract_path": str(contract_path) if contract_path else "",
        "completed_contract": str(completed_contract) if completed_contract else "",
        "runner_request": str(runner_request) if runner_request else "",
        "bound_request": str(bound_request) if bound_request else "",
        "feature_build": feature_build,
        "quality": quality,
        "selftest": selftest,
        "next_action": next_action,
        "full_run_allowed": full_run_allowed,
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Offline candidate pipeline only.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop MASTER processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital.",
            "Does not create active paper family."
        ],
    }

    state_path = run_dir / "learning_aware_offline_candidate_pipeline_v1_state.json"
    report_path = run_dir / "learning_aware_offline_candidate_pipeline_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Learning-Aware Offline Candidate Pipeline v1")
    md.append("")
    md.append(f"Status: `{pipeline_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Family: `{family_key}`")
    md.append(f"Next action: `{next_action}`")
    md.append(f"Full run allowed: `{full_run_allowed}`")
    md.append("")
    md.append("## Feature build")
    md.append("```json")
    md.append(json.dumps(feature_build, indent=2, ensure_ascii=False, default=str)[:4000])
    md.append("```")
    md.append("")
    md.append("## Quality")
    md.append("```json")
    md.append(json.dumps(quality, indent=2, ensure_ascii=False, default=str)[:4000])
    md.append("```")
    md.append("")
    md.append("## Self-test")
    md.append("```json")
    md.append(json.dumps(selftest, indent=2, ensure_ascii=False, default=str)[:4000])
    md.append("```")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY LEARNING-AWARE OFFLINE CANDIDATE PIPELINE v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"run_dir   : {run_dir}")
    print(f"pipeline_status: {pipeline_status}")
    print(f"candidate : {candidate_key}")
    print(f"family    : {family_key}")
    print(f"blockers  : {blockers}")
    print(f"next_action: {next_action}")
    print(f"full_run_allowed: {full_run_allowed}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("FEATURE BUILD")
    print("-" * 100)
    print(json.dumps(feature_build, indent=2, ensure_ascii=False, default=str))
    print()
    print("QUALITY")
    print("-" * 100)
    print(json.dumps(quality, indent=2, ensure_ascii=False, default=str))
    print()
    print("SELFTEST")
    print("-" * 100)
    print(json.dumps(selftest, indent=2, ensure_ascii=False, default=str))
    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
