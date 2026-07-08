#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

TARGET = SCRIPT_DIR / "global_paper_risk_manager_v4_config.py"
REAL_V3 = SCRIPT_DIR / "global_paper_risk_manager_v3_priority.py"
PAPER_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

FLAT_CONFIG = WORKSPACE / "edge_factory_master_upper_system_family_config" / "master_upper_system_family_config_FLAT_FOR_RISK_MANAGER.json"

MAX_PER_FAMILY = {
    "old_short": 3,
    "impulse_long": 2,
    "market_relative_short": 3,
    "weak_market_short": 2,
}

FAMILY_PRIORITY = {
    "impulse_long": 150,
    "old_short": 100,
    "market_relative_short": 70,
    "weak_market_short": 30,
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_risk_manager_v4_wrapper_patch" / f"risk_wrapper_patch_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    flat_config = {
        "old_short": str(PAPER_DIR / "old_short"),
        "impulse_long": str(PAPER_DIR / "impulse_long"),
        "market_relative_short": str(PAPER_DIR / "market_relative_short"),
        "weak_market_short": str(PAPER_DIR / "weak_market_short"),
    }
    write_json(FLAT_CONFIG, flat_config)

    backup = None
    if TARGET.exists():
        backup = out_dir / "backup_global_paper_risk_manager_v4_config.py"
        shutil.copy2(TARGET, backup)

    wrapper = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

REAL_V3 = Path(r"{REAL_V3}")
FAMILY_CONFIG = Path(r"{FLAT_CONFIG}")
OUT_DIR = Path(r"{PAPER_DIR}")

MAX_PER_FAMILY = {json.dumps(MAX_PER_FAMILY, ensure_ascii=False)}
FAMILY_PRIORITY = {json.dumps(FAMILY_PRIORITY, ensure_ascii=False)}

def remove_arg(argv, name):
    out = []
    i = 0
    while i < len(argv):
        if argv[i] == name:
            i += 2
            continue
        out.append(argv[i])
        i += 1
    return out

def upsert_arg(argv, name, value):
    argv = remove_arg(argv, name)
    argv.extend([name, str(value)])
    return argv

def remove_flag(argv, name):
    return [x for x in argv if x != name]

def main():
    if not REAL_V3.exists():
        raise SystemExit(f"REAL risk manager missing: {{REAL_V3}}")

    argv = sys.argv[:]

    # Sanitize launcher / PowerShell quoting issues.
    argv = upsert_arg(argv, "--family_config", FAMILY_CONFIG)
    argv = upsert_arg(argv, "--out_dir", OUT_DIR)
    argv = upsert_arg(argv, "--global_max_positions", 6)
    argv = upsert_arg(argv, "--max_short_positions", 5)
    argv = upsert_arg(argv, "--max_long_positions", 2)
    argv = upsert_arg(argv, "--max_per_family_json", json.dumps(MAX_PER_FAMILY))
    argv = upsert_arg(argv, "--family_priority_json", json.dumps(FAMILY_PRIORITY))

    # Ensure backup-only flag exists once.
    argv = remove_flag(argv, "--weak_market_backup_only")
    argv.append("--weak_market_backup_only")

    # Keep --once if caller passed it; launcher without --once will run continuous manager.
    sys.argv = [str(REAL_V3)] + argv[1:]

    return runpy.run_path(str(REAL_V3), run_name="__main__")

if __name__ == "__main__":
    main()
'''

    TARGET.write_text(wrapper, encoding="utf-8")

    state = {
        "target": str(TARGET),
        "real_v3": str(REAL_V3),
        "flat_config": str(FLAT_CONFIG),
        "paper_dir": str(PAPER_DIR),
        "backup": str(backup) if backup else None,
        "wrapper_written": True,
        "live_allowed": False,
        "note": "Wrapper delegates to real v3 priority risk manager and injects safe args.",
    }
    write_json(out_dir / "risk_manager_v4_wrapper_patch_state.json", state)

    print("EDGE FACTORY RISK MANAGER v4 WRAPPER PATCH")
    print("=" * 100)
    print(f"target: {TARGET}")
    print(f"real_v3: {REAL_V3}")
    print(f"flat_config: {FLAT_CONFIG}")
    print(f"backup: {backup}")
    print("wrapper_written: True")
    print("live_allowed: False")
    print(f"State: {out_dir / 'risk_manager_v4_wrapper_patch_state.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
