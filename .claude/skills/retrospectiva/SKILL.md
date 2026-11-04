---
name: retrospectiva
description: Analisa um erro que se repetiu ou um problema que escapou da revisão e propõe a mudança que evita a repetição. Use quando o usuário disser que o mesmo erro aconteceu de novo, quando um bug passar pelo merge ou ao fim de um marco.
---

# Retrospectiva

1. **Fatos:** o que aconteceu, onde e quando. Sem culpa e sem suposição.
2. **Causa:** escolha uma.
   - A IA não tinha a informação (não estava no repositório nem nas regras).
   - A regra existia, mas foi ignorada.
   - Não havia nenhuma verificação que pegasse o problema.
   - A revisão não tinha esse item no checklist.
3. **Correção no nível certo.** Prefira sempre o mais automático:
   - dá para verificar por máquina → hook, regra de bloqueio no .claude/settings.json ou job no CI;
   - era informação que a IA não tinha → uma linha no AGENTS.md;
   - a revisão deixou passar → um item no checklist correspondente (docs/checklists/ ou a seção 10 do guia de design);
   - regra existente ignorada mais de uma vez → transforme em verificação automática em vez de reforçar o texto.
4. **Proposta:** mostre o arquivo e o texto exato da mudança. Não edite nada sem aprovação.
5. **Tamanho:** se a proposta deixar o AGENTS.md com mais de 120 linhas, sugira também o que remover ou mover para um arquivo separado.
6. **Lembrete final:** se a mudança vale para qualquer projeto, diga que ela deve ir também para o repositório modelo.
