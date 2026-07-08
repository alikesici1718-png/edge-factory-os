#!/usr/bin/env python
"""Validate the 81-symbol Binance USD-M daily aggTrades availability and size manifest."""

from __future__ import annotations

import csv
import json
import os
import re
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
EXPECTED_SYMBOL_COUNT = 81

AGGTRADES_MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_81_aggtrades_availability_manifest.csv"
AGGTRADES_MANIFEST_JSONL = OUTPUTS_DIR / "orderbook_um_81_aggtrades_availability_manifest.jsonl"
AGGTRADES_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_aggtrades_coverage_summary.json"
AGGTRADES_SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_aggtrades_coverage_summary.md"
AGGTRADES_GAPS_CSV = OUTPUTS_DIR / "orderbook_um_81_aggtrades_vs_bookdepth_coverage_gaps.csv"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_81_aggtrades_manifest_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_81_aggtrades_manifest_validator_report.md"

REQUIRED_COLUMNS = [
    "symbol",
    "data_type",
    "frequency",
    "file_date",
    "file_name",
    "url",
    "checksum_url",
    "size_bytes",
    "last_modified",
    "local_target_path",
    "bookdepth_available_same_day",
    "aggtrades_available_same_day",
    "status",
    "error_message",
]

CODE_AND_DOC_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_81_aggtrades_availability_size_audit_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_81_aggtrades_manifest_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_81_aggtrades_availability_size_audit_v1.ps1",
    REPO_ROOT / "run_orderbook_um_81_aggtrades_manifest_validator_v1.ps1",
    REPO_ROOT / "docs" / "orderbook_um_81_aggtrades_availability_size_notes_v1.md",
]
REPORT_FILES = [
    AGGTRADES_SUMMARY_JSON,
    AGGTRADES_SUMMARY_MD,
    AGGTRADES_GAPS_CSV,
]


class AggTradesValidatorBlocked(RuntimeError):
    """Raised when the aggTrades manifest is not safe to use."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def path_is_inside(child: Path, parent: Path) -> bool:
    child_text = os.path.normcase(os.path.abspath(os.fspath(child)))
    parent_text = os.path.normcase(os.path.abspath(os.fspath(parent)))
    return child_text == parent_text or child_text.startswith(parent_text + os.sep)


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise AggTradesValidatorBlocked(f"missing required CSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader], list(reader.fieldnames or [])


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AggTradesValidatorBlocked(f"missing required JSON: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AggTradesValidatorBlocked(f"JSON is not an object: {path}")
    return payload


def assert_public_aggtrades_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "data.binance.vision":
        raise AggTradesValidatorBlocked(f"blocked non-public Binance Data Vision URL: {url}")
    if not parsed.path.startswith("/data/futures/um/daily/aggTrades/"):
        raise AggTradesValidatorBlocked(f"blocked non-USD-M daily aggTrades URL: {url}")
    if "/bookDepth/" in parsed.path or "/klines/" in parsed.path:
        raise AggTradesValidatorBlocked(f"blocked non-aggTrades URL: {url}")


def allowed_safety_context(line: str) -> bool:
    lowered = line.lower()
    tokens = [
        "no ",
        "not ",
        "without",
        "blocked",
        "forbidden",
        "prohibited",
        "safety",
        "refuse",
        "public binance",
        "data vision",
        "aggtrades",
        "bookdepth",
        "orderbook",
        "target path",
        "target directory",
        "raw target",
        "checksum",
        "manifest",
        "availability",
        "size audit",
        "recommended next action",
        "next action",
        "stop due to missing",
        "erroractionpreference",
        "exit $",
        "not a trading",
        "not a backtest",
        "not a signal",
    ]
    return any(token in lowered for token in tokens)


def scan_terms(paths: list[Path]) -> dict[str, Any]:
    patterns = [
        r"\bstrategy\b",
        r"\bbacktest\b",
        r"\bsignal\b",
        r"\bprivate\b",
        r"\baccount\b",
        r"\border execution\b",
        r"\bapi key\b",
        r"\bsecret\b",
        r"\bleverage\b",
        r"\bpnl\b",
        r"\bentry\b",
        r"\bexit\b",
        r"\bstop\b",
        r"\btarget\b",
        r"\bposition sizing\b",
        r"\bbuy\b",
        r"\bsell\b",
        r"\brecommendation\b",
    ]
    matches: list[dict[str, Any]] = []
    blocking: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for pattern in patterns:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    allowed = allowed_safety_context(line)
                    item = {
                        "path": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
                        "line": line_number,
                        "pattern": pattern,
                        "text": line.strip()[:240],
                        "allowed_safety_context": allowed,
                    }
                    matches.append(item)
                    if not allowed:
                        blocking.append(item)
    return {"matches": matches, "blocking_matches": blocking}


def raw_zip_count(raw_target_directory: str) -> int:
    if not raw_target_directory:
        return 0
    path = Path(raw_target_directory)
    if not path.exists():
        return 0
    if path_is_inside(path, REPO_ROOT):
        return 0
    return sum(1 for item in path.rglob("*.zip") if item.is_file())


def build_report() -> dict[str, Any]:
    rows, fieldnames = read_csv_rows(AGGTRADES_MANIFEST_CSV)
    summary = load_json(AGGTRADES_SUMMARY_JSON)
    gaps_rows, _gap_fields = read_csv_rows(AGGTRADES_GAPS_CSV)
    if not AGGTRADES_MANIFEST_JSONL.exists():
        raise AggTradesValidatorBlocked(f"missing required JSONL: {AGGTRADES_MANIFEST_JSONL}")
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    available_rows = [row for row in rows if row.get("status") == "AVAILABLE"]
    symbols = sorted({row.get("symbol", "") for row in rows if row.get("symbol")})
    urls = [row["url"] for row in available_rows if row.get("url")]
    duplicate_urls = sorted(url for url, count in Counter(urls).items() if count > 1)
    invalid_urls: list[str] = []
    invalid_checksum_urls: list[str] = []
    local_paths_inside_repo: list[str] = []
    wrong_type_rows: list[dict[str, str]] = []
    for row in rows:
        if row.get("data_type") != "aggTrades" or row.get("frequency") != "daily":
            wrong_type_rows.append(row)
        if row.get("url"):
            try:
                assert_public_aggtrades_url(row["url"])
            except AggTradesValidatorBlocked as exc:
                invalid_urls.append(str(exc))
        if row.get("checksum_url"):
            try:
                if not row["checksum_url"].endswith(".CHECKSUM"):
                    raise AggTradesValidatorBlocked(f"checksum URL does not end with .CHECKSUM: {row['checksum_url']}")
                assert_public_aggtrades_url(row["checksum_url"].removesuffix(".CHECKSUM"))
            except AggTradesValidatorBlocked as exc:
                invalid_checksum_urls.append(str(exc))
        if row.get("local_target_path") and path_is_inside(Path(row["local_target_path"]), REPO_ROOT):
            local_paths_inside_repo.append(row["local_target_path"])

    checksum_covered = [row for row in available_rows if row.get("checksum_url")]
    checksum_coverage_rate = len(checksum_covered) / len(available_rows) if available_rows else 0.0
    raw_count = raw_zip_count(str(summary.get("raw_target_directory") or ""))
    code_scan = scan_terms(CODE_AND_DOC_FILES)
    report_scan = scan_terms(REPORT_FILES)
    checks = {
        "manifest_csv_exists": AGGTRADES_MANIFEST_CSV.exists(),
        "manifest_jsonl_exists": AGGTRADES_MANIFEST_JSONL.exists(),
        "coverage_summary_json_exists": AGGTRADES_SUMMARY_JSON.exists(),
        "coverage_summary_md_exists": AGGTRADES_SUMMARY_MD.exists(),
        "coverage_gaps_csv_exists": AGGTRADES_GAPS_CSV.exists(),
        "required_columns_exist": not missing_columns,
        "symbols_represented_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
        "summary_symbol_count_requested_81": summary.get("symbol_count_requested") == EXPECTED_SYMBOL_COUNT,
        "urls_public_binance_data_vision": not invalid_urls and not invalid_checksum_urls,
        "rows_are_aggtrades_daily": not wrong_type_rows,
        "no_duplicate_url_rows": not duplicate_urls,
        "checksum_url_coverage_rate_reported": checksum_coverage_rate >= 0.0,
        "size_estimate_exists": isinstance(summary.get("total_estimated_size_gb"), (int, float)),
        "bookdepth_coverage_comparison_exists": isinstance(summary.get("bookdepth_coverage_comparison"), dict),
        "no_raw_downloads_occurred": raw_count == 0,
        "no_output_path_inside_repo_for_raw_data": not local_paths_inside_repo,
        "no_strategy_order_execution_private_api_logic": not code_scan["blocking_matches"],
        "no_forbidden_trading_recommendation_language": not report_scan["blocking_matches"],
    }
    replacement_checks_all_true = all(checks.values())
    return {
        "status": (
            "PASS_ORDERBOOK_UM_81_AGGTRADES_MANIFEST_VALIDATOR"
            if replacement_checks_all_true
            else "BLOCKED_ORDERBOOK_UM_81_AGGTRADES_MANIFEST_VALIDATOR"
        ),
        "created_at_utc": utc_now_text(),
        "manifest_csv": str(AGGTRADES_MANIFEST_CSV),
        "manifest_jsonl": str(AGGTRADES_MANIFEST_JSONL),
        "coverage_summary_json": str(AGGTRADES_SUMMARY_JSON),
        "coverage_gaps_csv": str(AGGTRADES_GAPS_CSV),
        "row_count": len(rows),
        "available_row_count": len(available_rows),
        "gap_row_count": len(gaps_rows),
        "symbol_count": len(symbols),
        "checksum_url_coverage_rate": checksum_coverage_rate,
        "duplicate_urls": duplicate_urls[:50],
        "invalid_url_examples": invalid_urls[:50],
        "invalid_checksum_url_examples": invalid_checksum_urls[:50],
        "local_paths_inside_repo": local_paths_inside_repo[:50],
        "raw_target_zip_count": raw_count,
        "total_estimated_size_gb": summary.get("total_estimated_size_gb"),
        "earliest_global_date": summary.get("earliest_global_date"),
        "latest_global_date": summary.get("latest_global_date"),
        "missing_symbols": summary.get("missing_symbols", []),
        "symbols_with_partial_coverage": summary.get("symbols_with_partial_coverage", []),
        "recommended_next_action": summary.get("recommended_next_action"),
        "code_forbidden_term_scan": code_scan,
        "report_forbidden_term_scan": report_scan,
        "validation_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "next_module": (
            "ORDERBOOK_UM_81_AGGTRADES_DOWNLOAD_DECISION_REVIEW"
            if replacement_checks_all_true
            else "ORDERBOOK_UM_81_AGGTRADES_APPROVAL_OR_BLOCKER_REVIEW"
        ),
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 aggTrades manifest validator v1",
        "",
        f"status: {report['status']}",
        f"row_count: {report.get('row_count', '')}",
        f"available_row_count: {report.get('available_row_count', '')}",
        f"gap_row_count: {report.get('gap_row_count', '')}",
        f"symbol_count: {report.get('symbol_count', '')}",
        f"checksum_url_coverage_rate: {report.get('checksum_url_coverage_rate', 0):.6f}",
        f"total_estimated_size_gb: {report.get('total_estimated_size_gb', '')}",
        f"earliest_global_date: {report.get('earliest_global_date', '')}",
        f"latest_global_date: {report.get('latest_global_date', '')}",
        f"raw_target_zip_count: {report.get('raw_target_zip_count', '')}",
        f"recommended_next_action: {report.get('recommended_next_action', '')}",
        f"replacement_checks_all_true: {bool_text(bool(report['replacement_checks_all_true']))}",
        f"next_module: {report['next_module']}",
        "",
        "## Checks",
    ]
    for key, value in report["validation_checks"].items():
        lines.append(f"- {key}: {bool_text(bool(value))}")
    lines.extend(["", "## Forbidden-term scan"])
    lines.append(f"- code_matches: {len(report.get('code_forbidden_term_scan', {}).get('matches', []))}")
    lines.append(f"- code_blocking_matches: {len(report.get('code_forbidden_term_scan', {}).get('blocking_matches', []))}")
    lines.append(f"- report_matches: {len(report.get('report_forbidden_term_scan', {}).get('matches', []))}")
    lines.append(f"- report_blocking_matches: {len(report.get('report_forbidden_term_scan', {}).get('blocking_matches', []))}")
    lines.append("")
    VALIDATOR_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "BLOCKED_ORDERBOOK_UM_81_AGGTRADES_MANIFEST_VALIDATOR",
            "created_at_utc": utc_now_text(),
            "exact_blocker": str(exc),
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_81_AGGTRADES_APPROVAL_OR_BLOCKER_REVIEW",
        }
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_report_md(report)
    print(f"status: {report['status']}")
    print(f"validator_json: {VALIDATOR_JSON}")
    print(f"validator_md: {VALIDATOR_MD}")
    print(f"replacement_checks_all_true: {bool_text(bool(report['replacement_checks_all_true']))}")
    print(f"next_module: {report['next_module']}")
    return 0 if report["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
