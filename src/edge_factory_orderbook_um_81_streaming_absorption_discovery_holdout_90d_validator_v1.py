#!/usr/bin/env python
"""Validate compact holdout 90-day absorption discovery outputs."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_summary.md"
CANDIDATE_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_candidate_comparison.csv"
SIGN_AUDIT_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_sign_audit.csv"
STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_stability.csv"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_holdout_90d_validator_report.md"

SCANNER_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_streaming_absorption_discovery_holdout_90d_v1.py"
VALIDATOR_PATH = REPO_ROOT / "src" / "edge_factory_orderbook_um_81_streaming_absorption_discovery_holdout_90d_validator_v1.py"
RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_streaming_absorption_discovery_holdout_90d_v1.ps1"
VALIDATOR_RUNNER_PATH = REPO_ROOT / "run_edge_factory_orderbook_um_81_streaming_absorption_discovery_holdout_90d_validator_v1.ps1"
DOCS_PATH = REPO_ROOT / "docs" / "edge_factory_orderbook_um_81_streaming_absorption_discovery_holdout_90d_v1.md"

CODE_AND_REPORT_FILES = [
    SCANNER_PATH,
    VALIDATOR_PATH,
    RUNNER_PATH,
    VALIDATOR_RUNNER_PATH,
    DOCS_PATH,
    SUMMARY_MD,
    VALIDATOR_MD,
]
COMPACT_OUTPUTS = [
    SUMMARY_JSON,
    SUMMARY_MD,
    CANDIDATE_COMPARISON_CSV,
    SIGN_AUDIT_CSV,
    STABILITY_CSV,
]

EXPECTED_SYMBOL_COUNT = 81
EXPECTED_CANDIDATE_COUNT = 5
EXPECTED_STABILITY_ROWS = 15
EXPECTED_HOLDOUT_SYMBOL_DAYS = 7290
EXPECTED_CATEGORIES = {
    "BUY_PRESSURE_ABSORBED",
    "SELL_PRESSURE_ABSORBED",
    "FLOW_AND_DEPTH_ALIGNED_UP",
    "FLOW_AND_DEPTH_ALIGNED_DOWN",
    "MIXED_OR_NOISY",
    "INSUFFICIENT_DATA",
}
EXPECTED_HORIZONS = {"10", "30", "60", "300"}

FORBIDDEN_PATTERNS = [
    r"\bstrategy\b",
    r"\bbacktest\b",
    r"\bsignal\b",
    r"\bpnl\b",
    r"\bentry\b",
    r"\bexit\b",
    r"\bstop\b",
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
        "research-only",
        "downloads_run",
        "no_real_prohibited_behavior",
    ]
    if any(marker in context_text for marker in safety_markers):
        return "SAFETY_CONTEXT", "safety, absence, or refusal wording"
    if term == "exit" and ("exitcode" in context_text or "systemexit" in context_text):
        return "SAFETY_CONTEXT", "runner or process-control context"
    if term == "stop" and "erroractionpreference" in context_text:
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
    matches: list[str] = []
    allowed = {path.resolve() for path in COMPACT_OUTPUTS + [VALIDATOR_JSON, VALIDATOR_MD]}
    for path in OUTPUTS_DIR.glob("*streaming_absorption_discovery_holdout_90d*"):
        if path.resolve() in allowed:
            continue
        if path.suffix.lower() in {".parquet", ".jsonl", ".db", ".sqlite", ".duckdb"}:
            matches.append(str(path.relative_to(REPO_ROOT)))
    return matches


def validate() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON) if SUMMARY_JSON.exists() else {}
    comparison_rows = read_csv_rows(CANDIDATE_COMPARISON_CSV)
    sign_rows = read_csv_rows(SIGN_AUDIT_CSV)
    stability_rows = read_csv_rows(STABILITY_CSV)
    scan = scan_forbidden_terms()
    raw_inside = raw_book_or_trade_files_inside_repo()
    row_level_outputs = row_level_or_parquet_outputs()
    horizons = {str(item) for item in summary.get("horizon_seconds", [])}
    categories = set(summary.get("categories_found", []))
    compact_sizes = {path.name: path.stat().st_size for path in COMPACT_OUTPUTS if path.exists()}

    checks = {
        "summary_exists": SUMMARY_JSON.exists(),
        "summary_status_completed": str(summary.get("status", "")).startswith("PASS"),
        "all_compact_outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in COMPACT_OUTPUTS),
        "selected_81_symbols": int_value(summary.get("selected_symbol_count")) == EXPECTED_SYMBOL_COUNT,
        "processed_expected_symbol_days": int_value(summary.get("processed_symbol_days")) == EXPECTED_HOLDOUT_SYMBOL_DAYS,
        "failed_symbol_days_zero": int_value(summary.get("failed_symbol_days")) == 0,
        "candidate_comparison_has_five_rows": len(comparison_rows) == EXPECTED_CANDIDATE_COUNT,
        "sign_audit_has_five_rows": len(sign_rows) == EXPECTED_CANDIDATE_COUNT,
        "stability_has_three_rows_per_candidate": len(stability_rows) == EXPECTED_STABILITY_ROWS,
        "categories_cover_expected": EXPECTED_CATEGORIES.issubset(categories),
        "horizons_cover_expected": EXPECTED_HORIZONS.issubset(horizons),
        "valid_forward_observations_nonzero": int_value(summary.get("valid_forward_observations")) > 0,
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
        "PASS_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_HOLDOUT_90D_VALIDATED"
        if replacement_checks_all_true
        else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_HOLDOUT_90D_VALIDATION"
    )
    report = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "source_summary_status": summary.get("status", ""),
        "runtime_seconds": summary.get("runtime_seconds", 0),
        "processed_symbol_days": summary.get("processed_symbol_days", 0),
        "survived_candidates": summary.get("survived_candidates", []),
        "failed_candidates": summary.get("failed_candidates", []),
        "candidate_comparison": comparison_rows,
        "sign_audit": sign_rows,
        "stability_rows": stability_rows,
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
        "# Orderbook UM 81 streaming absorption discovery holdout 90d validator v1",
        "",
        f"status: {report['status']}",
        f"source_summary_status: {report.get('source_summary_status', '')}",
        f"processed_symbol_days: {report.get('processed_symbol_days', 0)}",
        f"replacement_checks_all_true: {str(report.get('replacement_checks_all_true', False)).lower()}",
        "",
        "## Checks",
    ]
    for key, value in report.get("checks", {}).items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(["", "## Candidate Comparison"])
    for row in report.get("candidate_comparison", []):
        lines.append(
            "- "
            f"{row.get('category')} @ {row.get('horizon_seconds')}s: {row.get('holdout_status')} "
            f"holdout_effect_size={row.get('holdout_effect_size_vs_null')}"
        )
    VALIDATOR_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        report = validate()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "FAILED_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_HOLDOUT_90D_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "replacement_checks_all_true": False,
        }
        VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        VALIDATOR_MD.write_text(
            "# Orderbook UM 81 streaming absorption discovery holdout 90d validator v1\n\n"
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
