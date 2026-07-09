"""
Patches live paper logger scripts to replace hardcoded $50 notional assignments with a dynamic family-aware notional resolver, reading the four strategy family logger Python files as inputs.
Operates in dry-run mode by default; use --apply to back up and overwrite originals.
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd


LOGGER_SCRIPTS = {
    "old_short": "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": "market_relative_live_paper_logger.py",
    "weak_market_short": "weak_market_breakdown_short_live_paper_logger.py",
}

FIXED_ASSIGN_RE = re.compile(
    r"^(\s*)(notional|base_notional|trade_notional|paper_notional|fixed_notional)\s*=\s*(50(?:\.0+)?)(\s*(?:#.*)?)$",
    re.MULTILINE,
)
LITERAL_NOTIONAL_RE = re.compile(r"([\"']notional[\"']\s*:\s*)(50(?:\.0+)?)")


def utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def insert_import(text: str) -> tuple[str, bool]:
    line_to_add = "from sizing_contract_runtime import resolve_family_notional"
    if line_to_add in text:
        return text, False
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
        elif insert_at and line.strip() and not line.startswith(("import ", "from ")):
            break
    lines.insert(insert_at, line_to_add)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), True


def find_parser_var(text: str) -> str | None:
    m = re.search(r"(\w+)\s*=\s*argparse\.ArgumentParser\s*\(", text)
    if m:
        return m.group(1)
    m = re.search(r"(\w+)\s*=\s*ArgumentParser\s*\(", text)
    if m:
        return m.group(1)
    m = re.search(r"(\w+)\.add_argument\s*\(", text)
    if m:
        return m.group(1)
    return None


def insert_argparse_args(text: str, parser_var: str | None) -> tuple[str, bool]:
    if "--sizing_contract" in text and "--default_notional" in text:
        return text, False
    if not parser_var:
        return text, False

    add_lines = [
        f'{parser_var}.add_argument("--sizing_contract", default="", help="Path to position_sizing_contract.json")',
        f'{parser_var}.add_argument("--default_notional", type=float, default=50.0, help="Fallback paper notional if sizing contract is missing")',
    ]

    lines = text.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and re.search(rf"\b{re.escape(parser_var)}\s*=\s*(argparse\.)?ArgumentParser\s*\(", line):
            out.extend(add_lines)
            inserted = True

    if not inserted:
        out = []
        for line in lines:
            if not inserted and ".parse_args(" in line:
                out.extend(add_lines)
                inserted = True
            out.append(line)

    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), inserted


def find_args_var(text: str) -> str | None:
    m = re.search(r"(\w+)\s*=\s*\w+\.parse_args\s*\(", text)
    if m:
        return m.group(1)
    if "args." in text:
        return "args"
    return None


def insert_contract_notional(text: str, family_key: str, args_var: str | None) -> tuple[str, bool]:
    if "CONTRACT_NOTIONAL" in text and "resolve_family_notional" in text:
        return text, False
    if not args_var:
        return text, False

    block_text = f"""
FAMILY_KEY = "{family_key}"
CONTRACT_NOTIONAL = resolve_family_notional(
    FAMILY_KEY,
    default_notional={args_var}.default_notional,
    sizing_contract_path={args_var}.sizing_contract,
)
"""
    block = block_text.strip("\n").splitlines()

    lines = text.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and re.search(rf"\b{re.escape(args_var)}\s*=\s*\w+\.parse_args\s*\(", line):
            out.extend(block)
            inserted = True

    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), inserted


def replace_fixed_notional(text: str) -> tuple[str, int]:
    count = 0

    def repl_assign(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"{m.group(1)}{m.group(2)} = CONTRACT_NOTIONAL{m.group(4)}"

    text2 = FIXED_ASSIGN_RE.sub(repl_assign, text)

    def repl_literal(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"{m.group(1)}CONTRACT_NOTIONAL"

    text2 = LITERAL_NOTIONAL_RE.sub(repl_literal, text2)
    return text2, count


def patch_text(text: str, family_key: str) -> tuple[str, dict]:
    stats = {
        "import_added": False,
        "parser_var": "",
        "args_added": False,
        "args_var": "",
        "contract_block_added": False,
        "fixed_notional_replacements": 0,
        "status": "UNKNOWN",
    }

    t, changed = insert_import(text)
    stats["import_added"] = changed

    parser_var = find_parser_var(t)
    stats["parser_var"] = parser_var or ""
    t, changed = insert_argparse_args(t, parser_var)
    stats["args_added"] = changed

    args_var = find_args_var(t)
    stats["args_var"] = args_var or ""
    t, changed = insert_contract_notional(t, family_key, args_var)
    stats["contract_block_added"] = changed

    t, n = replace_fixed_notional(t)
    stats["fixed_notional_replacements"] = n

    if not parser_var:
        stats["status"] = "NEEDS_MANUAL_PATCH_NO_ARGPARSE"
    elif not args_var:
        stats["status"] = "NEEDS_MANUAL_PATCH_NO_PARSE_ARGS"
    elif n == 0:
        stats["status"] = "NEEDS_MANUAL_PATCH_NO_FIXED_NOTIONAL_FOUND"
    else:
        stats["status"] = "PATCH_CANDIDATE"

    return t, stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Safely create contract-aware patched logger copies.")
    ap.add_argument("--user_dir", default=r"C:\Users\alike")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_logger_sizing_patch")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    user_dir = Path(args.user_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    backup_dir = out_dir / f"backup_{utc_stamp()}"
    patched_dir = out_dir / "patched"
    diff_dir = out_dir / "diffs"
    patched_dir.mkdir(parents=True, exist_ok=True)
    diff_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for family_key, script_name in LOGGER_SCRIPTS.items():
        src = user_dir / script_name
        row = {
            "family_key": family_key,
            "script": str(src),
            "exists": src.exists(),
            "patched_file": "",
            "diff_file": "",
            "backup_file": "",
            "applied": False,
        }

        if not src.exists():
            row.update({
                "status": "MISSING",
                "import_added": False,
                "parser_var": "",
                "args_added": False,
                "args_var": "",
                "contract_block_added": False,
                "fixed_notional_replacements": 0,
            })
            rows.append(row)
            continue

        original = src.read_text(encoding="utf-8-sig", errors="replace")
        patched, stats = patch_text(original, family_key)

        patched_file = patched_dir / script_name
        diff_file = diff_dir / f"{script_name}.diff"
        patched_file.write_text(patched, encoding="utf-8")

        diff = "\n".join(difflib.unified_diff(
            original.splitlines(),
            patched.splitlines(),
            fromfile=str(src),
            tofile=str(patched_file),
            lineterm="",
        ))
        diff_file.write_text(diff, encoding="utf-8")

        row.update(stats)
        row["patched_file"] = str(patched_file)
        row["diff_file"] = str(diff_file)

        if args.apply and stats["status"] == "PATCH_CANDIDATE":
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / script_name
            shutil.copy2(src, backup_file)
            src.write_text(patched, encoding="utf-8")
            row["backup_file"] = str(backup_file)
            row["applied"] = True

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "logger_sizing_patch_report.csv", index=False)

    report = []
    report.append("EDGE FACTORY LOGGER SIZING PATCHER REPORT")
    report.append("=" * 120)
    report.append(f"apply_mode: {args.apply}")
    report.append(f"out_dir: {out_dir}")
    report.append("")
    report.append("PATCH SUMMARY")
    report.append("-" * 120)
    report.append(df.to_string(index=False))
    report.append("")
    report.append("NEXT STEP")
    report.append("-" * 120)
    if args.apply:
        report.append("Applied all PATCH_CANDIDATE scripts. Now rerun position sizing contract audit.")
    else:
        report.append("Dry-run only. Review diffs. If status is PATCH_CANDIDATE for all needed loggers, run with --apply.")
        report.append(f"Diff folder: {diff_dir}")
    report.append("")
    report.append("IMPORTANT")
    report.append("-" * 120)
    report.append("If any logger says NEEDS_MANUAL_PATCH, send its diff/snippet and do not apply blindly.")
    (out_dir / "LOGGER_SIZING_PATCHER_REPORT.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))


if __name__ == "__main__":
    main()
