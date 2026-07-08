#!/usr/bin/env python
"""Validate causal capacity filter repair outputs and lookahead guardrails."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_causal_capacity_filter_repair"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
SUBSET_SUMMARY_CSV = OUTPUTS_DIR / f"{PREFIX}_subset_summary.csv"
DELAY_COST_GRID_CSV = OUTPUTS_DIR / f"{PREFIX}_delay_cost_grid.csv"
INVALIDATED_FILTERS_JSON = OUTPUTS_DIR / f"{PREFIX}_invalidated_non_causal_filters.json"
PRIOR_LIQUIDITY_CSV = OUTPUTS_DIR / f"{PREFIX}_prior_liquidity_symbol_rank.csv"
VALIDATOR_JSON = OUTPUTS_DIR / f"{PREFIX}_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / f"{PREFIX}_validator_report.md"

SCANNER_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_causal_capacity_filter_repair_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_causal_capacity_filter_repair_validator_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_causal_capacity_filter_repair_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_causal_capacity_filter_repair_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_orderbook_um_81_causal_capacity_filter_repair_v1.md"

COMPACT_OUTPUTS = [
    SUMMARY_JSON,
    SUMMARY_MD,
    SUBSET_SUMMARY_CSV,
    DELAY_COST_GRID_CSV,
    INVALIDATED_FILTERS_JSON,
    PRIOR_LIQUIDITY_CSV,
]
CODE_AND_REPORT_FILES = [
    SCANNER_PATH,
    VALIDATOR_PATH,
    RUNNER_PATH,
    VALIDATOR_RUNNER_PATH,
    DOCS_PATH,
    SUMMARY_MD,
    VALIDATOR_MD,
]

EXPECTED_CANDIDATE = "SELL_PRESSURE_ABSORBED@300s"
EXPECTED_CATEGORY = "SELL_PRESSURE_ABSORBED"
EXPECTED_HORIZON_SECONDS = 300
EXPECTED_COOLDOWN_SECONDS = 600
EXPECTED_SYMBOL_DAYS_TOTAL = 14_580
EXPECTED_DELAYS = {0, 1, 3, 5, 10}
EXPECTED_COSTS = {0.0, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0}
EXPECTED_WINDOWS = {"LATEST_90D", "HOLDOUT_90D"}
EXPECTED_FILTERS = (
    {"BASELINE_ALL_SYMBOLS", "TOP_10_BY_CAUSAL_PRIOR_7D_LIQUIDITY", "TOP_20_BY_CAUSAL_PRIOR_7D_LIQUIDITY",
     "TOP_40_BY_CAUSAL_PRIOR_7D_LIQUIDITY", "EXCLUDE_CAUSAL_THIN_PRIOR_7D"}
    | {f"TRAILING_NOTIONAL_{window}S_GE_{threshold}" for window in (60, 300, 600) for threshold in (5000, 10000, 25000, 50000, 100000)}
    | {f"TRAILING_TRADE_COUNT_{window}S_GE_{threshold}" for window in (60, 300, 600) for threshold in (5, 10, 25, 50, 100)}
    | {f"EVENT_BOOKDEPTH_NOTIONAL_GE_{threshold}" for threshold in (5000, 10000, 25000, 50000, 100000)}
)
EXPECTED_SUBSET_ROWS = len(EXPECTED_FILTERS) * len(EXPECTED_DELAYS)
EXPECTED_COST_ROWS = EXPECTED_SUBSET_ROWS * len(EXPECTED_COSTS)
EXPECTED_INVALIDATED_FILTERS = {
    "MIN_AROUND_EVENT_NOTIONAL",
    "TOP_BY_AROUND_EVENT_NOTIONAL",
    "HIGH_MEDIUM_LOW_THIN_FROM_AROUND_EVENT",
}
ALLOWED_DIAGNOSTIC_CLASSIFICATIONS = {"FUND_CAPABLE", "CAPACITY_SAFE", "FILTER_ONLY", "REJECTED"}
ALLOWED_CAPACITY_CLASSIFICATIONS = {
    "BASELINE",
    "CAUSAL_PRIOR_LIQUIDITY",
    "FUND_CAPABLE_CAUSAL_TRAILING_NOTIONAL",
    "CAPACITY_SAFE_CAUSAL_TRAILING_NOTIONAL",
    "CAPACITY_MODERATE_CAUSAL_TRAILING_NOTIONAL",
    "SMALL_CAP_OR_MIXED_CAUSAL_TRAILING_NOTIONAL",
    "CAUSAL_TRAILING_TRADE_COUNT_PROXY",
    "FUND_CAPABLE_EVENT_TIME_BOOKDEPTH",
    "CAPACITY_SAFE_EVENT_TIME_BOOKDEPTH",
    "EVENT_TIME_BOOKDEPTH_PROXY",
}

FORBIDDEN_PATTERNS = [
    r"\bstrategy\b",
    r"\bbacktest\b",
    r"\bsignal\b",
    r"\bpnl\b",
    r"\bpnl curve\b",
    r"\bentries\b",
    r"\bentry\b",
    r"\bexits\b",
    r"\bexit\b",
    r"\bstops?\b",
    r"\btargets?\b",
    r"\bleverage\b",
    r"\border execution\b",
    r"\bprivate endpoints?\b",
    r"\bapi keys?\b",
    r"\bsecret\b",
    r"\brecommendations?\b",
    r"\blive trading\b",
    r"\bpaper trading\b",
    r"\borders?\b",
]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = -1.0) -> float:
    try:
        text = str(value).strip()
        if text == "":
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def forbidden_term(pattern: str) -> str:
    return pattern.replace(r"\b", "").replace("\\", "").replace("?", "")


def context_window(lines: list[str], line_number: int, radius: int = 2) -> list[dict[str, Any]]:
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)
    return [{"line": current, "text": lines[current - 1].rstrip()[:300]} for current in range(start, end + 1)]


def classify_forbidden_match(pattern: str, context: list[dict[str, Any]]) -> tuple[str, str]:
    term = forbidden_term(pattern).lower()
    context_text = "\n".join(str(item.get("text", "")) for item in context).lower()
    safety_markers = [
        "no ",
        "not ",
        "without",
        "forbidden",
        "prohibited",
        "must not",
        "safety",
        "research",
        "diagnostic only",
        "downloads_run",
        "full_history_run",
        "full_parquet_dataset_created",
        "row_level_dataset_created",
        "strategy_created",
        "backtest_created",
        "pnl_created",
        "orders_created",
        "private_endpoints_used",
        "recommendations_created",
        ": false",
        "no_real_prohibited_behavior",
    ]
    if any(marker in context_text for marker in safety_markers):
        return "SAFETY_CONTEXT", "safety, absence, or research-boundary wording"
    if term == "exit" and ("exitcode" in context_text or "systemexit" in context_text):
        return "SAFETY_CONTEXT", "runner or process-control context"
    if term.startswith("stop") and "erroractionpreference" in context_text:
        return "SAFETY_CONTEXT", "runner error-control context"
    if "forbidden_patterns" in context_text:
        return "SAFETY_CONTEXT", "validator pattern declaration"
    return "REAL_BLOCKER", "potential prohibited restricted behavior"


def scan_forbidden_terms() -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    real_blockers: list[dict[str, Any]] = []
    for path in CODE_AND_REPORT_FILES:
        if not path.exists() or path.is_dir():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, line in enumerate(lines, start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if not re.search(pattern, line, flags=re.IGNORECASE):
                    continue
                context = context_window(lines, line_number)
                if "FORBIDDEN_PATTERNS" in line or line.strip().startswith("r\""):
                    classification, reason = "SAFETY_CONTEXT", "validator pattern declaration"
                else:
                    classification, reason = classify_forbidden_match(pattern, context)
                item = {
                    "path": str(path.relative_to(REPO_ROOT)),
                    "line": line_number,
                    "term": forbidden_term(pattern),
                    "text": line.strip()[:240],
                    "classification": classification,
                    "classification_reason": reason,
                    "context": context,
                }
                matches.append(item)
                if classification == "REAL_BLOCKER":
                    real_blockers.append(item)
    return {"matches": matches, "real_blockers": real_blockers}


def scanner_noncausal_selection_matches() -> list[dict[str, Any]]:
    if not SCANNER_PATH.exists():
        return [{"pattern": "scanner_missing", "line": 0, "text": str(SCANNER_PATH)}]
    lines = SCANNER_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    checks = [
        ("event_ms_plus_future_window", re.compile(r"event_ms\s*\+")),
        ("notional_around_event_call", re.compile(r"\bnotional_around_event\s*\(")),
        ("capacity_window_radius_helper", re.compile(r"\bCAPACITY_WINDOW_RADIUS_MS\b")),
        ("bisect_right_event_ms", re.compile(r"\bbisect_right\s*\(\s*trade_times\s*,\s*event_ms")),
    ]
    matches: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        for name, pattern in checks:
            if pattern.search(line):
                matches.append({"pattern": name, "line": line_number, "text": line.strip()[:240]})
    return matches


def row_level_or_parquet_outputs() -> list[str]:
    allowed = {path.resolve() for path in COMPACT_OUTPUTS + [VALIDATOR_JSON, VALIDATOR_MD]}
    matches: list[str] = []
    for path in OUTPUTS_DIR.glob(f"{PREFIX}*"):
        if path.resolve() in allowed:
            continue
        if path.suffix.lower() in {".parquet", ".jsonl", ".db", ".sqlite", ".duckdb"}:
            matches.append(str(path.relative_to(REPO_ROOT)))
    return matches


def invalidated_filters_are_report_only(rows: Any) -> bool:
    if not isinstance(rows, list) or not rows:
        return False
    names = {str(row.get("filter_family", "")) for row in rows if isinstance(row, dict)}
    if names != EXPECTED_INVALIDATED_FILTERS:
        return False
    return all(
        isinstance(row, dict)
        and row.get("classification") == "NON_CAUSAL_DIAGNOSTIC"
        and row.get("selection_allowed") is False
        for row in rows
    )


def validate() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON)
    subset_rows = read_csv_rows(SUBSET_SUMMARY_CSV)
    cost_rows = read_csv_rows(DELAY_COST_GRID_CSV)
    prior_liquidity_rows = read_csv_rows(PRIOR_LIQUIDITY_CSV)
    invalidated_rows = load_json(INVALIDATED_FILTERS_JSON)
    forbidden_scan = scan_forbidden_terms()
    noncausal_source_matches = scanner_noncausal_selection_matches()
    row_level_outputs = row_level_or_parquet_outputs()
    compact_sizes = {path.name: path.stat().st_size for path in COMPACT_OUTPUTS if path.exists()}

    subset_names = {str(row.get("filter_name", "")) for row in subset_rows}
    subset_delays = {int_value(row.get("delay_seconds"), -1) for row in subset_rows}
    cost_values = {float_value(row.get("cost_bps")) for row in cost_rows}
    cost_names = {str(row.get("filter_name", "")) for row in cost_rows}
    cost_delays = {int_value(row.get("delay_seconds"), -1) for row in cost_rows}
    subset_classifications = {str(row.get("diagnostic_classification", "")) for row in subset_rows}
    capacity_classifications = {str(row.get("capacity_classification", "")) for row in subset_rows}
    output_paths = [Path(str(value)) for value in summary.get("outputs", {}).values() if value] if isinstance(summary, dict) else []
    outputs_inside_repo = all(path_is_inside(path, REPO_ROOT) for path in output_paths) if output_paths else False

    window_names = set()
    if isinstance(summary, dict):
        for item in summary.get("window_summaries", []):
            if isinstance(item, dict):
                window_names.add(str(item.get("window", "")))

    checks = {
        "summary_exists": SUMMARY_JSON.exists(),
        "summary_status_pass": isinstance(summary, dict) and summary.get("status") == "PASS_ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR",
        "candidate_locked": isinstance(summary, dict) and summary.get("candidate") == EXPECTED_CANDIDATE,
        "category_locked": isinstance(summary, dict) and summary.get("locked_category") == EXPECTED_CATEGORY,
        "horizon_locked": isinstance(summary, dict) and int_value(summary.get("locked_horizon_seconds")) == EXPECTED_HORIZON_SECONDS,
        "cooldown_locked": isinstance(summary, dict) and int_value(summary.get("locked_cooldown_seconds")) == EXPECTED_COOLDOWN_SECONDS,
        "latest_holdout_only": isinstance(summary, dict) and summary.get("mode") == "LATEST_90D_AND_HOLDOUT_90D_ONLY",
        "window_names_expected": window_names == EXPECTED_WINDOWS,
        "delay_set_expected": isinstance(summary, dict) and {int_value(item, -1) for item in summary.get("delay_seconds", [])} == EXPECTED_DELAYS,
        "cost_set_expected": isinstance(summary, dict) and {float_value(item) for item in summary.get("cost_grid_bps", [])} == EXPECTED_COSTS,
        "processed_expected_symbol_days": isinstance(summary, dict) and int_value(summary.get("symbol_days_processed_total")) == EXPECTED_SYMBOL_DAYS_TOTAL,
        "failed_symbol_days_zero": isinstance(summary, dict) and int_value(summary.get("failed_symbol_days_total")) == 0,
        "old_non_causal_result_invalidated": isinstance(summary, dict) and summary.get("old_non_causal_result_must_not_be_used") is True,
        "invalidated_filters_report_only": invalidated_filters_are_report_only(invalidated_rows),
        "summary_future_flags_false": isinstance(summary, dict)
        and summary.get("causal_selection_uses_future_window") is False
        and summary.get("causal_selection_uses_post_event_notional") is False
        and summary.get("causal_selection_uses_post_event_trade_count") is False
        and summary.get("causal_selection_uses_post_event_volatility") is False,
        "scanner_source_no_future_selection_patterns": not noncausal_source_matches,
        "subset_rows_expected": len(subset_rows) == EXPECTED_SUBSET_ROWS,
        "subset_names_expected": subset_names == EXPECTED_FILTERS,
        "subset_delays_expected": subset_delays == EXPECTED_DELAYS,
        "subset_filters_no_around_event": not any("AROUND_EVENT" in name for name in subset_names),
        "subset_classifications_allowed": subset_classifications.issubset(ALLOWED_DIAGNOSTIC_CLASSIFICATIONS),
        "capacity_classifications_allowed": capacity_classifications.issubset(ALLOWED_CAPACITY_CLASSIFICATIONS),
        "cost_rows_expected": len(cost_rows) == EXPECTED_COST_ROWS,
        "cost_names_expected": cost_names == EXPECTED_FILTERS,
        "cost_delays_expected": cost_delays == EXPECTED_DELAYS,
        "cost_values_expected": cost_values == EXPECTED_COSTS,
        "prior_liquidity_rank_rows_expected": len(prior_liquidity_rows) == 162,
        "all_compact_outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in COMPACT_OUTPUTS),
        "outputs_inside_repo_compact_only": outputs_inside_repo,
        "no_row_level_or_parquet_outputs": not row_level_outputs,
        "summary_confirms_no_downloads": isinstance(summary, dict) and summary.get("downloads_run") is False,
        "summary_confirms_raw_data_not_modified": isinstance(summary, dict) and summary.get("raw_data_modified") is False,
        "summary_confirms_no_full_history": isinstance(summary, dict) and summary.get("full_history_run") is False,
        "summary_confirms_no_full_parquet_dataset": isinstance(summary, dict) and summary.get("full_parquet_dataset_created") is False,
        "summary_confirms_no_row_level_dataset": isinstance(summary, dict) and summary.get("row_level_dataset_created") is False,
        "summary_confirms_no_strategy": isinstance(summary, dict) and summary.get("strategy_created") is False,
        "summary_confirms_no_backtest": isinstance(summary, dict) and summary.get("backtest_created") is False,
        "summary_confirms_no_pnl": isinstance(summary, dict) and summary.get("pnl_created") is False,
        "summary_confirms_no_orders": isinstance(summary, dict) and summary.get("orders_created") is False,
        "summary_confirms_no_private_endpoints": isinstance(summary, dict) and summary.get("private_endpoints_used") is False,
        "summary_confirms_no_recommendations": isinstance(summary, dict) and summary.get("recommendations_created") is False,
        "no_real_prohibited_behavior": not forbidden_scan["real_blockers"],
    }
    replacement_checks_all_true = all(checks.values())
    status = (
        "PASS_ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR_VALIDATED"
        if replacement_checks_all_true
        else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR_VALIDATION"
    )
    report = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "source_summary_status": summary.get("status", "") if isinstance(summary, dict) else "",
        "causal_capacity_repair_succeeded": summary.get("causal_capacity_repair_succeeded", False) if isinstance(summary, dict) else False,
        "old_non_causal_result_must_not_be_used": summary.get("old_non_causal_result_must_not_be_used", False) if isinstance(summary, dict) else False,
        "invalidated_non_causal_filters": invalidated_rows if isinstance(invalidated_rows, list) else [],
        "best_causal_capacity_subset": summary.get("best_causal_capacity_subset", {}) if isinstance(summary, dict) else {},
        "baseline_delay_zero": summary.get("baseline_delay_zero", {}) if isinstance(summary, dict) else {},
        "symbol_days_processed_total": summary.get("symbol_days_processed_total", 0) if isinstance(summary, dict) else 0,
        "runtime_seconds": summary.get("runtime_seconds", 0) if isinstance(summary, dict) else 0,
        "compact_output_sizes_bytes": compact_sizes,
        "scanner_noncausal_selection_matches": noncausal_source_matches,
        "row_level_or_parquet_outputs": row_level_outputs,
        "prohibited_term_matches": forbidden_scan["matches"],
        "real_prohibited_behavior_matches": forbidden_scan["real_blockers"],
        "checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_validator_md(report)
    return report


def write_validator_md(report: dict[str, Any]) -> None:
    best = report.get("best_causal_capacity_subset", {})
    lines = [
        "# Causal capacity filter repair validator v1",
        "",
        f"status: {report['status']}",
        f"source_summary_status: {report.get('source_summary_status', '')}",
        f"causal_capacity_repair_succeeded: {str(report.get('causal_capacity_repair_succeeded', False)).lower()}",
        f"old_non_causal_result_must_not_be_used: {str(report.get('old_non_causal_result_must_not_be_used', False)).lower()}",
        f"best_filter_name: {best.get('filter_name', '') if isinstance(best, dict) else ''}",
        f"best_delay_seconds: {best.get('delay_seconds', '') if isinstance(best, dict) else ''}",
        f"replacement_checks_all_true: {str(report.get('replacement_checks_all_true', False)).lower()}",
        "",
        "## Checks",
    ]
    for key, value in report.get("checks", {}).items():
        lines.append(f"- {key}: {str(value).lower()}")
    if report.get("scanner_noncausal_selection_matches"):
        lines.append("")
        lines.append("## Non-Causal Source Matches")
        for item in report["scanner_noncausal_selection_matches"]:
            lines.append(f"- {item.get('pattern')}: line {item.get('line')} {item.get('text')}")
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        report = validate()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "FAILED_ORDERBOOK_UM_81_CAUSAL_CAPACITY_FILTER_REPAIR_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "replacement_checks_all_true": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        VALIDATOR_MD.write_text(
            "# Causal capacity filter repair validator v1\n\n"
            f"status: {report['status']}\n"
            f"error: {report['error']}\n",
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
