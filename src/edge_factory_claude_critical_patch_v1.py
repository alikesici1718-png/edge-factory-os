#!/usr/bin/env python
# -*- coding: utf-8 -*-
# EDGE_FACTORY_GATE_METADATA_START
# gate_metadata_version: 1
# gate_metadata_kind: non_behavioral_comment_block
# gate_review_source_file: gate_review_candidate_preview_latest.json
# gate_review_target_path: src/edge_factory_claude_critical_patch_v1.py
# gate_review_issue_id: MUTATION_SURFACE:src/edge_factory_claude_critical_patch_v1.py
# gate_review_classification: GATE_REVIEW_FAIL_MISSING_EXPLICIT_GATE_METADATA
# gate_review_risk: UNKNOWN
# gate_review_evidence: Mutation-like tokens: .write_text(, shutil.copy
# allowed_scope: REPO_ONLY_OS_INTELLIGENCE
# preview_only: true
# non_behavioral_comment_only: true
# runtime_touch_allowed: false
# launcher_allowed: false
# capital_change_allowed: false
# active_paper_allowed: false
# live_allowed: false
# real_orders_allowed: false
# candidate_generation_allowed: false
# family_release_allowed: false
# strategy_research_allowed: false
# holdout_access_allowed: false
# backup_delete_allowed: false
# backup_move_allowed: false
# direct_apply_allowed: false
# EDGE_FACTORY_GATE_METADATA_END

# EDGE_FACTORY_OS_EXPLICIT_GATE_METADATA_V1
# allowed_scope: REPO_ONLY_GOVERNED_TOOLING
# runtime_touch_allowed: False
# launcher_allowed: False
# capital_change_allowed: False
# live_allowed: False
# real_orders_allowed: False
# backup_delete_allowed: False
# backup_move_allowed: False
# gitignore_change_allowed: False
# requires_preview_before_apply: True
# requires_explicit_approval_before_mutation: True
# behavior_change: False
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_claude_critical_patch_v1"

RISK_MANAGER = USERDIR / "global_paper_risk_manager_v3_priority.py"

LOGGER_FILES = [
    USERDIR / "old_short_gate_aware_live_paper_logger.py",
    USERDIR / "impulse_long_gate_aware_live_paper_logger.py",
    USERDIR / "market_relative_live_paper_logger.py",
    USERDIR / "weak_market_breakdown_short_live_paper_logger.py",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def backup(path: Path, backup_dir: Path) -> Path | None:
    if not path.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    dst = backup_dir / path.name
    shutil.copy2(path, dst)
    return dst

def patch_risk_manager(path: Path) -> dict[str, Any]:
    result = {
        "file": str(path),
        "exists": path.exists(),
        "patched_signal_id_fallback": False,
        "already_patched": False,
        "notes": [],
    }

    if not path.exists():
        result["notes"].append("missing")
        return result

    txt = path.read_text(encoding="utf-8", errors="replace")

    if "EDGE_FACTORY_CANONICAL_SIGNAL_ID_FALLBACK_V1" in txt:
        result["already_patched"] = True
        result["notes"].append("already contains canonical fallback marker")
        return result

    old = '''if "signal_id" not in x.columns:
            base_time = pd.to_datetime(x.get("target_entry_time", x.get("log_time", "")), errors="coerce", utc=True).dt.strftime("%Y%m%dT%H%M%SZ")
            x["signal_id"] = x["family_key"].astype(str) + "_" + x["coin"].astype(str) + "_" + base_time
        else:
            x["signal_id"] = ""'''

    new = '''# EDGE_FACTORY_CANONICAL_SIGNAL_ID_FALLBACK_V1
        # Preserve logger-provided signal_id whenever present. Only synthesize a fallback
        # when the pending file genuinely lacks signal_id. The canonical fallback must
        # match logger format: COIN_STRATEGY_OR_FAMILY_YYYYMMDDTHHMMSSZ.
        if "signal_id" not in x.columns:
            base_time = pd.to_datetime(
                x.get("target_entry_time", x.get("signal_time", x.get("log_time", ""))),
                errors="coerce",
                utc=True
            ).dt.strftime("%Y%m%dT%H%M%SZ")

            if "strategy" in x.columns:
                id_part = x["strategy"].astype(str)
            elif "family" in x.columns:
                id_part = x["family"].astype(str)
            else:
                id_part = x["family_key"].astype(str)

            x["signal_id"] = x["coin"].astype(str) + "_" + id_part + "_" + base_time
        else:
            x["signal_id"] = x["signal_id"].astype(str)'''

    if old in txt:
        txt2 = txt.replace(old, new)
        path.write_text(txt2, encoding="utf-8")
        result["patched_signal_id_fallback"] = True
        result["notes"].append("replaced exact old signal_id fallback block")
        return result

    # Fallback regex patch if exact block differs.
    pattern = re.compile(
        r'if\s+"signal_id"\s+not\s+in\s+x\.columns:\s*\n'
        r'\s*base_time\s*=\s*pd\.to_datetime\(.*?\)\.dt\.strftime\("%Y%m%dT%H%M%SZ"\)\s*\n'
        r'\s*x\["signal_id"\]\s*=\s*x\["family_key"\]\.astype\(str\)\s*\+\s*"_"\s*\+\s*x\["coin"\]\.astype\(str\)\s*\+\s*"_"\s*\+\s*base_time\s*\n'
        r'\s*else:\s*\n'
        r'\s*x\["signal_id"\]\s*=\s*""',
        re.DOTALL
    )

    if pattern.search(txt):
        txt2 = pattern.sub(new, txt, count=1)
        path.write_text(txt2, encoding="utf-8")
        result["patched_signal_id_fallback"] = True
        result["notes"].append("replaced signal_id fallback block by regex")
    else:
        result["notes"].append("could not locate old fallback block; manual inspection needed")

    return result

def patch_logger_gate_default(path: Path) -> dict[str, Any]:
    result = {
        "file": str(path),
        "exists": path.exists(),
        "patched_require_global_gate_default": False,
        "added_no_global_gate": False,
        "already_patched": False,
        "notes": [],
    }

    if not path.exists():
        result["notes"].append("missing")
        return result

    txt = path.read_text(encoding="utf-8", errors="replace")

    if "EDGE_FACTORY_REQUIRE_GLOBAL_GATE_DEFAULT_TRUE_V1" in txt:
        result["already_patched"] = True
        result["notes"].append("already patched marker exists")
        return result

    # Common old pattern:
    # ap.add_argument("--require_global_gate", action="store_true")
    old_patterns = [
        'ap.add_argument("--require_global_gate", action="store_true")',
        'ap.add_argument("--require_global_gate", action="store_true", default=False)',
    ]

    replacement = '''# EDGE_FACTORY_REQUIRE_GLOBAL_GATE_DEFAULT_TRUE_V1
    ap.add_argument("--require_global_gate", dest="require_global_gate", action="store_true", default=True)
    ap.add_argument("--no_global_gate", dest="require_global_gate", action="store_false")'''

    patched = False
    for old in old_patterns:
        if old in txt:
            txt = txt.replace(old, replacement, 1)
            patched = True
            break

    if not patched:
        # Regex fallback, preserving indentation.
        pattern = re.compile(r'(\s*)ap\.add_argument\("--require_global_gate",\s*action="store_true"(?:,\s*default=False)?\)')
        m = pattern.search(txt)
        if m:
            indent = m.group(1)
            repl = (
                f'{indent}# EDGE_FACTORY_REQUIRE_GLOBAL_GATE_DEFAULT_TRUE_V1\n'
                f'{indent}ap.add_argument("--require_global_gate", dest="require_global_gate", action="store_true", default=True)\n'
                f'{indent}ap.add_argument("--no_global_gate", dest="require_global_gate", action="store_false")'
            )
            txt = pattern.sub(repl, txt, count=1)
            patched = True

    if patched:
        path.write_text(txt, encoding="utf-8")
        result["patched_require_global_gate_default"] = True
        result["added_no_global_gate"] = True
        result["notes"].append("require_global_gate now defaults True; --no_global_gate added")
    else:
        result["notes"].append("could not locate require_global_gate argparse line; manual inspection needed")

    return result

def scan_for_markers() -> dict[str, Any]:
    out = {}
    for p in [RISK_MANAGER] + LOGGER_FILES:
        if not p.exists():
            out[str(p)] = {"exists": False}
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        out[str(p)] = {
            "exists": True,
            "canonical_signal_id_marker": "EDGE_FACTORY_CANONICAL_SIGNAL_ID_FALLBACK_V1" in txt,
            "require_gate_marker": "EDGE_FACTORY_REQUIRE_GLOBAL_GATE_DEFAULT_TRUE_V1" in txt,
            "no_global_gate_present": "--no_global_gate" in txt,
        }
    return out

def main() -> int:
    out_dir = OUT_ROOT / f"claude_critical_patch_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir = out_dir / "backup_before_patch"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = [RISK_MANAGER] + LOGGER_FILES
    backups = {}
    for p in files:
        b = backup(p, backup_dir)
        backups[str(p)] = str(b) if b else ""

    patch_results = []
    patch_results.append(patch_risk_manager(RISK_MANAGER))
    for p in LOGGER_FILES:
        patch_results.append(patch_logger_gate_default(p))

    markers = scan_for_markers()

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "out_dir": str(out_dir),
        "backup_dir": str(backup_dir),
        "backups": backups,
        "patch_results": patch_results,
        "markers": markers,
        "restart_allowed": False,
        "next_action": "RUN_PY_COMPILE_AND_SIGNAL_ID_AUDIT_BEFORE_RESTART",
        "safety": {
            "does_not_start_master": True,
            "does_not_stop_processes": True,
            "does_not_place_orders": True,
            "does_not_change_capital": True,
            "patches_code_only": True,
        }
    }

    state_path = out_dir / "claude_critical_patch_v1_state.json"
    report_path = out_dir / "claude_critical_patch_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Claude Critical Patch v1")
    md.append("")
    md.append("## Purpose")
    md.append("- Patch signal_id fallback contract in risk manager.")
    md.append("- Make require_global_gate default True in all active loggers.")
    md.append("- Do not restart MASTER.")
    md.append("")
    md.append("## Results")
    for r in patch_results:
        md.append(f"- `{r['file']}`: {r}")
    md.append("")
    md.append("## Next")
    md.append("Run py_compile and signal_id contract audit before restart.")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY CLAUDE CRITICAL PATCH v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"out_dir   : {out_dir}")
    print(f"backup_dir: {backup_dir}")
    print("restart_allowed: False")
    print("next_action: RUN_PY_COMPILE_AND_SIGNAL_ID_AUDIT_BEFORE_RESTART")
    print()
    print("PATCH RESULTS")
    print("-" * 100)
    for r in patch_results:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    print()
    print("MARKERS")
    print("-" * 100)
    print(json.dumps(markers, indent=2, ensure_ascii=False))
    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
