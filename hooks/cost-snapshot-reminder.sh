#!/bin/bash
# UserPromptSubmit: remind Claude to take the session cost snapshot until it exists.
# Desktop app only (get_usage tool is not available in the terminal CLI).
[ "$CLAUDE_CODE_ENTRYPOINT" = "claude-desktop" ] || exit 0
sid=$(python3 -c "import sys,json;print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)
[ -n "$sid" ] || exit 0
[ -f "$HOME/.claude/state/session-cost/$sid.json" ] && exit 0
cat <<EOF
Cost snapshot missing for session $sid. Before anything else this turn, silently: call mcp__ccd_session_mgmt__get_usage, then run ~/.claude/hooks/session-cost.py snapshot --session $sid --spent <plan.extraUsage.spent>. Do not mention it in chat.
EOF
