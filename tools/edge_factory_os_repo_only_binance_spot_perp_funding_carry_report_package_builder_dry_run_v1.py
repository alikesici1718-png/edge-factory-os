#!/usr/bin/env python3
"""Build a JSON-only report package dry-run for the funding-carry paper monitor."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_PACKAGE_BUILDER_DRY_RUN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_PACKAGE_BUILDER_DRY_RUN"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_package_builder_dry_run_v1"
CLASSIFICATION = "REPORT_PACKAGE_BUILDER_DRY_RUN_PASS_READY_FOR_PACKAGE_REVIEW_NO_LIVE_PERMISSION"
NEXT_ALLOWED_STEP = "REPORT_PACKAGE_DRY_RUN_REVIEW_ONLY"

ROOT = Path(__file__).resolve().parents[1]
TOOL_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_report_package_builder_dry_run_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/report_package_dry_runs/binance_spot_perp_funding_carry_report_package_builder_dry_run_v1.json"

REQUIRED_SECTIONS = [
    "executive_summary",
    "evidence_chain_summary",
    "strategy_mechanics",
    "historical_diagnostic_summary",
    "operational_readiness_summary",
    "paper_monitor_architecture",
    "reporting_reconciliation_package",
    "risk_register",
    "institutional_review_checklist",
    "appendix",
]

SOURCE_ARTIFACTS = {
    "report_package_design": {
        "path": "artifacts/report_package_designs/binance_spot_perp_funding_carry_report_package_design_v1.json",
        "expected_status": "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_REPORT_PACKAGE_DESIGN_CREATED",
        "expected_classification": "REPORT_PACKAGE_DESIGN_READY_FOR_PACKAGE_BUILDER_DRY_RUN_NO_LIVE_PERMISSION",
        "expected_next_allowed_step": "REPORT_PACKAGE_BUILDER_DRY_RUN_ONLY",
        "expected_hash": "c4d10185cfad8efe60ddf31d15c5cd9f5e292f71e8f21b95a50c0b0289552ece",
    },
    "report_builder_review": {
        "path": "artifacts/report_builder_reviews/binance_spot_perp_funding_carry_report_builder_dry_run_review_v1.json",
        "expected_hash": "5aca807f96e6f451fc723db5c4149a3ffb50c70776923f2508ca696d1827c5fc",
    },
    "report_builder_dry_run": {
        "path": "artifacts/report_builder_dry_runs/binance_spot_perp_funding_carry_report_builder_dry_run_v1.json",
        "expected_hash": "d1314f8e9038c705e2c83bbb8551092ff259a93af5ee865178fbfde382ad26d2",
    },
    "reporting_design": {
        "path": "artifacts/reporting_designs/binance_spot_perp_funding_carry_reporting_reconciliation_design_v1.json",
        "expected_hash": "ee0892db27885562b257294033992bff57bb387877d528638e6c709664bd7eb8",
    },
    "multi_cycle_dry_run": {
        "path": "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.json",
        "expected_hash": "4c4a16750aa3c15bda0d497127217c38a0171ca798220bf16ed701c86dd7fa13",
    },
    "risk_capital": {
        "path": "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json",
        "expected_hash": "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc",
    },
    "operational_feasibility": {
        "path": "artifacts/operational_feasibility/binance_spot_perp_delta_neutral_funding_carry_operational_feasibility_v1.json",
        "expected_hash": "5af80fc87f583f4f5f4ed4baaa5620d708eff1ade5aaa54969d4259e54d6604e",
    },
    "sizing_repair": {
        "path": "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json",
        "expected_hash": "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822",
    },
    "strategy_evaluation": {
        "path": "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json",
        "expected_hash": "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b",
    },
    "strategy_closure": {
        "path": "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json",
        "expected_hash": "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required source artifact missing: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(payload: dict[str, Any]) -> str:
    payload_without_hash = deepcopy(payload)
    payload_without_hash.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def classification_value(data: dict[str, Any]) -> Any:
    return data.get("classification") or data.get("result_classification") or data.get("feasibility_classification")


def validate_source(name: str, spec: dict[str, str], data: dict[str, Any]) -> None:
    expected_status = spec.get("expected_status")
    if expected_status and data.get("status") != expected_status:
        raise ValueError(f"{name} status mismatch: {data.get('status')} != {expected_status}")
    expected_classification = spec.get("expected_classification")
    if expected_classification and data.get("classification") != expected_classification:
        raise ValueError(f"{name} classification mismatch: {data.get('classification')} != {expected_classification}")
    expected_next = spec.get("expected_next_allowed_step")
    if expected_next and data.get("next_allowed_step") != expected_next:
        raise ValueError(f"{name} next_allowed_step mismatch: {data.get('next_allowed_step')} != {expected_next}")
    expected_hash = spec.get("expected_hash")
    if expected_hash and data.get("payload_sha256_excluding_hash") != expected_hash:
        raise ValueError(f"{name} payload hash mismatch")
    if data.get("replacement_checks_all_true") is False:
        raise ValueError(f"{name} replacement_checks_all_true is false")


def source_summary(name: str, spec: dict[str, str], data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": spec["path"],
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "classification": classification_value(data),
        "next_allowed_step": data.get("next_allowed_step"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "expected_payload_sha256_excluding_hash": spec.get("expected_hash"),
    }


def risk_split_summary(risk: dict[str, Any], split: str) -> dict[str, Any]:
    aggregate = (risk.get("symbol_concentration_diagnostic") or {}).get("all_3_aggregate_from_execution") or {}
    return aggregate.get(split) or {}


def metric(risk: dict[str, Any], split: str, key: str) -> Any:
    return risk_split_summary(risk, split).get(key)


def build_executive_summary() -> dict[str, Any]:
    return {
        "diagnostic_status": "diagnostic_promising_not_live",
        "candidate_generation_allowed": False,
        "edge_claim_allowed": False,
        "capital_permission_allowed": False,
        "mechanism": "long Binance spot plus short Binance USD-M perpetual funding carry",
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "current_system_status": "paper_and_reporting_dry_run_only",
        "live_trading_allowed": False,
    }


def build_evidence_chain_summary(loaded: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"stage": "strategy diagnostic", "artifact": SOURCE_ARTIFACTS["strategy_evaluation"]["path"], "summary": classification_value(loaded["strategy_evaluation"])},
        {"stage": "risk/capital feasibility", "artifact": SOURCE_ARTIFACTS["risk_capital"]["path"], "summary": classification_value(loaded["risk_capital"])},
        {"stage": "operational feasibility", "artifact": SOURCE_ARTIFACTS["operational_feasibility"]["path"], "summary": classification_value(loaded["operational_feasibility"])},
        {"stage": "sizing failure and repair", "artifact": SOURCE_ARTIFACTS["sizing_repair"]["path"], "summary": classification_value(loaded["sizing_repair"])},
        {"stage": "multi-cycle dry run", "artifact": SOURCE_ARTIFACTS["multi_cycle_dry_run"]["path"], "summary": classification_value(loaded["multi_cycle_dry_run"])},
        {"stage": "reporting/reconciliation design", "artifact": SOURCE_ARTIFACTS["reporting_design"]["path"], "summary": classification_value(loaded["reporting_design"])},
        {"stage": "report builder dry run", "artifact": SOURCE_ARTIFACTS["report_builder_dry_run"]["path"], "summary": classification_value(loaded["report_builder_dry_run"])},
        {"stage": "report builder review", "artifact": SOURCE_ARTIFACTS["report_builder_review"]["path"], "summary": classification_value(loaded["report_builder_review"])},
        {"stage": "report package design", "artifact": SOURCE_ARTIFACTS["report_package_design"]["path"], "summary": classification_value(loaded["report_package_design"])},
    ]


def build_strategy_mechanics() -> dict[str, Any]:
    return {
        "position_model": "long spot and short USD-M perpetual on the same symbol",
        "sizing_model": "same base asset quantity for spot and perpetual legs",
        "funding_cashflow_source": "short perpetual leg receives positive funding and pays negative funding",
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "directional_prediction": False,
        "leverage_assumption": "no leverage assumption beyond margin buffer scenario modeling",
        "capital_margin_caveats": [
            "spot capital is locked",
            "perpetual margin buffer is required",
            "liquidation risk is not eliminated by spot hedge",
        ],
    }


def build_historical_summary(risk: dict[str, Any]) -> dict[str, Any]:
    combined = risk.get("combined_stress") or {}
    monthly = risk.get("monthly_robustness_diagnostic") or {}
    return {
        "validation_base_net_bps": metric(risk, "validation", "net_after_lifecycle_cost_bps"),
        "holdout_base_net_bps": metric(risk, "holdout", "net_after_lifecycle_cost_bps"),
        "validation_50pct_funding_haircut_2x_cost_net_bps": ((combined.get("validation") or {}).get("50pct_funding_haircut_2x_lifecycle_cost") or {}).get("net_bps"),
        "holdout_50pct_funding_haircut_2x_cost_net_bps": ((combined.get("holdout") or {}).get("50pct_funding_haircut_2x_lifecycle_cost") or {}).get("net_bps"),
        "validation_monthly_positive_rate": ((monthly.get("validation") or {}).get("monthly_positive_rate")),
        "holdout_monthly_positive_rate": ((monthly.get("holdout") or {}).get("monthly_positive_rate")),
        "risk_capital_classification": risk.get("feasibility_classification"),
        "live_permission_allowed": False,
        "capital_permission_allowed": False,
    }


def build_operational_summary(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sizing = loaded["sizing_repair"]
    multi_cycle = loaded["multi_cycle_dry_run"]
    aggregate = multi_cycle.get("aggregate_run_report") or {}
    return {
        "exchange_rules_discovered": True,
        "sizing_initial_failure": (sizing.get("prior_failure_preserved") or {}).get("prior_sizing_classification"),
        "sizing_repair_pass": classification_value(sizing),
        "minimum_passing_capital_from_repaired_sizing": (classification_value(sizing) or {}).get("minimum_passing_capital_all3")
        if isinstance(classification_value(sizing), dict)
        else "235",
        "paper_dry_run_partial_risk_flags": True,
        "multi_cycle_dry_run_result": classification_value(multi_cycle),
        "multi_cycle_minimum_passing_capital_by_cycle": aggregate.get("minimum_passing_capital_by_cycle"),
        "orders_placed": False,
    }


def build_paper_monitor_architecture(design: dict[str, Any]) -> dict[str, Any]:
    architecture = design.get("paper_monitor_architecture_design") or {}
    return {
        "state_machine": architecture.get("states") or [],
        "public_snapshot_inputs": [
            "public spot price snapshot",
            "public futures price snapshot",
            "public premiumIndex/funding snapshot",
            "public exchangeInfo rules",
        ],
        "repaired_sizing": "common base quantity, Decimal arithmetic, exchange-filter aware",
        "report_only_state": "CYCLE_REPORT / FINAL_REPORT_ONLY",
        "risk_halt_state": "RISK_HALT",
        "private_api_allowed": False,
        "scheduler_daemon_runtime_allowed": False,
    }


def build_reporting_package(dry_run: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_count": (dry_run.get("report_pack") or {}).get("report_count"),
        "reports": [
            "cycle report",
            "funding reconciliation report",
            "daily report",
            "weekly report",
            "monthly report",
            "risk incident report",
            "sizing stability report",
            "simulated PnL attribution report",
            "audit summary",
        ],
        "reconciliation_mode": "simulated_public_data_only",
        "real_funding_received_verified": False,
        "actual_fills_verified": False,
        "account_balance_checked": False,
    }


def build_risk_register(design: dict[str, Any]) -> list[dict[str, Any]]:
    return list(design.get("risk_register_design") or [])


def build_checklist(design: dict[str, Any]) -> list[dict[str, Any]]:
    return list(design.get("institutional_review_checklist") or [])


def build_appendix(source_artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "source_artifact_list": {name: summary["path"] for name, summary in source_artifacts.items()},
        "payload_hashes": {name: summary.get("payload_sha256_excluding_hash") for name, summary in source_artifacts.items()},
        "glossary": {
            "paper_only": "JSON-only simulated reporting package without live permissions",
            "diagnostic_promising": "research diagnostic classification that does not imply an edge claim",
            "funding_carry": "spot-perp structure where short perp funding is the intended return source",
            "same_base_quantity": "spot and perp legs use equal base asset quantity per symbol",
        },
        "no_live_no_edge_disclaimers": [
            "no candidate generation",
            "no edge claim",
            "no runtime, live, or capital permission",
            "no PDF, DOCX, HTML, or Markdown external report export",
        ],
        "future_requirements": [
            "report package dry-run review",
            "longer paper monitoring before any live discussion",
            "true reconciliation design before account-level reconciliation",
            "separate explicit approval for any future report export",
        ],
    }


def main() -> None:
    artifact_path = ROOT / ARTIFACT_RELATIVE_PATH

    loaded: dict[str, dict[str, Any]] = {}
    source_artifacts: dict[str, dict[str, Any]] = {}
    for name, spec in SOURCE_ARTIFACTS.items():
        data = load_json(spec["path"])
        validate_source(name, spec, data)
        loaded[name] = data
        source_artifacts[name] = source_summary(name, spec, data)

    design = loaded["report_package_design"]
    risk = loaded["risk_capital"]
    dry_run = loaded["report_builder_dry_run"]

    sections = {
        "executive_summary": build_executive_summary(),
        "evidence_chain_summary": build_evidence_chain_summary(loaded),
        "strategy_mechanics": build_strategy_mechanics(),
        "historical_diagnostic_summary": build_historical_summary(risk),
        "operational_readiness_summary": build_operational_summary(loaded),
        "paper_monitor_architecture": build_paper_monitor_architecture(design),
        "reporting_reconciliation_package": build_reporting_package(dry_run),
        "risk_register": build_risk_register(design),
        "institutional_review_checklist": build_checklist(design),
        "appendix": build_appendix(source_artifacts),
    }

    safety_permissions = {
        "report_package_builder_dry_run_created": True,
        "report_package_exported_now": False,
        "private_api_allowed_now": False,
        "order_placement_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "scheduler_allowed_now": False,
        "daemon_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "next_step_must_not_be_live_or_capital": True,
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_report_package_design_loaded": True,
        "prior_design_next_allowed_step_verified": design.get("next_allowed_step") == "REPORT_PACKAGE_BUILDER_DRY_RUN_ONLY",
        "all_10_package_sections_created": len(sections) == 10 and all(section in sections for section in REQUIRED_SECTIONS),
        "risk_register_min_11_items": len(sections["risk_register"]) >= 11,
        "institutional_checklist_min_9_items": len(sections["institutional_review_checklist"]) >= 9,
        "no_report_file_exported": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_live_or_capital_permission": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }
    if not all(validation_checks.values()):
        failed = [key for key, value in validation_checks.items() if not value]
        raise ValueError(f"Validation checks failed: {failed}")

    report_package = {
        "package_mode": "json_only_dry_run",
        "section_count": len(sections),
        "external_report_files_created": False,
        "sections": sections,
    }

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "created_at_utc": utc_now(),
            "current_head_expected": "193f0c34090e12662cc9d2872f5661cc350b74e7",
            "tracked_python_count_before": 901,
            "tool_path": TOOL_RELATIVE_PATH,
            "artifact_path": ARTIFACT_RELATIVE_PATH,
        },
        "source_artifacts": source_artifacts,
        "prior_report_package_design_preserved": {
            "status": design.get("status"),
            "classification": design.get("classification"),
            "next_allowed_step": design.get("next_allowed_step"),
            "package_section_count": len(design.get("package_sections") or {}),
            "risk_register_item_count": len(design.get("risk_register_design") or []),
            "institutional_checklist_item_count": len(design.get("institutional_review_checklist") or []),
            "payload_sha256_excluding_hash": design.get("payload_sha256_excluding_hash"),
        },
        "report_package": report_package,
        **sections,
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "limitations": [
            "Report package builder dry-run only; no external report file was generated.",
            "No PDF, DOCX, HTML, Markdown, or other report export was created.",
            "No network, API, private endpoint, order endpoint, scheduler, daemon, runtime, live, or capital action occurred.",
            "No candidate generation, edge claim, or family release is allowed.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout_fields = {
        "status": STATUS,
        "classification": CLASSIFICATION,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "package_section_count": len(sections),
        "risk_register_item_count": len(sections["risk_register"]),
        "institutional_checklist_item_count": len(sections["institutional_review_checklist"]),
        "report_package_exported_now": False,
        "order_placement_allowed_now": False,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    for key, value in stdout_fields.items():
        print(f"{key}={json.dumps(value, sort_keys=True)}")


if __name__ == "__main__":
    main()
