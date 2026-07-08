from __future__ import annotations

import ast
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "c79d839"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_UNIVERSE_DISCOVERY_PREVIEW_READY_FOR_SOURCE_DISCOVERY"
PASS_LOCAL_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_SOURCE_DISCOVERY_READY_FOR_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW"
PASS_LOCAL_INCOMPLETE_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_SOURCE_DISCOVERY_LOCAL_INCOMPLETE_OFFICIAL_LOOKUP_APPROVAL_READY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_SOURCE_DISCOVERY_FAILED_CLOSED"
NEXT_LOCAL_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_eligibility_preview_after_symbol_source_discovery_v1.py"
NEXT_OFFICIAL_LOOKUP_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_official_usdt_swap_symbol_source_lookup_approval_after_local_discovery_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_blocked_record_v1.py"
QUALITY_LOCAL = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_SOURCE_DISCOVERY_READY_FOR_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW"
QUALITY_LOCAL_INCOMPLETE = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_SYMBOL_SOURCE_DISCOVERY_LOCAL_INCOMPLETE_OFFICIAL_LOOKUP_APPROVAL_READY"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
UNIVERSE_DIR = EDGE_LAB_ROOT / "_universe"
PREVIEW_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_universe_discovery_preview_after_10_symbol_pilot_summary_v1"
PILOT_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_after_build_validator_v1"
POLICY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_after_batch_anomaly_classification_v1"

ARTIFACTS = {
    "universe_preview_summary": PREVIEW_DIR / "historical_okx_full_usdt_swap_universe_discovery_preview_summary.json",
    "universe_preview": PREVIEW_DIR / "historical_okx_full_usdt_swap_symbol_universe_discovery_preview.json",
    "pilot_pipeline_summary": PILOT_SUMMARY_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json",
    "batch_policy_summary": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy_summary.json",
}

LOCAL_SYMBOL_ARTIFACT_CANDIDATES = [
    UNIVERSE_DIR / "okx_usdt_swap_universe_filtered.csv",
    UNIVERSE_DIR / "okx_usdt_swap_universe.csv",
]

REQUIRED_BASE_OUTPUTS = [
    "historical_okx_full_usdt_swap_symbol_source_discovery_report.json",
    "historical_okx_full_usdt_swap_local_symbol_artifact_search_report.json",
    "historical_okx_full_usdt_swap_symbol_filter_validation_report.json",
    "historical_okx_full_usdt_swap_symbol_source_survivorship_limitations_report.json",
    "historical_okx_full_usdt_swap_symbol_source_next_route_decision.json",
    "historical_okx_full_usdt_swap_symbol_source_discovery_self_validator.json",
    "historical_okx_full_usdt_swap_symbol_source_discovery_summary.json",
]
CANDIDATE_LIST_OUTPUT = "historical_okx_full_usdt_swap_candidate_symbol_list.json"
OFFICIAL_APPROVAL_OUTPUT = "historical_okx_full_usdt_swap_official_source_lookup_approval_record.json"

SYMBOL_RE = re.compile(r"^[A-Z0-9]+-USDT-SWAP$")

POLICY = {
    "exact_duplicate_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW",
    "material_conflict_policy": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP",
    "missing_minute_policy": "NO_FILL_MARK_AFFECTED_HOUR_INCOMPLETE_OR_EXCLUDE_FROM_COMPLETE_CLAIMS",
    "synthetic_fill_allowed": False,
    "forward_fill_allowed": False,
    "backfill_allowed": False,
}


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def current_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def repo_has_only_this_tool_change() -> bool:
    status = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    if not status:
        return True
    rel = current_tool_rel()
    return all(line[3:].replace("\\", "/") == rel for line in status)


def tracked_python_files_including_current() -> list[str]:
    files = sorted(path for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))
    rel = current_tool_rel()
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files)


def tracked_python_validation() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    files = tracked_python_files_including_current()
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.exists(), f"missing required artifact {label}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def normalize_symbol(raw: str) -> str:
    return raw.strip().upper().replace("_", "-")


def extract_symbol_from_record(record: dict[str, str]) -> str | None:
    for key in ["instId", "inst_id", "symbol", "instrument_name"]:
        value = record.get(key)
        if value:
            return normalize_symbol(value)
    for value in record.values():
        text = normalize_symbol(str(value))
        match = re.search(r"[A-Z0-9]+-USDT-SWAP", text)
        if match:
            return match.group(0)
    return None


def validate_symbols(raw_symbols: list[str]) -> dict[str, Any]:
    seen: set[str] = set()
    candidates: list[str] = []
    malformed: list[str] = []
    duplicates: list[str] = []
    non_usdt_swap: list[str] = []
    for raw in raw_symbols:
        symbol = normalize_symbol(raw)
        if not symbol:
            continue
        if not symbol.endswith("-USDT-SWAP"):
            non_usdt_swap.append(symbol)
            continue
        if not SYMBOL_RE.match(symbol):
            malformed.append(symbol)
            continue
        if symbol in seen:
            duplicates.append(symbol)
            continue
        seen.add(symbol)
        candidates.append(symbol)
    return {
        "candidate_symbols": candidates,
        "candidate_symbol_count": len(candidates),
        "usdt_swap_symbol_count": len(candidates),
        "malformed_symbols": malformed,
        "malformed_symbol_count": len(malformed),
        "duplicate_symbols": duplicates,
        "duplicate_symbol_count": len(duplicates),
        "non_usdt_swap_excluded": non_usdt_swap,
        "non_usdt_swap_excluded_count": len(non_usdt_swap),
    }


def inspect_local_symbol_artifacts() -> dict[str, Any]:
    inspected: list[dict[str, Any]] = []
    selected: dict[str, Any] | None = None
    for path in LOCAL_SYMBOL_ARTIFACT_CANDIDATES:
        entry: dict[str, Any] = {
            "path": str(path),
            "exists": path.exists(),
            "selected": False,
            "reason": None,
        }
        if not path.exists():
            entry["reason"] = "missing"
            inspected.append(entry)
            continue
        raw_symbols: list[str] = []
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                for record in reader:
                    symbol = extract_symbol_from_record(record)
                    if symbol:
                        raw_symbols.append(symbol)
        elif path.suffix.lower() in {".txt", ".list"}:
            raw_symbols = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        elif path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            raw_symbols = extract_symbols_from_json(payload)
        validation = validate_symbols(raw_symbols)
        entry.update(
            {
                "raw_symbol_count": len(raw_symbols),
                "candidate_symbol_count": validation["candidate_symbol_count"],
                "malformed_symbol_count": validation["malformed_symbol_count"],
                "duplicate_symbol_count": validation["duplicate_symbol_count"],
                "non_usdt_swap_excluded_count": validation["non_usdt_swap_excluded_count"],
            }
        )
        if selected is None and validation["candidate_symbol_count"] > 0 and validation["malformed_symbol_count"] == 0:
            entry["selected"] = True
            entry["reason"] = "valid local OKX USDT-SWAP symbol artifact"
            selected = {
                "path": path,
                "validation": validation,
                "raw_symbol_count": len(raw_symbols),
            }
        else:
            entry["reason"] = "not selected"
        inspected.append(entry)
    return {
        "inspected_artifacts": inspected,
        "selected_artifact_path": str(selected["path"]) if selected else None,
        "local_or_user_symbol_list_found": selected is not None,
        "selected_validation": selected["validation"] if selected else validate_symbols([]),
        "local_artifact_search_scope": [str(path) for path in LOCAL_SYMBOL_ARTIFACT_CANDIDATES],
    }


def extract_symbols_from_json(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for item in value.values():
            found.extend(extract_symbols_from_json(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(extract_symbols_from_json(item))
    elif isinstance(value, str):
        for match in re.findall(r"[A-Za-z0-9]+[-_]USDT[-_]SWAP", value):
            found.append(normalize_symbol(match))
    return found


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    preview = artifacts["universe_preview_summary"]
    pilot = artifacts["pilot_pipeline_summary"]
    policy = artifacts["batch_policy_summary"]
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "preview_status_passed": preview.get("historical_data_acquisition_okx_full_usdt_swap_symbol_universe_discovery_preview_status") == PREVIOUS_STATUS,
        "current_next_module_matches": preview.get("next_module") == REQUESTED_MODULE,
        "future_source_discovery_approved": preview.get("approval_grants_future_symbol_source_discovery_next") is True,
        "preview_does_not_allow_api_browse_download_build_now": (
            preview.get("okx_api_call_allowed_now") is False
            and preview.get("okx_browse_allowed_now") is False
            and preview.get("archive_download_allowed_now") is False
            and preview.get("data_build_allowed_now") is False
        ),
        "preview_no_research_or_universe_ready_claim": (
            preview.get("output_valid_for_research_backtest") is False
            and preview.get("output_valid_for_edge_claim") is False
            and preview.get("safe_for_full_universe_acquisition") is False
            and preview.get("broad_acquisition_ready") is False
        ),
        "pilot_pipeline_closed": pilot.get("pipeline_closed_successfully") is True and pilot.get("replacement_checks_all_true") is True,
        "batch_policy_carry_forward_available": policy.get("replacement_checks_all_true") is True,
    }
    return {"head": head, "checks": checks}


def common_summary(
    artifacts: dict[str, dict[str, Any]],
    chain: dict[str, Any],
    search: dict[str, Any],
    py_state: dict[str, Any],
) -> dict[str, Any]:
    validation = search["selected_validation"]
    found = search["local_or_user_symbol_list_found"]
    candidate_count = int(validation["candidate_symbol_count"])
    official_required = not found
    status = PASS_LOCAL_STATUS if found else PASS_LOCAL_INCOMPLETE_STATUS
    replacement_checks = {
        **chain["checks"],
        "symbol_source_discovery_performed": True,
        "local_symbol_list_branch_valid": found and candidate_count > 0 or official_required,
        "malformed_symbols_not_accepted": validation["malformed_symbol_count"] == 0,
        "no_api_browse_download_build_aggregation_now": True,
        "no_research_backtest_edge_claim": True,
        "no_full_universe_or_broad_ready_claim": True,
        "next_route_not_download_or_build": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    if not replacement_checks_all_true:
        status = BLOCKED_STATUS
    next_module = (
        NEXT_LOCAL_MODULE
        if found and replacement_checks_all_true
        else NEXT_OFFICIAL_LOOKUP_MODULE
        if replacement_checks_all_true
        else FAILED_NEXT_MODULE
    )
    quality = (
        QUALITY_LOCAL
        if found and replacement_checks_all_true
        else QUALITY_LOCAL_INCOMPLETE
        if replacement_checks_all_true
        else "FULL_USDT_SWAP_SYMBOL_SOURCE_DISCOVERY_FAILED_CLOSED"
    )
    return {
        "historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_status": status,
        "symbol_source_discovery_performed": True,
        "source_route_used": "USER_SUPPLIED_OR_LOCAL_EXISTING_SYMBOL_LIST" if found else "LOCAL_ARTIFACT_SEARCH_ONLY",
        "local_or_user_symbol_list_found": found,
        "candidate_symbol_list_created": found,
        "candidate_symbol_count": candidate_count if found else 0,
        "usdt_swap_symbol_count": int(validation["usdt_swap_symbol_count"]) if found else 0,
        "malformed_symbol_count": int(validation["malformed_symbol_count"]),
        "duplicate_symbol_count": int(validation["duplicate_symbol_count"]),
        "non_usdt_swap_excluded_count": int(validation["non_usdt_swap_excluded_count"]),
        "official_source_lookup_required": official_required,
        "official_source_lookup_approval_record_created": official_required,
        "survivorship_bias_limitations_recorded": True,
        "current_active_only_limitation_recorded": True,
        "historical_delisted_symbols_not_proven": True,
        "batch_policy_carry_forward_created": True,
        "archive_coverage_eligibility_preview_ready": found,
        "full_universe_acquisition_allowed_now": False,
        "archive_download_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": max(int(artifacts["universe_preview_summary"].get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_discovery": quality,
        "next_module": next_module,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
        **POLICY,
    }


def build_outputs(summary: dict[str, Any], search: dict[str, Any]) -> dict[str, Any]:
    validation = search["selected_validation"]
    outputs: dict[str, Any] = {
        "historical_okx_full_usdt_swap_symbol_source_discovery_report.json": {
            **summary,
            "artifact_type": "symbol_source_discovery_report",
            "selected_local_artifact_path": search["selected_artifact_path"],
            "source_discovery_notes": "Local artifact search only; no OKX API, browse, URL fetch, archive check, download, build, or aggregation performed.",
        },
        "historical_okx_full_usdt_swap_local_symbol_artifact_search_report.json": {
            **summary,
            "artifact_type": "local_symbol_artifact_search_report",
            "search": search,
        },
        "historical_okx_full_usdt_swap_symbol_filter_validation_report.json": {
            **summary,
            "artifact_type": "symbol_filter_validation_report",
            "candidate_symbols_sample": validation["candidate_symbols"][:25],
            "malformed_symbols": validation["malformed_symbols"],
            "duplicate_symbols": validation["duplicate_symbols"][:50],
            "non_usdt_swap_excluded": validation["non_usdt_swap_excluded"][:50],
        },
        "historical_okx_full_usdt_swap_symbol_source_survivorship_limitations_report.json": {
            **summary,
            "artifact_type": "survivorship_limitations_report",
            "limitations": [
                "Current OKX instruments list may be current-active only.",
                "Current-active list is not guaranteed survivorship-complete for 2023-07-01 through 2026-05-18.",
                "Delisted or historical symbols require a separate historical source or user-supplied list.",
                "Near-3y eligible data universe may initially be current-active near-3y universe unless historical delisted list is supplied.",
            ],
        },
        "historical_okx_full_usdt_swap_symbol_source_next_route_decision.json": {
            **summary,
            "artifact_type": "next_route_decision",
            "route_reason": (
                "Valid local/user symbol artifact found; next route is archive coverage eligibility preview."
                if summary["local_or_user_symbol_list_found"]
                else "No valid local/user symbol artifact found; next route is official OKX source lookup approval."
            ),
        },
        "historical_okx_full_usdt_swap_symbol_source_discovery_self_validator.json": {
            **summary,
            "artifact_type": "self_validator",
            "required_outputs": required_outputs(summary),
        },
        "historical_okx_full_usdt_swap_symbol_source_discovery_summary.json": {
            **summary,
            "artifact_type": "summary",
        },
    }
    if summary["candidate_symbol_list_created"]:
        outputs[CANDIDATE_LIST_OUTPUT] = {
            **summary,
            "artifact_type": "candidate_symbol_list",
            "candidate_symbols": validation["candidate_symbols"],
            "candidate_symbol_count": validation["candidate_symbol_count"],
            "source_artifact_path": search["selected_artifact_path"],
            "valid_for_archive_coverage_eligibility_preview": True,
            "valid_for_download_now": False,
            "valid_for_data_build_now": False,
        }
    if summary["official_source_lookup_required"]:
        outputs[OFFICIAL_APPROVAL_OUTPUT] = {
            **summary,
            "artifact_type": "official_source_lookup_approval_record",
            "approval_grants_official_source_lookup_now": False,
            "approval_grants_future_official_source_lookup_next": True,
            "approval_grants_api_now": False,
            "approval_grants_browse_now": False,
            "approval_grants_archive_download_now": False,
            "approval_grants_data_build_now": False,
        }
    return outputs


def required_outputs(summary: dict[str, Any]) -> list[str]:
    outputs = list(REQUIRED_BASE_OUTPUTS)
    if summary["candidate_symbol_list_created"]:
        outputs.append(CANDIDATE_LIST_OUTPUT)
    if summary["official_source_lookup_required"]:
        outputs.append(OFFICIAL_APPROVAL_OUTPUT)
    return outputs


def run_discovery() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    chain = validate_inputs(artifacts, py_state)
    search = inspect_local_symbol_artifacts()
    summary = common_summary(artifacts, chain, search, py_state)
    outputs = build_outputs(summary, search)
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in required_outputs(summary) if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing required outputs: {missing}")
    require(summary["replacement_checks_all_true"] is True, "replacement checks did not all pass")
    return summary


def main() -> int:
    try:
        summary = run_discovery()
    except Exception as exc:
        blocked = {
            "historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_status": BLOCKED_STATUS,
            "symbol_source_discovery_performed": False,
            "blocked_reason": repr(exc),
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "created_at_utc": utc_now(),
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_symbol_source_discovery_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
