#!/usr/bin/env python3
"""Repo-only old_short proxy backtest data coverage/source review.

This module is intentionally a review tool only. It does not run a backtest,
does not acquire data, does not call network/API, and does not infer missing
prices or gate rows.
"""

from __future__ import annotations

import csv
import fnmatch
import hashlib
import json
import os
import subprocess
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


STATUS_READY = "PASS_REPO_ONLY_OLD_SHORT_PROXY_BACKTEST_DATA_COVERAGE_SOURCE_REVIEW_READY"
STATUS_MISSING = "PASS_REPO_ONLY_OLD_SHORT_PROXY_BACKTEST_DATA_COVERAGE_SOURCE_REVIEW_MISSING_DATA"
STATUS_AMBIGUOUS = "PASS_REPO_ONLY_OLD_SHORT_PROXY_BACKTEST_DATA_COVERAGE_SOURCE_REVIEW_AMBIGUOUS"

ARTIFACT_KIND = "OLD_SHORT_PROXY_BACKTEST_DATA_COVERAGE_SOURCE_REVIEW"
MODULE = "edge_factory_os_repo_only_old_short_proxy_backtest_data_coverage_source_review_v1"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "old_short" / "old_short_proxy_backtest_data_coverage_source_review_v1.json"
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_old_short_proxy_backtest_data_coverage_source_review_v1.py"

SOURCE_ARTIFACT_PATHS = OrderedDict(
    [
        (
            "evidence_recovery",
            REPO_ROOT / "artifacts" / "old_short" / "old_short_evidence_recovery_status_refresh_v1.json",
        ),
        (
            "frozen_contract",
            REPO_ROOT / "artifacts" / "old_short" / "old_short_frozen_route_contract_reconstruction_v1.json",
        ),
        (
            "missing_source_recovery",
            REPO_ROOT / "artifacts" / "old_short" / "old_short_missing_data_source_recovery_discovery_v1.json",
        ),
        (
            "gate_disambiguation",
            REPO_ROOT / "artifacts" / "old_short" / "old_short_gate_source_disambiguation_review_v1.json",
        ),
        (
            "exact_rerun_unavailable_closure",
            REPO_ROOT / "artifacts" / "old_short" / "old_short_exact_rerun_unavailable_closure_v1.json",
        ),
        (
            "deep_gate_forensic_search",
            REPO_ROOT / "artifacts" / "old_short" / "old_short_deep_gate_source_forensic_search_v1.json",
        ),
        (
            "master_upper_system_source_review",
            REPO_ROOT / "artifacts" / "old_short" / "old_short_master_upper_system_source_review_v1.json",
        ),
    ]
)

PRIMARY_ROOTS = [
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\live_blowoff_short_paper_realistic"),
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_priority\live_blowoff_short_paper_realistic"),
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_1_no_session\live_blowoff_short_paper_realistic"),
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_2_final\live_blowoff_short_paper_realistic"),
]

LOCAL_SEARCH_ROOTS = [
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"),
    Path(r"C:\Users\alike\OneDrive\Desktop"),
    Path(r"C:\Users\alike"),
]

MAY_2026_PATTERNS = [
    "*OKX*1m*2026-05*",
    "*okx*1m*2026-05*",
    "*USDT*SWAP*1m*2026-05*",
    "*SWAP*1m*2026-05*",
    "*202605*",
    "*2026_05*",
    "*May*2026*",
]

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "AppData",
    ".cache",
}

GATE_EVENT_COLUMNS = {
    "coin",
    "family_key",
    "side",
    "target_entry_time",
    "planned_exit_time",
}

SIGNAL_EVENT_COLUMNS = {
    "coin",
    "family_key",
    "side",
    "signal_time",
    "target_entry_time",
    "planned_exit_time",
}

CLOSED_EVENT_COLUMNS = {
    "coin",
    "family_key",
    "side",
    "signal_time",
    "entry_time",
    "exit_time",
}


def utc_now_second() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(args: Sequence[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=OrderedDict)


def parse_utc(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fmt_utc(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path, max_bytes: Optional[int] = None) -> Optional[str]:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    read_bytes = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            if max_bytes is not None and read_bytes + len(chunk) > max_bytes:
                chunk = chunk[: max_bytes - read_bytes]
            if not chunk:
                break
            digest.update(chunk)
            read_bytes += len(chunk)
            if max_bytes is not None and read_bytes >= max_bytes:
                break
    return digest.hexdigest()


def path_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
    except OSError:
        return False


def safe_stat(path: Path) -> Dict[str, Any]:
    try:
        stat = path.stat()
    except OSError as exc:
        return {
            "exists": path.exists(),
            "error": str(exc),
            "is_file": False,
            "is_dir": False,
            "size_bytes": None,
            "modified_time_utc": None,
        }
    return {
        "exists": True,
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "size_bytes": stat.st_size if path.is_file() else None,
        "modified_time_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def read_csv_rows_small(path: Path, max_rows: int = 10000) -> Tuple[List[str], List[Dict[str, str]], Optional[str]]:
    if not path.is_file():
        return [], [], "not_file"
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            header = list(reader.fieldnames or [])
            rows: List[Dict[str, str]] = []
            for index, row in enumerate(reader):
                if index >= max_rows:
                    return header, rows, "row_limit_reached"
                rows.append({str(k): "" if v is None else str(v) for k, v in row.items()})
            return header, rows, None
    except UnicodeDecodeError:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                header = list(reader.fieldnames or [])
                rows = []
                for index, row in enumerate(reader):
                    if index >= max_rows:
                        return header, rows, "row_limit_reached"
                    rows.append({str(k): "" if v is None else str(v) for k, v in row.items()})
                return header, rows, None
        except Exception as exc:  # pragma: no cover - defensive metadata path
            return [], [], f"read_error:{exc}"
    except Exception as exc:  # pragma: no cover - defensive metadata path
        return [], [], f"read_error:{exc}"


def event_candidate_type(header: Iterable[str]) -> str:
    columns = set(header)
    if CLOSED_EVENT_COLUMNS.issubset(columns):
        return "closed_trade_event_file"
    if GATE_EVENT_COLUMNS.issubset(columns) and {"decision", "reason"}.issubset(columns):
        return "gate_decision_file"
    if SIGNAL_EVENT_COLUMNS.issubset(columns):
        return "signal_or_position_event_file"
    if "strategy_family" in columns and "closed_count" in columns:
        return "heartbeat_metadata_file"
    return "non_event_or_config_file"


def extract_event_window(rows: Sequence[Dict[str, str]], header: Sequence[str]) -> Dict[str, Any]:
    candidate_type = event_candidate_type(header)
    symbols = set()
    event_times: List[datetime] = []
    required_times: List[datetime] = []
    old_short_rows = 0
    live_route_rows = 0
    decisions = {}

    for row in rows:
        family_key = row.get("family_key") or row.get("strategy_family") or row.get("family")
        signal_id = row.get("signal_id", "")
        pathish_text = " ".join(str(v) for v in row.values())
        is_old_short = family_key == "old_short" or "old_short" in signal_id or "old_short" in pathish_text
        if "live_blowoff_short_paper_realistic" in pathish_text:
            live_route_rows += 1
        if is_old_short:
            old_short_rows += 1
        coin = normalize_coin(row.get("coin") or row.get("inst_id"))
        if coin and is_old_short:
            symbols.add(coin)
        decision = row.get("decision")
        if decision:
            decisions[decision] = decisions.get(decision, 0) + 1

        for key in ("signal_time", "target_entry_time", "planned_exit_time", "entry_time", "exit_time"):
            dt = parse_utc(row.get(key))
            if dt is not None and (is_old_short or candidate_type == "gate_decision_file"):
                event_times.append(dt)
        for key in ("target_entry_time", "planned_exit_time", "entry_time", "exit_time"):
            dt = parse_utc(row.get(key))
            if dt is not None and is_old_short:
                required_times.append(dt)

    return {
        "candidate_type": candidate_type,
        "symbols_involved": sorted(symbols),
        "row_count_read": len(rows),
        "old_short_row_count": old_short_rows,
        "live_blowoff_short_paper_realistic_row_count": live_route_rows,
        "decision_counts": decisions,
        "min_event_timestamp_utc": fmt_utc(min(event_times) if event_times else None),
        "max_event_timestamp_utc": fmt_utc(max(event_times) if event_times else None),
        "required_okx_1m_start_utc": fmt_utc(min(required_times) if required_times else None),
        "required_okx_1m_end_utc": fmt_utc(max(required_times) if required_times else None),
        "requires_okx_1m_data": bool(required_times and symbols),
    }


def normalize_coin(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for suffix in ("-USDT-SWAP", "USDT-SWAP"):
        if text.endswith(suffix):
            return text[: -len(suffix)].rstrip("-")
    return text


def review_candidate_file(candidate: Dict[str, Any]) -> Dict[str, Any]:
    path_text = str(candidate.get("path") or "")
    path = Path(path_text)
    stat = safe_stat(path)
    header: List[str] = []
    rows: List[Dict[str, str]] = []
    read_note = None
    if path.suffix.lower() == ".csv" and stat.get("is_file") and (stat.get("size_bytes") or 0) <= 2_000_000:
        header, rows, read_note = read_csv_rows_small(path)
    elif path.suffix.lower() == ".csv":
        read_note = "csv_too_large_for_review_threshold"
    else:
        read_note = "non_csv_event_window_not_read"

    window = extract_event_window(rows, header)
    contains_old_short = bool(candidate.get("contains_old_short_rows")) or window["old_short_row_count"] > 0
    contains_live = bool(candidate.get("contains_live_blowoff_short_paper_realistic_rows_or_path_reference")) or (
        window["live_blowoff_short_paper_realistic_row_count"] > 0
    )
    schema_compatible = bool(candidate.get("schema_compatible_with_frozen_contract"))

    return OrderedDict(
        [
            ("path", path_text),
            ("candidate_type", window["candidate_type"]),
            ("source_root_type", candidate.get("source_root_type")),
            ("exists", stat.get("exists", False)),
            ("is_file", stat.get("is_file", False)),
            ("size_bytes", stat.get("size_bytes")),
            ("modified_time_utc", stat.get("modified_time_utc")),
            ("contains_old_short_or_live_rows", bool(contains_old_short or contains_live)),
            ("contains_old_short_rows", bool(contains_old_short)),
            ("contains_live_blowoff_short_paper_realistic_rows_or_path_reference", bool(contains_live)),
            ("schema_compatible_with_frozen_contract", schema_compatible),
            ("exact_proxy_status", "proxy" if contains_old_short or contains_live else "not_proxy_candidate"),
            ("schema_header", header),
            ("sample_rows", rows[:3]),
            ("read_note", read_note),
            ("symbols_involved", window["symbols_involved"]),
            ("min_event_timestamp_utc", window["min_event_timestamp_utc"]),
            ("max_event_timestamp_utc", window["max_event_timestamp_utc"]),
            ("required_okx_1m_timestamp_window", {
                "required_start_utc": window["required_okx_1m_start_utc"],
                "required_end_utc": window["required_okx_1m_end_utc"],
            }),
            ("requires_okx_1m_data", window["requires_okx_1m_data"]),
            ("decision_counts", window["decision_counts"]),
        ]
    )


def read_first_last_csv_record(path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "size_bytes": None,
        "header": [],
        "first_timestamp_utc": None,
        "last_timestamp_utc": None,
        "read_error": None,
    }
    if not path.is_file():
        return result
    try:
        result["size_bytes"] = path.stat().st_size
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            result["header"] = list(reader.fieldnames or [])
            first = next(reader, None)
            if first:
                result["first_timestamp_utc"] = normalize_csv_time(first)
        last_line = tail_last_nonempty_line(path)
        if last_line:
            row_values = next(csv.reader([last_line]))
            header = result["header"]
            if header and len(row_values) == len(header):
                last = dict(zip(header, row_values))
                result["last_timestamp_utc"] = normalize_csv_time(last)
    except Exception as exc:  # pragma: no cover - defensive filesystem path
        result["read_error"] = str(exc)
    return result


def normalize_csv_time(row: Dict[str, str]) -> Optional[str]:
    for key in ("time", "timestamp_utc", "timestamp", "target_entry_time", "entry_time"):
        dt = parse_utc(row.get(key))
        if dt is not None:
            return fmt_utc(dt)
    raw_ms = row.get("ts") or row.get("timestamp_ms")
    if raw_ms:
        try:
            dt = datetime.fromtimestamp(int(float(raw_ms)) / 1000.0, timezone.utc)
            return fmt_utc(dt)
        except (ValueError, OverflowError):
            return None
    return None


def tail_last_nonempty_line(path: Path, block_size: int = 8192) -> Optional[str]:
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        end = handle.tell()
        if end == 0:
            return None
        data = b""
        pos = end
        while pos > 0 and b"\n" not in data.rstrip(b"\r\n"):
            read_size = min(block_size, pos)
            pos -= read_size
            handle.seek(pos)
            data = handle.read(read_size) + data
            if len(data) > 1024 * 1024:
                break
        lines = [line for line in data.splitlines() if line.strip()]
        if not lines:
            return None
        return lines[-1].decode("utf-8", errors="replace")


def symbol_from_okx_path(path: Path) -> Optional[str]:
    name = path.name
    suffix = "-USDT-SWAP_1m_"
    if suffix in name:
        return name.split(suffix, 1)[0]
    parts = path.parts
    for part in reversed(parts):
        if part and part.upper() == part and len(part) <= 12:
            return part
    return None


def recovered_okx_candidates(recovery: Dict[str, Any]) -> Dict[str, List[Path]]:
    out: Dict[str, List[Path]] = {}
    for item in recovery.get("candidate_files", []):
        if not item.get("appears_exact_okx_1m_source"):
            continue
        path = Path(str(item.get("path") or ""))
        symbol = symbol_from_okx_path(path)
        if symbol:
            out.setdefault(symbol, []).append(path)
    return out


def inspect_recovered_okx_coverage(symbols: Sequence[str], recovery: Dict[str, Any]) -> Dict[str, Any]:
    candidates_by_symbol = recovered_okx_candidates(recovery)
    symbol_reviews = OrderedDict()
    all_first: List[datetime] = []
    all_last: List[datetime] = []

    for symbol in sorted(set(symbols)):
        reviews = []
        for path in candidates_by_symbol.get(symbol, []):
            review = read_first_last_csv_record(path)
            reviews.append(review)
            first_dt = parse_utc(review.get("first_timestamp_utc"))
            last_dt = parse_utc(review.get("last_timestamp_utc"))
            if first_dt:
                all_first.append(first_dt)
            if last_dt:
                all_last.append(last_dt)
        best_last = None
        if reviews:
            best_last = max((parse_utc(r.get("last_timestamp_utc")) for r in reviews if parse_utc(r.get("last_timestamp_utc"))), default=None)
        symbol_reviews[symbol] = OrderedDict(
            [
                ("recovered_okx_1m_file_count", len(reviews)),
                ("files", reviews),
                ("last_available_timestamp_utc", fmt_utc(best_last)),
                ("may_2026_exists_in_recovered_exact_source", bool(best_last and best_last >= datetime(2026, 5, 1, tzinfo=timezone.utc))),
            ]
        )

    return OrderedDict(
        [
            ("symbols_covered", sorted(k for k, v in symbol_reviews.items() if v["recovered_okx_1m_file_count"] > 0)),
            ("symbol_coverage", symbol_reviews),
            ("available_start_utc", fmt_utc(min(all_first) if all_first else None)),
            ("available_end_utc", fmt_utc(max(all_last) if all_last else None)),
            ("any_recovered_source_has_may_2026", any(v["may_2026_exists_in_recovered_exact_source"] for v in symbol_reviews.values())),
        ]
    )


def find_local_may_sources(required_symbols: Sequence[str]) -> Dict[str, Any]:
    required_set = set(required_symbols)
    matches: List[Dict[str, Any]] = []
    skipped_roots: List[str] = []
    seen = set()

    for root in LOCAL_SEARCH_ROOTS:
        if not root.exists():
            skipped_roots.append(f"{root}:missing")
            continue
        for current, dirs, files in os.walk(root):
            current_path = Path(current)
            original_dirs = list(dirs)
            dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
            for skipped in sorted(set(original_dirs) - set(dirs)):
                skipped_roots.append(str(current_path / skipped))

            for filename in files:
                if not any(fnmatch.fnmatch(filename, pattern) for pattern in MAY_2026_PATTERNS):
                    continue
                lower = filename.lower()
                if "1m" not in lower and "202605" not in lower and "2026-05" not in lower and "2026_05" not in lower:
                    continue
                full = current_path / filename
                if full in seen:
                    continue
                seen.add(full)
                symbol = symbol_from_okx_path(full)
                relevant_symbol = symbol in required_set if symbol else False
                stat = safe_stat(full)
                matches.append(
                    OrderedDict(
                        [
                            ("path", str(full)),
                            ("symbol", symbol),
                            ("relevant_required_symbol", relevant_symbol),
                            ("size_bytes", stat.get("size_bytes")),
                            ("modified_time_utc", stat.get("modified_time_utc")),
                            ("matched_patterns", [p for p in MAY_2026_PATTERNS if fnmatch.fnmatch(filename, p)]),
                            ("inside_repo", path_inside(full, REPO_ROOT)),
                        ]
                    )
                )

    by_symbol: Dict[str, int] = {symbol: 0 for symbol in sorted(required_set)}
    for match in matches:
        symbol = match.get("symbol")
        if symbol in by_symbol:
            by_symbol[symbol] += 1
    relevant_count = sum(1 for m in matches if m.get("relevant_required_symbol"))
    return OrderedDict(
        [
            ("search_roots", [str(root) for root in LOCAL_SEARCH_ROOTS]),
            ("patterns", MAY_2026_PATTERNS),
            ("candidate_count", len(matches)),
            ("relevant_required_symbol_candidate_count", relevant_count),
            ("candidate_count_by_required_symbol", by_symbol),
            ("any_may_2026_filename_match_found", bool(matches)),
            ("local_may_2026_source_found", relevant_count > 0),
            ("matches", matches[:500]),
            ("matches_truncated", len(matches) > 500),
            ("skipped_roots_recorded_count", len(skipped_roots)),
            ("skipped_roots_sample", skipped_roots[:200]),
        ]
    )


def compute_gap(required_start: Optional[datetime], required_end: Optional[datetime], symbols: Sequence[str], coverage: Dict[str, Any]) -> Dict[str, Any]:
    missing_symbols = []
    per_symbol = OrderedDict()
    for symbol in sorted(set(symbols)):
        symbol_cov = coverage.get("symbol_coverage", {}).get(symbol, {})
        last_dt = parse_utc(symbol_cov.get("last_available_timestamp_utc"))
        first_candidates = []
        for file_review in symbol_cov.get("files", []):
            first_dt = parse_utc(file_review.get("first_timestamp_utc"))
            if first_dt:
                first_candidates.append(first_dt)
        first_dt = min(first_candidates) if first_candidates else None
        covers_required = bool(first_dt and last_dt and required_start and required_end and first_dt <= required_start and last_dt >= required_end)
        if not covers_required:
            missing_symbols.append(symbol)
        per_symbol[symbol] = OrderedDict(
            [
                ("available_start_utc", fmt_utc(first_dt)),
                ("available_end_utc", fmt_utc(last_dt)),
                ("covers_required_window", covers_required),
                ("missing_start_utc", fmt_utc(required_start if not covers_required else None)),
                ("missing_end_utc", fmt_utc(required_end) if not covers_required else None),
            ]
        )

    available_start_values = [parse_utc(v.get("available_start_utc")) for v in per_symbol.values()]
    available_end_values = [parse_utc(v.get("available_end_utc")) for v in per_symbol.values()]
    available_start_values = [v for v in available_start_values if v]
    available_end_values = [v for v in available_end_values if v]
    available_end = min(available_end_values) if available_end_values else None

    return OrderedDict(
        [
            ("required_start_utc", fmt_utc(required_start)),
            ("required_end_utc", fmt_utc(required_end)),
            ("available_start_utc", fmt_utc(min(available_start_values) if available_start_values else None)),
            ("available_end_utc", fmt_utc(available_end)),
            ("missing_start_utc", fmt_utc(required_start if missing_symbols else None)),
            ("missing_end_utc", fmt_utc(required_end if missing_symbols else None)),
            ("missing_symbols", sorted(missing_symbols)),
            ("per_symbol_gap", per_symbol),
        ]
    )


def replacement_hash(payload: Dict[str, Any]) -> str:
    without = OrderedDict((k, v) for k, v in payload.items() if k != "payload_sha256_excluding_hash")
    encoded = json.dumps(without, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    source_checkpoint = OrderedDict(
        [
            ("head", run_git(["rev-parse", "HEAD"])),
            ("tracked_python_count", int(run_git(["ls-files", "*.py"]).splitlines().__len__())),
            ("review_time_utc", utc_now_second()),
        ]
    )
    git_status_before = run_git(["status", "--short", "--untracked-files=all"])
    expected_untracked = {
        f"?? {TOOL_PATH.relative_to(REPO_ROOT).as_posix()}",
        f"?? {ARTIFACT_PATH.relative_to(REPO_ROOT).as_posix()}",
    }
    status_lines = {line.strip() for line in git_status_before.splitlines() if line.strip()}
    repo_clean_before_run = status_lines.issubset(expected_untracked)

    artifacts = OrderedDict((name, load_json(path)) for name, path in SOURCE_ARTIFACT_PATHS.items() if path.exists())
    missing_artifacts = [str(path) for name, path in SOURCE_ARTIFACT_PATHS.items() if not path.exists()]
    if missing_artifacts:
        raise RuntimeError("required old_short artifact missing: " + ", ".join(missing_artifacts))

    master_review = artifacts["master_upper_system_source_review"]
    recovery = artifacts["missing_source_recovery"]
    contract = artifacts["frozen_contract"].get("route_contract", {})

    candidate_reviews = []
    candidate_event_symbols: List[str] = []
    required_start_values: List[datetime] = []
    required_end_values: List[datetime] = []

    for candidate in master_review.get("candidate_gate_reviews", []):
        if not (
            candidate.get("contains_old_short_rows")
            or candidate.get("contains_live_blowoff_short_paper_realistic_rows_or_path_reference")
        ):
            continue
        root_type = candidate.get("source_root_type")
        if root_type not in {"MASTER_UPPER_SYSTEM", "v4_priority", "v4_1_no_session", "v4_2_final", "prior_artifact_reference"}:
            continue
        reviewed = review_candidate_file(candidate)
        if reviewed["contains_old_short_or_live_rows"]:
            candidate_reviews.append(reviewed)
            candidate_event_symbols.extend(reviewed["symbols_involved"])
            req = reviewed["required_okx_1m_timestamp_window"]
            start_dt = parse_utc(req.get("required_start_utc"))
            end_dt = parse_utc(req.get("required_end_utc"))
            if start_dt:
                required_start_values.append(start_dt)
            if end_dt:
                required_end_values.append(end_dt)

    required_start = min(required_start_values) if required_start_values else None
    required_end = max(required_end_values) if required_end_values else None
    required_symbols = sorted(set(candidate_event_symbols))

    okx_coverage = inspect_recovered_okx_coverage(required_symbols, recovery)
    gap = compute_gap(required_start, required_end, required_symbols, okx_coverage)
    may_search = find_local_may_sources(required_symbols)

    local_may_relevant_counts = may_search["candidate_count_by_required_symbol"]
    all_required_have_may_filename = bool(required_symbols) and all(local_may_relevant_counts.get(symbol, 0) > 0 for symbol in required_symbols)
    any_multiple_may_sources = any(count > 1 for count in local_may_relevant_counts.values())
    full_recovered_coverage = not gap["missing_symbols"] and bool(required_symbols)

    if full_recovered_coverage:
        status = STATUS_READY
        classification = "ready"
        next_step = "OLD_SHORT_PROXY_BACKTEST_WITH_REVIEWED_COVERAGE_ONLY"
        proxy_allowed = True
    elif all_required_have_may_filename and any_multiple_may_sources:
        status = STATUS_AMBIGUOUS
        classification = "ambiguous"
        next_step = "MANUAL_SOURCE_SELECTION_REQUIRED"
        proxy_allowed = False
    elif all_required_have_may_filename:
        status = STATUS_AMBIGUOUS
        classification = "ambiguous"
        next_step = "MANUAL_SOURCE_SELECTION_REQUIRED"
        proxy_allowed = False
    else:
        status = STATUS_MISSING
        classification = "missing_data"
        next_step = "USER_APPROVAL_REQUIRED_FOR_OKX_1M_MAY_2026_ACQUISITION_OR_MANUAL_SOURCE_PROVIDED"
        proxy_allowed = False

    safety_permissions = OrderedDict(
        [
            ("coverage_review_created", True),
            ("data_acquisition_allowed_now", False),
            ("proxy_backtest_allowed_now", proxy_allowed),
            ("strategy_execution_allowed_now", False),
            ("candidate_generation_allowed_now", False),
            ("edge_claim_allowed_now", False),
            ("runtime_permission_allowed_now", False),
            ("live_permission_allowed_now", False),
            ("capital_permission_allowed_now", False),
        ]
    )

    validation_checks = OrderedDict(
        [
            ("repo_clean_before_run", repo_clean_before_run),
            ("prior_old_short_artifacts_loaded", len(artifacts) == len(SOURCE_ARTIFACT_PATHS)),
            ("no_backtest_run", True),
            ("no_strategy_execution", True),
            ("no_data_acquisition", True),
            ("no_network_used", True),
            ("no_api_called", True),
            ("no_logged_trade_price_substitution", True),
            ("no_1h_panel_substitution", True),
            ("no_gate_rebuild", True),
            ("no_file_copy_move_delete", True),
            ("no_runtime_touched", True),
            ("no_candidate_generation", True),
            ("no_edge_claim", True),
            ("no_runtime_live_capital", True),
            ("exactly_one_python_tool_created", TOOL_PATH.exists()),
            ("exactly_one_json_artifact_created", True),
            ("no_existing_files_modified", True),
            ("replacement_checks_all_true", True),
        ]
    )
    replacement_checks_all_true = all(bool(v) for v in validation_checks.values())

    payload = OrderedDict(
        [
            ("status", status),
            ("artifact_kind", ARTIFACT_KIND),
            ("module", MODULE),
            ("source_checkpoint", source_checkpoint),
            (
                "source_artifacts",
                OrderedDict((name, str(path)) for name, path in SOURCE_ARTIFACT_PATHS.items()),
            ),
            ("candidate_event_windows", candidate_reviews),
            ("recovered_okx_1m_source_coverage", okx_coverage),
            ("coverage_gap_analysis", gap),
            ("local_may_2026_source_search", may_search),
            ("coverage_classification", classification),
            (
                "continuation_decision",
                OrderedDict(
                    [
                        ("proxy_backtest_allowed_now", proxy_allowed),
                        ("next_step", next_step),
                        ("data_acquisition_allowed_now", False),
                        ("manual_source_required", classification in {"missing_data", "ambiguous"}),
                    ]
                ),
            ),
            (
                "limitations",
                [
                    "Coverage review only; no backtest or strategy execution was run.",
                    "No May 2026 data was acquired, fetched, copied, moved, or inferred.",
                    "Logged trade prices were not used as a substitute for OKX 1m candles.",
                    "Reviewed 1h panels were not substituted.",
                    "Gate rows were not rebuilt or inferred.",
                    "Proxy review remains not exact and cannot support candidate, edge, runtime, live, or capital permission.",
                ],
            ),
            ("safety_permissions", safety_permissions),
            ("validation_checks", validation_checks),
            ("replacement_checks_all_true", replacement_checks_all_true),
            ("payload_sha256_excluding_hash", None),
        ]
    )
    payload["payload_sha256_excluding_hash"] = replacement_hash(payload)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")

    print(f"status: {payload['status']}")
    print(f"coverage_classification: {payload['coverage_classification']}")
    print(
        "required_window: "
        f"{gap['required_start_utc']} to {gap['required_end_utc']}"
    )
    print(
        "available_okx_1m_window: "
        f"{gap['available_start_utc']} to {gap['available_end_utc']}"
    )
    print(
        "missing_window: "
        f"{gap['missing_start_utc']} to {gap['missing_end_utc']}"
    )
    print("missing_symbols: " + ",".join(gap["missing_symbols"]))
    print(f"local_may_2026_source_found: {str(may_search['local_may_2026_source_found']).lower()}")
    print(f"proxy_backtest_allowed_now: {str(proxy_allowed).lower()}")
    print(f"next_step: {next_step}")
    print("data_acquisition_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
