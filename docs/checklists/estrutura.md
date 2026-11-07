# Checklist de estrutura

Usado na revisão de todo PR. Cada item não atendido vira um apontamento, com arquivo:linha.

## Aderência ao docs/PLAN.md
- [ ] O PR implementa um único ticket, e o ticket está em Review.
- [ ] Os critérios de aceite e os passos de validação do ticket foram cumpridos, com evidência no PR.
- [ ] Os módulos e o fluxo de dados seguem o Esboço de arquitetura. Desvios têm aprovação registrada nas Notas.

## Organização
- [ ] Cada arquivo novo está no módulo responsável por aquilo, segundo o docs/PLAN.md.
- [ ] Nomes de arquivos, funções e pastas seguem o padrão já usado no projeto.

## Duplicação
- [ ] Nenhuma lógica copiada de outro ponto do código quando dava para reaproveitar a existente.
- [ ] Constantes e regras de negócio definidas em um só lugar.

## Acoplamento
- [ ] Módulos não acessam o interior de outros (banco, estado ou arquivos internos) fora da interface prevista.
- [ ] Nenhuma dependência circular nova.
- [ ] Interface não contém regra de negócio que deveria estar no servidor.

## Tratamento de erros
- [ ] Nenhum erro engolido (catch vazio, retorno padrão silencioso).
- [ ] Erros esperados (entrada inválida, recurso inexistente, falha de rede) têm tratamento e mensagem para o usuário.
- [ ] Falhas de integração externa têm timeout e não derrubam o app inteiro.

## Testes que testam algo de verdade
- [ ] Cada critério de aceite tem ao menos um teste, incluindo os casos de erro e vazio.
- [ ] Os testes falhariam se o comportamento quebrasse (não só checam que "não deu erro" nem testam o próprio mock).
- [ ] Nenhum teste, lint ou typecheck desativado, apagado ou afrouxado para passar.

## Escopo
- [ ] Nenhuma mudança fora do escopo do ticket (refatoração, formatação, "melhorias" em volta).
- [ ] Problemas vistos fora do escopo foram para o Registro de problemas, não para este PR.
- [ ] Nenhuma dependência nova sem aprovação.
