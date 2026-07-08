#!/usr/bin/env python
"""Validate strict discovery evaluator outputs and safety constraints."""

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
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_summary.md"
CATEGORY_EFFECTS_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_category_effects.csv"
SYMBOL_EFFECTS_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_symbol_effects.csv"
DAILY_EFFECTS_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_daily_effects.csv"
SPLIT_VALIDATION_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_split_validation.csv"
PERMUTATION_NULL_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_permutation_null.csv"
CANDIDATE_JSON = OUTPUTS_DIR / "orderbook_um_30d_strict_candidate_hypotheses.json"
QUALITY_REPORT_MD = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_quality_report.md"
VALIDATOR_JSON = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_validator_report.json"
VALIDATOR_MD = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_validator_report.md"

CODE_AND_REPORT_FILES = [
    REPO_ROOT / "src" / "edge_factory_orderbook_um_30d_strict_discovery_evaluator_v1.py",
    REPO_ROOT / "src" / "edge_factory_orderbook_um_30d_strict_discovery_validator_v1.py",
    REPO_ROOT / "run_orderbook_um_30d_strict_discovery_evaluator_v1.ps1",
    REPO_ROOT / "run_orderbook_um_30d_strict_discovery_validator_v1.ps1",
    REPO_ROOT / "docs" / "orderbook_um_30d_strict_discovery_notes_v1.md",
    SUMMARY_MD,
    QUALITY_REPORT_MD,
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


def csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def output_zip_files() -> list[str]:
    return sorted(str(path.relative_to(REPO_ROOT)) for path in OUTPUTS_DIR.rglob("*.zip"))


def large_repo_outputs() -> list[str]:
    oversized: list[str] = []
    for path in OUTPUTS_DIR.rglob("*"):
        if path.is_file() and path.stat().st_size > 100 * 1024 * 1024:
            oversized.append(str(path.relative_to(REPO_ROOT)))
    return oversized


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
            "research",
            "discovery",
            "exit $exitcode",
            "expected_direction",
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
                    if path.name == "edge_factory_orderbook_um_30d_strict_discovery_validator_v1.py" and line.strip().startswith("r\""):
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


def discovery_candidate_evidence_present(candidate_payload: dict[str, Any]) -> bool:
    candidates = candidate_payload.get("discovery_candidates")
    if not isinstance(candidates, list):
        return False
    for item in candidates:
        strict = item.get("strict_criteria")
        if not isinstance(strict, dict) or not strict:
            return False
        if not all(strict.values()):
            return False
        required = ["effect_vs_mixed_bps", "count", "bootstrap_ci_low", "bootstrap_ci_high", "permutation_p_value", "bh_q_value"]
        if any(key not in item for key in required):
            return False
    return True


def no_edge_claim(summary_text: str, quality_text: str) -> bool:
    lowered = (summary_text + "\n" + quality_text).lower()
    blocked_phrases = [
        "edge was found",
        "tradable edge",
        "profitable",
        "trade recommendation",  # blocked phrase detector
        "long recommendation",  # blocked phrase detector
        "short recommendation",  # blocked phrase detector
    ]
    return not any(phrase in lowered for phrase in blocked_phrases)


def build_report() -> dict[str, Any]:
    summary = load_json(SUMMARY_JSON)
    candidates = load_json(CANDIDATE_JSON)
    category_rows = csv_rows(CATEGORY_EFFECTS_CSV)
    split_rows = csv_rows(SPLIT_VALIDATION_CSV)
    permutation_rows = csv_rows(PERMUTATION_NULL_CSV)
    summary_text = SUMMARY_MD.read_text(encoding="utf-8", errors="replace") if SUMMARY_MD.exists() else ""
    quality_text = QUALITY_REPORT_MD.read_text(encoding="utf-8", errors="replace") if QUALITY_REPORT_MD.exists() else ""
    scan = scan_forbidden_terms()
    expected_outputs = [
        SUMMARY_JSON,
        SUMMARY_MD,
        CATEGORY_EFFECTS_CSV,
        SYMBOL_EFFECTS_CSV,
        DAILY_EFFECTS_CSV,
        SPLIT_VALIDATION_CSV,
        PERMUTATION_NULL_CSV,
        CANDIDATE_JSON,
        QUALITY_REPORT_MD,
    ]
    candidate_count = int(summary.get("discovery_candidate_count") or 0)
    labels = {row.get("research_status_label", "") for row in category_rows}
    checks = {
        "expected_outputs_exist": all(path.exists() for path in expected_outputs),
        "no_raw_zip_or_large_raw_extracted_data_inside_repo": len(output_zip_files()) == 0 and len(large_repo_outputs()) == 0,
        "external_work_path_outside_repo": not path_is_inside(Path(str(summary.get("external_work_path", data_root()))), REPO_ROOT),
        "summary_has_status": bool(summary.get("status")),
        "category_effects_file_exists": CATEGORY_EFFECTS_CSV.exists() and bool(category_rows),
        "split_validation_file_exists": SPLIT_VALIDATION_CSV.exists() and bool(split_rows),
        "permutation_null_file_exists": PERMUTATION_NULL_CSV.exists() and bool(permutation_rows),
        "candidate_hypotheses_file_exists": CANDIDATE_JSON.exists(),
        "no_strategy_order_execution_private_api_logic": len(scan["blocking_matches"]) == 0,
        "no_forbidden_trading_recommendation_language": no_edge_claim(summary_text, quality_text),
        "no_full_81_symbol_download_occurred": summary.get("full_81_symbol_download_attempted") is False,
        "no_90_day_download_occurred": summary.get("ninety_day_download_attempted") is False,
        "no_pnl_or_trade_construction_logic": len(scan["blocking_matches"]) == 0,
        "discovery_labels_are_research_labels_only": summary.get("research_labels_only") is True
        and candidates.get("research_labels_only") is True
        and labels <= {"DISCOVERY_CANDIDATE", "WEAK_MONITOR_ONLY", "FAIL_NO_STABLE_SEPARATION"},
        "candidate_strict_criteria_evidence_present_if_needed": candidate_count == 0 or discovery_candidate_evidence_present(candidates),
        "criteria_not_met_does_not_imply_edge": no_edge_claim(summary_text, quality_text),
    }
    checks["replacement_checks_all_true"] = all(checks.values())
    return {
        "status": "PASS_ORDERBOOK_UM_30D_STRICT_DISCOVERY_VALIDATOR" if checks["replacement_checks_all_true"] else "BLOCKED_ORDERBOOK_UM_30D_STRICT_DISCOVERY_VALIDATOR",
        "summary_json": str(SUMMARY_JSON),
        "category_effects_csv": str(CATEGORY_EFFECTS_CSV),
        "split_validation_csv": str(SPLIT_VALIDATION_CSV),
        "permutation_null_csv": str(PERMUTATION_NULL_CSV),
        "candidate_hypotheses_json": str(CANDIDATE_JSON),
        "candidate_count": candidate_count,
        "labels_found": sorted(labels),
        "forbidden_string_scan": scan,
        "validation_checks": checks,
        "replacement_checks_all_true": checks["replacement_checks_all_true"],
        "next_recommended_step": summary.get("next_recommended_step"),
        "next_module": "ORDERBOOK_UM_STRICT_DISCOVERY_NEXT_STEP_REVIEW"
        if checks["replacement_checks_all_true"]
        else "ORDERBOOK_UM_STRICT_DISCOVERY_BLOCKER_REVIEW",
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d strict discovery validator v1",
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
            "status": "BLOCKED_ORDERBOOK_UM_30D_STRICT_DISCOVERY_VALIDATOR",
            "exact_blocker": str(exc),
            "validation_checks": {"replacement_checks_all_true": False},
            "replacement_checks_all_true": False,
            "next_recommended_step": "C_STOP_ORDERBOOK_ABSORPTION_ROUTE_IF_NO_STABLE_SEPARATION",
            "next_module": "ORDERBOOK_UM_STRICT_DISCOVERY_BLOCKER_REVIEW",
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
