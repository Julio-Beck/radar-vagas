# Radar de Vagas

Busca vagas no Indeed, LinkedIn, Glassdoor, Gupy, Vagas.com.br, Remotar, Trampos, em repositórios de vagas do GitHub e nos sites de carreira das empresas que eu escolher. Também junta concursos e estágios públicos do RS, SC e PR (e os nacionais). Classifica tudo por perfil (TI ou Direito) e publica uma página simples pra abrir no celular. Roda sozinho no GitHub Actions 4x por dia.

Na página:
- **Vagas / Concursos**: as duas abas do topo.
- **Perfil TI / Direito**: a chavinha ao lado troca o perfil das duas abas.
  - **TI**: técnico em informática, cursando Sistemas de Informação. Vagas de estágio e júnior; concursos de técnico ou nível médio em TI e estágios de TI.
  - **Direito**: cursando Direito, formatura em janeiro de 2027, sem OAB. Estágios de Direito e vagas jurídicas que não pedem diploma nem OAB.

## Arquivos

| Arquivo | O que é |
|---|---|
| `vagas.py` | O coletor de vagas. A configuração (perfis, termos, cidades, empresas favoritas) fica no topo. |
| `concursos.py` | O coletor de concursos. Procura e lê o edital de cada concurso. A configuração (estados, cargos que servem pra cada perfil) fica no topo. |
| `municipios.json` | Lista de municípios de RS, SC, PR e SP (IBGE), pra achar a cidade de cada concurso. |
| `template.html` | O visual da página. |
| `requirements.txt` | Bibliotecas Python. |
| `.github/workflows/vagas.yml` | O agendamento no GitHub Actions. |
| `docs/` | Criada automaticamente: a página publicada, o histórico de vagas já vistas e o que já foi lido de cada concurso e edital (`concursos.json`). |

## Configurar pelo celular (uma vez só)

Dica: se algum menu não aparecer no navegador do celular, ative **"Site para computador"** no menu ⋮ do Chrome.

1. **Criar o repositório.** No github.com, toque em **+ → New repository**. Nome: `radar-vagas`. Deixe **Public** e **não** marque "Add a README". Toque em **Create repository**.
2. **Subir os arquivos.** Na página do repositório vazio, toque em **uploading an existing file**. Selecione `vagas.py`, `template.html`, `requirements.txt` e `README.md`. Toque em **Commit changes**.
3. **Criar o agendamento.** Toque em **Add file → Create new file**. No nome, digite exatamente `.github/workflows/vagas.yml` (as barras criam as pastas). Cole o conteúdo do `vagas.yml` e toque em **Commit changes**.
4. **Dar permissão de escrita.** **Settings → Actions → General**, role até **Workflow permissions**, marque **Read and write permissions** e salve.
5. **Rodar a primeira vez.** Aba **Actions → Buscar vagas → Run workflow → Run workflow**. Leva uns 5 a 15 minutos. Quando ficar com o ✓ verde, siga.
6. **Ligar a página.** **Settings → Pages**. Em *Source*, escolha **Deploy from a branch**, depois **main** e a pasta **/docs**. Salve. Em 1 ou 2 minutos aparece o link, no formato `https://SEU-USUARIO.github.io/radar-vagas/`.
7. **Atalho na tela inicial.** Abra o link no Chrome, toque em **⋮ → Adicionar à tela inicial**.

Pronto. Daqui pra frente a página se atualiza sozinha às 6h17, 10h17, 14h17 e 18h17. Pra forçar uma busca na hora, repita o passo 5.

## Ajustar a busca

Abra `vagas.py` no GitHub, toque no lápis e mexa só no bloco **CONFIGURAÇÃO** do topo:

- `TERMOS`: o que buscar nos sites de vagas pro perfil TI. `TERMOS_DIREITO`: o mesmo pro perfil Direito.
- `EMPRESAS`: sites de carreira de empresas. Cole o nome e o link da página "Trabalhe conosco". O script reconhece Gupy (`nome.gupy.io`), InHire (`nome.inhire.app`), Greenhouse, Lever, Ashby, Workable e SmartRecruiters. Se o link for de outra plataforma, a página avisa em "Fontes". Dica: abra uma vaga da empresa no LinkedIn e veja pra onde o botão "Candidatar" leva.
- `REPOS_VAGAS`: repositórios do GitHub com vagas em issues. Só entram as remotas.
- `BUSCA_LOCAL` e `CIDADES_PERTO`: onde vale vaga presencial. Remoto do Brasil todo entra sempre.
- `EMPRESAS_FAVORITAS`: ganham estrela e sobem na lista.
- `NIVEL_BOM`, `NIVEL_RUIM`, `AREA_TI`: as palavras que decidem "Encaixa", "Talvez" e "Fora".
- `AREA_DIREITO`, `CARGO_PEDE_OAB`: as palavras que decidem o perfil Direito.
- `FONTES_JOBSPY`: se uma fonte só der erro, tire da lista. As outras fontes ligam e desligam com `USAR_GUPY`, `USAR_VAGAS_COM_BR`, `USAR_REMOTAR`, `USAR_TRAMPOS` e `USAR_CONCURSOS` (`True` ou `False`).

Os concursos se ajustam no topo do `concursos.py`:

- `UFS`: estados da busca. RS, SC e PR cobrem até uns 1000 km de Porto Alegre e Santa Maria. Pra incluir São Paulo, acrescente `"SP"`.
- `INCLUIR_NACIONAIS`: concursos federais com vagas no país todo.
- `CARGOS_TI`, `CURSOS_TI`, `CARGOS_DIREITO` e as listas `_TALVEZ` / `_FORA`: os cargos procurados no edital.

## Como a classificação funciona

- **Encaixa:** o título tem nível de entrada (estágio, júnior, trainee...) **e** área de TI.
- **Talvez:** é de TI, mas o título não diz o nível, cita júnior junto com um nível acima ("Júnior/Pleno"), ou a vaga pede mais de 2 anos de experiência.
- **Fora:** nível acima (pleno, sênior, N2/N3, liderança) ou fora de TI. Expressões como "redes sociais" ou "desenvolvimento de negócios" não contam como TI (lista `TITULO_NAO_TI`).
- **Nova:** apareceu pela primeira vez nas últimas 24 horas.

No perfil **Direito** (cursando, formatura em jan/2027, sem OAB):

- **Encaixa:** estágio de Direito e vaga jurídica que não pede diploma nem OAB.
- **Talvez:** pede faculdade concluída, a OAB aparece como diferencial ou sem dizer se é obrigatória, ou pede mais de 2 anos de experiência.
- **Fora:** advogado/procurador, vaga que pede OAB, estágio de pós-graduação, nível acima ou fora da área jurídica.

### Concursos: como o edital é lido

Pra cada concurso, o radar procura o edital em vários lugares e fica com o primeiro que for mesmo daquele órgão:

1. As notícias do concurso no Concursos no Brasil, no Gran e no Estratégia (não só a da lista).
2. O site da banca citado nessas notícias.
3. O site da prefeitura ou da câmara (`cidade.rs.gov.br`).
4. O Diário Oficial da União, nos concursos federais.

Do edital sai, pra cada cargo que interessa, a escolaridade exigida e o salário. O cartão mostra:

- **O salário do cargo que serve pra você**, quando o edital (ou a notícia) diz. Quando não diz, aparece "salário do cargo não confirmado" e a faixa do edital em letra pequena. Os concursos com salário confirmado vêm primeiro.
- **A cidade:** a da prefeitura/câmara ou as cidades de lotação que aparecem no edital (Santa Maria e Porto Alegre vêm na frente).
- **Se o edital foi lido.** Algumas bancas (Objetiva e Fundatec, por exemplo) e o próprio PCI bloqueiam robôs; aí a classificação usa a notícia e o cartão avisa.

Como fica cada perfil:

- **TI:** encaixa quando o cargo é de técnico em informática ou de nível médio em TI, ou é estágio pra estudante de TI. Cargo de TI que pede faculdade concluída fica em "Talvez" (você ainda está cursando SI). Licenciatura (professor de informática) fica em "Fora".
- **Direito:** encaixa estágio de Direito e cargo jurídico de nível médio (técnico judiciário, escrevente, quando pedem só ensino médio). Analista judiciário, oficial de justiça e outros que pedem faculdade concluída ficam em "Talvez": você se forma em jan/2027 e o diploma é cobrado na posse. Advogado, procurador, juiz, promotor e estágio de pós ficam em "Fora".
- **"Concurso nº 001/2026"** é o número do edital (o primeiro daquele órgão em 2026), não a data. O que vale é o prazo de inscrição que aparece no cartão.
- Concursos com inscrição encerrada somem sozinhos.

## Problemas comuns

- **LinkedIn ou Glassdoor "bloqueado nesta rodada":** esses sites barram servidores de nuvem às vezes. É normal; nas outras rodadas costuma voltar.
- **Fonte com "nada encontrado":** a busca rodou sem erro e não trouxe nada. Se durar várias rodadas, a fonte provavelmente parou de funcionar.
- **Gupy com "bloqueado (HTTP 404)":** a Gupy não tem API de busca documentada e já trocou o endereço uma vez. Ele fica em `GUPY_URL`, no `vagas.py`.
- **Vagas remotas do LinkedIn:** só entram se o título ou o local disserem que são remotas, porque a busca não traz a descrição.
- **Página com "busca atrasada":** passaram mais de 16 horas sem atualizar. Veja a aba **Actions**. O GitHub pode atrasar ou pular agendamentos.
- **Workflow falhou com "Nenhuma vaga nesta rodada":** todas as fontes falharam, e a página anterior continua no ar.
- **Erro de permissão no passo "Publicar a página":** refaça o passo 4.
- **Concurso sem cidade:** órgãos estaduais e federais (tribunais, hospitais, polícia) mostram só o estado; a lotação está no edital.
- **Testar o visual sem buscar nada:** `python vagas.py --demo` gera `demo/index.html` com vagas e concursos de exemplo.
