# Orderbook UM 30d Absorption Pilot Notes V1

## Scope

This module expands the existing diagnostic pilot to BTCUSDT, ETHUSDT, and SOLUSDT over one 30-calendar-day window only.

The window is selected from the existing Binance USD-M bookDepth availability manifest as the latest 30 complete days ending at the latest common complete day for all three symbols.

Raw bookDepth and aggTrades ZIP files are stored under the configured external data root, not inside the git repo.

## Data Sources

- Binance Data Vision USD-M Futures daily bookDepth.
- Binance Data Vision USD-M Futures daily aggTrades.
- Public archive data only.

No API keys, private endpoints, account endpoints, live trading, paper trading, execution actions, candidate generation, entries, exits, stops, targets, position sizing, leverage logic, PnL, trade signals, buy/sell labels, or recommendations are part of this module.

## bookDepth Schema Limitation

The Data Vision bookDepth files used here contain timestamp, percentage, depth, and notional columns.

This is percentage-depth data, not a true full L2 level-book feed. Exact best bid/ask, exact level-1 quantities, exact top-5 levels, exact top-10 levels, and exact microprice remain unsupported.

The preview derives percentage-depth proxies such as mid_price_proxy_pct1, spread_proxy_pct1, spread_bps_proxy_pct1, pct-1/pct-5 depth, imbalance, microprice proxy, liquidity-pull proxy, and rolling proxy diagnostics.

## aggTrades Convention

Binance aggTrades include isBuyerMaker.

If isBuyerMaker is true, the buyer was maker and the aggressive/taker side is sell.

If isBuyerMaker is false, the buyer was taker and the aggressive/taker side is buy.

The preview uses this convention for aggressive buy and aggressive sell quantity and notional features.

## Alignment Rule

At timestamp T, feature construction uses only bookDepth and aggTrades information available at or before T.

Forward returns from the bookDepth mid price proxy are retained only as diagnostics. They are not input features for forward-looking construction and are not presented as trading outcomes.

## Diagnostic Categories

The categories are diagnostic buckets only:

- BUY_PRESSURE_ABSORBED
- SELL_PRESSURE_ABSORBED
- FLOW_AND_DEPTH_ALIGNED_UP
- FLOW_AND_DEPTH_ALIGNED_DOWN
- MIXED_OR_NOISY
- INSUFFICIENT_DATA

They are not long/short instructions and are not trade recommendations.

## Outputs

The module writes a 30-day pilot manifest, download summary, absorption preview summary, category diagnostics, quantile diagnostics, daily stability, symbol stability, a quality report, and a bounded feature sample.

replacement_checks_all_true is required before downstream review.
