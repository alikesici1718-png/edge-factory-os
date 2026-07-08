from __future__ import annotations
import argparse, json, re
from pathlib import Path
import pandas as pd

DEFAULT_BASE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_USER_DIR = r"C:\Users\alike"
DEFAULT_GOVERNOR_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_capital_governor"

LOGGER_SCRIPTS = {
    "old_short": "old_short_gate_aware_live_paper_logger.py",
    "impulse_long": "impulse_long_gate_aware_live_paper_logger.py",
    "market_relative_short": "market_relative_live_paper_logger.py",
    "weak_market_short": "weak_market_breakdown_short_live_paper_logger.py",
}

SEARCH_PATTERNS = [
    r"notional\s*=", r"base_notional", r"trade_notional", r"paper_notional",
    r"fixed_notional", r"capital_fraction", r"default_notional", r"50\.0", r"\b50\b",
    r"open_positions", r"closed_trades", r"pending_entries",
]

def read_json(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))

def make_contract(governor_dir: Path, out_dir: Path, base_equity: float) -> dict:
    blueprint = read_json(governor_dir / "upper_system_blueprint.json")
    if not blueprint:
        raise FileNotFoundError(f"Missing upper_system_blueprint.json in {governor_dir}")
    policy = blueprint.get("family_policy", {})
    families = {}
    for fam, pol in policy.items():
        if fam == "session_short":
            continue
        cf = float(pol.get("capital_fraction", 0.0))
        families[fam] = {
            "enabled": fam in blueprint.get("enabled_families", []),
            "lifecycle": pol.get("lifecycle", ""),
            "priority": int(pol.get("priority", 0)),
            "max_positions": int(pol.get("max_positions", 0)),
            "capital_fraction": cf,
            "fixed_notional": round(base_equity * cf, 8),
            "role": pol.get("role", ""),
        }
    contract = {
        "contract_name": "EDGE_FACTORY_POSITION_SIZING_CONTRACT_v1",
        "base_equity": float(base_equity),
        "rule": "notional = base_equity * family.capital_fraction unless fixed_notional is set",
        "families": families,
        "expected_notional_1000_equity": {fam: data["fixed_notional"] for fam, data in families.items()},
        "notes": [
            "old_short and impulse_long are 5% notional.",
            "market_relative_short is half-size: 2.5% notional.",
            "weak_market_short is backup-only and 2.5% notional.",
            "Every logger must consume this contract before opening paper positions.",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "position_sizing_contract.json").write_text(json.dumps(contract, indent=2), encoding="utf-8")
    return contract

def extract_snippets(path: Path, context: int = 4):
    if not path.exists():
        return [], ""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    rows, snippets = [], []
    for i, line in enumerate(lines, start=1):
        matched = [pat for pat in SEARCH_PATTERNS if re.search(pat, line, flags=re.IGNORECASE)]
        if not matched:
            continue
        lo, hi = max(1, i-context), min(len(lines), i+context)
        snippet = "\n".join(f"{j:04d}: {lines[j-1]}" for j in range(lo, hi+1))
        rows.append({"file": str(path), "line": i, "matched_patterns": ",".join(matched), "text": line.strip()[:300]})
        snippets.append(f"\n### {path.name} line {i} patterns={','.join(matched)}\n{snippet}\n")
    return rows, "\n".join(snippets)

def audit_loggers(user_dir: Path, out_dir: Path):
    rows, all_snippets = [], []
    for fam, script in LOGGER_SCRIPTS.items():
        path = user_dir / script
        if not path.exists():
            rows.append({"family_key": fam, "script": str(path), "exists": False, "supports_sizing_contract_literal": False, "supports_notional_arg_literal": False, "notional_related_hits": 0, "needs_patch": True})
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        hit_rows, snippets = extract_snippets(path)
        rows.append({
            "family_key": fam,
            "script": str(path),
            "exists": True,
            "supports_sizing_contract_literal": "--sizing_contract" in text or "sizing_contract" in text,
            "supports_notional_arg_literal": any(k in text for k in ["--notional", "--default_notional", "--fixed_notional", "--paper_notional", "--trade_notional"]),
            "notional_related_hits": len(hit_rows),
            "needs_patch": not ("--sizing_contract" in text or "sizing_contract" in text),
        })
        all_snippets.append(f"\n\n{'='*120}\nFAMILY={fam} SCRIPT={path}\n{'='*120}\n")
        all_snippets.append(snippets if snippets else "No notional-related snippets found.\n")
        pd.DataFrame(hit_rows).to_csv(out_dir / f"{fam}_notional_hits.csv", index=False)
    return pd.DataFrame(rows), "\n".join(all_snippets)

def write_patch_plan(out_dir: Path, contract_path: Path):
    txt = f"""POSITION SIZING CONTRACT PATCH PLAN

Goal:
  Every paper/live logger must open positions using family-specific notional from:
    {contract_path}

Contract expected notional at 1000 USDT base:
  old_short              50 USDT
  impulse_long           50 USDT
  market_relative_short  25 USDT
  weak_market_short      25 USDT

Required logger behavior:
  1) Add CLI args:
       --sizing_contract
       --default_notional

  2) Import:
       from sizing_contract_runtime import resolve_family_notional

  3) Before writing open_positions.csv or calculating quantity:
       notional = resolve_family_notional(
           FAMILY_KEY,
           default_notional=args.default_notional,
           sizing_contract_path=args.sizing_contract
       )

  4) All emitted rows must include:
       notional
       sizing_contract_path
       sizing_contract_family_key

Why:
  Capital governor found the upper-system improvement is SIZE_MARKET_RELATIVE_HALF.
  Without logger-level sizing support, the optimizer result is not actually implemented.
"""
    (out_dir / "POSITION_SIZING_PATCH_PLAN.txt").write_text(txt, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Build and audit Edge Factory position sizing contract.")
    ap.add_argument("--base_dir", default=DEFAULT_BASE)
    ap.add_argument("--user_dir", default=DEFAULT_USER_DIR)
    ap.add_argument("--governor_dir", default=DEFAULT_GOVERNOR_DIR)
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--base_equity", type=float, default=1000.0)
    args = ap.parse_args()

    base = Path(args.base_dir)
    user_dir = Path(args.user_dir)
    governor_dir = Path(args.governor_dir)
    out_dir = Path(args.out_dir) if args.out_dir else base / "edge_factory_position_sizing_contract"
    out_dir.mkdir(parents=True, exist_ok=True)

    contract = make_contract(governor_dir, out_dir, args.base_equity)
    contract_path = out_dir / "position_sizing_contract.json"
    audit_df, snippets = audit_loggers(user_dir, out_dir)
    audit_df.to_csv(out_dir / "logger_sizing_contract_audit.csv", index=False)
    (out_dir / "logger_notional_code_snippets.txt").write_text(snippets, encoding="utf-8")
    write_patch_plan(out_dir, contract_path)

    runtime_here = Path(r"C:\Users\alike\sizing_contract_runtime.py")
    report = []
    report.append("EDGE FACTORY POSITION SIZING CONTRACT REPORT")
    report.append("=" * 120)
    report.append(f"out_dir: {out_dir}")
    report.append(f"contract_path: {contract_path}")
    report.append("")
    report.append("CONTRACT")
    report.append("-" * 120)
    report.append(json.dumps(contract, indent=2))
    report.append("")
    report.append("LOGGER AUDIT")
    report.append("-" * 120)
    report.append(audit_df.to_string(index=False))
    report.append("")
    report.append("NEXT STEP")
    report.append("-" * 120)
    if bool(audit_df["needs_patch"].any()):
        report.append("Patch logger scripts to consume --sizing_contract before upper system can be faithfully paper/live tested.")
        report.append("Send logger_notional_code_snippets.txt so exact logger patch can be produced.")
    else:
        report.append("Logger scripts appear to contain sizing_contract support. Verify market_relative notional is half-size in paper logs.")
    (out_dir / "POSITION_SIZING_CONTRACT_REPORT.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))

if __name__ == "__main__":
    main()
