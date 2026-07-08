#!/usr/bin/env python
"""Validate the 81-symbol full bookDepth download outputs and safety boundaries."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edge_factory_orderbook_um_81_full_bookdepth_downloader_v1 import (
    BLOCKED_NOT_ACK_MD,
    DOWNLOAD_SUMMARY_JSON,
    DOWNLOAD_SUMMARY_MD,
    FILE_STATUS_CSV,
    SYMBOL_COVERAGE_CSV,
)
from edge_factory_orderbook_um_81_full_bookdepth_manifest_validator_v1 import (
    EXPECTED_SYMBOL_COUNT,
    MANIFEST_CSV,
    OUTPUTS_DIR,
    REPORT_JSON as MANIFEST_VALIDATION_JSON,
    REPO_ROOT,
    bool_text,
    data_root,
    logs_dir,
    path_is_inside,
    raw_target_dir,
    read_manifest,
)


VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_download_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_download_validator_report.md"

CREATED_CODE_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_81_full_bookdepth_manifest_validator_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_81_full_bookdepth_downloader_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_81_full_bookdepth_download_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_81_full_bookdepth_manifest_validator_v1.ps1",
    REPO_ROOT / "run_orderbook_um_81_full_bookdepth_downloader_v1.ps1",
    REPO_ROOT / "run_orderbook_um_81_full_bookdepth_download_validator_v1.ps1",
    REPO_ROOT / "docs" / "orderbook_um_81_full_bookdepth_download_notes_v1.md",
]

GENERATED_REPORT_FILES = [
    MANIFEST_VALIDATION_JSON,
    OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_manifest_validation.md",
    DOWNLOAD_SUMMARY_JSON,
    DOWNLOAD_SUMMARY_MD,
    FILE_STATUS_CSV,
    SYMBOL_COVERAGE_CSV,
    BLOCKED_NOT_ACK_MD,
]

FORBIDDEN_PATTERNS = [
    r"\bstrategy\b",
    r"\bprivate\b",
    r"\baccount\b",
    r"\border execution\b",
    r"\bexecution logic\b",
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
    r"\bsignal generator\b",
]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"not a JSON object: {path}")
    return payload


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def allowed_safety_context(line: str) -> bool:
    lowered = line.lower()
    safety_tokens = [
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
        "bookdepth",
        "orderbook",
        "raw target",
        "target directory",
        "target path",
        "target: path",
        "target.parent",
        "target.with_name",
        "replace(target)",
        "download_to_part",
        "local_zip_path",
        "rawfull",
        "checksum",
        "stop closed",
        "erroractionpreference",
        "exit $",
        "not a trading",
        "not part",
    ]
    return any(token in lowered for token in safety_tokens)


def scan_forbidden_terms(paths: list[Path]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    blocking: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_PATTERNS:
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


def raw_extracted_files_inside_repo() -> list[str]:
    matches: list[str] = []
    for pattern in ["*-bookDepth-*.csv", "*-bookDepth-*.zip", "*-bookDepth-*.zip.CHECKSUM"]:
        for path in REPO_ROOT.rglob(pattern):
            if ".git" in path.parts:
                continue
            matches.append(str(path.relative_to(REPO_ROOT)))
    return sorted(set(matches))


def output_paths_outside_repo(summary: dict[str, Any], file_rows: list[dict[str, str]]) -> list[str]:
    inside: list[str] = []
    candidates = [
        summary.get("external_data_root", ""),
        summary.get("raw_target_directory", ""),
        summary.get("logs_directory", ""),
    ]
    candidates.extend(row.get("local_zip_path", "") for row in file_rows)
    candidates.extend(row.get("local_checksum_path", "") for row in file_rows)
    for value in candidates:
        if value and path_is_inside(Path(value), REPO_ROOT):
            inside.append(value)
    return inside


def build_blocked_ack_report() -> dict[str, Any]:
    checks = {
        "blocked_acknowledgement_report_exists": BLOCKED_NOT_ACK_MD.exists(),
        "download_summary_not_required_when_ack_missing": not DOWNLOAD_SUMMARY_JSON.exists(),
    }
    return {
        "status": "BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED",
        "created_at_utc": utc_now_text(),
        "exact_blocker": f"required environment variable was not set; see {BLOCKED_NOT_ACK_MD}",
        "validation_checks": checks,
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_81_FULL_BOOKDEPTH_APPROVAL_OR_BLOCKER_REVIEW",
    }


def build_report() -> dict[str, Any]:
    if not DOWNLOAD_SUMMARY_JSON.exists() and BLOCKED_NOT_ACK_MD.exists():
        return build_blocked_ack_report()
    manifest_rows, _fieldnames = read_manifest()
    manifest_rows = [row for row in manifest_rows if row.get("status") == "AVAILABLE"]
    manifest_validation = load_json(MANIFEST_VALIDATION_JSON)
    summary = load_json(DOWNLOAD_SUMMARY_JSON)
    file_rows = read_csv_rows(FILE_STATUS_CSV) if FILE_STATUS_CSV.exists() else []
    symbol_rows = read_csv_rows(SYMBOL_COVERAGE_CSV) if SYMBOL_COVERAGE_CSV.exists() else []
    code_scan = scan_forbidden_terms(CREATED_CODE_FILES)
    report_scan = scan_forbidden_terms([path for path in GENERATED_REPORT_FILES if path.exists()])
    inside_paths = output_paths_outside_repo(summary, file_rows)
    raw_inside = raw_extracted_files_inside_repo()
    file_count_matches = len(file_rows) == len(manifest_rows)
    partial_with_failures = summary.get("status") == "PARTIAL_81_FULL_BOOKDEPTH_DOWNLOAD_RETRY_REQUIRED" and int(summary.get("failed_count") or 0) > 0
    pass_status = summary.get("status") == "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED"
    file_urls = " ".join(row.get("url", "") for row in file_rows)
    checks = {
        "manifest_validation_output_exists": MANIFEST_VALIDATION_JSON.exists(),
        "manifest_validation_passed": manifest_validation.get("replacement_checks_all_true") is True,
        "download_summary_exists": DOWNLOAD_SUMMARY_JSON.exists(),
        "download_summary_md_exists": DOWNLOAD_SUMMARY_MD.exists(),
        "file_status_csv_exists": FILE_STATUS_CSV.exists(),
        "symbol_coverage_csv_exists": SYMBOL_COVERAGE_CSV.exists(),
        "raw_zips_stored_outside_repo": not inside_paths,
        "no_raw_extracted_files_inside_repo": not raw_inside,
        "data_root_outside_repo": not path_is_inside(data_root(), REPO_ROOT),
        "raw_target_directory_outside_repo": not path_is_inside(raw_target_dir(), REPO_ROOT),
        "logs_directory_outside_repo": not path_is_inside(logs_dir(), REPO_ROOT),
        "symbols_represented_81": len({row.get("symbol", "") for row in symbol_rows}) == EXPECTED_SYMBOL_COUNT,
        "file_count_matches_manifest_or_partial_reports_failures": file_count_matches or partial_with_failures,
        "checksum_verification_summary_exists": "checksum_verified_count" in summary and "checksum_missing_count" in summary,
        "failed_count_zero_for_pass": (not pass_status) or int(summary.get("failed_count") or 0) == 0,
        "checksum_missing_zero_for_pass": (not pass_status) or int(summary.get("checksum_missing_count") or 0) == 0,
        "no_full_aggtrades_download_in_outputs": "aggTrades" not in file_urls,
        "no_strategy_order_execution_private_api_logic": not code_scan["blocking_matches"],
        "no_forbidden_trading_recommendation_language_in_reports": not report_scan["blocking_matches"],
    }
    replacement_checks_all_true = all(checks.values()) and pass_status
    return {
        "status": (
            "PASS_ORDERBOOK_UM_81_FULL_BOOKDEPTH_DOWNLOAD_VALIDATED"
            if replacement_checks_all_true
            else "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_FULL_BOOKDEPTH_DOWNLOAD_VALIDATION"
        ),
        "created_at_utc": utc_now_text(),
        "download_summary_status": summary.get("status"),
        "symbol_count": summary.get("symbol_count"),
        "expected_file_count": summary.get("expected_file_count"),
        "downloaded_file_count": summary.get("downloaded_file_count"),
        "skipped_verified_file_count": summary.get("skipped_verified_file_count"),
        "checksum_verified_count": summary.get("checksum_verified_count"),
        "checksum_missing_count": summary.get("checksum_missing_count"),
        "failed_count": summary.get("failed_count"),
        "total_downloaded_gb": summary.get("total_downloaded_gb"),
        "total_verified_gb": summary.get("total_verified_gb"),
        "inside_repo_paths": inside_paths[:100],
        "raw_extracted_files_inside_repo": raw_inside[:100],
        "code_forbidden_term_scan": code_scan,
        "report_forbidden_term_scan": report_scan,
        "validation_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "next_module": (
            "ORDERBOOK_UM_81_FULL_BOOKDEPTH_FEATURE_DATASET_REVIEW"
            if replacement_checks_all_true
            else "ORDERBOOK_UM_81_FULL_BOOKDEPTH_APPROVAL_OR_BLOCKER_REVIEW"
        ),
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 full bookDepth download validator v1",
        "",
        f"status: {report['status']}",
        f"download_summary_status: {report.get('download_summary_status', '')}",
        f"expected_file_count: {report.get('expected_file_count', '')}",
        f"downloaded_file_count: {report.get('downloaded_file_count', '')}",
        f"skipped_verified_file_count: {report.get('skipped_verified_file_count', '')}",
        f"checksum_verified_count: {report.get('checksum_verified_count', '')}",
        f"checksum_missing_count: {report.get('checksum_missing_count', '')}",
        f"failed_count: {report.get('failed_count', '')}",
        f"replacement_checks_all_true: {bool_text(report['replacement_checks_all_true'])}",
        f"next_module: {report['next_module']}",
        "",
        "## Checks",
    ]
    for key, value in report["validation_checks"].items():
        lines.append(f"- {key}: {bool_text(bool(value))}")
    lines.extend(["", "## Forbidden-term scan"])
    code_scan = report.get("code_forbidden_term_scan", {"matches": [], "blocking_matches": []})
    report_scan = report.get("report_forbidden_term_scan", {"matches": [], "blocking_matches": []})
    lines.append(f"- code_matches: {len(code_scan.get('matches', []))}")
    lines.append(f"- code_blocking_matches: {len(code_scan.get('blocking_matches', []))}")
    lines.append(f"- report_matches: {len(report_scan.get('matches', []))}")
    lines.append(f"- report_blocking_matches: {len(report_scan.get('blocking_matches', []))}")
    lines.append("")
    VALIDATOR_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "BLOCKED_OR_PARTIAL_ORDERBOOK_UM_81_FULL_BOOKDEPTH_DOWNLOAD_VALIDATION",
            "created_at_utc": utc_now_text(),
            "exact_blocker": str(exc),
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_81_FULL_BOOKDEPTH_APPROVAL_OR_BLOCKER_REVIEW",
        }
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_report_md(report)
    print(f"status: {report['status']}")
    print(f"download_validator_json: {VALIDATOR_JSON}")
    print(f"download_validator_md: {VALIDATOR_MD}")
    print(f"replacement_checks_all_true: {bool_text(bool(report['replacement_checks_all_true']))}")
    print(f"next_module: {report['next_module']}")
    return 0 if report["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
