# Global instructions — Claude Code

Rules that apply to every project. Keep this file short: a rule belongs here only if its absence would cause a mistake. Add your own rules below the kit rules.

## Session flow (git repos)

- At the start, create a branch `session/YYYY-MM-DD-<topic>` from `main` and work only there. Never commit to `main`.
- Commit automatically after each finished, stable unit of work. Message in English: scope prefix + short imperative description (`landing-page: add hero section`). One subject per commit.
- Merge, push, PR and deploy happen only when the user asks. `/main` squash-merges the session branch into `main` and pushes.
- Never commit secrets. Never repeat a full key in chat.

## Session start

Orient yourself from four sources: claude-mem history (if installed), the project's `CLAUDE.md`, the latest file in `docs/worklog/`, and `git status`/branch/diff. The `SessionStart` hook injects the last two.

If the folder has no `CLAUDE.md`, create one: a short description of what the folder is for, the stack, and build/dev commands. Ask the user one question if the sources are not enough.

## Session end

Create `docs/worklog/YYYY-MM-DD-HHMM-<topic>.md`, one file per session, with `/log`. Never edit another session's file.

## Cost tracking

The `UserPromptSubmit` hook `cost-snapshot-reminder.sh` reminds you until a snapshot of the session exists. Follow the reminder silently: call `mcp__ccd_session_mgmt__get_usage`, then run `~/.claude/hooks/session-cost.py snapshot --session <id> --spent <plan.extraUsage.spent>`. Do not mention it in chat. `/log` uses the snapshot to report the real cost.

## Verification

- Never claim success without evidence: the command and its output, the diff, a number or a screenshot. If something was not verified, say so.
- If a runnable check exists (build, lint, test), run it and iterate until it passes before delivering.

## My rules

<!-- Add your own: language, tone, design system, tools, etc. -->
