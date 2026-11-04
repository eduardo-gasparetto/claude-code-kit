# Claude Code Kit

A shared setup for Claude Code: per-session cost tracking, a standard project start, one worklog file per session, and the savvy-progress agents panel.

## What you get

| Piece | What it does |
|---|---|
| `hooks/cost-snapshot-reminder.sh` + `hooks/session-cost.py` | Snapshot of the account's extra-usage spend at session start; Billed and Estimate cost at the end |
| `hooks/session-start.sh` | Injects git state, folder contents and the latest worklog when a session starts |
| `commands/log.md` (`/log`) | Writes `docs/worklog/YYYY-MM-DD-HHMM-<topic>.md`, including the cost |
| `commands/main.md` (`/main`) | Squash-merges the session branch into `main` and pushes |
| `templates/` | Global `CLAUDE.md`, project `CLAUDE.md`, worklog |
| savvy-progress plugin | Progress bar and agents panel (`/agents-info`) with estimated cost per subagent. Third-party plugin from `JohnnyVizz/claude-kit`, not part of this repo |

## Install

Requirements: Claude Code (desktop app for the cost flow), `python3`, `jq`.

1. Clone this repository and open Claude Code in its folder.
2. Paste the prompt from [INSTALL-PROMPT.md](INSTALL-PROMPT.md).
3. Restart Claude Code so the plugin loads.

The prompt backs up every file it changes and never overwrites your `permissions` or your existing `CLAUDE.md`.

## Daily use

1. Open a project and start working. The context and the cost snapshot are automatic.
2. Claude works on a `session/YYYY-MM-DD-<topic>` branch.
3. When done: `/log` to record the session, `/main` to merge into `main`.
4. `/agents-info` toggles the agents panel.

## Docs

- [What happens when you start a project](docs/how-a-project-starts.md)
- [Cost tracking and its limits](docs/cost-tracking.md)

## Notes

- savvy-progress is third-party code. Check it against your company's policy before enabling it; this kit does not audit it.
- Billed cost is account-wide. Run one session at a time when you want a clean number.
