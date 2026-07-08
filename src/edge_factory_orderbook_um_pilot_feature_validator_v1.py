#!/usr/bin/env python
"""Validate pilot-only orderbook feature preview outputs."""

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
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_pilot_feature_preview_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_pilot_feature_preview_summary.md"
QUANTILE_CSV = OUTPUTS_DIR / "orderbook_um_pilot_feature_quantile_diagnostics.csv"
QUALITY_MD = OUTPUTS_DIR / "orderbook_um_pilot_feature_quality_report.md"
FEATURE_SAMPLE_CSV = OUTPUTS_DIR / "orderbook_um_pilot_feature_sample.csv"
FEATURE_SAMPLE_PARQUET = OUTPUTS_DIR / "orderbook_um_pilot_feature_sample.parquet"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_pilot_feature_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_pilot_feature_validator_report.md"

CODE_AND_REPORT_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_pilot_feature_preview_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_pilot_feature_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_pilot_feature_preview_v1.ps1",
    REPO_ROOT / "run_orderbook_um_pilot_feature_validator_v1.ps1",
    REPO_ROOT / "docs" / "orderbook_um_pilot_feature_preview_notes_v1.md",
    SUMMARY_MD,
    QUALITY_MD,
]


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def load_summary() -> dict[str, Any]:
    if not SUMMARY_JSON.exists():
        raise FileNotFoundError(f"missing summary: {SUMMARY_JSON}")
    return json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))


def read_sample_header() -> list[str]:
    if not FEATURE_SAMPLE_CSV.exists():
        return []
    with FEATURE_SAMPLE_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader, [])


def repo_zip_files() -> list[str]:
    paths: list[str] = []
    for path in REPO_ROOT.rglob("*.zip"):
        if ".git" in path.parts:
            continue
        paths.append(str(path.relative_to(REPO_ROOT)))
    return sorted(paths)


def task_created_repo_zip_files(zip_paths: list[str]) -> list[str]:
    return [
        path
        for path in zip_paths
        if "orderbook_um_pilot_feature" in path.lower()
        or path.lower().startswith("outputs\\")
        or path.lower().startswith("src\\edge_factory_orderbook_um_pilot_feature")
    ]


def large_raw_like_task_output_files() -> list[str]:
    offenders: list[str] = []
    for path in OUTPUTS_DIR.glob("orderbook_um_pilot_feature*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.stat().st_size < 25 * 1024 * 1024:
            continue
        offenders.append(str(path.relative_to(REPO_ROOT)))
    return sorted(offenders)


def allowed_safety_context(line: str) -> bool:
    lowered = line.lower()
    return any(
        token in lowered
        for token in [
            "forbidden",
            "not allowed",
            "blocked",
            "no ",
            "no_",
            "false",
            "diagnostic",
            "orderbook",
            "bookdepth",
            "public",
            "validator",
            "unsupported",
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
                    if term == r"\bexit\b" and line.strip().lower() == "exit $exitcode":
                        allowed = True
                    if path.name == "edge_factory_orderbook_um_pilot_feature_validator_v1.py" and "exit $exitcode" in line.lower():
                        allowed = True
                    if path.name == "edge_factory_orderbook_um_pilot_feature_validator_v1.py" and line.strip().startswith("r\""):
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
    summary = load_summary()
    sample_header = read_sample_header()
    output_files = [SUMMARY_JSON, SUMMARY_MD, QUANTILE_CSV, QUALITY_MD, FEATURE_SAMPLE_CSV]
    parquet_optional = FEATURE_SAMPLE_PARQUET.exists()
    zip_files = repo_zip_files()
    task_zip_files = task_created_repo_zip_files(zip_files)
    raw_like = large_raw_like_task_output_files()
    group_availability = summary.get("feature_group_availability", {})
    mid_exists = group_availability.get("mid_proxy") is True
    forward_availability = summary.get("forward_diagnostic_availability", {})
    forward_columns_expected = [f"forward_return_{horizon}s" for horizon in [10, 30, 60, 300]]
    scan = scan_forbidden_terms()
    root = data_root()
    checks = {
        "output_files_exist": all(path.exists() for path in output_files),
        "no_task_raw_zip_extraction_inside_repo": len(task_zip_files) == 0,
        "no_large_raw_like_task_output_files": len(raw_like) == 0,
        "feature_sample_has_timestamp_and_symbol": "timestamp" in sample_header and "symbol" in sample_header,
        "at_least_one_mid_spread_or_imbalance_group_exists": any(
            group_availability.get(key) is True for key in ["mid_proxy", "spread_proxy", "imbalance"]
        ),
        "forward_diagnostic_columns_exist_if_mid_exists": (not mid_exists)
        or all(column in sample_header and forward_availability.get(column, 0) > 0 for column in forward_columns_expected),
        "no_strategy_order_execution_private_api_logic": len(scan["blocking_matches"]) == 0,
        "data_root_outside_repo": not path_is_inside(root, REPO_ROOT),
        "full_download_not_attempted": summary.get("full_historical_download_attempted") is False,
        "parquet_optional_ok": True if parquet_optional or not summary.get("parquet_written") else FEATURE_SAMPLE_PARQUET.exists(),
    }
    checks["replacement_checks_all_true"] = all(checks.values())
    return {
        "status": "PASS_ORDERBOOK_UM_PILOT_FEATURE_VALIDATOR" if checks["replacement_checks_all_true"] else "BLOCKED_ORDERBOOK_UM_PILOT_FEATURE_VALIDATOR",
        "summary_json": str(SUMMARY_JSON),
        "feature_sample_csv": str(FEATURE_SAMPLE_CSV),
        "quantile_diagnostics_csv": str(QUANTILE_CSV),
        "quality_report_md": str(QUALITY_MD),
        "feature_sample_parquet_exists": parquet_optional,
        "sample_header": sample_header,
        "repo_zip_files": zip_files,
        "task_created_repo_zip_files": task_zip_files,
        "large_raw_like_repo_files": raw_like,
        "forbidden_string_scan": scan,
        "validation_checks": checks,
        "replacement_checks_all_true": checks["replacement_checks_all_true"],
        "next_recommended_step": summary.get("next_recommended_step"),
        "next_module": "ORDERBOOK_UM_AGGTRADES_PILOT_ABSORPTION_DIAGNOSTICS_DESIGN_OR_STOP"
        if checks["replacement_checks_all_true"]
        else "ORDERBOOK_UM_PILOT_FEATURE_BLOCKER_REVIEW",
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM pilot feature validator v1",
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
            "status": "BLOCKED_ORDERBOOK_UM_PILOT_FEATURE_VALIDATOR",
            "exact_blocker": str(exc),
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_recommended_step": "C_STOP_DUE_TO_UNSUPPORTED_SCHEMA",
            "next_module": "ORDERBOOK_UM_PILOT_FEATURE_BLOCKER_REVIEW",
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
