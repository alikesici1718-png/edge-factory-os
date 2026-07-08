from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_impulse_long_evidence_locator_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent
RUNTIME_DIR = BASE_DIR / "paper_run_gate_MASTER_UPPER_SYSTEM"

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"impulse_long_evidence_locator_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "impulse_long_evidence_locator_latest.json"
LATEST_MD = OUT_ROOT / "impulse_long_evidence_locator_latest.md"

SEARCH_ROOTS = [
    RUNTIME_DIR,
    BASE_DIR,
]

FILE_EXTS = {
    ".csv",
    ".json",
    ".jsonl",
    ".txt",
    ".log",
    ".md",
}

POSITIVE_TERMS = [
    "impulse_long",
    "impulse",
    "family_key",
    "closed_trades",
    "realized_pnl",
    "unrealized_pnl",
    "total_pnl",
    "win_rate",
    "paper",
    "trade",
    "position",
    "entry",
    "exit",
]

NEGATIVE_PATH_TERMS = [
    ".git",
    "__pycache__",
    "site-packages",
    "node_modules",
]

LOW_VALUE_PATH_TERMS = [
    "edge_factory_os_cycle_operator",
    "edge_factory_os_error",
    "edge_factory_os_family_drift_review",
    "edge_factory_os_impulse_long_failure_attribution",
]

HIGH_VALUE_PATH_TERMS = [
    "paper_run_gate_master_upper_system",
    "paper",
    "trade",
    "trades",
    "position",
    "positions",
    "ledger",
    "fills",
    "orders",
    "logger",
    "family_performance",
    "performance_discipline",
]


def load_json(path: Path) -> Optional[Any]:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def safe_text(path: Path, limit: int = 250_000) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""


def norm(s: Any) -> str:
    return str(s or "").strip().lower()


def path_allowed(path: Path) -> bool:
    p = norm(path)
    if any(term in p for term in NEGATIVE_PATH_TERMS):
        return False
    if path.suffix.lower() not in FILE_EXTS:
        return False
    return True


def score_file(path: Path, text: str) -> int:
    p = norm(path)
    t = text.lower()

    score = 0

    for term in POSITIVE_TERMS:
        if term in t:
            score += 5

    for term in HIGH_VALUE_PATH_TERMS:
        if term in p:
            score += 12

    for term in LOW_VALUE_PATH_TERMS:
        if term in p:
            score -= 20

    if "impulse_long" in t:
        score += 30

    if "family_key" in t and "impulse_long" in t:
        score += 20

    if "closed_trades" in t or "realized_pnl" in t or "total_pnl" in t:
        score += 15

    return score


def csv_probe(path: Path) -> Dict[str, Any]:
    out = {
        "type": "csv",
        "read_ok": False,
        "headers": [],
        "row_count_sampled": 0,
        "impulse_rows_sampled": 0,
        "has_trade_like_columns": False,
        "sample_impulse_rows": [],
        "error": None,
    }

    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            out["headers"] = headers

            lower_headers = [h.lower() for h in headers]

            trade_terms = [
                "symbol",
                "family",
                "family_key",
                "entry",
                "exit",
                "pnl",
                "realized",
                "unrealized",
                "side",
                "qty",
                "price",
                "timestamp",
                "closed",
            ]

            out["has_trade_like_columns"] = any(
                any(term in h for term in trade_terms)
                for h in lower_headers
            )

            for i, row in enumerate(reader):
                if i >= 5000:
                    break

                out["row_count_sampled"] += 1

                row_text = json.dumps(row, default=str).lower()

                if "impulse_long" in row_text or "impulse" in row_text:
                    out["impulse_rows_sampled"] += 1
                    if len(out["sample_impulse_rows"]) < 5:
                        out["sample_impulse_rows"].append(row)

        out["read_ok"] = True

    except Exception as e:
        out["error"] = repr(e)

    return out


def json_walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from json_walk(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from json_walk(x)


def json_probe(path: Path) -> Dict[str, Any]:
    out = {
        "type": "json_or_jsonl",
        "read_ok": False,
        "dict_count_sampled": 0,
        "impulse_dict_count": 0,
        "sample_impulse_dicts": [],
        "error": None,
    }

    try:
        if path.suffix.lower() == ".jsonl":
            objs = []
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= 5000:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        objs.append(json.loads(line))
                    except Exception:
                        continue
        else:
            obj = load_json(path)
            objs = [obj] if obj is not None else []

        for obj in objs:
            for d in json_walk(obj):
                out["dict_count_sampled"] += 1

                if out["dict_count_sampled"] > 20000:
                    break

                text = json.dumps(d, default=str).lower()

                if "impulse_long" in text or "impulse" in text:
                    out["impulse_dict_count"] += 1

                    if len(out["sample_impulse_dicts"]) < 5:
                        compact = {}
                        for k, v in d.items():
                            if isinstance(v, (str, int, float, bool)) or v is None:
                                compact[str(k)] = v
                            if len(compact) >= 40:
                                break
                        out["sample_impulse_dicts"].append(compact)

        out["read_ok"] = True

    except Exception as e:
        out["error"] = repr(e)

    return out


def text_probe(path: Path, text: str) -> Dict[str, Any]:
    lines = text.splitlines()

    matches = []

    for i, line in enumerate(lines[:10000], start=1):
        l = line.lower()
        if "impulse_long" in l or "impulse" in l:
            matches.append(
                {
                    "line": i,
                    "text": line[:500],
                }
            )
        if len(matches) >= 10:
            break

    return {
        "type": "text",
        "line_count_sampled": min(len(lines), 10000),
        "match_count_sampled": len(matches),
        "sample_matches": matches,
    }


def probe_file(path: Path, text: str) -> Dict[str, Any]:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return csv_probe(path)

    if suffix in {".json", ".jsonl"}:
        return json_probe(path)

    return text_probe(path, text)


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    candidates = []

    seen = set()

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            resolved = str(path.resolve()).lower()
            if resolved in seen:
                continue
            seen.add(resolved)

            if not path_allowed(path):
                continue

            try:
                size = path.stat().st_size
            except Exception:
                size = 0

            if size <= 0:
                continue

            if size > 50_000_000:
                continue

            text = safe_text(path, limit=250_000)
            if not text:
                continue

            score = score_file(path, text)

            if score <= 0:
                continue

            probe = probe_file(path, text)

            # Boost candidates with actual impulse rows/dicts/matches.
            if probe.get("impulse_rows_sampled", 0) > 0:
                score += 100

            if probe.get("impulse_dict_count", 0) > 0:
                score += 80

            if probe.get("match_count_sampled", 0) > 0:
                score += 30

            candidates.append(
                {
                    "score": score,
                    "path": str(path),
                    "size_bytes": size,
                    "suffix": path.suffix.lower(),
                    "probe": probe,
                }
            )

    candidates.sort(key=lambda x: x["score"], reverse=True)

    top = candidates[:30]

    raw_trade_like = [
        c for c in top
        if (
            c["probe"].get("impulse_rows_sampled", 0) > 0
            or c["probe"].get("impulse_dict_count", 0) > 0
        )
    ]

    if raw_trade_like:
        locator_status = "IMPULSE_LONG_EVIDENCE_LOCATOR_FOUND_ROW_LEVEL_CANDIDATES"
        severity = "INFO"
        next_action = "BUILD_IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_FROM_TOP_CANDIDATE"
        reason = f"row_level_candidate_count={len(raw_trade_like)}"
    elif top:
        locator_status = "IMPULSE_LONG_EVIDENCE_LOCATOR_FOUND_AGGREGATE_OR_TEXT_CANDIDATES"
        severity = "ATTENTION"
        next_action = "REVIEW_CANDIDATES_OR_ADD_LEDGER_EXPORTER"
        reason = "only aggregate/text evidence candidates found"
    else:
        locator_status = "IMPULSE_LONG_EVIDENCE_LOCATOR_NO_CANDIDATES_FOUND"
        severity = "ATTENTION"
        next_action = "ADD_READ_ONLY_TRADE_LEDGER_EXPORTER_TO_RUNTIME"
        reason = "no impulse_long evidence files found"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "locator_status": locator_status,
        "severity": severity,
        "next_action": next_action,
        "reason": reason,

        "search_roots": [str(p) for p in SEARCH_ROOTS],
        "candidate_count": len(candidates),
        "row_level_candidate_count": len(raw_trade_like),
        "top_candidates": top,

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "family_disable_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,
    }

    out_json = RUN_DIR / "impulse_long_evidence_locator_v1_state.json"
    out_md = RUN_DIR / "impulse_long_evidence_locator_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS IMPULSE LONG EVIDENCE LOCATOR v1",
        "",
        f"locator_status: {locator_status}",
        f"severity: {severity}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        f"candidate_count: {len(candidates)}",
        f"row_level_candidate_count: {len(raw_trade_like)}",
        "",
        "## Top Candidates",
        "",
    ]

    for c in top[:15]:
        md_lines.append(json.dumps(c, indent=2, default=str)[:4000])

    md_lines.extend(
        [
            "",
            "## Safety",
            "",
            "mutate_runtime_allowed: False",
            "launcher_allowed: False",
            "patch_runtime_allowed: False",
            "active_paper_allowed: False",
            "live_allowed: False",
            "capital_change_allowed: False",
            "family_disable_allowed: False",
            "real_orders_allowed: False",
            "execution_performed: False",
        ]
    )

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS IMPULSE LONG EVIDENCE LOCATOR v1")
    print("=" * 100)
    print(f"locator_status: {locator_status}")
    print(f"severity: {severity}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print(f"candidate_count: {len(candidates)}")
    print(f"row_level_candidate_count: {len(raw_trade_like)}")
    print()
    print("TOP CANDIDATES")
    print("-" * 100)
    for c in top[:10]:
        print(f"score={c['score']} path={c['path']}")
        probe = c.get("probe", {})
        print(f"probe_type={probe.get('type')}")
        print(f"impulse_rows_sampled={probe.get('impulse_rows_sampled')}")
        print(f"impulse_dict_count={probe.get('impulse_dict_count')}")
        print(f"match_count_sampled={probe.get('match_count_sampled')}")
        print()
    print("SAFETY")
    print("-" * 100)
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
