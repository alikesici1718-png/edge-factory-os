from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def load_sizing_contract(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return {}
    return json.loads(p.read_text(encoding="utf-8-sig"))

def resolve_family_notional(
    family_key: str,
    *,
    default_notional: float = 50.0,
    sizing_contract_path: str | Path | None = None,
    base_equity: float | None = None,
) -> float:
    if not sizing_contract_path:
        return float(default_notional)
    cfg = load_sizing_contract(sizing_contract_path)
    fam = cfg.get("families", {}).get(family_key, {})
    if not fam:
        return float(default_notional)
    if base_equity is None:
        base_equity = float(cfg.get("base_equity", 1000.0))
    fixed = fam.get("fixed_notional", None)
    if fixed is not None:
        return float(fixed)
    cf = fam.get("capital_fraction", None)
    if cf is None:
        return float(default_notional)
    return float(base_equity) * float(cf)
