# Demo video script (≤5 min)

Screen recording + voiceover, no face needed. Target ~4:00.

## 0:00–0:35 — The problem
- Show Polymarket: a wall of markets, prices ticking.
- VO: "If you trade prediction markets, this is your day — thousands of markets,
  wallets moving constantly, and no honest way to tell smart money from a whale
  making a dumb bet. Watching this all day is a full-time job most traders can't
  afford to hire for."

## 0:35–1:00 — The idea
- Title card: **Edge Scout — a Strands agent that watches for you, and only
  speaks when there's a real edge.**
- VO: "Edge Scout runs in the background, reads *signed* smart-money data, and
  pings you only when there's an edge worth acting on. And it pays for that data
  itself, per call, in USDC."

## 1:00–2:20 — It thinks (run `agent.py`)
- Terminal: `python agent.py "focus on macro / rates markets"`
- Point out the tool calls streaming: consensus → whales → wallet check → movers.
- VO: "It anchors on the sharp-wallet consensus, confirms the whales are
  concentrated, checks those wallets actually win, and makes sure the price
  hasn't already moved."
- Land on the final decision line (alert with conviction + why).

## 2:20–3:10 — It pays (the x402 moment)
- Show `ARCHITECTURE.md` diagram briefly, then (LIVE mode) show a request:
  `402 Payment Required` → USDC micropayment → `200` with data.
- VO: "This is the part that's new. Each tool call is a real purchase — the agent
  hits a 402, signs a few-cent USDC payment on Base, and gets its data. Predge
  only charges on success. A real agent-to-service transaction, inside one tool
  call."

## 3:10–3:50 — It stays quiet (run `watch.py`)
- Terminal: `MAX_SCANS=3 SCAN_INTERVAL_SEC=5 python watch.py`
- Show two `hold` heartbeats, then one `🎯 EDGE ALERT` firing to the webhook.
- VO: "Most of the time the honest answer is 'hold' — and it says nothing. When a
  real edge appears, one alert, straight to your phone."

## 3:50–4:00 — Close
- Title card: **Strands + Predge x402 · runnable in one command · MIT.**
- VO: "Edge Scout. The analyst a small trader couldn't hire — that pays its own way."

## Shot list / prep
- Record MOCK mode for reliability; capture ONE real LIVE 402→200 for the payment beat.
- Pre-fund the throwaway wallet with ~$1 USDC on Base before recording.
- Have the webhook point at a Telegram test chat so the alert visibly lands.
