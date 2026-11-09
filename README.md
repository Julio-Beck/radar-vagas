# Radar de Vagas

Busca vagas no Indeed, LinkedIn, Glassdoor, Gupy, Vagas.com.br, Remotar, Trampos, em repositórios de vagas do GitHub e nos sites de carreira das empresas que eu escolher. Também junta concursos e estágios públicos do RS, SC e PR (e os nacionais). Classifica tudo por perfil (TI ou Direito) e publica uma página simples pra abrir no celular. Roda sozinho no GitHub Actions 4x por dia.

Na página:
- **Vagas / Concursos**: as duas abas do topo.
- **Perfil TI / Direito**: a chavinha ao lado troca o perfil das duas abas.
  - **TI**: estágio e júnior em desenvolvimento, dados, suporte...
  - **Direito**: formado em Direito, ainda sem OAB.

## Arquivos

| Arquivo | O que é |
|---|---|
| `vagas.py` | O coletor de vagas. A configuração (perfis, termos, cidades, empresas favoritas) fica no topo. |
| `concursos.py` | O coletor de concursos. A configuração (estados, cargos que servem pra cada perfil) fica no topo. |
| `template.html` | O visual da página. |
| `requirements.txt` | Bibliotecas Python. |
| `.github/workflows/vagas.yml` | O agendamento no GitHub Actions. |
| `docs/` | Criada automaticamente: a página publicada, o histórico de vagas já vistas e o texto dos editais já lidos (`concursos.json`). |

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

No perfil **Direito** (formado, sem OAB):

- **Encaixa:** vaga da área jurídica (assistente/analista jurídico, contratos, licitações, paralegal...) que não pede OAB.
- **Talvez:** a OAB aparece como diferencial ou sem dizer se é obrigatória, pede mais de 2 anos de experiência, ou é estágio de pós-graduação.
- **Fora:** advogado/procurador, vaga que pede OAB ativa, estágio de graduação, nível acima ou fora da área jurídica.

Nos **concursos**, o salário vem em destaque e a lista é ordenada por ele. Quando o edital não diz o salário de cada cargo, aparece o maior salário do edital ("até"). O selo segue o perfil:

- **TI:** encaixa quando o edital tem cargo de técnico ou nível superior em TI (técnico em informática, analista de sistemas, programador...) ou é estágio para estudante de TI. Professor e instrutor de informática ficam em "Talvez". Cargos só de nível fundamental/médio ficam em "Fora".
- **Direito:** encaixa com analista/técnico judiciário, oficial de justiça, escrevente, cargos jurídicos sem OAB. Ficam em "Talvez" o assessor jurídico (às vezes pede OAB), as carreiras policiais, os cargos de controle interno e de fiscal, e o estágio de pós-graduação. Advogado, procurador, juiz e promotor ficam em "Fora".
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
