#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY EVIDENCE SYNTHESIS ENGINE v1
=========================================

Purpose
-------
Synthesize the current Edge Factory OS evidence into one research/control decision layer.

Inputs it reads, if available:
    - schema-aware validator v2
    - candle universe inventory v2
    - rolling retrain / time-OOS validator
    - family lifecycle state
    - research result ledger

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - collect latest evidence per target/family
    - prefer schema-aware v2 over provisional v1 validators
    - prefer rolling/time-OOS evidence over static full-sample evidence
    - classify each target into OS decisions:
        KEEP_CORE_ACTIVE
        KEEP_DIVERSIFIER_ACTIVE
        KEEP_BACKUP_ONLY
        REDUCE_OR_DISABLE_REVIEW
        PROMOTION_SANDBOX_CANDIDATE
        REJECT_OR_ARCHIVE
        NEEDS_MORE_DATA
    - write a synthesis report and action queue

Run:
    python "C:\Users\alike\edge_factory_evidence_synthesis_engine.py"

Core rule
---------
This module makes recommendations only. It never applies them.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

ACTIVE_ROLES = {
    "old_short": "CORE_ENGINE",
    "impulse_long": "HIGH_PRIORITY_DIVERSIFIER",
    "market_relative_short": "CAPPED_HALF_SIZE",
    "weak_market_short": "BACKUP_ONLY",
    "session_short": "DISABLED",
}

RESEARCH_CANDIDATES = {
    "ret60_reversal_short",
    "rel_extreme_reversion_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
}

TARGET_ORDER = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
    "ret60_reversal_short",
    "rel_extreme_reversion_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
    "session_short",
]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_csv_optional(path: Optional[Path]) -> pd.DataFrame:
    if not path or not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def read_json_optional(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def latest_schema_v2_summary(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_schema_aware_validator_v2", "schema_aware_v2_")
    return d / "schema_aware_validator_v2_summary.csv" if d and (d / "schema_aware_validator_v2_summary.csv").exists() else None


def latest_candle_inventory_v2_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_candle_universe_inventory_v2", "candle_inventory_v2_")
    return d / "candle_universe_inventory_v2_state.json" if d and (d / "candle_universe_inventory_v2_state.json").exists() else None


def latest_lifecycle_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_family_lifecycle", "lifecycle_")
    return d / "family_lifecycle_state.json" if d and (d / "family_lifecycle_state.json").exists() else None


def rolling_summary_files(workspace: Path) -> List[Path]:
    root = workspace / "edge_factory_rolling_retrain_validator"
    if not root.exists():
        return []
    paths = [p for p in root.rglob("rolling_time_oos_summary.csv") if p.exists()]
    return sorted(paths, key=lambda p: p.stat().st_mtime)


def latest_research_ledger(workspace: Path) -> Optional[Path]:
    p = workspace / "edge_factory_research_result_ledger" / "master_research_result_ledger.csv"
    return p if p.exists() else None


@dataclass
class EvidenceRow:
    target_key: str
    target_type: str
    role: str
    schema_status: str
    schema_clean_rows: Optional[int]
    schema_symbols: Optional[int]
    schema_pf: Optional[float]
    schema_avg_pnl: Optional[float]
    time_status: str
    time_clean_rows: Optional[int]
    time_valid_folds: Optional[int]
    time_pos_fold_rate: Optional[float]
    time_month_pos_rate: Optional[float]
    time_test_total: Optional[float]
    time_test_pf: Optional[float]
    time_worst_fold: Optional[float]
    candle_universe_verdict: str
    ledger_latest_status: str
    os_decision: str
    paper_permission_hint: str
    promotion_permission_hint: str
    reasons: List[str]
    warnings: List[str]


@dataclass
class SynthesisState:
    generated_at: str
    workspace: str
    schema_v2_path: Optional[str]
    candle_inventory_v2_path: Optional[str]
    rolling_summary_files: int
    ledger_path: Optional[str]
    targets_synthesized: int
    keep_count: int
    backup_count: int
    reduce_disable_count: int
    promotion_sandbox_count: int
    reject_count: int
    needs_data_count: int
    overall_state: str
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def df_latest_by_target(files: List[Path], key_col: str = "target_key") -> pd.DataFrame:
    rows = []
    for p in files:
        df = read_csv_optional(p)
        if df.empty or key_col not in df.columns:
            continue
        df = df.copy()
        df["__source_path"] = str(p)
        df["__mtime"] = p.stat().st_mtime
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    all_df = pd.concat(rows, ignore_index=True)
    all_df = all_df.sort_values("__mtime")
    return all_df.groupby(key_col, as_index=False).tail(1).reset_index(drop=True)


def latest_ledger_status(workspace: Path) -> Dict[str, str]:
    p = latest_research_ledger(workspace)
    df = read_csv_optional(p)
    if df.empty or "task_id" not in df.columns or "result_status" not in df.columns:
        return {}
    df = df.copy()
    if "recorded_at" in df.columns:
        df = df.sort_values("recorded_at")
    out: Dict[str, str] = {}
    for _, row in df.iterrows():
        task = str(row.get("task_id", ""))
        status = str(row.get("result_status", ""))
        # Extract target from common task ids.
        for prefix in ["schema_aware_v2_", "rolling_time_oos_", "validate_candidate_", "coin_subset_robustness_"]:
            if task.startswith(prefix):
                out[task[len(prefix):]] = status
    return out


def float_or_none(x: Any) -> Optional[float]:
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def int_or_none(x: Any) -> Optional[int]:
    try:
        if pd.isna(x):
            return None
        return int(float(x))
    except Exception:
        return None


def get_row_map(df: pd.DataFrame, key: str) -> Dict[str, Dict[str, Any]]:
    if df.empty or key not in df.columns:
        return {}
    out = {}
    for _, row in df.iterrows():
        out[str(row.get(key))] = row.to_dict()
    return out


def decide_target(target: str, schema: Dict[str, Any], time: Dict[str, Any], candle_verdict: str, ledger_status: str) -> EvidenceRow:
    role = ACTIVE_ROLES.get(target, "RESEARCH_CANDIDATE" if target in RESEARCH_CANDIDATES else "UNKNOWN")
    target_type = "ACTIVE_FAMILY" if target in ACTIVE_ROLES else "RESEARCH_CANDIDATE"
    schema_status = str(schema.get("validation_status", "MISSING")) if schema else "MISSING"
    time_status = str(time.get("validation_status", "MISSING")) if time else "MISSING"

    reasons: List[str] = []
    warnings: List[str] = []

    schema_clean_rows = int_or_none(schema.get("clean_rows"))
    schema_symbols = int_or_none(schema.get("symbol_count"))
    schema_pf = float_or_none(schema.get("profit_factor"))
    schema_avg = float_or_none(schema.get("avg_pnl"))

    time_clean_rows = int_or_none(time.get("rows_after_cleaning"))
    time_folds = int_or_none(time.get("valid_fold_count"))
    time_pos = float_or_none(time.get("positive_test_fold_rate"))
    time_month = float_or_none(time.get("monthly_positive_rate"))
    time_total = float_or_none(time.get("test_total_sum"))
    time_pf = float_or_none(time.get("test_pf_aggregate"))
    time_worst = float_or_none(time.get("worst_test_fold"))

    schema_pass = schema_status in {"ROBUST_COIN_FIT_SCHEMA_CLEAN", "CONCENTRATED_BUT_POSITIVE_SCHEMA_CLEAN"}
    schema_robust = schema_status == "ROBUST_COIN_FIT_SCHEMA_CLEAN"
    time_pass = time_status == "TIME_OOS_PASS"
    time_watch = time_status == "TIME_OOS_WATCHLIST"
    time_fail = time_status == "TIME_OOS_FAIL"
    needs_data = time_status == "NEEDS_MORE_DATA" or schema_status == "NEEDS_MORE_DATA"
    missing = schema_status == "MISSING" and time_status == "MISSING"

    if candle_verdict.startswith("WARN"):
        warnings.append("candle universe inventory has minor symbol gaps; decisions remain evidence-only")

    if role == "DISABLED":
        decision = "KEEP_DISABLED"
        paper = "PAPER_BLOCKED_DISABLED"
        promo = "PROMOTION_BLOCKED_DISABLED"
        reasons.append("family is explicitly disabled")
    elif target == "old_short":
        if schema_robust and time_pass:
            decision = "KEEP_CORE_ACTIVE"
            paper = "PAPER_ALLOWED_AS_CORE_AFTER_PREFLIGHT"
            promo = "NO_PROMOTION_NEEDED_ALREADY_CORE"
            reasons.append("core family passed schema-clean and time-OOS evidence")
        else:
            decision = "CORE_REVIEW_REQUIRED"
            paper = "PAPER_ALLOWED_ONLY_WITH_REVIEW"
            promo = "NO_PROMOTION_REVIEW_CORE"
            warnings.append("core family lacks clean pass evidence")
    elif target == "impulse_long":
        if schema_robust and time_pass:
            decision = "KEEP_DIVERSIFIER_ACTIVE"
            paper = "PAPER_ALLOWED_AS_DIVERSIFIER_AFTER_PREFLIGHT"
            promo = "NO_PROMOTION_NEEDED_ALREADY_DIVERSIFIER"
            reasons.append("diversifier passed schema-clean and time-OOS evidence")
        else:
            decision = "DIVERSIFIER_REVIEW_REQUIRED"
            paper = "PAPER_ALLOWED_ONLY_WITH_REVIEW"
            promo = "NO_PROMOTION_REVIEW_DIVERSIFIER"
            warnings.append("diversifier lacks clean pass evidence")
    elif target == "market_relative_short":
        if time_fail:
            decision = "REDUCE_OR_DISABLE_REVIEW"
            paper = "PAPER_ALLOWED_ONLY_BACKUP_OR_REMOVE_REVIEW"
            promo = "PROMOTION_BLOCKED_TIME_OOS_FAIL"
            reasons.append("market_relative_short failed time-OOS despite positive full/test aggregate")
        elif schema_pass and (time_pass or time_watch):
            decision = "KEEP_CAPPED_REDUCED_ONLY"
            paper = "PAPER_ALLOWED_CAPPED_ONLY"
            promo = "PROMOTION_BLOCKED_PRIOR_BAD_DAY_AND_CAPPED_ROLE"
            reasons.append("family has evidence but remains capped due prior role/risk")
        else:
            decision = "BACKUP_OR_DISABLE_REVIEW"
            paper = "PAPER_BACKUP_ONLY_WITH_REVIEW"
            promo = "PROMOTION_BLOCKED"
    elif target == "weak_market_short":
        if needs_data:
            decision = "KEEP_BACKUP_ONLY_NEEDS_MORE_DATA"
            paper = "PAPER_BACKUP_ONLY_SMALL_SIZE"
            promo = "PROMOTION_BLOCKED_NEEDS_DATA"
            reasons.append("weak_market_short lacks enough valid time-OOS folds")
        elif schema_pass and time_pass:
            decision = "KEEP_BACKUP_ONLY_WITH_PROMOTION_WATCH"
            paper = "PAPER_BACKUP_ONLY_SMALL_SIZE"
            promo = "PROMOTION_REQUIRES_SEPARATE_REVIEW"
        else:
            decision = "BACKUP_OR_DISABLE_REVIEW"
            paper = "PAPER_BACKUP_ONLY_WITH_REVIEW"
            promo = "PROMOTION_BLOCKED"
    elif target == "ret60_reversal_short":
        if schema_robust and time_pass:
            decision = "PROMOTION_SANDBOX_CANDIDATE"
            paper = "NOT_IN_ACTIVE_PAPER_UNTIL_SANDBOX_PLAN"
            promo = "SANDBOX_ALLOWED_REVIEW_ONLY"
            reasons.append("ret60 passed schema-clean, ready-universe, and row-order time-OOS evidence")
            warnings.append("candidate is not active; sandbox validation required before any paper inclusion")
        elif schema_pass and (time_watch or needs_data):
            decision = "RESEARCH_WATCHLIST"
            paper = "NO_ACTIVE_PAPER_YET"
            promo = "SANDBOX_AFTER_MORE_EVIDENCE"
        else:
            decision = "REJECT_OR_ARCHIVE"
            paper = "NO_PAPER"
            promo = "PROMOTION_BLOCKED"
    elif target in RESEARCH_CANDIDATES:
        if missing or needs_data:
            decision = "NEEDS_MORE_DATA_OR_SCHEMA_REPAIR"
            paper = "NO_PAPER"
            promo = "PROMOTION_BLOCKED_NEEDS_DATA"
        elif schema_pass and (time_pass or time_watch):
            decision = "RESEARCH_WATCHLIST"
            paper = "NO_ACTIVE_PAPER_YET"
            promo = "SANDBOX_REVIEW_ONLY"
        else:
            decision = "REJECT_OR_ARCHIVE"
            paper = "NO_PAPER"
            promo = "PROMOTION_BLOCKED"
            reasons.append("research candidate did not survive schema/time evidence")
    else:
        decision = "UNKNOWN_TARGET_REVIEW"
        paper = "NO_PAPER"
        promo = "PROMOTION_BLOCKED_UNKNOWN"

    if schema_status == "MISSING":
        warnings.append("missing schema-aware v2 evidence")
    if time_status == "MISSING":
        warnings.append("missing rolling/time-OOS evidence")
    if time_worst is not None and time_worst < 0:
        warnings.append(f"negative worst time-OOS fold: {time_worst}")

    return EvidenceRow(
        target_key=target,
        target_type=target_type,
        role=role,
        schema_status=schema_status,
        schema_clean_rows=schema_clean_rows,
        schema_symbols=schema_symbols,
        schema_pf=schema_pf,
        schema_avg_pnl=schema_avg,
        time_status=time_status,
        time_clean_rows=time_clean_rows,
        time_valid_folds=time_folds,
        time_pos_fold_rate=time_pos,
        time_month_pos_rate=time_month,
        time_test_total=time_total,
        time_test_pf=time_pf,
        time_worst_fold=time_worst,
        candle_universe_verdict=candle_verdict,
        ledger_latest_status=ledger_status,
        os_decision=decision,
        paper_permission_hint=paper,
        promotion_permission_hint=promo,
        reasons=reasons,
        warnings=warnings,
    )


def evidence_df(rows: List[EvidenceRow]) -> pd.DataFrame:
    out = []
    for r in rows:
        d = asdict(r)
        d["reasons"] = " | ".join(r.reasons)
        d["warnings"] = " | ".join(r.warnings)
        out.append(d)
    return pd.DataFrame(out)


def write_report(path: Path, state: SynthesisState, rows: List[EvidenceRow]) -> None:
    lines = [
        "# Edge Factory Evidence Synthesis Engine Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall state: **{state.overall_state}**",
        f"Targets synthesized: **{state.targets_synthesized}**",
        f"Keep: **{state.keep_count}**",
        f"Backup: **{state.backup_count}**",
        f"Reduce/disable review: **{state.reduce_disable_count}**",
        f"Promotion sandbox candidates: **{state.promotion_sandbox_count}**",
        f"Reject/archive: **{state.reject_count}**",
        f"Needs data: **{state.needs_data_count}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Decisions",
        "",
        "| Target | Role | Decision | Schema | Time-OOS | Paper hint | Promotion hint |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r.target_key} | {r.role} | {r.os_decision} | {r.schema_status} | {r.time_status} | {r.paper_permission_hint} | {r.promotion_permission_hint} |")
    lines += ["", "## Reasons", ""]
    for reason in state.reasons:
        lines.append(f"- {reason}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "This synthesis layer turns evidence into OS recommendations only. It does not start paper/live and does not mutate active config. ret60 can only move to a future promotion sandbox, not directly into active paper.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory evidence synthesis engine")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_evidence_synthesis_engine"
    out_dir = out_root / f"evidence_synthesis_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    schema_path = latest_schema_v2_summary(workspace)
    schema_df = read_csv_optional(schema_path)
    schema_map = get_row_map(schema_df, "target_key")

    rolling_files = rolling_summary_files(workspace)
    rolling_df = df_latest_by_target(rolling_files, "target_key")
    rolling_map = get_row_map(rolling_df, "target_key")

    candle_path = latest_candle_inventory_v2_state(workspace)
    candle_obj = read_json_optional(candle_path)
    candle_state = candle_obj.get("state", {}) if isinstance(candle_obj.get("state"), dict) else {}
    candle_verdict = str(candle_state.get("overall_verdict", "MISSING"))

    ledger_map = latest_ledger_status(workspace)

    all_targets = set(TARGET_ORDER) | set(schema_map.keys()) | set(rolling_map.keys())
    targets = [t for t in TARGET_ORDER if t in all_targets] + sorted(t for t in all_targets if t not in TARGET_ORDER)
    rows = [decide_target(t, schema_map.get(t, {}), rolling_map.get(t, {}), candle_verdict, ledger_map.get(t, "MISSING")) for t in targets]

    keep_count = len([r for r in rows if r.os_decision.startswith("KEEP_CORE") or r.os_decision.startswith("KEEP_DIVERSIFIER") or r.os_decision.startswith("KEEP_CAPPED")])
    backup_count = len([r for r in rows if "BACKUP" in r.os_decision])
    reduce_count = len([r for r in rows if "REDUCE" in r.os_decision or "DISABLE_REVIEW" in r.os_decision])
    sandbox_count = len([r for r in rows if r.os_decision == "PROMOTION_SANDBOX_CANDIDATE"])
    reject_count = len([r for r in rows if "REJECT" in r.os_decision or "ARCHIVE" in r.os_decision])
    needs_count = len([r for r in rows if "NEEDS_MORE_DATA" in r.os_decision or "NEEDS_DATA" in r.os_decision])

    warnings: List[str] = []
    reasons = [
        "Evidence synthesis read schema-aware v2, candle universe v2, and rolling/time-OOS outputs.",
        "v2 evidence supersedes earlier provisional validator outputs.",
    ]
    if sandbox_count:
        reasons.append("At least one research candidate qualifies for promotion sandbox review, not direct activation.")
    if reduce_count:
        warnings.append("At least one active family requires reduce/disable review based on time-OOS evidence.")
    if candle_verdict.startswith("WARN"):
        warnings.append(f"candle universe has warning verdict: {candle_verdict}")

    overall = "SYNTHESIS_READY_WITH_REVIEW_ITEMS" if warnings else "SYNTHESIS_READY"
    state = SynthesisState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        schema_v2_path=str(schema_path) if schema_path else None,
        candle_inventory_v2_path=str(candle_path) if candle_path else None,
        rolling_summary_files=len(rolling_files),
        ledger_path=str(latest_research_ledger(workspace)) if latest_research_ledger(workspace) else None,
        targets_synthesized=len(rows),
        keep_count=keep_count,
        backup_count=backup_count,
        reduce_disable_count=reduce_count,
        promotion_sandbox_count=sandbox_count,
        reject_count=reject_count,
        needs_data_count=needs_count,
        overall_state=overall,
        live_allowed=False,
        reasons=reasons,
        warnings=warnings,
        hard_rules=[
            "Evidence synthesis never starts paper/live.",
            "Evidence synthesis never mutates active config.",
            "Evidence synthesis never promotes candidates automatically.",
            "Promotion sandbox is a future isolated test stage, not active paper inclusion.",
            "Live remains blocked.",
        ],
    )

    state_path = out_dir / "evidence_synthesis_state.json"
    write_json(state_path, {"state": asdict(state), "decisions": [asdict(r) for r in rows]})
    evidence_df(rows).to_csv(out_dir / "evidence_synthesis_decisions.csv", index=False)
    evidence_df([r for r in rows if r.os_decision == "PROMOTION_SANDBOX_CANDIDATE"]).to_csv(out_dir / "promotion_sandbox_candidates.csv", index=False)
    evidence_df([r for r in rows if "REDUCE" in r.os_decision or "DISABLE" in r.os_decision]).to_csv(out_dir / "reduce_disable_review_queue.csv", index=False)
    write_report(out_dir / "evidence_synthesis_report.md", state, rows)

    print("EDGE FACTORY EVIDENCE SYNTHESIS ENGINE v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_state: {state.overall_state}")
    print(f"schema_v2: {state.schema_v2_path}")
    print(f"candle_inventory_v2: {state.candle_inventory_v2_path}")
    print(f"rolling_summary_files: {state.rolling_summary_files}")
    print(f"targets_synthesized: {state.targets_synthesized}")
    print(f"keep={state.keep_count} backup={state.backup_count} reduce_disable={state.reduce_disable_count} promotion_sandbox={state.promotion_sandbox_count} reject={state.reject_count} needs_data={state.needs_data_count}")
    print("live_allowed: False")
    print("")
    print("DECISIONS")
    print("-" * 100)
    for r in rows:
        print(f"{r.target_key:36s} role={r.role:26s} decision={r.os_decision:36s} schema={r.schema_status:34s} time={r.time_status}")
        if r.reasons:
            print(f"     - {' | '.join(r.reasons[:2])}")
        if r.warnings:
            print(f"     warnings: {' | '.join(r.warnings[:3])}")
    if state.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'evidence_synthesis_report.md'}")
    print(f"State  : {state_path}")
    print(f"Decisions: {out_dir / 'evidence_synthesis_decisions.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
