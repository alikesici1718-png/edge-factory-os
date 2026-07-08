#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
edge_factory_os_full_system_read_only_audit_v1

Read-only inventory of repo health, governance artifacts, and risk signals.
Uses in-process compile() for syntax only (no bytecode files, no imports, no execution).
Does not modify tracked files, run launcher, touch runtime, or execute strategy code.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
LAB_ROOT = REPO_ROOT.parent

OUT_DIR = REPO_ROOT / "edge_factory_os_full_system_read_only_audit"
OUT_JSON = OUT_DIR / "full_system_read_only_audit_latest.json"
OUT_TXT = OUT_DIR / "full_system_read_only_audit_latest.txt"

SCAN_PY_ROOTS = (REPO_ROOT / "tools", REPO_ROOT / "src")

IGNORE_DIR_NAMES = {".git", "__pycache__", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache"}

DANGEROUS_JSON_BOOLS: Tuple[Tuple[str, bool], ...] = (
    ("live_allowed", True),
    ("live_trading_allowed", True),
    ("real_orders_allowed", True),
    ("capital_change_allowed", True),
    ("launcher_allowed", True),
    ("runtime_touch_allowed", True),
    ("execution_allowed", True),
    ("active_paper_allowed", True),
    ("active_paper_execution_allowed_now", True),
    ("patch_apply_allowed_now", True),
    ("family_release_allowed", True),
    ("promotion_allowed", True),
)

MUTATION_LINE_PATTERNS: Tuple[str, ...] = (
    ".write_text(",
    ".write_bytes(",
    "shutil.copy",
    "shutil.move",
    "os.remove",
    "unlink(",
)

LAUNCHER_RISK_PATTERNS: Tuple[str, ...] = (
    "Start-Process",
    "start_edge_factory",
    "MASTER_UPPER_SYSTEM",
    "subprocess.run",
    "subprocess.Popen",
)

SAFETY_FLAGS: Dict[str, bool] = {
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "runtime_patch_allowed": False,
    "backup_delete_allowed": False,
    "backup_move_allowed": False,
    "gitignore_change_allowed": False,
    "strategy_research_allowed": False,
    "candidate_generation_allowed": False,
    "family_release_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "file_delete_allowed": False,
    "file_move_allowed": False,
    "execution_allowed": False,
}

FORBIDDEN_ACTIONS: List[str] = [
    "Do not fix anything from this audit run automatically.",
    "Do not modify tracked files except this tool's own outputs.",
    "Do not delete or move backup files.",
    "Do not change .gitignore.",
    "Do not use git add -f.",
    "Do not run launcher.",
    "Do not touch runtime.",
    "Do not start processes beyond read-only git status.",
    "Do not run strategy research.",
    "Do not generate candidates.",
    "Do not change capital.",
    "Do not enable active paper.",
    "Do not enable live trading.",
    "Do not enable or send real orders.",
    "Do not touch holdout.",
]

OLD_SHORT_CHAIN: Tuple[Tuple[str, str], ...] = (
    (
        "edge_factory_os_old_short_reactivation_gate/old_short_reactivation_gate_latest.json",
        "edge_factory_os_old_short_manual_reactivation_approval_v1.py",
    ),
    (
        "edge_factory_os_old_short_manual_reactivation_approval/old_short_manual_reactivation_approval_latest.json",
        "edge_factory_os_old_short_guarded_runtime_reenable_plan_v1.py",
    ),
    (
        "edge_factory_os_old_short_guarded_runtime_reenable_plan/old_short_guarded_runtime_reenable_plan_latest.json",
        "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview_v1.py",
    ),
    (
        "edge_factory_os_old_short_guarded_runtime_reenable_patch_preview/old_short_guarded_runtime_reenable_patch_preview_latest.json",
        "edge_factory_os_old_short_final_runtime_reenable_execution_approval_v1.py",
    ),
    (
        "edge_factory_os_old_short_final_runtime_reenable_execution_approval/old_short_final_runtime_reenable_execution_approval_latest.json",
        "edge_factory_os_old_short_guarded_runtime_reenable_apply_v1.py",
    ),
)


@dataclass
class AuditIssue:
    issue_id: str
    category: str
    severity: str
    path: str
    evidence: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_repo(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def run_cmd(args: List[str], timeout: int = 60) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except Exception as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": repr(exc)}


def git_state() -> Dict[str, Any]:
    st = run_cmd(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_cmd(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"])
    last = run_cmd(["git", "-C", str(REPO_ROOT), "log", "-1", "--pretty=%h %s"])
    lines = [x.strip().replace("\\", "/") for x in st["stdout"].splitlines() if x.strip()]
    backup_like = [
        x
        for x in lines
        if ".bak" in x
        or "_bak_" in x
        or "blocked_patch_bak" in x
        or "readonly_fix_bak" in x
        or ".guarded_reenable_bak_" in x
    ]
    return {
        "status_ok": st["ok"],
        "head_short": head["stdout"].strip() if head["ok"] else None,
        "last_commit": last["stdout"].strip() if last["ok"] else None,
        "git_status_lines": lines,
        "untracked_or_dirty_count": len(lines),
        "backup_like_untracked_or_dirty": backup_like,
        "universe_guard_in_status": any(
            "tools/edge_factory_os_universe_coverage_guard_v1.py" in x for x in lines
        ),
    }


def iter_py_files(root: Path) -> Iterator[Path]:
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES]
        for fn in filenames:
            if fn.endswith(".py"):
                yield Path(dirpath) / fn


def iter_json_files(root: Path) -> Iterator[Path]:
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in Path(dirpath).parts:
            continue
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES]
        for fn in filenames:
            if fn.endswith(".json"):
                yield Path(dirpath) / fn


def syntax_compile_check(source: str, filename: str) -> Optional[str]:
    """
    In-process syntax-only check. Does not import, execute, or write bytecode.
    """
    try:
        compile(source, filename, "exec", dont_inherit=True)
    except SyntaxError as exc:
        return str(exc)
    return None


def walk_json(obj: Any, prefix: str = "$") -> Iterator[Tuple[str, str, Any]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}"
            yield p, k, v
            yield from walk_json(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            yield from walk_json(v, p)


def audit_json_danger_bools(path: Path, data: Any) -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    rp = rel_repo(path)
    for jp, key, val in walk_json(data):
        if not isinstance(val, bool):
            continue
        for dk, bad in DANGEROUS_JSON_BOOLS:
            if key == dk and val == bad:
                issues.append(
                    AuditIssue(
                        issue_id=f"POLICY_FLAG_TRUE:{rp}:{jp}",
                        category="policy_safety_flag_drift",
                        severity="CRITICAL",
                        path=rp,
                        evidence=f"{key}=true at {jp}",
                        recommendation="Verify governance artifact; must remain false unless explicitly gated.",
                    )
                )
    return issues


def audit_json_paths(path: Path, data: Any) -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    rp = rel_repo(path)
    win_abs = re.compile(r"^[A-Za-z]:\\")
    for jp, key, val in walk_json(data):
        if not isinstance(val, str) or len(val) < 6:
            continue
        if win_abs.match(val) or val.startswith("\\\\"):
            p = Path(val)
            if not p.exists():
                issues.append(
                    AuditIssue(
                        issue_id=f"BROKEN_PATH:{rp}:{jp}",
                        category="broken_paths",
                        severity="ATTENTION",
                        path=rp,
                        evidence=f"Missing absolute path at {jp}: {val[:240]}",
                        recommendation="Confirm machine-local path or migrate to repo-relative reporting.",
                    )
                )
        elif "/edge_lab_new/" in val.replace("\\", "/") and "edge_factory_os_repo" not in val:
            alt = Path(val)
            if not alt.exists():
                issues.append(
                    AuditIssue(
                        issue_id=f"BROKEN_LAB_PATH:{rp}:{jp}",
                        category="broken_paths",
                        severity="ATTENTION",
                        path=rp,
                        evidence=f"Possible lab path not found at {jp}",
                        recommendation="Validate lab_root-relative artifact producers.",
                    )
                )
    return issues


def audit_latest_txt_pairs() -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    for js in REPO_ROOT.glob("edge_factory_os_*/*_latest.json"):
        if ".git" in js.parts:
            continue
        txt = js.with_suffix(".txt")
        if not txt.is_file():
            issues.append(
                AuditIssue(
                    issue_id=f"MISSING_TXT:{rel_repo(js)}",
                    category="missing_latest_artifacts",
                    severity="INFO",
                    path=rel_repo(js),
                    evidence=f"JSON exists but sibling TXT missing: {rel_repo(txt)}",
                    recommendation="Run the producing module to emit paired TXT or confirm intentional JSON-only.",
                )
            )
    for tx in REPO_ROOT.glob("edge_factory_os_*/*_latest.txt"):
        if ".git" in tx.parts:
            continue
        js = tx.with_suffix(".json")
        if not js.is_file():
            issues.append(
                AuditIssue(
                    issue_id=f"MISSING_JSON:{rel_repo(tx)}",
                    category="missing_latest_artifacts",
                    severity="ATTENTION",
                    path=rel_repo(tx),
                    evidence=f"TXT exists but sibling JSON missing: {rel_repo(js)}",
                    recommendation="Regenerate paired JSON or remove orphan TXT.",
                )
            )
    return issues


def load_json_safe(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        return {"__parse_error__": repr(exc)}


def next_module_targets() -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    for js in iter_json_files(REPO_ROOT):
        rp = rel_repo(js)
        if "edge_factory_os_" not in rp:
            continue
        if not (rp.startswith("edge_factory_os_") or rp.startswith("edge_factory_os_framework/")):
            continue
        data = load_json_safe(js)
        if isinstance(data, dict) and "__parse_error__" in data:
            issues.append(
                AuditIssue(
                    issue_id=f"JSON_PARSE:{rel_repo(js)}",
                    category="json_parse_errors",
                    severity="ATTENTION",
                    path=rel_repo(js),
                    evidence=str(data["__parse_error__"])[:500],
                    recommendation="Repair malformed governance JSON.",
                )
            )
            continue
        if not isinstance(data, dict):
            continue
        nm = data.get("next_module")
        if isinstance(nm, str) and nm.strip():
            tool = REPO_ROOT / "tools" / Path(nm.strip()).name
            if not tool.is_file():
                issues.append(
                    AuditIssue(
                        issue_id=f"NEXT_MODULE_MISSING:{rel_repo(js)}:{nm}",
                        category="next_module_chain",
                        severity="ATTENTION",
                        path=rel_repo(js),
                        evidence=f"next_module={nm!r} not found under tools/",
                        recommendation="Align next_module with an existing tools/ module or add the module.",
                    )
                )
    return issues


def old_short_chain_audit() -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    for json_rel, expected_next_tool in OLD_SHORT_CHAIN:
        jpath = REPO_ROOT / json_rel.replace("/", os.sep)
        if not jpath.is_file():
            issues.append(
                AuditIssue(
                    issue_id=f"OLD_SHORT_MISSING:{json_rel}",
                    category="old_short_governance_chain",
                    severity="ATTENTION",
                    path=json_rel,
                    evidence="Expected governance artifact missing.",
                    recommendation="Run upstream governance module or restore artifact.",
                )
            )
            continue
        data = load_json_safe(jpath)
        if not isinstance(data, dict) or "__parse_error__" in data:
            continue
        nm = data.get("next_module")
        if isinstance(nm, str) and nm.strip():
            exp_name = Path(expected_next_tool).name
            act_name = Path(nm.strip()).name
            if act_name != exp_name:
                issues.append(
                    AuditIssue(
                        issue_id=f"OLD_SHORT_NEXT_DRIFT:{json_rel}",
                        category="old_short_governance_chain",
                        severity="INFO",
                        path=json_rel,
                        evidence=f"next_module={nm!r} expected tool name {exp_name!r}",
                        recommendation="Confirm intentional chain change; update chain documentation.",
                    )
                )
    apply_dir = REPO_ROOT / "edge_factory_os_old_short_guarded_runtime_reenable_apply"
    apply_json = apply_dir / "old_short_guarded_runtime_reenable_apply_latest.json"
    if not apply_json.is_file():
        issues.append(
            AuditIssue(
                issue_id="OLD_SHORT_APPLY_ARTIFACT_ABSENT",
                category="old_short_governance_chain",
                severity="INFO",
                path=rel_repo(apply_json),
                evidence="Apply module output not present (apply may not have been run).",
                recommendation="Expected until guarded apply is executed with safe patterns.",
            )
        )
    return issues


def research_holdout_surface() -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    found: Set[str] = set()
    for pat in (
        "edge_factory_os_*holdout*.py",
        "edge_factory_os_*restricted*research*.py",
        "edge_factory_os_untouched_holdout*.py",
        "edge_factory_os_*multiple_testing*.py",
        "edge_factory_os_joint_null*.py",
    ):
        for py in (REPO_ROOT / "tools").glob(pat):
            found.add(rel_repo(py))
    if not found:
        issues.append(
            AuditIssue(
                issue_id="RESEARCH_HOLDOUT_TOOLS_ABSENT",
                category="research_holdout_governance",
                severity="INFO",
                path="tools/",
                evidence="No holdout/restricted-research / multiple-testing tool filenames matched globs.",
                recommendation="Verify naming if governance tools were renamed.",
            )
        )
    return issues


def lesson_memory_surface() -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    tool = REPO_ROOT / "tools" / "edge_factory_os_family_registry_and_lesson_enforcer_repair_v1.py"
    reg = REPO_ROOT / "edge_factory_os_framework" / "registries" / "runtime_family_registry_v1.json"
    if not tool.is_file():
        issues.append(
            AuditIssue(
                issue_id="LESSON_REGISTRY_TOOL_MISSING",
                category="lesson_memory_blocked_route",
                severity="ATTENTION",
                path="tools/",
                evidence="edge_factory_os_family_registry_and_lesson_enforcer_repair_v1.py not found",
                recommendation="Restore lesson/registry enforcer tool or update governance map.",
            )
        )
    if not reg.is_file():
        issues.append(
            AuditIssue(
                issue_id="RUNTIME_FAMILY_REGISTRY_JSON_MISSING",
                category="lesson_memory_blocked_route",
                severity="ATTENTION",
                path=rel_repo(reg),
                evidence="runtime_family_registry_v1.json missing",
                recommendation="Refresh registry artifact via repo-only refresh modules.",
            )
        )
    return issues
    issues: List[AuditIssue] = []
    buckets: Dict[str, List[str]] = defaultdict(list)
    for py in (REPO_ROOT / "tools").glob("edge_factory_os_*.py"):
        name = py.name
        m = re.match(r"^(edge_factory_os_.+)_v\d+\.py$", name)
        if m:
            buckets[m.group(1)].append(name)
    for stem, names in sorted(buckets.items()):
        if len(names) > 1:
            issues.append(
                AuditIssue(
                    issue_id=f"DUP_TOOL_FAMILY:{stem}",
                    category="duplicate_superseded_modules",
                    severity="INFO",
                    path="tools/",
                    evidence=", ".join(sorted(names)),
                    recommendation="Confirm which version is canonical; archive or document superseded files.",
                )
            )
    return issues


def scan_py_risks(py: Path) -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    rp = rel_repo(py)
    try:
        text = py.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        issues.append(
            AuditIssue(
                issue_id=f"READ_FAIL:{rp}",
                category="python_syntax_errors",
                severity="ATTENTION",
                path=rp,
                evidence=repr(exc),
                recommendation="Restore readable file encoding.",
            )
        )
        return issues
    lower = text.lower()
    if "read_only" in lower or "readonly" in lower or "repo_only" in lower:
        gate_hint = True
    else:
        gate_hint = False
    mut_hits = [p for p in MUTATION_LINE_PATTERNS if p in text]
    if mut_hits and "edge_factory_os_full_system_read_only_audit_v1.py" not in rp:
        sev = "INFO" if gate_hint else "ATTENTION"
        issues.append(
            AuditIssue(
                issue_id=f"MUTATION_SURFACE:{rp}",
                category="mutation_without_explicit_gate",
                severity=sev,
                path=rp,
                evidence=f"Mutation-like tokens: {', '.join(mut_hits[:6])}",
                recommendation="Ensure writes sit behind governance gates documented in module header.",
            )
        )
    launch_hits = [p for p in LAUNCHER_RISK_PATTERNS if p in text]
    if launch_hits and not gate_hint:
        issues.append(
            AuditIssue(
                issue_id=f"LAUNCHER_RUNTIME_RISK:{rp}",
                category="launcher_runtime_risk_heuristic",
                severity="ATTENTION",
                path=rp,
                evidence=f"Matched: {', '.join(launch_hits)}",
                recommendation="Confirm subprocess/Start-Process is gated, read-only, or non-trading.",
            )
        )
    return issues


def gitignore_audit() -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    gi = REPO_ROOT / ".gitignore"
    if not gi.is_file():
        issues.append(
            AuditIssue(
                issue_id="GITIGNORE_MISSING",
                category="gitignore_problems",
                severity="ATTENTION",
                path=".gitignore",
                evidence="File missing",
                recommendation="Restore .gitignore for repo hygiene.",
            )
        )
        return issues
    lines = gi.read_text(encoding="utf-8", errors="replace").splitlines()
    seen: Set[str] = set()
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s in seen:
            issues.append(
                AuditIssue(
                    issue_id=f"GITIGNORE_DUP:{i}",
                    category="gitignore_problems",
                    severity="INFO",
                    path=".gitignore",
                    evidence=f"Duplicate pattern line {i}: {s!r}",
                    recommendation="Deduplicate .gitignore entries.",
                )
            )
        seen.add(s)
    return issues


def categorize_counts(issues: List[AuditIssue]) -> Tuple[int, int, int, int]:
    c = a = i = 0
    for iss in issues:
        if iss.severity == "CRITICAL":
            c += 1
        elif iss.severity == "ATTENTION":
            a += 1
        else:
            i += 1
    return len(issues), c, a, i



def duplicate_tool_versions() -> List[AuditIssue]:
    """
    Read-only duplicate/superseded module inventory.

    Groups tools/edge_factory_os_*_vN.py files by stem before _vN.
    This does not delete, move, archive, or modify any old module.
    """
    issues: List[AuditIssue] = []
    tools_dir = REPO_ROOT / "tools"

    if not tools_dir.is_dir():
        return issues

    groups: Dict[str, List[Tuple[int, Path]]] = defaultdict(list)
    pattern = re.compile(r"^(?P<stem>edge_factory_os_.+)_v(?P<version>\d+)\.py$")

    for py in tools_dir.glob("edge_factory_os_*_v*.py"):
        match = pattern.match(py.name)
        if not match:
            continue

        stem = match.group("stem")
        version = int(match.group("version"))
        groups[stem].append((version, py))

    for stem, rows in sorted(groups.items()):
        if len(rows) <= 1:
            continue

        rows_sorted = sorted(rows, key=lambda item: item[0])
        latest_version = rows_sorted[-1][0]
        versions = [version for version, _ in rows_sorted]
        paths = [rel_repo(p) for _, p in rows_sorted]

        issues.append(
            AuditIssue(
                issue_id=f"DUPLICATE_TOOL_VERSION:{stem}",
                category="duplicate_superseded_modules",
                severity="INFO",
                path="tools",
                evidence=(
                    f"Multiple versions found for {stem}: versions={versions}; "
                    f"latest_detected_v{latest_version}; paths={paths}"
                ),
                recommendation=(
                    "Review manually. Do not delete or archive old versions from this audit. "
                    "If cleanup is needed, create a separate backup hygiene approval/gate."
                ),
            )
        )

    return issues

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    issues: List[AuditIssue] = []
    gs = git_state()

    for root in SCAN_PY_ROOTS:
        for py in iter_py_files(root):
            rp = rel_repo(py)
            try:
                src = py.read_text(encoding="utf-8", errors="strict")
            except Exception as exc:
                issues.append(
                    AuditIssue(
                        issue_id=f"PY_READ:{rp}",
                        category="python_syntax_errors",
                        severity="ATTENTION",
                        path=rp,
                        evidence=repr(exc),
                        recommendation="Restore readable UTF-8 source.",
                    )
                )
                continue
            err = syntax_compile_check(src, rp)
            if err:
                issues.append(
                    AuditIssue(
                        issue_id=f"SYNTAX_COMPILE:{rp}",
                        category="python_syntax_errors",
                        severity="CRITICAL",
                        path=rp,
                        evidence=err[:1500],
                        recommendation="Fix syntax before any governance execution.",
                    )
                )
            issues.extend(scan_py_risks(py))

    for js in iter_json_files(REPO_ROOT):
        if "node_modules" in js.parts:
            continue
        data = load_json_safe(js)
        if isinstance(data, dict) and "__parse_error__" in data:
            issues.append(
                AuditIssue(
                    issue_id=f"JSON_PARSE:{rel_repo(js)}",
                    category="json_parse_errors",
                    severity="ATTENTION",
                    path=rel_repo(js),
                    evidence=str(data["__parse_error__"])[:800],
                    recommendation="Repair JSON.",
                )
            )
            continue
        issues.extend(audit_json_danger_bools(js, data))
        issues.extend(audit_json_paths(js, data))

    issues.extend(audit_latest_txt_pairs())
    issues.extend(next_module_targets())
    issues.extend(old_short_chain_audit())
    issues.extend(research_holdout_surface())
    issues.extend(duplicate_tool_versions())
    issues.extend(lesson_memory_surface())
    issues.extend(gitignore_audit())

    total, crit, attn, info = categorize_counts(issues)

    if crit > 0:
        audit_status = "READ_ONLY_AUDIT_COMPLETE_WITH_CRITICAL"
        severity = "HIGH"
        final_decision = "STOP_ADDRESS_CRITICAL_ITEMS_BEFORE_GOVERNANCE_EXECUTION"
    elif attn > 0:
        audit_status = "READ_ONLY_AUDIT_COMPLETE_WITH_ATTENTION"
        severity = "MEDIUM"
        final_decision = "REVIEW_ATTENTION_ITEMS_THEN_PRIORITIZE_FIX_QUEUE"
    else:
        audit_status = "READ_ONLY_AUDIT_COMPLETE"
        severity = "LOW"
        final_decision = "OPTIONAL_INFO_CLEANUP_ONLY"

    allowed_scope = "READ_ONLY_REPO_AUDIT"

    queue = [
        {
            "issue_id": x.issue_id,
            "severity": x.severity,
            "category": x.category,
            "recommendation": x.recommendation,
        }
        for x in sorted(issues, key=lambda z: (0 if z.severity == "CRITICAL" else 1 if z.severity == "ATTENTION" else 2, z.issue_id))
    ][:80]

    payload: Dict[str, Any] = {
        "module": "edge_factory_os_full_system_read_only_audit_v1.py",
        "generated_at_utc": now_iso(),
        "audit_status": audit_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "final_decision": final_decision,
        "issue_count": total,
        "critical_issue_count": crit,
        "attention_issue_count": attn,
        "info_issue_count": info,
        "issue_inventory": [x.to_dict() for x in issues],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "git_state": gs,
        "recommended_fix_queue": queue,
        "next_action": "TRIAGE_ISSUE_INVENTORY_NO_AUTO_FIX",
        "next_module": None,
        "outputs": {"json": str(OUT_JSON), "txt": str(OUT_TXT)},
        "audit_limits": {
            "python_syntax_scan_roots": [rel_repo(p) for p in SCAN_PY_ROOTS],
            "python_syntax_check": "compile_source_in_process_exec_mode_no_import_no_execution_no_pyc",
            "json_scan_roots": ["edge_factory_os_framework", "repo_root_excluding_dot_git"],
            "lab_root": str(LAB_ROOT),
        },
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    txt = [
        "Edge Factory OS — full system READ-ONLY audit",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"audit_status: {audit_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"final_decision: {final_decision}",
        f"issue_count: {total} (critical={crit}, attention={attn}, info={info})",
        f"next_action: {payload['next_action']}",
        f"next_module: {payload['next_module']}",
        "",
        "recommended_fix_queue (first 80):",
        json.dumps(queue, indent=2, ensure_ascii=False),
        "",
        "safety_flags:",
        json.dumps(SAFETY_FLAGS, indent=2),
        "",
        "git_state:",
        json.dumps(gs, indent=2, ensure_ascii=False),
    ]
    OUT_TXT.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
