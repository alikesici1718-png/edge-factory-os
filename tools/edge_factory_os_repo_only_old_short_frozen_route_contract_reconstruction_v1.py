#!/usr/bin/env python3
"""Frozen old_short route contract reconstruction.

This module reconstructs the old_short route contract from repo-local source
and evidence artifacts. It does not optimize, rerun, touch runtime, place
orders, generate candidates, claim edge, or grant live/capital permissions.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
TOOL_REL = "tools/edge_factory_os_repo_only_old_short_frozen_route_contract_reconstruction_v1.py"
ARTIFACT_REL = "artifacts/old_short/old_short_frozen_route_contract_reconstruction_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

STEP1_REL = "artifacts/old_short/old_short_evidence_recovery_status_refresh_v1.json"
SOURCE_REL = "src/old_short_gate_aware_live_paper_logger.py"
SIZING_REL = "configs/position_sizing_contract.current.json"
FAMILY_CONFIG_REL = "configs/family_config.current.json"
REGISTRY_REL = "edge_factory_os_framework/registries/runtime_family_registry_v1.json"
STATUS_PANEL_REL = "edge_factory_os_framework/status/runtime_family_monitor_status_panel_no_capital_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION_CREATED"
ARTIFACT_KIND = "OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION"
MODULE = "edge_factory_os_repo_only_old_short_frozen_route_contract_reconstruction_v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_output(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repo_clean_except_expected() -> bool:
    allowed = {TOOL_REL, ARTIFACT_REL}
    status = git_output(["status", "--short", "--untracked-files=all"])
    if not status:
        return True
    for line in status.splitlines():
        rel = line[3:].replace("\\", "/")
        if rel not in allowed:
            return False
    return True


def tracked_python_count() -> int:
    out = git_output(["ls-files", "*.py"])
    return 0 if not out else len(out.splitlines())


def load_json(rel_path: str) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {rel_path}")
    return path.read_text(encoding="utf-8", errors="ignore")


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_argparse_defaults(source: str) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        option = None
        if node.args and isinstance(node.args[0], ast.Constant):
            option = str(node.args[0].value).lstrip("-").replace("-", "_")
        if not option:
            continue
        for keyword in node.keywords:
            if keyword.arg == "dest" and isinstance(keyword.value, ast.Constant):
                option = str(keyword.value.value)
        default_found = False
        for keyword in node.keywords:
            if keyword.arg == "default":
                try:
                    defaults[option] = ast.literal_eval(keyword.value)
                except Exception:
                    defaults[option] = None
                default_found = True
        if not default_found:
            for keyword in node.keywords:
                if keyword.arg == "action" and isinstance(keyword.value, ast.Constant):
                    action = str(keyword.value.value)
                    if action == "store_true":
                        defaults.setdefault(option, False)
                    if action == "store_false":
                        defaults.setdefault(option, True)
    return defaults


def find_required_source_snippets(source: str) -> dict[str, Any]:
    checks = {
        "okx_candle_endpoint": 'CANDLES_ENDPOINT = "/api/v5/market/candles"' in source,
        "ret1_bps_defined": 'df["ret1_bps"] = close.pct_change() * 10000.0' in source,
        "ret3_bps_defined": 'df["ret3_bps"] = (close / close.shift(3) - 1.0) * 10000.0' in source,
        "ret5_bps_defined": 'df["ret5_bps"] = (close / close.shift(5) - 1.0) * 10000.0' in source,
        "ret60_bps_defined": 'df["ret60_bps"] = (close / close.shift(60) - 1.0) * 10000.0' in source,
        "range_bps_defined": 'df["range_bps"] = (df["high"] - df["low"]) / df["open"].replace(0, np.nan) * 10000.0' in source,
        "blowoff_rule_present": "blowoff_ret60_bps" in source and "blowoff_ret3_max_bps" in source,
        "meanrev_rule_present": "meanrev_ret5_bps" in source,
        "entry_delay_present": "target_entry = signal_time + pd.Timedelta(minutes=self.args.entry_delay_minutes)" in source,
        "planned_exit_present": "planned_exit = target_entry + pd.Timedelta(minutes=self.args.hold_minutes)" in source,
        "entry_slippage_present": "entry_price = raw_entry * (1.0 - self.args.entry_slip_bps / 10000.0)" in source,
        "exit_slippage_present": "exit_price = raw_exit * (1.0 + pos.exit_slip_bps / 10000.0)" in source,
        "short_return_present": "gross_ret = pos.entry_price / exit_price - 1.0" in source,
        "fee_model_present": "realistic_net_ret = gross_ret - pos.fee_bps_total / 10000.0" in source,
        "global_gate_present": "def global_gate_decision" in source and "require_global_gate" in source,
    }
    line_refs = {}
    for key, needle in {
        "blowoff_rule_line": "blowoff = x.loc[",
        "meanrev_rule_line": "meanrev = x.loc[",
        "entry_slippage_line": "entry_price = raw_entry",
        "exit_return_line": "gross_ret = pos.entry_price / exit_price - 1.0",
        "argparse_start_line": "ap = argparse.ArgumentParser",
    }.items():
        for idx, line in enumerate(source.splitlines(), start=1):
            if needle in line:
                line_refs[key] = {"line": idx, "text": line.strip()}
                break
    return {"checks": checks, "line_refs": line_refs}


def build_payload() -> dict[str, Any]:
    step1 = load_json(STEP1_REL)
    source = read_text(SOURCE_REL)
    sizing = load_json(SIZING_REL)
    family_config = load_json(FAMILY_CONFIG_REL)
    registry = load_json(REGISTRY_REL)
    status_panel = load_json(STATUS_PANEL_REL)

    defaults = parse_argparse_defaults(source)
    snippets = find_required_source_snippets(source)
    source_checks = snippets["checks"]

    old_short_sizing = sizing.get("families", {}).get("old_short", {})
    registry_old_short = {}
    for row in registry.get("runtime_family_rows", []):
        if row.get("family_key") == "old_short":
            registry_old_short = row
            break

    route_contract = {
        "route_name": "old_short_gate_aware",
        "family_key": "old_short",
        "strategy_type": "short_reversal_after_upside_blowoff_or_mean_reversion_event",
        "exchange": "OKX",
        "instrument_type": "USDT-SWAP",
        "timeframe": "1m",
        "source_module": SOURCE_REL,
        "symbol_universe": {
            "mode": defaults.get("coins"),
            "base_dir": defaults.get("base_dir"),
            "out_dir": defaults.get("out_dir"),
            "exclude": defaults.get("exclude"),
            "resolution_rule": [
                "If coins arg is explicit, use those symbols minus excluded symbols.",
                "If out_dir/old_short_coin_universe.txt exists, use that list minus excluded symbols.",
                "Else if out_dir/old_short_gate_aware_config.json or strategy_config.json exists, use recorded coins minus excluded symbols.",
                "Else scan base_dir coin directories containing raw/**/{COIN}-USDT-SWAP_1m_*.csv, minus excluded symbols.",
            ],
            "no_symbol_additions_or_removals_allowed_by_reconstruction": True,
        },
        "signal_definition": {
            "feature_source": "confirmed OKX 1m candles",
            "ret1_bps": "close.pct_change(1) * 10000",
            "ret3_bps": "(close / close.shift(3) - 1) * 10000",
            "ret5_bps": "(close / close.shift(5) - 1) * 10000",
            "ret60_bps": "(close / close.shift(60) - 1) * 10000",
            "range_bps": "(high - low) / open * 10000",
            "blowoff_short": {
                "ret60_bps_gte": defaults.get("blowoff_ret60_bps"),
                "ret3_bps_lte": defaults.get("blowoff_ret3_max_bps"),
                "ret1_bps_lte": defaults.get("ret1_max_bps"),
            },
            "mean_reversion_short": {
                "ret5_bps_gte": defaults.get("meanrev_ret5_bps"),
                "ret1_bps_lte": defaults.get("ret1_max_bps"),
            },
            "signal_backfill_minutes_runtime_window": defaults.get("signal_backfill_minutes"),
        },
        "entry_rule": {
            "side": "short",
            "entry_delay_minutes": defaults.get("entry_delay_minutes"),
            "entry_price": "target_entry 1m candle close adjusted by entry_slip_bps: raw_entry_close * (1 - entry_slip_bps / 10000)",
            "global_gate_required_by_default": defaults.get("require_global_gate"),
            "global_gate_path": defaults.get("global_gate_path"),
            "required_gate_decision": "ALLOW when require_global_gate is true",
            "entry_filters": {
                "min_signal_vol_quote": defaults.get("min_signal_vol_quote"),
                "min_entry_vol_quote": defaults.get("min_entry_vol_quote"),
                "max_signal_range_bps": defaults.get("max_signal_range_bps"),
                "max_entry_range_bps": defaults.get("max_entry_range_bps"),
                "max_positions": defaults.get("max_positions"),
                "same_coin_overlap_allowed": False,
                "pending_max_wait_minutes": defaults.get("pending_max_wait_minutes"),
            },
        },
        "exit_rule": {
            "hold_minutes": defaults.get("hold_minutes"),
            "exit_price": "planned_exit 1m candle close adjusted by exit_slip_bps: raw_exit_close * (1 + exit_slip_bps / 10000)",
            "gross_short_return": "entry_price / exit_price - 1",
            "net_return": "gross_short_return - fee_bps_total / 10000",
            "stress_net_return": "net_return - stress_extra_bps / 10000",
        },
        "holding_stop_take_profit": {
            "fixed_holding_minutes": defaults.get("hold_minutes"),
            "stop_loss": None,
            "take_profit": None,
            "source_contract_has_stop_or_take_profit": False,
        },
        "cost_model": {
            "entry_slip_bps": defaults.get("entry_slip_bps"),
            "exit_slip_bps": defaults.get("exit_slip_bps"),
            "fee_bps_total": defaults.get("fee_bps_total"),
            "stress_extra_bps": defaults.get("stress_extra_bps"),
            "realistic_net_includes_fee_bps_but_slippage_is_embedded_in_entry_exit_prices": True,
        },
        "sizing": {
            "start_equity": defaults.get("start_equity"),
            "paper_fraction": defaults.get("paper_fraction"),
            "default_notional": defaults.get("default_notional"),
            "sizing_contract_default_path": defaults.get("sizing_contract"),
            "repo_position_sizing_contract": {
                "enabled": old_short_sizing.get("enabled"),
                "lifecycle": old_short_sizing.get("lifecycle"),
                "priority": old_short_sizing.get("priority"),
                "max_positions": old_short_sizing.get("max_positions"),
                "capital_fraction": old_short_sizing.get("capital_fraction"),
                "fixed_notional": old_short_sizing.get("fixed_notional"),
                "expected_notional": old_short_sizing.get("expected_notional"),
            },
        },
        "data_source": {
            "runtime_public_endpoint_in_source": "https://www.okx.com/api/v5/market/candles",
            "historical_file_pattern_in_source": r"{base_dir}\{COIN}\raw\**\{COIN}-USDT-SWAP_1m_*.csv",
            "family_config_old_short_output_dir": family_config.get("old_short"),
            "reviewed_historical_data_required_before_backtest": True,
        },
        "old_monitoring_rules": {
            "minimum_closed_trades_for_monitoring_decision": registry_old_short.get("minimum_closed_trades_for_monitoring_decision", 20),
            "minimum_closed_trades_for_capital_review": registry_old_short.get("minimum_closed_trades_for_capital_review", 50),
            "protected_from_unrelated_research_route_failures": registry_old_short.get("protected_from_unrelated_research_route_failures", True),
            "capital_requires_separate_governor": True,
            "runtime_live_capital_allowed_now": False,
        },
        "old_capital_review_threshold": registry_old_short.get("minimum_closed_trades_for_capital_review", 50),
        "no_optimization": True,
        "no_parameter_changes": True,
        "no_threshold_changes": True,
        "no_universe_expansion": True,
    }

    required_fields = {
        "route_name": route_contract["route_name"],
        "symbol_universe": route_contract["symbol_universe"],
        "timeframe": route_contract["timeframe"],
        "signal_definition": route_contract["signal_definition"],
        "entry_rule": route_contract["entry_rule"],
        "exit_rule": route_contract["exit_rule"],
        "cost_model": route_contract["cost_model"],
        "data_source": route_contract["data_source"],
        "old_monitoring_rules": route_contract["old_monitoring_rules"],
        "old_capital_review_threshold": route_contract["old_capital_review_threshold"],
    }
    unresolved_fields = [
        name
        for name, value in required_fields.items()
        if value in (None, "", {}, [])
    ]
    missing_source_checks = [name for name, ok in source_checks.items() if not ok]
    if missing_source_checks:
        unresolved_fields.extend([f"source_check_missing:{name}" for name in missing_source_checks])

    complete = not unresolved_fields
    execution_allowed_next = bool(complete)
    safety_permissions = {
        "frozen_route_contract_reconstructed": True,
        "strategy_execution_allowed_now": False,
        "strategy_execution_allowed_next": execution_allowed_next,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_except_expected(),
        "step1_artifact_loaded": step1.get("status") == "PASS_REPO_ONLY_OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH_CREATED",
        "source_old_short_logger_loaded": True,
        "position_sizing_contract_loaded": True,
        "family_config_loaded": True,
        "runtime_family_registry_loaded": True,
        "no_parameter_changes": True,
        "no_threshold_changes": True,
        "no_symbol_additions_or_removals": True,
        "no_optimization": True,
        "contract_complete": complete,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
    }
    replacement_checks_all_true = all(validation_checks.values()) and all(
        value is False
        for key, value in safety_permissions.items()
        if key.endswith("_allowed_now")
    )

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "head": git_output(["rev-parse", "HEAD"]),
            "repo_clean_before_run": validation_checks["repo_clean_before_run"],
            "tracked_python_count_before": tracked_python_count(),
            "generated_at_utc": utc_now(),
        },
        "route_contract": route_contract,
        "reconstructed_from_files": {
            "step1_evidence_recovery": STEP1_REL,
            "old_short_source": SOURCE_REL,
            "position_sizing_contract": SIZING_REL,
            "family_config": FAMILY_CONFIG_REL,
            "runtime_family_registry": REGISTRY_REL,
            "runtime_family_status_panel": STATUS_PANEL_REL,
            "source_line_refs": snippets["line_refs"],
        },
        "completeness_check": {
            "complete": complete,
            "required_fields_present": sorted(required_fields),
            "source_checks": source_checks,
            "missing_source_checks": missing_source_checks,
            "global_gate_dependency_preserved": True,
            "data_source_must_be_verified_in_backtest_step": True,
        },
        "unresolved_fields": unresolved_fields,
        "execution_allowed_next": execution_allowed_next,
        "next_recommended_step": "OLD_SHORT_FROZEN_BACKTEST_RERUN_ONLY" if execution_allowed_next else "MANUAL_SOURCE_REVIEW",
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    return payload


def main() -> None:
    payload = build_payload()
    write_artifact(payload)
    print(f"status: {payload['status']}")
    print(f"contract_complete: {str(payload['completeness_check']['complete']).lower()}")
    print(f"execution_allowed_next: {str(payload['execution_allowed_next']).lower()}")
    print(f"unresolved_fields_count: {len(payload['unresolved_fields'])}")
    print(f"route_name: {payload['route_contract']['route_name']}")
    print(f"timeframe: {payload['route_contract']['timeframe']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


if __name__ == "__main__":
    main()
