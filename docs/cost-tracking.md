# Cost tracking

Two numbers per session, both written to the worklog by `/log`.

| Measure | How it is computed | Caveat |
|---|---|---|
| **Billed** | `extraUsage.spent` now minus `extraUsage.spent` at the start snapshot | Account-wide: other sessions or usage in the same period inflate it |
| **Estimate** | Tokens from the session transcript (plus subagents) at list price | Approximation; unknown models are listed as unpriced and left out |

## Flow

1. **Snapshot** (first message of the session). The `UserPromptSubmit` hook reminds Claude until `~/.claude/state/session-cost/<session_id>.json` exists. Claude calls `get_usage`, reads `plan.extraUsage.spent` and runs `session-cost.py snapshot`. An existing snapshot is never overwritten.
2. **Report** (`/log`). Claude reads `spent` again and runs `session-cost.py report`. The two output lines go into the `## Cost` section.

## Prices

`session-cost.py` reads the public Anthropic pricing page and caches it for 7 days in `~/.claude/state/session-cost/prices.json`. If the page and the cache are unavailable, it uses a hard-coded table (`FALLBACK`), which can be out of date. The Estimate also applies the fast-mode multiplier, the long-prompt tier of Haiku, the US-geo surcharge (+10%) and US$ 0.01 per web search.

## Limits

- Needs the **Claude desktop app**: the `get_usage` tool does not exist in the terminal CLI, and the hook stays silent there.
- Needs extra usage enabled on the plan; otherwise there is no `spent` value to snapshot.
- No alert or hard limit. The cost shows up only in `/log` and in the savvy-progress panel.
- The savvy-progress panel keeps its own estimate (own price table). It does not share data with `session-cost.py`.

## Manual use

```bash
~/.claude/hooks/session-cost.py snapshot --session <session_id> --spent 127.52
~/.claude/hooks/session-cost.py report   --cwd "$PWD" --session <session_id> --spent 129.80
```
