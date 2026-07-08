#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY ROLLING OOS VALIDATOR v2 CLEANUP
=============================================

Purpose
-------
Data-hygiene / active-family cleanup layer for the Edge Factory OS.

The v1 Rolling OOS Validator produced useful active-family results, but it also allowed
some broad-scan / summary / numeric / garbage family names into the report. This v2 module
DOES NOT rerun the full historical scan. It consumes the latest v1 outputs and separates:

    1) active master families
    2) disabled known family
    3) clean research candidates
    4) garbage / summary / malformed family rows

It creates clean files that future OS modules can use safely.

It does NOT start paper/live trading.
It DOES NOT edit contracts/loggers.
It DOES NOT modify v1 outputs.

Run:
    python "C:\Users\alike\edge_factory_rolling_oos_validator_v2.py"

Optional explicit v1 folder:
    python "C:\Users\alike\edge_factory_rolling_oos_validator_v2.py" ^
      --oos_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_rolling_oos_validator\rolling_oos_20260510_165749"

Outputs:
    <workspace>\edge_factory_rolling_oos_validator_v2\rolling_oos_v2_YYYYMMDD_HHMMSS\
        rolling_oos_v2_report.md
        active_family_decisions.json
        active_family_summary.csv
        known_disabled_family_summary.csv
        candidate_family_watchlist.csv
        garbage_family_rows.csv
        clean_os_family_state_seed.json
        v2_cleanup_manifest.json

Design rule
-----------
Only these are active master families:
    old_short, impulse_long, market_relative_short, weak_market_short

session_short is known but disabled.
Everything else is either a research candidate or garbage/noise.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

ACTIVE_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]
DISABLED_KNOWN_FAMILIES = ["session_short"]
KNOWN_FAMILIES = ACTIVE_FAMILIES + DISABLED_KNOWN_FAMILIES

RESEARCH_CANDIDATE_EXACT_NAMES = {
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
    "relative_strength_continuation_long",
}

RESEARCH_CANDIDATE_HINTS = [
    "reversion",
    "snapback",
    "panic",
    "capitulation",
    "continuation",
]

EXCLUDED_RESEARCH_NAME_HINTS = [
    "volume_desc",
    "volume_asc",
    "all_four",
    "all_existing",
    "impulse_only",
    "market_only",
    "old_only",
    "weak_only",
]

GARBAGE_VALUES = {"", "unknown", "nan", "none", "null", "{}", "[]", "all", "total", "summary"}


@dataclass
class ClassifiedRow:
    family_key: str
    classification: str
    reason: str
    decision: str
    confidence: str
    trade_count: int
    total_pnl: float
    avg_pnl: float
    win_rate: float
    profit_factor: float
    test_trade_count: int
    test_avg_pnl: float
    raw: Dict[str, Any]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        if isinstance(x, str):
            s = x.strip().lower()
            if s in {"", "none", "null", "nan", "inf", "infinity"}:
                return default
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except Exception:
        return default


def safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(round(safe_float(x, default)))
    except Exception:
        return default


def normalize_name(x: Any) -> str:
    s = str(x).strip().lower()
    s = s.replace("-", "_").replace(" ", "_")
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_oos_dir(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    return latest_child_dir(workspace / "edge_factory_rolling_oos_validator", "rolling_oos_")


def load_v1_decisions(oos_dir: Path) -> List[Dict[str, Any]]:
    p = oos_dir / "rolling_oos_decisions.json"
    if not p.exists():
        raise FileNotFoundError(f"Missing rolling_oos_decisions.json: {p}")
    obj = load_json(p)
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict) and isinstance(obj.get("decisions"), list):
        return [x for x in obj["decisions"] if isinstance(x, dict)]
    return []


def extract_metrics(row: Dict[str, Any]) -> Dict[str, Any]:
    m = row.get("metrics") or {}
    o = row.get("oos_metrics") or {}
    test = o.get("test") if isinstance(o.get("test"), dict) else {}
    return {
        "trade_count": safe_int(m.get("trade_count")),
        "total_pnl": safe_float(m.get("total_pnl")),
        "avg_pnl": safe_float(m.get("avg_pnl")),
        "win_rate": safe_float(m.get("win_rate")),
        "profit_factor": safe_float(m.get("profit_factor")),
        "test_trade_count": safe_int(test.get("trade_count")),
        "test_avg_pnl": safe_float(test.get("avg_pnl")),
    }


def is_numeric_or_malformed(name: str) -> bool:
    if name in GARBAGE_VALUES:
        return True
    if name.isdigit():
        return True
    try:
        float(name)
        return True
    except Exception:
        pass
    if len(name) < 3:
        return True
    # mostly punctuation/braces
    if re.fullmatch(r"[{}\[\](),.\-_/\\]+", name):
        return True
    return False


def is_research_candidate_name(name: str) -> bool:
    if name in KNOWN_FAMILIES:
        return False
    if is_numeric_or_malformed(name):
        return False
    if any(h in name for h in EXCLUDED_RESEARCH_NAME_HINTS):
        return False
    if name in RESEARCH_CANDIDATE_EXACT_NAMES:
        return True
    return any(h in name for h in RESEARCH_CANDIDATE_HINTS)


def classify_row(row: Dict[str, Any]) -> ClassifiedRow:
    fam = normalize_name(row.get("family_key", "unknown"))
    decision = str(row.get("decision", "UNKNOWN"))
    confidence = str(row.get("confidence", "low"))
    metrics = extract_metrics(row)

    if fam in ACTIVE_FAMILIES:
        classification = "ACTIVE_MASTER_FAMILY"
        reason = "known active MASTER_UPPER_SYSTEM family"
    elif fam in DISABLED_KNOWN_FAMILIES:
        classification = "KNOWN_DISABLED_FAMILY"
        reason = "known family but disabled by current architecture"
    elif is_numeric_or_malformed(fam):
        classification = "GARBAGE_OR_SUMMARY_ROW"
        reason = "numeric/malformed/summary-like family key; must not enter OS decisions"
    elif is_research_candidate_name(fam) and decision in {"STRONG_CANDIDATE", "PASS_CANDIDATE"} and metrics["trade_count"] >= 100 and metrics["avg_pnl"] > 0 and metrics["test_avg_pnl"] > 0:
        classification = "RESEARCH_CANDIDATE"
        reason = "non-master candidate name pattern plus positive broad-scan/OOS metrics; isolate before any lifecycle inclusion"
    elif decision in {"STRONG_CANDIDATE", "PASS_CANDIDATE"} and metrics["trade_count"] >= 250 and metrics["profit_factor"] >= 1.25 and metrics["avg_pnl"] > 0 and metrics["test_avg_pnl"] > 0 and not any(h in fam for h in EXCLUDED_RESEARCH_NAME_HINTS):
        classification = "RESEARCH_CANDIDATE"
        reason = "non-master row passed broad scan with sufficient sample; research-only"
    else:
        classification = "UNCLASSIFIED_NON_MASTER"
        reason = "non-master row; insufficient quality or unknown naming; exclude from OS decisions"

    return ClassifiedRow(
        family_key=fam,
        classification=classification,
        reason=reason,
        decision=decision,
        confidence=confidence,
        trade_count=metrics["trade_count"],
        total_pnl=metrics["total_pnl"],
        avg_pnl=metrics["avg_pnl"],
        win_rate=metrics["win_rate"],
        profit_factor=metrics["profit_factor"],
        test_trade_count=metrics["test_trade_count"],
        test_avg_pnl=metrics["test_avg_pnl"],
        raw=row,
    )


def classify_rows(rows: List[Dict[str, Any]]) -> List[ClassifiedRow]:
    classified = [classify_row(r) for r in rows]
    # Deduplicate: keep strongest/largest row per family+classification.
    best: Dict[Tuple[str, str], ClassifiedRow] = {}
    decision_rank = {
        "STRONG_CANDIDATE": 5,
        "PASS_CANDIDATE": 4,
        "WATCH_WEAK_OOS": 3,
        "REDUCE_OR_BACKUP_ONLY": 2,
        "INSUFFICIENT_DATA": 1,
        "NO_USABLE_DATA": 0,
        "REJECT_OR_DISABLE": -1,
    }
    for c in classified:
        key = (c.family_key, c.classification)
        old = best.get(key)
        if old is None:
            best[key] = c
            continue
        old_rank = decision_rank.get(old.decision, 0)
        new_rank = decision_rank.get(c.decision, 0)
        if (new_rank, c.trade_count, c.profit_factor) > (old_rank, old.trade_count, old.profit_factor):
            best[key] = c
    return list(best.values())


def row_dicts(rows: List[ClassifiedRow], include_raw: bool = False) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        d = asdict(r)
        if not include_raw:
            d.pop("raw", None)
        out.append(d)
    return out


def build_active_state_seed(active: List[ClassifiedRow], disabled: List[ClassifiedRow]) -> Dict[str, Any]:
    by_fam = {r.family_key: r for r in active + disabled}
    seed = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "edge_factory_rolling_oos_validator_v2_cleanup",
        "active_master_families": ACTIVE_FAMILIES,
        "disabled_known_families": DISABLED_KNOWN_FAMILIES,
        "families": {},
        "hard_rules": [
            "Only ACTIVE_MASTER_FAMILY rows may feed lifecycle/capital OS modules directly.",
            "RESEARCH_CANDIDATE rows must go through isolated validation first.",
            "GARBAGE_OR_SUMMARY_ROW and UNCLASSIFIED_NON_MASTER rows are excluded from decisions.",
        ],
    }
    for fam in KNOWN_FAMILIES:
        r = by_fam.get(fam)
        if r is None:
            seed["families"][fam] = {
                "classification": "MISSING_FROM_V1",
                "decision": "NO_USABLE_DATA",
                "trade_count": 0,
                "allowed_to_feed_lifecycle": fam in ACTIVE_FAMILIES,
            }
        else:
            seed["families"][fam] = {
                "classification": r.classification,
                "decision": r.decision,
                "confidence": r.confidence,
                "trade_count": r.trade_count,
                "total_pnl": r.total_pnl,
                "avg_pnl": r.avg_pnl,
                "win_rate": r.win_rate,
                "profit_factor": r.profit_factor,
                "test_trade_count": r.test_trade_count,
                "test_avg_pnl": r.test_avg_pnl,
                "allowed_to_feed_lifecycle": r.classification == "ACTIVE_MASTER_FAMILY",
            }
    return seed


def write_report(path: Path, context: Dict[str, Any], active: List[ClassifiedRow], disabled: List[ClassifiedRow], candidates: List[ClassifiedRow], garbage: List[ClassifiedRow], other: List[ClassifiedRow]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Rolling OOS Validator v2 Cleanup Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"V1 source: `{context['oos_dir']}`")
    lines.append("")

    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Active master families: **{len(active)}**")
    lines.append(f"- Known disabled families: **{len(disabled)}**")
    lines.append(f"- Research candidates: **{len(candidates)}**")
    lines.append(f"- Garbage/summary rows: **{len(garbage)}**")
    lines.append(f"- Other excluded non-master rows: **{len(other)}**")
    lines.append("")

    lines.append("## Clean active-family decisions")
    lines.append("")
    lines.append("| Family | Decision | Confidence | Trades | Total PnL | Avg PnL | WR | PF | Test Avg |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in sorted(active, key=lambda x: ACTIVE_FAMILIES.index(x.family_key) if x.family_key in ACTIVE_FAMILIES else 999):
        lines.append(f"| {r.family_key} | {r.decision} | {r.confidence} | {r.trade_count} | {r.total_pnl:.6f} | {r.avg_pnl:.6f} | {r.win_rate:.2%} | {r.profit_factor:.3f} | {r.test_avg_pnl:.6f} |")
    lines.append("")

    if disabled:
        lines.append("## Known disabled families")
        lines.append("")
        for r in disabled:
            lines.append(f"- `{r.family_key}`: decision={r.decision}, still disabled by architecture")
        lines.append("")

    lines.append("## Research candidates")
    lines.append("")
    if not candidates:
        lines.append("No clean research candidates found.")
    else:
        lines.append("| Candidate | Decision | Trades | PF | Avg PnL | Test Avg | Reason |")
        lines.append("|---|---:|---:|---:|---:|---:|---|")
        for r in sorted(candidates, key=lambda x: (x.decision == "STRONG_CANDIDATE", x.profit_factor, x.trade_count), reverse=True)[:30]:
            lines.append(f"| {r.family_key} | {r.decision} | {r.trade_count} | {r.profit_factor:.3f} | {r.avg_pnl:.6f} | {r.test_avg_pnl:.6f} | {r.reason} |")
    lines.append("")

    lines.append("## Excluded garbage/summary examples")
    lines.append("")
    if not garbage:
        lines.append("No garbage rows found.")
    else:
        for r in garbage[:30]:
            lines.append(f"- `{r.family_key}`: {r.reason}")
    lines.append("")

    lines.append("## OS rule")
    lines.append("")
    lines.append("Future lifecycle/capital modules should consume `active_family_decisions.json`, not the raw v1 broad-scan decisions, unless they explicitly want research candidates.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory rolling OOS validator v2 cleanup")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--oos_dir", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    oos_dir = discover_oos_dir(workspace, Path(args.oos_dir) if args.oos_dir else None)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_rolling_oos_validator_v2"
    out_dir = out_root / f"rolling_oos_v2_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if oos_dir is None:
        err = {"error": "No v1 rolling OOS directory found", "expected_root": str(workspace / "edge_factory_rolling_oos_validator")}
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY ROLLING OOS VALIDATOR v2 CLEANUP")
        print("No v1 rolling OOS directory found.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    rows = load_v1_decisions(oos_dir)
    classified = classify_rows(rows)
    active = [r for r in classified if r.classification == "ACTIVE_MASTER_FAMILY"]
    disabled = [r for r in classified if r.classification == "KNOWN_DISABLED_FAMILY"]
    candidates = [r for r in classified if r.classification == "RESEARCH_CANDIDATE"]
    garbage = [r for r in classified if r.classification == "GARBAGE_OR_SUMMARY_ROW"]
    other = [r for r in classified if r.classification == "UNCLASSIFIED_NON_MASTER"]

    # Ensure active output is ordered and complete where possible.
    active = sorted(active, key=lambda x: ACTIVE_FAMILIES.index(x.family_key) if x.family_key in ACTIVE_FAMILIES else 999)
    disabled = sorted(disabled, key=lambda x: DISABLED_KNOWN_FAMILIES.index(x.family_key) if x.family_key in DISABLED_KNOWN_FAMILIES else 999)
    candidates = sorted(candidates, key=lambda x: (x.decision == "STRONG_CANDIDATE", x.profit_factor, x.trade_count), reverse=True)
    garbage = sorted(garbage, key=lambda x: x.family_key)
    other = sorted(other, key=lambda x: x.family_key)

    active_json = [r.raw for r in active]
    seed = build_active_state_seed(active, disabled)
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_oos_dir": str(oos_dir),
        "source_rows": len(rows),
        "deduped_classified_rows": len(classified),
        "active_master_count": len(active),
        "disabled_known_count": len(disabled),
        "research_candidate_count": len(candidates),
        "garbage_or_summary_count": len(garbage),
        "unclassified_non_master_count": len(other),
        "output_dir": str(out_dir),
    }

    write_json(out_dir / "active_family_decisions.json", active_json)
    write_json(out_dir / "clean_os_family_state_seed.json", seed)
    write_json(out_dir / "v2_cleanup_manifest.json", manifest)
    pd.DataFrame(row_dicts(active)).to_csv(out_dir / "active_family_summary.csv", index=False)
    pd.DataFrame(row_dicts(disabled)).to_csv(out_dir / "known_disabled_family_summary.csv", index=False)
    pd.DataFrame(row_dicts(candidates)).to_csv(out_dir / "candidate_family_watchlist.csv", index=False)
    pd.DataFrame(row_dicts(garbage)).to_csv(out_dir / "garbage_family_rows.csv", index=False)
    pd.DataFrame(row_dicts(other)).to_csv(out_dir / "unclassified_non_master_rows.csv", index=False)

    context = {"generated_at": manifest["generated_at"], "oos_dir": str(oos_dir)}
    write_report(out_dir / "rolling_oos_v2_report.md", context, active, disabled, candidates, garbage, other)

    print("EDGE FACTORY ROLLING OOS VALIDATOR v2 CLEANUP")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"v1_oos_dir: {oos_dir}")
    print(f"output_dir: {out_dir}")
    print(f"source_rows              : {len(rows)}")
    print(f"deduped_classified_rows  : {len(classified)}")
    print(f"active_master_count      : {len(active)}")
    print(f"disabled_known_count     : {len(disabled)}")
    print(f"research_candidate_count : {len(candidates)}")
    print(f"garbage_or_summary_count : {len(garbage)}")
    print(f"unclassified_non_master  : {len(other)}")
    print("")
    print("ACTIVE FAMILY DECISIONS")
    print("-" * 100)
    for r in active:
        print(f"{r.family_key:24s} decision={r.decision:24s} trades={r.trade_count:7d} avg={r.avg_pnl: .6f} pf={r.profit_factor:.3f}")
    if disabled:
        print("")
        print("KNOWN DISABLED")
        print("-" * 100)
        for r in disabled:
            print(f"{r.family_key:24s} decision={r.decision:24s} trades={r.trade_count:7d} status=DISABLED")
    if candidates:
        print("")
        print("TOP RESEARCH CANDIDATES")
        print("-" * 100)
        for r in candidates[:10]:
            print(f"{r.family_key:40s} decision={r.decision:24s} trades={r.trade_count:7d} pf={r.profit_factor:.3f}")
    print("")
    print(f"Report  : {out_dir / 'rolling_oos_v2_report.md'}")
    print(f"Active  : {out_dir / 'active_family_decisions.json'}")
    print(f"Seed    : {out_dir / 'clean_os_family_state_seed.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
