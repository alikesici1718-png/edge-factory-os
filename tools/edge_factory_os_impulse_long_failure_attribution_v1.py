from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


MODULE = "edge_factory_os_impulse_long_failure_attribution_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent
RUNTIME_DIR = BASE_DIR / "paper_run_gate_MASTER_UPPER_SYSTEM"

DRIFT_V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_drift_review_v3"
    / "family_drift_review_v3_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"impulse_long_failure_attribution_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "impulse_long_failure_attribution_latest.json"
LATEST_MD = OUT_ROOT / "impulse_long_failure_attribution_latest.md"


PNL_KEYS = [
    "realized_pnl",
    "pnl",
    "net_pnl",
    "total_pnl",
    "profit",
    "profit_usdt",
    "net_profit",
    "closed_pnl",
    "pnl_usdt",
]

RETURN_KEYS = [
    "ret",
    "return",
    "return_pct",
    "net_return",
    "net_return_pct",
    "net_bps",
    "return_bps",
]

SYMBOL_KEYS = [
    "symbol",
    "coin",
    "ticker",
    "instid",
    "inst_id",
    "instrument",
    "pair",
]

TIME_KEYS = [
    "timestamp",
    "time",
    "entry_time",
    "exit_time",
    "closed_at",
    "created_at",
    "datetime",
]

FAMILY_KEYS = [
    "family",
    "family_key",
    "strategy_family",
    "strategy",
    "source_family",
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


def to_float(v: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return float(int(v))
        if isinstance(v, (int, float)):
            if math.isnan(float(v)):
                return default
            return float(v)
        if isinstance(v, str):
            s = v.strip().replace(",", "").replace("%", "")
            if not s:
                return default
            m = re.search(r"-?\d+(?:\.\d+)?", s)
            return float(m.group(0)) if m else default
    except Exception:
        return default
    return default


def to_int(v: Any, default: int = 0) -> int:
    x = to_float(v, None)
    if x is None:
        return default
    return int(x)


def norm_key(k: str) -> str:
    return str(k).strip().lower().replace(" ", "_")


def pick_col(headers: List[str], aliases: List[str]) -> Optional[str]:
    normalized = {norm_key(h): h for h in headers}
    for alias in aliases:
        a = norm_key(alias)
        if a in normalized:
            return normalized[a]
    for h in headers:
        nh = norm_key(h)
        for alias in aliases:
            if norm_key(alias) in nh:
                return h
    return None


def row_mentions_impulse(row: Dict[str, Any], path: Path) -> bool:
    if "impulse_long" in str(path).lower():
        return True

    for k, v in row.items():
        text = f"{k}={v}".lower()
        if "impulse_long" in text:
            return True

    return False


def safe_read_csv_rows(path: Path, max_rows: int = 20000) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    meta = {
        "path": str(path),
        "read_ok": False,
        "error": None,
        "row_count_seen": 0,
        "impulse_row_count": 0,
        "headers": [],
    }

    rows: List[Dict[str, Any]] = []

    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            sample = f.read(4096)
            f.seek(0)

            if "impulse_long" not in sample.lower() and "family" not in sample.lower() and "pnl" not in sample.lower():
                return rows, meta

            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            meta["headers"] = headers

            for i, row in enumerate(reader):
                if i >= max_rows:
                    break
                meta["row_count_seen"] += 1

                if row_mentions_impulse(row, path):
                    rows.append(row)
                    meta["impulse_row_count"] += 1

        meta["read_ok"] = True

    except Exception as e:
        meta["error"] = repr(e)

    return rows, meta


def scan_runtime_impulse_rows() -> Dict[str, Any]:
    roots = []

    if RUNTIME_DIR.exists():
        roots.append(RUNTIME_DIR)

    roots.append(BASE_DIR)

    csv_files: List[Path] = []

    for root in roots:
        for p in root.rglob("*.csv"):
            ps = str(p).lower()

            # Skip generated OS reports where possible.
            if "edge_factory_os_" in ps and "paper_run_gate" not in ps:
                continue
            if ".git" in ps:
                continue

            csv_files.append(p)

    csv_files = sorted(set(csv_files), key=lambda p: str(p))

    all_rows: List[Dict[str, Any]] = []
    file_metas = []

    for path in csv_files[:300]:
        rows, meta = safe_read_csv_rows(path)
        file_metas.append(meta)

        for r in rows:
            r["_source_file"] = str(path)
            all_rows.append(r)

    return {
        "csv_file_count_scanned": len(csv_files[:300]),
        "csv_file_count_total_seen": len(csv_files),
        "impulse_row_count": len(all_rows),
        "file_metas": [
            m for m in file_metas
            if m.get("impulse_row_count", 0) > 0 or m.get("error")
        ][:50],
        "rows": all_rows,
    }


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {
            "available": False,
            "reason": "no_impulse_long_rows_found_in_runtime_csvs",
        }

    headers = list(rows[0].keys())

    pnl_col = pick_col(headers, PNL_KEYS)
    ret_col = pick_col(headers, RETURN_KEYS)
    symbol_col = pick_col(headers, SYMBOL_KEYS)
    time_col = pick_col(headers, TIME_KEYS)

    pnl_values = []
    ret_values = []
    symbol_pnl = defaultdict(float)
    symbol_count = Counter()
    source_count = Counter()

    for row in rows:
        source_count[row.get("_source_file", "unknown")] += 1

        symbol = "UNKNOWN"
        if symbol_col:
            symbol = str(row.get(symbol_col) or "UNKNOWN").strip() or "UNKNOWN"

        pnl = to_float(row.get(pnl_col), None) if pnl_col else None
        ret = to_float(row.get(ret_col), None) if ret_col else None

        if pnl is not None:
            pnl_values.append(pnl)
            symbol_pnl[symbol] += pnl

        if ret is not None:
            ret_values.append(ret)

        symbol_count[symbol] += 1

    pnl_summary = None

    if pnl_values:
        wins = [x for x in pnl_values if x > 0]
        losses = [x for x in pnl_values if x < 0]
        pnl_summary = {
            "count": len(pnl_values),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(pnl_values) if pnl_values else None,
            "total_pnl": sum(pnl_values),
            "mean_pnl": sum(pnl_values) / len(pnl_values),
            "best_pnl": max(pnl_values),
            "worst_pnl": min(pnl_values),
        }

    ret_summary = None

    if ret_values:
        wins = [x for x in ret_values if x > 0]
        losses = [x for x in ret_values if x < 0]
        ret_summary = {
            "count": len(ret_values),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(ret_values) if ret_values else None,
            "total_return": sum(ret_values),
            "mean_return": sum(ret_values) / len(ret_values),
            "best_return": max(ret_values),
            "worst_return": min(ret_values),
        }

    top_loss_symbols = sorted(symbol_pnl.items(), key=lambda x: x[1])[:10]
    top_win_symbols = sorted(symbol_pnl.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "available": True,
        "row_count": len(rows),
        "detected_columns": {
            "pnl_col": pnl_col,
            "return_col": ret_col,
            "symbol_col": symbol_col,
            "time_col": time_col,
        },
        "pnl_summary": pnl_summary,
        "return_summary": ret_summary,
        "symbol_count_top": symbol_count.most_common(20),
        "top_loss_symbols": top_loss_symbols,
        "top_win_symbols": top_win_symbols,
        "source_count_top": source_count.most_common(10),
    }


def build_hypotheses(profile: Dict[str, Any], judgement: Dict[str, Any], runtime_summary: Dict[str, Any], drift_gate_ready: bool) -> List[Dict[str, Any]]:
    hypotheses = []

    closed = to_int(profile.get("closed"), 0)
    win_rate = to_float(profile.get("win_rate"), None)
    realized = to_float(profile.get("realized"), None)
    unrealized = to_float(profile.get("unrealized"), None)
    total = to_float(profile.get("total"), None)

    if win_rate is not None and win_rate < 0.35:
        hypotheses.append({
            "hypothesis_id": "H1_LOW_PRECISION_ENTRY_OR_BAD_REGIME",
            "severity": "HIGH",
            "claim": "impulse_long entry condition currently has low realized precision.",
            "evidence": f"closed={closed}, win_rate={win_rate:.3f}",
            "next_read_only_test": "Split impulse_long closed trades by market regime, volatility bucket, impulse strength, and entry hour. Look for pockets where win_rate normalizes.",
            "action_allowed_now": False,
        })

    if total is not None and total < 0:
        hypotheses.append({
            "hypothesis_id": "H2_NEGATIVE_TOTAL_EDGE_DRIFT_OR_COST_DRAG",
            "severity": "HIGH",
            "claim": "impulse_long total contribution is negative at the current sample.",
            "evidence": f"total_pnl={total:.4f}",
            "next_read_only_test": "Compare live/paper impulse_long average net PnL against backtest expected net PnL after fees/slippage. Attribute gap to entry, exit, or execution.",
            "action_allowed_now": False,
        })

    if realized is not None and realized < 0 and unrealized is not None and unrealized > 0:
        hypotheses.append({
            "hypothesis_id": "H3_EXIT_OR_HOLDING_SELECTION_PROBLEM",
            "severity": "MEDIUM_HIGH",
            "claim": "Closed impulse_long trades are materially negative while current open exposure is positive.",
            "evidence": f"realized={realized:.4f}, unrealized={unrealized:.4f}",
            "next_read_only_test": "Separate losing closed trades from currently open winners. Inspect exit timing, max favorable excursion, and whether exits close trades before rebound continuation.",
            "action_allowed_now": False,
        })

    if not drift_gate_ready:
        hypotheses.append({
            "hypothesis_id": "H4_SAMPLE_GATE_NOT_READY",
            "severity": "CONTROL",
            "claim": "Drift gate is not ready yet; no capital or runtime action is allowed.",
            "evidence": f"closed={closed}, required_global_closed>=20 or drift_remaining<=0",
            "next_read_only_test": "Wait for the next closed trade, then rerun v4, drift review v3, and this attribution module.",
            "action_allowed_now": False,
        })

    pnl_summary = runtime_summary.get("pnl_summary") if runtime_summary.get("available") else None

    if pnl_summary and pnl_summary.get("worst_pnl") is not None:
        hypotheses.append({
            "hypothesis_id": "H5_TAIL_LOSS_CONCENTRATION_CHECK",
            "severity": "MEDIUM",
            "claim": "Runtime rows are available; check whether losses are concentrated in a few symbols or events.",
            "evidence": f"worst_pnl={pnl_summary.get('worst_pnl')}, total_pnl={pnl_summary.get('total_pnl')}",
            "next_read_only_test": "Review top_loss_symbols and source rows. If a small number of symbols dominate losses, create a symbol/regime concentration diagnostic.",
            "action_allowed_now": False,
        })

    if not hypotheses:
        hypotheses.append({
            "hypothesis_id": "H0_NO_STRONG_FAILURE_ATTRIBUTION",
            "severity": "INFO",
            "claim": "No strong failure attribution from current aggregate metrics.",
            "evidence": "Metrics are either missing or not severe enough.",
            "next_read_only_test": "Collect more sample and rerun attribution.",
            "action_allowed_now": False,
        })

    return hypotheses


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical = []
    attention = []
    info = []

    drift = load_json(DRIFT_V3_LATEST)

    if drift is None:
        critical.append("family_drift_review_v3_latest_json_not_found")
        drift = {}

    closed = to_int(drift.get("closed"), 0)
    drift_remaining = to_int(drift.get("drift_remaining"), 999999)
    capital_remaining = to_int(drift.get("capital_remaining"), 999999)
    drift_gate_ready = bool(drift.get("drift_gate_ready") is True)

    profiles = drift.get("family_profiles") or {}
    judgements = drift.get("family_judgements") or {}

    impulse_profile = profiles.get("impulse_long") or {}
    impulse_judgement = judgements.get("impulse_long") or {}

    if not impulse_profile:
        critical.append("impulse_long_profile_missing_from_drift_v3")

    if not impulse_judgement:
        attention.append("impulse_long_judgement_missing_from_drift_v3")

    scan = scan_runtime_impulse_rows()
    runtime_summary = summarize_rows(scan.get("rows", []))

    hypotheses = build_hypotheses(
        profile=impulse_profile,
        judgement=impulse_judgement,
        runtime_summary=runtime_summary,
        drift_gate_ready=drift_gate_ready,
    )

    high_count = sum(1 for h in hypotheses if str(h.get("severity")).upper() == "HIGH")
    med_high_count = sum(1 for h in hypotheses if str(h.get("severity")).upper() == "MEDIUM_HIGH")

    if critical:
        attribution_status = "IMPULSE_LONG_FAILURE_ATTRIBUTION_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_MISSING_DRIFT_REVIEW_INPUT"
        reason = "; ".join(critical)

    elif not drift_gate_ready:
        attribution_status = "IMPULSE_LONG_FAILURE_ATTRIBUTION_PRE_THRESHOLD_WATCH"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_COLLECTING_UNTIL_DRIFT_GATE_READY_NO_CAPITAL_CHANGE"
        reason = f"closed={closed}; drift_remaining={drift_remaining}; pre_threshold_failure_hypotheses_ready"

    elif high_count > 0 or med_high_count > 0:
        attribution_status = "IMPULSE_LONG_FAILURE_ATTRIBUTION_ATTENTION"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "RUN_READ_ONLY_IMPULSE_LONG_REGIME_AND_EXIT_DIAGNOSTICS"
        reason = f"high_hypotheses={high_count}; medium_high_hypotheses={med_high_count}"

    else:
        attribution_status = "IMPULSE_LONG_FAILURE_ATTRIBUTION_INFO"
        severity = "INFO"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "CONTINUE_MONITORING_NO_CAPITAL_CHANGE"
        reason = "no_high_confidence_failure_mode_yet"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "attribution_status": attribution_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "drift_v3_source": str(DRIFT_V3_LATEST),

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "impulse_long_profile": impulse_profile,
        "impulse_long_judgement": impulse_judgement,

        "runtime_scan": {
            "csv_file_count_scanned": scan.get("csv_file_count_scanned"),
            "csv_file_count_total_seen": scan.get("csv_file_count_total_seen"),
            "impulse_row_count": scan.get("impulse_row_count"),
            "file_metas": scan.get("file_metas"),
        },
        "runtime_trade_summary": runtime_summary,

        "failure_hypotheses": hypotheses,

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

    out_json = RUN_DIR / "impulse_long_failure_attribution_v1_state.json"
    out_md = RUN_DIR / "impulse_long_failure_attribution_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS IMPULSE LONG FAILURE ATTRIBUTION v1",
        "",
        f"attribution_status: {attribution_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Gate",
        "",
        f"closed: {closed}",
        f"drift_remaining: {drift_remaining}",
        f"capital_remaining: {capital_remaining}",
        f"drift_gate_ready: {drift_gate_ready}",
        "",
        "## impulse_long",
        "",
        f"profile: {impulse_profile}",
        f"judgement: {impulse_judgement}",
        "",
        "## Runtime Trade Summary",
        "",
        f"{runtime_summary}",
        "",
        "## Failure Hypotheses",
        "",
    ]

    for h in hypotheses:
        md_lines.append(str(h))

    md_lines.extend([
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
    ])

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS IMPULSE LONG FAILURE ATTRIBUTION v1")
    print("=" * 100)
    print(f"attribution_status: {attribution_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("GATE")
    print("-" * 100)
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print()
    print("IMPULSE_LONG")
    print("-" * 100)
    print(f"profile: {impulse_profile}")
    print(f"judgement: {impulse_judgement}")
    print()
    print("RUNTIME TRADE SUMMARY")
    print("-" * 100)
    print(runtime_summary)
    print()
    print("FAILURE HYPOTHESES")
    print("-" * 100)
    for h in hypotheses:
        print(h)
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
