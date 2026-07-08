#!/usr/bin/env python
"""Validate SELL_PRESSURE_ABSORBED execution delay and capacity diagnostics."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
DELAY_COST_GRID_CSV = OUTPUTS_DIR / f"{PREFIX}_delay_cost_grid.csv"
CAPACITY_CSV = OUTPUTS_DIR / f"{PREFIX}_capacity_by_symbol_window.csv"
STABILITY_CSV = OUTPUTS_DIR / f"{PREFIX}_stability.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / f"{PREFIX}_null_comparison.csv"
VALIDATOR_JSON = OUTPUTS_DIR / f"{PREFIX}_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / f"{PREFIX}_validator_report.md"

SCANNER_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_diagnostic_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_validator_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_diagnostic_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_diagnostic_v1.md"

COMPACT_OUTPUTS = [
    SUMMARY_JSON,
    SUMMARY_MD,
    DELAY_COST_GRID_CSV,
    CAPACITY_CSV,
    STABILITY_CSV,
    NULL_COMPARISON_CSV,
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
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_SYMBOL_DAYS_TOTAL = 14_580
EXPECTED_DELAY_SECONDS = {0, 1, 3, 5, 10, 30}
EXPECTED_COST_BPS = {0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0}
EXPECTED_GRID_ROWS = len(EXPECTED_DELAY_SECONDS) * len(EXPECTED_COST_BPS)
EXPECTED_CAPACITY_ROWS = EXPECTED_SYMBOL_COUNT * 2
EXPECTED_WINDOWS = {"LATEST_90D", "HOLDOUT_90D"}
ALLOWED_ASSESSMENTS = {
    "STANDALONE_VIABLE",
    "LATENCY_SENSITIVE",
    "CAPACITY_LIMITED",
    "REJECTED",
}
ALLOWED_ROW_CLASSIFICATIONS = {
    "EXECUTION_SURVIVED",
    "LATENCY_SENSITIVE",
    "CAPACITY_LIMITED",
    "FILTER_ONLY",
    "REJECTED",
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


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"not a JSON object: {path}")
    return payload


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


def float_value(value: Any, default: float | None = None) -> float | None:
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
        "validation only",
        "downloads_run",
        "full_history_run",
        "row_level_dataset_created",
        "full_parquet_dataset_created",
        "orders_created",
        "private_endpoints_used",
        "new_filters_added",
        "thresholds_optimized",
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


def raw_book_or_trade_files_inside_repo() -> list[str]:
    matches: list[str] = []
    for pattern in ["*-bookDepth-*.csv", "*-aggTrades-*.csv", "*-bookDepth-*.zip", "*-aggTrades-*.zip"]:
        for path in REPO_ROOT.rglob(pattern):
            if ".git" in path.parts:
                continue
            matches.append(str(path.relative_to(REPO_ROOT)))
            if len(matches) >= 100:
                return matches
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


def validate() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON)
    grid_rows = read_csv_rows(DELAY_COST_GRID_CSV)
    capacity_rows = read_csv_rows(CAPACITY_CSV)
    stability_rows = read_csv_rows(STABILITY_CSV)
    null_rows = read_csv_rows(NULL_COMPARISON_CSV)
    scan = scan_forbidden_terms()
    raw_inside = raw_book_or_trade_files_inside_repo()
    row_level_outputs = row_level_or_parquet_outputs()
    compact_sizes = {path.name: path.stat().st_size for path in COMPACT_OUTPUTS if path.exists()}

    grid_delays = {int_value(row.get("delay_seconds"), -1) for row in grid_rows}
    grid_costs = {float_value(row.get("cost_bps"), -1.0) for row in grid_rows}
    grid_windows_consistent = all(
        str(row.get("latest_vs_holdout_consistency", "")) in {"CONSISTENT_POSITIVE", "NOT_POSITIVE_IN_BOTH_WINDOWS"}
        for row in grid_rows
    )
    grid_classifications = {str(row.get("classification", "")) for row in grid_rows}
    capacity_windows = {str(row.get("window", "")) for row in capacity_rows}
    capacity_symbols_by_window = {
        window: {str(row.get("symbol", "")) for row in capacity_rows if str(row.get("window", "")) == window}
        for window in EXPECTED_WINDOWS
    }
    stability_windows = {str(row.get("window", "")) for row in stability_rows}
    null_windows = {str(row.get("window", "")) for row in null_rows}
    output_paths = [Path(str(value)) for value in summary.get("outputs", {}).values() if value]
    outputs_inside_repo = all(path_is_inside(path, REPO_ROOT) for path in output_paths) if output_paths else False

    checks = {
        "summary_exists": SUMMARY_JSON.exists(),
        "summary_status_pass": str(summary.get("status", "")).startswith("PASS"),
        "assessment_allowed": str(summary.get("assessment", "")) in ALLOWED_ASSESSMENTS,
        "mode_latest_and_holdout_only": summary.get("mode") == "LATEST_90D_AND_HOLDOUT_90D_ONLY",
        "candidate_locked": summary.get("candidate") == EXPECTED_CANDIDATE,
        "category_locked": summary.get("locked_category") == EXPECTED_CATEGORY,
        "horizon_locked": int_value(summary.get("locked_horizon_seconds")) == EXPECTED_HORIZON_SECONDS,
        "cooldown_locked": int_value(summary.get("locked_cooldown_seconds")) == EXPECTED_COOLDOWN_SECONDS,
        "delay_set_expected": set(int_value(item, -1) for item in summary.get("delay_seconds", [])) == EXPECTED_DELAY_SECONDS,
        "cost_set_expected": set(float_value(item, -1.0) for item in summary.get("cost_grid_bps", [])) == EXPECTED_COST_BPS,
        "processed_latest_holdout_symbol_days": int_value(summary.get("symbol_days_processed_total")) == EXPECTED_SYMBOL_DAYS_TOTAL,
        "failed_symbol_days_zero": int_value(summary.get("failed_symbol_days_total")) == 0,
        "all_compact_outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in COMPACT_OUTPUTS),
        "delay_cost_grid_expected_row_count": len(grid_rows) == EXPECTED_GRID_ROWS,
        "delay_cost_grid_delays_expected": grid_delays == EXPECTED_DELAY_SECONDS,
        "delay_cost_grid_costs_expected": grid_costs == EXPECTED_COST_BPS,
        "delay_cost_grid_classifications_allowed": grid_classifications.issubset(ALLOWED_ROW_CLASSIFICATIONS),
        "delay_cost_grid_has_latest_holdout_consistency": grid_windows_consistent,
        "capacity_expected_row_count": len(capacity_rows) == EXPECTED_CAPACITY_ROWS,
        "capacity_windows_expected": capacity_windows == EXPECTED_WINDOWS,
        "capacity_81_symbols_per_window": all(len(symbols) == EXPECTED_SYMBOL_COUNT for symbols in capacity_symbols_by_window.values()),
        "capacity_counts_nonzero": all(int_value(row.get("kept_event_count")) > 0 for row in capacity_rows),
        "stability_windows_expected": stability_windows == EXPECTED_WINDOWS,
        "stability_nonzero": len(stability_rows) > 0,
        "null_windows_expected": null_windows == EXPECTED_WINDOWS,
        "null_rows_expected": len(null_rows) == len(EXPECTED_WINDOWS) * len(EXPECTED_DELAY_SECONDS),
        "summary_confirms_no_downloads": summary.get("downloads_run") is False,
        "summary_confirms_no_full_history_run": summary.get("full_history_run") is False,
        "summary_confirms_no_full_parquet_dataset": summary.get("full_parquet_dataset_created") is False,
        "summary_confirms_no_row_level_dataset": summary.get("row_level_dataset_created") is False,
        "summary_confirms_no_orders": summary.get("orders_created") is False,
        "summary_confirms_no_private_endpoints": summary.get("private_endpoints_used") is False,
        "new_filters_not_added": summary.get("new_filters_added") is False,
        "thresholds_not_optimized": summary.get("thresholds_optimized") is False,
        "outputs_inside_repo_compact_only": outputs_inside_repo,
        "raw_roots_outside_repo": summary.get("raw_roots_outside_repo") is True,
        "no_raw_book_or_trade_files_inside_repo": not raw_inside,
        "no_row_level_or_parquet_outputs": not row_level_outputs,
        "no_real_prohibited_behavior": not scan["real_blockers"],
    }
    replacement_checks_all_true = all(checks.values())
    status = (
        "PASS_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_EXECUTION_DELAY_CAPACITY_VALIDATOR"
        if replacement_checks_all_true
        else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_EXECUTION_DELAY_CAPACITY_VALIDATION"
    )
    report = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "source_summary_status": summary.get("status", ""),
        "assessment": summary.get("assessment", ""),
        "runtime_seconds": summary.get("runtime_seconds", 0),
        "symbol_days_processed_total": summary.get("symbol_days_processed_total", 0),
        "kept_event_count_total": summary.get("kept_event_count_total", 0),
        "break_even_by_delay": summary.get("break_even_by_delay", {}),
        "classification_counts": summary.get("classification_counts", {}),
        "strongest_viable_delay_cost": summary.get("strongest_viable_delay_cost", {}),
        "capacity_summary": summary.get("capacity_summary", {}),
        "compact_output_sizes_bytes": compact_sizes,
        "raw_book_or_trade_files_inside_repo": raw_inside,
        "row_level_or_parquet_outputs": row_level_outputs,
        "prohibited_term_matches": scan["matches"],
        "real_prohibited_behavior_matches": scan["real_blockers"],
        "checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_validator_md(report)
    return report


def write_validator_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sell pressure absorbed execution delay capacity validator v1",
        "",
        f"status: {report['status']}",
        f"source_summary_status: {report.get('source_summary_status', '')}",
        f"assessment: {report.get('assessment', '')}",
        f"symbol_days_processed_total: {report.get('symbol_days_processed_total', 0)}",
        f"kept_event_count_total: {report.get('kept_event_count_total', 0)}",
        f"replacement_checks_all_true: {str(report.get('replacement_checks_all_true', False)).lower()}",
        "",
        "## Checks",
    ]
    for key, value in report.get("checks", {}).items():
        lines.append(f"- {key}: {str(value).lower()}")
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        report = validate()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "FAILED_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_EXECUTION_DELAY_CAPACITY_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "replacement_checks_all_true": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        VALIDATOR_MD.write_text(
            "# Sell pressure absorbed execution delay capacity validator v1\n\n"
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
