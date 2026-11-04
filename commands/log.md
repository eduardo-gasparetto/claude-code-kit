---
description: Registra a sessão atual em um arquivo próprio em docs/worklog/ do projeto
---

1. Definir o nome do arquivo: `docs/worklog/AAAA-MM-DD-HHMM-<tópico>.md`, com HHMM = hora local (24h) de criação do arquivo. Data = dia da sessão (hoje), não a da branch. Em repo git, usar o tópico da branch de sessão sem o prefixo `session/` e sem a data; fora de git, derivar um tópico curto da sessão. Criar a pasta `docs/worklog/` se não existir.
2. Se esta sessão já criou um arquivo de worklog (mesma data e tópico, qualquer HHMM), atualizá-lo em vez de criar outro. Nunca editar arquivos de outras sessões.
3. Escrever o arquivo, em EN e curto, com:
   - Título: `# AAAA-MM-DD — <tópico>`
   - O que foi feito (resumo)
   - Decisões tomadas + porquê
   - Arquivos/áreas tocadas
   - Estado final / próximo passo
   - Pendências ou bloqueios (se houver)
   - `## Cost`: chamar `mcp__ccd_session_mgmt__get_usage`, pegar `plan.extraUsage.spent` e rodar `~/.claude/hooks/session-cost.py report --cwd "<cwd da sessão>" --spent <spent>`. Colar as linhas da saída como estão. Ao atualizar um worklog já existente, substituir a seção Cost.
4. Se o projeto tiver um `docs/WORKLOG.md` legado, não mexer nele nem migrar sem pedido.
5. Confirmar ao usuário o que foi registrado e o caminho do arquivo, em 1-2 linhas.

Se `$ARGUMENTS` foi passado, usar como direção adicional sobre o que destacar.
