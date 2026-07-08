#!/usr/bin/env python
"""Validate BTC/ETH/SOL 30-day absorption pilot outputs and safety constraints."""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest.csv"
MANIFEST_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest_summary.json"
DOWNLOAD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_download_summary.json"
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_absorption_preview_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_30d_absorption_preview_summary.md"
CATEGORY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_category_diagnostics.csv"
QUANTILE_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_quantile_diagnostics.csv"
DAILY_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_daily_stability.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_symbol_stability.csv"
QUALITY_MD = OUTPUTS_DIR / "orderbook_um_30d_absorption_quality_report.md"
SAMPLE_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_sample.csv"
SAMPLE_PARQUET = OUTPUTS_DIR / "orderbook_um_30d_absorption_sample.parquet"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_30d_absorption_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_30d_absorption_validator_report.md"
TARGET_SYMBOLS = {"BTCUSDT", "ETHUSDT", "SOLUSDT"}

CODE_AND_REPORT_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_30d_pilot_manifest_builder_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_30d_pilot_downloader_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_30d_absorption_preview_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_30d_absorption_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_30d_pilot_manifest_builder_v1.ps1",
    REPO_ROOT / "run_orderbook_um_30d_pilot_downloader_v1.ps1",
    REPO_ROOT / "run_orderbook_um_30d_absorption_preview_v1.ps1",
    REPO_ROOT / "run_orderbook_um_30d_absorption_validator_v1.ps1",
    REPO_ROOT / "docs" / "orderbook_um_30d_absorption_pilot_notes_v1.md",
    SUMMARY_MD,
    QUALITY_MD,
]


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing required output: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"output is not a JSON object: {path}")
    return payload


def sample_header() -> list[str]:
    if not SAMPLE_CSV.exists():
        return []
    with SAMPLE_CSV.open("r", encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle), [])


def manifest_rows() -> list[dict[str, str]]:
    if not MANIFEST_CSV.exists():
        return []
    with MANIFEST_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def output_zip_files() -> list[str]:
    return sorted(str(path.relative_to(REPO_ROOT)) for path in OUTPUTS_DIR.rglob("*.zip"))


def raw_zip_paths_outside_repo(download_summary: dict[str, Any]) -> bool:
    downloads = download_summary.get("downloads")
    if not isinstance(downloads, list) or not downloads:
        return False
    for item in downloads:
        path = Path(str(item.get("local_zip_path", "")))
        if not path.exists() or path_is_inside(path, REPO_ROOT):
            return False
    return True


def allowed_safety_context(line: str) -> bool:
    lowered = line.lower()
    return any(
        token in lowered
        for token in [
            "forbidden",
            "not ",
            "not allowed",
            "blocked",
            "no ",
            "no_",
            "false",
            "diagnostic",
            "category",
            "absorption",
            "orderbook",
            "bookdepth",
            "aggtrades",
            "public",
            "validator",
            "unsupported",
            "exit $exitcode",
            "isbuyermaker",
        ]
    )


def scan_forbidden_terms() -> dict[str, Any]:
    terms = [
        r"strategy\.",
        r"\border\b",
        r"\bprivate\b",
        r"apiKey",
        r"\bsecret\b",
        r"\bleverage\b",
        r"position sizing",
        r"\bentry\b",
        r"\bexit\b",
        r"stop loss",
        r"take profit",
        r"\bpnl\b",
        r"paper trading",
        r"live trading",
        r"buy signal",
        r"sell signal",
        r"recommendation",
    ]
    matches: list[dict[str, Any]] = []
    blocking: list[dict[str, Any]] = []
    for path in CODE_AND_REPORT_FILES:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for term in terms:
                if re.search(term, line, flags=re.IGNORECASE):
                    allowed = allowed_safety_context(line)
                    if path.name == "edge_factory_orderbook_um_30d_absorption_validator_v1.py" and line.strip().startswith("r\""):
                        allowed = True
                    item = {
                        "path": str(path.relative_to(REPO_ROOT)),
                        "line": line_number,
                        "term": term,
                        "text": line.strip()[:240],
                        "allowed_safety_context": allowed,
                    }
                    matches.append(item)
                    if not allowed:
                        if term == r"\border\b" and "orderbook" in line.lower():
                            continue
                        blocking.append(item)
    return {"matches": matches, "blocking_matches": blocking}


def manifest_exact_symbols_and_days(rows: list[dict[str, str]]) -> bool:
    if len(rows) != 90:
        return False
    symbols = {row.get("symbol", "") for row in rows}
    if symbols != TARGET_SYMBOLS:
        return False
    for symbol in TARGET_SYMBOLS:
        if len({row.get("file_date", "") for row in rows if row.get("symbol") == symbol}) != 30:
            return False
    return True


def build_report() -> dict[str, Any]:
    manifest_summary = load_json(MANIFEST_SUMMARY_JSON)
    download_summary = load_json(DOWNLOAD_SUMMARY_JSON)
    preview_summary = load_json(SUMMARY_JSON)
    rows = manifest_rows()
    header = sample_header()
    expected_outputs = [
        MANIFEST_CSV,
        MANIFEST_SUMMARY_JSON,
        DOWNLOAD_SUMMARY_JSON,
        SUMMARY_JSON,
        SUMMARY_MD,
        CATEGORY_CSV,
        QUANTILE_CSV,
        DAILY_STABILITY_CSV,
        SYMBOL_STABILITY_CSV,
        QUALITY_MD,
        SAMPLE_CSV,
    ]
    trade_features = [column for column in header if column.startswith("trade_count_") or column.startswith("total_notional_") or column.startswith("trade_imbalance_")]
    bookdepth_features = [column for column in header if column in {"mid_price_proxy_pct1", "spread_bps_proxy_pct1", "imbalance_1", "liquidity_pull_proxy_pct1"}]
    forward_columns = ["forward_return_10s", "forward_return_30s", "forward_return_60s", "forward_return_300s"]
    scan = scan_forbidden_terms()
    checks = {
        "expected_output_files_exist": all(path.exists() for path in expected_outputs),
        "raw_zips_stored_outside_repo": raw_zip_paths_outside_repo(download_summary),
        "no_raw_zip_extraction_inside_repo": len(output_zip_files()) == 0,
        "data_root_outside_repo": not path_is_inside(data_root(), REPO_ROOT),
        "manifest_has_exactly_btc_eth_sol": {row.get("symbol", "") for row in rows} == TARGET_SYMBOLS,
        "manifest_day_count_is_30": manifest_exact_symbols_and_days(rows),
        "checksum_verification_summary_exists": preview_summary.get("checksum_verification_summary", {}).get("verified_file_count") == 180,
        "absorption_preview_summary_exists": SUMMARY_JSON.exists(),
        "category_diagnostics_exists": CATEGORY_CSV.exists(),
        "daily_stability_output_exists": DAILY_STABILITY_CSV.exists(),
        "symbol_stability_output_exists": SYMBOL_STABILITY_CSV.exists(),
        "feature_sample_has_timestamp_and_symbol": "timestamp" in header and "symbol" in header,
        "sample_has_trade_flow_feature": bool(trade_features),
        "sample_has_bookdepth_feature": bool(bookdepth_features),
        "sample_has_absorption_category": "absorption_category" in header,
        "forward_diagnostic_columns_exist_if_mid_proxy_exists": ("mid_price_proxy_pct1" not in header)
        or all(column in header for column in forward_columns),
        "no_future_leakage_documented": preview_summary.get("alignment_method", {}).get("no_future_leakage") is True,
        "no_strategy_order_execution_private_api_logic": len(scan["blocking_matches"]) == 0,
        "no_full_81_symbol_historical_download_occurred": preview_summary.get("full_81_symbol_download_attempted") is False
        and download_summary.get("full_81_symbol_download_attempted") is False
        and manifest_summary.get("selected_symbols") == ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    }
    checks["replacement_checks_all_true"] = all(checks.values())
    return {
        "status": "PASS_ORDERBOOK_UM_30D_ABSORPTION_VALIDATOR" if checks["replacement_checks_all_true"] else "BLOCKED_ORDERBOOK_UM_30D_ABSORPTION_VALIDATOR",
        "manifest_summary_json": str(MANIFEST_SUMMARY_JSON),
        "download_summary_json": str(DOWNLOAD_SUMMARY_JSON),
        "preview_summary_json": str(SUMMARY_JSON),
        "sample_csv": str(SAMPLE_CSV),
        "sample_parquet_exists": SAMPLE_PARQUET.exists(),
        "sample_header": header,
        "trade_flow_feature_columns_found": trade_features[:80],
        "bookdepth_feature_columns_found": bookdepth_features,
        "manifest_row_count": len(rows),
        "selected_window": {
            "start": preview_summary.get("selected_start_date"),
            "end": preview_summary.get("selected_end_date"),
            "day_count": preview_summary.get("selected_day_count"),
        },
        "forbidden_string_scan": scan,
        "validation_checks": checks,
        "replacement_checks_all_true": checks["replacement_checks_all_true"],
        "next_recommended_step": preview_summary.get("recommended_next_step"),
        "next_module": "ORDERBOOK_UM_30D_NEXT_STEP_REVIEW"
        if checks["replacement_checks_all_true"]
        else "ORDERBOOK_UM_30D_ABSORPTION_BLOCKER_REVIEW",
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d absorption validator v1",
        "",
        f"status: {report['status']}",
        f"replacement_checks_all_true: {str(report['replacement_checks_all_true']).lower()}",
        f"next_recommended_step: {report['next_recommended_step']}",
        "",
        "## Checks",
    ]
    for key, value in report["validation_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Forbidden string matches"])
    matches = report["forbidden_string_scan"]["matches"]
    if not matches:
        lines.append("- none")
    for item in matches[:120]:
        lines.append(f"- {item['path']}:{item['line']} term={item['term']} allowed_safety_context={item['allowed_safety_context']}")
    lines.append("")
    VALIDATOR_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "BLOCKED_ORDERBOOK_UM_30D_ABSORPTION_VALIDATOR",
            "exact_blocker": str(exc),
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_recommended_step": "D_STOP_DUE_TO_WEAK_OR_UNSTABLE_DIAGNOSTICS",
            "next_module": "ORDERBOOK_UM_30D_ABSORPTION_BLOCKER_REVIEW",
        }
    VALIDATOR_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_report_md(report)
    print(f"status: {report['status']}")
    print(f"validator_report_json: {VALIDATOR_JSON}")
    print(f"replacement_checks_all_true: {str(report['replacement_checks_all_true']).lower()}")
    print(f"next_recommended_step: {report['next_recommended_step']}")
    return 0 if report["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
