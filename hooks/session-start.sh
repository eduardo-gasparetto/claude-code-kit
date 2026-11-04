#!/bin/bash
# SessionStart hook — injeta estado do git + estrutura da pasta atual.
# Falha em silêncio fora de repo git (sem set -e; cada bloco trata o próprio erro).

CTX=""

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  BRANCH=$(git branch --show-current 2>/dev/null)
  STATUS=$(git status -s 2>/dev/null)
  LOG=$(git log --oneline -5 2>/dev/null)

  CTX+="## Estado do repositório git
Branch: ${BRANCH:-desconhecida}

Alterações pendentes:
${STATUS:-nenhuma}

Últimos 5 commits:
${LOG:-sem histórico}

"
fi

FILES=$(ls -1 2>/dev/null | head -30)
CTX+="## Conteúdo da pasta atual (1º nível)
${FILES:-vazio}"

# Worklog mais recente: arquivo por sessão em docs/worklog/ (nome começa com a data);
# fallback para a entrada do topo de um docs/WORKLOG.md legado.
LATEST_WORKLOG=$(ls -1 docs/worklog/*.md 2>/dev/null | sort | tail -1)
if [ -n "$LATEST_WORKLOG" ]; then
  CTX+="

## Último worklog (${LATEST_WORKLOG})
$(head -60 "$LATEST_WORKLOG")"
elif [ -f "docs/WORKLOG.md" ]; then
  WORKLOG_TOP=$(awk '/^## /{c++} c==2{exit} {print}' docs/WORKLOG.md 2>/dev/null)
  CTX+="

## Última entrada do WORKLOG (docs/WORKLOG.md)
${WORKLOG_TOP}"
fi

jq -n --arg ctx "$CTX" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
exit 0
