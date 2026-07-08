#!/usr/bin/env python
"""Causal audit for the SELL_PRESSURE_ABSORBED capacity filter."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_sell_pressure_absorbed_capacity_filter_causal_full_history"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
CAUSAL_AUDIT_JSON = OUTPUTS_DIR / f"{PREFIX}_causal_audit.json"

EXECUTION_DELAY_SOURCE = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_diagnostic_v1.py"
CAPACITY_REFINEMENT_SOURCE = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_capacity_aware_refinement_v1.py"

LOCKED_CANDIDATE = "SELL_PRESSURE_ABSORBED@300s"
LOCKED_CATEGORY = "SELL_PRESSURE_ABSORBED"
LOCKED_HORIZON_SECONDS = 300
LOCKED_COOLDOWN_SECONDS = 600
LOCKED_CAPACITY_SUBSET = "MIN_AROUND_EVENT_NOTIONAL_100000"
EXPECTED_COVERAGE_START = "2023-01-01"
EXPECTED_COVERAGE_END = "2026-06-15"


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def context_window(path: Path, line_number: int, radius: int = 3) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)
    return [{"line": current, "text": lines[current - 1].rstrip()} for current in range(start, end + 1)]


def find_matches(path: Path, pattern: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if not path.exists():
        return matches
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if re.search(pattern, line):
            matches.append(
                {
                    "path": str(path.relative_to(REPO_ROOT)),
                    "line": line_number,
                    "text": line.strip(),
                    "context": context_window(path, line_number),
                }
            )
    return matches


def build_audit() -> dict[str, Any]:
    future_bound_matches = find_matches(EXECUTION_DELAY_SOURCE, r"event_ms\s*\+\s*CAPACITY_WINDOW_RADIUS_MS")
    trailing_bound_matches = find_matches(EXECUTION_DELAY_SOURCE, r"event_ms\s*-\s*CAPACITY_WINDOW_RADIUS_MS")
    capacity_filter_usage_matches = find_matches(CAPACITY_REFINEMENT_SOURCE, r"notional_around_event\(")
    locked_threshold_matches = find_matches(CAPACITY_REFINEMENT_SOURCE, r"MIN_AROUND_EVENT_NOTIONAL|NOTIONAL_THRESHOLDS")

    uses_future_window = bool(future_bound_matches)
    uses_capacity_filter = bool(capacity_filter_usage_matches)
    capacity_filter_causal = uses_capacity_filter and not uses_future_window
    status = (
        "PASS_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_FILTER_CAUSAL_FULL_HISTORY_VALIDATED"
        if capacity_filter_causal
        else "LOOKAHEAD_BLOCKED_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_FILTER_CAUSAL_FULL_HISTORY_VALIDATION"
    )
    audit = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_CAPACITY_FILTER_CAUSAL_FULL_HISTORY_VALIDATION_V1",
        "candidate": LOCKED_CANDIDATE,
        "locked_category": LOCKED_CATEGORY,
        "locked_horizon_seconds": LOCKED_HORIZON_SECONDS,
        "locked_cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "locked_capacity_subset": LOCKED_CAPACITY_SUBSET,
        "coverage_start": EXPECTED_COVERAGE_START,
        "coverage_end": EXPECTED_COVERAGE_END,
        "capacity_filter_causal": capacity_filter_causal,
        "lookahead_blocked": not capacity_filter_causal,
        "lookahead_reason": (
            "capacity subset uses notional_around_event, which includes event_ms + CAPACITY_WINDOW_RADIUS_MS"
            if not capacity_filter_causal
            else ""
        ),
        "future_bound_matches": future_bound_matches,
        "trailing_bound_matches": trailing_bound_matches,
        "capacity_filter_usage_matches": capacity_filter_usage_matches,
        "locked_threshold_matches": locked_threshold_matches,
        "full_history_validation_run": False if not capacity_filter_causal else False,
        "full_history_validation_skipped_reason": (
            "LOOKAHEAD_BLOCKED: filter uses post-event notional"
            if not capacity_filter_causal
            else "causal audit passed, but this audit tool does not start the long full-history stream"
        ),
        "downloads_run": False,
        "raw_data_modified": False,
        "full_parquet_dataset_created": False,
        "row_level_dataset_created": False,
        "strategy_created": False,
        "backtest_created": False,
        "pnl_created": False,
        "signals_created": False,
        "orders_created": False,
        "private_endpoints_used": False,
        "recommendations_created": False,
    }
    return audit


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Sell pressure absorbed capacity filter causal full-history validation v1",
        "",
        f"status: {summary['status']}",
        f"capacity_filter_causal: {str(summary['capacity_filter_causal']).lower()}",
        f"lookahead_blocked: {str(summary['lookahead_blocked']).lower()}",
        f"lookahead_reason: {summary['lookahead_reason']}",
        f"full_history_validation_run: {str(summary['full_history_validation_run']).lower()}",
        "",
        "## Causal Audit",
        "The locked capacity subset is `MIN_AROUND_EVENT_NOTIONAL_100000`.",
        "The existing implementation uses `notional_around_event(event_ms, ...)` for that subset.",
        "The helper computes a right boundary with `event_ms + CAPACITY_WINDOW_RADIUS_MS`, so it includes post-event trade notional.",
        "",
        "No downloads, full parquet dataset, row-level dataset, strategy, backtest, PnL, signals, orders, private endpoints, or recommendations were created.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_audit() -> dict[str, Any]:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    audit = build_audit()
    CAUSAL_AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SUMMARY_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(audit)
    audit["outputs"] = {
        "summary_json": str(SUMMARY_JSON),
        "summary_md": str(SUMMARY_MD),
        "causal_audit_json": str(CAUSAL_AUDIT_JSON),
    }
    SUMMARY_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return audit


def main() -> int:
    summary = run_audit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(summary.get("status", "")).startswith(("PASS", "LOOKAHEAD_BLOCKED")) else 2


if __name__ == "__main__":
    raise SystemExit(main())
