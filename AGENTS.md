# AGENTS.md

Regras deste repositório para qualquer agente (Claude, Codex). O CLAUDE.md só importa este arquivo.

Projeto: Radar de Vagas. Coleta vagas de estágio e júnior em TI, classifica pelo perfil do Julio e publica uma página no GitHub Pages.
Plano, arquitetura e backlog: docs/PLAN.md.

## Comandos

- Instalar: `pip install -r requirements.txt`
- Rodar o app: `python vagas.py` (busca de verdade e grava em docs/) ou `python vagas.py --demo` (sem internet, grava em demo/)
- Rodar todos os testes: `python -B -m unittest discover -s tests`
- Rodar um teste: `python -B -m unittest tests.test_vagas.Regiao`
- Lint: TODO: nenhum linter aprovado ainda (dependência nova precisa de aprovação)
- Typecheck: TODO: nenhum typechecker aprovado ainda (dependência nova precisa de aprovação)

## Particularidades deste projeto

- docs/ é também a pasta publicada pelo GitHub Pages. `docs/index.html` e `docs/vistas.json` são gerados: não edite à mão. O visual fica em `template.html`.
- Documentação nova em docs/ precisa entrar no `exclude` de `docs/_config.yml`, ou vai para o site.
- O repositório é público: tudo o que for commitado fica visível.
- O workflow `.github/workflows/vagas.yml` commita em docs/ direto na main (exceção à regra de nunca commitar na main, só para esse robô). Qualquer proteção da main precisa permitir esse push.

## Fluxo

1. Projeto ou funcionalidade nova: rode /entrevista e depois /planejar.
2. Antes de qualquer interface, acione o agente designer.
3. Trabalhe um ticket do docs/PLAN.md por vez: um branch e um PR por ticket.
4. Nunca commite na main.
5. Siga as regras de uso do topo do docs/PLAN.md (status, Notas, Registro de problemas).
6. Para bugs, use /depurar.
7. Rode /salvar-progresso antes de /clear e ao encerrar a sessão.
8. Antes de abrir o PR, acione os agentes revisor-seguranca e revisor-ux (este quando houver interface).

## Git

- Adicione arquivos pelo nome. Nunca use `git add .` nem `git add -A`.
- Mostre o `git status` antes de todo commit.

## Dependências

- Nunca adicione dependência nova sem minha aprovação.
- Antes de propor um pacote, confirme no registro oficial (npm, PyPI) que ele existe, é mantido e é popular. Mostre o link.
- Fixe sempre a versão via lockfile e versione o lockfile.

## Segredos

- Nunca escreva chave, senha ou token no código, em testes ou em exemplos.
- Use variáveis de ambiente e registre o nome (sem valor) no .env.example.

## Design

- Todo trabalho de interface segue docs/design/design-sem-cara-de-ia.md.
- Use somente os tokens de docs/design/tokens.md e a especificação da tela em docs/design/.

## Definição de pronto

Um ticket só está pronto quando:
- os critérios de aceite e os passos de validação do ticket foram cumpridos;
- testes e lint passam;
- o app foi rodado e os fluxos principais foram testados;
- o `git status` foi conferido.

Ao dizer que terminou, mostre a evidência: os comandos rodados e a saída.

## Code Review Rules

- Revise seguindo docs/checklists/estrutura.md.
- Compare o PR com o critério de aceite do ticket no docs/PLAN.md.
- Reporte só problemas de funcionamento, estrutura ou escopo. Ignore estilo.

## Pergunte antes de

- Apagar arquivos.
- Mudar a arquitetura definida no docs/PLAN.md.
- Mexer em configuração de CI ou de segurança (.github/, .pre-commit-config.yaml, .claude/settings.json, docs/checklists/).

## Deploy

- Hospedagem: GitHub Pages, branch `main`, pasta `/docs`.
- Publicar: depois do merge na main, `gh workflow run "Buscar vagas"` regenera a página. O workflow também roda sozinho nos horários do cron.
- Desfazer: `git revert` do commit do PR, via novo PR, e rodar o workflow de novo.

O deploy só acontece via /deploy, quando eu pedir.
