"""
predge_client.py — thin HTTP client for the Predge whale-data API.

Predge (https://api.predge.io) is a *pure x402 pay-per-call* API: no API keys,
no accounts. Every request to a `/v1/*` endpoint is answered with HTTP 402 until
an x402 USDC micropayment is attached. This module hides that so the agent's
tools just call `get(path)` and get JSON back — the per-call payment happens
transparently underneath, exactly the "agents pay for what they use" pattern.

Two modes:
  * LIVE — a funded wallet signs each x402 payment (real agent-pays-per-call).
           Enable by setting PREDGE_AGENT_PRIVATE_KEY to a *throwaway* wallet
           holding a little USDC on the chain api.predge.io settles on (Base).
  * MOCK — no wallet: returns representative sample payloads so the agent, the
           tests and the demo run with zero funds. On by default when no
           private key is set, or force it with PREDGE_MOCK=1.

The private key is read only from the environment and is never logged. Prices
are fractions of a cent per call ($0.005–$0.03), so a live demo needs ~$1.
"""
from __future__ import annotations

import os
import random
from typing import Any

import requests

PREDGE_API_BASE = os.getenv("PREDGE_API_BASE", "https://api.predge.io").rstrip("/")
_PRIVATE_KEY = os.getenv("PREDGE_AGENT_PRIVATE_KEY", "").strip()
_MOCK = os.getenv("PREDGE_MOCK", "").strip().lower() in ("1", "true", "yes") or not _PRIVATE_KEY

_session = None  # lazily-built x402 session (LIVE mode only)


def is_mock() -> bool:
    """True when running without a funded wallet (sample data)."""
    return _MOCK


def _live_session():
    """Build (once) a requests-compatible session that auto-pays x402 402s."""
    global _session
    if _session is not None:
        return _session
    # Imported lazily so MOCK mode does not require the web3 deps to be present.
    from eth_account import Account
    from x402.clients import x402_requests

    account = Account.from_key(_PRIVATE_KEY)
    _session = x402_requests(account)
    return _session


def get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET a Predge endpoint, paying the x402 micropayment if the server asks.

    `path` is e.g. "/v1/signals/consensus". Returns parsed JSON. In LIVE mode a
    402 triggers a USDC payment and an automatic retry; the handler only settles
    on a 2xx, so a failed call costs nothing.
    """
    if _MOCK:
        return _mock(path, params or {})
    url = f"{PREDGE_API_BASE}{path}"
    resp = _live_session().get(url, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------- #
# MOCK payloads — shaped like the real endpoints so the agent behaves the same
# with or without a wallet. Clearly flagged with "_mock": true.
# --------------------------------------------------------------------------- #
def _mock(path: str, params: dict[str, Any]) -> dict[str, Any]:
    if path == "/v1/signals/consensus":
        return {
            "_mock": True,
            "window": "24h",
            "min_score": 70,
            "markets": [
                {
                    "conditionId": "0x9a3f...c21e",
                    "question": "Fed cuts rates at the September 2026 meeting?",
                    "sharp_wallets": 11,
                    "net_flow_usdc": 184_500,
                    "direction": "NO",
                    "avg_wallet_score": 82,
                },
                {
                    "conditionId": "0x41bd...77aa",
                    "question": "Will BTC close above $150k on Sep 30?",
                    "sharp_wallets": 4,
                    "net_flow_usdc": 22_100,
                    "direction": "YES",
                    "avg_wallet_score": 74,
                },
            ],
        }
    if path == "/v1/wallets/leaderboard":
        return {
            "_mock": True,
            "window": params.get("window", "30d"),
            "wallets": [
                {"address": "0xA11ce...9f2", "score": 88, "win_rate": 0.71, "resolved": 143, "top_category": "politics"},
                {"address": "0xB0b...4c7", "score": 84, "win_rate": 0.66, "resolved": 98, "top_category": "macro"},
                {"address": "0xCa11...aa1", "score": 81, "win_rate": 0.63, "resolved": 210, "top_category": "crypto"},
            ][: int(params.get("limit", 20))],
        }
    if path.startswith("/v1/wallets/"):
        addr = path.rsplit("/", 1)[-1]
        return {
            "_mock": True,
            "address": addr,
            "score": 85,
            "win_rate": {"7d": 0.69, "30d": 0.67},
            "categories": {"politics": 0.72, "macro": 0.61},
            "last_trades": [
                {"market": "Fed cuts in September?", "side": "NO", "size_usdc": 42000, "price": 0.38},
                {"market": "Gov shutdown by Oct 1?", "side": "YES", "size_usdc": 15500, "price": 0.55},
            ],
        }
    if path == "/v1/markets/movers":
        return {
            "_mock": True,
            "window": params.get("window", "6h"),
            "movers": [
                {"conditionId": "0x9a3f...c21e", "question": "Fed cuts rates in September 2026?", "yes_delta": -0.09, "from": 0.47, "to": 0.38},
                {"conditionId": "0x77de...0b3", "question": "Ceasefire announced this month?", "yes_delta": +0.06, "from": 0.20, "to": 0.26},
            ],
        }
    if path.startswith("/v1/whales/market/"):
        cid = path.rsplit("/", 1)[-1]
        return {
            "_mock": True,
            "conditionId": cid,
            "window": "7d",
            "whale_trades": 17,
            "net_flow_usdc": 176_200,
            "dominant_side": "NO",
            "largest_bet_usdc": 48_000,
            "distinct_wallets": 9,
        }
    if path == "/v1/signals/daily":
        return {
            "_mock": True,
            "window": "24h",
            "top_markets": [
                {"question": "Fed cuts rates in September 2026?", "volume_usdc": 2_410_000, "net_flow_usdc": -184_500},
                {"question": "Will BTC close above $150k on Sep 30?", "volume_usdc": 890_000, "net_flow_usdc": 22_100},
            ],
            "largest_bet": {"market": "Fed cuts in September?", "side": "NO", "size_usdc": 48_000},
        }
    return {"_mock": True, "path": path, "params": params, "note": "no mock fixture for this path"}
