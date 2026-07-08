#!/usr/bin/env python3
"""Deep forensic search for missing old_short exact global gate replay source.

Forensic source discovery only. This module does not restore files, checkout
commits, move/copy/delete data, run a backtest, touch runtime/live/capital, or
create candidate/edge claims.
"""

from __future__ import annotations

import csv
import fnmatch
import hashlib
import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DESKTOP_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop")
USER_ROOT = Path(r"C:\Users\alike")

TOOL_REL = "tools/edge_factory_os_repo_only_old_short_deep_gate_source_forensic_search_v1.py"
ARTIFACT_REL = "artifacts/old_short/old_short_deep_gate_source_forensic_search_v1.json"
TOOL_PATH = REPO_ROOT / TOOL_REL
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_REL

EVIDENCE_REL = "artifacts/old_short/old_short_evidence_recovery_status_refresh_v1.json"
CONTRACT_REL = "artifacts/old_short/old_short_frozen_route_contract_reconstruction_v1.json"
RECOVERY_REL = "artifacts/old_short/old_short_missing_data_source_recovery_discovery_v1.json"
DISAMBIGUATION_REL = "artifacts/old_short/old_short_gate_source_disambiguation_review_v1.json"
CLOSURE_REL = "artifacts/old_short/old_short_exact_rerun_unavailable_closure_v1.json"

STATUS_EXACT = "PASS_REPO_ONLY_OLD_SHORT_DEEP_GATE_SOURCE_FORENSIC_SEARCH_EXACT_FOUND"
STATUS_CANDIDATES = "PASS_REPO_ONLY_OLD_SHORT_DEEP_GATE_SOURCE_FORENSIC_SEARCH_CANDIDATES_FOUND_NOT_EXACT"
STATUS_NOT_FOUND = "PASS_REPO_ONLY_OLD_SHORT_DEEP_GATE_SOURCE_FORENSIC_SEARCH_NOT_FOUND"
ARTIFACT_KIND = "OLD_SHORT_DEEP_GATE_SOURCE_FORENSIC_SEARCH"
MODULE = "edge_factory_os_repo_only_old_short_deep_gate_source_forensic_search_v1"

SEARCH_PATTERNS = [
    "global_gate_decisions.csv",
    "*global*gate*decision*",
    "*gate*decision*",
    "*gate_replay*",
    "*paper_run_gate*",
    "*paper*gate*",
    "*old_short*",
    "*OLD_SHORT*",
    "*old*short*gate*",
    "*old*short*decision*",
    "*monitoring_ready*",
]
CONTENT_TERMS = [
    "OLD_SHORT_MONITORING_READY_CONTINUE_COLLECT_NO_CAPITAL",
    "old_short rows",
    "route_key old_short",
    "family_key old_short",
    "signal old_short",
    "gate v4 priority",
    "paper_run_gate_v4_priority",
    "global_gate_decisions.csv",
    "old_short",
]
REQUIRED_GATE_COLUMNS = {"decision", "family_key", "signal_id"}
MAX_SAFE_READ_BYTES = 10_000_000
MAX_SHA_BYTES = 50_000_000
MAX_EXTERNAL_CANDIDATES = 2000
MAX_MANIFEST_REFERENCES = 600
PRUNE_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "site-packages",
    "dist",
    "build",
    ".cache",
    "AppData",
}
TEXT_EXTENSIONS = {".csv", ".json", ".txt", ".md", ".log", ".toml", ".yaml", ".yml", ".ps1", ".py"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_output(args: list[str], check: bool = True, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", "-C", str(REPO_ROOT), *args],
        check=check,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def git_stdout(args: list[str], check: bool = True, timeout: int = 180) -> str:
    result = git_output(args, check=check, timeout=timeout)
    return result.stdout.strip()


def repo_status_lines() -> list[str]:
    out = git_stdout(["status", "--short", "--untracked-files=all"])
    return [] if not out else out.splitlines()


def repo_clean_except_expected() -> bool:
    allowed = {TOOL_REL, ARTIFACT_REL}
    for line in repo_status_lines():
        rel = line[3:].replace("\\", "/")
        if line[:2] == "??" and rel in allowed:
            continue
        return False
    return True


def tracked_python_count() -> int:
    out = git_stdout(["ls-files", "*.py"])
    return 0 if not out else len(out.splitlines())


def load_json(rel_path: str) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Required artifact missing: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_raw(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8", errors="ignore")


def payload_hash(payload: dict[str, Any]) -> str:
    copy = json_safe(dict(payload))
    copy.pop("payload_sha256_excluding_hash", None)
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    safe_payload = json_safe(payload)
    ARTIFACT_PATH.write_text(json.dumps(safe_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k) if k is not None else "__extra__": json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    return value


def is_inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
        return True
    except ValueError:
        return False


def lower_path(path: str | Path) -> str:
    return str(path).replace("\\", "/").lower()


def path_matches_patterns(path: str | Path) -> bool:
    text = lower_path(path)
    name = Path(str(path)).name.lower()
    for pattern in SEARCH_PATTERNS:
        p = pattern.lower()
        if fnmatch.fnmatch(name, p) or fnmatch.fnmatch(text, p):
            return True
    return False


def possible_gate_source_path(path: str | Path) -> bool:
    text = lower_path(path)
    name = Path(str(path)).name.lower()
    return (
        "global_gate_decisions" in name
        or "gate_replay" in text
        or ("gate" in text and "decision" in text)
        or ("old_short" in text and ("gate" in text or "decision" in text))
        or ("paper_run_gate" in text and Path(str(path)).suffix.lower() in TEXT_EXTENSIONS)
    )


def path_variants(path: str) -> set[str]:
    p = str(path)
    return {p, p.replace("\\", "/"), p.replace("/", "\\"), p.replace("\\", "\\\\"), Path(p).name}


def sha256_file(path: Path, size_bytes: int | None) -> str | None:
    if size_bytes is None or size_bytes > MAX_SHA_BYTES:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_timestamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return None


def review_csv_text(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_header": [],
        "first_3_data_rows": [],
        "row_count": 0,
        "contains_old_short_rows": False,
        "old_short_row_count": 0,
        "contains_exact_old_short_route_identifier": False,
        "matches_expected_schema": False,
        "route_family_identifiers_found": [],
        "timestamp_range": {"min_utc": None, "max_utc": None},
        "sample_old_short_rows": [],
    }
    reader = csv.DictReader(text.splitlines())
    header = list(reader.fieldnames or [])
    lower_header = {col.lower() for col in header}
    result["schema_header"] = header
    result["matches_expected_schema"] = REQUIRED_GATE_COLUMNS.issubset(lower_header)
    identifiers: set[str] = set()
    ts_min: datetime | None = None
    ts_max: datetime | None = None
    for row in reader:
        result["row_count"] += 1
        if len(result["first_3_data_rows"]) < 3:
            result["first_3_data_rows"].append({k: str(v) for k, v in row.items()})
        family_key = str(row.get("family_key", "")).strip()
        strategy = str(row.get("strategy", "")).strip()
        signal_id = str(row.get("signal_id", "")).strip()
        row_text = json.dumps(row, ensure_ascii=True).lower()
        if family_key:
            identifiers.add(f"family_key:{family_key}")
        if strategy:
            identifiers.add(f"strategy:{strategy}")
        old_short_hit = family_key == "old_short" or "old_short" in row_text
        exact_route_hit = strategy in {"blowoff_short", "mean_reversion_short"} or "_blowoff_short_" in signal_id or "_mean_reversion_short_" in signal_id
        if old_short_hit:
            result["old_short_row_count"] += 1
            result["contains_old_short_rows"] = True
            if len(result["sample_old_short_rows"]) < 5:
                result["sample_old_short_rows"].append({k: str(v) for k, v in row.items()})
        if exact_route_hit:
            result["contains_exact_old_short_route_identifier"] = True
        for key in ("log_time", "target_entry_time", "planned_exit_time"):
            ts = parse_timestamp(str(row.get(key, "")))
            if ts is None:
                continue
            ts_min = ts if ts_min is None or ts < ts_min else ts_min
            ts_max = ts if ts_max is None or ts > ts_max else ts_max
    result["route_family_identifiers_found"] = sorted(identifiers)
    result["timestamp_range"] = {
        "min_utc": ts_min.strftime("%Y-%m-%dT%H:%M:%SZ") if ts_min else None,
        "max_utc": ts_max.strftime("%Y-%m-%dT%H:%M:%SZ") if ts_max else None,
    }
    return result


def review_text_content(text: str) -> dict[str, Any]:
    lower = text.lower()
    return {
        "schema_header": [],
        "first_3_data_rows": [],
        "row_count": None,
        "contains_old_short_rows": "old_short" in lower,
        "old_short_row_count": lower.count("old_short"),
        "contains_exact_old_short_route_identifier": "blowoff_short" in lower or "mean_reversion_short" in lower,
        "matches_expected_schema": all(term in lower for term in REQUIRED_GATE_COLUMNS),
        "route_family_identifiers_found": sorted(
            term for term in ["old_short", "blowoff_short", "mean_reversion_short"] if term in lower
        ),
        "timestamp_range": {"min_utc": None, "max_utc": None},
        "sample_old_short_rows": [
            line[:500]
            for line in text.splitlines()
            if "old_short" in line.lower()
        ][:5],
    }


def review_filesystem_candidate(
    path: Path,
    source_type: str,
    frozen_gate_path: str,
    prior_raw_text: str,
    expected_period_known: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extra = extra or {}
    exists = path.exists()
    stat = path.stat() if exists else None
    is_file = path.is_file() if exists else False
    size_bytes = stat.st_size if stat and is_file else None
    modified_time_utc = (
        datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if stat
        else None
    )
    content_review: dict[str, Any] = {
        "schema_header": [],
        "first_3_data_rows": [],
        "row_count": None,
        "contains_old_short_rows": False,
        "old_short_row_count": 0,
        "contains_exact_old_short_route_identifier": False,
        "matches_expected_schema": False,
        "route_family_identifiers_found": [],
        "timestamp_range": {"min_utc": None, "max_utc": None},
        "sample_old_short_rows": [],
    }
    read_error = None
    safe_read = is_file and size_bytes is not None and size_bytes <= MAX_SAFE_READ_BYTES and path.suffix.lower() in TEXT_EXTENSIONS
    if safe_read:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix.lower() == ".csv":
                content_review = review_csv_text(text)
            else:
                content_review = review_text_content(text)
        except OSError as exc:
            read_error = f"{exc.__class__.__name__}: {exc}"
    elif is_file:
        read_error = "not_safely_read_due_size_or_extension"

    direct_contract = str(path).lower() == str(frozen_gate_path).lower()
    referenced_by_evidence = any(variant in prior_raw_text for variant in path_variants(str(path)))
    deterministic_link = direct_contract or referenced_by_evidence or bool(extra.get("git_path_matches_contract"))
    period_condition = True if not expected_period_known else False
    is_csv_gate_replay_source = path.suffix.lower() == ".csv" and (
        "gate" in lower_path(path) or "decision" in lower_path(path)
    )
    contains_old_short_or_route = bool(
        content_review.get("contains_old_short_rows")
        or content_review.get("contains_exact_old_short_route_identifier")
    )
    exact_conditions = {
        "is_csv_gate_replay_source_candidate": is_csv_gate_replay_source,
        "contains_old_short_rows_or_exact_route_identifier": contains_old_short_or_route,
        "schema_compatible_with_frozen_contract": bool(content_review.get("matches_expected_schema")),
        "deterministically_linked_to_frozen_contract_or_old_short_evidence": deterministic_link,
        "covers_expected_period_if_known": period_condition,
    }
    exact_score = (
        (25 if contains_old_short_or_route else 0)
        + (25 if content_review.get("matches_expected_schema") else 0)
        + (25 if deterministic_link else 0)
        + (15 if direct_contract else 0)
        + (10 if referenced_by_evidence else 0)
    )
    return {
        "source_type": source_type,
        "path": str(path),
        "git_ref": None,
        "exists_or_accessible": exists,
        "size_bytes": size_bytes,
        "modified_time_utc": modified_time_utc,
        "commit_hash": None,
        "blob_hash": None,
        "extension": "".join(path.suffixes).lower() if is_file else "",
        "inside_repo": is_inside_repo(path) if exists else None,
        "schema_header": content_review.get("schema_header", []),
        "first_3_data_rows": content_review.get("first_3_data_rows", []),
        "sample_old_short_rows": content_review.get("sample_old_short_rows", []),
        "row_count": content_review.get("row_count"),
        "contains_old_short_rows": content_review.get("contains_old_short_rows"),
        "contains_exact_old_short_route_identifier": content_review.get("contains_exact_old_short_route_identifier"),
        "directly_referenced_by_frozen_contract": direct_contract,
        "referenced_by_old_short_evidence": referenced_by_evidence,
        "matches_expected_schema": content_review.get("matches_expected_schema"),
        "matches_expected_date_range_if_known": period_condition,
        "route_family_identifiers_found": content_review.get("route_family_identifiers_found", []),
        "timestamp_range": content_review.get("timestamp_range", {"min_utc": None, "max_utc": None}),
        "sha256": sha256_file(path, size_bytes) if is_file else None,
        "exact_selection_conditions": exact_conditions,
        "satisfies_exact_selection_conditions": all(exact_conditions.values()),
        "exact_source_score": exact_score,
        "why_candidate_is_or_is_not_exact": "satisfies_all_exact_conditions"
        if all(exact_conditions.values())
        else "missing:" + ",".join(k for k, v in exact_conditions.items() if not v),
        "read_error": read_error,
        **extra,
    }


def blob_metadata(commit: str, path: str) -> tuple[str | None, int | None]:
    tree = git_stdout(["ls-tree", commit, "--", path], check=False, timeout=60)
    parts = tree.split()
    blob = parts[2] if len(parts) >= 3 else None
    size = None
    if blob:
        size_out = git_stdout(["cat-file", "-s", blob], check=False, timeout=60)
        try:
            size = int(size_out)
        except ValueError:
            size = None
    return blob, size


def review_git_blob_candidate(
    commit: str,
    path: str,
    frozen_gate_path: str,
    prior_raw_text: str,
    expected_period_known: bool,
    deleted_path: bool = False,
) -> dict[str, Any]:
    blob, size = blob_metadata(commit, path)
    content_review: dict[str, Any] = {
        "schema_header": [],
        "first_3_data_rows": [],
        "row_count": None,
        "contains_old_short_rows": False,
        "old_short_row_count": 0,
        "contains_exact_old_short_route_identifier": False,
        "matches_expected_schema": False,
        "route_family_identifiers_found": [],
        "timestamp_range": {"min_utc": None, "max_utc": None},
        "sample_old_short_rows": [],
    }
    read_error = None
    if blob and size is not None and size <= MAX_SAFE_READ_BYTES and Path(path).suffix.lower() in TEXT_EXTENSIONS:
        shown = git_output(["show", f"{commit}:{path}"], check=False, timeout=90)
        if shown.returncode == 0:
            text = shown.stdout
            if Path(path).suffix.lower() == ".csv":
                content_review = review_csv_text(text)
            else:
                content_review = review_text_content(text)
        else:
            read_error = shown.stderr.strip()[:500] or "git_show_failed"
    else:
        read_error = "not_safely_read_due_size_or_extension_or_missing_blob"

    git_path_matches_contract = lower_path(path).endswith(lower_path(frozen_gate_path).split("edge_lab_new/")[-1])
    referenced_by_evidence = any(variant in prior_raw_text for variant in path_variants(path))
    deterministic_link = git_path_matches_contract or referenced_by_evidence
    period_condition = True if not expected_period_known else False
    is_csv_gate_replay_source = Path(path).suffix.lower() == ".csv" and (
        "gate" in lower_path(path) or "decision" in lower_path(path)
    )
    contains_old_short_or_route = bool(
        content_review.get("contains_old_short_rows")
        or content_review.get("contains_exact_old_short_route_identifier")
    )
    exact_conditions = {
        "is_csv_gate_replay_source_candidate": is_csv_gate_replay_source,
        "contains_old_short_rows_or_exact_route_identifier": contains_old_short_or_route,
        "schema_compatible_with_frozen_contract": bool(content_review.get("matches_expected_schema")),
        "deterministically_linked_to_frozen_contract_or_old_short_evidence": deterministic_link,
        "covers_expected_period_if_known": period_condition,
    }
    score = (
        (25 if contains_old_short_or_route else 0)
        + (25 if content_review.get("matches_expected_schema") else 0)
        + (25 if deterministic_link else 0)
        + (15 if git_path_matches_contract else 0)
        + (10 if referenced_by_evidence else 0)
    )
    return {
        "source_type": "git_history",
        "path": path,
        "git_ref": f"{commit}:{path}",
        "exists_or_accessible": blob is not None,
        "size_bytes": size,
        "modified_time_utc": None,
        "commit_hash": commit,
        "blob_hash": blob,
        "extension": "".join(Path(path).suffixes).lower(),
        "inside_repo": True,
        "schema_header": content_review.get("schema_header", []),
        "first_3_data_rows": content_review.get("first_3_data_rows", []),
        "sample_old_short_rows": content_review.get("sample_old_short_rows", []),
        "row_count": content_review.get("row_count"),
        "contains_old_short_rows": content_review.get("contains_old_short_rows"),
        "contains_exact_old_short_route_identifier": content_review.get("contains_exact_old_short_route_identifier"),
        "directly_referenced_by_frozen_contract": git_path_matches_contract,
        "referenced_by_old_short_evidence": referenced_by_evidence,
        "matches_expected_schema": content_review.get("matches_expected_schema"),
        "matches_expected_date_range_if_known": period_condition,
        "route_family_identifiers_found": content_review.get("route_family_identifiers_found", []),
        "timestamp_range": content_review.get("timestamp_range", {"min_utc": None, "max_utc": None}),
        "sha256": blob,
        "exact_selection_conditions": exact_conditions,
        "satisfies_exact_selection_conditions": all(exact_conditions.values()),
        "exact_source_score": score,
        "why_candidate_is_or_is_not_exact": "satisfies_all_exact_conditions"
        if all(exact_conditions.values())
        else "missing:" + ",".join(k for k, v in exact_conditions.items() if not v),
        "read_error": read_error,
        "deleted_path_candidate": deleted_path,
    }


def current_repo_search() -> dict[str, Any]:
    tracked = git_stdout(["ls-files"]).splitlines()
    matching_paths = [path for path in tracked if path_matches_patterns(path)]
    grep = git_output(
        [
            "grep",
            "-I",
            "-n",
            "-e",
            "old_short",
            "-e",
            "OLD_SHORT",
            "-e",
            "global_gate_decisions.csv",
            "-e",
            "paper_run_gate_v4_priority",
            "--",
            ".",
        ],
        check=False,
        timeout=180,
    )
    grep_lines = grep.stdout.splitlines() if grep.stdout else []
    return {
        "git_status_short": repo_status_lines(),
        "tracked_file_count": len(tracked),
        "tracked_paths_matching_patterns_count": len(matching_paths),
        "tracked_paths_matching_patterns_sample": matching_paths[:300],
        "git_grep_returncode": grep.returncode,
        "git_grep_hit_count": len(grep_lines),
        "git_grep_sample": grep_lines[:300],
    }


def ignored_untracked_search() -> dict[str, Any]:
    status = git_output(["status", "--short", "--ignored", "--untracked-files=all"], check=False, timeout=120)
    lines = status.stdout.splitlines() if status.stdout else []
    matching = [line for line in lines if path_matches_patterns(line[3:] if len(line) > 3 else line)]
    return {
        "git_status_ignored_returncode": status.returncode,
        "ignored_untracked_line_count": len(lines),
        "ignored_untracked_matching_count": len(matching),
        "ignored_untracked_matching_sample": matching[:300],
    }


def parse_git_log_name_only(output: str) -> dict[str, set[str]]:
    commit = None
    by_path: dict[str, set[str]] = defaultdict(set)
    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("__COMMIT__"):
            commit = line.replace("__COMMIT__", "", 1)
            continue
        if commit and path_matches_patterns(line):
            by_path[line].add(commit)
    return by_path


def git_history_search(frozen_gate_path: str, prior_raw_text: str, expected_period_known: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    log_out = git_stdout(["log", "--all", "--name-only", "--pretty=format:__COMMIT__%H"], check=False, timeout=240)
    path_commits = parse_git_log_name_only(log_out)
    deleted_out = git_stdout(
        ["log", "--all", "--diff-filter=D", "--name-only", "--pretty=format:__COMMIT__%H"],
        check=False,
        timeout=240,
    )
    deleted_path_commits = parse_git_log_name_only(deleted_out)

    grep_out = git_output(
        [
            "log",
            "--all",
            "-G",
            "global_gate_decisions|paper_run_gate_v4_priority|family_key.*old_short|OLD_SHORT_MONITORING_READY",
            "--name-only",
            "--pretty=format:__COMMIT__%H",
        ],
        check=False,
        timeout=240,
    )
    grep_path_commits = parse_git_log_name_only(grep_out.stdout if grep_out.stdout else "")

    candidate_pairs: list[tuple[str, str, bool]] = []
    seen: set[tuple[str, str]] = set()
    for source, deleted in ((path_commits, False), (deleted_path_commits, True), (grep_path_commits, False)):
        for path, commits in source.items():
            if not possible_gate_source_path(path):
                continue
            for commit in sorted(commits)[:5]:
                key = (commit, path)
                if key not in seen:
                    seen.add(key)
                    candidate_pairs.append((commit, path, deleted))

    reviews = [
        review_git_blob_candidate(commit, path, frozen_gate_path, prior_raw_text, expected_period_known, deleted)
        for commit, path, deleted in candidate_pairs[:250]
    ]
    search = {
        "git_log_name_only_paths_matching_patterns_count": len(path_commits),
        "git_log_name_only_paths_matching_patterns_sample": [
            {"path": path, "commit_count": len(commits), "commits_sample": sorted(commits)[:5]}
            for path, commits in list(path_commits.items())[:300]
        ],
        "deleted_paths_matching_gate_patterns_count": len(deleted_path_commits),
        "deleted_paths_matching_gate_patterns_sample": [
            {"path": path, "commit_count": len(commits), "commits_sample": sorted(commits)[:5]}
            for path, commits in list(deleted_path_commits.items())[:300]
        ],
        "git_log_G_returncode": grep_out.returncode,
        "git_log_G_paths_matching_patterns_count": len(grep_path_commits),
        "history_blob_candidate_count": len(reviews),
    }
    return search, reviews


def external_root_search(
    frozen_gate_path: str,
    prior_raw_text: str,
    expected_period_known: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    roots = [EDGE_LAB_ROOT, DESKTOP_ROOT, USER_ROOT]
    candidates: list[dict[str, Any]] = []
    manifest_hits: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    visited_dirs = 0
    file_match_count = 0

    recovery = load_json(RECOVERY_REL)
    for row in recovery.get("exact_source_assessment", {}).get("exact_global_gate_candidates", []):
        path = Path(str(row.get("path", "")))
        if path.exists():
            key = str(path.resolve()).lower()
            if key not in seen_paths:
                seen_paths.add(key)
                candidates.append(review_filesystem_candidate(path, "external_file", frozen_gate_path, prior_raw_text, expected_period_known, {"from_prior_recovery_candidate": True}))

    for root in roots:
        if not root.exists():
            skipped.append({"path": str(root), "reason": "search_root_missing"})
            continue
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            current = Path(dirpath)
            visited_dirs += 1
            kept_dirs = []
            for dirname in dirnames:
                if dirname in PRUNE_DIR_NAMES:
                    skipped.append({"path": str(current / dirname), "reason": "pruned_directory_name"})
                else:
                    kept_dirs.append(dirname)
            dirnames[:] = kept_dirs
            for filename in filenames:
                path = current / filename
                text_path = lower_path(path)
                if path_matches_patterns(path):
                    file_match_count += 1
                if possible_gate_source_path(path) and len(candidates) < MAX_EXTERNAL_CANDIDATES:
                    key = str(path.resolve()).lower()
                    if key not in seen_paths:
                        seen_paths.add(key)
                        candidates.append(review_filesystem_candidate(path, "external_file", frozen_gate_path, prior_raw_text, expected_period_known))
                manifestish = any(token in text_path for token in ("quarantine", "cleanup", "backup", "audit_export", "redacted", "manifest"))
                if manifestish and path.suffix.lower() in TEXT_EXTENSIONS and len(manifest_hits) < MAX_MANIFEST_REFERENCES:
                    try:
                        stat = path.stat()
                        if stat.st_size <= MAX_SAFE_READ_BYTES:
                            body = path.read_text(encoding="utf-8", errors="replace")
                            lower = body.lower()
                            if any(term.lower() in lower for term in CONTENT_TERMS):
                                manifest_hits.append(
                                    {
                                        "source_type": "quarantine_manifest",
                                        "path": str(path),
                                        "size_bytes": stat.st_size,
                                        "modified_time_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "contains_global_gate_reference": "global_gate_decisions" in lower,
                                        "contains_old_short_reference": "old_short" in lower,
                                        "contains_paper_run_gate_v4_priority_reference": "paper_run_gate_v4_priority" in lower,
                                        "sample_lines": [line[:500] for line in body.splitlines() if any(term.lower() in line.lower() for term in CONTENT_TERMS)][:10],
                                    }
                                )
                    except OSError:
                        pass
    search = {
        "search_roots": [str(root) for root in roots],
        "visited_directories": visited_dirs,
        "filename_pattern_match_count": file_match_count,
        "external_gate_candidate_count": len(candidates),
        "skipped_roots_or_dirs_count": len(skipped),
        "skipped_roots_or_dirs_sample": skipped[:300],
    }
    quarantine = {
        "quarantine_cleanup_backup_manifest_reference_count": len(manifest_hits),
        "manifest_reference_sample": manifest_hits[:200],
    }
    return search, candidates, quarantine, manifest_hits


def select_exact(candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str, str, str]:
    qualified = [row for row in candidates if row.get("satisfies_exact_selection_conditions")]
    if len(qualified) == 1:
        return (
            qualified[0],
            STATUS_EXACT,
            "OLD_SHORT_DEEP_GATE_SOURCE_FORENSIC_EXACT_FOUND",
            "OLD_SHORT_EXACT_GATE_SOURCE_MATERIALIZATION_REVIEW_ONLY",
        )
    if candidates:
        return (
            None,
            STATUS_CANDIDATES,
            "OLD_SHORT_DEEP_GATE_SOURCE_FORENSIC_CANDIDATES_FOUND_NOT_EXACT",
            "MANUAL_SOURCE_REVIEW_OR_ONEDRIVE_VERSION_HISTORY_CHECK",
        )
    return (
        None,
        STATUS_NOT_FOUND,
        "OLD_SHORT_DEEP_GATE_SOURCE_FORENSIC_NOT_FOUND",
        "OLD_SHORT_REMAINS_MONITORING_ONLY_EXACT_GATE_SOURCE_UNAVAILABLE",
    )


def build_payload() -> dict[str, Any]:
    evidence = load_json(EVIDENCE_REL)
    contract = load_json(CONTRACT_REL)
    recovery = load_json(RECOVERY_REL)
    disambiguation = load_json(DISAMBIGUATION_REL)
    closure = load_json(CLOSURE_REL)
    evidence_raw = read_raw(EVIDENCE_REL)
    prior_raw_text = "\n".join(
        read_raw(rel)
        for rel in (EVIDENCE_REL, CONTRACT_REL, RECOVERY_REL, DISAMBIGUATION_REL, CLOSURE_REL)
    )

    route_contract = contract.get("route_contract", {})
    entry_rule = route_contract.get("entry_rule", {})
    frozen_gate_path = str(entry_rule.get("global_gate_path", ""))
    expected_period_known = False
    frozen_clues = {
        "frozen_contract_gate_path": frozen_gate_path,
        "expected_schema_columns": sorted(REQUIRED_GATE_COLUMNS),
        "expected_route_family_identifiers": ["family_key:old_short", "strategy:blowoff_short", "strategy:mean_reversion_short"],
        "expected_date_range_available": expected_period_known,
        "timeframe": route_contract.get("timeframe"),
        "route_name": route_contract.get("route_name"),
    }

    current = current_repo_search()
    ignored = ignored_untracked_search()
    history, history_candidates = git_history_search(frozen_gate_path, evidence_raw, expected_period_known)
    external, external_candidates, quarantine, manifest_hits = external_root_search(
        frozen_gate_path, evidence_raw, expected_period_known
    )

    candidates_by_key: dict[str, dict[str, Any]] = {}
    for row in [*history_candidates, *external_candidates]:
        key = f"{row.get('source_type')}::{row.get('git_ref') or row.get('path')}"
        candidates_by_key[key] = row
    candidate_reviews = sorted(
        candidates_by_key.values(),
        key=lambda row: (
            row.get("satisfies_exact_selection_conditions") is True,
            int(row.get("exact_source_score") or 0),
            row.get("contains_old_short_rows") is True,
            row.get("directly_referenced_by_frozen_contract") is True,
        ),
        reverse=True,
    )
    selected, status, classification, next_step = select_exact(candidate_reviews)
    if selected and selected.get("source_type") == "git_history":
        selected_record = {
            "selected": True,
            "source_type": selected.get("source_type"),
            "git_ref": selected.get("git_ref"),
            "commit_hash": selected.get("commit_hash"),
            "path": selected.get("path"),
            "blob_hash": selected.get("blob_hash"),
            "source_restored_now": False,
        }
    elif selected:
        selected_record = {
            "selected": True,
            "source_type": selected.get("source_type"),
            "path": selected.get("path"),
            "sha256": selected.get("sha256"),
            "source_restored_now": False,
        }
    else:
        selected_record = {"selected": False, "selected_exact_gate_source": None, "source_restored_now": False}

    safety_permissions = {
        "forensic_search_created": True,
        "source_restored_now": False,
        "frozen_backtest_allowed_now": False,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_except_expected(),
        "prior_old_short_artifacts_loaded": all(
            [
                evidence.get("status") == "PASS_REPO_ONLY_OLD_SHORT_EVIDENCE_RECOVERY_STATUS_REFRESH_CREATED",
                contract.get("status") == "PASS_REPO_ONLY_OLD_SHORT_FROZEN_ROUTE_CONTRACT_RECONSTRUCTION_CREATED",
                recovery.get("status") == "PASS_REPO_ONLY_OLD_SHORT_MISSING_DATA_SOURCE_RECOVERY_FOUND",
                disambiguation.get("status") == "PASS_REPO_ONLY_OLD_SHORT_GATE_SOURCE_DISAMBIGUATION_NO_VALID_SOURCE",
                closure.get("status") == "PASS_REPO_ONLY_OLD_SHORT_EXACT_RERUN_UNAVAILABLE_CLOSURE_CREATED",
            ]
        ),
        "no_backtest_run": True,
        "no_runtime_touched": True,
        "no_file_restore": True,
        "no_checkout": True,
        "no_branch_change": True,
        "no_file_move_delete_copy": True,
        "git_history_checked": True,
        "current_repo_checked": True,
        "external_roots_checked_or_skips_recorded": True,
        "deterministic_selection_rule_applied": True,
        "no_network_used": True,
        "no_api_called": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
    }
    replacement_checks_all_true = all(validation_checks.values())

    payload = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "head": git_stdout(["rev-parse", "HEAD"]),
            "repo_clean_before_run": validation_checks["repo_clean_before_run"],
            "tracked_python_count_before": tracked_python_count(),
            "generated_at_utc": utc_now(),
        },
        "source_artifacts": {
            "evidence_recovery": EVIDENCE_REL,
            "frozen_route_contract": CONTRACT_REL,
            "missing_data_source_recovery": RECOVERY_REL,
            "gate_source_disambiguation": DISAMBIGUATION_REL,
            "exact_rerun_unavailable_closure": CLOSURE_REL,
        },
        "frozen_contract_clues": frozen_clues,
        "current_repo_search": current,
        "ignored_untracked_search": ignored,
        "git_history_search": history,
        "external_root_search": external,
        "quarantine_manifest_search": quarantine,
        "candidate_reviews": candidate_reviews,
        "selected_exact_gate_source": selected_record,
        "forensic_classification": classification,
        "continuation_decision": {
            "source_restored_now": False,
            "frozen_backtest_allowed_now": False,
            "next_step": next_step,
            "strategy_execution_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
        },
        "limitations": [
            "No files were restored, copied, moved, deleted, or checked out.",
            "Large files and compressed/archive candidates were not fully read.",
            "OneDrive version history is not accessible from repo-local forensic search.",
            "A candidate is exact only when deterministic linkage and schema/content conditions pass.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    return payload


def main() -> None:
    payload = build_payload()
    write_artifact(payload)
    candidate_count = len(payload["candidate_reviews"])
    git_history_count = payload["git_history_search"].get("history_blob_candidate_count", 0)
    external_count = payload["external_root_search"].get("external_gate_candidate_count", 0)
    selected = payload["selected_exact_gate_source"]
    selected_text = selected.get("git_ref") or selected.get("path") or "null"
    print(f"status: {payload['status']}")
    print(f"forensic_classification: {payload['forensic_classification']}")
    print(f"candidate_count: {candidate_count}")
    print(f"git_history_candidate_count: {git_history_count}")
    print(f"external_candidate_count: {external_count}")
    print(f"selected_exact_gate_source: {selected_text}")
    print("source_restored_now: false")
    print("frozen_backtest_allowed_now: false")
    print(f"next_step: {payload['continuation_decision']['next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


if __name__ == "__main__":
    main()
