#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY ORIGINAL SCANNER LOCATOR v1
========================================

Purpose
-------
Find the original scanner/backtest/generator code or artifacts that produced a candidate
such as ret60_reversal_short.

Why this exists
---------------
Signal rule extractor reported:
    RULE_PARTIAL_NEEDS_ORIGINAL_SCANNER

Meaning:
    - candidate passed evidence gates
    - side/feature were partially inferred
    - exact threshold/operator and hold/exit horizon are not reconstructable from normalized trades alone

So the OS must locate the original scanner/generator code before a sandbox logger can be built.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - search script_dir and workspace for candidate/scanner terms
    - inspect Python/PowerShell/JSON/CSV/MD artifacts
    - score likely source files
    - extract safe snippets around matching lines
    - classify whether original rule source is likely found
    - write a recovery packet for the next module

Run:
    python "C:\Users\alike\edge_factory_original_scanner_locator.py"

Run one candidate:
    python "C:\Users\alike\edge_factory_original_scanner_locator.py" --candidate ret60_reversal_short

Core rule
---------
This module only locates evidence. It does not execute candidate code.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

SEARCH_EXTENSIONS = {".py", ".ps1", ".bat", ".cmd", ".json", ".md", ".txt", ".csv", ".yaml", ".yml"}
EXCLUDE_DIR_PARTS = {
    "__pycache__",
    ".git",
    "site-packages",
    "node_modules",
    "appdata",
    "edge_factory_original_scanner_locator",
    "edge_factory_candidate_signal_rule_extractor",
}

DEFAULT_TERMS = [
    "ret60_reversal_short",
    "ret60",
    "ret_60",
    "ret60m",
    "60m",
    "range_mean_60m_bps",
    "reversal_short",
    "ret60_reversal",
    "reversal",
    "candidate",
    "scanner",
    "scan",
    "backtest",
    "family_key",
    "hold",
    "horizon",
    "threshold",
    "zscore",
    "z_score",
]

RULE_HINT_TERMS = [
    "ret60",
    "range_mean_60m_bps",
    "threshold",
    "<=",
    ">=",
    "<",
    ">",
    "hold",
    "horizon",
    "exit",
    "short",
    "family_key",
    "ret60_reversal_short",
]


@dataclass
class FileHit:
    path: str
    relative_scope: str
    suffix: str
    size_bytes: int
    modified_at: str
    score: float
    matched_terms: List[str]
    likely_role: str
    line_hits: int
    snippet_path: str
    reasons: List[str]
    warnings: List[str]


@dataclass
class CandidateLocatorResult:
    candidate_key: str
    locator_status: str
    top_score: float
    top_file: Optional[str]
    likely_source_files: List[str]
    exact_rule_source_found: bool
    original_scanner_likely_found: bool
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    next_action: str
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]


@dataclass
class LocatorState:
    generated_at: str
    workspace: str
    script_dir: str
    candidate: str
    files_scanned: int
    hits_found: int
    likely_source_count: int
    locator_status: str
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_key(x: Any) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def should_skip(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    if parts & EXCLUDE_DIR_PARTS:
        return True
    s = str(path).lower()
    if "appdata" in s or "site-packages" in s:
        return True
    return False


def discover_files(workspace: Path, script_dir: Path, max_files: int) -> List[Tuple[Path, str]]:
    roots = [(script_dir, "script_dir"), (workspace, "workspace")]
    seen: set[str] = set()
    out: List[Tuple[Path, str]] = []
    for root, scope in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if len(out) >= max_files:
                break
            if not p.is_file():
                continue
            if p.suffix.lower() not in SEARCH_EXTENSIONS:
                continue
            if should_skip(p):
                continue
            key = str(p.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            out.append((p, scope))
    out.sort(key=lambda item: item[0].stat().st_mtime, reverse=True)
    return out[:max_files]


def read_text_limited(path: Path, max_bytes: int) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    try:
        size = path.stat().st_size
        if size > max_bytes:
            warnings.append(f"file truncated for scan: size={size} max_bytes={max_bytes}")
        with path.open("rb") as f:
            raw = f.read(max_bytes)
        return raw.decode("utf-8", errors="replace"), warnings
    except Exception as e:
        return "", [f"read failed: {e}"]


def score_content(path: Path, text: str, candidate: str, terms: List[str]) -> Tuple[float, List[str], str, List[str], List[int]]:
    low = text.lower()
    name_low = path.name.lower()
    path_low = str(path).lower()
    matched: List[str] = []
    score = 0.0
    reasons: List[str] = []

    for term in terms:
        t = term.lower()
        if t and t in low:
            matched.append(term)
            count = low.count(t)
            score += min(20.0, 2.0 * count)
        if t and t in name_low:
            score += 25.0
            reasons.append(f"term in filename: {term}")
        elif t and t in path_low:
            score += 8.0

    cand = safe_key(candidate)
    if cand in low:
        score += 50.0
        reasons.append("exact candidate key appears in file")
    if cand in name_low:
        score += 80.0
        reasons.append("exact candidate key appears in filename")

    role = "UNKNOWN"
    if path.suffix.lower() == ".py":
        if any(x in low for x in ["def ", "argparse", "backtest", "scan", "candidate", "family_key"]):
            role = "POSSIBLE_SCANNER_OR_BACKTEST_CODE"
            score += 25.0
    if any(x in name_low for x in ["scanner", "scan", "backtest", "validator", "research", "candidate"]):
        role = "POSSIBLE_SCANNER_OR_BACKTEST_CODE"
        score += 20.0
    if path.suffix.lower() in {".json", ".csv"} and any(x in low for x in ["ret60_reversal_short", "range_mean_60m_bps", "threshold"]):
        role = "POSSIBLE_RESULT_OR_CONFIG_ARTIFACT"
        score += 15.0

    # Rule-source clues matter more than generic mentions.
    rule_clues = 0
    for clue in ["range_mean_60m_bps", "ret60", "threshold", "hold", "horizon", "<=", ">=", "short"]:
        if clue.lower() in low:
            rule_clues += 1
    if rule_clues >= 4:
        score += 60.0
        reasons.append("multiple rule-source clues found")
    elif rule_clues >= 2:
        score += 25.0
        reasons.append("some rule-source clues found")

    line_hits: List[int] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        l = line.lower()
        if any(t.lower() in l for t in matched[:20]) or any(c.lower() in l for c in RULE_HINT_TERMS):
            line_hits.append(i)
    return round(score, 4), sorted(set(matched)), role, reasons, line_hits[:80]


def make_snippet(path: Path, text: str, line_hits: List[int], out_path: Path, context: int = 4) -> None:
    lines = text.splitlines()
    if not line_hits:
        out_path.write_text("", encoding="utf-8")
        return
    blocks: List[str] = []
    used: set[int] = set()
    for line_no in line_hits[:30]:
        start = max(1, line_no - context)
        end = min(len(lines), line_no + context)
        block_lines = []
        for n in range(start, end + 1):
            if n in used:
                continue
            used.add(n)
            prefix = ">>" if n == line_no else "  "
            block_lines.append(f"{prefix} {n:05d}: {lines[n-1]}")
        if block_lines:
            blocks.append("\n".join(block_lines))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(f"SOURCE: {path}\n\n" + "\n\n---\n\n".join(blocks), encoding="utf-8")


def inspect_file(path: Path, scope: str, candidate: str, terms: List[str], out_dir: Path, max_bytes: int) -> Optional[FileHit]:
    text, warnings = read_text_limited(path, max_bytes)
    if not text:
        return None
    score, matched, role, reasons, line_hits = score_content(path, text, candidate, terms)
    if not matched and score < 15:
        return None
    if score < 10:
        return None
    snippet_name = stable_hash({"path": str(path), "candidate": candidate}) + "_snippet.txt"
    snippet_path = out_dir / "snippets" / snippet_name
    make_snippet(path, text, line_hits, snippet_path)
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except Exception:
        mtime = ""
    return FileHit(
        path=str(path),
        relative_scope=scope,
        suffix=path.suffix.lower(),
        size_bytes=int(path.stat().st_size),
        modified_at=mtime,
        score=score,
        matched_terms=matched,
        likely_role=role,
        line_hits=len(line_hits),
        snippet_path=str(snippet_path),
        reasons=reasons,
        warnings=warnings,
    )


def classify_locator(candidate: str, hits: List[FileHit]) -> CandidateLocatorResult:
    hits_sorted = sorted(hits, key=lambda h: h.score, reverse=True)
    top = hits_sorted[0] if hits_sorted else None
    likely = [h for h in hits_sorted if h.score >= 80 or h.likely_role == "POSSIBLE_SCANNER_OR_BACKTEST_CODE"][:20]

    reasons: List[str] = []
    warnings: List[str] = []
    blockers: List[str] = []

    original_scanner = any(h.likely_role == "POSSIBLE_SCANNER_OR_BACKTEST_CODE" and h.score >= 100 for h in hits_sorted)
    exact_rule = False
    for h in hits_sorted[:10]:
        terms = {t.lower() for t in h.matched_terms}
        if safe_key(candidate) in terms and ("range_mean_60m_bps" in terms or "ret60" in terms) and ("threshold" in terms or "hold" in terms or "horizon" in terms):
            exact_rule = True
            break

    if exact_rule and original_scanner:
        status = "ORIGINAL_RULE_SOURCE_LIKELY_FOUND"
        logger_allowed = False  # still needs rule extraction module v2, not direct logger build
        next_action = "RUN_RULE_EXTRACTOR_V2_ON_TOP_SOURCE"
        reasons.append("candidate/scanner terms and rule clues found in high-score source files")
    elif original_scanner or likely:
        status = "LIKELY_SOURCE_FILES_FOUND_NEEDS_REVIEW"
        logger_allowed = False
        next_action = "OPEN_TOP_SNIPPETS_AND_EXTRACT_EXACT_RULE"
        reasons.append("likely scanner/result files were found but exact rule is not proven yet")
        blockers.append("exact rule still requires snippet review or parser v2")
    else:
        status = "ORIGINAL_SCANNER_NOT_FOUND"
        logger_allowed = False
        next_action = "SEARCH_OLDER_WORKSPACE_OR_REGENERATE_SCANNER"
        blockers.append("no likely original scanner/backtest source found")

    if not hits_sorted:
        warnings.append("no hits found for candidate terms")
    elif top and top.score < 80:
        warnings.append("top hit score is weak; source may be incomplete")

    return CandidateLocatorResult(
        candidate_key=safe_key(candidate),
        locator_status=status,
        top_score=top.score if top else 0.0,
        top_file=top.path if top else None,
        likely_source_files=[h.path for h in likely],
        exact_rule_source_found=exact_rule,
        original_scanner_likely_found=original_scanner,
        logger_build_allowed=logger_allowed,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
    )


def append_ledger(workspace: Path, result: CandidateLocatorResult, state_path: Path) -> Optional[str]:
    try:
        root = workspace / "edge_factory_research_result_ledger"
        ledger = root / "master_research_result_ledger.jsonl"
        if result.locator_status == "ORIGINAL_RULE_SOURCE_LIKELY_FOUND":
            status = "PASS"
        elif result.locator_status == "LIKELY_SOURCE_FILES_FOUND_NEEDS_REVIEW":
            status = "WATCHLIST"
        else:
            status = "INCONCLUSIVE"
        raw = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "task_id": f"original_scanner_locator_{result.candidate_key}",
            "result_status": status,
            "score": result.top_score,
            "summary": f"{result.candidate_key}: {result.locator_status}, top_score={result.top_score}, top_file={result.top_file}",
            "evidence_path": str(state_path),
            "family": None,
            "candidate": result.candidate_key,
            "tags": ["original_scanner_locator", "rule_recovery", "offline", "no_runtime"],
            "reviewer": "original_scanner_locator_v1",
            "source": "edge_factory_original_scanner_locator_v1",
            "safe_for_auto_promotion": False,
            "live_allowed": False,
            "notes": "Source locating only. Does not execute candidate code.",
        }
        result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"
        row = {"result_id": result_id, **raw}
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        rows = []
        with ledger.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        pd.DataFrame(rows).to_csv(root / "master_research_result_ledger.csv", index=False)
        return result_id
    except Exception:
        return None


def hits_df(hits: List[FileHit]) -> pd.DataFrame:
    rows = []
    for h in hits:
        d = asdict(h)
        d["matched_terms"] = " | ".join(h.matched_terms)
        d["reasons"] = " | ".join(h.reasons)
        d["warnings"] = " | ".join(h.warnings)
        rows.append(d)
    return pd.DataFrame(rows)


def write_report(path: Path, state: LocatorState, result: CandidateLocatorResult, hits: List[FileHit]) -> None:
    lines = [
        "# Edge Factory Original Scanner Locator Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Candidate: **{state.candidate}**",
        f"Locator status: **{result.locator_status}**",
        f"Files scanned: **{state.files_scanned}**",
        f"Hits found: **{state.hits_found}**",
        f"Likely source count: **{state.likely_source_count}**",
        f"Top score: **{result.top_score}**",
        f"Top file: `{result.top_file}`",
        f"Logger build allowed: **{result.logger_build_allowed}**",
        f"Shadow start allowed: **{result.shadow_start_allowed}**",
        f"Live allowed: **{result.live_allowed}**",
        "",
        "## Top hits",
        "",
    ]
    if hits:
        lines += ["| Score | Role | File | Terms | Snippet |", "|---:|---|---|---|---|"]
        for h in sorted(hits, key=lambda x: x.score, reverse=True)[:30]:
            lines.append(f"| {h.score} | {h.likely_role} | `{h.path}` | {', '.join(h.matched_terms[:12])} | `{h.snippet_path}` |")
    else:
        lines.append("No hits found.")
    lines += ["", "## Reasons", ""]
    for r in state.reasons:
        lines.append(f"- {r}")
    for r in result.reasons:
        lines.append(f"- {r}")
    if result.blockers:
        lines += ["", "## Blockers", ""]
        for b in result.blockers:
            lines.append(f"- {b}")
    warnings = state.warnings + result.warnings
    if warnings:
        lines += ["", "## Warnings", ""]
        for w in warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "If likely source files are found, the next step is rule extraction from the top snippets. Do not build a runtime logger until exact threshold/operator/hold logic is recovered.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory original scanner locator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--candidate", default="ret60_reversal_short")
    p.add_argument("--terms", default=None, help="extra comma-separated search terms")
    p.add_argument("--out_dir", default=None)
    p.add_argument("--max_files", type=int, default=25000)
    p.add_argument("--max_bytes", type=int, default=2_000_000)
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    candidate = safe_key(args.candidate)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_original_scanner_locator"
    out_dir = out_root / f"original_scanner_locator_{candidate}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    terms = list(DEFAULT_TERMS)
    if args.terms:
        terms.extend([t.strip() for t in str(args.terms).split(",") if t.strip()])
    terms = list(dict.fromkeys(terms))

    files = discover_files(workspace, script_dir, int(args.max_files))
    hits: List[FileHit] = []
    for path, scope in files:
        hit = inspect_file(path, scope, candidate, terms, out_dir, int(args.max_bytes))
        if hit:
            hits.append(hit)
    hits.sort(key=lambda h: h.score, reverse=True)

    result = classify_locator(candidate, hits)
    warnings: List[str] = []
    if len(files) >= int(args.max_files):
        warnings.append("max_files limit reached; search may be incomplete")

    state = LocatorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        script_dir=str(script_dir),
        candidate=candidate,
        files_scanned=len(files),
        hits_found=len(hits),
        likely_source_count=len(result.likely_source_files),
        locator_status=result.locator_status,
        logger_build_allowed=result.logger_build_allowed,
        shadow_start_allowed=result.shadow_start_allowed,
        active_paper_allowed=result.active_paper_allowed,
        live_allowed=False,
        reasons=[
            "Original scanner locator searched workspace and script_dir for candidate/source terms.",
            "It only reads files and extracts snippets; it does not execute candidate code.",
        ],
        warnings=warnings,
        hard_rules=[
            "Original scanner locator never starts paper/live.",
            "Original scanner locator never mutates active config.",
            "Original scanner locator never executes located scanner code.",
            "Original scanner locator never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Logger build remains blocked until exact rule is extracted from source.",
            "Live remains blocked.",
        ],
    )

    state_path = out_dir / "original_scanner_locator_state.json"
    write_json(state_path, {"state": asdict(state), "result": asdict(result), "hits": [asdict(h) for h in hits]})
    hits_df(hits).to_csv(out_dir / "original_scanner_locator_hits.csv", index=False)
    hits_df(hits[:20]).to_csv(out_dir / "top_original_scanner_hits.csv", index=False)
    write_report(out_dir / "original_scanner_locator_report.md", state, result, hits)

    ledger_id = None
    if not args.no_ledger_append:
        ledger_id = append_ledger(workspace, result, state_path)

    print("EDGE FACTORY ORIGINAL SCANNER LOCATOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"locator_status: {result.locator_status}")
    print(f"files_scanned: {state.files_scanned}")
    print(f"hits_found: {state.hits_found}")
    print(f"likely_source_count: {state.likely_source_count}")
    print(f"top_score: {result.top_score}")
    print(f"top_file: {result.top_file}")
    print(f"logger_build_allowed: {result.logger_build_allowed}")
    print(f"shadow_start_allowed: {result.shadow_start_allowed}")
    print(f"active_paper_allowed: {result.active_paper_allowed}")
    print(f"ledger_result_id: {ledger_id}")
    print("live_allowed: False")
    print("")
    print("TOP HITS")
    print("-" * 100)
    for h in hits[:12]:
        print(f"score={h.score:8.2f} role={h.likely_role:36s} terms={len(h.matched_terms):2d} file={h.path}")
        print(f"     snippet={h.snippet_path}")
        if h.reasons:
            print(f"     - {' | '.join(h.reasons[:3])}")
    if result.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in result.blockers:
            print(f"- {b}")
    all_warnings = state.warnings + result.warnings
    if all_warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in all_warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not execute candidate code.")
    print(f"Report : {out_dir / 'original_scanner_locator_report.md'}")
    print(f"State  : {state_path}")
    print(f"Hits   : {out_dir / 'original_scanner_locator_hits.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
