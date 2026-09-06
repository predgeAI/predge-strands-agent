"""
predge_tools.py — the Predge signed smart-money API exposed as Strands tools.

Each function is a Strands `@tool`: its type hints become the tool schema and
its docstring is what the model reads to decide when to call it, so the wording
is deliberately about *when to use it*, not just what it returns. Every call
goes through `predge_client.get`, which pays the x402 micropayment underneath.
"""
from __future__ import annotations

from strands import tool

from predge_client import get


@tool
def smart_money_consensus() -> dict:
    """Premium 24h smart-money signal for Polymarket: per-market net USDC flow
    and directional lean (YES/NO) from wallets with a Predge score above 70 —
    the wallets with a proven realized track record. This is the single
    strongest "is there an edge right now" read; call it FIRST and anchor your
    decision on it. Returns net flow, direction, sharp-wallet count and average
    wallet score per market."""
    return get("/v1/signals/consensus")


@tool
def top_wallets(window: str = "30d", limit: int = 20) -> dict:
    """Leaderboard of the top Polymarket wallets by realized win rate on
    resolved markets only. `window` is "7d" or "30d". Use this to judge whether
    the wallets driving a signal are actually sharp, rather than lucky."""
    return get("/v1/wallets/leaderboard", {"window": window, "limit": limit})


@tool
def wallet_profile(address: str) -> dict:
    """Full profile for one wallet: Predge score, win rate by window, category
    specialisation (politics / macro / crypto / sports…) and its recent trades.
    Use to vet a specific wallet before trusting the move it is making."""
    return get(f"/v1/wallets/{address}")


@tool
def market_movers(window: str = "6h") -> dict:
    """Largest YES-price moves across Polymarket in the window ("1h", "6h" or
    "24h"), computed from real trade prints. Use this to check whether a move
    has already run — you do not want to enter an edge the market has priced."""
    return get("/v1/markets/movers", {"window": window})


@tool
def market_whales(condition_id: str) -> dict:
    """7-day whale activity (single trades >= $10k) and aggregates for ONE
    market, identified by its Polymarket conditionId. Use to confirm that a
    market flagged by the consensus signal has real, concentrated smart money
    behind it and not just a single outlier."""
    return get(f"/v1/whales/market/{condition_id}")


@tool
def daily_digest() -> dict:
    """Cheap 24h situational digest: top markets by activity, net flow, and the
    largest single bets. Good for a broad background scan before deciding
    whether any deeper (more expensive) look is warranted."""
    return get("/v1/signals/daily")


ALL_TOOLS = [
    smart_money_consensus,
    top_wallets,
    wallet_profile,
    market_movers,
    market_whales,
    daily_digest,
]
