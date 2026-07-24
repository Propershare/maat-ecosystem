# MAAT FVG Edge — Live Trading Readiness Assessment (2026-07-24)

## Current State
- **Paper account**: $80,242 equity, 1 open position (MDT put, -$57)
- **Pipeline**: data_fetcher → fvg_scanner → setup_ranker → entry_evaluator → paper_engine
- **Scan**: 81 symbols, 15 shortlist, 14 high-confidence setups
- **Dominant signal**: Broad bearish alignment across ES=F, SPY, QQQ — all below 50-yard lines with multiple retests
- **Cron jobs**: 09:25 ET market open watchdog, 16:15 ET daily ops, every 120m steering check
- **Dashboard**: http://localhost:8765 (port 8765)

## What's Working
1. Scanner pipeline runs reliably — fresh data every scan
2. 50-yard line methodology is producing consistent, interpretable setups
3. Paper account is funded and connected to Alpaca
4. Episodic memory logging is active (Sankofa driver + FVG edge pipeline)
5. Battle plans being written to state/ directory

## What's Missing for Live Trading
1. **No live Alpaca account connected** — paper only (PA3RC9SW3LOA)
2. **No entry_evaluator.py execution** — setups are identified but no automated entry decisions
3. **No lower-timeframe confirmation** (5m/15m) — 4H gives context but not entry precision
4. **No backtester** — no historical win-rate data to validate the methodology
5. **No position sizing model** — risk per trade, max drawdown, Kelly criteria not defined
6. **No trade journal** — no systematic record of why trades were taken or skipped
7. **No multi-timeframe confirmation** — roadmap V1.2 not implemented
8. **No live alert integration** — Telegram/Discord not wired (roadmap V3)
9. **No broker-agnostic execution layer** — paper_engine is Alpaca-specific
10. **No circuit breakers** — daily loss limit, max consecutive losses, volatility filter

## Goal
Build a consistent, agentic trading system that:
- Achieves a verified win rate through paper trading
- Can adjust strategy based on market regime (trending vs choppy)
- Has automated entry/exit rules with no emotional interference
- Survives the transition from paper to live without blowing up
- Funds a 5090 GPU purchase from trading profits

## Next Milestones (Priority Order)
1. **P1**: Run entry_evaluator.py on every scan — start making automated entry decisions on paper
2. **P1**: Build a trade journal — record every entry, exit, reason, and result
3. **P2**: Implement lower-timeframe confirmation (5m/15m after 4H signal)
4. **P2**: Build backtester — validate win rate on historical data
5. **P2**: Define position sizing rules (fixed % risk per trade)
6. **P3**: Wire live alerts (Telegram)
7. **P3**: Add circuit breakers (daily loss limit, volatility filter)
8. **P4**: Connect live Alpaca account
9. **P4**: Go live with small size, scale up as win rate proves out