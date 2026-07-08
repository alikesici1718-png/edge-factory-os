from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_impulse_long_evidence_locator_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent
RUNTIME_DIR = BASE_DIR / "paper_run_gate_MASTER_UPPER_SYSTEM"

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"impulse_long_evidence_locator_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "impulse_long_evidence_locator_v2_latest.json"
LATEST_MD = OUT_ROOT / "impulse_long_evidence_locator_v2_latest.md"

SEARCH_ROOTS = [
    RUNTIME_DIR,
    BASE_DIR,
]

FILE_EXTS = {".csv", ".json", ".jsonl", ".txt", ".log"}

AGGREGATE_PATH_TERMS = [
    "family_summary",
    "family_performance",
    "performance_discipline",
    "family_drift_review",
    "cycle_operator",
    "error_acknowledgement",
    "error_inventory",
    "state_reader",
    "control_tower",
    "sample_maturity",
    "trigger_engine",
]

TRADE_LEDGER_PATH_TERMS = [
    "trade",
    "trades",
    "ledger",
    "fill",
    "fills",
    "order",
    "orders",
    "position",
    "positions",
    "closed",
    "paper_run_gate_master_upper_system",
    "logger",
]

TRADE_COLUMN_TERMS = [
    "symbol",
    "instid",
    "inst_id",
    "ticker",
    "entry",
    "exit",
    "entry_time",
    "exit_time",
    "closed_at",
    "timestamp",
    "side",
    "qty",
    "size",
    "price",
    "entry_price",
    "exit_price",
    "pnl",
    "realized",
    "fee",
    "slippage",
    "return",
    "bps",
]

AGGREGATE_COLUMN_TERMS = [
    "family_key",
    "closed_trades",
    "open_positions",
    "pending_entries",
    "win_rate_closed",
    "profile_key",
    "profile_severity",
    "discipline_key",
    "discipline_severity",
    "allowed_scope",
    "recommended_action",
]


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def safe_text(path: Path, limit: int = 500_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def norm(x: Any) -> str:
    return str(x or "").strip().lower()


def path_allowed(path: Path) -> bool:
    p = norm(path)

    if ".git" in p or "__pycache__" in p:
        return False

    if path.suffix.lower() not in FILE_EXTS:
        return False

    try:
        size = path.stat().st_size
    except Exception:
        return False

    if size <= 0 or size > 50_000_000:
        return False

    return True


def classify_csv(path: Path) -> Dict[str, Any]:
    result = {
        "file_type": "csv",
        "read_ok": False,
        "headers": [],
        "row_count_sampled": 0,
        "impulse_row_count": 0,
        "unique_symbols_sampled": [],
        "symbol_count": 0,
        "trade_column_hits": [],
        "aggregate_column_hits": [],
        "sample_impulse_rows": [],
        "classification": "UNKNOWN",
        "classification_reason": [],
        "score_trade_ledger": 0,
        "score_aggregate": 0,
        "error": None,
    }

    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            result["headers"] = headers

            lower_headers = [norm(h) for h in headers]

            trade_hits = []
            for term in TRADE_COLUMN_TERMS:
                if any(term in h for h in lower_headers):
                    trade_hits.append(term)

            aggregate_hits = []
            for term in AGGREGATE_COLUMN_TERMS:
                if any(term in h for h in lower_headers):
                    aggregate_hits.append(term)

            result["trade_column_hits"] = sorted(set(trade_hits))
            result["aggregate_column_hits"] = sorted(set(aggregate_hits))

            symbol_values = set()

            symbol_cols = [
                h for h in headers
                if any(term in norm(h) for term in ["symbol", "instid", "inst_id", "ticker", "coin"])
            ]

            for i, row in enumerate(reader):
                if i >= 10000:
                    break

                result["row_count_sampled"] += 1
                row_text = json.dumps(row, default=str).lower()

                for sc in symbol_cols:
                    v = str(row.get(sc) or "").strip()
                    if v:
                        symbol_values.add(v)

                if "impulse_long" in row_text or "impulse" in row_text:
                    result["impulse_row_count"] += 1

                    if len(result["sample_impulse_rows"]) < 5:
                        result["sample_impulse_rows"].append(row)

            result["unique_symbols_sampled"] = sorted(list(symbol_values))[:50]
            result["symbol_count"] = len(symbol_values)
            result["read_ok"] = True

    except Exception as e:
        result["error"] = repr(e)
        return result

    p = norm(path)

    trade_score = 0
    agg_score = 0
    reasons = []

    trade_score += len(result["trade_column_hits"]) * 4
    agg_score += len(result["aggregate_column_hits"]) * 6

    if result["row_count_sampled"] >= 10:
        trade_score += 10
        reasons.append("row_count_ge_10")
    else:
        agg_score += 5
        reasons.append("row_count_lt_10")

    if result["impulse_row_count"] >= 5:
        trade_score += 20
        reasons.append("impulse_rows_ge_5")
    elif result["impulse_row_count"] == 1:
        agg_score += 10
        reasons.append("single_impulse_row")

    if result["symbol_count"] >= 3:
        trade_score += 15
        reasons.append("symbol_count_ge_3")
    elif result["symbol_count"] == 0:
        agg_score += 5
        reasons.append("no_symbol_diversity")

    for term in TRADE_LEDGER_PATH_TERMS:
        if term in p:
            trade_score += 4

    for term in AGGREGATE_PATH_TERMS:
        if term in p:
            agg_score += 12

    # Strong aggregate pattern: one family row with family summary metrics.
    if (
        result["impulse_row_count"] <= 1
        and len(result["aggregate_column_hits"]) >= 3
        and result["row_count_sampled"] <= 10
    ):
        agg_score += 40
        reasons.append("strong_family_summary_shape")

    # Strong trade ledger pattern.
    if (
        result["row_count_sampled"] >= 10
        and len(result["trade_column_hits"]) >= 5
        and result["symbol_count"] >= 2
    ):
        trade_score += 40
        reasons.append("strong_trade_ledger_shape")

    result["score_trade_ledger"] = trade_score
    result["score_aggregate"] = agg_score
    result["classification_reason"] = reasons

    if trade_score >= agg_score + 15 and trade_score >= 35:
        result["classification"] = "ROW_LEVEL_TRADE_LEDGER_CANDIDATE"
    elif agg_score >= trade_score:
        result["classification"] = "AGGREGATE_OR_FAMILY_SUMMARY"
    else:
        result["classification"] = "AMBIGUOUS_EVIDENCE_CANDIDATE"

    return result


def classify_text_or_json(path: Path, text: str) -> Dict[str, Any]:
    lower = text.lower()
    p = norm(path)

    impulse_hits = lower.count("impulse_long")
    family_hits = lower.count("family_key")
    pnl_hits = lower.count("pnl")
    symbol_hits = lower.count("symbol")

    trade_score = 0
    agg_score = 0
    reasons = []

    if impulse_hits > 0:
        trade_score += 5
        agg_score += 5

    if symbol_hits >= 5 and pnl_hits >= 5:
        trade_score += 20
        reasons.append("many_symbol_and_pnl_mentions")

    if family_hits >= 1 and impulse_hits <= 3:
        agg_score += 20
        reasons.append("family_summary_like_mentions")

    for term in TRADE_LEDGER_PATH_TERMS:
        if term in p:
            trade_score += 4

    for term in AGGREGATE_PATH_TERMS:
        if term in p:
            agg_score += 12

    if impulse_hits >= 5:
        trade_score += 15
        reasons.append("many_impulse_mentions")

    if trade_score >= agg_score + 15 and trade_score >= 25:
        classification = "ROW_LEVEL_TEXT_OR_JSON_CANDIDATE"
    elif agg_score >= trade_score:
        classification = "AGGREGATE_OR_TEXT_SUMMARY"
    else:
        classification = "AMBIGUOUS_TEXT_OR_JSON_CANDIDATE"

    return {
        "file_type": path.suffix.lower().replace(".", ""),
        "impulse_hits": impulse_hits,
        "family_hits": family_hits,
        "pnl_hits": pnl_hits,
        "symbol_hits": symbol_hits,
        "score_trade_ledger": trade_score,
        "score_aggregate": agg_score,
        "classification": classification,
        "classification_reason": reasons,
        "sample_matches": extract_matches(text),
    }


def extract_matches(text: str) -> List[Dict[str, Any]]:
    matches = []
    for i, line in enumerate(text.splitlines()[:20000], start=1):
        l = line.lower()
        if "impulse_long" in l or "impulse" in l:
            matches.append({"line": i, "text": line[:500]})
        if len(matches) >= 5:
            break
    return matches


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    candidates = []

    seen = set()

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if not path_allowed(path):
                continue

            rp = str(path.resolve()).lower()
            if rp in seen:
                continue
            seen.add(rp)

            text = safe_text(path)
            if not text:
                continue

            lower = text.lower()

            if "impulse_long" not in lower and "impulse" not in lower:
                continue

            if path.suffix.lower() == ".csv":
                probe = classify_csv(path)
            else:
                probe = classify_text_or_json(path, text)

            candidates.append({
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "suffix": path.suffix.lower(),
                "classification": probe.get("classification"),
                "score_trade_ledger": probe.get("score_trade_ledger"),
                "score_aggregate": probe.get("score_aggregate"),
                "probe": probe,
            })

    candidates.sort(
        key=lambda x: (
            1 if "ROW_LEVEL" in str(x.get("classification")) else 0,
            x.get("score_trade_ledger") or 0,
            -(x.get("score_aggregate") or 0),
        ),
        reverse=True,
    )

    row_level = [
        c for c in candidates
        if str(c.get("classification")).startswith("ROW_LEVEL")
    ]

    aggregate = [
        c for c in candidates
        if "AGGREGATE" in str(c.get("classification"))
    ]

    ambiguous = [
        c for c in candidates
        if "AMBIGUOUS" in str(c.get("classification"))
    ]

    if row_level:
        locator_status = "IMPULSE_LONG_EVIDENCE_LOCATOR_V2_TRUE_ROW_LEVEL_CANDIDATES_FOUND"
        severity = "INFO"
        next_action = "BUILD_IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_FROM_TRUE_LEDGER"
        reason = f"true_row_level_candidate_count={len(row_level)}"
    elif aggregate:
        locator_status = "IMPULSE_LONG_EVIDENCE_LOCATOR_V2_ONLY_AGGREGATE_EVIDENCE_FOUND"
        severity = "ATTENTION"
        next_action = "ADD_OR_FIND_READ_ONLY_TRADE_LEDGER_EXPORTER"
        reason = f"aggregate_candidate_count={len(aggregate)}; no_true_row_level_trade_ledger_found"
    elif ambiguous:
        locator_status = "IMPULSE_LONG_EVIDENCE_LOCATOR_V2_ONLY_AMBIGUOUS_EVIDENCE_FOUND"
        severity = "ATTENTION"
        next_action = "REVIEW_AMBIGUOUS_CANDIDATES_OR_ADD_LEDGER_EXPORTER"
        reason = f"ambiguous_candidate_count={len(ambiguous)}"
    else:
        locator_status = "IMPULSE_LONG_EVIDENCE_LOCATOR_V2_NO_EVIDENCE_FOUND"
        severity = "ATTENTION"
        next_action = "ADD_READ_ONLY_TRADE_LEDGER_EXPORTER"
        reason = "no impulse_long evidence found"

    class_counts = Counter(c.get("classification") for c in candidates)

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "locator_status": locator_status,
        "severity": severity,
        "next_action": next_action,
        "reason": reason,

        "search_roots": [str(p) for p in SEARCH_ROOTS],
        "candidate_count": len(candidates),
        "classification_counts": dict(class_counts),

        "true_row_level_candidate_count": len(row_level),
        "aggregate_candidate_count": len(aggregate),
        "ambiguous_candidate_count": len(ambiguous),

        "top_row_level_candidates": row_level[:20],
        "top_aggregate_candidates": aggregate[:20],
        "top_ambiguous_candidates": ambiguous[:20],

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "family_disable_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,
    }

    out_json = RUN_DIR / "impulse_long_evidence_locator_v2_state.json"
    out_md = RUN_DIR / "impulse_long_evidence_locator_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS IMPULSE LONG EVIDENCE LOCATOR v2",
        "",
        f"locator_status: {locator_status}",
        f"severity: {severity}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        f"candidate_count: {len(candidates)}",
        f"classification_counts: {dict(class_counts)}",
        f"true_row_level_candidate_count: {len(row_level)}",
        f"aggregate_candidate_count: {len(aggregate)}",
        f"ambiguous_candidate_count: {len(ambiguous)}",
        "",
        "## Top Row-Level Candidates",
        "",
    ]

    for c in row_level[:10]:
        md_lines.append(json.dumps(c, indent=2, default=str)[:4000])

    md_lines.append("")
    md_lines.append("## Top Aggregate Candidates")
    md_lines.append("")

    for c in aggregate[:10]:
        md_lines.append(json.dumps(c, indent=2, default=str)[:4000])

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
    ])

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS IMPULSE LONG EVIDENCE LOCATOR v2")
    print("=" * 100)
    print(f"locator_status: {locator_status}")
    print(f"severity: {severity}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print(f"candidate_count: {len(candidates)}")
    print(f"classification_counts: {dict(class_counts)}")
    print(f"true_row_level_candidate_count: {len(row_level)}")
    print(f"aggregate_candidate_count: {len(aggregate)}")
    print(f"ambiguous_candidate_count: {len(ambiguous)}")
    print()
    print("TOP ROW-LEVEL CANDIDATES")
    print("-" * 100)
    for c in row_level[:10]:
        print(f"path={c['path']}")
        print(f"classification={c['classification']}")
        print(f"trade_score={c['score_trade_ledger']} aggregate_score={c['score_aggregate']}")
        probe = c.get("probe", {})
        print(f"headers={probe.get('headers')}")
        print(f"row_count_sampled={probe.get('row_count_sampled')} impulse_row_count={probe.get('impulse_row_count')} symbol_count={probe.get('symbol_count')}")
        print()
    print("TOP AGGREGATE CANDIDATES")
    print("-" * 100)
    for c in aggregate[:10]:
        print(f"path={c['path']}")
        print(f"classification={c['classification']}")
        print(f"trade_score={c['score_trade_ledger']} aggregate_score={c['score_aggregate']}")
        probe = c.get("probe", {})
        print(f"headers={probe.get('headers')}")
        print(f"row_count_sampled={probe.get('row_count_sampled')} impulse_row_count={probe.get('impulse_row_count')} symbol_count={probe.get('symbol_count')}")
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
