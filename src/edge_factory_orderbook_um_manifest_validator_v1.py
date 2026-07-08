#!/usr/bin/env python
"""Validate the Binance USD-M orderbook availability manifest before pilot or full download."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.csv"
COVERAGE_JSON = OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.json"
REPORT_JSON = OUTPUTS_DIR / "orderbook_um_manifest_validator_report.json"
REPORT_MD = OUTPUTS_DIR / "orderbook_um_manifest_validator_report.md"
EXPECTED_SYMBOL_COUNT = 81
REQUIRED_COLUMNS = [
    "symbol",
    "data_type",
    "frequency",
    "file_date_or_month",
    "file_name",
    "url",
    "checksum_url",
    "size_bytes",
    "last_modified",
    "earliest_for_symbol",
    "latest_for_symbol",
    "local_target_path",
    "status",
    "error_message",
]

CODE_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_availability_audit_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_pilot_downloader_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_manifest_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_availability_audit_v1.ps1",
    REPO_ROOT / "run_orderbook_um_pilot_download_v1.ps1",
    REPO_ROOT / "run_orderbook_um_manifest_validator_v1.ps1",
]
OUTPUT_SCAN_FILES = [
    MANIFEST_CSV,
    COVERAGE_JSON,
    OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.md",
]


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST_CSV.exists():
        raise FileNotFoundError(f"missing manifest: {MANIFEST_CSV}")
    with MANIFEST_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        fieldnames = list(reader.fieldnames or [])
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"required manifest columns missing: {missing}")
    return rows


def load_summary() -> dict[str, Any]:
    if not COVERAGE_JSON.exists():
        raise FileNotFoundError(f"missing coverage summary: {COVERAGE_JSON}")
    return json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))


def valid_date(text: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", text or ""))


def allowed_safety_context(line: str) -> bool:
    lowered = line.lower()
    return any(
        token in lowered
        for token in [
            "forbidden",
            "blocked",
            "not allowed",
            "no ",
            "no_",
            "false",
            "safety",
            "guard",
            "prohibited",
            "locked",
            "public archive",
            "bookdepth",
            "orderbook",
        ]
    )


def scan_terms(paths: list[Path], output_mode: bool) -> dict[str, Any]:
    terms = [
        r"strategy\.",
        r"\border\b",
        r"\bprivate\b",
        r"apiKey",
        r"\bsecret\b",
        r"\bleverage\b",
        r"position size",
        r"buy signal",
        r"sell signal",
        r"\bentry\b",
        r"take profit",
        r"stop loss",
    ]
    matches: list[dict[str, Any]] = []
    blocking: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for term in terms:
                if re.search(term, line, flags=re.IGNORECASE):
                    allowed = allowed_safety_context(line) or (
                        path.name == "edge_factory_orderbook_um_manifest_validator_v1.py"
                        and line.strip().startswith("r\"")
                    )
                    item = {
                        "path": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
                        "line": line_number,
                        "term": term,
                        "text": line.strip()[:240],
                        "allowed_safety_context": allowed,
                    }
                    matches.append(item)
                    if not item["allowed_safety_context"]:
                        if output_mode or term not in {r"\border\b"}:
                            blocking.append(item)
    return {"matches": matches, "blocking_matches": blocking}


def pilot_rows_available(rows: list[dict[str, str]]) -> dict[str, Any]:
    available = [row for row in rows if row.get("status") == "AVAILABLE" and row.get("url")]
    by_symbol: dict[str, list[dict[str, str]]] = {}
    for row in available:
        by_symbol.setdefault(row["symbol"], []).append(row)
    requested = []
    for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        if symbol in by_symbol:
            requested.append({"symbol": symbol, "available_file_count": len(by_symbol[symbol])})
    btc_periods = sorted(row["file_date_or_month"] for row in by_symbol.get("BTCUSDT", []))
    return {
        "btc_earliest_available": bool(btc_periods),
        "btc_latest_available": bool(btc_periods),
        "eth_latest_available": bool(by_symbol.get("ETHUSDT")),
        "sol_latest_available": bool(by_symbol.get("SOLUSDT")),
        "requested_symbol_probe": requested,
        "pilot_sample_available": bool(btc_periods and by_symbol.get("ETHUSDT") and by_symbol.get("SOLUSDT")),
    }


def build_report() -> dict[str, Any]:
    rows = read_manifest()
    summary = load_summary()
    urls = [row["url"] for row in rows if row.get("url")]
    url_counts = Counter(urls)
    duplicate_urls = sorted(url for url, count in url_counts.items() if count > 1)
    local_paths_inside_repo = [
        row["local_target_path"]
        for row in rows
        if row.get("local_target_path") and path_is_inside(Path(row["local_target_path"]), REPO_ROOT)
    ]
    available_rows = [row for row in rows if row.get("status") == "AVAILABLE"]
    checksum_covered = [row for row in available_rows if row.get("checksum_url")]
    checksum_rate = len(checksum_covered) / len(available_rows) if available_rows else 0.0
    earliest_values = [row["earliest_for_symbol"] for row in available_rows if row.get("earliest_for_symbol")]
    latest_values = [row["latest_for_symbol"] for row in available_rows if row.get("latest_for_symbol")]
    date_parse_failures = [
        row
        for row in available_rows
        if not valid_date(row.get("file_date_or_month", ""))
        or (row.get("earliest_for_symbol") and not valid_date(row["earliest_for_symbol"]))
        or (row.get("latest_for_symbol") and not valid_date(row["latest_for_symbol"]))
    ]
    size_values: list[int] = []
    for row in available_rows:
        raw = row.get("size_bytes") or ""
        if raw:
            try:
                size_values.append(int(raw))
            except ValueError:
                date_parse_failures.append(row)
    pilot = pilot_rows_available(rows)
    code_scan = scan_terms(CODE_FILES, output_mode=False)
    output_scan = scan_terms(OUTPUT_SCAN_FILES, output_mode=True)
    checks = {
        "manifest_exists": MANIFEST_CSV.exists(),
        "coverage_summary_exists": COVERAGE_JSON.exists(),
        "required_manifest_columns_exist": True,
        "no_local_target_path_inside_git_repo": len(local_paths_inside_repo) == 0,
        "no_duplicate_url_rows": len(duplicate_urls) == 0,
        "checksum_url_coverage_rate_recorded": checksum_rate >= 0.0,
        "earliest_latest_date_parsing_valid": bool(earliest_values and latest_values) and len(date_parse_failures) == 0,
        "missing_symbol_count_recorded": isinstance(summary.get("symbol_count_missing"), int),
        "requested_symbol_count_verified_81": summary.get("symbol_count_requested") == EXPECTED_SYMBOL_COUNT,
        "estimated_total_size_recorded": isinstance(summary.get("total_estimated_size_bytes"), int),
        "pilot_sample_availability": pilot["pilot_sample_available"],
        "no_forbidden_private_or_flag_terms_in_code": len(code_scan["blocking_matches"]) == 0,
        "no_unapproved_strategy_order_signal_language_in_outputs": len(output_scan["blocking_matches"]) == 0,
    }
    checks["replacement_checks_all_true"] = all(checks.values())
    return {
        "status": "PASS_ORDERBOOK_UM_MANIFEST_VALIDATOR" if checks["replacement_checks_all_true"] else "BLOCKED_ORDERBOOK_UM_MANIFEST_VALIDATOR",
        "manifest_csv": str(MANIFEST_CSV),
        "coverage_summary_json": str(COVERAGE_JSON),
        "row_count": len(rows),
        "available_row_count": len(available_rows),
        "duplicate_urls": duplicate_urls[:50],
        "local_paths_inside_repo": local_paths_inside_repo[:50],
        "checksum_url_coverage_rate": checksum_rate,
        "earliest_global_date": summary.get("earliest_global_date"),
        "latest_global_date": summary.get("latest_global_date"),
        "missing_symbol_count": summary.get("symbol_count_missing"),
        "estimated_total_size_bytes": summary.get("total_estimated_size_bytes"),
        "estimated_total_size_gb": summary.get("total_estimated_size_gb"),
        "pilot_sample_availability": pilot,
        "code_forbidden_term_scan": code_scan,
        "output_forbidden_term_scan": output_scan,
        "validation_checks": checks,
        "replacement_checks_all_true": checks["replacement_checks_all_true"],
        "next_module": "ORDERBOOK_UM_PILOT_DOWNLOADER_V1" if checks["replacement_checks_all_true"] else "ORDERBOOK_UM_BLOCKER_REVIEW",
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM manifest validator v1",
        "",
        f"status: {report['status']}",
        f"row_count: {report['row_count']}",
        f"available_row_count: {report['available_row_count']}",
        f"checksum_url_coverage_rate: {report['checksum_url_coverage_rate']:.6f}",
        f"earliest_global_date: {report['earliest_global_date']}",
        f"latest_global_date: {report['latest_global_date']}",
        f"missing_symbol_count: {report['missing_symbol_count']}",
        f"estimated_total_size_gb: {report['estimated_total_size_gb']}",
        f"replacement_checks_all_true: {str(report['replacement_checks_all_true']).lower()}",
        f"next_module: {report['next_module']}",
        "",
        "## Checks",
    ]
    for key, value in report["validation_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Reported term matches"])
    for match in (report["code_forbidden_term_scan"]["matches"] + report["output_forbidden_term_scan"]["matches"])[:100]:
        lines.append(
            f"- {match['path']}:{match['line']} term={match['term']} allowed_safety_context={match['allowed_safety_context']}"
        )
    lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "BLOCKED_ORDERBOOK_UM_MANIFEST_VALIDATOR",
            "exact_blocker": str(exc),
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_BLOCKER_REVIEW",
        }
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_report_md(report)
    print(f"status: {report['status']}")
    print(f"manifest_csv: {MANIFEST_CSV}")
    print(f"coverage_summary_json: {COVERAGE_JSON}")
    print(f"validator_report_json: {REPORT_JSON}")
    print(f"replacement_checks_all_true: {str(report['replacement_checks_all_true']).lower()}")
    print(f"next_module: {report['next_module']}")
    return 0 if report["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
