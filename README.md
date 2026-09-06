# Edge Scout

**A Strands agent that watches Polymarket for you and only speaks when there's a real edge.**

Built for the [Agents for Humans Hackathon](https://agentsforhumans.devpost.com/) · Track: **Professional Agents**

Prediction-market traders drown in noise: thousands of markets, wallets moving
constantly, and no honest signal for *which* move is actually smart money versus
a whale making a bad bet. Edge Scout is the analyst a small trader can't afford
to hire. It runs quietly in the background, reads Predge's **signed smart-money
data**, and pings you only when there's a one-sided, track-record-backed edge
the price hasn't already caught up to. Most of the time it correctly says
nothing.

The interesting part for an agent: Edge Scout **pays for its own data, per call,
in USDC** — Predge is a pure [x402](https://x402.org) pay-per-call API, no keys,
no accounts. The agent's tools hit a `402`, settle a few-cent micropayment, and
retry. It's a working example of an agent that autonomously buys exactly the
data it needs to make one decision.

---

## What it does

1. **Anchors** on `smart_money_consensus()` — 24h net USDC flow and direction
   from wallets with a Predge score above 70 (proven sharps).
2. **Confirms** a candidate with `market_whales()` (concentration) and
   `top_wallets()` / `wallet_profile()` (do these wallets actually win?).
3. **Sanity-checks** `market_movers()` so it never fades a move that already ran.
4. **Decides** with a conviction score and either raises **one** clear alert or
   stays silent (HOLD).

Run it once (`agent.py`) or as a background watcher (`watch.py`) that notifies a
webhook — Telegram, Slack, your backend — only on a real call.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Runs out of the box in MOCK mode (sample data, no wallet, no funds):
python agent.py

# Background watcher, stop after 3 scans (nice for a demo recording):
MAX_SCANS=3 SCAN_INTERVAL_SEC=5 python watch.py
```

### Going live (real x402 payments + real data)

```bash
cp .env.example .env
# 1) put a THROWAWAY wallet key with ~$1 USDC on Base in PREDGE_AGENT_PRIVATE_KEY
# 2) give the model a provider: AWS Bedrock creds (default), or set ANTHROPIC_API_KEY
python agent.py "focus on macro / rates markets"
```

MOCK mode is the default whenever `PREDGE_AGENT_PRIVATE_KEY` is unset, so the
repo is runnable by anyone the moment they clone it — no wallet required to see
the agent think.

## The tools (Predge, paid per call)

| Tool | Predge endpoint | Price | Why the agent uses it |
|---|---|---|---|
| `smart_money_consensus()` | `GET /v1/signals/consensus` | $0.03 | Anchor: sharp net flow + direction, 24h |
| `market_whales(conditionId)` | `GET /v1/whales/market/:id` | $0.01 | Confirm concentration on one market |
| `top_wallets(window, limit)` | `GET /v1/wallets/leaderboard` | $0.01 | Are the driving wallets actually sharp? |
| `wallet_profile(address)` | `GET /v1/wallets/:address` | $0.01 | Vet a single wallet's track record |
| `market_movers(window)` | `GET /v1/markets/movers` | $0.005 | Has the price already moved? |
| `daily_digest()` | `GET /v1/signals/daily` | $0.02 | Cheap broad background scan |

Predge only settles a payment on a `2xx`, so a failed call costs the agent
nothing. Prices are a few cents; a full live demo runs on about a dollar.

## Configuration

Everything is env-driven — see [`.env.example`](.env.example). Highlights:
`PREDGE_AGENT_PRIVATE_KEY` (live payments), `ANTHROPIC_API_KEY` / Bedrock creds
(model), `NOTIFY_WEBHOOK`, `SCAN_INTERVAL_SEC`, `MIN_CONVICTION`.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the diagram and the (one-file) path to
deploying on **Amazon Bedrock AgentCore**.

## Not financial advice

Edge Scout surfaces where proven wallets are moving. It does not place trades and
it is not investment advice — a human makes every call.

## License

MIT — see [LICENSE](LICENSE).

Amir Latypov · [predge.io](https://predge.io) · AWS Builder ID: _`<add before submitting>`_
