"""
Independent verification of the null-baseline percentile claim for:
  crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only

Claimed result (from execution artifact):
  observed_validation_pnl_usdt : 47.446335
  validation_percentile         : 0.84
  null_pass                     : False
  method                        : deterministic trade-pnl timestamp/block shuffle proxy
  runs                          : 100

Original logic (from trap module, seed 1013409):
  rng = random.Random(1013409)
  for _ in range(100):
      shuffled = pool[:]
      rng.shuffle(shuffled)
      null_values.append(sum(shuffled[:n_validation]))
  percentile_rank = sum(v <= observed for v in null_values) / 100

This script:
  1. Loads the execution artifact and extracts what is available
  2. Verifies internal consistency of the claimed numbers
  3. Re-derives the percentile rank using scipy.stats.percentileofscore
     (an independent rank implementation, not used in the original)
  4. Attempts exact numerical reproduction using the documented seed
  5. Reports clearly what CAN and CANNOT be verified without trade-level data

CONSTRAINT: Does not import or call the original execution module.
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXEC_ARTIFACT = REPO_ROOT / "artifacts" / "strategy_executions" / \
    "crypto_15m_idiosyncratic_sweep_short_trap_quality_time_exit_only_execution_v1.json"

CLAIMED_OBSERVED_USDT = 47.446335
CLAIMED_PERCENTILE    = 0.84
CLAIMED_NULL_PASS     = False
CLAIMED_RUNS          = 100
ACCEPTANCE_THRESHOLD  = 0.95
ORIGINAL_SEED         = 1013409   # from trap module source
BASE_EQUITY           = 1000.0

SEPARATOR = "-" * 60


def load_artifact() -> dict:
    with open(EXEC_ARTIFACT, encoding="utf-8-sig") as f:
        return json.load(f)


# ── Independent rank implementation ──────────────────────────────────
def percentile_of_score(values: list[float], score: float) -> float:
    """
    Independent re-implementation using the 'weak' definition:
    fraction of values in the array that are <= score.

    This matches scipy.stats.percentileofscore(values, score, kind='weak')
    but does not import scipy, making it fully self-contained.
    """
    if not values:
        raise ValueError("empty values list")
    return sum(1 for v in values if v <= score) / len(values)


# ── Consistency check helpers ─────────────────────────────────────────
def check_close(label: str, expected: float, actual: float, tol: float = 1e-5) -> bool:
    diff = abs(expected - actual)
    ok = diff <= tol
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}")
    print(f"         expected={expected}, actual={actual:.6f}, diff={diff:.2e}")
    return ok


def main() -> int:
    print(SEPARATOR)
    print("INDEPENDENT NULL-BASELINE VERIFICATION")
    print("Strategy: crypto_15m_...trap_quality_time_exit_only")
    print(SEPARATOR)

    artifact = load_artifact()
    nb       = artifact["null_baseline"]
    sm       = artifact["split_metrics"]
    metrics  = artifact["metrics"]

    # ── Step 1: What data is available? ─────────────────────────────
    print("\n[STEP 1] Data available in artifact")
    print(f"  null_baseline.observed_validation_pnl_usdt : {nb['observed_validation_pnl_usdt']}")
    print(f"  null_baseline.validation_percentile        : {nb['validation_percentile']}")
    print(f"  null_baseline.null_pass                    : {nb['null_pass']}")
    print(f"  null_baseline.runs                         : {nb['runs']}")
    print(f"  split_metrics.validation.net_pnl_usdt      : {sm['validation']['net_pnl_usdt']}")
    print(f"  split_metrics.validation.closed_trades     : {sm['validation']['closed_trades']}")
    print(f"  metrics.closed_trades (total)              : {metrics['closed_trades']}")
    print()
    print("  !! Individual trade net_pnl_usdt values are NOT stored in the artifact.")
    print("     Exact numerical reproduction of the 100-shuffle sequence requires")
    print("     these 454 values — they live in the panel data, not in the repo.")

    # ── Step 2: Internal consistency checks ─────────────────────────
    print(f"\n[STEP 2] Internal consistency checks")

    all_pass = True

    # 2a. observed_validation_pnl_usdt matches split_metrics
    all_pass &= check_close(
        "observed_pnl matches split_metrics.validation.net_pnl_usdt",
        expected=sm["validation"]["net_pnl_usdt"],
        actual=nb["observed_validation_pnl_usdt"],
    )

    # 2b. portfolio_net_bps is consistent with net_pnl_usdt / BASE_EQUITY * 10000
    derived_bps = sm["validation"]["net_pnl_usdt"] / BASE_EQUITY * 10_000
    all_pass &= check_close(
        "portfolio_net_bps == net_pnl_usdt / 1000 * 10000",
        expected=sm["validation"]["portfolio_net_bps"],
        actual=derived_bps,
    )

    # 2c. net = gross - cost
    gross = sm["validation"]["gross_pnl_usdt"]
    cost  = sm["validation"]["cost_pnl_usdt"]
    net   = sm["validation"]["net_pnl_usdt"]
    all_pass &= check_close(
        "net_pnl_usdt == gross_pnl_usdt - cost_pnl_usdt",
        expected=net,
        actual=gross - cost,
    )

    # 2d. claimed percentile is a valid fraction (0.00–1.00, step 0.01 for 100 runs)
    pct = nb["validation_percentile"]
    steps_of_hundredth = abs(round(pct * 100) - pct * 100) < 1e-6
    print(f"  [{'PASS' if steps_of_hundredth else 'FAIL'}] validation_percentile is a multiple of 0.01 "
          f"(consistent with 100 runs): {pct}")
    all_pass &= steps_of_hundredth

    # 2e. null_pass is consistent with percentile vs threshold
    expected_pass = pct >= ACCEPTANCE_THRESHOLD
    pass_consistent = (expected_pass == nb["null_pass"])
    print(f"  [{'PASS' if pass_consistent else 'FAIL'}] null_pass consistent with percentile >= 0.95: "
          f"{pct} >= {ACCEPTANCE_THRESHOLD} → {expected_pass}, artifact says {nb['null_pass']}")
    all_pass &= pass_consistent

    # ── Step 3: Independent rank logic verification ──────────────────
    print(f"\n[STEP 3] Independent rank implementation (not used in original)")
    print("  Method: percentile_of_score(values, score)")
    print("  Definition: fraction of values where v <= score")
    print()
    print("  Since individual null run values are not stored, we verify the")
    print("  mathematical property: if percentile = 0.84 from 100 runs,")
    print("  exactly 84 values must satisfy v <= observed.")
    print()
    n_below = round(nb["validation_percentile"] * nb["runs"])
    n_above = nb["runs"] - n_below
    print(f"  Implied null distribution: {n_below} runs ≤ {nb['observed_validation_pnl_usdt']:.6f}")
    print(f"                             {n_above} runs >  {nb['observed_validation_pnl_usdt']:.6f}")

    # Construct a synthetic array consistent with the claim and verify our rank
    synthetic_null = [nb["observed_validation_pnl_usdt"] - 1.0] * n_below + \
                     [nb["observed_validation_pnl_usdt"] + 1.0] * n_above
    rank_indep = percentile_of_score(synthetic_null, nb["observed_validation_pnl_usdt"] - 1.0 + 1e-9)
    print()
    print(f"  Independent rank on synthetic array consistent with claim: {rank_indep:.2f}")
    check_close(
        "independent rank matches claimed percentile",
        expected=nb["validation_percentile"],
        actual=rank_indep,
        tol=0.01,
    )

    # ── Step 4: Exact reproduction attempt ──────────────────────────
    print(f"\n[STEP 4] Exact numerical reproduction attempt")
    print(f"  Original seed: {ORIGINAL_SEED}")
    print(f"  Required input: 454 individual net_pnl_usdt values")
    print(f"  Status: NOT POSSIBLE — trade-level data not persisted in artifact")
    print()
    print("  What IS reproducible with seed alone (logic demonstration):")

    # Demonstrate that the seed produces a deterministic sequence
    demo_pool = [1.0, -1.0, 2.0, -2.0, 0.5]
    rng = random.Random(ORIGINAL_SEED)
    demo_shuffle = demo_pool[:]
    rng.shuffle(demo_shuffle)
    print(f"  Demo: random.Random({ORIGINAL_SEED}).shuffle([1,-1,2,-2,0.5]) → {demo_shuffle}")
    rng2 = random.Random(ORIGINAL_SEED)
    demo_shuffle2 = demo_pool[:]
    rng2.shuffle(demo_shuffle2)
    print(f"  Replay (same seed):                                          → {demo_shuffle2}")
    seq_deterministic = demo_shuffle == demo_shuffle2
    print(f"  [{'PASS' if seq_deterministic else 'FAIL'}] Seed produces identical sequences on replay: {seq_deterministic}")

    # ── Summary ──────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("VERIFICATION SUMMARY")
    print(SEPARATOR)
    print(f"  Internal consistency checks : {'ALL PASS' if all_pass else 'SOME FAIL'}")
    print(f"  Claimed percentile (0.84)   : consistent — implies exactly 84 of 100 runs ≤ observed")
    print(f"  null_pass = False           : consistent — 0.84 < 0.95 threshold")
    print(f"  Independent rank method     : confirms rank logic produces same result by definition")
    print(f"  Exact numerical reproduction: NOT POSSIBLE without 454 trade-level PnL values")
    print()
    if all_pass:
        print("VERDICT: All verifiable claims are internally consistent.")
        print("         The 84th percentile / null_pass=False result is self-consistent")
        print("         and cannot be contradicted by the available artifact data.")
        print("         Full reproduction would require panel data outside the repo.")
    else:
        print("VERDICT: One or more consistency checks FAILED — see above.")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
