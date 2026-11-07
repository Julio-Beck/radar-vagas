---
name: deploy
description: Checklist para colocar o projeto em produção com segurança. Só roda quando o usuário digita /deploy.
disable-model-invocation: true
---

# Deploy

Pare e peça confirmação antes de qualquer passo irreversível. Nunca mostre o valor de segredos.

## 0. Processo definido

Se o AGENTS.md não tiver uma seção "Deploy" com a hospedagem, o comando de deploy e como desfazer, pare. Ajude o usuário a definir isso primeiro e proponha o texto da seção.

## 1. Antes

- Branch main atualizada e sem mudanças pendentes.
- CI verde no último commit da main.
- Todos os tickets do marco que vai para produção estão Done no docs/PLAN.md.
- Variáveis de ambiente: liste os nomes do .env.example e peça ao usuário que confirme que cada uma está configurada na hospedagem. Não leia nem mostre valores.
- Banco: se houver migrations novas, mostre quais são e peça aprovação. Confirme que existe backup recente antes de aplicar.
- Saiba como desfazer: o comando ou procedimento de rollback está escrito antes de começar.

## 2. Durante

- Rode apenas o comando de deploy documentado no AGENTS.md.
- Nunca use force push nem pule o CI.

## 3. Depois

- Teste os fluxos principais na URL de produção (os mesmos da Definition of Done).
- Verifique os logs da hospedagem procurando erros nos primeiros minutos.
- Se algo crítico falhar, proponha o rollback ao usuário imediatamente.
- Registre no docs/PLAN.md, no Registro de problemas: data, commit publicado, resultado e qualquer problema visto.
