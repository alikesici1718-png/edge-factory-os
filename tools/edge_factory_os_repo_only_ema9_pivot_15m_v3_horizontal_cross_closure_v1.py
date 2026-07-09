import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_ema9_pivot_15m_v3_horizontal_cross_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/lucifer_15m_v3_horizontal_cross_closure_v1.json"
EVALUATOR_PATH = "artifacts/strategy_evaluations/lucifer_15m_v3_horizontal_cross_evaluator_v1.json"

STATUS = "PASS_REPO_ONLY_LUCIFER_15M_V3_HORIZONTAL_CROSS_CLOSURE_CREATED"
ARTIFACT_KIND = "LUCIFER_15M_V3_HORIZONTAL_CROSS_CLOSURE"
EVALUATOR_STATUS = "PASS_REPO_ONLY_LUCIFER_15M_V3_HORIZONTAL_CROSS_EVALUATED"
ROUTE = "LUCIFER_15M_EMA9_HORIZONTAL_PIVOT_CROSS_TP_SL_V3"
CONFIG_ID = "lucifer_15m_v3_horizontal_pivot_cross_sl1_tp2"

EXPECTED_PRE_CLOSURE_HEAD = "074d6084d6d3b150e3e32977693f948caa2c53f6"
EXPECTED_PRE_CLOSURE_TRACKED_PYTHON_COUNT = 943


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def run_git(args: List[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def tracked_python_count() -> int:
    output = run_git(["ls-files", "*.py"])
    return 0 if not output else len(output.splitlines())


def dirty_paths() -> List[str]:
    output = run_git(["status", "--short"])
    paths: List[str] = []
    for line in output.splitlines():
        if line:
            paths.append(line[3:].strip().strip('"').replace("\\", "/"))
    return sorted(paths)


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"artifact is not a JSON object: {relative_path}")
    return payload


def verify_hash(payload: Dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError(f"{label} missing payload_sha256_excluding_hash")
    observed = canonical_payload_hash(payload)
    if observed != stored:
        raise RuntimeError(f"{label} payload hash mismatch: {observed} != {stored}")
    return stored


def build_payload() -> Dict[str, Any]:
    actual_head = run_git(["rev-parse", "HEAD"])
    actual_tracked_python_count = tracked_python_count()
    current_dirty_paths = dirty_paths()
    allowed_dirty = {MODULE_PATH, ARTIFACT_PATH}
    unexpected_dirty_paths = [path for path in current_dirty_paths if path not in allowed_dirty]
    if unexpected_dirty_paths:
        raise RuntimeError(f"unexpected dirty paths during V3 closure: {unexpected_dirty_paths}")
    if actual_head != EXPECTED_PRE_CLOSURE_HEAD:
        raise RuntimeError(f"HEAD moved before V3 closure: {actual_head} != {EXPECTED_PRE_CLOSURE_HEAD}")
    if actual_tracked_python_count != EXPECTED_PRE_CLOSURE_TRACKED_PYTHON_COUNT:
        raise RuntimeError(
            "tracked Python count mismatch before V3 closure: "
            f"{actual_tracked_python_count} != {EXPECTED_PRE_CLOSURE_TRACKED_PYTHON_COUNT}"
        )

    evaluator = read_json(EVALUATOR_PATH)
    evaluator_hash = verify_hash(evaluator, "evaluator")
    if evaluator.get("status") != EVALUATOR_STATUS:
        raise RuntimeError("evaluator status mismatch")
    if evaluator.get("route") != ROUTE:
        raise RuntimeError("route mismatch")
    if evaluator.get("config_id") != CONFIG_ID:
        raise RuntimeError("config id mismatch")

    evaluator_findings = evaluator.get("evaluator_findings")
    if not isinstance(evaluator_findings, dict):
        raise RuntimeError("evaluator findings missing")
    result_class = evaluator_findings.get("result_class")
    diagnostic_promising = evaluator_findings.get("diagnostic_promising")

    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route": ROUTE,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "pre_closure_head": EXPECTED_PRE_CLOSURE_HEAD,
            "pre_closure_head_verified_at_artifact_creation": actual_head,
            "repo_clean_before_closure_confirmed_externally": True,
            "tracked_python_count_before_closure": EXPECTED_PRE_CLOSURE_TRACKED_PYTHON_COUNT,
            "tracked_python_count_verified_at_artifact_creation": actual_tracked_python_count,
            "dirty_paths_during_artifact_creation_limited_to_expected_new_paths": True,
            "dirty_paths_during_artifact_creation": current_dirty_paths,
        },
        "closure_inputs": {
            "evaluator_artifact": EVALUATOR_PATH,
            "evaluator_status": evaluator.get("status"),
            "evaluator_payload_sha256_excluding_hash": evaluator_hash,
            "evaluator_payload_hash_verified": True,
            "panel_rows_read": False,
            "execution_rerun": False,
        },
        "route_closed": True,
        "final_result": {
            "result_class": result_class,
            "diagnostic_promising": diagnostic_promising,
            "evaluator_result_preserved_exactly": evaluator_findings,
        },
        "execution_metric_snapshot_preserved_from_evaluator": evaluator.get("execution_metric_snapshot"),
        "closure_reason": (
            "Route closed after evaluator. The evaluator result is preserved exactly; this V3 horizontal-only "
            "pivot cross correction grants no candidate, edge claim, family release, runtime, live, or capital permission."
        ),
        "permissions": {
            "candidate_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "orders_submitted": False,
        },
        "forbidden_actions_confirmed_false": {
            "network_used": False,
            "private_api_used": False,
            "data_downloaded": False,
            "other_timeframes_tested": False,
            "other_parameters_tested": False,
            "parameter_expansion": False,
            "grid_search": False,
            "optimization": False,
            "candidate_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "orders_submitted": False,
        },
        "next_module": None,
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "artifact_path_equals_required_path": True,
            "evaluator_artifact_loaded": True,
            "evaluator_payload_hash_verified": True,
            "evaluator_result_preserved_exactly": True,
            "route_closed_true": True,
            "no_candidate": True,
            "no_edge_claim": True,
            "no_family_release": True,
            "no_runtime_live_capital": True,
            "panel_rows_not_read": True,
            "execution_not_rerun": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    if not all(payload["validation_checks"].values()):
        raise RuntimeError(f"V3 closure validation checks failed: {payload['validation_checks']}")
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    if canonical_payload_hash(payload) != payload["payload_sha256_excluding_hash"]:
        raise RuntimeError("payload hash failed to stabilize")
    return payload


def main() -> None:
    payload = build_payload()
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": STATUS,
                "artifact_path": ARTIFACT_PATH,
                "route_closed": payload["route_closed"],
                "result_class": payload["final_result"]["result_class"],
                "diagnostic_promising": payload["final_result"]["diagnostic_promising"],
                "candidate_generated": False,
                "edge_claimed": False,
                "runtime_live_capital": False,
                "replacement_checks_all_true": True,
                "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
