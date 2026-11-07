# PLAN.md: Radar de Vagas

> Fonte única da verdade do projeto. Regras de uso:
> - Trabalhe um ticket por vez, respeitando prioridade e dependências.
> - Status: Todo → Doing (ao começar) → Review (ao abrir o PR) → Done (após o merge).
> - Ao concluir um ticket, registre em Notas as decisões tomadas, o porquê e como foi validado.
> - Problema encontrado fora do escopo do ticket vai para o Registro de problemas; não corrija no mesmo PR.
> - O Registro de problemas só recebe acréscimos. Nunca apague entradas.

## 1. Visão geral

Coletor de vagas de estágio e júnior em TI que roda sozinho e publica uma página para abrir no celular.

Sucesso significa: ao abrir a página, ver em Encaixa só vagas às quais o Julio se candidataria, com as fontes funcionando e as vagas novas aparecendo em até 1 dia.

## 2. Público e intenção

- Uso pessoal do Julio, no celular. Vagas presenciais só em Santa Maria (RS) e região; remotas, do Brasil todo.
- Tela principal: é sobre as vagas do momento / o primeiro toque é na vaga, que abre o anúncio original / feita para o próprio Julio.

Funcionalidades (já existem):

| Funcionalidade | Quando dá erro | Quando não há dados |
|---|---|---|
| Coleta de Indeed, LinkedIn, Glassdoor, Gupy, repositórios de vagas do GitHub e sites de empresas | "Fontes" mostra a falha de cada fonte, e as demais seguem | A fonte aparece como problema em "Fontes" |
| Classificação em Encaixa, Talvez e Fora | Não se aplica | A aba mostra uma mensagem de lista vazia |
| Página com busca e filtro de vagas novas | Busca há mais de 16 horas mostra "busca atrasada" | Se nenhuma vaga vier na rodada, o workflow falha e a página anterior fica no ar |

## 3. Não objetivos

- Acompanhar candidaturas (status, etapas ou notas).
- Contas e login.
- Uso por outras pessoas.
- Contornar bloqueios de sites com proxy.

## 4. Suposições

Nenhuma até aqui. O que ficou sem resposta está em Perguntas em aberto.

## 5. Restrições

- Orçamento: tudo gratuito, com GitHub Actions e GitHub Pages. O Pages gratuito exige repositório público.
- Publicação: o repositório é público, inclusive as regras de IA e o guia de design vindos do modelo privado (decisão do Julio em 2026-11-04).
- Proteção da main: exigir PR e checks, bloquear force push e abrir exceção para o robô que publica a página.
- Stack: Python 3.12 e JobSpy, já em uso.
- Identidade: a do `template.html` atual.
- Dados pessoais: nenhum além da cidade e do perfil de busca, que ficam no código público.
- Integrações: dependem de sites de terceiros. A busca da Gupy e a da InHire usam rotas sem documentação oficial e podem mudar.

## 6. Esboço de arquitetura

## 7. Definition of Done

### Build e testes
### Segurança
### Experiência do usuário
### Validação pelo usuário

## 8. Marcos

| Marco | Entrega utilizável | Tickets |
|---|---|---|

## 9. Backlog de tickets

> Backlog ainda não planejado (rodar /planejar). O T001 foi registrado aqui para guardar as Notas.

### T001: aplica o modelo-projeto
- **Prioridade:** P0
- **Status:** Review (PR #1)
- **Marco:** a definir no /planejar
- **Depende de:** nenhum
- **Escopo:** regras de agentes (AGENTS.md, .claude/), CI com gitleaks, Semgrep e testes, testes das regras atuais e este PLAN.md.
- **Critério de aceite:** o CI do PR passa (gitleaks, semgrep e testes) e os comandos do AGENTS.md funcionam.
- **Passos de validação:** `python -B -m unittest discover -s tests`; checks verdes no PR #1.
- **Notas:**
  - 2026-11-05: o Semgrep reprovava o CI com 6 alertas `github-actions-mutable-action-tag` (actions fixadas por tag em ci.yml e vagas.yml). Decisão: fixar por SHA de commit, mantendo as mesmas versões, com a tag num comentário. No vagas.yml, os SHAs de v5.1.0 e v6.3.0 são para onde `v5` e `v6` apontavam, então o robô não muda de versão. Mudança em .github/ aprovada pelo Julio em 2026-11-05.
  - Validação: SHAs conferidos com `git ls-remote --tags`; a regra do Semgrep (1.183.0) deu 6 alertas antes e 0 depois; testes OK. O `p/default` completo só roda no CI, porque o proxy do ambiente bloqueia semgrep.dev. revisor-seguranca: APROVADO, com 3 sugestões (ver Registro de problemas).
  - Lint e typecheck seguem pendentes (ver Perguntas em aberto).

## 10. Perguntas em aberto

- **Agendamento:** o cron nunca disparou (nenhuma execução agendada até 2026-11-04 15:24 UTC, com os horários de 09:17 e 13:17 UTC já passados). A causa é desconhecida. Bloqueia o objetivo de vagas novas em até 1 dia. Atualização 2026-11-05: o cron passou a disparar. Execuções agendadas #5 (2026-11-04 17:13 UTC) e #6 (22:38 UTC), as duas com sucesso, mas atrasadas em relação aos horários do cron (atraso normal do GitHub). Falta acompanhar se as quatro rodadas diárias acontecem.
- **Glassdoor:** dá 403 no GitHub Actions, mas funcionou fora dele. Tirar de `FONTES_JOBSPY`? O Julio pediu para deixar como está por enquanto. Enquanto ficar, "Fontes" mostra sempre um problema.
- **Filtro de híbrido no título:** barrar "híbrido" e "presencial" no título para a descrição não liberar a vaga? O Julio pediu para deixar como está por enquanto. Caso real: "Fullstack Jr (Híbrido - Manaus)" em Encaixa.
- **Linter e typecheck:** nenhum aprovado, porque seriam dependências novas. Bloqueia os jobs `lint` do CI e os comandos do AGENTS.md.
- **Vagas da Sylision:** 8 vagas "Java Júnior" parecidas, de cliente confidencial, publicadas pelo mesmo recrutador em `soujava/vagas-java`. Sem sinal de fraude; mantidas. Tratar de forma diferente?
- **Exceção na proteção da main:** falta testar se a exceção funciona com o token do workflow. Bloqueia a configuração da proteção.

## 11. Registro de problemas descobertos

> Somente acréscimos. Formato: AAAA-MM-DD, contexto, ticket relacionado.

- 2026-11-04, revisão do Codex, sem ticket ainda. Sintoma: vaga júnior que pede 5 anos caía em Encaixa quando a duplicata sem descrição vinha primeiro. Causa: a deduplicação não copiava a descrição. Correção: mantém a descrição mais longa.
- 2026-11-04, revisão do Codex, sem ticket ainda. Sintoma: "1 ano com SQL e 5 anos com Python" contava 1 ano. Causa: `anos_pedidos` usava o menor valor entre todos os requisitos. Correção: usa o maior, e o início de cada faixa continua valendo.
- 2026-11-04, revisão do Codex, sem ticket ainda. Sintoma: vaga híbrida fora da região passava por citar "trabalho remoto". Causa: a descrição não era checada quanto a híbrido ou presencial. Correção: `descricao_remota` exige a ausência desses termos.
- 2026-11-04, revisor-seguranca, sem ticket ainda. Página em branco: um título de issue em `REPOS_VAGAS` como `[Remoto] <!--<script> Dev Jr` impede o script da página de rodar, porque o `.replace("</", ...)` em `gerar_pagina` não neutraliza `<!--`. Qualquer pessoa pode abrir essa issue. Reproduzido em Chrome headless; sem execução de código. Correção proposta: `json.dumps(...).replace("<", "\u003c")`.
- 2026-11-04, revisor-seguranca, sem ticket ainda. O job de `vagas.yml` tem `contents: write`, passa o token ao `vagas.py` e instala dependências sem lockfile: uma release maliciosa poderia enviar para a main. Correção proposta: separar coleta (leitura) de publicação (escrita) e fixar versões.
- 2026-11-04, revisor-seguranca, sem ticket ainda. `esc(v.link)` em `template.html` não valida o esquema da URL, então um link `javascript:` passaria. Risco baixo. Correção proposta: aceitar só http e https em `nova_vaga`.
- 2026-11-04, revisor-seguranca, sem ticket ainda. `descricao_remota` descarta vaga fora da região que só nega o presencial ("100% remoto, sem necessidade de presencial"). Falta decidir se vale tratar a negação.
- 2026-11-05, T001. O `ci.yml` vindo do modelo-projeto fixa as actions por tag, e o Semgrep do próprio modelo reprova isso: todo projeto novo nasce com o CI vermelho. Corrigido aqui por SHA; a correção precisa ir também para o modelo-projeto.
- 2026-11-05, T001. O push do Claude deu 403 ("Claude doesn't have GitHub access"), tanto pelo git quanto pelo conector do GitHub. Resolvido pelo Julio liberando o acesso. Se voltar, conferir a conexão do GitHub e a permissão de workflows do app do Claude.
- 2026-11-05, revisor-seguranca, T001. Sugestão: sem `.github/dependabot.yml`, as actions fixadas por SHA não recebem correções. Proposta: Dependabot para `github-actions` (e `pip`), semanal, em ticket próprio (mexe em .github/).
- 2026-11-05, revisor-seguranca, T001. Sugestão: o vagas.yml, único job com `contents: write`, usa checkout v5 e setup-python v6, enquanto o CI usa v7. Avaliar a troca em ticket próprio, testando com `workflow_dispatch`.
