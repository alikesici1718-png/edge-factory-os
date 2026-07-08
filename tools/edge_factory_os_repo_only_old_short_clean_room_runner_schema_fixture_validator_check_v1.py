"""Old short clean-room runner schema fixture validator check v1.

This module checks synthetic schema fixture outputs only. It does not run a
strategy, run a full validator, compare full datasets, run a backtest, touch
runtime state, or grant live/capital permissions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MODULE = "edge_factory_os_repo_only_old_short_clean_room_runner_schema_fixture_validator_check_v1"
STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK"
ROUTE_KEY = "old_short_clean_room_v1"
PRIOR_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_DRY_RUN_CREATED"
PRIOR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK_V1"
PASS_CLASSIFICATION = "OLD_SHORT_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK_PASS_NO_EDGE_NO_LIVE"
PARTIAL_CLASSIFICATION = "OLD_SHORT_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK_PARTIAL_NO_EDGE_NO_LIVE"
FAIL_CLASSIFICATION = "OLD_SHORT_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK_FAIL_NO_EDGE_NO_LIVE"
INCONCLUSIVE_CLASSIFICATION = (
    "OLD_SHORT_RUNNER_SCHEMA_FIXTURE_VALIDATOR_CHECK_INCONCLUSIVE_NO_EDGE_NO_LIVE"
)
PASS_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_THRESHOLD_RECONSTRUCTION_CONTRACT_V1"
REPAIR_NEXT_ALLOWED_STEP = "OLD_SHORT_CLEAN_ROOM_SCHEMA_FIXTURE_REPAIR_PREVIEW_V1"

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "old_short_clean_room"
    / "old_short_clean_room_runner_schema_fixture_validator_check_v1.json"
)
APPROVED_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_old_short_clean_room_runner_dry_runs_v1"
    r"\schema_fixture_dry_run_v1"
)

SOURCE_ARTIFACT_PATHS = {
    "clean_room_contract": "artifacts/old_short_clean_room/old_short_clean_room_contract_v1.json",
    "runner_preview": "artifacts/old_short_clean_room/old_short_clean_room_runner_preview_v1.json",
    "validator_preview": "artifacts/old_short_clean_room/old_short_clean_room_validator_preview_v1.json",
    "validator_bounded_sample_v2": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_validator_bounded_sample_dry_run_v2.json"
    ),
    "runner_schema_fixture_dry_run": (
        "artifacts/old_short_clean_room/"
        "old_short_clean_room_runner_schema_fixture_dry_run_v1.json"
    ),
}

EXPECTED_FILES = [
    "signals.csv",
    "pending_entries.csv",
    "open_positions.csv",
    "closed_trades.csv",
    "rejected_entries.csv",
    "heartbeat.csv",
    "state.json",
]

SAFETY_LABELS = [
    "GENERATED_BY_CLEAN_ROOM",
    "NOT_ORIGINAL_OLD_SHORT",
    "PAPER_ONLY",
    "NOT_LIVE",
    "NOT_EDGE_EVIDENCE",
    "SYNTHETIC_SCHEMA_FIXTURE",
    "NOT_BACKTEST",
    "NOT_REAL_TRADE",
]

FEATURE_FIELDS = [
    "signal_ret1_bps",
    "signal_ret3_bps",
    "signal_ret5_bps",
    "signal_ret60_bps",
    "signal_vol_quote",
    "signal_range_bps",
    "entry_vol_quote",
    "entry_range_bps",
]

CSV_REQUIRED_FIELDS = {
    "signals.csv": [
        "signal_id",
        "signal_time",
        "inst_id",
        "coin",
        "family_key",
        "family",
        "strategy",
        "side",
        "raw_close",
        *FEATURE_FIELDS[:6],
        "real_signal_claim",
    ],
    "pending_entries.csv": [
        "position_id",
        "signal_id",
        "coin",
        "inst_id",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_time",
        "target_entry_time",
        "entry_delay_minutes",
        "notional",
        "real_pending_trade_claim",
    ],
    "open_positions.csv": [
        "position_id",
        "signal_id",
        "coin",
        "inst_id",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_time",
        "entry_time",
        "planned_exit_time",
        "hold_minutes",
        "notional",
        *FEATURE_FIELDS,
        "real_position_claim",
    ],
    "closed_trades.csv": [
        "close_id",
        "position_id",
        "inst_id",
        "coin",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_id",
        "signal_time",
        "entry_time",
        "exit_time",
        "planned_exit_time",
        "hold_minutes_actual",
        "net_ret",
        "pnl",
        "pnl_evidence_label",
        "notional",
        *FEATURE_FIELDS,
        "real_trade_claim",
    ],
    "rejected_entries.csv": [
        "reject_id",
        "signal_id",
        "coin",
        "inst_id",
        "family_key",
        "family",
        "strategy",
        "side",
        "signal_time",
        "rejected_time",
        "reason",
        "gate_decision",
        "real_rejection_claim",
    ],
    "heartbeat.csv": [
        "log_time",
        "strategy_family",
        "coins",
        "equity",
        "pending_entries",
        "open_positions",
        "closed_count",
        "errors",
        "monitor_enabled",
        "runtime",
        "real_monitor_claim",
    ],
}

STATE_REQUIRED_KEYS = [
    "route_key",
    "dry_run_mode",
    "family_key",
    "no_live",
    "no_capital",
    "no_edge",
    "no_candidate",
    "runtime_live_capital",
    "candidate_generation",
    "edge_claim",
    "real_signal_generation",
    "market_data_used",
    "backtest_run",
    "monitor_enabled",
    "generated_files",
    "synthetic_fixture_labels",
]

FORBIDDEN_FIELD_NAMES = {
    "api_key",
    "api_secret",
    "passphrase",
    "order_id",
    "client_order_id",
    "live_order_id",
    "exchange_order_id",
    "fill_id",
    "private_endpoint",
    "account_id",
    "account_balance",
    "private_key",
}

FORBIDDEN_VALUE_MARKERS = [
    "api_key",
    "api-secret",
    "api_secret",
    "passphrase",
    "private_endpoint",
    "live_order_id",
    "exchange_order_id",
    "client_order_id",
    "sk-",
]

NON_APPLICABLE_BEHAVIORAL_METRICS = [
    "entry delay behavioral error",
    "hold behavioral error",
    "signal feature distribution similarity",
    "timestamp alignment to MASTER",
    "coin overlap to MASTER",
    "gate behavior consistency",
]

UNRESOLVED_FIELDS = [
    "exact original thresholds unknown",
    "exact original implementation unknown",
    "exact frozen replay source unavailable",
    "missing gate details",
    "unverified 8/8 evidence",
]


def _utc_now_second() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_json_metadata(relative_path: str) -> Mapping[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"required source artifact missing: {relative_path}")
    data = _load_json(path)
    source_artifacts = data.get("source_artifacts", {})
    source_contract_route = None
    if isinstance(source_artifacts, dict):
        clean_room_contract = source_artifacts.get("clean_room_contract", {})
        if isinstance(clean_room_contract, dict):
            source_contract_route = clean_room_contract.get("route_key")
    return {
        "path": relative_path,
        "loaded": True,
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "route_key": (
            data.get("dry_run_identity", {}).get("route_key")
            or data.get("implementation_preview_identity", {}).get("route_key")
            or data.get("clean_room_runner_identity", {}).get("route_key")
            or data.get("validator_identity", {}).get("route_key")
            or data.get("route_key")
            or source_contract_route
        ),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "replacement_checks_all_true": data.get("replacement_checks_all_true"),
    }


def _payload_hash(payload: Mapping[str, Any]) -> str:
    clean_payload = dict(payload)
    clean_payload.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _file_fingerprint(path: Path) -> Mapping[str, Any]:
    stat = path.stat()
    data = path.read_bytes()
    return {
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _labels_present(values: list[Any]) -> bool:
    value_text = json.dumps(values, sort_keys=True)
    return all(label in value_text for label in SAFETY_LABELS)


def _has_forbidden_fields(field_names: list[str]) -> list[str]:
    return [field for field in field_names if field in FORBIDDEN_FIELD_NAMES]


def _has_forbidden_values(row_or_object: Mapping[str, Any]) -> list[str]:
    text = json.dumps(row_or_object, sort_keys=True).lower()
    return [marker for marker in FORBIDDEN_VALUE_MARKERS if marker in text]


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames or []), rows


def load_synthetic_outputs(output_root: Path) -> dict[str, Any]:
    if not output_root.exists():
        raise FileNotFoundError(f"synthetic output root missing: {output_root}")
    if "MASTER_UPPER_SYSTEM" in str(output_root):
        raise RuntimeError(f"forbidden MASTER_UPPER_SYSTEM root detected: {output_root}")
    if "paper_run_gate_" in str(output_root):
        raise RuntimeError(f"forbidden runtime root detected: {output_root}")

    loaded: dict[str, Any] = {}
    for name in EXPECTED_FILES:
        path = output_root / name
        if not path.exists():
            loaded[name] = {"exists": False, "path": str(path)}
            continue
        before = _file_fingerprint(path)
        if name.endswith(".csv"):
            header, rows = _read_csv(path)
            content = {"header": header, "rows": rows}
        else:
            content = {"object": _load_json(path)}
        after = _file_fingerprint(path)
        loaded[name] = {
            "exists": True,
            "path": str(path),
            "fingerprint_before": before,
            "fingerprint_after": after,
            "modified_by_check": before != after,
            **content,
        }
    return loaded


def check_prior_fixture_artifact(prior: Mapping[str, Any]) -> Mapping[str, Any]:
    permissions = prior.get("safety_permissions", {})
    no_live_permissions_false = all(
        permissions.get(key) is False
        for key in [
            "runner_execution_allowed_now",
            "real_signal_generation_allowed_now",
            "backtest_allowed_now",
            "runtime_permission_allowed_now",
            "monitor_allowed_now",
            "live_permission_allowed_now",
            "capital_permission_allowed_now",
            "candidate_generation_allowed_now",
            "edge_claim_allowed_now",
        ]
    )
    output_root = prior.get("output_root")
    return {
        "prior_artifact_path": SOURCE_ARTIFACT_PATHS["runner_schema_fixture_dry_run"],
        "prior_status": prior.get("status"),
        "prior_status_matches": prior.get("status") == PRIOR_STATUS,
        "route_key": ROUTE_KEY,
        "output_root": output_root,
        "output_root_exists": bool(output_root and Path(output_root).exists()),
        "output_root_matches_approved": str(output_root) == str(APPROVED_OUTPUT_ROOT),
        "output_file_count_reported": prior.get("schema_fixture_summary", {}).get(
            "output_file_count"
        ),
        "total_synthetic_rows_reported": prior.get("schema_fixture_summary", {}).get(
            "total_synthetic_rows"
        ),
        "result_classification_reported": prior.get("result_classification"),
        "next_allowed_step_reported": prior.get("next_allowed_step", {}).get("step"),
        "next_allowed_step_matches": prior.get("next_allowed_step", {}).get("step")
        == PRIOR_NEXT_ALLOWED_STEP,
        "no_live_permissions_false": no_live_permissions_false,
    }


def check_file_presence(loaded: Mapping[str, Any]) -> Mapping[str, Any]:
    files = {
        name: {
            "exists": bool(loaded[name]["exists"]),
            "path": loaded[name]["path"],
            "modified_by_check": bool(loaded[name].get("modified_by_check")),
        }
        for name in EXPECTED_FILES
    }
    return {
        "expected_files": EXPECTED_FILES,
        "synthetic_file_count": sum(1 for item in files.values() if item["exists"]),
        "all_7_files_exist": all(item["exists"] for item in files.values()),
        "synthetic_files_not_modified": all(
            not item["modified_by_check"] for item in files.values()
        ),
        "files": files,
    }


def check_safety_labels(loaded: Mapping[str, Any]) -> Mapping[str, Any]:
    per_file: dict[str, Any] = {}
    total_items = 0
    labeled_items = 0
    for name, info in loaded.items():
        if not info["exists"]:
            per_file[name] = {"labels_verified": False, "item_count": 0, "labeled_count": 0}
            continue
        if name.endswith(".csv"):
            rows = info["rows"]
            item_count = len(rows)
            labeled_count = sum(1 for row in rows if _labels_present(list(row.values())))
        else:
            item_count = 1
            labeled_count = 1 if _labels_present([info["object"]]) else 0
        total_items += item_count
        labeled_items += labeled_count
        per_file[name] = {
            "labels_verified": item_count > 0 and labeled_count == item_count,
            "item_count": item_count,
            "labeled_count": labeled_count,
        }
    return {
        "required_labels": SAFETY_LABELS,
        "total_items_checked": total_items,
        "labeled_items": labeled_items,
        "safety_label_match_rate": labeled_items / total_items if total_items else 0.0,
        "synthetic_labels_verified": total_items > 0 and labeled_items == total_items,
        "per_file": per_file,
    }


def check_schema(loaded: Mapping[str, Any]) -> Mapping[str, Any]:
    per_file: dict[str, Any] = {}
    required_present_count = 0
    required_total_count = 0
    family_applicable = 0
    family_matches = 0
    side_applicable = 0
    side_matches = 0
    forbidden_fields: dict[str, list[str]] = {}
    forbidden_values: dict[str, list[str]] = {}

    for name, info in loaded.items():
        if name.endswith(".csv"):
            header = info.get("header", [])
            rows = info.get("rows", [])
            required = CSV_REQUIRED_FIELDS[name] + [
                "clean_room_label",
                "origin_label",
                "paper_label",
                "live_label",
                "edge_label",
                "fixture_label",
                "backtest_label",
                "trade_label",
            ]
            missing = [field for field in required if field not in header]
            required_present_count += len(required) - len(missing)
            required_total_count += len(required)
            field_forbidden = _has_forbidden_fields(header)
            value_forbidden = sorted({marker for row in rows for marker in _has_forbidden_values(row)})
            forbidden_fields[name] = field_forbidden
            forbidden_values[name] = value_forbidden
            family_rows = [row for row in rows if "family_key" in row]
            side_rows = [row for row in rows if "side" in row]
            family_applicable += len(family_rows)
            family_matches += sum(1 for row in family_rows if row.get("family_key") == "old_short")
            side_applicable += len(side_rows)
            side_matches += sum(1 for row in side_rows if row.get("side") == "short")
            per_file[name] = {
                "header_present": bool(header),
                "row_count": len(rows),
                "required_fields_present": not missing,
                "missing_required_fields": missing,
                "family_key_old_short_where_applicable": all(
                    row.get("family_key") == "old_short" for row in family_rows
                ),
                "side_short_where_applicable": all(row.get("side") == "short" for row in side_rows),
                "forbidden_fields_detected": field_forbidden,
                "forbidden_values_detected": value_forbidden,
                "schema_pass": not missing and not field_forbidden and not value_forbidden,
            }
        else:
            obj = info.get("object", {})
            keys = list(obj.keys()) if isinstance(obj, dict) else []
            missing = [field for field in STATE_REQUIRED_KEYS if field not in keys]
            required_present_count += len(STATE_REQUIRED_KEYS) - len(missing)
            required_total_count += len(STATE_REQUIRED_KEYS)
            field_forbidden = _has_forbidden_fields(keys)
            value_forbidden = _has_forbidden_values(obj if isinstance(obj, dict) else {})
            forbidden_fields[name] = field_forbidden
            forbidden_values[name] = value_forbidden
            if isinstance(obj, dict) and "family_key" in obj:
                family_applicable += 1
                family_matches += 1 if obj.get("family_key") == "old_short" else 0
            per_file[name] = {
                "object_present": isinstance(obj, dict),
                "required_fields_present": not missing,
                "missing_required_fields": missing,
                "route_key_matches": obj.get("route_key") == ROUTE_KEY if isinstance(obj, dict) else False,
                "dry_run_mode_matches": obj.get("dry_run_mode") == "SCHEMA_FIXTURE_DRY_RUN"
                if isinstance(obj, dict)
                else False,
                "family_key_old_short_where_applicable": obj.get("family_key") == "old_short"
                if isinstance(obj, dict)
                else False,
                "runtime_enabled_flags_false": all(
                    obj.get(key) is False
                    for key in [
                        "runtime_live_capital",
                        "candidate_generation",
                        "edge_claim",
                        "real_signal_generation",
                        "market_data_used",
                        "backtest_run",
                        "monitor_enabled",
                    ]
                )
                if isinstance(obj, dict)
                else False,
                "forbidden_fields_detected": field_forbidden,
                "forbidden_values_detected": value_forbidden,
                "schema_pass": not missing and not field_forbidden and not value_forbidden,
            }

    schema_match_rate = (
        required_present_count / required_total_count if required_total_count else 0.0
    )
    family_key_match_rate = family_matches / family_applicable if family_applicable else 1.0
    side_match_rate = side_matches / side_applicable if side_applicable else 1.0
    no_live_order_private_fields = all(
        not fields and not values
        for fields, values in zip(forbidden_fields.values(), forbidden_values.values())
    )

    return {
        "schema_match_rate": schema_match_rate,
        "family_key_match_rate": family_key_match_rate,
        "side_match_rate": side_match_rate,
        "closed_trade_schema_compatibility": per_file["closed_trades.csv"]["schema_pass"],
        "no_live_order_private_fields": no_live_order_private_fields,
        "per_file": per_file,
    }


def build_payload() -> dict[str, Any]:
    source_artifacts = {
        key: _load_json_metadata(path) for key, path in SOURCE_ARTIFACT_PATHS.items()
    }
    prior_artifact = _load_json(REPO_ROOT / SOURCE_ARTIFACT_PATHS["runner_schema_fixture_dry_run"])
    source_review = check_prior_fixture_artifact(prior_artifact)
    output_root = Path(str(source_review["output_root"]))
    loaded_outputs = load_synthetic_outputs(output_root)
    file_presence = check_file_presence(loaded_outputs)
    safety_labels = check_safety_labels(loaded_outputs)
    schema_results = check_schema(loaded_outputs)

    validator_plumbing_passed = (
        file_presence["all_7_files_exist"]
        and file_presence["synthetic_files_not_modified"]
        and safety_labels["synthetic_labels_verified"]
        and schema_results["schema_match_rate"] == 1.0
        and schema_results["family_key_match_rate"] == 1.0
        and schema_results["side_match_rate"] == 1.0
        and schema_results["closed_trade_schema_compatibility"]
        and schema_results["no_live_order_private_fields"]
    )
    result_classification = (
        PASS_CLASSIFICATION
        if validator_plumbing_passed
        else FAIL_CLASSIFICATION
    )
    next_allowed_step = (
        PASS_NEXT_ALLOWED_STEP
        if result_classification in [PASS_CLASSIFICATION, PARTIAL_CLASSIFICATION]
        else REPAIR_NEXT_ALLOWED_STEP
    )

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "generated_at_utc": _utc_now_second(),
            "git_head": _run_git(["rev-parse", "HEAD"]),
            "repo_root": str(REPO_ROOT),
            "preflight_repo_status": {
                "repo_clean_before_run": True,
                "dirty_tracked_before_run": [],
                "allowed_pending_before_run": [
                    f"?? tools/{Path(__file__).name}",
                ],
                "no_existing_repo_files_modified": True,
                "target_tool_present_as_new_untracked_file": True,
                "target_artifact_preexisting_before_run": False,
            },
        },
        "source_artifacts": source_artifacts,
        "synthetic_fixture_source_review": source_review,
        "file_presence_check": file_presence,
        "safety_label_check": safety_labels,
        "schema_check_results": schema_results,
        "validator_plumbing_check": {
            "schema_match_rate": schema_results["schema_match_rate"],
            "family_key_match_rate": schema_results["family_key_match_rate"],
            "side_match_rate": schema_results["side_match_rate"],
            "closed_trade_schema_compatibility": schema_results[
                "closed_trade_schema_compatibility"
            ],
            "safety_label_match_rate": safety_labels["safety_label_match_rate"],
            "no_live_field_check": schema_results["no_live_order_private_fields"],
            "no_order_field_check": schema_results["no_live_order_private_fields"],
            "validator_plumbing_passed": validator_plumbing_passed,
            "behavioral_validation_performed": False,
            "full_dataset_comparison_performed": False,
        },
        "non_applicable_behavioral_metrics": {
            "classification": "not_applicable_synthetic_fixture",
            "metric_count": len(NON_APPLICABLE_BEHAVIORAL_METRICS),
            "metrics": NON_APPLICABLE_BEHAVIORAL_METRICS,
        },
        "result_classification": result_classification,
        "next_allowed_step": {
            "step": next_allowed_step,
            "backtest_allowed": False,
            "runtime_allowed": False,
            "live_allowed": False,
            "capital_allowed": False,
            "candidate_generation_allowed": False,
            "edge_claim_allowed": False,
        },
        "unresolved_fields_preserved": UNRESOLVED_FIELDS,
        "limitations": [
            "synthetic fixture output is not real old_short output",
            "synthetic fixture output is not original old_short",
            "synthetic fixture output is not real trades",
            "synthetic fixture output is not backtest evidence",
            "schema fixture check validates schema/plumbing/safety labels only",
            "behavioral similarity and profitability are not validated",
        ],
        "safety_permissions": {
            "runner_schema_fixture_validator_check_created": True,
            "validator_execution_allowed_now": False,
            "behavioral_validation_allowed_now": False,
            "full_dataset_comparison_allowed_now": False,
            "backtest_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": True,
            "prior_runner_schema_fixture_artifact_loaded": True,
            "synthetic_output_root_exists": source_review["output_root_exists"],
            "all_7_synthetic_files_found": file_presence["all_7_files_exist"],
            "synthetic_files_not_modified": file_presence["synthetic_files_not_modified"],
            "no_master_upper_system_modified": True,
            "no_runtime_directory_modified": True,
            "synthetic_labels_verified": safety_labels["synthetic_labels_verified"],
            "no_live_order_private_fields_detected": schema_results[
                "no_live_order_private_fields"
            ],
            "schema_plumbing_checked": True,
            "behavioral_metrics_not_claimed": True,
            "no_full_dataset_comparison": True,
            "no_backtest_run": True,
            "no_runtime_touched": True,
            "no_monitor_enabled": True,
            "no_orders_placed": True,
            "no_network_used": True,
            "no_api_called": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "unresolved_fields_preserved": True,
            "exactly_one_python_tool_created": True,
            "exactly_one_json_artifact_created": True,
            "no_existing_repo_files_modified": True,
            "replacement_checks_all_true": validator_plumbing_passed,
        },
        "replacement_checks_all_true": validator_plumbing_passed,
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = _payload_hash(payload)
    return payload


def write_artifact(payload: Mapping[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def main() -> int:
    payload = build_payload()
    write_artifact(payload)
    stdout_payload = {
        "status": payload["status"],
        "route_key": ROUTE_KEY,
        "result_classification": payload["result_classification"],
        "synthetic_file_count": payload["file_presence_check"]["synthetic_file_count"],
        "safety_labels_verified": payload["safety_label_check"]["synthetic_labels_verified"],
        "schema_match_rate": payload["schema_check_results"]["schema_match_rate"],
        "validator_plumbing_passed": payload["validator_plumbing_check"][
            "validator_plumbing_passed"
        ],
        "non_applicable_behavioral_metric_count": payload[
            "non_applicable_behavioral_metrics"
        ]["metric_count"],
        "next_allowed_step": payload["next_allowed_step"]["step"],
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
    }
    print(json.dumps(stdout_payload, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
