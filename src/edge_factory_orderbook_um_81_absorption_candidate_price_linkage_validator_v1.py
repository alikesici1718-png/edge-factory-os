#!/usr/bin/env python
"""Validate absorption candidate price-linkage compact outputs."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_summary.md"
CANDIDATE_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_candidate_comparison.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_symbol_stability.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_null_comparison.csv"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_81_absorption_candidate_price_linkage_validator_report.md"

SCANNER_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validation_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validator_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validation_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_orderbook_um_81_absorption_candidate_price_linkage_validation_v1.md"

COMPACT_OUTPUTS = [
    SUMMARY_JSON,
    SUMMARY_MD,
    CANDIDATE_COMPARISON_CSV,
    SYMBOL_STABILITY_CSV,
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

EXPECTED_SYMBOL_DAYS_TOTAL = 14_580
EXPECTED_CANDIDATES = {
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", "300"),
    ("SELL_PRESSURE_ABSORBED", "300"),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", "60"),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", "30"),
    ("FLOW_AND_DEPTH_ALIGNED_DOWN", "10"),
}
EXPECTED_WINDOWS = {"LATEST_90D", "HOLDOUT_90D"}

FORBIDDEN_PATTERNS = [
    r"\bstrategy\b",
    r"\bbacktest\b",
    r"\bsignal\b",
    r"\bpnl\b",
    r"\bentry\b",
    r"\bexit\b",
    r"\bstop\b",
    r"\btarget\b",
    r"\bleverage\b",
    r"\bposition sizing\b",
    r"\border execution\b",
    r"\bexecution logic\b",
    r"\bprivate\b",
    r"\bapi key\b",
    r"\bsecret\b",
    r"\brecommendation\b",
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
        return int(value)
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
        "downloads_run",
        "no_real_prohibited_behavior",
    ]
    if any(marker in context_text for marker in safety_markers):
        return "SAFETY_CONTEXT", "safety, absence, or research-boundary wording"
    if term == "exit" and ("exitcode" in context_text or "systemexit" in context_text):
        return "SAFETY_CONTEXT", "runner or process-control context"
    if term == "stop" and "erroractionpreference" in context_text:
        return "SAFETY_CONTEXT", "runner error-control context"
    if term == "target" and ("price target" in context_text or "user request" in context_text):
        return "SAFETY_CONTEXT", "quoted research request wording"
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
    for path in OUTPUTS_DIR.glob("*absorption_candidate_price_linkage*"):
        if path.resolve() in allowed:
            continue
        if path.suffix.lower() in {".parquet", ".jsonl", ".db", ".sqlite", ".duckdb"}:
            matches.append(str(path.relative_to(REPO_ROOT)))
    return matches


def validate() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON) if SUMMARY_JSON.exists() else {}
    comparison_rows = read_csv_rows(CANDIDATE_COMPARISON_CSV)
    stability_rows = read_csv_rows(SYMBOL_STABILITY_CSV)
    null_rows = read_csv_rows(NULL_COMPARISON_CSV)
    scan = scan_forbidden_terms()
    raw_inside = raw_book_or_trade_files_inside_repo()
    row_level_outputs = row_level_or_parquet_outputs()
    compact_sizes = {path.name: path.stat().st_size for path in COMPACT_OUTPUTS if path.exists()}

    comparison_candidates = {
        (str(row.get("category", "")), str(row.get("horizon_seconds", "")))
        for row in comparison_rows
    }
    null_windows = {str(row.get("window", "")) for row in null_rows}
    stability_windows = {str(row.get("window", "")) for row in stability_rows}
    checks = {
        "summary_exists": SUMMARY_JSON.exists(),
        "summary_status_pass": str(summary.get("status", "")).startswith("PASS"),
        "all_compact_outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in COMPACT_OUTPUTS),
        "processed_expected_symbol_days": int_value(summary.get("symbol_days_processed_total")) == EXPECTED_SYMBOL_DAYS_TOTAL,
        "failed_symbol_days_zero": int_value(summary.get("failed_symbol_days_total")) == 0,
        "candidate_comparison_has_five_rows": len(comparison_rows) == len(EXPECTED_CANDIDATES),
        "candidate_comparison_matches_fixed_candidates": comparison_candidates == EXPECTED_CANDIDATES,
        "null_comparison_has_both_windows": EXPECTED_WINDOWS.issubset(null_windows),
        "stability_has_both_windows": EXPECTED_WINDOWS.issubset(stability_windows),
        "valid_price_observations_nonzero": int_value(summary.get("valid_price_observations_total")) > 0,
        "raw_roots_outside_repo": not path_is_inside(Path(str(summary.get("raw_bookdepth_root", ""))), REPO_ROOT) and not path_is_inside(
            Path(str(summary.get("raw_aggtrades_root", ""))),
            REPO_ROOT,
        ),
        "no_raw_book_or_trade_files_inside_repo": not raw_inside,
        "no_row_level_or_parquet_outputs": not row_level_outputs,
        "summary_confirms_no_row_level_dataset": summary.get("row_level_dataset_created") is False,
        "summary_confirms_no_parquet_dataset": summary.get("parquet_dataset_created") is False,
        "summary_confirms_no_downloads": summary.get("downloads_run") is False,
        "no_real_prohibited_behavior": not scan["real_blockers"],
    }
    replacement_checks_all_true = all(checks.values())
    status = (
        "PASS_ORDERBOOK_UM_81_ABSORPTION_CANDIDATE_PRICE_LINKAGE_VALIDATOR"
        if replacement_checks_all_true
        else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_ABSORPTION_CANDIDATE_PRICE_LINKAGE_VALIDATION"
    )
    report = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "source_summary_status": summary.get("status", ""),
        "runtime_seconds": summary.get("runtime_seconds", 0),
        "symbol_days_processed_total": summary.get("symbol_days_processed_total", 0),
        "survived_price_linkage_candidates": summary.get("survived_price_linkage_candidates", []),
        "failed_price_linkage_candidates": summary.get("failed_price_linkage_candidates", []),
        "candidate_comparison": comparison_rows,
        "null_comparison": null_rows,
        "stability_row_count": len(stability_rows),
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
        "# Orderbook UM 81 absorption candidate price linkage validator v1",
        "",
        f"status: {report['status']}",
        f"source_summary_status: {report.get('source_summary_status', '')}",
        f"symbol_days_processed_total: {report.get('symbol_days_processed_total', 0)}",
        f"replacement_checks_all_true: {str(report.get('replacement_checks_all_true', False)).lower()}",
        "",
        "## Checks",
    ]
    for key, value in report.get("checks", {}).items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(["", "## Candidate Results"])
    for row in report.get("candidate_comparison", []):
        lines.append(
            "- "
            f"{row.get('category')} @ {row.get('horizon_seconds')}s: {row.get('price_linkage_status')} "
            f"latest={row.get('latest_price_effect_size_vs_null')} "
            f"holdout={row.get('holdout_price_effect_size_vs_null')}"
        )
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        report = validate()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "FAILED_ORDERBOOK_UM_81_ABSORPTION_CANDIDATE_PRICE_LINKAGE_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "replacement_checks_all_true": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        VALIDATOR_MD.write_text(
            "# Orderbook UM 81 absorption candidate price linkage validator v1\n\n"
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
