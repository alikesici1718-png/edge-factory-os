#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default

def find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    lower = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    for col in df.columns:
        cl = str(col).lower()
        for c in candidates:
            if c.lower() in cl:
                return col
    return None

def load_failed_families() -> tuple[Path, pd.DataFrame]:
    d = latest_dir(WORKSPACE / "edge_factory_active_family_robustness_refresh_v2", "active_family_refresh_v2_")
    if not d:
        raise SystemExit("active family refresh v2 output not found")

    p = d / "active_family_robustness_refresh_v2_summary.csv"
    if not p.exists():
        raise SystemExit("active family refresh v2 summary not found")

    df = pd.read_csv(p)
    failed = df[df["rolling_status"].astype(str) == "TIME_OOS_FAIL"].copy()
    return p, failed

def load_locator_details() -> Dict[str, Dict[str, Any]]:
    d = latest_dir(WORKSPACE / "edge_factory_active_family_evidence_locator_v2", "active_family_evidence_locator_v2_")
    p = d / "active_family_evidence_locator_v2_state.json" if d else None
    obj = read_json(p)

    out = {}
    for item in obj.get("details", []):
        fam = item.get("family_key")
        if fam:
            out[str(fam)] = item
    return out

def analyze_folds(evidence_csv: Optional[str]) -> tuple[pd.DataFrame, Dict[str, Any]]:
    if not evidence_csv or not Path(evidence_csv).exists():
        return pd.DataFrame(), {"exists": False}

    try:
        df = pd.read_csv(evidence_csv)
    except Exception as e:
        return pd.DataFrame(), {"exists": True, "read_error": repr(e)}

    pnl_col = find_col(df, ["test_pnl", "pnl", "net_pnl", "test_total", "fold_pnl", "total_pnl"])
    fold_col = find_col(df, ["fold", "fold_id", "window", "window_id"])
    start_col = find_col(df, ["test_start", "start", "start_time", "from"])
    end_col = find_col(df, ["test_end", "end", "end_time", "to"])

    if pnl_col is None:
        return df, {"exists": True, "rows": len(df), "pnl_col": None}

    tmp = df.copy()
    tmp["_pnl"] = pd.to_numeric(tmp[pnl_col], errors="coerce")
    tmp = tmp.dropna(subset=["_pnl"])

    worst = tmp.sort_values("_pnl").head(10).copy()
    best = tmp.sort_values("_pnl", ascending=False).head(10).copy()

    summary = {
        "exists": True,
        "rows": int(len(tmp)),
        "pnl_col": pnl_col,
        "fold_col": fold_col,
        "start_col": start_col,
        "end_col": end_col,
        "fold_total_pnl": float(tmp["_pnl"].sum()) if len(tmp) else 0.0,
        "fold_mean_pnl": float(tmp["_pnl"].mean()) if len(tmp) else 0.0,
        "fold_min_pnl": float(tmp["_pnl"].min()) if len(tmp) else 0.0,
        "fold_max_pnl": float(tmp["_pnl"].max()) if len(tmp) else 0.0,
        "positive_fold_rate": float((tmp["_pnl"] > 0).mean()) if len(tmp) else 0.0,
    }

    return df, {"summary": summary, "worst": worst.to_dict(orient="records"), "best": best.to_dict(orient="records")}

def analyze_trades(source_path: Optional[str], family: str, out_dir: Path) -> Dict[str, Any]:
    if not source_path or not Path(source_path).exists():
        return {"exists": False, "reason": "source_path missing"}

    try:
        df = pd.read_csv(source_path)
    except Exception as e:
        return {"exists": True, "read_error": repr(e)}

    fam_col = find_col(df, ["family_key", "family", "candidate", "target_key", "target"])
    pnl_col = find_col(df, ["pnl", "net_pnl", "net_pnl_usdt", "pnl_usdt"])
    sym_col = find_col(df, ["symbol", "inst_id", "inst", "ticker"])
    time_col = find_col(df, ["event_time", "entry_time", "signal_time", "time", "timestamp", "datetime"])

    if fam_col:
        df = df[df[fam_col].astype(str) == family].copy()

    if df.empty:
        return {"exists": True, "rows": 0, "reason": "no rows for family"}

    if pnl_col is None:
        return {"exists": True, "rows": int(len(df)), "reason": "pnl column missing"}

    df["_pnl"] = pd.to_numeric(df[pnl_col], errors="coerce")
    df = df.dropna(subset=["_pnl"])

    if time_col:
        df["_time"] = pd.to_datetime(df[time_col], errors="coerce", utc=True)
        df["_month"] = df["_time"].dt.to_period("M").astype(str)
    else:
        df["_month"] = "UNKNOWN"

    if sym_col is None:
        df["_symbol"] = "UNKNOWN"
    else:
        df["_symbol"] = df[sym_col].astype(str)

    by_symbol = (
        df.groupby("_symbol")
        .agg(
            trades=("_pnl", "count"),
            pnl_sum=("_pnl", "sum"),
            pnl_mean=("_pnl", "mean"),
            win_rate=("_pnl", lambda x: float((x > 0).mean())),
        )
        .reset_index()
        .rename(columns={"_symbol": "symbol"})
        .sort_values("pnl_sum")
    )

    by_month = (
        df.groupby("_month")
        .agg(
            trades=("_pnl", "count"),
            pnl_sum=("_pnl", "sum"),
            pnl_mean=("_pnl", "mean"),
            win_rate=("_pnl", lambda x: float((x > 0).mean())),
        )
        .reset_index()
        .rename(columns={"_month": "month"})
        .sort_values("month")
    )

    by_symbol.to_csv(out_dir / f"{family}_damage_by_symbol.csv", index=False)
    by_month.to_csv(out_dir / f"{family}_damage_by_month.csv", index=False)

    worst_symbols = by_symbol.head(20).to_dict(orient="records")
    best_symbols = by_symbol.sort_values("pnl_sum", ascending=False).head(20).to_dict(orient="records")

    return {
        "exists": True,
        "rows": int(len(df)),
        "pnl_col": pnl_col,
        "symbol_col": sym_col,
        "time_col": time_col,
        "total_pnl": float(df["_pnl"].sum()),
        "mean_pnl": float(df["_pnl"].mean()),
        "win_rate": float((df["_pnl"] > 0).mean()),
        "symbol_count": int(df["_symbol"].nunique()),
        "month_count": int(df["_month"].nunique()),
        "worst_symbol_pnl": float(by_symbol["pnl_sum"].min()) if len(by_symbol) else 0.0,
        "best_symbol_pnl": float(by_symbol["pnl_sum"].max()) if len(by_symbol) else 0.0,
        "negative_symbol_count": int((by_symbol["pnl_sum"] < 0).sum()) if len(by_symbol) else 0,
        "positive_symbol_count": int((by_symbol["pnl_sum"] > 0).sum()) if len(by_symbol) else 0,
        "worst_symbols": worst_symbols,
        "best_symbols": best_symbols,
    }

def decide_damage(family: str, refresh_row: pd.Series, folds: Dict[str, Any], trades: Dict[str, Any]) -> Dict[str, Any]:
    test_total = safe_float(refresh_row.get("test_total_sum"))
    pf = safe_float(refresh_row.get("test_pf_aggregate"))
    worst = safe_float(refresh_row.get("worst_test_fold"))
    pos_fold = safe_float(refresh_row.get("positive_test_fold_rate"))
    month_pos = safe_float(refresh_row.get("monthly_positive_rate"))

    if family == "market_relative_short":
        if test_total > 0 and pf > 1.0 and pos_fold < 0.5:
            decision = "KEEP_CAPPED_REDUCED_SIZE_ONLY_NO_EXPANSION"
            reason = "Aggregate positive but fold/month stability weak; reduced-size cap remains justified."
            capital_action = "KEEP_2P5_PERCENT_OR_LOWER_PENDING_DRIFT"
            retire_now = False
            reduce_now = False
        elif test_total <= 0:
            decision = "QUARANTINE_OR_DISABLE_REVIEW"
            reason = "Aggregate result non-positive."
            capital_action = "CONSIDER_ZERO_OR_BACKUP_ONLY"
            retire_now = True
            reduce_now = True
        else:
            decision = "REVIEW_FAILED_FAMILY"
            reason = "Failed time-OOS requires review."
            capital_action = "NO_EXPANSION"
            retire_now = False
            reduce_now = True
    else:
        decision = "REVIEW_FAILED_FAMILY"
        reason = "Generic failed-family review required."
        capital_action = "NO_EXPANSION"
        retire_now = False
        reduce_now = True

    return {
        "family_key": family,
        "damage_decision": decision,
        "reason": reason,
        "capital_action": capital_action,
        "retire_now_recommended": retire_now,
        "reduce_now_recommended": reduce_now,
        "active_paper_change_allowed_by_this_module": False,
        "capital_change_allowed_by_this_module": False,
        "live_allowed": False,
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_active_family_damage_decomposition_v1" / f"active_family_damage_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    refresh_path, failed = load_failed_families()
    locator = load_locator_details()

    family_results = []

    for _, row in failed.iterrows():
        family = str(row["family_key"])
        detail = locator.get(family, {})
        evidence_row = detail.get("row", {}) or {}

        evidence_csv = evidence_row.get("evidence_csv")
        source_path = evidence_row.get("source_path")

        folds_df, folds_analysis = analyze_folds(evidence_csv)
        trades_analysis = analyze_trades(source_path, family, out_dir)
        decision = decide_damage(family, row, folds_analysis, trades_analysis)

        family_results.append({
            "family_key": family,
            "refresh_row": row.to_dict(),
            "evidence_csv": evidence_csv,
            "source_path": source_path,
            "folds_analysis": folds_analysis,
            "trades_analysis": trades_analysis,
            "decision": decision,
        })

    flat = []
    for r in family_results:
        d = r["decision"]
        t = r.get("trades_analysis", {})
        fsum = r.get("folds_analysis", {}).get("summary", {}) if isinstance(r.get("folds_analysis"), dict) else {}
        flat.append({
            "family_key": r["family_key"],
            "damage_decision": d["damage_decision"],
            "reason": d["reason"],
            "capital_action": d["capital_action"],
            "trade_rows": t.get("rows"),
            "trade_total_pnl": t.get("total_pnl"),
            "trade_symbol_count": t.get("symbol_count"),
            "negative_symbol_count": t.get("negative_symbol_count"),
            "positive_symbol_count": t.get("positive_symbol_count"),
            "fold_rows": fsum.get("rows"),
            "fold_total_pnl": fsum.get("fold_total_pnl"),
            "fold_min_pnl": fsum.get("fold_min_pnl"),
            "fold_positive_rate": fsum.get("positive_fold_rate"),
            "retire_now_recommended": d["retire_now_recommended"],
            "reduce_now_recommended": d["reduce_now_recommended"],
            "capital_change_allowed_by_this_module": False,
            "live_allowed": False,
        })

    summary_df = pd.DataFrame(flat)

    if len(summary_df) == 0:
        overall = "NO_FAILED_ACTIVE_FAMILY_TO_DECOMPOSE"
        next_action = "RUN_DRIFT_MONITOR"
    else:
        overall = "FAILED_ACTIVE_FAMILY_DAMAGE_DECOMPOSITION_COMPLETE"
        next_action = "RUN_CAPITAL_GOVERNOR_REVIEW_WITH_DAMAGE_RESULTS"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "output_dir": str(out_dir),
        "overall_status": overall,
        "refresh_summary_path": str(refresh_path),
        "failed_family_count": int(len(failed)),
        "families": family_results,
        "next_os_action": next_action,
        "active_paper_change_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "hard_rules": [
            "This module does not change active paper.",
            "This module does not change capital.",
            "This module does not start live.",
            "Damage decomposition is advisory only.",
            "Capital governor must decide any size change in a separate gate.",
        ],
    }

    write_json(out_dir / "active_family_damage_decomposition_v1_state.json", state)
    summary_df.to_csv(out_dir / "active_family_damage_decomposition_v1_summary.csv", index=False)

    ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "master_research_result_ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": "active_family_damage_decomposition_v1",
            "overall_status": overall,
            "failed_family_count": int(len(failed)),
            "active_paper_change_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "state_path": str(out_dir / "active_family_damage_decomposition_v1_state.json"),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY ACTIVE FAMILY DAMAGE DECOMPOSITION v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"overall_status: {overall}")
    print(f"failed_family_count: {len(failed)}")
    print("active_paper_change_allowed: False")
    print("capital_change_allowed: False")
    print("live_allowed: False")
    print()

    if len(summary_df):
        print("SUMMARY")
        print("-" * 100)
        print(summary_df.to_string(index=False))
    else:
        print("No failed active family found.")

    print()
    print(f"State  : {out_dir / 'active_family_damage_decomposition_v1_state.json'}")
    print(f"Summary: {out_dir / 'active_family_damage_decomposition_v1_summary.csv'}")
    print(f"Ledger : {ledger}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
