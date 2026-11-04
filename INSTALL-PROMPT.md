# Install prompt

Open Claude Code **in the root of this repository** and paste everything inside the block below.

````text
Install the Claude Code kit from this repository on my machine. Work step by step and show what you do.

Rules for this install:
- Never overwrite an existing file without showing me the difference and asking.
- Back up every file you modify as `<file>.bak-kit` before changing it.
- Do not touch the `permissions` block of my settings.json.

Steps:

1. Check prerequisites: `python3 --version` and `jq --version`. If one is missing, stop and tell me how to install it.

2. Copy files into `~/.claude`:
   - `hooks/*` -> `~/.claude/hooks/` (keep them executable)
   - `commands/log.md` and `commands/main.md` -> `~/.claude/commands/`
   If a target already exists and differs, show the diff and ask.

3. Merge hooks into `~/.claude/settings.json` (create the file as `{}` if it does not exist). Use `jq`, never a blind overwrite. Add these entries, keeping any hooks I already have:
   - `hooks.SessionStart`: matcher `startup|resume|clear|compact|fork`, command `bash ~/.claude/hooks/session-start.sh`, timeout 15
   - `hooks.UserPromptSubmit`: command `bash ~/.claude/hooks/cost-snapshot-reminder.sh`, timeout 5
   Skip an entry if the same command is already registered. Validate the result with `jq empty ~/.claude/settings.json`.

4. Register the savvy-progress plugin in the same settings.json:
   - `extraKnownMarketplaces.claude-kit` = `{"source": {"source": "github", "repo": "JohnnyVizz/claude-kit"}}`
   - `enabledPlugins."savvy-progress@claude-kit"` = `true`
   Then tell me to restart Claude Code so the plugin loads. If I prefer, I can run `/plugin marketplace add JohnnyVizz/claude-kit` and `/plugin install savvy-progress@claude-kit` myself instead.

5. Global instructions: if `~/.claude/CLAUDE.md` does not exist, copy `templates/CLAUDE.global.md` there. If it exists, show me the kit's sections and ask which ones to append. Never replace my file.

6. Verify and report, with the command output as evidence:
   - `bash -n` on each `.sh` file and `python3 -I -m py_compile ~/.claude/hooks/session-cost.py`
   - `jq empty ~/.claude/settings.json`
   - list `~/.claude/hooks` and `~/.claude/commands`
   - say what you could not verify (the cost hook needs the Claude desktop app; the plugin loads only after a restart)

At the end, list the files created or modified and the backups.
````

After the restart, open any project and type `oi`. The first reply should come with the project context, and the cost snapshot is taken silently on the first message of each session.
