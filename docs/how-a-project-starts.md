# What happens when you start a project in Claude Code

Everything below runs automatically once the kit is installed.

## 1. Before your first message — `SessionStart` hook

`hooks/session-start.sh` runs on `startup`, `resume`, `clear`, `compact` and `fork`. It adds to Claude's context:

- **Git state** (only in a git repo): current branch, pending changes, last 5 commits.
- **Folder contents**: first 30 entries of the current directory.
- **Latest worklog**: the newest file in `docs/worklog/` (first 60 lines). If the project only has a legacy `docs/WORKLOG.md`, the top entry is used instead.

If none of this exists (new, empty folder) the hook adds only the folder listing.

## 2. Instructions Claude reads

- `~/.claude/CLAUDE.md` — your global rules (from `templates/CLAUDE.global.md`).
- `CLAUDE.md` in the project folder — what the folder is for, stack, commands. If it does not exist, the global rules tell Claude to create one from the worklog, `docs/` and history, or to ask you one question.

## 3. First message — cost snapshot

The `UserPromptSubmit` hook `cost-snapshot-reminder.sh` checks for `~/.claude/state/session-cost/<session_id>.json`. If missing, it tells Claude to take the snapshot silently: read the account's current extra-usage spend and save it. You will not see this in chat. Details in [cost-tracking.md](cost-tracking.md).

## 4. During the session

- Claude creates a branch `session/YYYY-MM-DD-<topic>` and commits there after each stable unit of work. It never commits to `main`.
- With savvy-progress installed, the progress bar and the agents panel (`/agents-info`) show running subagents with an estimated cost.

## 5. End of the session

- `/log` writes `docs/worklog/YYYY-MM-DD-HHMM-<topic>.md` (done, decisions, files, next step, pending, cost). One file per session; Claude never edits another session's file.
- `/main` squash-merges the session branch into `main`, deletes the branch and pushes. Running it is the authorization; Claude does not ask twice.

## What does not happen automatically

Merge, push, deploy and `rm` only happen when you ask. Secrets are never committed.
