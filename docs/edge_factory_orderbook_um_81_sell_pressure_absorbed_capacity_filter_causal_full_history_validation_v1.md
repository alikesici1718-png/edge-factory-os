# Sell pressure absorbed capacity filter causal full-history validation v1

This audit checks whether the locked capacity subset `MIN_AROUND_EVENT_NOTIONAL_100000` is causal before any full-history validation is allowed to run.

Locked settings:

- candidate: SELL_PRESSURE_ABSORBED@300s
- cooldown: 600 seconds
- capacity subset: MIN_AROUND_EVENT_NOTIONAL_100000
- intended coverage if causal: 2023-01-01 through 2026-06-15

Audit rule:

- If the capacity filter uses only event-time or pre-event/trailing information, a full-history validation may be run by a separate implementation.
- If the capacity filter uses post-event or forward-window notional, the run must be marked `LOOKAHEAD_BLOCKED` and no full-history stream may start.

Current finding:

- The existing helper `notional_around_event` uses `event_ms + CAPACITY_WINDOW_RADIUS_MS`.
- The locked capacity subset uses that helper.
- The filter is therefore lookahead-blocked.

Safety boundaries:

- No downloads.
- No full-history stream when lookahead-blocked.
- No parquet dataset.
- No row-level dataset.
- No strategy, backtest, PnL, signals, orders, private endpoints, or recommendations.
