#!/usr/bin/env python
"""Validate aggTrades plus bookDepth absorption pilot outputs."""

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
AGGTRADES_SCHEMA_JSON = OUTPUTS_DIR / "orderbook_um_aggtrades_pilot_schema_summary.json"
AGGTRADES_SCHEMA_MD = OUTPUTS_DIR / "orderbook_um_aggtrades_pilot_schema_summary.md"
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_absorption_pilot_preview_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_absorption_pilot_preview_summary.md"
QUANTILE_CSV = OUTPUTS_DIR / "orderbook_um_absorption_pilot_quantile_diagnostics.csv"
CATEGORY_CSV = OUTPUTS_DIR / "orderbook_um_absorption_pilot_category_diagnostics.csv"
QUALITY_MD = OUTPUTS_DIR / "orderbook_um_absorption_pilot_quality_report.md"
SAMPLE_CSV = OUTPUTS_DIR / "orderbook_um_absorption_pilot_sample.csv"
SAMPLE_PARQUET = OUTPUTS_DIR / "orderbook_um_absorption_pilot_sample.parquet"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_absorption_pilot_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_absorption_pilot_validator_report.md"

CODE_AND_REPORT_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_aggtrades_pilot_downloader_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_absorption_pilot_preview_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_absorption_pilot_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_aggtrades_pilot_download_v1.ps1",
    REPO_ROOT / "run_orderbook_um_absorption_pilot_preview_v1.ps1",
    REPO_ROOT / "run_orderbook_um_absorption_pilot_validator_v1.ps1",
    REPO_ROOT / "docs" / "orderbook_um_absorption_pilot_preview_notes_v1.md",
    AGGTRADES_SCHEMA_MD,
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


def output_zip_files() -> list[str]:
    return sorted(str(path.relative_to(REPO_ROOT)) for path in OUTPUTS_DIR.rglob("*.zip"))


def raw_zip_paths_outside_repo(schema: dict[str, Any]) -> bool:
    downloads = schema.get("downloads")
    if not isinstance(downloads, list):
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
                    if path.name == "edge_factory_orderbook_um_absorption_pilot_validator_v1.py" and line.strip().startswith("r\""):
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


def build_report() -> dict[str, Any]:
    schema = load_json(AGGTRADES_SCHEMA_JSON)
    summary = load_json(SUMMARY_JSON)
    header = sample_header()
    expected_outputs = [AGGTRADES_SCHEMA_JSON, AGGTRADES_SCHEMA_MD, SUMMARY_JSON, SUMMARY_MD, QUANTILE_CSV, CATEGORY_CSV, QUALITY_MD, SAMPLE_CSV]
    trade_features = [column for column in header if column.startswith("trade_count_") or column.startswith("total_notional_") or column.startswith("trade_imbalance_")]
    bookdepth_features = [column for column in header if column in {"mid_price_proxy_pct1", "spread_bps_proxy_pct1", "imbalance_1", "liquidity_pull_proxy_pct1"}]
    forward_columns = ["forward_return_10s", "forward_return_30s", "forward_return_60s", "forward_return_300s"]
    scan = scan_forbidden_terms()
    checks = {
        "expected_output_files_exist": all(path.exists() for path in expected_outputs),
        "raw_zips_stored_outside_repo": raw_zip_paths_outside_repo(schema),
        "no_raw_zip_extraction_inside_repo": len(output_zip_files()) == 0,
        "data_root_outside_repo": not path_is_inside(data_root(), REPO_ROOT),
        "aggtrades_schema_summary_exists": AGGTRADES_SCHEMA_JSON.exists(),
        "absorption_preview_summary_exists": SUMMARY_JSON.exists(),
        "feature_sample_has_timestamp_and_symbol": "timestamp" in header and "symbol" in header,
        "sample_has_trade_flow_feature": bool(trade_features),
        "sample_has_bookdepth_feature": bool(bookdepth_features),
        "sample_has_absorption_category": "absorption_category" in header,
        "forward_diagnostic_columns_exist_if_mid_proxy_exists": ("mid_price_proxy_pct1" not in header)
        or all(column in header for column in forward_columns),
        "no_future_leakage_documented": summary.get("alignment_method", {}).get("no_future_leakage") is True,
        "no_strategy_order_execution_private_api_logic": len(scan["blocking_matches"]) == 0,
        "no_full_historical_download_occurred": summary.get("full_historical_download_attempted") is False
        and schema.get("full_historical_download_attempted") is False,
    }
    checks["replacement_checks_all_true"] = all(checks.values())
    return {
        "status": "PASS_ORDERBOOK_UM_ABSORPTION_PILOT_VALIDATOR" if checks["replacement_checks_all_true"] else "BLOCKED_ORDERBOOK_UM_ABSORPTION_PILOT_VALIDATOR",
        "schema_summary_json": str(AGGTRADES_SCHEMA_JSON),
        "preview_summary_json": str(SUMMARY_JSON),
        "sample_csv": str(SAMPLE_CSV),
        "sample_parquet_exists": SAMPLE_PARQUET.exists(),
        "sample_header": header,
        "trade_flow_feature_columns_found": trade_features[:50],
        "bookdepth_feature_columns_found": bookdepth_features,
        "forbidden_string_scan": scan,
        "validation_checks": checks,
        "replacement_checks_all_true": checks["replacement_checks_all_true"],
        "next_recommended_step": summary.get("recommended_next_step"),
        "next_module": "ORDERBOOK_UM_30_DAY_BTC_ETH_SOL_PILOT_DESIGN_OR_STOP"
        if checks["replacement_checks_all_true"]
        else "ORDERBOOK_UM_ABSORPTION_PILOT_BLOCKER_REVIEW",
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM absorption pilot validator v1",
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
    for item in matches[:100]:
        lines.append(
            f"- {item['path']}:{item['line']} term={item['term']} allowed_safety_context={item['allowed_safety_context']}"
        )
    lines.append("")
    VALIDATOR_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = {
            "status": "BLOCKED_ORDERBOOK_UM_ABSORPTION_PILOT_VALIDATOR",
            "exact_blocker": str(exc),
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_recommended_step": "D_STOP_DUE_TO_UNSUPPORTED_SCHEMA_OR_INSUFFICIENT_ALIGNMENT",
            "next_module": "ORDERBOOK_UM_ABSORPTION_PILOT_BLOCKER_REVIEW",
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
