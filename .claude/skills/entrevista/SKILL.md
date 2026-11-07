---
name: entrevista
description: Entrevista o usuário para transformar uma ideia vaga em escopo definido e preencher o início do docs/PLAN.md. Use no começo de um projeto ou funcionalidade nova, ou quando o usuário pedir "me entreviste", "vamos definir o escopo" ou "grill me".
---

# Entrevista de escopo

Objetivo: chegar a um entendimento compartilhado da ideia, resolvendo uma decisão por vez, até ser possível escrever o início do docs/PLAN.md sem inventar nada.

## Como perguntar

- Use a ferramenta AskUserQuestion para toda pergunta. Nunca pergunte em texto solto.
- Uma pergunta por vez. Espere a resposta antes da próxima.
- Dê 2 a 4 opções concretas e prováveis para este projeto. Evite "Sim/Não", a menos que a pergunta seja realmente binária. O usuário sempre pode escrever outra resposta.
- Se tiver uma recomendação, coloque-a como primeira opção com "(Recomendado)" e explique o motivo na descrição da opção.
- Se a resposta estiver nos arquivos do projeto, procure você mesmo em vez de perguntar.
- Depois de cada resposta, confirme a decisão em uma frase e siga para a próxima.

## Ordem das decisões

As decisões de baixo dependem das de cima. Pule o que já estiver respondido.

1. **Problema e objetivo:** que problema resolve e como saberemos que deu certo, em uma frase observável.
2. **Público:** quem usa, em que contexto, com que nível técnico e em qual dispositivo principal.
3. **Tela principal:** sobre o que é, onde o usuário clica primeiro e para qual público (as 3 perguntas do docs/design/design-sem-cara-de-ia.md).
4. **Funcionalidades do MVP:** o mínimo que entrega o objetivo. Para cada uma, o que acontece quando dá erro e quando não há dados.
5. **Não objetivos:** o que fica explicitamente de fora.
6. **Restrições:** prazo, orçamento, hospedagem, integrações e dados pessoais ou sensíveis (LGPD).
7. **Stack:** se o usuário não tiver preferência, proponha uma com justificativa curta e peça confirmação.
8. **Identidade:** já existe marca, cores, site ou referências visuais?

## Postura

- Desafie pontos fracos: contradições, escopo grande demais para um MVP, funcionalidade sem caso de erro. Aponte e pergunte; não decida pelo usuário.
- Não proponha arquitetura nem código durante a entrevista, exceto a stack no item 7.
- Pare quando todos os itens estiverem resolvidos ou o usuário disser que basta. O que ficar sem resposta vai para "Perguntas em aberto"; nunca vira suposição silenciosa.

## Ao terminar

1. Mostre um resumo das decisões em tópicos curtos e pergunte se está correto.
2. Com a confirmação, crie ou atualize o docs/PLAN.md seguindo a estrutura de .claude/skills/planejar/modelo-PLAN.md. Preencha apenas as seções 1 a 5 e a 10 (Perguntas em aberto). Não escreva arquitetura nem backlog.
3. Diga que o próximo passo é rodar /planejar.
