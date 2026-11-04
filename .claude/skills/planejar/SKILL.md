---
name: planejar
description: Gera ou atualiza o plano de implementação em docs/PLAN.md, com arquitetura, Definition of Done, marcos e backlog de tickets pequenos. Use depois da /entrevista, ou quando o usuário pedir para planejar, quebrar em tarefas ou replanejar o projeto.
---

# Planejar

## Regras

- Escreva apenas o docs/PLAN.md. Não implemente código nem crie outros arquivos.
- Siga exatamente a estrutura de .claude/skills/planejar/modelo-PLAN.md.
- Se as seções 1 a 5 estiverem vazias ou vagas, pare e sugira rodar /entrevista primeiro.
- Não invente. O que faltar vira item em Suposições (se for razoável seguir sem resposta) ou em Perguntas em aberto (se a resposta mudar o plano).
- Se o plano já existe: preserve os tickets Done, as Notas e o Registro de problemas. Ajuste só os tickets não iniciados e explique o que mudou.

## Arquitetura

- Módulos e a responsabilidade de cada um, fluxo de dados, integrações externas e onde ficam os segredos (variáveis de ambiente).
- Se houver banco de dados, escreva só um resumo e crie um ticket para rodar /modelar-banco.
- Específica o bastante para guiar a implementação, sem pseudocódigo.

## Definition of Done

Critérios objetivos e verificáveis. Inclua sempre:
- build e testes passando, com os comandos exatos;
- lint e typecheck sem erros;
- gitleaks e Semgrep sem alertas no CI;
- fluxos principais testados de ponta a ponta (Playwright, quando houver interface);
- checklist da seção 10 do docs/design/design-sem-cara-de-ia.md aprovado pelo revisor-ux;
- checklist docs/checklists/seguranca.md aprovado pelo revisor-seguranca.

## Marcos

Agrupe os tickets em 2 a 5 marcos. Cada marco termina em algo que o usuário consegue usar e testar (ex.: "M1: cadastrar e listar tarefas, ainda sem login").

## Backlog

- Comece com 10 a 25 tickets, no formato do modelo.
- Cada ticket cabe em um PR e pode ser revisado sozinho.
- Prefira fatias verticais (uma funcionalidade funcionando de ponta a ponta) a camadas ("todo o backend" e depois "todo o frontend").
- O T001 é sempre o setup: stack instalada, comandos preenchidos no AGENTS.md, testes e lint rodando no CI e hook Stop criado.
- Tickets de interface dependem do ticket de design da tela (tokens e especificação, feitos pelo agente designer).
- Critério de aceite: testável e do ponto de vista do usuário, incluindo os estados de erro e vazio quando existirem.
- Passos de validação: comandos ou verificações concretas (ex.: "abrir /login, enviar o formulário vazio e ver a mensagem de erro junto ao campo").
- As Notas começam vazias.

## Conferência final

Antes de entregar, confira:
- todas as 11 seções existem, na ordem do modelo;
- cada ticket tem todos os campos, prioridade, marco e dependências coerentes;
- nenhum ticket depende de um ticket posterior a ele;
- a Definition of Done só tem critérios verificáveis.

Depois mostre um resumo (marcos e quantidade de tickets por prioridade) e liste as Perguntas em aberto que bloqueiam o primeiro marco.
