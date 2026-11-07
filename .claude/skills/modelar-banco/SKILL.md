---
name: modelar-banco
description: Modela o banco de dados (tabelas, campos, tipos, chaves, relações, índices e regras de migração) a partir do docs/PLAN.md. Use quando o projeto precisar de banco, quando um ticket pedir modelagem ou ao planejar uma mudança de schema.
---

# Modelar banco

## Antes de modelar

1. Leia o docs/PLAN.md (funcionalidades, restrições, stack) e o docs/banco.md, se existir.
2. Liste as entidades e as consultas principais que o app vai fazer (ex.: "listar as tarefas do usuário por status, ordenadas por data"). Os índices vêm dessas consultas, não de suposição.
3. Pergunte só o que muda o modelo: volume esperado, dados pessoais ou sensíveis, exclusão definitiva ou lógica, um ou vários usuários.

## Regras de modelagem

- Banco relacional por padrão (PostgreSQL; SQLite para protótipo local). Outro tipo só com um motivo concreto registrado em Decisões.
- Normalize até a 3ª forma normal. Desnormalize só com motivo concreto (uma consulta lenta medida, por exemplo), registrado em Decisões.
- Nomes em snake_case, tabelas no plural, chave primária `id`, chave estrangeira `<entidade>_id`, datas `created_at` e `updated_at`.
- Toda tabela tem chave primária. Toda relação tem chave estrangeira com a regra de ON DELETE explícita.
- Garanta no banco as regras que não podem falhar, com NOT NULL, UNIQUE e CHECK (e-mail único, status dentro de um conjunto fixo).
- Dinheiro em DECIMAL ou em centavos como INTEGER, nunca FLOAT. Datas com fuso horário (TIMESTAMPTZ no PostgreSQL).
- Índice em toda chave estrangeira e nos filtros e ordenações das consultas principais. Nenhum outro sem motivo.

## Segurança e LGPD

- Senha nunca é guardada, apenas o hash (bcrypt ou argon2), gerado pela aplicação.
- Marque os campos com dados pessoais ou sensíveis e diga como são protegidos e quando são apagados.
- A aplicação acessa o banco com um usuário de permissões mínimas, nunca com o superusuário.
- Consultas sempre parametrizadas ou via ORM. Nunca SQL montado concatenando texto.

## Migrações

- Toda mudança de schema é uma migration versionada no repositório, com a forma de desfazer.
- Mudanças destrutivas (apagar coluna ou tabela, mudar tipo, renomear) seguem o padrão expandir e contrair: adicionar o novo, migrar os dados, trocar o código, e só então remover o antigo.
- Não crie nem rode migrations sem aprovação do usuário. Nunca rode nada em produção por esta skill.

## Entrega

Escreva o docs/banco.md com:
1. Diagrama ER em Mermaid (`erDiagram`).
2. Cada tabela com seus campos, tipos, restrições e significado.
3. As consultas principais e o índice que atende cada uma.
4. Os dados pessoais e como são tratados.
5. Decisões: cada escolha não óbvia e o motivo.

Depois que o usuário aprovar, registre isso nas Notas do ticket correspondente no docs/PLAN.md e crie tickets para as migrations, se ainda não existirem.
