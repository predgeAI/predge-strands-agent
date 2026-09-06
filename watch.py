"""
watch.py — run Edge Scout on a schedule and stay silent unless there's a real
call. This is the "runs quietly in the background, only pings you when there's a
real decision to make" pattern the hackathon explicitly rewards.

    python watch.py

Env:
    SCAN_INTERVAL_SEC   seconds between scans (default 900 = 15 min)
    MIN_CONVICTION      minimum conviction to notify (default 70)
    NOTIFY_WEBHOOK      optional URL; the alert JSON is POSTed to it
                        (Telegram/Slack/Discord/your backend). If unset,
                        alerts print to stdout.
    MAX_SCANS           stop after N scans (default 0 = run forever) — handy
                        for a demo recording.
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone

import requests

from agent import build_agent
from predge_client import is_mock

INTERVAL = int(os.getenv("SCAN_INTERVAL_SEC", "900"))
MIN_CONVICTION = int(os.getenv("MIN_CONVICTION", "70"))
WEBHOOK = os.getenv("NOTIFY_WEBHOOK", "").strip()
MAX_SCANS = int(os.getenv("MAX_SCANS", "0"))

_JSON_LINE = re.compile(r"\{.*\"decision\".*\}", re.DOTALL)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _extract_decision(text: str) -> dict:
    """Pull the trailing strict-JSON decision line out of the agent's reply."""
    matches = _JSON_LINE.findall(str(text))
    if not matches:
        return {"decision": "hold", "conviction": 0, "why": "no parseable decision"}
    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError:
        return {"decision": "hold", "conviction": 0, "why": "unparseable decision json"}


def _notify(decision: dict) -> None:
    line = (
        f"🎯 EDGE ALERT  {decision.get('market')}  ->  {decision.get('direction')}  "
        f"(conviction {decision.get('conviction')})\n   {decision.get('why')}"
    )
    print(f"\n{line}\n")
    if WEBHOOK:
        try:
            requests.post(WEBHOOK, json={"text": line, "decision": decision}, timeout=15)
        except requests.RequestException as e:  # never let a webhook failure kill the loop
            print(f"[warn] webhook failed: {e}")


def scan_once(agent) -> dict:
    result = agent(
        "Background scan. Decide if there is an actionable edge right now. "
        "Be economical with tool calls. End with the strict JSON decision line."
    )
    decision = _extract_decision(getattr(result, "message", result))
    alert = decision.get("decision") == "alert" and int(decision.get("conviction", 0)) >= MIN_CONVICTION
    stamp = _now()
    if alert:
        _notify(decision)
    else:
        # quiet by design — one terse heartbeat line, nothing that demands attention
        print(f"[{stamp}] hold — {decision.get('why', 'no edge')} (conv {decision.get('conviction', 0)})")
    return decision


def main() -> None:
    mode = "MOCK" if is_mock() else "LIVE x402"
    print(
        f"[Edge Scout watcher] mode={mode}  interval={INTERVAL}s  "
        f"min_conviction={MIN_CONVICTION}  webhook={'on' if WEBHOOK else 'off'}"
    )
    agent = build_agent()
    scans = 0
    while True:
        try:
            scan_once(agent)
        except Exception as e:  # a bad scan should never stop the watcher
            print(f"[{_now()}] scan error: {e}")
        scans += 1
        if MAX_SCANS and scans >= MAX_SCANS:
            print(f"[Edge Scout watcher] reached MAX_SCANS={MAX_SCANS}, stopping.")
            return
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
