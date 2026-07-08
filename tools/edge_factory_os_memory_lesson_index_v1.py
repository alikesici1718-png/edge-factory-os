#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_memory_lesson_index_v1"

MEMORY_JSONL = WORKSPACE / "edge_factory_os_research_learning_controller_v1" / "edge_factory_research_learning_memory_master.jsonl"

SCAN_ROOTS = [
    WORKSPACE / "edge_factory_strict_validation_learning_finalizer_v1",
    WORKSPACE / "edge_factory_os_research_learning_controller_v1",
    WORKSPACE / "edge_factory_learning_aware_candidate_selector_v2",
    WORKSPACE / "edge_factory_research_route_decision_v1",
    WORKSPACE / "edge_factory_candidate_idea_bank_v1",
    WORKSPACE / "edge_factory_candidate_lifecycle_registry_v1",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"__parse_error__": line[:500]})
    return rows

def latest_files(root: Path, pattern: str, limit: int = 30) -> list[Path]:
    if not root.exists():
        return []
    files = list(root.rglob(pattern))
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]

def extract_candidate_key(d: dict) -> str:
    for k in ["candidate_key", "candidate", "base", "top_candidate"]:
        v = d.get(k)
        if isinstance(v, str) and v and v != "UNKNOWN":
            return v
    return "UNKNOWN"

def norm_list(x):
    if isinstance(x, list):
        return [str(v) for v in x]
    if isinstance(x, str) and x:
        return [x]
    return []

def main() -> int:
    out_dir = OUT_ROOT / f"os_memory_lesson_index_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    memory_rows = read_jsonl(MEMORY_JSONL)

    candidate_records = []
    family_records = {}
    hard_blocks = set()
    failure_tags = set()
    lessons = []
    source_files = []

    # 1) JSONL learning memory
    for row in memory_rows:
        candidate = extract_candidate_key(row)
        family = str(row.get("family_key") or row.get("family") or "UNKNOWN")
        decision = str(row.get("decision_learned") or row.get("lifecycle_update") or row.get("validation_status") or "")
        tags = norm_list(row.get("failure_tags"))
        row_lessons = norm_list(row.get("lessons"))
        blocks = norm_list(row.get("hard_blocks"))

        for t in tags:
            failure_tags.add(t)
        for b in blocks:
            hard_blocks.add(b)
        for l in row_lessons:
            lessons.append({
                "candidate": candidate,
                "family": family,
                "lesson": l,
                "source": str(MEMORY_JSONL),
            })

        if candidate != "UNKNOWN":
            candidate_records.append({
                "candidate": candidate,
                "family": family,
                "status": str(row.get("lifecycle_update") or row.get("lifecycle_status") or "LEARNED"),
                "decision": decision,
                "failure_tags": tags,
                "hard_blocks": blocks,
                "source": str(MEMORY_JSONL),
            })

    # 2) scan latest state/archive/blocklist JSONs
    patterns = [
        "*state.json",
        "*archive_policy*.json",
        "*blocklist*.json",
        "*directive*.json",
        "*selector*.json",
        "*decision*.json",
    ]

    for root in SCAN_ROOTS:
        for pattern in patterns:
            for p in latest_files(root, pattern, limit=10):
                d = read_json(p)
                source_files.append(str(p))

                candidate = extract_candidate_key(d)
                family = str(d.get("family_key") or d.get("family") or "UNKNOWN")

                tags = []
                blocks = []

                for key in ["failure_tags", "blockers", "hard_blocks", "exact_blocks", "family_cooldowns"]:
                    vals = norm_list(d.get(key))
                    if "block" in key or "cooldown" in key:
                        blocks.extend(vals)
                    else:
                        tags.extend(vals)

                for t in tags:
                    failure_tags.add(t)
                for b in blocks:
                    hard_blocks.add(b)

                if candidate != "UNKNOWN":
                    candidate_records.append({
                        "candidate": candidate,
                        "family": family,
                        "status": str(d.get("lifecycle_status") or d.get("validation_status") or d.get("selector_status") or d.get("route_status") or "SCANNED"),
                        "decision": str(d.get("decision") or d.get("next_action") or ""),
                        "failure_tags": tags,
                        "hard_blocks": blocks,
                        "source": str(p),
                    })

                for l in norm_list(d.get("lessons")):
                    lessons.append({
                        "candidate": candidate,
                        "family": family,
                        "lesson": l,
                        "source": str(p),
                    })

    # Deduplicate candidate records lightly.
    dedup = {}
    for r in candidate_records:
        key = (r["candidate"], r["family"], r["status"], r["decision"], r["source"])
        dedup[key] = r
    candidate_records = list(dedup.values())

    exact_candidate_blocks = set()
    family_cooldowns = set()

    for r in candidate_records:
        cand = r["candidate"]
        fam = r["family"]
        status = (r["status"] + " " + r["decision"] + " " + " ".join(r["hard_blocks"])).upper()

        if any(x in status for x in ["ARCHIVE", "BLOCK", "FAIL", "DO_NOT_PROMOTE", "NO_FULL_RUN"]):
            if cand != "UNKNOWN":
                exact_candidate_blocks.add(cand)
            if fam != "UNKNOWN":
                family_cooldowns.add(fam)

    # Manual high-signal known blocks from current project state, if memory scan sees them.
    known_rules = []

    if "market_panic_rebound_long_v1" in exact_candidate_blocks:
        known_rules.append({
            "rule": "Do not rerun market_panic_rebound_long_v1 exact rule.",
            "reason": "Negative self-test, PF collapse, strong negative mean/median, catches falling knives without stabilization.",
        })

    if "post_impulse_drift_long_v1" in exact_candidate_blocks or "post_impulse_drift_long_strict_v1" in exact_candidate_blocks:
        known_rules.append({
            "rule": "Do not promote post_impulse_drift_long_v1 / strict variant without genuinely new feature evidence.",
            "reason": "Strict validation failed full/in-sample/month stability despite OOS-positive subperiod.",
        })

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "memory_status": "OS_MEMORY_LESSON_INDEX_READY",
        "memory_jsonl": str(MEMORY_JSONL),
        "memory_row_count": len(memory_rows),
        "candidate_record_count": len(candidate_records),
        "lesson_count": len(lessons),
        "failure_tag_count": len(failure_tags),
        "hard_block_count": len(hard_blocks),
        "exact_candidate_blocks": sorted(exact_candidate_blocks),
        "family_cooldowns": sorted(family_cooldowns),
        "failure_tags": sorted(failure_tags),
        "hard_blocks": sorted(hard_blocks),
        "known_rules": known_rules,
        "next_action": "USE_MEMORY_INDEX_IN_SELECTOR_AND_NEXT_ACTION_PLANNER",
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "source_files_scanned": sorted(set(source_files)),
    }

    state_path = out_dir / "os_memory_lesson_index_v1_state.json"
    latest_path = OUT_ROOT / "os_memory_lesson_index_latest.json"
    candidates_csv = out_dir / "os_memory_lesson_index_v1_candidates.csv"
    lessons_csv = out_dir / "os_memory_lesson_index_v1_lessons.csv"
    report_path = out_dir / "os_memory_lesson_index_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with candidates_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["candidate", "family", "status", "decision", "failure_tags", "hard_blocks", "source"],
        )
        writer.writeheader()
        for r in candidate_records:
            rr = dict(r)
            rr["failure_tags"] = "|".join(rr.get("failure_tags", []))
            rr["hard_blocks"] = "|".join(rr.get("hard_blocks", []))
            writer.writerow(rr)

    with lessons_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate", "family", "lesson", "source"])
        writer.writeheader()
        writer.writerows(lessons)

    md = []
    md.append("# Edge Factory OS Memory / Lesson Index v1")
    md.append("")
    md.append(f"memory_status: `{state['memory_status']}`")
    md.append(f"memory_row_count: `{len(memory_rows)}`")
    md.append(f"candidate_record_count: `{len(candidate_records)}`")
    md.append(f"lesson_count: `{len(lessons)}`")
    md.append("")
    md.append("## Exact candidate blocks")
    for x in state["exact_candidate_blocks"]:
        md.append(f"- `{x}`")
    md.append("")
    md.append("## Family cooldowns")
    for x in state["family_cooldowns"]:
        md.append(f"- `{x}`")
    md.append("")
    md.append("## Known rules")
    for r in known_rules:
        md.append(f"- **{r['rule']}** {r['reason']}")
    md.append("")
    md.append("## Safety")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS MEMORY / LESSON INDEX v1")
    print("=" * 100)
    print(f"memory_status: {state['memory_status']}")
    print(f"memory_row_count: {len(memory_rows)}")
    print(f"candidate_record_count: {len(candidate_records)}")
    print(f"lesson_count: {len(lessons)}")
    print(f"failure_tag_count: {len(failure_tags)}")
    print(f"hard_block_count: {len(hard_blocks)}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("EXACT CANDIDATE BLOCKS")
    print("-" * 100)
    print("\n".join(f"- {x}" for x in state["exact_candidate_blocks"]) if state["exact_candidate_blocks"] else "NONE")
    print()
    print("FAMILY COOLDOWNS")
    print("-" * 100)
    print("\n".join(f"- {x}" for x in state["family_cooldowns"]) if state["family_cooldowns"] else "NONE")
    print()
    print("KNOWN RULES")
    print("-" * 100)
    if known_rules:
        for r in known_rules:
            print(f"- {r['rule']} -> {r['reason']}")
    else:
        print("NONE")
    print()
    print(f"State     : {state_path}")
    print(f"Latest    : {latest_path}")
    print(f"Candidates: {candidates_csv}")
    print(f"Lessons   : {lessons_csv}")
    print(f"Report    : {report_path}")

if __name__ == "__main__":
    main()
