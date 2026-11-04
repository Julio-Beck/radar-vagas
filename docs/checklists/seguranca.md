# Checklist de segurança

Usado pelo agente revisor-seguranca em todo PR. Cada item não atendido vira um apontamento, com arquivo:linha e como explorar.

## Autenticação e autorização
- [ ] Toda rota ou endpoint novo exige autenticação, exceto os marcados como públicos no docs/PLAN.md.
- [ ] Toda rota verifica se o usuário pode acessar aquele recurso específico (não só se está logado). Trocar o id na URL ou no corpo não dá acesso a dados de outro usuário.
- [ ] Ações administrativas checam o papel no servidor, nunca só escondendo o botão na interface.
- [ ] Sessões e tokens expiram, são invalidados no logout e trafegam só em cookie `HttpOnly`/`Secure`/`SameSite` ou cabeçalho.
- [ ] Senhas guardadas apenas como hash (bcrypt ou argon2). Login com limite de tentativas.

## Validação de entrada
- [ ] Toda entrada externa (corpo, query, cabeçalho, arquivo, webhook) é validada no servidor quanto a tipo, tamanho e formato.
- [ ] Upload de arquivo limita tipo e tamanho e não usa o nome enviado pelo usuário como caminho.
- [ ] Nenhum caminho de arquivo, URL de redirecionamento ou URL de requisição externa vem direto do usuário sem lista de permitidos.

## SQL injection
- [ ] Consultas sempre parametrizadas ou via ORM. Nenhum SQL montado concatenando texto.
- [ ] Trechos de SQL bruto no ORM também usam parâmetros.

## XSS
- [ ] Conteúdo do usuário é escapado na saída. Nenhum `innerHTML`, `dangerouslySetInnerHTML`, `v-html` ou equivalente com dado do usuário sem sanitização.
- [ ] Nenhum dado do usuário em `eval`, `new Function`, atributos de evento ou `href="javascript:"`.

## CSRF
- [ ] Ações que mudam estado não usam GET.
- [ ] Com autenticação por cookie: token CSRF ou `SameSite=Lax/Strict`, e checagem de origem.
- [ ] CORS não usa `*` junto com credenciais.

## Segredos no código
- [ ] Nenhuma chave, senha, token ou string de conexão no código, testes, fixtures, docs ou histórico do branch.
- [ ] Toda variável de ambiente nova está no .env.example, sem valor.
- [ ] Nenhum segredo exposto ao frontend (variáveis públicas do bundler só com dados públicos).

## Dados sensíveis em logs
- [ ] Logs não registram senha, token, cookie, documento, cartão ou dado pessoal desnecessário.
- [ ] Erros devolvidos ao usuário não mostram stack trace, SQL ou caminhos internos.

## Dependências
- [ ] Toda dependência nova foi aprovada e existe no registro oficial (npm, PyPI) com o nome exato (sem typosquatting nem pacote inventado).
- [ ] O pacote é mantido e popular, e a versão está fixada no lockfile.
- [ ] O scanner de vulnerabilidades da stack (`npm audit`, `pip-audit` ou equivalente) não aponta falha alta ou crítica.

## Permissões do CI
- [ ] Workflows declaram `permissions` mínimas (padrão `contents: read`).
- [ ] Nenhum workflow usa `pull_request_target` com checkout do código do PR.
- [ ] Segredos do CI não são impressos nem passados para código de PRs externos.
- [ ] Actions de terceiros com versão fixa.
- [ ] Nenhuma mudança em .github/, .pre-commit-config.yaml ou .claude/settings.json sem aprovação explícita registrada.
