---
name: depurar
description: Investiga e corrige bugs com método, reproduzindo com um teste que falha, achando a causa raiz, corrigindo o mínimo e provando que resolveu. Use quando algo não funciona, quando aparecer um erro ou quando o usuário relatar um bug.
---

# Depurar

## Passos

1. **Entenda o sintoma.** O que acontece, o que deveria acontecer, como reproduzir. Se faltar informação para reproduzir, pergunte.
2. **Reproduza com um teste que falha.** Escreva o teste antes de mexer no código e mostre a falha. Se não for possível automatizar, escreva os passos manuais exatos e mostre o resultado errado.
3. **Ache a causa raiz.** Levante hipóteses e teste uma por vez, com logs, leitura do código ou testes menores. Explique a causa em uma ou duas frases antes de corrigir.
4. **Corrija o mínimo necessário.** Só o que resolve a causa. Nada de refatorar ou "melhorar" código em volta.
5. **Prove.** Mostre o teste que falhava passando e a suíte inteira passando.
6. **Registre.** Nas Notas do ticket (ou no Registro de problemas do docs/PLAN.md): sintoma, causa e correção, em três linhas.

## Proibido

- Corrigir no chute, sem reproduzir antes.
- Desativar, apagar ou afrouxar teste, lint ou typecheck para "passar".
- Engolir o erro (try/catch vazio, retorno padrão silencioso) em vez de resolver a causa.

## Se travar

Depois de duas hipóteses descartadas sem progresso, pare e informe: o que foi tentado, o que foi descartado e a próxima hipótese. Peça orientação antes de continuar.
