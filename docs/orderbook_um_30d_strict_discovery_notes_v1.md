# Orderbook UM 30d Strict Discovery Notes V1

## Scope

This module evaluates whether the 30-day BTCUSDT, ETHUSDT, and SOLUSDT absorption diagnostics show stable non-random forward mid-return separation.

It is a diagnostic research evaluator only. It is not a trading strategy, not a backtest, not a signal generator, and not an execution module.

No API keys, private endpoints, account endpoints, live trading, paper trading, order execution, candidate generation for trading, entries, exits, stops, targets, position sizing, leverage logic, PnL, buy/sell labels, or trade recommendations are part of this module.

## Inputs

The evaluator uses existing 30-day absorption outputs and rebuilds compact row diagnostics from already downloaded and checksum-verified external pilot ZIP files when strict checks require symbol-day row evidence.

It does not download 90-day data, does not download full 81-symbol data, and does not write raw market data into the git repo.

## Hypotheses

- H1: BUY_PRESSURE_ABSORBED should show weaker forward mid returns than baseline.
- H2: SELL_PRESSURE_ABSORBED should show stronger forward mid returns than baseline.
- H3: FLOW_AND_DEPTH_ALIGNED_UP should show stronger positive forward mid returns than baseline.
- H4: FLOW_AND_DEPTH_ALIGNED_DOWN should show stronger negative forward mid returns than baseline.

Baseline definitions are MIXED_OR_NOISY and unconditional all-category baseline.

## Strict Research Labels

- DISCOVERY_CANDIDATE means strict diagnostic criteria passed for the category and horizon. It is not a tradable strategy label.
- WEAK_MONITOR_ONLY means some evidence exists but strict criteria did not fully pass.
- FAIL_NO_STABLE_SEPARATION means the strict checks did not show stable separation.
- BLOCKED_INSUFFICIENT_DIAGNOSTIC_DATA means required inputs or evidence were unavailable.

These labels are research labels only and must not be read as trade recommendations.

## Statistical Checks

The evaluator uses bootstrap confidence intervals for mean effects, within-symbol-day permutation/null tests, and Benjamini-Hochberg false discovery rate correction across category/horizon tests.

Forward returns are diagnostic outcomes only and are not used as features for construction.

replacement_checks_all_true is required before downstream review.
