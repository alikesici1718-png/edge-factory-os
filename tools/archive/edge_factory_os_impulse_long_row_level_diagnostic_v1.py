from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


MODULE = "edge_factory_os_impulse_long_row_level_diagnostic_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent
RUNTIME_DIR = BASE_DIR / "paper_run_gate_MASTER_UPPER_SYSTEM"

LOCATOR_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_impulse_long_evidence_locator_v2"
    / "impulse_long_evidence_locator_v2_latest.json"
)

DRIFT_V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_drift_review_v3"
    / "family_drift_review_v3_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"impulse_long_row_level_diagnostic_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "impulse_long_row_level_diagnostic_latest.json"
LATEST_MD = OUT_ROOT / "impulse_long_row_level_diagnostic_latest.md"


PREFERRED_RUNTIME_LEDGER_PATHS = [
    RUNTIME_DIR / "live_impulse_event_long_paper" / "closed_trades.csv",
    RUNTIME_DIR / "global_closed_trades.csv",
    RUNTIME_DIR / "live_performance_report" / "live_closed_trades_all.csv",
]


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def norm(x: Any) -> str:
    return str(x or "").strip().lower()


def to_float(v: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return float(int(v))
        if isinstance(v, (int, float)):
            x = float(v)
            if math.isnan(x):
                return default
            return x
        if isinstance(v, str):
            s = v.strip().replace(",", "").replace("%", "")
            if not s:
                return default
            return float(s)
    except Exception:
        return default
    return default


def to_int(v: Any, default: int = 0) -> int:
    x = to_float(v, None)
    if x is None:
        return default
    return int(x)


def parse_dt(v: Any) -> Optional[datetime]:
    if not isinstance(v, str):
        return None

    s = v.strip()
    if not s:
        return None

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    for candidate in [s, s.replace(" ", "T")]:
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

    return None


def read_csv(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["_source_file"] = str(path)
                rows.append(row)
    except Exception:
        pass

    return rows


def is_impulse_long_row(row: Dict[str, Any]) -> bool:
    direct_keys = ["family_key", "family", "strategy", "source_family", "family_name"]

    for k in direct_keys:
        if norm(row.get(k)) == "impulse_long":
            return True

    row_text = json.dumps(row, default=str).lower()
    return "impulse_long" in row_text


def get_value(row: Dict[str, Any], names: List[str]) -> Any:
    lower_map = {norm(k): k for k in row.keys()}

    for name in names:
        n = norm(name)
        if n in lower_map:
            return row.get(lower_map[n])

    for k in row.keys():
        nk = norm(k)
        for name in names:
            if norm(name) in nk:
                return row.get(k)

    return None


def percentile(values: List[float], q: float) -> Optional[float]:
    if not values:
        return None

    values = sorted(values)

    if len(values) == 1:
        return values[0]

    pos = (len(values) - 1) * q
    lower = math.floor(pos)
    upper = math.ceil(pos)

    if lower == upper:
        return values[int(pos)]

    return values[lower] * (upper - pos) + values[upper] * (pos - lower)


def summarize_numeric(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "sum": None,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "p25": None,
            "p75": None,
        }

    return {
        "count": len(values),
        "sum": sum(values),
        "mean": sum(values) / len(values),
        "median": percentile(values, 0.50),
        "min": min(values),
        "max": max(values),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
    }


def bucket_signal_ret3(x: Optional[float]) -> str:
    if x is None:
        return "missing"
    if x < -300:
        return "ret3_lt_-300"
    if x < -150:
        return "ret3_-300_to_-150"
    if x < 0:
        return "ret3_-150_to_0"
    if x < 150:
        return "ret3_0_to_150"
    if x < 300:
        return "ret3_150_to_300"
    return "ret3_gt_300"


def bucket_entry_range(x: Optional[float]) -> str:
    if x is None:
        return "missing"
    if x < 50:
        return "range_lt_50"
    if x < 150:
        return "range_50_to_150"
    if x < 300:
        return "range_150_to_300"
    return "range_gt_300"


def choose_runtime_ledgers(locator: Dict[str, Any]) -> List[Path]:
    chosen: List[Path] = []

    for p in PREFERRED_RUNTIME_LEDGER_PATHS:
        if p.exists():
            chosen.append(p)

    if chosen:
        return chosen

    for c in locator.get("top_row_level_candidates") or []:
        p = Path(str(c.get("path") or ""))
        ps = norm(p)

        if not p.exists():
            continue

        if "family4_overlap" in ps or "combined_sim" in ps or "backtest" in ps:
            continue

        if "paper_run_gate_master_upper_system" in ps:
            chosen.append(p)

    return chosen[:3]


def dedupe_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []

    for row in rows:
        keys = [
            row.get("close_id"),
            row.get("position_id"),
            row.get("signal_id"),
            row.get("inst_id"),
            row.get("entry_time"),
            row.get("exit_time"),
            row.get("pnl"),
        ]

        key = "|".join(str(x) for x in keys)

        if key in seen:
            continue

        seen.add(key)
        out.append(row)

    return out


def analyze_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    impulse_rows = [r for r in rows if is_impulse_long_row(r)]
    impulse_rows = dedupe_rows(impulse_rows)

    pnl_values: List[float] = []
    net_ret_values: List[float] = []
    gross_ret_values: List[float] = []
    realistic_net_ret_values: List[float] = []
    stress_net_ret_values: List[float] = []
    fee_bps_values: List[float] = []
    entry_slip_values: List[float] = []
    exit_slip_values: List[float] = []
    hold_minutes_values: List[float] = []

    symbol_pnl = defaultdict(float)
    symbol_count = Counter()
    hour_pnl = defaultdict(float)
    hour_count = Counter()
    signal_ret3_bucket_pnl = defaultdict(float)
    signal_ret3_bucket_count = Counter()
    entry_range_bucket_pnl = defaultdict(float)
    entry_range_bucket_count = Counter()

    enriched_rows = []

    for row in impulse_rows:
        coin = str(get_value(row, ["coin", "inst_id", "symbol", "ticker"]) or "UNKNOWN")
        pnl = to_float(get_value(row, ["pnl", "realized_pnl", "net_pnl"]), None)
        net_ret = to_float(get_value(row, ["net_ret"]), None)
        gross_ret = to_float(get_value(row, ["gross_ret"]), None)
        realistic_net_ret = to_float(get_value(row, ["realistic_net_ret"]), None)
        stress_net_ret = to_float(get_value(row, ["stress_net_ret"]), None)
        fee_bps = to_float(get_value(row, ["fee_bps_total"]), None)
        entry_slip = to_float(get_value(row, ["entry_slip_bps"]), None)
        exit_slip = to_float(get_value(row, ["exit_slip_bps"]), None)
        hold_minutes = to_float(get_value(row, ["hold_minutes_actual"]), None)
        signal_ret3 = to_float(get_value(row, ["signal_ret3_bps"]), None)
        entry_range = to_float(get_value(row, ["entry_range_bps"]), None)

        exit_dt = parse_dt(str(get_value(row, ["exit_time", "closed_at", "timestamp"]) or ""))
        hour = exit_dt.hour if exit_dt else None

        if pnl is not None:
            pnl_values.append(pnl)
            symbol_pnl[coin] += pnl
            signal_ret3_bucket_pnl[bucket_signal_ret3(signal_ret3)] += pnl
            entry_range_bucket_pnl[bucket_entry_range(entry_range)] += pnl

            if hour is not None:
                hour_pnl[hour] += pnl

        if net_ret is not None:
            net_ret_values.append(net_ret)

        if gross_ret is not None:
            gross_ret_values.append(gross_ret)

        if realistic_net_ret is not None:
            realistic_net_ret_values.append(realistic_net_ret)

        if stress_net_ret is not None:
            stress_net_ret_values.append(stress_net_ret)

        if fee_bps is not None:
            fee_bps_values.append(fee_bps)

        if entry_slip is not None:
            entry_slip_values.append(entry_slip)

        if exit_slip is not None:
            exit_slip_values.append(exit_slip)

        if hold_minutes is not None:
            hold_minutes_values.append(hold_minutes)

        symbol_count[coin] += 1
        signal_ret3_bucket_count[bucket_signal_ret3(signal_ret3)] += 1
        entry_range_bucket_count[bucket_entry_range(entry_range)] += 1

        if hour is not None:
            hour_count[hour] += 1

        enriched_rows.append(
            {
                "coin": coin,
                "pnl": pnl,
                "net_ret": net_ret,
                "gross_ret": gross_ret,
                "realistic_net_ret": realistic_net_ret,
                "stress_net_ret": stress_net_ret,
                "fee_bps_total": fee_bps,
                "entry_slip_bps": entry_slip,
                "exit_slip_bps": exit_slip,
                "hold_minutes_actual": hold_minutes,
                "signal_ret3_bps": signal_ret3,
                "entry_range_bps": entry_range,
                "exit_hour_utc": hour,
                "entry_time": get_value(row, ["entry_time"]),
                "exit_time": get_value(row, ["exit_time"]),
                "close_id": get_value(row, ["close_id"]),
                "position_id": get_value(row, ["position_id"]),
                "source_file": row.get("_source_file"),
            }
        )

    wins = [x for x in pnl_values if x > 0]
    losses = [x for x in pnl_values if x < 0]

    worst_rows = sorted(
        [r for r in enriched_rows if r.get("pnl") is not None],
        key=lambda x: x["pnl"],
    )[:10]

    best_rows = sorted(
        [r for r in enriched_rows if r.get("pnl") is not None],
        key=lambda x: x["pnl"],
        reverse=True,
    )[:10]

    gross_net_gap = None
    if gross_ret_values and net_ret_values and len(gross_ret_values) == len(net_ret_values):
        gross_net_gap = sum(gross_ret_values) - sum(net_ret_values)

    return {
        "available": bool(impulse_rows),
        "all_rows_loaded": len(rows),
        "impulse_rows": len(impulse_rows),
        "pnl_count": len(pnl_values),
        "win_count": len(wins),
        "loss_count": len(losses),
        "win_rate": len(wins) / len(pnl_values) if pnl_values else None,
        "pnl_summary": summarize_numeric(pnl_values),
        "net_ret_summary": summarize_numeric(net_ret_values),
        "gross_ret_summary": summarize_numeric(gross_ret_values),
        "realistic_net_ret_summary": summarize_numeric(realistic_net_ret_values),
        "stress_net_ret_summary": summarize_numeric(stress_net_ret_values),
        "fee_bps_summary": summarize_numeric(fee_bps_values),
        "entry_slip_bps_summary": summarize_numeric(entry_slip_values),
        "exit_slip_bps_summary": summarize_numeric(exit_slip_values),
        "hold_minutes_summary": summarize_numeric(hold_minutes_values),
        "gross_minus_net_ret_sum_gap": gross_net_gap,
        "symbol_count_top": symbol_count.most_common(20),
        "top_loss_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1])[:20],
        "top_win_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1], reverse=True)[:20],
        "exit_hour_count": dict(sorted(hour_count.items())),
        "exit_hour_pnl": dict(sorted(hour_pnl.items())),
        "signal_ret3_bucket_count": dict(signal_ret3_bucket_count),
        "signal_ret3_bucket_pnl": dict(signal_ret3_bucket_pnl),
        "entry_range_bucket_count": dict(entry_range_bucket_count),
        "entry_range_bucket_pnl": dict(entry_range_bucket_pnl),
        "worst_trades": worst_rows,
        "best_trades": best_rows,
    }


def build_diagnosis(summary: Dict[str, Any], aggregate_profile: Dict[str, Any], drift_gate_ready: bool) -> List[Dict[str, Any]]:
    findings = []

    if not summary.get("available"):
        return [
            {
                "finding_id": "F0_NO_ROW_LEVEL_DATA",
                "severity": "ATTENTION",
                "claim": "No row-level impulse_long data available.",
                "evidence": "runtime ledger rows could not be filtered to impulse_long",
                "next_action": "add read-only ledger exporter",
            }
        ]

    win_rate = summary.get("win_rate")
    pnl_sum = (summary.get("pnl_summary") or {}).get("sum")
    pnl_mean = (summary.get("pnl_summary") or {}).get("mean")
    worst_pnl = (summary.get("pnl_summary") or {}).get("min")
    gross_net_gap = summary.get("gross_minus_net_ret_sum_gap")

    if win_rate is not None and win_rate < 0.35:
        findings.append(
            {
                "finding_id": "F1_LOW_ROW_LEVEL_WIN_RATE",
                "severity": "HIGH",
                "claim": "Row-level impulse_long win rate is low.",
                "evidence": f"win_rate={win_rate:.4f}; impulse_rows={summary.get('impulse_rows')}",
                "next_action": "split by signal_ret3_bps, entry_range_bps, symbol, and exit_hour_utc",
            }
        )

    if pnl_sum is not None and pnl_sum < 0:
        findings.append(
            {
                "finding_id": "F2_NEGATIVE_ROW_LEVEL_TOTAL_PNL",
                "severity": "HIGH",
                "claim": "Row-level impulse_long total PnL is negative.",
                "evidence": f"total_pnl={pnl_sum:.6f}; mean_pnl={pnl_mean}",
                "next_action": "compare losing trades against entry signal strength and exit timing",
            }
        )

    top_loss_symbols = summary.get("top_loss_symbols") or []
    if top_loss_symbols and pnl_sum is not None and pnl_sum < 0:
        worst_symbol, worst_symbol_pnl = top_loss_symbols[0]
        if worst_symbol_pnl < 0 and abs(worst_symbol_pnl) >= abs(pnl_sum) * 0.30:
            findings.append(
                {
                    "finding_id": "F3_SYMBOL_LOSS_CONCENTRATION",
                    "severity": "MEDIUM_HIGH",
                    "claim": "A meaningful part of impulse_long loss may be concentrated in one symbol.",
                    "evidence": f"worst_symbol={worst_symbol}; worst_symbol_pnl={worst_symbol_pnl:.6f}; total_pnl={pnl_sum:.6f}",
                    "next_action": "check whether symbol-level loss is regime-specific or due to one-off event",
                }
            )

    if gross_net_gap is not None and gross_net_gap > 0:
        findings.append(
            {
                "finding_id": "F4_COST_AND_SLIPPAGE_GAP_PRESENT",
                "severity": "MEDIUM",
                "claim": "Gross-to-net return gap exists and should be checked for cost drag.",
                "evidence": f"sum_gross_minus_sum_net_ret={gross_net_gap:.8f}",
                "next_action": "inspect fee_bps_total, entry_slip_bps, exit_slip_bps distributions",
            }
        )

    if not drift_gate_ready:
        findings.append(
            {
                "finding_id": "F5_CONTROL_GATE_NOT_READY",
                "severity": "CONTROL",
                "claim": "Global drift gate is not ready yet; no mutation is allowed.",
                "evidence": "closed<20 and drift_remaining>0",
                "next_action": "wait for threshold, then rerun v4 + drift review v3 + row-level diagnostic",
            }
        )

    if not findings:
        findings.append(
            {
                "finding_id": "F_INFO_NO_STRONG_ROW_LEVEL_FAILURE",
                "severity": "INFO",
                "claim": "No strong row-level failure pattern was detected.",
                "evidence": "available row-level sample does not breach configured diagnostic thresholds",
                "next_action": "continue collecting sample",
            }
        )

    return findings


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    locator = load_json(LOCATOR_V2_LATEST)
    drift = load_json(DRIFT_V3_LATEST)

    if locator is None:
        critical.append("locator_v2_latest_json_not_found")
        locator = {}

    if drift is None:
        attention.append("drift_v3_latest_json_not_found")
        drift = {}

    ledgers = choose_runtime_ledgers(locator)

    if not ledgers:
        critical.append("no_runtime_trade_ledger_found")

    all_rows: List[Dict[str, Any]] = []

    for ledger in ledgers:
        all_rows.extend(read_csv(ledger))

    summary = analyze_rows(all_rows)

    profiles = drift.get("family_profiles") or {}
    aggregate_profile = profiles.get("impulse_long") or {}

    closed = drift.get("closed")
    drift_remaining = drift.get("drift_remaining")
    capital_remaining = drift.get("capital_remaining")
    drift_gate_ready = bool(drift.get("drift_gate_ready") is True)

    findings = build_diagnosis(summary, aggregate_profile, drift_gate_ready)

    high_findings = [
        f for f in findings
        if str(f.get("severity")).upper() in {"HIGH", "MEDIUM_HIGH"}
    ]

    if critical:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_ROW_LEVEL_LEDGER"
        reason = "; ".join(critical)

    elif high_findings and not drift_gate_ready:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_PRE_THRESHOLD_ATTENTION"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_COLLECTING_NO_CAPITAL_CHANGE_RERUN_AT_DRIFT_GATE"
        reason = f"high_or_medium_high_findings={len(high_findings)}; drift_gate_ready=False"

    elif high_findings:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_ATTENTION"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "BUILD_READ_ONLY_RESEARCH_HYPOTHESES_FROM_ROW_LEVEL_FINDINGS"
        reason = f"high_or_medium_high_findings={len(high_findings)}"

    else:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_INFO"
        severity = "INFO"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "CONTINUE_MONITORING"
        reason = "no_high_severity_row_level_findings"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "diagnostic_status": diagnostic_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "ledger_sources": [str(p) for p in ledgers],
        "locator_v2_source": str(LOCATOR_V2_LATEST),
        "drift_v3_source": str(DRIFT_V3_LATEST),

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "aggregate_impulse_long_profile": aggregate_profile,
        "row_level_summary": summary,
        "row_level_findings": findings,

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "family_disable_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "impulse_long_row_level_diagnostic_v1_state.json"
    out_md = RUN_DIR / "impulse_long_row_level_diagnostic_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS IMPULSE LONG ROW LEVEL DIAGNOSTIC v1",
        "",
        f"diagnostic_status: {diagnostic_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Ledger Sources",
        "",
    ]

    for p in ledgers:
        md_lines.append(str(p))

    md_lines.extend(
        [
            "",
            "## Gate",
            "",
            f"closed: {closed}",
            f"drift_remaining: {drift_remaining}",
            f"capital_remaining: {capital_remaining}",
            f"drift_gate_ready: {drift_gate_ready}",
            "",
            "## Aggregate Profile",
            "",
            str(aggregate_profile),
            "",
            "## Row-Level Summary",
            "",
            json.dumps(summary, indent=2, default=str)[:12000],
            "",
            "## Findings",
            "",
        ]
    )

    for f in findings:
        md_lines.append(str(f))

    md_lines.extend(
        [
            "",
            "## Safety",
            "",
            "mutate_runtime_allowed: False",
            "launcher_allowed: False",
            "patch_runtime_allowed: False",
            "active_paper_allowed: False",
            "live_allowed: False",
            "capital_change_allowed: False",
            "family_disable_allowed: False",
            "real_orders_allowed: False",
            "execution_performed: False",
            "",
            f"critical: {critical}",
            f"attention: {attention}",
            f"info: {info}",
        ]
    )

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS IMPULSE LONG ROW LEVEL DIAGNOSTIC v1")
    print("=" * 100)
    print(f"diagnostic_status: {diagnostic_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("LEDGER SOURCES")
    print("-" * 100)
    for p in ledgers:
        print(p)
    print()
    print("GATE")
    print("-" * 100)
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print()
    print("ROW-LEVEL SUMMARY")
    print("-" * 100)
    print(f"available: {summary.get('available')}")
    print(f"all_rows_loaded: {summary.get('all_rows_loaded')}")
    print(f"impulse_rows: {summary.get('impulse_rows')}")
    print(f"win_rate: {summary.get('win_rate')}")
    print(f"pnl_summary: {summary.get('pnl_summary')}")
    print(f"net_ret_summary: {summary.get('net_ret_summary')}")
    print(f"fee_bps_summary: {summary.get('fee_bps_summary')}")
    print(f"entry_slip_bps_summary: {summary.get('entry_slip_bps_summary')}")
    print(f"exit_slip_bps_summary: {summary.get('exit_slip_bps_summary')}")
    print(f"top_loss_symbols: {summary.get('top_loss_symbols')}")
    print(f"top_win_symbols: {summary.get('top_win_symbols')}")
    print()
    print("FINDINGS")
    print("-" * 100)
    for f in findings:
        print(f)
    print()
    print("SAFETY")
    print("-" * 100)
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
