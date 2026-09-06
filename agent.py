"""
agent.py — Edge Scout: a Strands agent that decides whether a Polymarket trader
has a real, actionable edge right now, and stays quiet when they don't.

Run one scan:
    python agent.py
    python agent.py "focus on macro / rates markets"

Model provider is chosen from the environment (see _resolve_model). By default
it uses Amazon Bedrock — the AWS-native path for this hackathon; deploying the
same agent to Bedrock AgentCore is a one-file change (see ARCHITECTURE.md).
"""
from __future__ import annotations

import os
import sys

from strands import Agent

from predge_client import is_mock
from predge_tools import ALL_TOOLS

SYSTEM_PROMPT = """You are Edge Scout, a research analyst for a single Polymarket trader.

Your job: decide whether there is a REAL, actionable edge right now — and if
there isn't, say so. You are not a hype machine. Most scans should end in HOLD.
A false alert costs the trader money and trust; silence is a valid, common,
correct answer.

You have paid tools into Predge's *signed* smart-money data. Every call costs
the trader a fraction of a cent in USDC, so be economical: do not fan out calls
you do not need to reach a confident decision.

Workflow:
  1. Call smart_money_consensus() — the sharp-wallet (score > 70) net flow.
     This is your anchor.
  2. If one market shows strong, one-sided sharp flow, CONFIRM it:
     market_whales(conditionId) for concentration, and top_wallets() /
     wallet_profile() to check the wallets behind it actually win.
  3. Sanity-check market_movers() so you are not fading a move that already ran
     (no edge left if the price is already there).

Score your conviction 0-100. Only return an ALERT when ALL hold:
  - sharp net flow is clearly one-sided (not marginal), AND
  - the wallets behind it have a genuine realized win rate, AND
  - the price has NOT already fully moved to reflect it.
Otherwise return HOLD.

Explain your reasoning briefly for the trader. Then, as the VERY LAST line of
your reply, output one line of strict JSON and nothing after it (no code fence):
{"decision":"alert"|"hold","market":<string or null>,"direction":"YES"|"NO"|null,"conviction":<int 0-100>,"why":<short string>}
"""


def _resolve_model():
    """Pick a model provider from the environment.

    Precedence: ANTHROPIC_API_KEY -> OpenAI -> Amazon Bedrock (default).
    Bedrock is the default because this is an AWS hackathon; set an API key if
    you do not have Bedrock model access. MODEL_ID overrides the model id in
    every case. Returns None to let Strands use its built-in Bedrock default.
    """
    model_id = os.getenv("MODEL_ID")
    if os.getenv("ANTHROPIC_API_KEY"):
        from strands.models import AnthropicModel

        return AnthropicModel(model_id=model_id or "claude-sonnet-4-5", max_tokens=2048)
    if os.getenv("OPENAI_API_KEY"):
        from strands.models import OpenAIModel

        return OpenAIModel(model_id=model_id or "gpt-4o")
    return model_id  # string id for Bedrock, or None -> Strands default


def build_agent() -> Agent:
    kwargs = {"tools": ALL_TOOLS, "system_prompt": SYSTEM_PROMPT}
    model = _resolve_model()
    if model:
        kwargs["model"] = model
    return Agent(**kwargs)


def main() -> None:
    focus = " ".join(sys.argv[1:]).strip()
    prompt = (
        "Scan Polymarket right now and decide if I have an actionable edge. "
        "Give me your call."
    )
    if focus:
        prompt += f" Focus: {focus}."

    mode = "MOCK (sample data — no wallet)" if is_mock() else "LIVE (paying x402 per call)"
    print(f"[Edge Scout] mode: {mode}\n")

    agent = build_agent()
    result = agent(prompt)  # Strands streams the reply to stdout as it goes
    # `result` also carries the final text; print a trailing newline for tidiness
    print()
    return result


if __name__ == "__main__":
    main()
