# Checklist de novo projeto

Siga na ordem toda vez que criar um projeto a partir deste modelo.

## 1. Repositório

- [ ] Crie o projeto a partir do modelo: `gh repo create NOME --template Julio-Beck/modelo-projeto --private --clone`.
- [ ] Entre na pasta: `cd NOME`.
- [ ] Rode `pre-commit install` (precisa do `pre-commit` instalado: `pip install pre-commit`).

## 2. Proteções no GitHub

- [ ] Settings → Branches (ou Rules → Rulesets): proteja a branch `main`.
  - [ ] Exigir pull request antes do merge.
  - [ ] Exigir os checks do CI passando (`gitleaks`, `semgrep` e, depois do T001, `lint` e `testes`).
  - [ ] Bloquear force push e exclusão da branch.
- [ ] Settings → Code security: ative Secret scanning e Push protection.
- [ ] Conecte o repositório novo nas configurações do Codex (code review).

## 3. Escopo e plano

- [ ] Rode /entrevista. Ela cria o docs/PLAN.md a partir de .claude/skills/planejar/modelo-PLAN.md.
- [ ] Rode /planejar para completar arquitetura, Definition of Done, marcos e backlog.
- [ ] Preencha a linha "Projeto" no topo do AGENTS.md.

## 4. T001 (setup)

Em um branch próprio, com PR, como qualquer ticket:
- [ ] Preencha a seção Comandos do AGENTS.md (instalar, rodar o app, todos os testes, um teste, lint, typecheck).
- [ ] Ative os jobs `lint` e `testes` em .github/workflows/ci.yml e fixe as versões das actions.
- [ ] Crie em .claude/settings.json um hook `Stop` que roda os testes e o typecheck. Exemplo (troque os comandos):

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        { "type": "command", "command": "TODO comando de testes && TODO comando de typecheck" }
      ]
    }
  ]
}
```

- [ ] Inclua no .env.example o nome de cada variável de ambiente que a stack exigir.

## 5. Antes do primeiro deploy

- [ ] Preencha a seção Deploy do AGENTS.md: hospedagem, comando de deploy e como desfazer.
- [ ] Só então rode /deploy.

## 6. Limpeza

- [ ] Apague as linhas TODO já resolvidas (AGENTS.md, ci.yml, .claude/settings.json).
- [ ] Confira que não sobrou nenhum: `git grep -n TODO -- AGENTS.md .github .claude/settings.json`.
