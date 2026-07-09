"""
Patches live paper logger scripts to replace the equity-fraction notional line with a call to resolve_family_notional(), injecting dynamic per-family position sizing into each of the four strategy logger files.
Operates in dry-run mode by default; use --apply to back up originals and write patched files.
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


# =============================================================================
# EDGE FACTORY LOGGER SIZING PATCHER v2
# =============================================================================
#
# This v2 patches the real notional line found in the snippets:
#
#     notional = self.equity * self.args.paper_fraction
#
# into:
#
#     default_notional = self.equity * self.args.paper_fraction
#     notional = resolve_family_notional(...)
#
# Safety:
#   Dry-run by default.
#   --apply backs up originals before overwriting.
#
# Usage:
#   python "C:\Users\alike\edge_factory_logger_sizing_patcher_v2.py"
#   python "C:\Users\alike\edge_factory_logger_sizing_patcher_v2.py" --apply
# =============================================================================


LOGGER_SCRIPTS = {
    "old_short": "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": "market_relative_live_paper_logger.py",
    "weak_market_short": "weak_market_breakdown_short_live_paper_logger.py",
}

TARGET_LINE_RE = re.compile(
    r"^(\s*)notional\s*=\s*self\.equity\s*\*\s*self\.args\.paper_fraction\s*$",
    re.MULTILINE,
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


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
    # Current scripts use ap.add_argument(...)
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

    # Best insertion: after the existing --paper_fraction arg if present.
    for line in lines:
        out.append(line)
        if not inserted and "--paper_fraction" in line:
            out.extend(add_lines)
            inserted = True

    # Fallback: before parse_args.
    if not inserted:
        out = []
        for line in lines:
            if not inserted and ".parse_args(" in line:
                out.extend(add_lines)
                inserted = True
            out.append(line)

    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), inserted


def replace_notional_line(text: str, family_key: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        indent = m.group(1)
        return (
            f"{indent}default_notional = self.equity * self.args.paper_fraction\n"
            f"{indent}notional = resolve_family_notional(\n"
            f'{indent}    "{family_key}",\n'
            f"{indent}    default_notional=default_notional,\n"
            f"{indent}    sizing_contract_path=self.args.sizing_contract,\n"
            f"{indent}    base_equity=self.equity,\n"
            f"{indent})"
        )

    return TARGET_LINE_RE.sub(repl, text), count


def patch_text(text: str, family_key: str) -> tuple[str, dict]:
    stats = {
        "import_added": False,
        "parser_var": "",
        "args_added": False,
        "notional_line_replacements": 0,
        "status": "UNKNOWN",
    }

    t, changed = insert_import(text)
    stats["import_added"] = changed

    parser_var = find_parser_var(t)
    stats["parser_var"] = parser_var or ""
    t, changed = insert_argparse_args(t, parser_var)
    stats["args_added"] = changed

    t, n = replace_notional_line(t, family_key)
    stats["notional_line_replacements"] = n

    if not parser_var:
        stats["status"] = "NEEDS_MANUAL_PATCH_NO_ARGPARSE"
    elif n == 0:
        stats["status"] = "NEEDS_MANUAL_PATCH_TARGET_LINE_NOT_FOUND"
    else:
        stats["status"] = "PATCH_CANDIDATE"

    return t, stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Patch family paper loggers to consume position_sizing_contract.json.")
    ap.add_argument("--user_dir", default=r"C:\Users\alike")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_logger_sizing_patch_v2")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    user_dir = Path(args.user_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    patched_dir = out_dir / "patched"
    diff_dir = out_dir / "diffs"
    backup_dir = out_dir / f"backup_{utc_stamp()}"
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
                "notional_line_replacements": 0,
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
    df.to_csv(out_dir / "logger_sizing_patch_report_v2.csv", index=False)

    report = []
    report.append("EDGE FACTORY LOGGER SIZING PATCHER v2 REPORT")
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
        report.append('python "C:\\Users\\alike\\edge_factory_position_sizing_contract.py"')
    else:
        report.append("Dry-run only. If all important loggers are PATCH_CANDIDATE, run with --apply.")
        report.append(f"Diff folder: {diff_dir}")
    report.append("")
    report.append("IMPORTANT")
    report.append("-" * 120)
    report.append("Do not start paper/live until position sizing audit says needs_patch=False for all active loggers.")
    (out_dir / "LOGGER_SIZING_PATCHER_V2_REPORT.txt").write_text("\n".join(report), encoding="utf-8")

    print("\n" + "\n".join(report))


if __name__ == "__main__":
    main()
