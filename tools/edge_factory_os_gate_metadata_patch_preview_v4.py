from __future__ import annotations

import difflib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

MODULE_NAME = "edge_factory_os_gate_metadata_patch_preview_v4"
OUT_DIR = LAB_ROOT / "edge_factory_os_gate_metadata_patch_preview_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_JSON = REPO_ROOT / "edge_factory_os_gate_review_candidate_preview" / "gate_review_candidate_preview_latest.json"

EXPECTED_HEAD_PREFIX = "f62e5bd"
EXPECTED_GATE_REVIEW_CANDIDATE_COUNT = 25
EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT = 11

ALLOWED_TARGET_ROOTS = ("tools/", "src/")

SAFETY_FLAGS: Dict[str, bool] = {
    "preview_only": True,
    "apply_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "candidate_generation_allowed": False,
    "candidate_release_allowed": False,
    "family_release_allowed": False,
    "strategy_research_allowed": False,
    "holdout_access_allowed": False,
    "gitignore_change_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "git_add_force_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "runtime_touch",
    "launcher_execution",
    "capital_change",
    "active_paper_change",
    "live_trading",
    "real_order_execution",
    "strategy_research",
    "candidate_generation",
    "candidate_release",
    "family_release",
    "holdout_access",
    "gitignore_change",
    "backup_delete",
    "backup_move",
    "git_add_force",
    "blind_fix_all",
    "direct_apply",
    "old_short_guarded_apply_execution",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: List[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_git_state() -> Dict[str, Any]:
    head = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    branch = run_cmd(["git", "branch", "--show-current"])
    status = run_cmd(["git", "status", "--porcelain=v1"])
    remote = run_cmd(["git", "status", "-sb"])

    status_lines = [line for line in status.stdout.splitlines() if line.strip()]
    untracked = [line[3:] for line in status_lines if line.startswith("?? ")]
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]

    return {
        "head": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "status_porcelain": status_lines,
        "remote_status_short": remote.stdout.splitlines(),
        "git_dirty": bool(status_lines),
        "dirty_tracked_count": len(dirty_tracked),
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
    }


def fail_closed(reason: str, extra: Optional[Dict[str, Any]] = None) -> int:
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "preview_status": "GATE_METADATA_PATCH_PREVIEW_V4_FAIL_CLOSED",
        "severity": "BLOCKED",
        "allowed_scope": "READ_ONLY_REPO_PREVIEW_ONLY",
        "final_decision": "STOP_REVIEW_INPUTS_NO_APPLY",
        "next_action": "FIX_INPUT_OR_REVIEW_SOURCE_BEFORE_APPROVAL",
        "reason": reason,
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "source_json": str(SOURCE_JSON),
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_allowed_now": False,
    }
    if extra:
        payload.update(extra)

    out = OUT_DIR / "gate_metadata_patch_preview_v4_fail_closed_latest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS GATE METADATA PATCH PREVIEW v4")
    print("=" * 100)
    print("preview_status: GATE_METADATA_PATCH_PREVIEW_V4_FAIL_CLOSED")
    print(f"reason: {reason}")
    print(f"output: {out}")
    return 2


def assert_safety_shape() -> Optional[str]:
    for key, value in SAFETY_FLAGS.items():
        if not isinstance(value, bool):
            return f"safety_flags[{key}] is not boolean"
    if not isinstance(FORBIDDEN_ACTIONS, list) or not all(isinstance(x, str) for x in FORBIDDEN_ACTIONS):
        return "forbidden_actions must be list[str]"
    return None


def is_tracked_file(rel_path: str) -> bool:
    result = run_cmd(["git", "ls-files", "--error-unmatch", rel_path])
    return result.returncode == 0


def normalize_possible_path(raw: Any) -> Optional[str]:
    if not isinstance(raw, str):
        return None

    text = raw.strip().replace("\\", "/")
    if not text:
        return None

    repo_norm = str(REPO_ROOT).replace("\\", "/")
    if text.lower().startswith(repo_norm.lower() + "/"):
        text = text[len(repo_norm) + 1:]

    match = re.search(r"((?:tools|src)/[A-Za-z0-9_./\-]+?\.py)(?:\b|$)", text)
    if match:
        text = match.group(1)

    text = text.strip().strip("\"'`.,;:()[]{}")

    if text.startswith("/") or ":" in text:
        return None
    if ".." in Path(text).parts:
        return None
    if not any(text.startswith(root) for root in ALLOWED_TARGET_ROOTS):
        return None
    if not text.endswith(".py"):
        return None
    if ".bak" in text or "readonly_fix_bak" in text or "blocked_patch_bak" in text:
        return None
    if text == "tools/edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py":
        return None
    if not is_tracked_file(text):
        return None

    return text


def recursive_path_candidates(node: Any) -> List[str]:
    candidates: List[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, str):
                    direct = normalize_possible_path(v)
                    if direct:
                        candidates.append(direct)

                    for match in re.findall(r"(?:tools|src)[\\/][A-Za-z0-9_./\\\-]+?\.py", v):
                        found = normalize_possible_path(match)
                        if found:
                            candidates.append(found)

                    if any(token in str(k).lower() for token in ["path", "file", "script", "module", "target", "issue"]):
                        keyed = normalize_possible_path(v)
                        if keyed:
                            candidates.append(keyed)
                else:
                    visit(v)

        elif isinstance(value, list):
            for item in value:
                visit(item)

        elif isinstance(value, str):
            direct = normalize_possible_path(value)
            if direct:
                candidates.append(direct)

            for match in re.findall(r"(?:tools|src)[\\/][A-Za-z0-9_./\\\-]+?\.py", value):
                found = normalize_possible_path(match)
                if found:
                    candidates.append(found)

    visit(node)

    deduped: List[str] = []
    seen = set()
    for item in candidates:
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    return deduped


def resolve_candidate_path(row: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
    issue = row.get("issue") if isinstance(row.get("issue"), dict) else {}

    preferred_values = [
        row.get("path"),
        issue.get("path"),
        row.get("target_path"),
        issue.get("target_path"),
        row.get("target_file"),
        issue.get("target_file"),
        row.get("file_path"),
        issue.get("file_path"),
        row.get("script_path"),
        issue.get("script_path"),
        row.get("module_path"),
        issue.get("module_path"),
        row.get("file"),
        issue.get("file"),
        row.get("script"),
        issue.get("script"),
        row.get("issue_id"),
        issue.get("issue_id"),
        row.get("id"),
        issue.get("id"),
    ]

    preferred_candidates: List[str] = []
    for value in preferred_values:
        resolved = normalize_possible_path(value)
        if resolved:
            preferred_candidates.append(resolved)

    recursive_candidates = recursive_path_candidates(row)

    all_candidates: List[str] = []
    for item in preferred_candidates + recursive_candidates:
        if item not in all_candidates:
            all_candidates.append(item)

    debug = {
        "preferred_candidates": preferred_candidates,
        "recursive_candidates": recursive_candidates,
        "all_candidates": all_candidates,
    }

    if len(all_candidates) == 1:
        return all_candidates[0], debug

    return None, debug


def load_source_json() -> Dict[str, Any]:
    if not SOURCE_JSON.exists():
        raise FileNotFoundError(str(SOURCE_JSON))
    return json.loads(SOURCE_JSON.read_text(encoding="utf-8"))


def walk_find_candidate_rows(obj: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def visit(node: Any) -> None:
        if isinstance(node, list):
            dict_items = [x for x in node if isinstance(x, dict)]
            if dict_items:
                hit_count = 0
                for item in dict_items:
                    issue = item.get("issue") if isinstance(item.get("issue"), dict) else {}
                    merged_keys = set(item.keys()) | set(issue.keys())
                    if (
                        "classification" in merged_keys
                        or "risk" in merged_keys
                        or "path" in merged_keys
                        or "target_path" in merged_keys
                        or "target_file" in merged_keys
                        or "issue_id" in merged_keys
                        or "preview_fix_candidate" in merged_keys
                        or "apply_recommended_now" in merged_keys
                    ):
                        hit_count += 1

                if hit_count >= max(1, len(dict_items) // 3):
                    rows.extend(dict_items)

            for item in node:
                visit(item)

        elif isinstance(node, dict):
            for value in node.values():
                visit(value)

    visit(obj)

    deduped: List[Dict[str, Any]] = []
    seen = set()

    for row in rows:
        issue = row.get("issue") if isinstance(row.get("issue"), dict) else {}
        path_guess, _ = resolve_candidate_path(row)
        issue_id = row.get("issue_id") or issue.get("issue_id") or row.get("id") or issue.get("id") or ""
        classification = row.get("classification") or issue.get("classification") or ""
        evidence = row.get("evidence") or issue.get("evidence") or row.get("reason") or issue.get("reason") or ""
        key = (
            str(path_guess),
            str(issue_id),
            str(classification),
            json.dumps(evidence, sort_keys=True, default=str)[:500],
        )
        if key not in seen:
            seen.add(key)
            deduped.append(row)

    return deduped


def normalize_candidate(row: Dict[str, Any]) -> Dict[str, Any]:
    issue = row.get("issue") if isinstance(row.get("issue"), dict) else {}

    resolved_path, path_debug = resolve_candidate_path(row)

    classification = (
        row.get("classification")
        or issue.get("classification")
        or row.get("gate_review_classification")
        or issue.get("gate_review_classification")
        or ""
    )

    risk = (
        row.get("risk")
        or issue.get("risk")
        or row.get("severity")
        or issue.get("severity")
        or ""
    )

    issue_id = (
        row.get("issue_id")
        or issue.get("issue_id")
        or row.get("id")
        or issue.get("id")
        or row.get("candidate_id")
        or ""
    )

    evidence = row.get("evidence") or issue.get("evidence") or row.get("reason") or issue.get("reason") or ""

    preview_fix_candidate = bool(
        row.get("preview_fix_candidate") is True
        or issue.get("preview_fix_candidate") is True
        or row.get("fix_candidate") is True
        or issue.get("fix_candidate") is True
        or row.get("metadata_patch_preview_candidate") is True
        or issue.get("metadata_patch_preview_candidate") is True
        or classification in {
            "GATE_REVIEW_FAIL_MISSING_EXPLICIT_GATE_METADATA",
            "GATE_REVIEW_FAIL_DANGEROUS_PATTERN_NO_CLEAR_GATE",
        }
    )

    apply_recommended_now = bool(
        row.get("apply_recommended_now") is True
        or issue.get("apply_recommended_now") is True
        or row.get("direct_apply_recommended_now") is True
        or issue.get("direct_apply_recommended_now") is True
    )

    return {
        "rel_path": resolved_path,
        "classification": str(classification),
        "risk": str(risk),
        "issue_id": str(issue_id),
        "evidence": evidence,
        "preview_fix_candidate": preview_fix_candidate,
        "apply_recommended_now": apply_recommended_now,
        "path_resolution_debug": path_debug,
        "raw": row,
    }


def extract_counts(source_obj: Dict[str, Any], normalized_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    explicit_counts = source_obj.get("counts") if isinstance(source_obj.get("counts"), dict) else {}
    classification_counts = source_obj.get("classification_counts") if isinstance(source_obj.get("classification_counts"), dict) else {}
    risk_counts = source_obj.get("risk_counts") if isinstance(source_obj.get("risk_counts"), dict) else {}

    candidate_count = (
        source_obj.get("gate_review_candidate_count")
        or explicit_counts.get("gate_review_candidate_count")
        or len(normalized_rows)
    )

    preview_fix_count = (
        source_obj.get("preview_fix_candidate_count")
        or explicit_counts.get("preview_fix_candidate_count")
        or len([x for x in normalized_rows if x["preview_fix_candidate"]])
    )

    return {
        "gate_review_candidate_count": int(candidate_count),
        "preview_fix_candidate_count": int(preview_fix_count),
        "classification_counts": classification_counts,
        "risk_counts": risk_counts,
    }


def find_insert_index(lines: List[str]) -> int:
    if not lines:
        return 0

    i = 0

    if lines and lines[0].startswith("#!"):
        i = 1

    while i < len(lines) and re.match(r"#.*coding[:=]\s*[-\w.]+", lines[i]):
        i += 1

    while i < len(lines) and not lines[i].strip():
        i += 1

    if i < len(lines) and lines[i].lstrip().startswith(('"""', "'''")):
        quote = '"""' if lines[i].lstrip().startswith('"""') else "'''"
        stripped = lines[i].strip()
        if stripped.count(quote) >= 2 and stripped.endswith(quote) and len(stripped) > 3:
            i += 1
        else:
            i += 1
            while i < len(lines):
                if quote in lines[i]:
                    i += 1
                    break
                i += 1

    while i < len(lines) and not lines[i].strip():
        i += 1

    return i


def clean_one_line(value: Any, max_len: int = 180) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, default=str)
    else:
        text = str(value)
    text = text.replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return text


def build_metadata_block(candidate: Dict[str, Any]) -> List[str]:
    rel_path = candidate["rel_path"]
    issue_id = clean_one_line(candidate["issue_id"] or "UNKNOWN")
    classification = clean_one_line(candidate["classification"] or "UNKNOWN")
    risk = clean_one_line(candidate["risk"] or "UNKNOWN")
    evidence = clean_one_line(candidate["evidence"] or "not provided")

    block = [
        "# EDGE_FACTORY_GATE_METADATA_START",
        "# gate_metadata_version: 1",
        "# gate_metadata_kind: non_behavioral_comment_block",
        f"# gate_review_source_file: {SOURCE_JSON.name}",
        f"# gate_review_target_path: {rel_path}",
        f"# gate_review_issue_id: {issue_id}",
        f"# gate_review_classification: {classification}",
        f"# gate_review_risk: {risk}",
        f"# gate_review_evidence: {evidence}",
        "# allowed_scope: REPO_ONLY_OS_INTELLIGENCE",
        "# preview_only: true",
        "# non_behavioral_comment_only: true",
        "# runtime_touch_allowed: false",
        "# launcher_allowed: false",
        "# capital_change_allowed: false",
        "# active_paper_allowed: false",
        "# live_allowed: false",
        "# real_orders_allowed: false",
        "# candidate_generation_allowed: false",
        "# family_release_allowed: false",
        "# strategy_research_allowed: false",
        "# holdout_access_allowed: false",
        "# backup_delete_allowed: false",
        "# backup_move_allowed: false",
        "# direct_apply_allowed: false",
        "# EDGE_FACTORY_GATE_METADATA_END",
        "",
    ]

    if not all(line.startswith("#") or line == "" for line in block):
        raise ValueError("metadata block contains non-comment content")

    return block


def make_preview(candidate: Dict[str, Any]) -> Dict[str, Any]:
    rel_path = candidate["rel_path"]

    if not rel_path:
        return {
            "status": "BLOCKED_PATH_UNRESOLVED_OR_AMBIGUOUS",
            "candidate_summary": {
                "issue_id": candidate["issue_id"],
                "classification": candidate["classification"],
                "risk": candidate["risk"],
                "path_resolution_debug": candidate["path_resolution_debug"],
            },
            "diff": "",
        }

    if not is_tracked_file(rel_path):
        return {
            "status": "BLOCKED_TARGET_NOT_TRACKED_BY_GIT",
            "target_path": rel_path,
            "diff": "",
        }

    target = REPO_ROOT / rel_path
    if not target.exists():
        return {
            "status": "BLOCKED_TARGET_FILE_MISSING",
            "target_path": rel_path,
            "diff": "",
        }

    text = target.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        return {
            "status": "BLOCKED_TARGET_HAS_BOM",
            "target_path": rel_path,
            "diff": "",
        }

    if "EDGE_FACTORY_GATE_METADATA_START" in text:
        return {
            "status": "SKIP_ALREADY_HAS_GATE_METADATA_BLOCK",
            "target_path": rel_path,
            "diff": "",
        }

    lines = text.splitlines()
    insert_at = find_insert_index(lines)
    block = build_metadata_block(candidate)
    new_lines = lines[:insert_at] + block + lines[insert_at:]

    diff_lines = list(difflib.unified_diff(
        [line + "\n" for line in lines],
        [line + "\n" for line in new_lines],
        fromfile=f"a/{rel_path}",
        tofile=f"b/{rel_path}",
        lineterm="",
    ))

    diff = "\n".join(diff_lines) + ("\n" if diff_lines else "")

    added_non_comment_lines = [
        line for line in diff.splitlines()
        if line.startswith("+")
        and not line.startswith("+++")
        and line.strip() != "+"
        and not line.startswith("+#")
    ]

    if added_non_comment_lines:
        return {
            "status": "BLOCKED_PREVIEW_WOULD_ADD_NON_COMMENT_LINES",
            "target_path": rel_path,
            "added_non_comment_lines": added_non_comment_lines[:20],
            "diff": diff,
        }

    return {
        "status": "PREVIEW_READY_NON_BEHAVIORAL_COMMENT_ONLY",
        "target_path": rel_path,
        "insert_line_1based": insert_at + 1,
        "issue_id": candidate["issue_id"],
        "classification": candidate["classification"],
        "risk": candidate["risk"],
        "diff": diff,
    }


def main() -> int:
    safety_error = assert_safety_shape()
    if safety_error:
        return fail_closed(safety_error)

    git_state = get_git_state()

    if not git_state["head"].startswith(EXPECTED_HEAD_PREFIX):
        return fail_closed(
            "unexpected git HEAD; refusing to preview against unknown repo state",
            {
                "expected_head_prefix": EXPECTED_HEAD_PREFIX,
                "git_state": git_state,
            },
        )

    try:
        source_obj = load_source_json()
    except Exception as exc:
        return fail_closed(
            "could not read source gate review candidate preview json",
            {
                "source_json": str(SOURCE_JSON),
                "error": repr(exc),
                "git_state": git_state,
            },
        )

    rows = walk_find_candidate_rows(source_obj)
    normalized_rows = [normalize_candidate(row) for row in rows]
    counts = extract_counts(source_obj, normalized_rows)

    candidate_count = counts["gate_review_candidate_count"]
    preview_fix_count = counts["preview_fix_candidate_count"]

    if candidate_count != EXPECTED_GATE_REVIEW_CANDIDATE_COUNT:
        return fail_closed(
            "gate_review_candidate_count mismatch; refusing to preview",
            {
                "expected_gate_review_candidate_count": EXPECTED_GATE_REVIEW_CANDIDATE_COUNT,
                "actual_gate_review_candidate_count": candidate_count,
                "counts": counts,
                "git_state": git_state,
            },
        )

    if preview_fix_count != EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT:
        return fail_closed(
            "preview_fix_candidate_count mismatch; refusing to preview",
            {
                "expected_preview_fix_candidate_count": EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT,
                "actual_preview_fix_candidate_count": preview_fix_count,
                "counts": counts,
                "git_state": git_state,
            },
        )

    fix_candidates = [
        row for row in normalized_rows
        if row["preview_fix_candidate"] is True
        and row["apply_recommended_now"] is False
        and row["classification"] in {
            "GATE_REVIEW_FAIL_MISSING_EXPLICIT_GATE_METADATA",
            "GATE_REVIEW_FAIL_DANGEROUS_PATTERN_NO_CLEAR_GATE",
        }
    ]

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for row in fix_candidates:
        key = (
            row["rel_path"],
            row["issue_id"],
            row["classification"],
            json.dumps(row["evidence"], sort_keys=True, default=str)[:500],
        )
        if key not in seen:
            seen.add(key)
            deduped.append(row)

    fix_candidates = deduped

    if len(fix_candidates) != EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT:
        return fail_closed(
            "could not normalize exactly 11 preview-fix candidates",
            {
                "expected_preview_fix_candidate_count": EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT,
                "normalized_preview_fix_candidate_count": len(fix_candidates),
                "fix_candidate_summaries": [
                    {
                        "rel_path": row["rel_path"],
                        "issue_id": row["issue_id"],
                        "classification": row["classification"],
                        "risk": row["risk"],
                        "path_resolution_debug": row["path_resolution_debug"],
                    }
                    for row in fix_candidates
                ],
                "counts": counts,
                "git_state": git_state,
            },
        )

    previews = [make_preview(candidate) for candidate in fix_candidates]

    status_counts: Dict[str, int] = {}
    for item in previews:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    blocked_statuses = [status for status in status_counts if status.startswith("BLOCKED")]
    preview_ready_count = status_counts.get("PREVIEW_READY_NON_BEHAVIORAL_COMMENT_ONLY", 0)
    already_present_count = status_counts.get("SKIP_ALREADY_HAS_GATE_METADATA_BLOCK", 0)

    preview_clean = (
        not blocked_statuses
        and preview_ready_count + already_present_count == EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT
    )

    patch_preview_path = OUT_DIR / "gate_metadata_patch_preview_v4_latest.diff"
    patch_preview_path.write_text(
        "\n".join([item["diff"] for item in previews if item.get("diff")]),
        encoding="utf-8",
    )

    unresolved_debug = [
        item for item in previews
        if item["status"].startswith("BLOCKED")
    ]

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "preview_status": (
            "GATE_METADATA_PATCH_PREVIEW_V4_READY_NO_APPLY"
            if preview_clean
            else "GATE_METADATA_PATCH_PREVIEW_V4_BLOCKED_REVIEW_REQUIRED_NO_APPLY"
        ),
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_REPO_PREVIEW_ONLY",
        "final_decision": (
            "REVIEW_PREVIEW_THEN_BUILD_APPROVAL_IF_ACCEPTED"
            if preview_clean
            else "REVIEW_BLOCKED_PREVIEW_ITEMS_BEFORE_APPROVAL"
        ),
        "next_action": (
            "BUILD_GATE_METADATA_PATCH_APPROVAL_V4_IF_PREVIEW_ACCEPTED"
            if preview_clean
            else "REVIEW_PATH_RESOLUTION_DEBUG_NO_APPLY"
        ),
        "next_module": (
            "edge_factory_os_gate_metadata_patch_approval_v4.py"
            if preview_clean
            else None
        ),
        "reason": (
            f"preview_ready_count={preview_ready_count}; "
            f"already_present_count={already_present_count}; "
            f"blocked_statuses={blocked_statuses}"
        ),
        "created_at_utc": now_utc(),
        "repo_root": str(REPO_ROOT),
        "source_gate_review_candidate_preview_json": str(SOURCE_JSON),
        "patch_preview_path": str(patch_preview_path),
        "counts": counts,
        "expected_gate_review_candidate_count": EXPECTED_GATE_REVIEW_CANDIDATE_COUNT,
        "expected_preview_fix_candidate_count": EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT,
        "normalized_preview_fix_candidate_count": len(fix_candidates),
        "preview_ready_count": preview_ready_count,
        "already_present_count": already_present_count,
        "blocked_statuses": blocked_statuses,
        "status_counts": status_counts,
        "unresolved_debug": unresolved_debug,
        "previews": previews,
        "fix_candidate_summaries": [
            {
                "rel_path": row["rel_path"],
                "issue_id": row["issue_id"],
                "classification": row["classification"],
                "risk": row["risk"],
                "path_resolution_debug": row["path_resolution_debug"],
            }
            for row in fix_candidates
        ],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "direct_apply_recommended_now": False,
        "apply_allowed_now": False,
        "target_files_modified": [],
        "runtime_touched": False,
        "launcher_executed": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "holdout_accessed": False,
        "backup_deleted_or_moved": False,
        "gitignore_changed": False,
        "git_add_force_used": False,
        "git_state": git_state,
    }

    latest_json = OUT_DIR / "gate_metadata_patch_preview_v4_latest.json"
    timestamped_json = OUT_DIR / f"gate_metadata_patch_preview_v4_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest_txt = OUT_DIR / "gate_metadata_patch_preview_v4_latest.txt"

    latest_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timestamped_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    txt_lines = [
        "EDGE FACTORY OS GATE METADATA PATCH PREVIEW v4",
        "=" * 100,
        f"preview_status: {payload['preview_status']}",
        f"severity: {payload['severity']}",
        f"allowed_scope: {payload['allowed_scope']}",
        f"final_decision: {payload['final_decision']}",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        f"reason: {payload['reason']}",
        f"source_gate_review_candidate_preview_json: {SOURCE_JSON}",
        f"patch_preview_path: {patch_preview_path}",
        "",
        "COUNTS",
        "-" * 100,
        json.dumps({
            "expected_gate_review_candidate_count": EXPECTED_GATE_REVIEW_CANDIDATE_COUNT,
            "actual_gate_review_candidate_count": candidate_count,
            "expected_preview_fix_candidate_count": EXPECTED_PREVIEW_FIX_CANDIDATE_COUNT,
            "actual_preview_fix_candidate_count": preview_fix_count,
            "normalized_preview_fix_candidate_count": len(fix_candidates),
            "preview_ready_count": preview_ready_count,
            "already_present_count": already_present_count,
            "status_counts": status_counts,
            "blocked_statuses": blocked_statuses,
        }, indent=2, sort_keys=True),
        "",
        "FIX CANDIDATE SUMMARIES",
        "-" * 100,
        json.dumps(payload["fix_candidate_summaries"], indent=2, sort_keys=True),
        "",
        "SAFETY",
        "-" * 100,
        json.dumps(SAFETY_FLAGS, indent=2, sort_keys=True),
        "",
        "GIT STATE",
        "-" * 100,
        json.dumps(git_state, indent=2, sort_keys=True),
        "",
        "OUTPUTS",
        "-" * 100,
        f"latest_json: {latest_json}",
        f"timestamped_json: {timestamped_json}",
        f"latest_txt: {latest_txt}",
        f"latest_diff: {patch_preview_path}",
    ]

    latest_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    print("\n".join(txt_lines))

    return 0 if preview_clean else 3


if __name__ == "__main__":
    raise SystemExit(main())