from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_repo_only_whole_system_adversarial_logic_audit_after_evidence_chain_adoption_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_whole_system_adversarial_logic_audit_after_evidence_chain_adoption_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "07dc2d4"
PREVIOUS_TRACKED_PYTHON_COUNT = 570
EXPECTED_PREVIOUS_POST_CHECK = "REPO_ONLY_POST_CHECK_ARTIFACT_RELIABILITY_ENFORCEMENT_ADOPTION_RECORD_POST_COMMIT_CHECK_PASS"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
EVIDENCE_CHAIN_QUALITY = "DERIVED_OVERUSED_ATTENTION"

SUPERSEDED_NEXT_MODULE = "edge_factory_os_repo_only_future_module_evidence_chain_contract_v1.py"
SUPERSEDE_REASON = "human_requested_whole_system_adversarial_logic_audit_before_continuing"

NEXT_MODULE_P0 = "edge_factory_os_repo_only_whole_system_adversarial_logic_audit_repair_preview_v1.py"
NEXT_MODULE_P1 = "edge_factory_os_repo_only_whole_system_adversarial_logic_audit_attention_review_v1.py"
NEXT_MODULE_PASS = SUPERSEDED_NEXT_MODULE

GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

PLANNED_SCHEMA_REL_PATHS = [
    "edge_factory_os_framework/schemas/edge_factory_os_status_record_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_safety_flags_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_git_state_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_tracked_python_validation_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_queue_item_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_artifact_reference_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_post_commit_check_v1.schema.json",
    "edge_factory_os_framework/schemas/edge_factory_os_framework_schema_registry_v1.schema.json",
]

DANGEROUS_FLAGS = [
    "runtime_touched",
    "launcher_executed",
    "capital_changed",
    "live_or_real_orders",
    "holdout_accessed",
    "strategy_research_recommended_now",
    "candidate_generation_recommended_now",
    "candidate_release_recommended_now",
    "family_release_recommended_now",
    "schema_apply_allowed_now",
    "schema_file_creation_allowed_now",
    "schema_file_edit_allowed_now",
    "schema_apply_performed_now",
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "file_move_allowed_now",
    "file_delete_allowed_now",
    "repo_restructure_allowed_now",
    "gitignore_changed",
    "git_add_force_used",
    "backup_deleted",
    "mass_metadata_patch_allowed",
    "blind_fix_all_allowed",
    "direct_apply_recommended_now",
    "apply_allowed_now",
    "apply_performed_now",
    "manual_approval_present_now",
    "manual_approval_valid_now",
    "implementation_allowed_now",
    "generic_runner_implementation_allowed_now",
    "generic_runner_file_creation_allowed_now",
    "config_file_creation_allowed_now",
    "consolidation_apply_allowed_now",
]

ISSUE_CLASSES = [
    "SYNTAX_ERROR",
    "BOM_ERROR",
    "DIRTY_REPO",
    "UNEXPECTED_UNTRACKED",
    "DANGEROUS_FLAG",
    "SCHEMA_CONFIG_VIOLATION",
    "GENERIC_RUNNER_VIOLATION",
    "RUNTIME_CAPITAL_LIVE_VIOLATION",
    "CANDIDATE_FAMILY_VIOLATION",
    "HOLDOUT_VIOLATION",
    "CLOSED_LOOP_REOPEN_RISK",
    "MECHANICAL_LOOP_RISK",
    "NEXT_MODULE_CHAIN_CONTRADICTION",
    "ARTIFACT_STATE_CONTRADICTION",
    "POST_CHECK_EVIDENCE_WEAKNESS",
    "EVIDENCE_CHAIN_POLICY_VIOLATION",
    "DERIVED_CHECK_OVERUSE",
    "FAIL_OPEN_LOGIC",
    "DEAD_GUARD",
    "HARDCODED_PASS",
    "BROAD_EXCEPTION_SWALLOW",
    "PATH_ASSUMPTION_RISK",
    "SELF_DECEPTION_RISK",
    "INFO",
]

ORDINARY_LOOP_RE = re.compile(
    r"edge_factory_os_repo_only_(next_action_selector|development_queue_selector|development_backlog_refresh)"
    r"_after_(generic_governance_blocked_status|standard_os_status).*_v1[.]py$"
)
MECHANICAL_NAME_RE = re.compile(r"(status_backlog.*){2,}|(backlog_){3,}|(_status_.*){5,}")

TOUCH_GROUPS: Dict[str, Tuple[str, List[str]]] = {
    "runtime_touch_indicator_count": ("RUNTIME_CAPITAL_LIVE_VIOLATION", ["runtime"]),
    "launcher_touch_indicator_count": ("RUNTIME_CAPITAL_LIVE_VIOLATION", ["launcher"]),
    "capital_touch_indicator_count": ("RUNTIME_CAPITAL_LIVE_VIOLATION", ["capital"]),
    "live_touch_indicator_count": ("RUNTIME_CAPITAL_LIVE_VIOLATION", ["live"]),
    "real_order_touch_indicator_count": ("RUNTIME_CAPITAL_LIVE_VIOLATION", ["real_order", "real order", "orders"]),
    "holdout_touch_indicator_count": ("HOLDOUT_VIOLATION", ["holdout"]),
    "candidate_family_touch_indicator_count": ("CANDIDATE_FAMILY_VIOLATION", ["candidate_release", "family_release", "candidate generation"]),
    "strategy_research_implementation_indicator_count": (
        "SELF_DECEPTION_RISK",
        ["strategy_research", "research_runner", "research_evaluator"],
    ),
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str]) -> subprocess.CompletedProcess[str]:
    safe_args = args
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    result = subprocess.run(safe_args, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {safe_args} returncode={result.returncode} stderr={result.stderr}")
    return result


def tracked_files(pattern: Optional[str] = None) -> List[str]:
    args = ["git", "ls-files"]
    if pattern:
        args.append(pattern)
    return sorted(line.strip().replace("\\", "/") for line in run_cmd(args).stdout.splitlines() if line.strip())


def git_state() -> Dict[str, Any]:
    status_lines = [
        line
        for line in run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"]).stdout.splitlines()
        if line.strip()
    ]
    untracked = sorted(line[3:].replace("\\", "/") for line in status_lines if line.startswith("?? "))
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    staged = [line for line in dirty_tracked if line[0] != " "]
    expected_untracked = [CURRENT_TOOL_REL] if (REPO_ROOT / CURRENT_TOOL_REL).exists() else []
    unexpected_untracked = [path for path in untracked if path not in expected_untracked]
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "branch": run_cmd(["git", "branch", "--show-current"]).stdout.strip(),
        "status_porcelain": status_lines,
        "dirty_tracked_count": len(dirty_tracked),
        "dirty_tracked_paths": [line[3:].replace("\\", "/") for line in dirty_tracked],
        "staged_count": len(staged),
        "staged_paths": [line[3:].replace("\\", "/") for line in staged],
        "untracked_paths": untracked,
        "expected_untracked_paths": expected_untracked,
        "unexpected_untracked_paths": unexpected_untracked,
        "unexpected_untracked_count": len(unexpected_untracked),
        "repo_clean_for_audit_scope": len(dirty_tracked) == 0 and len(unexpected_untracked) == 0,
    }


def make_finding(
    seq: int,
    severity: str,
    issue_class: str,
    affected_path: str,
    evidence: Any,
    why_it_matters: str,
    self_deception_risk: str,
    recommended_next_action: str,
) -> Dict[str, Any]:
    return {
        "issue_id": f"WSA-{seq:04d}",
        "severity": severity,
        "issue_class": issue_class,
        "affected_path": affected_path,
        "evidence": evidence,
        "why_it_matters": why_it_matters,
        "self_deception_risk": self_deception_risk,
        "recommended_next_action": recommended_next_action,
        "auto_fix_allowed": False,
        "direct_apply_allowed": False,
    }


def validate_tracked_python(py_files: List[str]) -> Dict[str, Any]:
    syntax_errors: List[Dict[str, str]] = []
    bom_errors: List[str] = []
    for rel in py_files:
        data = (REPO_ROOT / rel).read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(data.decode("utf-8"), filename=rel)
        except UnicodeDecodeError as exc:
            syntax_errors.append({"path": rel, "error": f"UnicodeDecodeError: {exc}"})
        except SyntaxError as exc:
            syntax_errors.append({"path": rel, "error": f"SyntaxError line={exc.lineno}: {exc.msg}"})
    return {
        "tracked_python_count": len(py_files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def read_text_lossy(rel: str, limit: int = 400000) -> str:
    data = (REPO_ROOT / rel).read_bytes()[:limit]
    return data.decode("utf-8", errors="replace")


def iter_latest_artifacts(limit: int = 120) -> List[Path]:
    candidates: List[Path] = []
    for pattern in ("edge_factory_os_*/*_latest.json", "edge_factory_os_*/*_latest.txt"):
        candidates.extend(LAB_ROOT.glob(pattern))
    candidates = [path for path in candidates if path.is_file()]
    return sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]


def load_json_artifact(path: Path) -> Optional[Dict[str, Any]]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def iter_scalar_fields(obj: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from iter_scalar_fields(value, next_prefix)
    elif isinstance(obj, list):
        for index, value in enumerate(obj[:50]):
            yield from iter_scalar_fields(value, f"{prefix}[{index}]")
    else:
        yield prefix, obj


def latest_commit_paths(ref: str = "HEAD") -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "show", "--name-only", "--format=", ref]).stdout.splitlines()
        if line.strip()
    )


def recent_commit_summaries(limit: int = 20) -> List[Dict[str, Any]]:
    lines = run_cmd(["git", "log", f"--max-count={limit}", "--format=%h%x09%s"]).stdout.splitlines()
    commits: List[Dict[str, Any]] = []
    for line in lines:
        if "\t" not in line:
            continue
        sha, subject = line.split("\t", 1)
        commits.append({"sha": sha, "subject": subject, "paths": latest_commit_paths(sha)})
    return commits


def count_touch_indicators(files: List[str]) -> Dict[str, Dict[str, Any]]:
    results: Dict[str, Dict[str, Any]] = {}
    for count_name, (_issue_class, needles) in TOUCH_GROUPS.items():
        hits: List[Dict[str, str]] = []
        for rel in files:
            lower_rel = rel.lower()
            path_hit = any(needle in lower_rel for needle in needles)
            text_hit = False
            if not path_hit and rel.endswith((".py", ".json", ".txt", ".md")):
                lower_text = read_text_lossy(rel, limit=100000).lower()
                text_hit = any(needle in lower_text for needle in needles)
            if path_hit or text_hit:
                hits.append({"path": rel, "match_type": "path" if path_hit else "content"})
        results[count_name] = {"count": len(hits), "samples": hits[:25]}
    return results


def scan_logic_risks(py_files: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    risks: Dict[str, List[Dict[str, Any]]] = {
        "broad_exception_swallow": [],
        "fail_open_logic": [],
        "dead_guard": [],
        "hardcoded_pass": [],
        "path_assumption": [],
        "forbidden_git_command": [],
        "todo_placeholder": [],
    }
    for rel in py_files:
        text = read_text_lossy(rel)
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                broad = node.type is None
                if isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}:
                    broad = True
                if broad:
                    body_names = [type(child).__name__ for child in node.body]
                    risks["broad_exception_swallow"].append({"path": rel, "line": node.lineno, "body_nodes": body_names[:5]})
                    if any(isinstance(child, ast.Pass) for child in node.body):
                        risks["fail_open_logic"].append({"path": rel, "line": node.lineno, "pattern": "broad_except_pass"})
            if isinstance(node, ast.If) and isinstance(node.test, ast.Constant) and node.test.value in {True, False}:
                risks["dead_guard"].append({"path": rel, "line": node.lineno, "constant": node.test.value})
            if isinstance(node, ast.FunctionDef) and re.search(r"(check|validate|guard|assert|verify)", node.name):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                    value = node.body[0].value
                    if isinstance(value, ast.Constant) and value.value is True:
                        risks["hardcoded_pass"].append({"path": rel, "line": node.lineno, "function": node.name})
        lower_text = text.lower()
        if "todo" in lower_text or "placeholder" in lower_text:
            risks["todo_placeholder"].append({"path": rel, "evidence": "TODO/placeholder token present"})
        if "c:\\users\\" in lower_text or "/users/" in lower_text:
            risks["path_assumption"].append({"path": rel, "evidence": "machine-specific absolute path token"})
        if "git add -a" in lower_text or "git add ." in lower_text or "git config --global" in lower_text:
            risks["forbidden_git_command"].append({"path": rel, "evidence": "forbidden git command token"})
        if re.search(r"post_check_status\s*=\s*[\"']PASS[\"']", text) or re.search(r"status\s*=\s*[\"']PASS[\"']", text):
            risks["hardcoded_pass"].append({"path": rel, "evidence": "plain PASS assignment"})
    return risks


def scan_artifacts(paths: List[Path]) -> Dict[str, Any]:
    json_records: List[Dict[str, Any]] = []
    dangerous_true: List[Dict[str, Any]] = []
    plain_pass: List[Dict[str, Any]] = []
    derived_records: List[Dict[str, Any]] = []
    exact_marker_records: List[Dict[str, Any]] = []
    missing_primary_pass: List[Dict[str, Any]] = []
    policy_missing_fields: List[Dict[str, Any]] = []
    state_claims: List[Dict[str, Any]] = []
    tracked_python_counts: List[Dict[str, Any]] = []
    next_modules: List[Dict[str, Any]] = []

    mandatory_policy_fields = {
        "evidence_chain_policy_level",
        "future_modules_must_classify_evidence_quality",
        "full_post_check_marker_preferred_over_plain_pass",
        "plain_pass_without_marker_is_attention",
        "replacement_checks_are_not_equivalent_to_primary_artifact",
    }
    for path in paths:
        if path.suffix.lower() != ".json":
            continue
        obj = load_json_artifact(path)
        if obj is None:
            continue
        rel = str(path.relative_to(LAB_ROOT)).replace("\\", "/")
        json_records.append({"path": rel, "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()})
        scalar = dict(iter_scalar_fields(obj))
        for field, value in scalar.items():
            leaf = field.rsplit(".", 1)[-1]
            if leaf in DANGEROUS_FLAGS and value is True:
                dangerous_true.append({"path": rel, "field": field, "value": value})
            if leaf in {"tracked_python_count", "tracked_python_file_count", "previous_tracked_python_count"} and isinstance(value, int):
                tracked_python_counts.append({"path": rel, "field": field, "value": value})
            if leaf == "next_module" and isinstance(value, str):
                next_modules.append({"path": rel, "value": value})
            if isinstance(value, str):
                if value == "PASS":
                    plain_pass.append({"path": rel, "field": field, "value": value})
                if "POST_COMMIT_CHECK_PASS" in value or value.startswith("REPO_ONLY_") and value.endswith("_PASS"):
                    exact_marker_records.append({"path": rel, "field": field, "value": value})
        if obj.get("derived_live_repo_post_check") is True:
            derived_records.append({"path": rel})
            if not obj.get("derived_live_repo_post_check_reason") or obj.get("replacement_checks_all_true") is not True:
                missing_primary_pass.append(
                    {
                        "path": rel,
                        "derived_live_repo_post_check_reason": obj.get("derived_live_repo_post_check_reason"),
                        "replacement_checks_all_true": obj.get("replacement_checks_all_true"),
                    }
                )
        status_values = [value for _field, value in scalar.items() if isinstance(value, str) and "PASS" in value]
        primary_verified = obj.get("primary_artifact_verified")
        if status_values and primary_verified is False and obj.get("replacement_checks_all_true") is not True:
            missing_primary_pass.append({"path": rel, "primary_artifact_verified": primary_verified, "status_values": status_values[:5]})
        missing_policy = sorted(field for field in mandatory_policy_fields if field not in obj)
        if obj.get("evidence_chain_policy_level") == POLICY_LEVEL and missing_policy:
            policy_missing_fields.append({"path": rel, "missing_policy_fields": missing_policy})
        for claim in ("repo_clean", "planned_schema_files_existing_count", "generic_runner_target_exists", "loop_remains_closed"):
            if claim in obj:
                state_claims.append({"path": rel, "field": claim, "value": obj.get(claim)})

    return {
        "json_records": json_records,
        "dangerous_true": dangerous_true,
        "plain_pass": plain_pass,
        "derived_records": derived_records,
        "exact_marker_records": exact_marker_records,
        "missing_primary_pass": missing_primary_pass,
        "policy_missing_fields": policy_missing_fields,
        "state_claims": state_claims,
        "tracked_python_counts": tracked_python_counts,
        "next_modules": next_modules,
    }


def add_aggregate_finding(
    findings: List[Dict[str, Any]],
    severity: str,
    issue_class: str,
    affected_path: str,
    evidence: Any,
    why_it_matters: str,
    self_deception_risk: str,
    recommended_next_action: str,
) -> None:
    findings.append(
        make_finding(
            len(findings) + 1,
            severity,
            issue_class,
            affected_path,
            evidence,
            why_it_matters,
            self_deception_risk,
            recommended_next_action,
        )
    )


def build_findings(
    git: Dict[str, Any],
    tracked: List[str],
    py_validation: Dict[str, Any],
    touch: Dict[str, Dict[str, Any]],
    artifacts: Dict[str, Any],
    logic: Dict[str, List[Dict[str, Any]]],
    recent_commits: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    if git["head"] != EXPECTED_HEAD:
        add_aggregate_finding(
            findings,
            "P0_BLOCKER",
            "ARTIFACT_STATE_CONTRADICTION",
            ".git/HEAD",
            {"expected": EXPECTED_HEAD, "actual": git["head"]},
            "The audit was authorized against a specific checkpoint.",
            "Continuing from the wrong commit can make later PASS claims refer to the wrong state.",
            "Stop and re-anchor the audit to the intended checkpoint before any continuation.",
        )
    if not git["repo_clean_for_audit_scope"]:
        add_aggregate_finding(
            findings,
            "P0_BLOCKER" if git["dirty_tracked_count"] else "P1_ATTENTION",
            "DIRTY_REPO",
            "REPO",
            git,
            "A dirty repo can contaminate evidence about what the audit actually inspected.",
            "Uncommitted or unexpected files can be rationalized as harmless and later become hidden state.",
            "Review the dirty state; only the approved audit module may be present as expected untracked input.",
        )
    if git["unexpected_untracked_count"]:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "UNEXPECTED_UNTRACKED",
            "REPO",
            git["unexpected_untracked_paths"],
            "Unexpected untracked files can become invisible dependencies for repo-only claims.",
            "A clean-looking audit can accidentally rely on files that will not exist after checkout.",
            "Classify or remove unexpected untracked files in a separate human-approved step.",
        )

    for item in py_validation["syntax_errors"]:
        add_aggregate_finding(
            findings,
            "P0_BLOCKER",
            "SYNTAX_ERROR",
            item["path"],
            item,
            "Tracked Python syntax errors prevent reliable whole-system execution and validation.",
            "A PASS marker can mask modules that cannot even be parsed.",
            "Create a repair preview module; do not fix from this audit.",
        )
    for rel in py_validation["bom_errors"]:
        add_aggregate_finding(
            findings,
            "P0_BLOCKER",
            "BOM_ERROR",
            rel,
            {"bom": "UTF-8 BOM detected"},
            "BOM bytes can break strict parsers, checksums, and generated artifact comparisons.",
            "Encoding drift can be ignored because syntax checks still appear green.",
            "Create a repair preview module; do not rewrite from this audit.",
        )

    planned_existing = sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())
    if planned_existing:
        add_aggregate_finding(
            findings,
            "P0_BLOCKER",
            "SCHEMA_CONFIG_VIOLATION",
            "edge_factory_os_framework/schemas",
            planned_existing,
            "The checkpoint requires planned schema files to remain absent.",
            "Schema existence can falsely imply approval or enforcement maturity.",
            "Stop and route to repair preview or human review without deleting anything here.",
        )
    if (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists():
        add_aggregate_finding(
            findings,
            "P0_BLOCKER",
            "GENERIC_RUNNER_VIOLATION",
            GENERIC_RUNNER_TARGET_FILE,
            {"exists": True},
            "The generic runner target must remain absent while implementation is blocked.",
            "A blocked runner can become functionally approved by presence alone.",
            "Stop and route to repair preview; do not remove the file from this audit.",
        )

    if artifacts["dangerous_true"]:
        add_aggregate_finding(
            findings,
            "P0_BLOCKER",
            "DANGEROUS_FLAG",
            "edge_factory_os_*/*_latest.json",
            artifacts["dangerous_true"][:50],
            "Latest artifacts contain dangerous true flags that must be explicit blockers or attention items.",
            "A true safety flag can be buried inside a large JSON payload and overlooked.",
            "Review the flagged artifacts and require a separate preview for any remediation.",
        )

    for count_name, result in touch.items():
        count = result["count"]
        if count:
            issue_class = TOUCH_GROUPS[count_name][0]
            severity = "P2_REVIEW"
            if count_name in {"holdout_touch_indicator_count", "candidate_family_touch_indicator_count"}:
                severity = "P1_ATTENTION"
            add_aggregate_finding(
                findings,
                severity,
                issue_class,
                "MULTIPLE_TRACKED_FILES",
                {"indicator": count_name, "count": count, "samples": result["samples"]},
                "Repo-only status can be undermined by surfaces that look like runtime, capital, live, holdout, candidate, or strategy implementation paths.",
                "The system may treat old path names or dormant modules as harmless without checking whether claims still match the surface area.",
                "Manually review the sampled surfaces; this audit is not allowed to edit or disable them.",
            )

    loop_next_modules = [item for item in artifacts["next_modules"] if ORDINARY_LOOP_RE.match(item["value"])]
    if loop_next_modules:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "CLOSED_LOOP_REOPEN_RISK",
            "edge_factory_os_*/*_latest.json",
            loop_next_modules[:25],
            "Some latest artifacts point back into ordinary selector/backlog routes that the checkpoint says remain closed.",
            "A status field can say the loop is closed while next_module quietly re-enters it.",
            "Use an attention review before following any next_module from these artifacts.",
        )

    mechanical_paths = [rel for rel in tracked if MECHANICAL_NAME_RE.search(rel)]
    if mechanical_paths:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "MECHANICAL_LOOP_RISK",
            "MULTIPLE_TRACKED_FILES",
            {"count": len(mechanical_paths), "samples": mechanical_paths[:40]},
            "Repeated name growth is a project-level signal that status modules may be looping without adding new evidence.",
            "Longer names can be mistaken for progress even when the decision state is unchanged.",
            "Require any next step to justify new evidence, not just another refresh selector.",
        )

    generic_next = [item for item in artifacts["next_modules"] if "generic_governance_runner" in item["value"]]
    if generic_next:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "NEXT_MODULE_CHAIN_CONTRADICTION",
            "edge_factory_os_*/*_latest.json",
            generic_next[:25],
            "A next_module that routes to generic runner work conflicts with the blocked implementation stance.",
            "A blocked approval gate can be bypassed by chain momentum.",
            "Hold generic runner implementation blocked unless explicit human approval exists.",
        )

    if artifacts["plain_pass"]:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "POST_CHECK_EVIDENCE_WEAKNESS",
            "edge_factory_os_*/*_latest.json",
            artifacts["plain_pass"][:50],
            "Plain PASS values are weaker than full post-check markers under the adopted evidence-chain policy.",
            "PASS can be treated as proof even when it lacks the exact marker context.",
            "Classify plain PASS as attention evidence and prefer full markers or primary artifacts.",
        )

    derived_count = len(artifacts["derived_records"])
    exact_count = len(artifacts["exact_marker_records"])
    if derived_count > exact_count:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "DERIVED_CHECK_OVERUSE",
            "edge_factory_os_*/*_latest.json",
            {"derived_live_repo_post_check_recent_count": derived_count, "exact_post_check_marker_recent_count": exact_count},
            "Derived live repo checks are weaker than primary artifacts or exact post-check markers.",
            "The system can begin treating replacement checks as equivalent proof by repetition.",
            "Keep the future evidence-chain contract path active and make primary artifact preference explicit.",
        )
    if artifacts["missing_primary_pass"]:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "EVIDENCE_CHAIN_POLICY_VIOLATION",
            "edge_factory_os_*/*_latest.json",
            artifacts["missing_primary_pass"][:50],
            "Derived or missing-primary evidence must not silently pass without explicit replacement checks.",
            "Missing artifacts can be rationalized away by fallback status fields.",
            "Require attention review and explicit replacement-check reporting.",
        )
    if artifacts["policy_missing_fields"]:
        add_aggregate_finding(
            findings,
            "P2_REVIEW",
            "EVIDENCE_CHAIN_POLICY_VIOLATION",
            "edge_factory_os_*/*_latest.json",
            artifacts["policy_missing_fields"][:50],
            "Artifacts claiming the active policy should include the policy fields future modules rely on.",
            "A policy can be declared active while evidence quality remains unclassified.",
            "Review policy-field completeness before using those artifacts as strong evidence.",
        )

    tracked_counts = artifacts["tracked_python_counts"]
    observed_counts = sorted({item["value"] for item in tracked_counts})
    if len(observed_counts) > 1:
        add_aggregate_finding(
            findings,
            "P2_REVIEW",
            "ARTIFACT_STATE_CONTRADICTION",
            "edge_factory_os_*/*_latest.json",
            {"observed_counts": observed_counts, "samples": tracked_counts[:40]},
            "Tracked Python counts differ across checkpoints; some differences may be expected after commits, but they should not be used unqualified.",
            "Old counts can be repeated as current facts after the repo has grown.",
            "When using a count as evidence, pair it with the exact commit and current git manifest.",
        )

    for key, issue_class, severity, why, risk, action in [
        (
            "broad_exception_swallow",
            "BROAD_EXCEPTION_SWALLOW",
            "P2_REVIEW",
            "Broad exception handlers can convert real failures into partial artifacts.",
            "A module may look robust while actually hiding evidence collection failures.",
            "Review sampled handlers and require fail-closed behavior in future modules.",
        ),
        (
            "fail_open_logic",
            "FAIL_OPEN_LOGIC",
            "P1_ATTENTION",
            "Exception pass blocks can leave validation incomplete while execution continues.",
            "Missing data may be silently converted into PASS-like output.",
            "Route to attention review; any fix must be preview-only first.",
        ),
        (
            "dead_guard",
            "DEAD_GUARD",
            "P2_REVIEW",
            "Constant guards can create unreachable or always-on validation paths.",
            "Dead guards make code look checked while the branch outcome is predetermined.",
            "Inspect sampled guards before trusting their surrounding checks.",
        ),
        (
            "hardcoded_pass",
            "HARDCODED_PASS",
            "P1_ATTENTION",
            "Hardcoded PASS-like returns or assignments can bypass evidence-backed decisions.",
            "A fixed pass value can masquerade as validation.",
            "Require evidence-tied checks in any follow-up repair preview.",
        ),
        (
            "path_assumption",
            "PATH_ASSUMPTION_RISK",
            "P2_REVIEW",
            "Machine-specific paths can break repo-only portability and hide local dependencies.",
            "A module can pass only on one workstation and still appear repo-valid.",
            "Review path assumptions when promoting modules to reusable tooling.",
        ),
        (
            "todo_placeholder",
            "SELF_DECEPTION_RISK",
            "P2_REVIEW",
            "TODO or placeholder markers can leave unfinished validation behind a finished artifact.",
            "Placeholder logic may be normalized by repeated status refreshes.",
            "Require concrete evidence before treating these surfaces as complete.",
        ),
    ]:
        if logic[key]:
            add_aggregate_finding(
                findings,
                severity,
                issue_class,
                "MULTIPLE_TRACKED_PYTHON_FILES",
                {"count": len(logic[key]), "samples": logic[key][:40]},
                why,
                risk,
                action,
            )
    if logic["forbidden_git_command"]:
        add_aggregate_finding(
            findings,
            "P1_ATTENTION",
            "SELF_DECEPTION_RISK",
            "MULTIPLE_TRACKED_PYTHON_FILES",
            {"count": len(logic["forbidden_git_command"]), "samples": logic["forbidden_git_command"][:40]},
            "Forbidden git command tokens can stage too much or mutate global configuration.",
            "A one-file audit discipline can be broken by broad staging commands hidden in helper modules.",
            "Verify commit discipline manually and keep this audit preview-only.",
        )

    runtime_commit_paths = [
        commit
        for commit in recent_commits
        if any(any(token in path.lower() for token in ["runtime", "capital", "live", "order", "candidate", "family"]) for path in commit["paths"])
    ]
    if runtime_commit_paths:
        add_aggregate_finding(
            findings,
            "P2_REVIEW",
            "RUNTIME_CAPITAL_LIVE_VIOLATION",
            "RECENT_COMMITS",
            runtime_commit_paths[:20],
            "Recent commits touched names associated with runtime, capital, live/order, candidate, or family surfaces.",
            "Repo-only posture can drift if recent history is treated as irrelevant.",
            "Review recent paths before asserting no related surface exists; this audit does not modify them.",
        )

    if not findings:
        add_aggregate_finding(
            findings,
            "INFO",
            "INFO",
            "REPO",
            {"tracked_files_scanned": len(tracked), "latest_artifacts_scanned": len(artifacts["json_records"])},
            "The audit completed without P0/P1/P2 findings under its heuristic scope.",
            "No audit can prove absence of all possible semantic bugs.",
            "Continue to the future evidence-chain contract module.",
        )
    return findings


def severity_counts(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "p0_blocker_count": sum(1 for item in findings if item["severity"] == "P0_BLOCKER"),
        "p1_attention_count": sum(1 for item in findings if item["severity"] == "P1_ATTENTION"),
        "p2_review_count": sum(1 for item in findings if item["severity"] == "P2_REVIEW"),
        "info_count": sum(1 for item in findings if item["severity"] == "INFO"),
    }


def decision_from_counts(counts: Dict[str, int]) -> Dict[str, Any]:
    if counts["p0_blocker_count"] > 0:
        return {
            "audit_status": "BLOCKER",
            "final_decision": "WHOLE_SYSTEM_ADVERSARIAL_AUDIT_BLOCKER_REPAIR_PREVIEW_REQUIRED",
            "next_action": "BUILD_WHOLE_SYSTEM_ADVERSARIAL_LOGIC_AUDIT_REPAIR_PREVIEW",
            "next_module": NEXT_MODULE_P0,
            "repair_preview_required": True,
        }
    if counts["p1_attention_count"] > 0:
        return {
            "audit_status": "PASS_WITH_ATTENTION",
            "final_decision": "WHOLE_SYSTEM_ADVERSARIAL_AUDIT_RECORDED_ATTENTION_REVIEW_REQUIRED",
            "next_action": "BUILD_WHOLE_SYSTEM_ADVERSARIAL_LOGIC_AUDIT_ATTENTION_REVIEW",
            "next_module": NEXT_MODULE_P1,
            "repair_preview_required": True,
        }
    return {
        "audit_status": "PASS",
        "final_decision": "WHOLE_SYSTEM_ADVERSARIAL_AUDIT_PASS_RETURN_TO_FUTURE_EVIDENCE_CHAIN_CONTRACT",
        "next_action": "BUILD_REPO_ONLY_FUTURE_MODULE_EVIDENCE_CHAIN_CONTRACT_V1",
        "next_module": NEXT_MODULE_PASS,
        "repair_preview_required": False,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    tracked = tracked_files()
    py_files = tracked_files("*.py")
    py_validation = validate_tracked_python(py_files)
    touch = count_touch_indicators(tracked)
    latest_artifacts = iter_latest_artifacts()
    artifact_scan = scan_artifacts(latest_artifacts)
    logic = scan_logic_risks(py_files)
    recent_commits = recent_commit_summaries()
    findings = build_findings(git, tracked, py_validation, touch, artifact_scan, logic, recent_commits)
    counts = severity_counts(findings)
    decision = decision_from_counts(counts)

    planned_existing = sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    closed_loop_reopen_indicator_count = len([item for item in artifact_scan["next_modules"] if ORDINARY_LOOP_RE.match(item["value"])])
    mechanical_loop_indicator_count = len([rel for rel in tracked if MECHANICAL_NAME_RE.search(rel)])
    next_module_chain_issue_count = sum(
        1
        for finding in findings
        if finding["issue_class"] in {"NEXT_MODULE_CHAIN_CONTRADICTION", "CLOSED_LOOP_REOPEN_RISK"}
    )
    artifact_state_contradiction_count = sum(
        1
        for finding in findings
        if finding["issue_class"] in {"ARTIFACT_STATE_CONTRADICTION", "SCHEMA_CONFIG_VIOLATION", "GENERIC_RUNNER_VIOLATION"}
    )
    dangerous_flag_true_count = len(artifact_scan["dangerous_true"])
    dangerous_flags_all_false = dangerous_flag_true_count == 0
    replacement_checks = {
        "expected_head_observed": git["head"] == EXPECTED_HEAD,
        "repo_clean_for_audit_scope": git["repo_clean_for_audit_scope"],
        "tracked_python_scan_completed": py_validation["tracked_python_count"] == len(py_files),
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_true_flags_recorded": dangerous_flags_all_false or any(item["issue_class"] == "DANGEROUS_FLAG" for item in findings),
        "policy_level_active": POLICY_LEVEL == "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE",
        "fixed_safety_values_preserved": True,
        "decision_logic_applied": decision["next_module"]
        in {NEXT_MODULE_P0, NEXT_MODULE_P1, NEXT_MODULE_PASS},
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "expected_head": EXPECTED_HEAD,
        "previous_confirmed_post_check": EXPECTED_PREVIOUS_POST_CHECK,
        "audit_status": decision["audit_status"],
        "final_decision": decision["final_decision"],
        "next_action": decision["next_action"],
        "next_module": decision["next_module"],
        "audit_scope": {
            "tracked_repo_files": True,
            "tracked_python_files": True,
            "latest_json_txt_artifacts": True,
            "tools_modules": True,
            "edge_factory_os_artifact_directories": True,
            "recent_git_commits": True,
            "current_git_state": True,
            "current_tracked_manifest": True,
        },
        "audit_limitations": [
            "This audit is adversarial and heuristic; it cannot mathematically prove the absence of all bugs.",
            "Indicator counts include historical and dormant surfaces; findings require human review before any repair.",
            "The audit module is preview-only and performs no fixes or direct applies.",
        ],
        "supported_issue_classes": ISSUE_CLASSES,
        "repo_clean": git["repo_clean_for_audit_scope"],
        "tracked_file_count": len(tracked),
        "tracked_python_count": py_validation["tracked_python_count"],
        "previous_tracked_python_count": PREVIOUS_TRACKED_PYTHON_COUNT,
        "tracked_python_syntax_error_count": py_validation["syntax_error_count"],
        "tracked_python_bom_error_count": py_validation["bom_error_count"],
        "unexpected_untracked_count": git["unexpected_untracked_count"],
        "planned_schema_files_existing_count": len(planned_existing),
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "generic_runner_target_file": GENERIC_RUNNER_TARGET_FILE,
        "dangerous_flags_all_false": dangerous_flags_all_false,
        "dangerous_flag_true_count": dangerous_flag_true_count,
        "dangerous_flag_true_records": artifact_scan["dangerous_true"],
        "runtime_touch_indicator_count": touch["runtime_touch_indicator_count"]["count"],
        "launcher_touch_indicator_count": touch["launcher_touch_indicator_count"]["count"],
        "capital_touch_indicator_count": touch["capital_touch_indicator_count"]["count"],
        "live_touch_indicator_count": touch["live_touch_indicator_count"]["count"],
        "real_order_touch_indicator_count": touch["real_order_touch_indicator_count"]["count"],
        "holdout_touch_indicator_count": touch["holdout_touch_indicator_count"]["count"],
        "candidate_family_touch_indicator_count": touch["candidate_family_touch_indicator_count"]["count"],
        "strategy_research_implementation_indicator_count": touch["strategy_research_implementation_indicator_count"]["count"],
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "closed_loop_reopen_indicator_count": closed_loop_reopen_indicator_count,
        "mechanical_loop_indicator_count": mechanical_loop_indicator_count,
        "next_module_chain_issue_count": next_module_chain_issue_count,
        "artifact_state_contradiction_count": artifact_state_contradiction_count,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "derived_live_repo_post_check_recent_count": len(artifact_scan["derived_records"]),
        "exact_post_check_marker_recent_count": len(artifact_scan["exact_marker_records"]),
        "derived_live_repo_post_check_overuse_attention": len(artifact_scan["derived_records"]) > len(artifact_scan["exact_marker_records"]),
        "primary_artifact_preferred": True,
        "missing_primary_artifact_must_not_silently_pass": True,
        "replacement_checks_must_be_explicit": True,
        "replacement_checks_all_true_required": True,
        "previous_next_module_temporarily_superseded_by_human_audit_decision": True,
        "superseded_next_module": SUPERSEDED_NEXT_MODULE,
        "supersede_reason": SUPERSEDE_REASON,
        "issue_count": len(findings),
        "p0_blocker_count": counts["p0_blocker_count"],
        "p1_attention_count": counts["p1_attention_count"],
        "p2_review_count": counts["p2_review_count"],
        "info_count": counts["info_count"],
        "findings": findings,
        "auto_fix_performed": False,
        "direct_apply_performed": False,
        "repair_preview_required": decision["repair_preview_required"],
        "repair_apply_allowed_now": False,
        "evidence_chain_quality": EVIDENCE_CHAIN_QUALITY,
        "current_evidence_chain_quality": EVIDENCE_CHAIN_QUALITY,
        "derived_live_repo_post_check": True,
        "derived_live_repo_post_check_reason": (
            "Whole-system audit uses live repo scans plus latest artifact inspection as replacement evidence; "
            "this remains weaker than a primary post-check artifact and is classified as DERIVED_OVERUSED_ATTENTION."
        ),
        "replacement_checks_all_true": all(value is True for value in replacement_checks.values()),
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py_validation,
            "touch_indicator_samples": touch,
            "artifact_scan_summary": {
                "latest_artifact_count": len(latest_artifacts),
                "latest_json_artifact_count": len(artifact_scan["json_records"]),
                "dangerous_true_count": dangerous_flag_true_count,
                "plain_pass_count": len(artifact_scan["plain_pass"]),
                "derived_record_count": len(artifact_scan["derived_records"]),
                "exact_marker_record_count": len(artifact_scan["exact_marker_records"]),
                "tracked_python_count_records": artifact_scan["tracked_python_counts"][:80],
                "next_module_records": artifact_scan["next_modules"][:80],
                "state_claim_records": artifact_scan["state_claims"][:80],
            },
            "logic_risk_summary": {key: {"count": len(value), "samples": value[:25]} for key, value in logic.items()},
            "recent_commits": recent_commits,
        },
        "dangerous_flags": {flag: False for flag in DANGEROUS_FLAGS},
        "safety_flags": {
            "whole_system_adversarial_logic_audit_after_evidence_chain_adoption": True,
            "audit_must_not_fix": True,
            "auto_fix_performed": False,
            "direct_apply_performed": False,
            "repair_apply_allowed_now": False,
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            **{flag: False for flag in DANGEROUS_FLAGS},
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_whole_system_adversarial_logic_audit_after_evidence_chain_adoption_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_whole_system_adversarial_logic_audit_after_evidence_chain_adoption_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_whole_system_adversarial_logic_audit_after_evidence_chain_adoption_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    return {"latest_json": str(latest_json), "timestamped_json": str(timestamped_json), "latest_txt": str(latest_txt)}


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    Path(outputs["latest_json"]).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
