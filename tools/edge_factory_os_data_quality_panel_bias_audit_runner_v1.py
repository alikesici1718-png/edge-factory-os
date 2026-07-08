#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Data Quality Panel Bias Audit Runner v1

Purpose:
- Consume Data Quality Panel Bias Audit Contract v1.
- Audit the full panel for data quality, coverage, survivorship, missingness,
  timestamp integrity, raw/canonical month semantics, and feature-construction risks.
- This is not strategy search and not candidate generation.

This runner does NOT:
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
"""

from __future__ import annotations

import datetime as dt
import json
import math
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "data_quality_panel_bias_audit_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_data_quality_panel_bias_audit_runner"
OUT_JSON = OUT_DIR / "data_quality_panel_bias_audit_runner_latest.json"
OUT_TXT = OUT_DIR / "data_quality_panel_bias_audit_runner_latest.txt"
OUT_COLUMN_CSV = OUT_DIR / "data_quality_column_quality_latest.csv"
OUT_SYMBOL_CSV = OUT_DIR / "data_quality_symbol_coverage_latest.csv"
OUT_MONTH_CSV = OUT_DIR / "data_quality_month_coverage_latest.csv"
OUT_GAP_CSV = OUT_DIR / "data_quality_symbol_gap_summary_latest.csv"
OUT_OUTLIER_CSV = OUT_DIR / "data_quality_return_outliers_latest.csv"
OUT_FINDINGS_CSV = OUT_DIR / "data_quality_audit_findings_latest.csv"

RUNNER_NAME = "edge_factory_os_data_quality_panel_bias_audit_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "DATA_QUALITY_PANEL_BIAS_AUDIT_CONTRACT_READY"
REQUIRED_DIRECTION_QUEUE_KEY = "RD4_05_DATA_QUALITY_AND_PANEL_BIAS_AUDIT"

EXPECTED_SYMBOL_COUNT = 285

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        rename[c] = str(c).strip().lower().replace(" ", "_").replace("-", "_")
    return df.rename(columns=rename)


def pick_col(df: pd.DataFrame, candidates: List[str], required: bool = True) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise ValueError(f"Missing required column. Tried={candidates}; available_sample={list(df.columns)[:100]}")
    return None


def safe_datetime_utc_naive(series: pd.Series) -> pd.Series:
    t = pd.to_datetime(series, utc=True, errors="coerce")
    return t.dt.tz_convert("UTC").dt.tz_localize(None)


def safe_month_from_time(series: pd.Series) -> pd.Series:
    t = pd.to_datetime(series, utc=True, errors="coerce")
    t = t.dt.tz_convert("UTC").dt.tz_localize(None)
    return t.dt.to_period("M").astype(str)


def score_panel_path(path: Path) -> int:
    s = str(path).lower()
    score = 0
    for token, weight in [
        ("okx", 20),
        ("swap", 20),
        ("285", 18),
        ("1y", 16),
        ("feature_panel", 14),
        ("dynamic", 8),
        ("full", 8),
        ("panel", 8),
        ("universe", 6),
        ("parquet", 5),
    ]:
        if token in s:
            score += weight
    try:
        score += min(int(path.stat().st_size / 100_000_000), 30)
    except Exception:
        pass
    return score


def find_panel_file(contract: Dict[str, Any]) -> Optional[Path]:
    candidates: List[Path] = []

    for p in contract.get("panel_candidates", []) or []:
        try:
            pp = Path(str(p))
            if pp.exists() and pp.is_file():
                candidates.append(pp)
        except Exception:
            pass

    if candidates:
        return sorted(candidates, key=score_panel_path, reverse=True)[0]

    roots = [
        BASE_DIR / "edge_factory_feature_panels",
        BASE_DIR / "edge_factory_os_universe",
        BASE_DIR / "edge_factory_universe",
        BASE_DIR,
    ]

    patterns = [
        "**/*feature_panel*.parquet",
        "**/*okx*swap*1y*.parquet",
        "**/*285*.parquet",
        "**/*full*panel*.parquet",
        "**/*panel*.parquet",
    ]

    found: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            try:
                for p in root.glob(pattern):
                    if p.is_file() and p.suffix.lower() in {".parquet", ".csv"}:
                        found.append(p)
            except Exception:
                pass

    if not found:
        return None

    return sorted(set(found), key=score_panel_path, reverse=True)[0]


def read_panel(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported panel file: {path}")


def derive_canonical_months_from_month_coverage(month_coverage: pd.DataFrame, canonical_policy_month_count: int) -> Tuple[List[str], List[str], List[str]]:
    months = sorted(month_coverage["month"].astype(str).tolist())
    if len(months) <= canonical_policy_month_count:
        return months, [], []

    counts = month_coverage.set_index("month")["row_count"].astype(float)
    median_count = float(counts[counts > 0].median()) if (counts > 0).any() else 0.0

    if median_count <= 0:
        canonical = months[-canonical_policy_month_count:]
        partial = [m for m in months if m not in canonical]
        return canonical, partial, partial

    month_coverage = month_coverage.copy()
    month_coverage["coverage_ratio_vs_median"] = month_coverage["row_count"].astype(float) / median_count
    partial_months = month_coverage.loc[month_coverage["coverage_ratio_vs_median"] < 0.55, "month"].astype(str).tolist()

    fullish = month_coverage[month_coverage["coverage_ratio_vs_median"] >= 0.55].copy()
    if len(fullish) >= canonical_policy_month_count:
        canonical = (
            fullish.sort_values("row_count", ascending=False)
            .head(canonical_policy_month_count)["month"]
            .astype(str)
            .sort_values()
            .tolist()
        )
    else:
        canonical = months[-canonical_policy_month_count:]

    excluded = [m for m in months if m not in canonical]
    return canonical, partial_months, excluded


def build_core_panel(raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Optional[str]], List[str]]:
    raw = normalize_columns(raw)

    time_col = pick_col(raw, ["time", "timestamp", "datetime", "date", "open_time", "ts"])
    symbol_col = pick_col(raw, ["symbol", "instid", "instrument", "ticker", "coin"])
    close_col = pick_col(raw, ["close", "c", "last", "price", "mark_price"])
    volume_col = pick_col(raw, ["volume", "vol", "quote_volume", "quote_vol", "volume_quote", "turnover"], required=False)
    high_col = pick_col(raw, ["high", "h"], required=False)
    low_col = pick_col(raw, ["low", "l"], required=False)
    open_col = pick_col(raw, ["open", "o"], required=False)

    keep = [time_col, symbol_col, close_col]
    for c in [volume_col, high_col, low_col, open_col]:
        if c and c not in keep:
            keep.append(c)

    df = raw[keep].copy()

    rename = {time_col: "time", symbol_col: "symbol", close_col: "close"}
    if volume_col:
        rename[volume_col] = "volume"
    if high_col:
        rename[high_col] = "high"
    if low_col:
        rename[low_col] = "low"
    if open_col:
        rename[open_col] = "open"

    df = df.rename(columns=rename)

    df["time"] = safe_datetime_utc_naive(df["time"])
    df["month"] = safe_month_from_time(df["time"])
    df["symbol"] = df["symbol"].astype(str)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    for c in ["open", "high", "low", "volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            df[c] = np.nan

    # Keep raw nulls visible in audit, but remove rows without the absolute core identity.
    df = df.dropna(subset=["time", "symbol"]).sort_values(["symbol", "time"]).reset_index(drop=True)

    missing_required = []
    for c in ["time", "symbol", "close"]:
        if c not in df.columns:
            missing_required.append(c)

    column_map = {
        "time_col": time_col,
        "symbol_col": symbol_col,
        "close_col": close_col,
        "volume_col": volume_col,
        "high_col": high_col,
        "low_col": low_col,
        "open_col": open_col,
    }

    return df, column_map, missing_required


def audit_columns(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = len(df)

    for c in df.columns:
        s = df[c]
        missing_count = int(s.isna().sum())
        missing_ratio = float(missing_count / n) if n else 1.0

        inf_count = 0
        min_value = None
        max_value = None
        mean_value = None

        if pd.api.types.is_numeric_dtype(s):
            arr = pd.to_numeric(s, errors="coerce").to_numpy(dtype=np.float64)
            inf_count = int(np.isinf(arr).sum())
            finite = arr[np.isfinite(arr)]
            if finite.size:
                min_value = float(np.min(finite))
                max_value = float(np.max(finite))
                mean_value = float(np.mean(finite))

        rows.append({
            "column": c,
            "dtype": str(s.dtype),
            "missing_count": missing_count,
            "missing_ratio": missing_ratio,
            "inf_count": inf_count,
            "min_value": min_value,
            "max_value": max_value,
            "mean_value": mean_value,
            "non_null_count": int(n - missing_count),
        })

    return pd.DataFrame(rows)


def audit_month_coverage(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("month", observed=True)

    rows = g.agg(
        row_count=("time", "count"),
        symbol_count=("symbol", "nunique"),
        first_time=("time", "min"),
        last_time=("time", "max"),
    ).reset_index()

    rows["first_time"] = rows["first_time"].astype(str)
    rows["last_time"] = rows["last_time"].astype(str)
    rows = rows.sort_values("month").reset_index(drop=True)
    return rows


def audit_symbol_coverage(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("symbol", observed=True)

    rows = g.agg(
        row_count=("time", "count"),
        active_month_count=("month", "nunique"),
        first_time=("time", "min"),
        last_time=("time", "max"),
        close_missing_ratio=("close", lambda s: float(s.isna().mean())),
        volume_missing_ratio=("volume", lambda s: float(s.isna().mean())),
        high_missing_ratio=("high", lambda s: float(s.isna().mean())),
        low_missing_ratio=("low", lambda s: float(s.isna().mean())),
    ).reset_index()

    rows["first_time"] = rows["first_time"].astype(str)
    rows["last_time"] = rows["last_time"].astype(str)
    rows = rows.sort_values(["active_month_count", "row_count"], ascending=[True, True]).reset_index(drop=True)
    return rows


def audit_gaps(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for symbol, sdf in df[["symbol", "time"]].dropna().sort_values(["symbol", "time"]).groupby("symbol", observed=True):
        times = sdf["time"].drop_duplicates().sort_values()
        diffs = times.diff().dropna()

        if diffs.empty:
            rows.append({
                "symbol": symbol,
                "timestamp_count": int(len(times)),
                "median_gap_hours": None,
                "max_gap_hours": None,
                "gap_gt_1h_count": 0,
                "gap_gt_3h_count": 0,
                "gap_gt_24h_count": 0,
            })
            continue

        hours = diffs.dt.total_seconds() / 3600.0
        rows.append({
            "symbol": symbol,
            "timestamp_count": int(len(times)),
            "median_gap_hours": float(hours.median()),
            "max_gap_hours": float(hours.max()),
            "gap_gt_1h_count": int((hours > 1.5).sum()),
            "gap_gt_3h_count": int((hours > 3.5).sum()),
            "gap_gt_24h_count": int((hours > 24.5).sum()),
        })

    return pd.DataFrame(rows).sort_values(["gap_gt_24h_count", "gap_gt_3h_count", "max_gap_hours"], ascending=[False, False, False]).reset_index(drop=True)


def audit_return_outliers(df: pd.DataFrame) -> pd.DataFrame:
    work = df[["symbol", "time", "month", "close"]].copy()
    work["close"] = pd.to_numeric(work["close"], errors="coerce")
    work = work.dropna(subset=["symbol", "time", "close"]).sort_values(["symbol", "time"])

    work["ret_1_bps"] = work.groupby("symbol", observed=True)["close"].pct_change() * 10000.0
    work["abs_ret_1_bps"] = work["ret_1_bps"].abs()

    out = work[
        (work["abs_ret_1_bps"] >= 2000.0)
        | (~np.isfinite(work["ret_1_bps"].to_numpy(dtype=np.float64)))
    ].copy()

    if out.empty:
        return pd.DataFrame(columns=["symbol", "time", "month", "close", "ret_1_bps", "abs_ret_1_bps", "outlier_reason"])

    out["outlier_reason"] = np.where(out["abs_ret_1_bps"] >= 2000.0, "ABS_1H_RETURN_GE_2000_BPS", "NON_FINITE_RETURN")
    return out.sort_values("abs_ret_1_bps", ascending=False).head(5000).reset_index(drop=True)


def high_low_range_quality(df: pd.DataFrame) -> Dict[str, Any]:
    n = len(df)
    if n == 0:
        return {}

    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")
    open_ = pd.to_numeric(df["open"], errors="coerce")

    high_low_inverted = int(((high < low) & high.notna() & low.notna()).sum())
    close_outside_hl = int((((close > high) | (close < low)) & close.notna() & high.notna() & low.notna()).sum())
    open_outside_hl = int((((open_ > high) | (open_ < low)) & open_.notna() & high.notna() & low.notna()).sum())

    zero_or_negative_close = int((close <= 0).sum())
    zero_or_negative_high = int((high <= 0).sum())
    zero_or_negative_low = int((low <= 0).sum())

    range_bps = ((high - low) / close) * 10000.0
    finite_range = range_bps.replace([np.inf, -np.inf], np.nan).dropna()

    return {
        "high_low_inverted_count": high_low_inverted,
        "high_low_inverted_ratio": float(high_low_inverted / n),
        "close_outside_high_low_count": close_outside_hl,
        "close_outside_high_low_ratio": float(close_outside_hl / n),
        "open_outside_high_low_count": open_outside_hl,
        "open_outside_high_low_ratio": float(open_outside_hl / n),
        "zero_or_negative_close_count": zero_or_negative_close,
        "zero_or_negative_high_count": zero_or_negative_high,
        "zero_or_negative_low_count": zero_or_negative_low,
        "median_range_bps": float(finite_range.median()) if not finite_range.empty else None,
        "p99_range_bps": float(finite_range.quantile(0.99)) if not finite_range.empty else None,
        "max_range_bps": float(finite_range.max()) if not finite_range.empty else None,
    }


def duplicate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    total_duplicates = int(df.duplicated().sum())
    key_duplicates = int(df.duplicated(subset=["symbol", "time"]).sum()) if {"symbol", "time"}.issubset(df.columns) else 0
    return {
        "duplicate_full_row_count": total_duplicates,
        "duplicate_symbol_time_count": key_duplicates,
    }


def build_findings(
    *,
    row_count: int,
    symbol_count: int,
    raw_calendar_month_count: int,
    canonical_months: List[str],
    partial_boundary_months: List[str],
    excluded_months: List[str],
    duplicate_info: Dict[str, Any],
    column_quality: pd.DataFrame,
    symbol_coverage: pd.DataFrame,
    gap_summary: pd.DataFrame,
    outliers: pd.DataFrame,
    hl_quality: Dict[str, Any],
    panel_path: Path,
) -> Tuple[str, str, List[Dict[str, Any]], List[str]]:
    findings: List[Dict[str, Any]] = []
    recommendations: List[str] = []

    def add(severity: str, key: str, message: str, recommendation: str) -> None:
        findings.append({
            "severity": severity,
            "finding_key": key,
            "message": message,
            "recommendation": recommendation,
        })
        if recommendation not in recommendations:
            recommendations.append(recommendation)

    if "feature_panel" not in str(panel_path).lower() and "panel" not in str(panel_path).lower():
        add(
            "ATTENTION",
            "PANEL_PATH_NOT_OBVIOUS_FEATURE_PANEL",
            f"Panel path does not clearly look like a feature/full panel: {panel_path}",
            "Verify that the audit is running on the intended full-universe feature panel.",
        )

    if symbol_count < int(EXPECTED_SYMBOL_COUNT * 0.90):
        add(
            "ATTENTION",
            "SYMBOL_COUNT_BELOW_EXPECTED",
            f"Symbol count {symbol_count} is far below expected {EXPECTED_SYMBOL_COUNT}.",
            "Check universe construction, symbol filtering, and whether inactive/delisted symbols were removed.",
        )

    if raw_calendar_month_count < 12:
        add(
            "CRITICAL",
            "RAW_CALENDAR_MONTH_COUNT_BELOW_12",
            f"Raw calendar month count is {raw_calendar_month_count}.",
            "Block further research until a full enough panel is available.",
        )

    if len(canonical_months) != 12:
        add(
            "CRITICAL",
            "CANONICAL_POLICY_MONTH_COUNT_NOT_12",
            f"Canonical policy month count is {len(canonical_months)}, expected 12.",
            "Fix canonical month guard before further research.",
        )

    if raw_calendar_month_count == 13 and partial_boundary_months:
        add(
            "INFO",
            "RAW_13_WITH_PARTIAL_BOUNDARIES_DETECTED",
            f"Raw 13 month buckets detected; partial boundary months: {partial_boundary_months}.",
            "Keep partial boundary months out of release policy; use canonical 12 months only.",
        )

    if duplicate_info.get("duplicate_full_row_count", 0) > 0 or duplicate_info.get("duplicate_symbol_time_count", 0) > 0:
        add(
            "ATTENTION",
            "DUPLICATE_ROWS_PRESENT",
            f"Duplicates: full={duplicate_info.get('duplicate_full_row_count')}, symbol_time={duplicate_info.get('duplicate_symbol_time_count')}.",
            "Deduplicate panel or prove duplicates are harmless before further research.",
        )

    bad_missing = column_quality[column_quality["missing_ratio"] > 0.20].copy()
    if not bad_missing.empty:
        cols = bad_missing["column"].astype(str).head(20).tolist()
        add(
            "ATTENTION",
            "HIGH_COLUMN_MISSINGNESS",
            f"Columns with >20% missingness: {cols}",
            "Audit whether high-missingness columns are used by research runners; block or impute explicitly.",
        )

    inf_cols = column_quality[column_quality["inf_count"] > 0].copy()
    if not inf_cols.empty:
        cols = inf_cols["column"].astype(str).head(20).tolist()
        add(
            "ATTENTION",
            "INF_VALUES_PRESENT",
            f"Columns with inf values: {cols}",
            "Clean inf values at panel construction stage or enforce runner-level guards.",
        )

    weak_symbols = symbol_coverage[symbol_coverage["active_month_count"] < 10].copy()
    if not weak_symbols.empty:
        add(
            "ATTENTION",
            "SYMBOL_LIFECYCLE_SHORT_COVERAGE_PRESENT",
            f"{len(weak_symbols)} symbols have fewer than 10 active months.",
            "Decide whether short-lifecycle symbols are allowed in research or require lifecycle-aware splits.",
        )

    large_gap_symbols = gap_summary[gap_summary["gap_gt_24h_count"] > 0].copy() if not gap_summary.empty else pd.DataFrame()
    if not large_gap_symbols.empty:
        add(
            "ATTENTION",
            "LARGE_TIMESTAMP_GAPS_PRESENT",
            f"{len(large_gap_symbols)} symbols have gaps >24h.",
            "Audit exchange outages, listing gaps, missing candles, and whether features forward-fill across gaps.",
        )

    if len(outliers) > 0:
        add(
            "ATTENTION",
            "EXTREME_RETURN_OUTLIERS_PRESENT",
            f"{len(outliers)} extreme/non-finite 1-bar return outliers detected in exported sample.",
            "Inspect outliers for bad candles, split-like discontinuities, or exchange data anomalies.",
        )

    if hl_quality.get("high_low_inverted_count", 0) > 0:
        add(
            "CRITICAL",
            "HIGH_LOW_INVERTED",
            f"high < low detected in {hl_quality.get('high_low_inverted_count')} rows.",
            "Fix OHLC data before further research.",
        )

    if hl_quality.get("close_outside_high_low_count", 0) > 0:
        add(
            "ATTENTION",
            "CLOSE_OUTSIDE_HIGH_LOW",
            f"close outside high/low detected in {hl_quality.get('close_outside_high_low_count')} rows.",
            "Audit OHLC consistency and vendor normalization.",
        )

    if not findings:
        add(
            "INFO",
            "AUDIT_NO_MATERIAL_ISSUES_FOUND_V1",
            "No material v1 panel quality issue detected by this audit.",
            "If audit passes cleanly, proceed to a research meta-synthesizer or new evidence-generation queue rather than reopening blocked routes blindly.",
        )

    severities = {f["severity"] for f in findings}
    if "CRITICAL" in severities:
        audit_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_CRITICAL_ISSUES_FOUND"
        next_action = "BUILD_PANEL_REPAIR_OR_DATA_FIX_CONTRACT_BLOCK_RESEARCH"
    elif "ATTENTION" in severities:
        audit_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_ATTENTION_FINDINGS_PRESENT"
        next_action = "BUILD_DATA_QUALITY_EVALUATOR_AND_DECIDE_REPAIR_OR_META_SYNTHESIS"
    else:
        audit_status = "DATA_QUALITY_PANEL_BIAS_AUDIT_READ_ONLY_PASS"
        next_action = "BUILD_DATA_QUALITY_EVALUATOR_AND_RESEARCH_META_SYNTHESIS"

    return audit_status, next_action, findings, recommendations


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS DATA QUALITY PANEL BIAS AUDIT RUNNER v1")
    lines.append("=" * 100)

    for k in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "strict_policy_key",
        "canonical_policy_month_count",
        "raw_calendar_month_count",
        "symbol_count",
        "row_count",
        "finding_count",
        "critical_finding_count",
        "attention_finding_count",
        "elapsed_seconds",
        "panel_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("CANONICAL MONTHS")
    lines.append("-" * 100)
    lines.append(f"canonical_months: {result.get('canonical_months')}")
    lines.append(f"partial_boundary_months: {result.get('partial_boundary_months')}")
    lines.append(f"excluded_policy_months: {result.get('excluded_policy_months')}")

    lines.append("")
    lines.append("FINDINGS")
    lines.append("-" * 100)
    for row in result.get("audit_findings", []):
        lines.append(f"[{row.get('severity')}] {row.get('finding_key')}: {row.get('message')}")
        lines.append(f"  recommendation: {row.get('recommendation')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in [
        "output_json",
        "output_txt",
        "column_quality_csv",
        "symbol_coverage_csv",
        "month_coverage_csv",
        "gap_summary_csv",
        "outlier_csv",
        "findings_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS DATA QUALITY PANEL BIAS AUDIT RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"finding_count: {result.get('finding_count')}")
    print(f"critical_finding_count: {result.get('critical_finding_count')}")
    print(f"attention_finding_count: {result.get('attention_finding_count')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"FINDINGS CSV: {result.get('findings_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_PATH, default={})

    canonical_policy_month_count = int(contract.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "contract_path": str(CONTRACT_PATH),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "research_key": contract.get("research_key"),
        "direction_queue_key": contract.get("direction_queue_key"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "column_quality_csv": str(OUT_COLUMN_CSV),
        "symbol_coverage_csv": str(OUT_SYMBOL_CSV),
        "month_coverage_csv": str(OUT_MONTH_CSV),
        "gap_summary_csv": str(OUT_GAP_CSV),
        "outlier_csv": str(OUT_OUTLIER_CSV),
        "findings_csv": str(OUT_FINDINGS_CSV),
        **SAFETY_FLAGS,
    }

    try:
        prerequisite_pass = (
            contract.get("builder_status") == REQUIRED_BUILDER_STATUS
            and contract.get("direction_queue_key") == REQUIRED_DIRECTION_QUEUE_KEY
            and canonical_policy_month_count == 12
        )

        if not prerequisite_pass:
            result = {
                **base_result,
                "runner_status": "DATA_QUALITY_PANEL_BIAS_AUDIT_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_DATA_QUALITY_AUDIT_CONTRACT_NO_RELEASE",
                "reason": (
                    f"builder_status={contract.get('builder_status')}; "
                    f"direction_queue_key={contract.get('direction_queue_key')}; "
                    f"canonical_policy_month_count={canonical_policy_month_count}"
                ),
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        panel_path = find_panel_file(contract)
        if panel_path is None:
            result = {
                **base_result,
                "runner_status": "DATA_QUALITY_PANEL_BIAS_AUDIT_RUNNER_BLOCKED_NO_PANEL_FOUND",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "LOCATE_FULL_UNIVERSE_PANEL_AND_RERUN_NO_RELEASE",
                "reason": "No parquet/csv panel found.",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        print(f"Loading panel: {panel_path}")
        raw = read_panel(panel_path)
        raw_column_count = int(len(raw.columns))

        print("Building normalized audit panel...")
        df, column_map, missing_required = build_core_panel(raw)

        row_count = int(len(df))
        symbol_count = int(df["symbol"].nunique())

        print("Auditing column quality...")
        column_quality = audit_columns(df)
        column_quality.to_csv(OUT_COLUMN_CSV, index=False)

        print("Auditing month coverage...")
        month_coverage = audit_month_coverage(df)
        month_coverage.to_csv(OUT_MONTH_CSV, index=False)

        raw_calendar_month_count = int(len(month_coverage))
        canonical_months, partial_boundary_months, excluded_policy_months = derive_canonical_months_from_month_coverage(
            month_coverage,
            canonical_policy_month_count,
        )

        print("Auditing symbol coverage...")
        symbol_coverage = audit_symbol_coverage(df)
        symbol_coverage.to_csv(OUT_SYMBOL_CSV, index=False)

        print("Auditing timestamp gaps...")
        gap_summary = audit_gaps(df)
        gap_summary.to_csv(OUT_GAP_CSV, index=False)

        print("Auditing return outliers...")
        outliers = audit_return_outliers(df)
        outliers.to_csv(OUT_OUTLIER_CSV, index=False)

        print("Auditing duplicate and OHLC quality...")
        duplicate_info = duplicate_summary(df)
        hl_quality = high_low_range_quality(df)

        audit_status, next_action, findings, recommendations = build_findings(
            row_count=row_count,
            symbol_count=symbol_count,
            raw_calendar_month_count=raw_calendar_month_count,
            canonical_months=canonical_months,
            partial_boundary_months=partial_boundary_months,
            excluded_months=excluded_policy_months,
            duplicate_info=duplicate_info,
            column_quality=column_quality,
            symbol_coverage=symbol_coverage,
            gap_summary=gap_summary,
            outliers=outliers,
            hl_quality=hl_quality,
            panel_path=panel_path,
        )

        pd.DataFrame(findings).to_csv(OUT_FINDINGS_CSV, index=False)

        critical_count = int(sum(1 for x in findings if x.get("severity") == "CRITICAL"))
        attention_count = int(sum(1 for x in findings if x.get("severity") == "ATTENTION"))
        info_count = int(sum(1 for x in findings if x.get("severity") == "INFO"))

        if critical_count > 0:
            severity = "CRITICAL"
        elif attention_count > 0:
            severity = "ATTENTION"
        else:
            severity = "OK"

        reason = (
            f"findings={len(findings)}; critical={critical_count}; attention={attention_count}; "
            f"raw_months={raw_calendar_month_count}; canonical_months={len(canonical_months)}; "
            f"symbols={symbol_count}; rows={row_count}"
        )

        result = {
            **base_result,
            "runner_status": audit_status,
            "severity": severity,
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "reason": reason,
            "panel_path": str(panel_path),
            "raw_column_count": raw_column_count,
            "normalized_column_count": int(len(df.columns)),
            "column_map": column_map,
            "missing_required_columns": missing_required,
            "row_count": row_count,
            "symbol_count": symbol_count,
            "expected_symbol_count": EXPECTED_SYMBOL_COUNT,
            "raw_calendar_month_count": raw_calendar_month_count,
            "canonical_policy_month_count": canonical_policy_month_count,
            "canonical_months": canonical_months,
            "partial_boundary_months": partial_boundary_months,
            "excluded_policy_months": excluded_policy_months,
            "duplicate_info": duplicate_info,
            "high_low_range_quality": hl_quality,
            "finding_count": int(len(findings)),
            "critical_finding_count": critical_count,
            "attention_finding_count": attention_count,
            "info_finding_count": info_count,
            "audit_findings": findings,
            "audit_recommendations": recommendations,
            "column_quality_summary": {
                "column_count": int(len(column_quality)),
                "columns_with_missing": int((column_quality["missing_count"] > 0).sum()),
                "columns_with_missing_gt_20pct": int((column_quality["missing_ratio"] > 0.20).sum()),
                "columns_with_inf": int((column_quality["inf_count"] > 0).sum()),
            },
            "symbol_coverage_summary": {
                "symbol_count": symbol_count,
                "min_active_month_count": int(symbol_coverage["active_month_count"].min()) if not symbol_coverage.empty else 0,
                "median_active_month_count": float(symbol_coverage["active_month_count"].median()) if not symbol_coverage.empty else 0.0,
                "symbols_lt_10_active_months": int((symbol_coverage["active_month_count"] < 10).sum()) if not symbol_coverage.empty else 0,
            },
            "gap_summary": {
                "symbols_with_gap_gt_24h": int((gap_summary["gap_gt_24h_count"] > 0).sum()) if not gap_summary.empty else 0,
                "symbols_with_gap_gt_3h": int((gap_summary["gap_gt_3h_count"] > 0).sum()) if not gap_summary.empty else 0,
                "max_gap_hours": float(gap_summary["max_gap_hours"].max()) if not gap_summary.empty and gap_summary["max_gap_hours"].notna().any() else None,
            },
            "outlier_summary": {
                "exported_outlier_row_count": int(len(outliers)),
                "outlier_threshold_abs_1h_return_bps": 2000.0,
            },
            "release_gate_feed": {
                "DATA_QUALITY_PANEL_BIAS_AUDIT_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "AUDIT_CRITICAL_FINDING_COUNT": critical_count,
                "AUDIT_ATTENTION_FINDING_COUNT": attention_count,
                "RELEASE_PASS_FROM_THIS_RUNNER": False,
                "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_RUNNER": False,
                "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_RUNNER": False,
                "FAMILY_RELEASE_ALLOWED_FROM_THIS_RUNNER": False,
                "RUNTIME_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
                "CAPITAL_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
                "ACTIVE_PAPER_ALLOWED_FROM_THIS_RUNNER": False,
                "LIVE_ALLOWED_FROM_THIS_RUNNER": False,
                "REAL_ORDERS_ALLOWED_FROM_THIS_RUNNER": False,
            },
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }

        write_json(OUT_JSON, result)
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 0

    except Exception as e:
        result = {
            **base_result,
            "runner_status": "DATA_QUALITY_PANEL_BIAS_AUDIT_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_DATA_QUALITY_AUDIT_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(e).__name__}: {e}",
            "error_type": type(e).__name__,
            "error": str(e),
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
