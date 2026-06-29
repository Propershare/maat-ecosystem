# FVG Edge Trading System

## Identity
- System: MAAT FVG Edge (50-yard line methodology)
- Based on: Easy E's ICT/SMC framework
- Status: Paper trading via Alpaca
- Account: PA3RC9SW3LOA (paper)

## Methodology
1. 4H FVG gives context/bias
2. 50-yard line (FVG midpoint) is the battlefield
3. Sweep grabs liquidity
4. Retest confirms respect
5. First target = opposing FVG
6. Entry via bracket order (market + stop + take profit)

## Components
- `trading-system/scripts/paper_engine.py` — Alpaca REST client
- `trading-system/scripts/entry_evaluator.py` — Easy E entry rules
- `trading-system/scripts/maat_daily_loop_ops.py` — daily cron ops
- `trading-system/scripts/dashboard_server.py` — web dashboard (port 8765)
- `trading-system/scripts/orchestrator.py` — data pipeline (fetch → scan → rank)
- `trading-system/scripts/fvg_scanner.py` — FVG detection engine
- `trading-system/scripts/setup_ranker.py` — setup prioritization
- `trading-system/scripts/data_fetcher.py` — OHLCV data fetcher

## Pipeline
1. data_fetcher.py → fetches 4H OHLCV for 55+ tickers
2. fvg_scanner.py → detects FVGs, sweeps, retests
3. setup_ranker.py → filters/ranks setups
4. entry_evaluator.py → evaluates against Easy E rules
5. paper_engine.py → places bracket orders on Alpaca

## Cron Jobs
- 09:25 ET — market open watchdog (maat_market_open_check.py)
- 16:15 ET — daily ops loop (maat_daily_loop_ops.py)
- Every 120m — project steering check

## Dashboard
- URL: http://localhost:8765
- Auto-refresh: 30s
- Shows: account, positions, orders, shortlist, activity
