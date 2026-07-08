#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY CONTRACT RECONCILER v1
===================================

Purpose
-------
Offline contract reconciliation module for the Edge Factory OS.

It solves the important preflight warning:
    contract_vs_governor_proposal

Current situation:
    Active position_sizing_contract.json still says market_relative_short = 25 USDT.
    Adaptive Capital Governor v2 proposed market_relative_short = 12.5 USDT.

This module reads:
    latest capital_policy_proposal.json
    active position_sizing_contract.json

Then writes a reviewed contract preview:
    reviewed_position_sizing_contract.json

By default it DOES NOT overwrite the active contract.
Use --apply only when you intentionally want to update the active sizing contract.
Even with --apply, it creates a backup first.

Run preview only:
    python "C:\Users\alike\edge_factory_contract_reconciler.py"

Apply after review:
    python "C:\Users\alike\edge_factory_contract_reconciler.py" --apply

Outputs
-------
    <workspace>\edge_factory_contract_reconciler\contract_reconcile_YYYYMMDD_HHMMSS\
        contract_reconciliation_report.md
        contract_diff.json
        reviewed_position_sizing_contract.json
        apply_contract_plan.ps1
        active_contract_backup.json  only in --apply mode

Important
---------
This module does not start paper/live.
It only aligns the active sizing contract with the governor proposal, or creates a preview.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CONTRACT_REL = Path("edge_factory_position_sizing_contract") / "position_sizing_contract.json"
KNOWN_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short", "session_short"]


@dataclass
class FamilyContractDiff:
    family_key: str
    active_notional: Optional[float]
    proposed_notional: float
    delta: Optional[float]
    status: str


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        if isinstance(x, str):
            s = x.strip().lower()
            if s in {"", "none", "null", "nan", "inf", "infinity"}:
                return None
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def discover_capital_dir(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    return latest_child_dir(workspace / "edge_factory_adaptive_capital_governor_v2", "capital_governor_")


def load_capital_policy(capital_dir: Path) -> Dict[str, Any]:
    p = capital_dir / "capital_policy_proposal.json"
    if not p.exists():
        raise FileNotFoundError(f"capital_policy_proposal.json not found: {p}")
    obj = load_json(p)
    if not isinstance(obj, dict):
        raise ValueError("capital policy is not a JSON object")
    return obj


def proposed_notional_map(policy: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    rows = policy.get("family_decisions") or []
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict) and r.get("family_key"):
                val = safe_float(r.get("proposed_notional"))
                if val is not None:
                    out[str(r["family_key"])] = float(val)
    return out


def recursive_find_family_value(obj: Any, family_key: str, preferred_keys: List[str]) -> Optional[float]:
    if isinstance(obj, dict):
        if family_key in obj:
            node = obj[family_key]
            v = safe_float(node)
            if v is not None:
                return v
            if isinstance(node, dict):
                for k in preferred_keys:
                    if k in node:
                        v = safe_float(node[k])
                        if v is not None:
                            return v
        for k in preferred_keys + ["expected_notional_by_family", "notional_by_family", "family_notional"]:
            node = obj.get(k)
            if isinstance(node, dict) and family_key in node:
                v = safe_float(node[family_key])
                if v is not None:
                    return v
        for v in obj.values():
            found = recursive_find_family_value(v, family_key, preferred_keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = recursive_find_family_value(item, family_key, preferred_keys)
            if found is not None:
                return found
    return None


def active_notional_map(contract: Dict[str, Any], families: List[str]) -> Dict[str, Optional[float]]:
    preferred = [
        "expected_notional", "expected_notional_usdt", "notional", "notional_usdt",
        "default_notional", "target_notional", "target_notional_usdt",
    ]
    return {fam: recursive_find_family_value(contract, fam, preferred) for fam in families}


def update_family_notional_in_contract(contract: Dict[str, Any], family_key: str, proposed: float) -> bool:
    """Best-effort schema-preserving update. Returns True if it updated an existing place."""
    updated = False

    # Top-level map shapes.
    map_keys = ["expected_notional_by_family", "notional_by_family", "family_notional", "expected_notional", "notional_pct_by_family"]
    for key in map_keys:
        node = contract.get(key)
        if isinstance(node, dict) and family_key in node:
            # notional_pct_by_family is not USDT, skip here.
            if key == "notional_pct_by_family":
                continue
            node[family_key] = proposed
            updated = True

    # Common families dict shape.
    for families_key in ["families", "family_contracts", "family_sizing", "family_settings"]:
        fams = contract.get(families_key)
        if isinstance(fams, dict) and family_key in fams:
            node = fams[family_key]
            if isinstance(node, dict):
                target_key = None
                for k in ["expected_notional", "expected_notional_usdt", "notional", "notional_usdt", "default_notional", "target_notional", "target_notional_usdt"]:
                    if k in node:
                        target_key = k
                        break
                if target_key is None:
                    target_key = "expected_notional"
                node[target_key] = proposed
                updated = True
            else:
                fams[family_key] = proposed
                updated = True

    return updated


def build_reviewed_contract(active_contract: Dict[str, Any], proposed: Dict[str, float], base_equity: float) -> Tuple[Dict[str, Any], Dict[str, bool]]:
    reviewed = copy.deepcopy(active_contract)
    update_hits: Dict[str, bool] = {}

    for fam, val in proposed.items():
        if fam not in KNOWN_FAMILIES:
            continue
        update_hits[fam] = update_family_notional_in_contract(reviewed, fam, float(val))

    # Always include a clean top-level canonical map for future OS modules.
    reviewed["expected_notional_by_family"] = {fam: float(proposed.get(fam, 0.0)) for fam in KNOWN_FAMILIES if fam in proposed}
    reviewed["notional_pct_by_family"] = {fam: (float(proposed.get(fam, 0.0)) / base_equity if base_equity > 0 else 0.0) for fam in KNOWN_FAMILIES if fam in proposed}
    reviewed["edge_factory_contract_reconciliation"] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "edge_factory_contract_reconciler_v1",
        "preview_or_applied_by_module": True,
        "base_equity": base_equity,
        "notes": [
            "Canonical expected_notional_by_family was inserted/updated from adaptive capital governor proposal.",
            "This contract should be reviewed before paper boot.",
            "This module does not start paper/live.",
        ],
    }
    return reviewed, update_hits


def build_diffs(active: Dict[str, Optional[float]], proposed: Dict[str, float]) -> List[FamilyContractDiff]:
    diffs: List[FamilyContractDiff] = []
    for fam in KNOWN_FAMILIES:
        if fam not in proposed:
            continue
        a = active.get(fam)
        p = float(proposed[fam])
        delta = None if a is None else p - float(a)
        if a is None:
            status = "MISSING_IN_ACTIVE_CONTRACT"
        elif abs(delta or 0.0) < 1e-9:
            status = "MATCH"
        else:
            status = "DIFF"
        diffs.append(FamilyContractDiff(fam, a, p, delta, status))
    return diffs


def write_apply_plan(path: Path, script_path: Path, contract_path: Path) -> None:
    content = f'''# EDGE FACTORY CONTRACT APPLY PLAN
# Review before running.
# This applies the governor-reviewed sizing contract to the active contract path.

python "{script_path}" --apply --contract "{contract_path}"
'''
    path.write_text(content, encoding="utf-8")


def write_report(path: Path, context: Dict[str, Any], diffs: List[FamilyContractDiff], applied: bool, backup_path: Optional[Path]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Contract Reconciliation Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Mode: **{'APPLIED' if applied else 'PREVIEW_ONLY'}**")
    lines.append(f"Active contract: `{context['contract_path']}`")
    lines.append(f"Capital source: `{context['capital_dir']}`")
    if backup_path:
        lines.append(f"Backup: `{backup_path}`")
    lines.append("")

    lines.append("## Diff")
    lines.append("")
    lines.append("| Family | Active | Governor proposed | Delta | Status |")
    lines.append("|---|---:|---:|---:|---:|")
    for d in diffs:
        lines.append(f"| {d.family_key} | {d.active_notional} | {d.proposed_notional} | {d.delta} | {d.status} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("- `MATCH` means active contract already agrees with the adaptive governor.")
    lines.append("- `DIFF` means the active contract and governor proposal differ.")
    lines.append("- The main expected diff is `market_relative_short`: 25 → 12.5 USDT.")
    lines.append("- This module does not start paper/live.")
    lines.append("")

    if not applied:
        lines.append("## Next")
        lines.append("")
        lines.append("Review `reviewed_position_sizing_contract.json`. If you intentionally want to apply it, run this script with `--apply`.")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory contract reconciler")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--capital_dir", default=None)
    p.add_argument("--contract", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--base_equity", type=float, default=1000.0)
    p.add_argument("--apply", action="store_true", help="backup and overwrite active position_sizing_contract.json")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    capital_dir = discover_capital_dir(workspace, Path(args.capital_dir) if args.capital_dir else None)
    contract_path = Path(args.contract) if args.contract else workspace / DEFAULT_CONTRACT_REL

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_contract_reconciler"
    out_dir = out_root / f"contract_reconcile_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if capital_dir is None:
        print("EDGE FACTORY CONTRACT RECONCILER v1")
        print("No capital governor directory found.")
        return 2
    if not contract_path.exists():
        print("EDGE FACTORY CONTRACT RECONCILER v1")
        print(f"Contract not found: {contract_path}")
        return 2

    policy = load_capital_policy(capital_dir)
    proposed = proposed_notional_map(policy)
    active_contract = load_json(contract_path)
    if not isinstance(active_contract, dict):
        raise ValueError("Active contract is not a JSON object")

    active = active_notional_map(active_contract, KNOWN_FAMILIES)
    diffs = build_diffs(active, proposed)
    reviewed, update_hits = build_reviewed_contract(active_contract, proposed, args.base_equity)

    backup_path: Optional[Path] = None
    if args.apply:
        backup_path = out_dir / "active_contract_backup.json"
        shutil.copy2(contract_path, backup_path)
        write_json(contract_path, reviewed)

    write_json(out_dir / "reviewed_position_sizing_contract.json", reviewed)
    write_json(out_dir / "contract_diff.json", {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "applied": bool(args.apply),
        "contract_path": str(contract_path),
        "capital_dir": str(capital_dir),
        "diffs": [asdict(d) for d in diffs],
        "schema_update_hits": update_hits,
        "backup_path": str(backup_path) if backup_path else None,
    })
    write_apply_plan(out_dir / "apply_contract_plan.ps1", Path(__file__), contract_path)

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "contract_path": str(contract_path),
        "capital_dir": str(capital_dir),
    }
    write_report(out_dir / "contract_reconciliation_report.md", context, diffs, bool(args.apply), backup_path)

    print("EDGE FACTORY CONTRACT RECONCILER v1")
    print("=" * 100)
    print(f"workspace  : {workspace}")
    print(f"capital_dir: {capital_dir}")
    print(f"contract   : {contract_path}")
    print(f"output_dir : {out_dir}")
    print(f"mode       : {'APPLY' if args.apply else 'PREVIEW_ONLY'}")
    print("")
    print("CONTRACT DIFF")
    print("-" * 100)
    for d in diffs:
        print(f"{d.family_key:24s} active={str(d.active_notional):>8s} proposed={d.proposed_notional:8.4f} delta={str(d.delta):>8s} status={d.status}")
    print("")
    if args.apply:
        print(f"APPLIED. Backup written: {backup_path}")
    else:
        print("Preview only. Active contract was NOT modified.")
    print(f"Reviewed contract: {out_dir / 'reviewed_position_sizing_contract.json'}")
    print(f"Report           : {out_dir / 'contract_reconciliation_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
