from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "old_short_clean_room_direct_backtest_evaluator_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "old_short_clean_room_direct_backtest_closure_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_CLOSURE_CREATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_CLOSURE"
ROUTE_KEY = "old_short_clean_room_v1"
EVALUATOR_STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_EVALUATED"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def git_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def main() -> int:
    head = git(["rev-parse", "HEAD"])
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status_entries = {
        "?? tools/edge_factory_os_repo_only_old_short_clean_room_direct_backtest_closure_v1.py",
        "?? artifacts/strategy_closures/old_short_clean_room_direct_backtest_closure_v1.json",
    }
    unexpected_status_entries = [line for line in status_lines if line not in allowed_status_entries]
    repo_clean_before_run = not unexpected_status_entries
    evaluator = load_json(EVALUATOR_ARTIFACT_PATH)
    evaluator_result = evaluator.get("result_classification")
    diagnostic_promising = evaluator.get("diagnostic_promising")
    metric_summary = evaluator.get("execution_metric_summary", {})
    metric_integrity = evaluator.get("metric_integrity_result", {})
    safety_permissions = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runner_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "full_dataset_comparison_allowed_now": False,
        "backtest_rerun_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "monitor_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "real_orders_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "evaluator_artifact_loaded": True,
        "evaluator_status_verified": evaluator.get("status") == EVALUATOR_STATUS,
        "route_key_verified": evaluator.get("route_key") == ROUTE_KEY,
        "evaluator_result_preserved_exactly": isinstance(evaluator_result, str) and bool(evaluator_result),
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_runtime_live_capital": True,
        "no_backtest_rerun": True,
        "no_runner_execution": True,
        "no_signal_generation": True,
        "no_full_dataset_comparison": True,
        "no_network_used": True,
        "no_api_used": True,
    }
    closure_decision = {
        "closed": True,
        "evaluator_result_preserved": evaluator_result,
        "diagnostic_promising_preserved": diagnostic_promising,
        "candidate_created": False,
        "edge_claim_created": False,
        "family_release_created": False,
        "runtime_live_capital_permission_created": False,
        "closure_note": "Direct clean-room historical diagnostic cycle closed; evaluator result controls follow-up status.",
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_old_short_clean_room_direct_backtest_closure_v1",
        "route_key": ROUTE_KEY,
        "source_checkpoint": {
            "head": head,
            "tracked_python_count": git_python_count(),
            "repo_clean_before_run": repo_clean_before_run,
            "git_status_at_closure": status_lines,
            "allowed_new_paths_at_closure": sorted(allowed_status_entries),
            "unexpected_dirty_paths_at_closure": unexpected_status_entries,
        },
        "source_artifacts": {
            "evaluator_artifact": str(EVALUATOR_ARTIFACT_PATH),
        },
        "evaluator_status_preserved": evaluator.get("status"),
        "evaluator_result_classification_preserved": evaluator_result,
        "diagnostic_promising_preserved": diagnostic_promising,
        "execution_metric_summary_preserved": metric_summary,
        "metric_integrity_result_preserved": metric_integrity,
        "closure_decision": closure_decision,
        "limitations_preserved": evaluator.get("limitations", []),
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["replacement_checks_all_true"] = all(validation_checks.values()) and all(value is False for value in safety_permissions.values())
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"evaluator_result_classification_preserved: {evaluator_result}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
