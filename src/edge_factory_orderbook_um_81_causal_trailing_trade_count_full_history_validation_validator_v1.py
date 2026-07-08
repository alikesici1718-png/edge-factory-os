#!/usr/bin/env python
"""Validate causal trailing trade-count full-history validation outputs."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_causal_trailing_trade_count_full_history_validation"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
PERIOD_STABILITY_CSV = OUTPUTS_DIR / f"{PREFIX}_period_stability.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / f"{PREFIX}_symbol_stability.csv"
DELAY_COST_GRID_CSV = OUTPUTS_DIR / f"{PREFIX}_delay_cost_grid.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / f"{PREFIX}_null_comparison.csv"
CHUNK_PROGRESS_CSV = OUTPUTS_DIR / f"{PREFIX}_chunk_progress.csv"
COMPLETED_CHUNKS_MANIFEST_JSON = OUTPUTS_DIR / f"{PREFIX}_completed_chunks_manifest.json"
PARTIAL_AGGREGATE_SUMMARIES_JSON = OUTPUTS_DIR / f"{PREFIX}_partial_aggregate_summaries.json"
CHUNK_OUTPUT_DIR = OUTPUTS_DIR / f"{PREFIX}_chunks"
VALIDATOR_JSON = OUTPUTS_DIR / f"{PREFIX}_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / f"{PREFIX}_validator_report.md"

SCANNER_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_validator_v1.py"
REPAIR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_causal_capacity_filter_repair_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.md"

COMPACT_OUTPUTS = [
    SUMMARY_JSON,
    SUMMARY_MD,
    PERIOD_STABILITY_CSV,
    SYMBOL_STABILITY_CSV,
    DELAY_COST_GRID_CSV,
    NULL_COMPARISON_CSV,
    CHUNK_PROGRESS_CSV,
    COMPLETED_CHUNKS_MANIFEST_JSON,
    PARTIAL_AGGREGATE_SUMMARIES_JSON,
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

EXPECTED_STATUS = "PASS_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATED"
EXPECTED_PARTIAL_STATUS = "SMOKE_OR_PARTIAL_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATION_CHUNKED"
EXPECTED_STATUSES = {EXPECTED_STATUS, EXPECTED_PARTIAL_STATUS}
EXPECTED_SYMBOL_DAYS = 99_404
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_CANDIDATE = "SELL_PRESSURE_ABSORBED@300s"
EXPECTED_CATEGORY = "SELL_PRESSURE_ABSORBED"
EXPECTED_HORIZON = 300
EXPECTED_COOLDOWN = 600
EXPECTED_FILTER = "TRAILING_TRADE_COUNT_60S_GE_100"
EXPECTED_DELAYS = {0, 1, 3, 5, 10}
EXPECTED_COSTS = {0.0, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0}
EXPECTED_SCOPE_VALUES = {"2023-01-01_TO_2026-06-15", "LATEST_90D", "HOLDOUT_90D", "OLDER_HISTORY"}
EXPECTED_DELAY_COST_ROWS = len(EXPECTED_SCOPE_VALUES) * len(EXPECTED_DELAYS) * len(EXPECTED_COSTS)
EXPECTED_NULL_ROWS = len(EXPECTED_SCOPE_VALUES) * len(EXPECTED_DELAYS)
ALLOWED_CLASSIFICATIONS = {
    "FULL_HISTORY_SURVIVED",
    "RECENT_ONLY",
    "FILTER_ONLY",
    "UNSTABLE",
    "REJECTED",
    "PARTIAL_CHUNKED_SMOKE",
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
    r"\bexecution logic\b",
    r"\bprivate endpoints?\b",
    r"\bapi key\b",
    r"\bsecret\b",
    r"\brecommendations?\b",
    r"\blive trading\b",
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
        "validation only",
        "downloads_run",
        "row_level_dataset_created",
        "parquet_dataset_created",
        "strategy_created",
        "backtest_created",
        "pnl_created",
        "signals_created",
        "orders_created",
        "private_endpoints_used",
        "recommendations_created",
        "no_real_prohibited_behavior",
        "new_filters_added",
        "thresholds_optimized",
        ": false",
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


def scanner_selection_blocker_matches() -> list[dict[str, Any]]:
    if not SCANNER_PATH.exists():
        return [{"pattern": "scanner_missing", "line": 0, "text": str(SCANNER_PATH)}]
    lines = SCANNER_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    checks = [
        ("event_ms_plus_in_scanner", re.compile(r"event_ms\s*\+")),
        ("notional_around_event_call", re.compile(r"\bnotional_around_event\s*\(")),
        ("capacity_window_radius_helper", re.compile(r"\bCAPACITY_WINDOW_RADIUS_MS\b")),
        ("post_event_notional_selection", re.compile(r"post[-_ ]event.*notional.*selection", re.IGNORECASE)),
        ("post_event_trade_count_selection", re.compile(r"post[-_ ]event.*trade.*count.*selection", re.IGNORECASE)),
    ]
    matches: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        for name, pattern in checks:
            if pattern.search(line):
                matches.append({"pattern": name, "line": line_number, "text": line.strip()[:240]})
    return matches


def repair_trailing_slice_is_causal() -> bool:
    if not REPAIR_PATH.exists():
        return False
    source = REPAIR_PATH.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"def trailing_trade_slice\(.*?(?=\ndef |\Z)", source, flags=re.DOTALL)
    if not match:
        return False
    block = match.group(0)
    return "event_ms +" not in block and "bisect_left(trade_times, event_ms)" in block


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
    period_rows = read_csv_rows(PERIOD_STABILITY_CSV)
    symbol_rows = read_csv_rows(SYMBOL_STABILITY_CSV)
    cost_rows = read_csv_rows(DELAY_COST_GRID_CSV)
    null_rows = read_csv_rows(NULL_COMPARISON_CSV)
    chunk_rows = read_csv_rows(CHUNK_PROGRESS_CSV)
    manifest = load_json(COMPLETED_CHUNKS_MANIFEST_JSON)
    partial_summaries = load_json(PARTIAL_AGGREGATE_SUMMARIES_JSON)
    scan = scan_forbidden_terms()
    selection_blockers = scanner_selection_blocker_matches()
    row_level_outputs = row_level_or_parquet_outputs()
    compact_sizes = {path.name: path.stat().st_size for path in COMPACT_OUTPUTS if path.exists()}

    delay_set = {int_value(item, -1) for item in summary.get("delay_seconds", [])}
    cost_set = {float_value(item) for item in summary.get("cost_grid_bps", [])}
    cost_scope_values = {str(row.get("scope_value", "")) for row in cost_rows}
    cost_delays = {int_value(row.get("delay_seconds"), -1) for row in cost_rows}
    cost_values = {float_value(row.get("cost_bps")) for row in cost_rows}
    null_scope_values = {str(row.get("scope_value", "")) for row in null_rows}
    null_delays = {int_value(row.get("delay_seconds"), -1) for row in null_rows}
    period_types_delay0 = {
        str(row.get("scope_type", ""))
        for row in period_rows
        if int_value(row.get("delay_seconds"), -1) == 0
    }
    symbol_delay0 = {
        str(row.get("symbol", ""))
        for row in symbol_rows
        if int_value(row.get("delay_seconds"), -1) == 0 and str(row.get("symbol", ""))
    }
    output_paths = [Path(str(value)) for value in summary.get("outputs", {}).values() if value]
    outputs_inside_repo = all(path_is_inside(path, REPO_ROOT) for path in output_paths) if output_paths else False
    source_status = str(summary.get("status", ""))
    is_full_complete = source_status == EXPECTED_STATUS
    is_chunked_partial = source_status == EXPECTED_PARTIAL_STATUS
    processed_symbol_days = int_value(summary.get("symbol_days_processed"))
    completed_chunk_count = int_value(summary.get("completed_chunk_count"))
    chunk_count_total = int_value(summary.get("chunk_count_total"))
    chunk_json_count = len(list(CHUNK_OUTPUT_DIR.glob(f"{PREFIX}_*_chunk_summary.json"))) if CHUNK_OUTPUT_DIR.exists() else 0

    checks = {
        "summary_exists": SUMMARY_JSON.exists(),
        "summary_status_pass_or_chunked_partial": source_status in EXPECTED_STATUSES,
        "classification_allowed": str(summary.get("classification", "")) in ALLOWED_CLASSIFICATIONS,
        "candidate_locked": summary.get("candidate") == EXPECTED_CANDIDATE,
        "category_locked": summary.get("locked_category") == EXPECTED_CATEGORY,
        "horizon_locked": int_value(summary.get("locked_horizon_seconds")) == EXPECTED_HORIZON,
        "cooldown_locked": int_value(summary.get("locked_cooldown_seconds")) == EXPECTED_COOLDOWN,
        "filter_locked": summary.get("locked_causal_filter") == EXPECTED_FILTER,
        "filter_definition_expected": "[event_ms - 60s, event_ms)" in str(summary.get("filter_definition", "")),
        "delay_set_expected": delay_set == EXPECTED_DELAYS,
        "cost_set_expected": cost_set == EXPECTED_COSTS,
        "processed_symbol_days_valid_for_status": (
            processed_symbol_days == EXPECTED_SYMBOL_DAYS
            if is_full_complete
            else is_chunked_partial and 0 < processed_symbol_days < EXPECTED_SYMBOL_DAYS
        ),
        "failed_symbol_days_zero": int_value(summary.get("failed_symbol_days")) == 0,
        "symbol_count_expected": int_value(summary.get("pair_metadata", {}).get("symbol_count")) == EXPECTED_SYMBOL_COUNT,
        "coverage_start_expected": summary.get("coverage_start") == "2023-01-01",
        "coverage_end_expected": summary.get("coverage_end") == "2026-06-15",
        "causal_filter_has_events": int_value(summary.get("event_count_after_causal_filter")) > 0,
        "causal_filter_selection_flags_false": summary.get("candidate_selection_uses_future_window") is False
        and summary.get("candidate_selection_uses_post_event_notional") is False
        and summary.get("candidate_selection_uses_post_event_trade_count") is False
        and summary.get("candidate_selection_uses_around_event_helper") is False,
        "scanner_source_no_selection_blockers": not selection_blockers,
        "repair_trailing_slice_causal": repair_trailing_slice_is_causal(),
        "all_compact_outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in COMPACT_OUTPUTS),
        "outputs_inside_repo_compact_only": outputs_inside_repo,
        "chunked_resume_enabled": summary.get("chunked_resume_enabled") is True,
        "chunk_period_month_or_quarter": str(summary.get("chunk_period", "")) in {"month", "quarter"},
        "chunk_workers_capped": 1 <= int_value(summary.get("requested_chunk_workers"), 1) <= 4,
        "effective_workers_safe": int_value(summary.get("effective_chunk_workers"), 0) == 1,
        "completed_chunks_manifest_exists": COMPLETED_CHUNKS_MANIFEST_JSON.exists()
        and manifest.get("resume_safe") is True
        and int_value(manifest.get("completed_chunk_count")) == completed_chunk_count,
        "chunk_progress_csv_exists": CHUNK_PROGRESS_CSV.exists() and len(chunk_rows) == chunk_count_total,
        "partial_aggregate_summaries_exists": PARTIAL_AGGREGATE_SUMMARIES_JSON.exists()
        and int_value(partial_summaries.get("completed_chunk_count")) == completed_chunk_count,
        "completed_chunk_jsons_exist": completed_chunk_count > 0 and chunk_json_count >= completed_chunk_count,
        "period_stability_has_required_period_types": {"YEAR", "QUARTER", "MONTH", "WEEK", "WINDOW"}.issubset(period_types_delay0),
        "symbol_stability_has_symbol_support": len(symbol_delay0) > 0,
        "delay_cost_grid_expected_row_count": len(cost_rows) == EXPECTED_DELAY_COST_ROWS,
        "delay_cost_scope_values_expected": cost_scope_values == EXPECTED_SCOPE_VALUES,
        "delay_cost_delays_expected": cost_delays == EXPECTED_DELAYS,
        "delay_cost_costs_expected": cost_values == EXPECTED_COSTS,
        "null_comparison_expected_row_count": len(null_rows) == EXPECTED_NULL_ROWS,
        "null_comparison_scope_values_expected": null_scope_values == EXPECTED_SCOPE_VALUES,
        "null_comparison_delays_expected": null_delays == EXPECTED_DELAYS,
        "new_filters_not_added": summary.get("new_filters_added") is False,
        "thresholds_not_optimized": summary.get("thresholds_optimized") is False,
        "summary_confirms_no_row_level_dataset": summary.get("row_level_dataset_created") is False,
        "summary_confirms_no_parquet_dataset": summary.get("parquet_dataset_created") is False,
        "summary_confirms_no_downloads": summary.get("downloads_run") is False,
        "summary_confirms_no_raw_modification": summary.get("raw_data_modified") is False,
        "summary_confirms_no_strategy": summary.get("strategy_created") is False,
        "summary_confirms_no_backtest": summary.get("backtest_created") is False,
        "summary_confirms_no_pnl": summary.get("pnl_created") is False,
        "summary_confirms_no_signals": summary.get("signals_created") is False,
        "summary_confirms_no_orders": summary.get("orders_created") is False,
        "summary_confirms_no_private_endpoints": summary.get("private_endpoints_used") is False,
        "summary_confirms_no_recommendations": summary.get("recommendations_created") is False,
        "no_row_level_or_parquet_outputs": not row_level_outputs,
        "no_real_prohibited_behavior": not scan["real_blockers"],
    }
    replacement_checks_all_true = all(checks.values())
    status = (
        "PASS_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATOR"
        if replacement_checks_all_true
        else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATION"
    )
    report = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "source_summary_status": summary.get("status", ""),
        "classification": summary.get("classification", ""),
        "runtime_seconds": summary.get("runtime_seconds", 0),
        "completed_chunk_count": summary.get("completed_chunk_count", 0),
        "pending_chunk_count": summary.get("pending_chunk_count", 0),
        "estimated_full_runtime_seconds": summary.get("estimated_full_runtime_seconds", ""),
        "event_count_after_causal_filter": summary.get("event_count_after_causal_filter", 0),
        "full_history_metrics_delay0": summary.get("full_history_metrics_delay0", {}),
        "delay_survival": summary.get("delay_survival", {}),
        "worst_month": summary.get("worst_month", {}),
        "worst_quarter": summary.get("worst_quarter", {}),
        "compact_output_sizes_bytes": compact_sizes,
        "scanner_selection_blocker_matches": selection_blockers,
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
        "# Causal trailing trade-count full-history validator v1",
        "",
        f"status: {report['status']}",
        f"source_summary_status: {report.get('source_summary_status', '')}",
        f"classification: {report.get('classification', '')}",
        f"completed_chunk_count: {report.get('completed_chunk_count', '')}",
        f"pending_chunk_count: {report.get('pending_chunk_count', '')}",
        f"estimated_full_runtime_seconds: {report.get('estimated_full_runtime_seconds', '')}",
        f"event_count_after_causal_filter: {report.get('event_count_after_causal_filter', '')}",
        f"replacement_checks_all_true: {str(report.get('replacement_checks_all_true', False)).lower()}",
        "",
        "## Checks",
    ]
    for key, value in report.get("checks", {}).items():
        lines.append(f"- {key}: {str(value).lower()}")
    if report.get("scanner_selection_blocker_matches"):
        lines.append("")
        lines.append("## Selection Blocker Matches")
        for item in report["scanner_selection_blocker_matches"]:
            lines.append(f"- {item.get('pattern')}: line {item.get('line')} {item.get('text')}")
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        report = validate()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "FAILED_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "replacement_checks_all_true": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        VALIDATOR_MD.write_text(
            "# Causal trailing trade-count full-history validator v1\n\n"
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
