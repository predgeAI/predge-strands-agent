# Edge Scout — Devpost submission

**Track:** Professional Agents
**Elevator pitch:** A Strands agent that watches Polymarket for a trader and only
speaks when there's a real, track-record-backed edge — and pays for its own data,
per call, in USDC.

## The problem (who it's for, why it matters)

Prediction-market traders — the individuals, not the funds — face thousands of
markets and constant wallet activity with no honest signal for *which* move is
smart money. Sitting and staring at flow all day is exactly the repetitive,
judgment-heavy work that eats a professional's day. Hiring an analyst isn't an
option at their size. The result: they either over-trade on noise or miss the
few moments that actually matter.

Edge Scout is that analyst. It runs quietly in the background and pings the
trader only when there's a one-sided, proven-wallet edge the price hasn't already
caught. Most scans end in silence — which is the point.

## What it does

- Anchors on Predge's **signed smart-money consensus** (net USDC flow + direction
  from wallets scoring above 70 on realized win rate).
- Confirms candidates with whale concentration and per-wallet track records, and
  rejects moves that have already run.
- Emits a single conviction-scored alert, or holds. Alerts go to a webhook
  (Telegram / Slack / a backend) so it truly runs in the background.

## How we built it

- **Strands Agents SDK** for the agent loop and the six `@tool` functions.
- **Predge** (api.predge.io) as the data layer — a production x402 pay-per-call
  API over a read-only view of Polymarket trades/markets/wallets.
- **x402 + eth-account** for the payment: each tool call hits a `402`, signs a
  USDC micropayment on Base, and retries. Predge settles only on `2xx`, so failed
  calls are free.
- Model: Amazon Bedrock Claude by default; Anthropic/OpenAI are drop-in. Ships
  with a one-file **Bedrock AgentCore** entrypoint.
- A MOCK mode (sample data, no wallet) so anyone can clone and run it instantly.

## The agent-economy angle

The demo isn't just "LLM calls an API". The agent autonomously decides which one
question it needs answered and buys exactly that data for a few cents. That's a
real agent-to-service micro-transaction happening inside a single tool call — the
pattern the whole x402 ecosystem is betting on, shown working end-to-end.

## Challenges

- Tuning the agent to *stay quiet*: the first version alerted on everything.
  The fix was hard conviction gates in the system prompt (one-sided flow **and**
  proven wallets **and** unspent price) plus a numeric threshold in the watcher.
- Keeping the repo runnable with zero setup while still demonstrating real
  payments — solved with the MOCK/LIVE split.

## What's next

- Wire the trader's own risk limits so alerts carry position sizing.
- Deploy the watcher on AgentCore Runtime for always-on hosting.
- Add Predge's signed-call attestations so each alert is verifiable after the
  outcome resolves.

## Links

- Code: _`<public repo URL>`_
- Demo video: _`<≤5-min video URL>`_
- Live demo (optional): _`<url>`_
- AWS Builder ID: _`<id>`_
- Built by Amir Latypov · https://predge.io
