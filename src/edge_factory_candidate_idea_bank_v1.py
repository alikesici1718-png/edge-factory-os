#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Persistent ledger for storing, querying, and managing candidate strategy idea entries for the Edge Factory research pipeline. Reads and appends to a JSONL master ledger file and exposes CLI commands to add ideas, list them, and check contract-readiness of each entry.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_candidate_idea_bank_v1"
MASTER_LEDGER = OUT_ROOT / "candidate_idea_bank_master_ledger.jsonl"

REQUIRED_FOR_CONTRACT = [
    "candidate_key",
    "family_key",
    "side",
    "edge",
    "entry_rule",
    "exit_rule",
    "hold_time",
]

RECOMMENDED = [
    "regime",
    "why",
    "failure_modes",
    "required_columns",
    "source_files",
    "lookback_window",
    "cooldown",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def slugify(x: str) -> str:
    x = (x or "").strip().lower()
    x = re.sub(r"[^a-z0-9_]+", "_", x)
    x = re.sub(r"_+", "_", x).strip("_")
    return x

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def nonempty(x: Any) -> bool:
    if x is None:
        return False
    if isinstance(x, str):
        return bool(x.strip())
    if isinstance(x, list):
        return len(x) > 0
    return True

def score_idea(idea: dict[str, Any]) -> dict[str, Any]:
    missing_required = [k for k in REQUIRED_FOR_CONTRACT if not nonempty(idea.get(k))]
    missing_recommended = [k for k in RECOMMENDED if not nonempty(idea.get(k))]

    required_score = (len(REQUIRED_FOR_CONTRACT) - len(missing_required)) / len(REQUIRED_FOR_CONTRACT)
    recommended_score = (len(RECOMMENDED) - len(missing_recommended)) / len(RECOMMENDED)
    readiness_score = round((0.75 * required_score + 0.25 * recommended_score) * 100, 2)

    if missing_required:
        status = "IDEA_INCOMPLETE"
        next_action = "FILL_REQUIRED_FIELDS_BEFORE_CONTRACT"
        contract_ready = False
    elif missing_recommended:
        status = "IDEA_CONTRACT_READY_BUT_WEAK_CONTEXT"
        next_action = "GENERATE_CONTRACT_ALLOWED_BUT_CONTEXT_SHOULD_BE_FILLED"
        contract_ready = True
    else:
        status = "IDEA_CONTRACT_READY"
        next_action = "GENERATE_OFFLINE_EXPERIMENT_CONTRACT"
        contract_ready = True

    return {
        "readiness_score": readiness_score,
        "status": status,
        "contract_ready": contract_ready,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "next_action": next_action,
    }

def build_generator_command(idea: dict[str, Any]) -> str:
    def q(x):
        x = str(x or "").replace('"', "'")
        return f'"{x}"'

    parts = [
        'python -u "C:\\Users\\alike\\edge_factory_candidate_contract_generator_v1.py"',
        "--candidate_key", q(idea.get("candidate_key", "")),
        "--family_key", q(idea.get("family_key", "")),
        "--side", q(idea.get("side", "short")),
        "--edge", q(idea.get("edge", "")),
        "--regime", q(idea.get("regime", "")),
        "--why", q(idea.get("why", "")),
        "--failure_modes", q(idea.get("failure_modes", "")),
        "--universe", q(idea.get("universe", "OKX USDT swaps ready universe")),
        "--timeframe", q(idea.get("timeframe", "1h candles")),
        "--lookback_window", q(idea.get("lookback_window", "")),
        "--source_files", q(idea.get("source_files", "")),
        "--required_columns", q(idea.get("required_columns", "")),
        "--entry_rule", q(idea.get("entry_rule", "")),
        "--exit_rule", q(idea.get("exit_rule", "")),
        "--hold_time", q(idea.get("hold_time", "")),
        "--cooldown", q(idea.get("cooldown", "")),
    ]
    return " ".join(parts)

def main() -> int:
    ap = argparse.ArgumentParser(description="Edge Factory Candidate Idea Bank v1.")
    ap.add_argument("--candidate_key", default="")
    ap.add_argument("--family_key", default="")
    ap.add_argument("--side", default="short", choices=["long", "short", "both"])
    ap.add_argument("--edge", default="")
    ap.add_argument("--regime", default="")
    ap.add_argument("--why", default="")
    ap.add_argument("--failure_modes", default="")
    ap.add_argument("--universe", default="OKX USDT swaps ready universe")
    ap.add_argument("--timeframe", default="1h candles")
    ap.add_argument("--lookback_window", default="")
    ap.add_argument("--source_files", default="")
    ap.add_argument("--required_columns", default="")
    ap.add_argument("--entry_rule", default="")
    ap.add_argument("--exit_rule", default="")
    ap.add_argument("--hold_time", default="")
    ap.add_argument("--cooldown", default="")
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"candidate_idea_bank_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    registry_dir = latest_dir(WORKSPACE / "edge_factory_candidate_lifecycle_registry_v1", "candidate_lifecycle_registry_v1_")
    registry = read_json(registry_dir / "candidate_lifecycle_registry_v1_state.json" if registry_dir else None)

    provided_any = bool(args.candidate_key or args.edge or args.entry_rule or args.exit_rule)

    new_idea = None
    if provided_any:
        new_idea = {
            "created_at": now_iso(),
            "candidate_key": slugify(args.candidate_key),
            "family_key": slugify(args.family_key),
            "side": args.side,
            "edge": args.edge,
            "regime": args.regime,
            "why": args.why,
            "failure_modes": args.failure_modes,
            "universe": args.universe,
            "timeframe": args.timeframe,
            "lookback_window": args.lookback_window,
            "source_files": args.source_files,
            "required_columns": args.required_columns,
            "entry_rule": args.entry_rule,
            "exit_rule": args.exit_rule,
            "hold_time": args.hold_time,
            "cooldown": args.cooldown,
            "source": "manual_cli",
            "live_allowed": False,
            "active_paper_allowed": False,
            "capital_change_allowed": False,
        }
        new_idea.update(score_idea(new_idea))
        new_idea["contract_generator_command"] = build_generator_command(new_idea)
        append_jsonl(MASTER_LEDGER, new_idea)

    ledger_rows = read_jsonl(MASTER_LEDGER)

    archived_candidates = []
    for c in registry.get("candidates", []):
        if c.get("lifecycle_status") == "ARCHIVE_WAIT":
            archived_candidates.append({
                "candidate_key": c.get("candidate"),
                "status": "ARCHIVE_WAIT",
                "reason": c.get("blockers", []),
                "contract_ready": False,
                "next_action": "DO_NOT_PROMOTE_WITHOUT_NEW_CONTRACT_AND_RESULT_EVIDENCE",
            })

    if ledger_rows:
        idea_df = pd.DataFrame(ledger_rows)
    else:
        idea_df = pd.DataFrame(columns=[
            "candidate_key", "family_key", "side", "status", "readiness_score",
            "contract_ready", "missing_required", "missing_recommended", "next_action"
        ])

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "idea_bank_status": "IDEA_BANK_UPDATED" if provided_any else "IDEA_BANK_READY_WAITING_FOR_IDEAS",
        "new_idea_added": bool(new_idea),
        "new_idea": new_idea,
        "idea_count": len(ledger_rows),
        "archived_candidates": archived_candidates,
        "master_ledger": str(MASTER_LEDGER),
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Idea bank does not run experiments.",
            "Idea bank does not touch MASTER_UPPER_SYSTEM.",
            "Idea bank does not start/stop processes.",
            "Idea bank does not promote candidates.",
            "Idea bank does not place orders.",
            "Idea bank only scores and stores candidate ideas.",
        ],
    }

    state_path = out_dir / "candidate_idea_bank_v1_state.json"
    ideas_csv = out_dir / "candidate_idea_bank_v1_ideas.csv"
    archive_csv = out_dir / "candidate_idea_bank_v1_archived_candidates.csv"
    report_path = out_dir / "candidate_idea_bank_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    idea_df.to_csv(ideas_csv, index=False)
    pd.DataFrame(archived_candidates).to_csv(archive_csv, index=False)

    md = []
    md.append("# Edge Factory Candidate Idea Bank v1")
    md.append("")
    md.append(f"Status: `{state['idea_bank_status']}`")
    md.append(f"Idea count: `{len(ledger_rows)}`")
    md.append("")
    if new_idea:
        md.append("## New idea")
        md.append(f"- `{new_idea['candidate_key']}` — `{new_idea['status']}` score `{new_idea['readiness_score']}`")
        md.append("")
        if new_idea["contract_ready"]:
            md.append("## Contract generator command")
            md.append("```powershell")
            md.append(new_idea["contract_generator_command"])
            md.append("```")
    else:
        md.append("No new idea provided. Use CLI args to add one.")
    md.append("")
    md.append("## Archived candidates")
    for c in archived_candidates:
        md.append(f"- `{c['candidate_key']}` — `{c['status']}`")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY CANDIDATE IDEA BANK v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"idea_bank_status: {state['idea_bank_status']}")
    print(f"new_idea_added: {bool(new_idea)}")
    print(f"idea_count: {len(ledger_rows)}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("IDEAS")
    print("-" * 100)
    if idea_df.empty:
        print("No ideas yet. Add one with --candidate_key/--family_key/--edge/--entry_rule/--exit_rule/--hold_time.")
    else:
        cols = ["candidate_key", "family_key", "side", "status", "readiness_score", "contract_ready", "next_action"]
        cols = [c for c in cols if c in idea_df.columns]
        print(idea_df[cols].tail(20).to_string(index=False))

    print()
    print("ARCHIVED CANDIDATES")
    print("-" * 100)
    if archived_candidates:
        print(pd.DataFrame(archived_candidates).to_string(index=False))
    else:
        print("None")

    if new_idea and new_idea.get("contract_ready"):
        print()
        print("CONTRACT GENERATOR COMMAND")
        print("-" * 100)
        print(new_idea["contract_generator_command"])

    print()
    print(f"State  : {state_path}")
    print(f"Ideas  : {ideas_csv}")
    print(f"Archive: {archive_csv}")
    print(f"Report : {report_path}")

if __name__ == "__main__":
    main()
