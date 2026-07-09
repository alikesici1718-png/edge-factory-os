#!/usr/bin/env python3
"""
Edge Factory OS - Command Line Interface

A thin wrapper around existing pipeline scripts. This CLI does not
reimplement any logic - it only routes commands to existing, tested files.
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

def run_script(script_path, extra_args=None):
    """Run an existing script via subprocess, passing through output."""
    full_path = REPO_ROOT / script_path
    if not full_path.exists():
        print(f"Error: {script_path} not found at {full_path}")
        sys.exit(1)
    cmd = [sys.executable, str(full_path)] + (extra_args or [])
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(
        description="Edge Factory OS CLI - routes to existing pipeline scripts"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("evaluate-example",
        help="Run the institutional size classification pilot (example evaluation)")
    subparsers.add_parser("status",
        help="Show a summary of artifacts/ contents (closures, evaluations)")

    args = parser.parse_args()

    if args.command == "evaluate-example":
        run_script("institutional_size_classification_pilot.py")
    elif args.command == "status":
        # Bu, YENİ bir küçük script - artifacts/ klasöründeki dosya sayılarını
        # özetleyen, salt-okunur bir durum raporu. Hiçbir mevcut dosyayı okumaz/değiştirmez.
        import json
        closures = list((REPO_ROOT / "artifacts" / "strategy_closures").glob("*.json"))
        evals = list((REPO_ROOT / "artifacts" / "strategy_evaluations").glob("*.json"))
        print(f"Strategy evaluations: {len(evals)}")
        print(f"Strategy closures: {len(closures)}")
        print(f"See README.md for full findings.")

if __name__ == "__main__":
    main()
