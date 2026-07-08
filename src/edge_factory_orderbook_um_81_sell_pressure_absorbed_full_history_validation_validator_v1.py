#!/usr/bin/env python
"""Validate locked SELL_PRESSURE_ABSORBED full-history validation outputs."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_summary.md"
PERIOD_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_period_stability.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_symbol_stability.csv"
COST_GRID_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_cost_grid.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_null_comparison.csv"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_81_sell_pressure_absorbed_full_history_validation_validator_report.md"

SCANNER_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_full_history_validation_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_full_history_validation_validator_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_sell_pressure_absorbed_full_history_validation_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_sell_pressure_absorbed_full_history_validation_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_orderbook_um_81_sell_pressure_absorbed_full_history_validation_v1.md"

COMPACT_OUTPUTS = [
    SUMMARY_JSON,
    SUMMARY_MD,
    PERIOD_STABILITY_CSV,
    SYMBOL_STABILITY_CSV,
    COST_GRID_CSV,
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

EXPECTED_SYMBOL_DAYS = 99_404
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_CANDIDATE = "SELL_PRESSURE_ABSORBED@300s"
EXPECTED_CATEGORY = "SELL_PRESSURE_ABSORBED"
EXPECTED_HORIZON = 300
EXPECTED_COOLDOWN = 600
EXPECTED_COST_GRID_ROWS = 28
EXPECTED_COSTS = {"0.0", "0.5", "1.0", "2.0", "3.0", "5.0", "10.0"}
EXPECTED_COST_SCOPE_VALUES = {"2023-01-01_TO_2026-06-15", "LATEST_90D", "HOLDOUT_90D", "OLDER_HISTORY"}
ALLOWED_CLASSIFICATIONS = {"FULL_HISTORY_SURVIVED", "RECENT_ONLY", "UNSTABLE", "REJECTED"}

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
    r"\bexecution logic\b",
    r"\bprivate\b",
    r"\bapi key\b",
    r"\bsecret\b",
    r"\brecommendation\b",
    r"\brecommendations\b",
    r"\blive trading\b",
    r"\borders?\b",
]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
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
        return int(str(value))
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
        "validation only",
        "downloads_run",
        "row_level_dataset_created",
        "parquet_dataset_created",
        "no_real_prohibited_behavior",
        "new_filters_added",
        "thresholds_optimized",
    ]
    if any(marker in context_text for marker in safety_markers):
        return "SAFETY_CONTEXT", "safety, absence, or research-boundary wording"
    if term == "exit" and ("exitcode" in context_text or "systemexit" in context_text):
        return "SAFETY_CONTEXT", "runner or process-control context"
    if term.startswith("stop") and "erroractionpreference" in context_text:
        return "SAFETY_CONTEXT", "runner error-control context"
    if "forbidden_patterns" in context_text:
        return "SAFETY_CONTEXT", "scanner pattern declaration"
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
                    classification, reason = "SAFETY_CONTEXT", "scanner pattern declaration"
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
    for path in OUTPUTS_DIR.glob("*sell_pressure_absorbed_full_history_validation*"):
        if path.resolve() in allowed:
            continue
        if path.suffix.lower() in {".parquet", ".jsonl", ".db", ".sqlite", ".duckdb"}:
            matches.append(str(path.relative_to(REPO_ROOT)))
    return matches


def validate() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON) if SUMMARY_JSON.exists() else {}
    period_rows = read_csv_rows(PERIOD_STABILITY_CSV)
    symbol_rows = read_csv_rows(SYMBOL_STABILITY_CSV)
    cost_rows = read_csv_rows(COST_GRID_CSV)
    null_rows = read_csv_rows(NULL_COMPARISON_CSV)
    scan = scan_forbidden_terms()
    raw_inside = raw_book_or_trade_files_inside_repo()
    row_level_outputs = row_level_or_parquet_outputs()
    compact_sizes = {path.name: path.stat().st_size for path in COMPACT_OUTPUTS if path.exists()}

    cost_scope_values = {str(row.get("scope_value", "")) for row in cost_rows}
    costs = {str(row.get("cost_bps", "")) for row in cost_rows}
    period_types = {str(row.get("scope_type", "")) for row in period_rows}
    checks = {
        "summary_exists": SUMMARY_JSON.exists(),
        "summary_status_pass": str(summary.get("status", "")).startswith("PASS"),
        "classification_allowed": str(summary.get("classification", "")) in ALLOWED_CLASSIFICATIONS,
        "candidate_locked": summary.get("candidate") == EXPECTED_CANDIDATE,
        "category_locked": summary.get("locked_category") == EXPECTED_CATEGORY,
        "horizon_locked": int_value(summary.get("locked_horizon_seconds")) == EXPECTED_HORIZON,
        "cooldown_locked": int_value(summary.get("locked_cooldown_seconds")) == EXPECTED_COOLDOWN,
        "processed_expected_symbol_days": int_value(summary.get("symbol_days_processed")) == EXPECTED_SYMBOL_DAYS,
        "failed_symbol_days_zero": int_value(summary.get("failed_symbol_days")) == 0,
        "symbol_count_expected": int_value(summary.get("pair_metadata", {}).get("symbol_count")) == EXPECTED_SYMBOL_COUNT,
        "coverage_start_expected": summary.get("coverage_start") == "2023-01-01",
        "coverage_end_expected": summary.get("coverage_end") == "2026-06-15",
        "all_compact_outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in COMPACT_OUTPUTS),
        "period_stability_has_required_period_types": {"YEAR", "QUARTER", "MONTH", "WEEK", "WINDOW"}.issubset(period_types),
        "symbol_stability_has_81_rows": len(symbol_rows) == EXPECTED_SYMBOL_COUNT,
        "cost_grid_expected_row_count": len(cost_rows) == EXPECTED_COST_GRID_ROWS,
        "cost_grid_scope_values_expected": cost_scope_values == EXPECTED_COST_SCOPE_VALUES,
        "cost_grid_costs_expected": costs == EXPECTED_COSTS,
        "null_comparison_nonzero": len(null_rows) > 0,
        "new_filters_not_added": summary.get("new_filters_added") is False,
        "thresholds_not_optimized": summary.get("thresholds_optimized") is False,
        "summary_confirms_no_row_level_dataset": summary.get("row_level_dataset_created") is False,
        "summary_confirms_no_parquet_dataset": summary.get("parquet_dataset_created") is False,
        "summary_confirms_no_downloads": summary.get("downloads_run") is False,
        "no_raw_book_or_trade_files_inside_repo": not raw_inside,
        "no_row_level_or_parquet_outputs": not row_level_outputs,
        "no_real_prohibited_behavior": not scan["real_blockers"],
    }
    replacement_checks_all_true = all(checks.values())
    status = (
        "PASS_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_FULL_HISTORY_VALIDATOR"
        if replacement_checks_all_true
        else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_FULL_HISTORY_VALIDATION"
    )
    report = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "source_summary_status": summary.get("status", ""),
        "classification": summary.get("classification", ""),
        "runtime_seconds": summary.get("runtime_seconds", 0),
        "symbol_days_processed": summary.get("symbol_days_processed", 0),
        "kept_non_overlap_event_count": summary.get("kept_non_overlap_event_count", 0),
        "break_even_cost_bps": summary.get("full_history_metrics", {}).get("break_even_cost_bps", ""),
        "max_cost_bps_survived_full_history": summary.get("max_cost_bps_survived_full_history", ""),
        "max_cost_bps_survived_latest_holdout_older": summary.get("max_cost_bps_survived_latest_holdout_older", ""),
        "stability": summary.get("stability", {}),
        "worst_quarter": summary.get("worst_quarter", {}),
        "worst_month": summary.get("worst_month", {}),
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
        "# Sell pressure absorbed full-history validator v1",
        "",
        f"status: {report['status']}",
        f"source_summary_status: {report.get('source_summary_status', '')}",
        f"classification: {report.get('classification', '')}",
        f"symbol_days_processed: {report.get('symbol_days_processed', 0)}",
        f"kept_non_overlap_event_count: {report.get('kept_non_overlap_event_count', 0)}",
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
            "status": "FAILED_ORDERBOOK_UM_81_SELL_PRESSURE_ABSORBED_FULL_HISTORY_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "replacement_checks_all_true": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        VALIDATOR_MD.write_text(
            "# Sell pressure absorbed full-history validator v1\n\n"
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
