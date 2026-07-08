#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_claude_audit_export_v1"

MAX_MD_CHARS = 240_000

CODE_FILES = [
    # MASTER launcher / runtime / risk manager
    USERDIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1",
    USERDIR / "global_paper_risk_manager_v4_config.py",
    USERDIR / "global_paper_risk_manager_v3_priority.py",
    USERDIR / "sizing_contract_runtime.py",

    # Active family loggers
    USERDIR / "old_short_gate_aware_live_paper_logger.py",
    USERDIR / "impulse_long_gate_aware_live_paper_logger.py",
    USERDIR / "market_relative_live_paper_logger.py",
    USERDIR / "weak_market_breakdown_short_live_paper_logger.py",

    # MASTER monitoring
    USERDIR / "edge_factory_live_health_check_v5.py",
    USERDIR / "edge_factory_live_performance_analyzer_v3.py",
    USERDIR / "edge_factory_live_decision_dashboard.py",

    # OS runtime / supervision
    USERDIR / "edge_factory_os_autopilot_loop_v4.py",
    USERDIR / "edge_factory_os_command_center_v1.py",
    USERDIR / "edge_factory_os_supervisor_v1.py",
    USERDIR / "edge_factory_os_lifecycle_queue_v1.py",
    USERDIR / "edge_factory_os_invariant_guard_v1.py",
    USERDIR / "edge_factory_os_process_watchdog_v1.py",
    USERDIR / "edge_factory_os_recovery_manifest_v2.py",
    USERDIR / "edge_factory_os_research_brain_v1.py",

    # Contract / interface / lifecycle chain
    USERDIR / "edge_factory_offline_experiment_contract_schema_v1.py",
    USERDIR / "edge_factory_offline_experiment_contract_validator_v1.py",
    USERDIR / "edge_factory_offline_experiment_queue_v1.py",
    USERDIR / "edge_factory_os_interface_specs_v1.py",
    USERDIR / "edge_factory_contract_to_runner_adapter_v1.py",
    USERDIR / "edge_factory_result_to_lifecycle_adapter_v1.py",
    USERDIR / "edge_factory_candidate_contract_generator_v1.py",
    USERDIR / "edge_factory_candidate_contract_artifact_planner_v1.py",

    # Idea / learning / selector chain
    USERDIR / "edge_factory_candidate_idea_bank_v1.py",
    USERDIR / "edge_factory_candidate_idea_seeder_v1.py",
    USERDIR / "edge_factory_candidate_idea_prioritizer_v1.py",
    USERDIR / "edge_factory_os_research_learning_controller_v1.py",
    USERDIR / "edge_factory_learning_aware_candidate_selector_v1.py",
    USERDIR / "edge_factory_learning_aware_candidate_selector_v2.py",
    USERDIR / "edge_factory_research_route_decision_v1.py",
    USERDIR / "edge_factory_orthogonal_idea_seeder_v2.py",

    # Offline runner / data / feature pipeline
    USERDIR / "edge_factory_offline_runner_request_preflight_auditor_v1.py",
    USERDIR / "edge_factory_offline_runner_data_resolver_v1.py",
    USERDIR / "edge_factory_candle_source_locator_v1.py",
    USERDIR / "edge_factory_offline_runner_data_source_binding_v1.py",
    USERDIR / "edge_factory_feature_panel_build_planner_v1.py",
    USERDIR / "edge_factory_feature_panel_builder_selftest_v1.py",
    USERDIR / "edge_factory_feature_panel_builder_v1.py",
    USERDIR / "edge_factory_feature_panel_quality_auditor_v1.py",
    USERDIR / "edge_factory_offline_runner_plan_v1.py",
    USERDIR / "edge_factory_offline_runner_selftest_controller_v1.py",
    USERDIR / "edge_factory_offline_candidate_selftest_triage_v1.py",
    USERDIR / "edge_factory_learning_aware_offline_candidate_pipeline_v1.py",

    # Candidate diagnostics / strict validation
    USERDIR / "edge_factory_post_impulse_threshold_hold_diagnostic_v1.py",
    USERDIR / "edge_factory_post_impulse_strict_validation_v1.py",
    USERDIR / "edge_factory_strict_validation_learning_finalizer_v1.py",
]

CONFIG_FILES = [
    WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM" / "family_config.json",
    WORKSPACE / "edge_factory_position_sizing_contract" / "position_sizing_contract.json",
    WORKSPACE / "edge_factory_os_recovery_manifest_v2" / "edge_factory_os_recovery_manifest_latest.json",
    WORKSPACE / "edge_factory_os_recovery_manifest_v2" / "edge_factory_os_recovery_manifest_latest.md",
    WORKSPACE / "edge_factory_os_autopilot_loop_v4" / "edge_factory_os_autopilot_v4_latest_state.json",
    WORKSPACE / "edge_factory_os_autopilot_loop_v4" / "edge_factory_os_autopilot_v4_latest_status.txt",
]

LATEST_STATE_DIRS = [
    "edge_factory_os_command_center_v1",
    "edge_factory_os_supervisor_v1",
    "edge_factory_os_lifecycle_queue_v1",
    "edge_factory_os_invariant_guard_v1",
    "edge_factory_candidate_idea_bank_v1",
    "edge_factory_learning_aware_candidate_selector_v2",
    "edge_factory_research_route_decision_v1",
    "edge_factory_os_research_learning_controller_v1",
    "edge_factory_strict_validation_learning_finalizer_v1",
    "edge_factory_feature_panel_quality_auditor_v1",
    "edge_factory_learning_aware_offline_candidate_pipeline_v1",
    "edge_factory_post_impulse_threshold_hold_diagnostic_v1",
    "edge_factory_post_impulse_strict_validation_v1",
]

TAIL_FILES = [
    WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM" / "global_gate_decisions.csv",
    WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM" / "global_risk_snapshot.csv",
]

SECRET_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|passphrase|password|token|private[_-]?key|access[_-]?key)\s*[:=]\s*["\']?[^"\'\s,}\]]+'),
    re.compile(r'(?i)("?(api[_-]?key|secret|passphrase|password|token|private[_-]?key|access[_-]?key)"?\s*:\s*)"(.*?)"'),
    re.compile(r'(?i)(OKX|BINANCE|BYBIT|KUCOIN)[A-Z0-9_\-]*\s*[:=]\s*["\']?[^"\'\s,}\]]+'),
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_name(path: Path) -> str:
    s = str(path).replace(":", "").replace("\\", "__").replace("/", "__")
    s = re.sub(r"[^A-Za-z0-9_.\-]+", "_", s)
    return s[-180:]

def lang_for(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".py":
        return "python"
    if ext == ".ps1":
        return "powershell"
    if ext == ".json":
        return "json"
    if ext == ".md":
        return "markdown"
    if ext == ".csv":
        return "csv"
    if ext == ".txt":
        return "text"
    return "text"

def redact(text: str) -> str:
    out = text
    for pat in SECRET_PATTERNS:
        def repl(m):
            g = m.group(0)
            if ":" in g:
                key = g.split(":", 1)[0]
                return key + ': "[REDACTED_SECRET]"'
            if "=" in g:
                key = g.split("=", 1)[0]
                return key + '= "[REDACTED_SECRET]"'
            return "[REDACTED_SECRET]"
        out = pat.sub(repl, out)

    # Redact obvious long credential-looking quoted strings only when near sensitive words.
    lines = []
    for line in out.splitlines():
        if re.search(r"(?i)api|secret|pass|token|key", line):
            line = re.sub(r'(["\'])[A-Za-z0-9_\-]{24,}(["\'])', r'\1[REDACTED_SECRET]\2', line)
        lines.append(line)
    return "\n".join(lines)

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[READ_ERROR] {repr(e)}"

def tail_text(path: Path, max_lines: int = 200) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-max_lines:])
    except Exception as e:
        return f"[TAIL_READ_ERROR] {repr(e)}"

def latest_files_in_dir(root: Path) -> list[Path]:
    if not root.exists():
        return []
    candidates = []
    patterns = [
        "*state.json",
        "*report.md",
        "*latest.json",
        "*latest.md",
        "*policy*.json",
        "*blocklist*.json",
        "*directive*.json",
    ]
    for pat in patterns:
        candidates.extend(root.rglob(pat))
    # keep most recent 6 per dir to avoid huge bundle
    candidates = sorted(set(candidates), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[:6]

def collect_process_snapshot(out_dir: Path) -> Path:
    p = out_dir / "process_snapshot_edge_factory.txt"
    cmd = r"""
Get-CimInstance Win32_Process |
Where-Object { $_.CommandLine -match 'edge_factory|MASTER_UPPER_SYSTEM|global_paper_risk|gate_aware|live_paper_logger' } |
Select-Object ProcessId, Name, CommandLine |
Format-List
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=30,
        )
        txt = result.stdout + "\n\nSTDERR:\n" + result.stderr
    except Exception as e:
        txt = f"[PROCESS_SNAPSHOT_ERROR] {repr(e)}"
    p.write_text(redact(txt), encoding="utf-8")
    return p

def collect_tree_snapshot(out_dir: Path) -> Path:
    p = out_dir / "workspace_tree_snapshot_limited.txt"
    lines = []
    important = [
        WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM",
        WORKSPACE / "edge_factory_feature_panels",
        WORKSPACE / "edge_factory_os_research_learning_controller_v1",
        WORKSPACE / "edge_factory_learning_aware_candidate_selector_v2",
        WORKSPACE / "edge_factory_research_route_decision_v1",
        WORKSPACE / "edge_factory_strict_validation_learning_finalizer_v1",
    ]

    for root in important:
        lines.append(f"\n# {root}")
        if not root.exists():
            lines.append("MISSING")
            continue
        count = 0
        for x in root.rglob("*"):
            if count >= 250:
                lines.append("... truncated ...")
                break
            if x.is_file():
                try:
                    size = x.stat().st_size
                except Exception:
                    size = -1
                # avoid raw parquet/csv spam, but show their existence
                lines.append(f"{x} | {size} bytes")
                count += 1
    p.write_text("\n".join(lines), encoding="utf-8")
    return p

def add_file_entry(entries: list[dict[str, Any]], path: Path, category: str, mode: str = "full") -> None:
    exists = path.exists()
    info = {
        "category": category,
        "path": str(path),
        "exists": exists,
        "mode": mode,
        "size_bytes": path.stat().st_size if exists else None,
        "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat() if exists else None,
        "content": "",
    }
    if exists and path.is_file():
        if mode == "tail":
            info["content"] = redact(tail_text(path))
        else:
            info["content"] = redact(read_text(path))
    entries.append(info)

def write_markdown_parts(entries: list[dict[str, Any]], out_dir: Path) -> list[Path]:
    header = f"""# Edge Factory Claude Audit Bundle

Generated: {now_iso()}

Workspace: `{WORKSPACE}`

Purpose: external code/system audit.

Safety statement:
- This bundle should contain code/config/state only.
- Large market data files are intentionally excluded.
- Secrets/API keys/tokens/passphrases are redacted by pattern.
- Active paper/live/capital permissions should remain false unless explicitly reviewed.
- Ask Claude to be hostile and find bugs, not to praise the system.

Suggested audit focus:
1. MASTER runtime safety and gate logic.
2. Risk manager / logger consistency.
3. Position sizing contract handling.
4. Global gate matching by family_key + signal_id.
5. Autopilot/supervisor invariant logic.
6. Offline research pipeline correctness.
7. Learning memory / selector policy correctness.
8. Leakage / lookahead / overfit risks.
9. Places where file discovery could select stale outputs.
10. Any code path that could touch live/API/capital unexpectedly.

---

"""

    parts = []
    current = header
    part_idx = 1

    for e in entries:
        section = []
        section.append(f"\n\n## {e['category']}: `{e['path']}`\n")
        section.append(f"- exists: `{e['exists']}`\n")
        section.append(f"- mode: `{e['mode']}`\n")
        section.append(f"- size_bytes: `{e['size_bytes']}`\n")
        section.append(f"- modified_utc: `{e['modified_utc']}`\n\n")

        if e["exists"] and e["content"]:
            lang = lang_for(Path(e["path"]))
            section.append(f"```{lang}\n")
            section.append(e["content"])
            if not e["content"].endswith("\n"):
                section.append("\n")
            section.append("```\n")
        elif not e["exists"]:
            section.append("```text\nMISSING\n```\n")
        else:
            section.append("```text\nEMPTY_OR_UNREADABLE\n```\n")

        sec = "".join(section)

        if len(current) + len(sec) > MAX_MD_CHARS and current.strip():
            part_path = out_dir / f"CLAUDE_AUDIT_BUNDLE_PART_{part_idx:03d}.md"
            part_path.write_text(current, encoding="utf-8")
            parts.append(part_path)
            part_idx += 1
            current = header + f"\n\n# Continuation part {part_idx}\n\n"

        current += sec

    if current.strip():
        part_path = out_dir / f"CLAUDE_AUDIT_BUNDLE_PART_{part_idx:03d}.md"
        part_path.write_text(current, encoding="utf-8")
        parts.append(part_path)

    return parts

def main() -> int:
    out_dir = OUT_ROOT / f"claude_audit_export_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    redacted_dir = out_dir / "redacted_files"
    redacted_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []

    # Explicit code files
    for path in CODE_FILES:
        add_file_entry(entries, path, "CODE", "full")

    # Explicit configs
    for path in CONFIG_FILES:
        add_file_entry(entries, path, "CONFIG_OR_LATEST_STATE", "full")

    # Latest state/report files by directory
    for d in LATEST_STATE_DIRS:
        root = WORKSPACE / d
        for p in latest_files_in_dir(root):
            add_file_entry(entries, p, f"LATEST_ARTIFACT:{d}", "full")

    # CSV tails only
    for p in TAIL_FILES:
        add_file_entry(entries, p, "CSV_TAIL_RUNTIME", "tail")

    # Process and tree snapshots
    process_snapshot = collect_process_snapshot(out_dir)
    tree_snapshot = collect_tree_snapshot(out_dir)
    add_file_entry(entries, process_snapshot, "PROCESS_SNAPSHOT", "full")
    add_file_entry(entries, tree_snapshot, "TREE_SNAPSHOT_LIMITED", "full")

    # Write redacted individual files
    for e in entries:
        if not e["exists"]:
            continue
        src = Path(e["path"])
        out_name = safe_name(src)
        if src.suffix:
            out_file = redacted_dir / out_name
        else:
            out_file = redacted_dir / (out_name + ".txt")
        out_file.write_text(e["content"], encoding="utf-8")
        e["redacted_copy"] = str(out_file)

    # Inventory
    inventory_path = out_dir / "claude_audit_inventory.csv"
    with inventory_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category", "path", "exists", "mode", "size_bytes",
                "modified_utc", "redacted_copy"
            ],
        )
        writer.writeheader()
        for e in entries:
            writer.writerow({
                "category": e.get("category"),
                "path": e.get("path"),
                "exists": e.get("exists"),
                "mode": e.get("mode"),
                "size_bytes": e.get("size_bytes"),
                "modified_utc": e.get("modified_utc"),
                "redacted_copy": e.get("redacted_copy", ""),
            })

    # Markdown bundle parts
    parts = write_markdown_parts(entries, out_dir)

    # Claude prompt
    prompt = f"""Claude, I want a hostile audit of this Edge Factory OS trading research/paper system.

Please do NOT praise it. Find failure modes.

Context:
- MASTER_UPPER_SYSTEM is a gate-aware paper trading system.
- Live trading / real orders / capital changes should be disabled.
- Active paper promotion should remain blocked unless validation gates pass.
- Offline research pipeline should not touch the running MASTER system.
- The system has learning memory, candidate selector, strict validation, and guarded candidate routing.
- Several candidate strategies failed; the important question is whether the OS correctly prevents bad candidates from promotion and whether code paths can accidentally touch runtime/live/capital.

Audit tasks:
1. Identify any path that can accidentally place live orders or alter capital.
2. Check whether MASTER runtime scripts and offline research scripts are properly separated.
3. Check risk manager / logger / gate contract consistency.
4. Check family_key + signal_id matching and stale/duplicate signal handling.
5. Check if global gate decision handling can deadlock or allow wrong entries.
6. Check if offline data discovery can accidentally use generated outputs instead of raw data.
7. Check for lookahead/leakage in feature panel building and validation.
8. Check whether diagnostic threshold searches are correctly prevented from promotion without strict validation.
9. Check if selector learning/blocklist logic can be bypassed by similar renamed candidates.
10. Propose concrete fixes with file names and code-level patches.

Attached are markdown bundle parts and redacted source files.
"""
    prompt_path = out_dir / "PROMPT_TO_CLAUDE.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    # Zip
    zip_base = str(out_dir)
    zip_path = shutil.make_archive(zip_base, "zip", out_dir)

    manifest = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "out_dir": str(out_dir),
        "inventory": str(inventory_path),
        "prompt_to_claude": str(prompt_path),
        "bundle_parts": [str(p) for p in parts],
        "redacted_files_dir": str(redacted_dir),
        "zip_path": zip_path,
        "entry_count": len(entries),
        "existing_entry_count": sum(1 for e in entries if e["exists"]),
        "missing_entry_count": sum(1 for e in entries if not e["exists"]),
        "safety": {
            "secrets_redacted_by_pattern": True,
            "large_market_data_excluded": True,
            "csv_runtime_files_tail_only": True,
        },
    }

    manifest_path = out_dir / "claude_audit_export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print("EDGE FACTORY CLAUDE AUDIT EXPORTER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"out_dir   : {out_dir}")
    print(f"entry_count: {manifest['entry_count']}")
    print(f"existing   : {manifest['existing_entry_count']}")
    print(f"missing    : {manifest['missing_entry_count']}")
    print()
    print("BUNDLE PARTS")
    print("-" * 100)
    for p in parts:
        print(p)
    print()
    print(f"Prompt   : {prompt_path}")
    print(f"Inventory: {inventory_path}")
    print(f"Manifest : {manifest_path}")
    print(f"Zip      : {zip_path}")
    print()
    print("IMPORTANT:")
    print("- Claude'a önce PROMPT_TO_CLAUDE.txt içeriğini ver.")
    print("- Sonra CLAUDE_AUDIT_BUNDLE_PART_*.md dosyalarını yükle/yapıştır.")
    print("- Zip'i yükleyebiliyorsan zip daha temiz.")
    print("- Yine de API key/secret yok mu diye hızlıca kontrol et.")

if __name__ == "__main__":
    main()
