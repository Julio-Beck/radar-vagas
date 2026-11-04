#!/usr/bin/env python3
"""
Radar de Vagas
Coleta vagas de sites de vagas e de sites de carreira de empresas,
classifica pelo seu perfil e gera uma página HTML.

Uso:
    python vagas.py           -> busca de verdade e gera docs/index.html
    python vagas.py --demo    -> gera demo/index.html com vagas de exemplo (sem internet)
"""
import html as htmllib
import json
import os
import re
import sys
import time
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# =====================================================================
# CONFIGURAÇÃO  (é só isso aqui que você precisa mexer no dia a dia)
# =====================================================================

# O que buscar nos sites de vagas. Cada termo vira uma busca local + uma remota.
TERMOS = [
    "estágio TI",
    "estágio desenvolvimento",
    "estágio dados",
    "trainee tecnologia",
    "desenvolvedor júnior",
    "programador júnior",
    "analista de dados júnior",
    "engenheiro de dados júnior",
    "analista de BI júnior",
    "analista de suporte júnior",
    "suporte técnico TI",
    "QA júnior",
]

# Sites de carreira de empresas: cole o link da página "Trabalhe conosco".
# O script reconhece sozinho estas plataformas:
#   Gupy         -> https://NOME.gupy.io
#   Greenhouse   -> https://job-boards.greenhouse.io/NOME  (ou boards.greenhouse.io/NOME)
#   Lever        -> https://jobs.lever.co/NOME
#   Ashby        -> https://jobs.ashbyhq.com/NOME
#   Workable     -> https://apply.workable.com/NOME
#   SmartRecruiters -> https://jobs.smartrecruiters.com/NOME
#   InHire       -> https://NOME.inhire.app/vagas
# Se o link for de outra plataforma, a página avisa em "Fontes".
# Dica: abra uma vaga da empresa no LinkedIn/Indeed e veja pra onde o botão "Candidatar" leva.
EMPRESAS = [
    ("CI&T", "https://jobs.lever.co/ciandt"),
    ("Zenvia", "https://zenvia.gupy.io"),
    ("Grupo RBS", "https://gruporbs.gupy.io"),
    ("Indicium", "https://indicium.inhire.app/vagas"),
]

# Busca presencial/híbrida perto de você. Vagas remotas do Brasil todo entram sempre.
BUSCA_LOCAL = "Santa Maria, RS"
RAIO_MILHAS = 40  # ~65 km

# Vaga presencial só passa se for numa dessas cidades (sem acento, minúsculo).
CIDADES_PERTO = [
    "santa maria", "restinga seca", "sao joao do polesine", "faxinal do soturno",
    "silveira martins", "itaara", "agudo", "formigueiro", "camobi",
]

# Sites de vagas. Se algum só der erro, é só tirar da lista.
FONTES_JOBSPY = ["indeed", "linkedin", "glassdoor"]
USAR_GUPY = True

# Repositórios do GitHub onde as vagas são publicadas como issues. Só entram as remotas.
REPOS_VAGAS = [
    "backend-br/vagas", "frontendbr/vagas", "react-brasil/vagas", "soujava/vagas-java",
    "phpdevbr/vagas", "androiddevbr/vagas", "qa-brasil/vagas", "datascience-br/vagas",
]

RESULTADOS_POR_BUSCA = 50
DIAS_MAX = 14              # ignora vagas publicadas há mais tempo que isso
ANOS_EXPERIENCIA_MAX = 2   # se a vaga pedir mais que isso, cai pra "Talvez"

# Empresas que você quer ver primeiro (ganham estrela), venham de onde vierem.
EMPRESAS_FAVORITAS = ["indicium", "rbs"]

# Palavras que definem o nível (procuradas no título).
ESTAGIO = [
    "estagio", "estagios", "estagiario", "estagiaria", "estagiarios", "estagiarias",
    "trainee", "aprendiz", "intern", "internship",
]
NIVEL_BOM = ESTAGIO + [
    "junior", "jr", "assistente", "auxiliar", "iniciante", "nivel 1", "nivel i", "n1",
    "analista i", "entry level", "entry-level",
]
NIVEL_RUIM = [
    "senior", "sr", "pleno", "pl", "especialista", "lead", "lider", "tech lead",
    "coordenador", "coordenadora", "gerente", "head", "principal", "staff",
    "arquiteto", "arquiteta", "architect", "manager", "diretor", "diretora", "director",
    "mid-level", "mid level", "mid", "n2", "n3", "nivel 2", "nivel 3", "ii", "iii", "iv",
    "specialist", "master", "expert",
]

# Palavras que dizem que a vaga é de TI (procuradas no título).
AREA_TI = [
    "ti", "tecnologia", "dados", "data", "desenvolvedor", "desenvolvedora",
    "desenvolvimento", "developer", "programador", "programadora", "programacao",
    "software", "sistemas", "suporte", "help desk", "helpdesk", "service desk",
    "infraestrutura", "redes", "python", "sql", "bi", "analytics", "etl",
    "devops", "cloud", "qa", "testes", "frontend", "front-end", "backend",
    "back-end", "full stack", "fullstack", "web", "mobile", "android",
    "banco de dados", "seguranca da informacao", "informatica", "computacao",
    "engenheiro de dados", "engenharia de dados", "it", "ia", "ai",
    "inteligencia artificial", "machine learning", "ml", "business intelligence",
    "ciberseguranca", "cybersecurity", "infosec", "observabilidade", "testador", "tester",
    "rpa", "java", "javascript", "typescript", ".net", "php", "golang", "kotlin", "react",
    "platform engineer", "site reliability",
]

# Expressões que usam palavras de TI, mas são de outra área. Saem do título
# antes de procurar AREA_TI (a descrição ainda pode mostrar que a vaga é de TI).
TITULO_NAO_TI = [
    "desenvolvimento de negocios", "desenvolvimento humano", "desenvolvimento organizacional",
    "desenvolvimento de pessoas", "desenvolvimento comercial", "desenvolvimento de mercado",
    "redes sociais", "suporte ao paciente", "suporte ao cliente", "suporte a vendas",
    "suporte de vendas", "suporte comercial", "suporte administrativo", "suporte operacional",
    "sistemas de irrigacao", "sistemas de gestao da qualidade",
]

# Cargos de outra área, mesmo que o título cite TI ("Sales Executive - Data & AI").
CARGO_NAO_TI = ["sales", "account executive", "vendas", "vendedor", "vendedora", "recruiter", "recrutador", "recrutadora"]

# Se o título não diz a área, estas na descrição indicam que é de TI.
AREA_TI_DESCRICAO = [
    "python", "sql", "programacao", "desenvolvimento de software",
    "suporte tecnico", "infraestrutura de ti", "redes de computadores",
    "ciencia da computacao", "sistemas de informacao", "engenharia de software",
    "analise de dados", "power bi", "javascript", "java", "linux",
]

# =====================================================================

BASE = Path(__file__).resolve().parent
FUSO = timezone(timedelta(hours=-3))
UA = "radar-vagas/1.0 (+https://github.com/Julio-Beck/radar-vagas)"
REMOTO = ["remoto", "remota", "remote", "home office", "homeoffice", "anywhere"]
NAO_REMOTO = ["hibrido", "hibrida", "hybrid", "presencial", "on-site", "onsite"]
# "home office" sozinho não basta na descrição: costuma ser benefício ("auxílio home office")
DESCRICAO_REMOTA = ["100% remoto", "100% home office", "trabalho remoto", "modelo remoto", "fully remote"]
# Endereços internos da Gupy, sem documentação oficial: podem mudar de novo.
GUPY_URL = "https://portal.gupy.io/api/job-search/jobs"
GUPY_EMPRESA_URL = "https://private-api.gupy.io/job-publication/public/jobs"
ANOS_PLAUSIVEIS = 10  # acima disso é a história da empresa, não um requisito
NOMES_FONTES = {
    "indeed": "Indeed", "linkedin": "LinkedIn", "glassdoor": "Glassdoor",
    "google": "Google", "gupy": "Gupy", "empresas": "Sites das empresas", "github": "GitHub",
}
UFS = ("ac al ap am ba ce df es go ma mt ms mg pa pb pr pe pi rj rn rs ro rr sc sp se to").split()
ESTADOS = [
    "acre", "alagoas", "amapa", "amazonas", "bahia", "ceara", "distrito federal",
    "espirito santo", "goias", "maranhao", "mato grosso", "minas gerais", "para",
    "paraiba", "parana", "pernambuco", "piaui", "rio de janeiro", "rio grande do norte",
    "rio grande do sul", "rondonia", "roraima", "santa catarina", "sao paulo",
    "sergipe", "tocantins",
]
CIDADES_BR = [
    "belo horizonte", "curitiba", "porto alegre", "florianopolis", "campinas", "recife",
    "salvador", "fortaleza", "brasilia", "goiania", "manaus", "belem", "vitoria", "joinville",
    "blumenau", "londrina", "maringa", "ribeirao preto", "sorocaba", "uberlandia", "santos",
    "osasco", "barueri", "sao jose dos campos", "caxias do sul", "pelotas", "natal",
    "joao pessoa", "maceio", "aracaju", "teresina", "sao luis", "cuiaba", "campo grande",
    "palmas", "niteroi", "jundiai", "sao carlos", "itajai", "chapeco", "passo fundo",
    "canoas", "novo hamburgo", "sao leopoldo", "gravatai",
]
ESTRANGEIRO = [
    "usa", "us", "united states", "eua", "estados unidos", "canada", "mexico", "colombia",
    "argentina", "chile", "peru", "uruguay", "uruguai", "paraguay", "portugal", "spain",
    "espanha", "united kingdom", "uk", "england", "london", "ireland", "germany", "alemanha",
    "france", "india", "emea", "europe", "europa", "apac", "bay area",
]


# ---------- utilidades ----------

def norm(texto):
    """minúsculo e sem acento, pra comparar palavras."""
    texto = unicodedata.normalize("NFKD", str(texto or "").lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def tem(palavras, texto):
    """True se alguma palavra aparece como palavra inteira no texto."""
    for p in palavras:
        if re.search(r"(?<![a-z0-9])" + re.escape(norm(p)) + r"(?![a-z0-9])", texto):
            return True
    return False


def limpo(valor):
    """Converte valores do pandas (NaN, None, datas) em texto simples."""
    if valor is None:
        return ""
    try:
        if valor != valor:  # NaN
            return ""
    except Exception:
        pass
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()[:10]
    return str(valor).strip()


def data_de_ms(ms):
    try:
        return datetime.fromtimestamp(int(ms) / 1000, FUSO).date().isoformat()
    except Exception:
        return ""


def nova_vaga(titulo, empresa, local, link, fonte, data="", remoto=False, descricao=""):
    return {
        "titulo": str(titulo or "").strip(), "empresa": str(empresa or "").strip(),
        "local": str(local or "").strip(), "link": str(link or "").strip(),
        "fontes": [fonte], "data": str(data or "")[:10], "remoto": bool(remoto),
        "descricao": str(descricao or ""),
    }


def descricao_remota(descricao):
    """True se a descrição confirma trabalho remoto e não cita modelo híbrido ou presencial."""
    d = norm(descricao[:3000])
    return tem(DESCRICAO_REMOTA, d) and not tem(NAO_REMOTO, d)


def sessao():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
                      "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    return s


# ---------- sites de vagas (JobSpy) ----------

def e_remota(flag, titulo, local, busca_remota):
    """O LinkedIn só marca remota se houver "remote" em inglês, então o título também conta."""
    t = norm(titulo)
    if tem(NAO_REMOTO, t):
        return False
    if flag == "true" or tem(REMOTO, t) or tem(REMOTO, norm(local)):
        return True
    return flag == "" and busca_remota


def coletar_jobspy(status):
    try:
        from jobspy import scrape_jobs
    except ImportError:
        for f in FONTES_JOBSPY:
            status[f] = "biblioteca não instalada"
        return []

    vagas = []
    for fonte in FONTES_JOBSPY:
        achadas, erros, tentativas = 0, 0, 0
        for termo in TERMOS:
            for remoto in (False, True):
                if erros >= 3 and achadas == 0:
                    break  # a fonte está bloqueando; não adianta insistir
                kw = dict(
                    site_name=[fonte], search_term=termo,
                    results_wanted=RESULTADOS_POR_BUSCA,
                    country_indeed="Brazil", verbose=0, hours_old=24 * DIAS_MAX,
                )
                if not remoto:
                    kw.update(location=BUSCA_LOCAL, distance=RAIO_MILHAS)
                elif fonte == "linkedin":
                    # o JobSpy ignora is_remote no LinkedIn: a busca precisa pedir pelo termo
                    kw.update(location="Brazil", search_term=f"{termo} remoto")
                else:
                    kw.update(location="Brazil", is_remote=True)
                if fonte == "google":
                    onde = "remoto" if remoto else BUSCA_LOCAL
                    kw["google_search_term"] = f"vagas {termo} {onde}"
                tentativas += 1
                try:
                    df = scrape_jobs(**kw)
                except Exception as e:
                    erros += 1
                    print(f"  [{fonte}] erro em '{termo}' ({'remoto' if remoto else 'local'}): {str(e)[:150]}")
                    continue
                # o JobSpy não levanta exceção quando a fonte falha: guarda o erro aqui
                erro = df.attrs.get("errors", {}).get(fonte)
                if erro:
                    erros += 1
                    print(f"  [{fonte}] falha em '{termo}' ({'remoto' if remoto else 'local'}): {str(erro)[:150]}")
                for _, r in df.iterrows():
                    titulo, local = limpo(r.get("title")), limpo(r.get("location"))
                    rem = e_remota(limpo(r.get("is_remote")).lower(), titulo, local, remoto)
                    vagas.append(nova_vaga(
                        titulo, limpo(r.get("company")), local,
                        limpo(r.get("job_url")) or limpo(r.get("job_url_direct")),
                        fonte, limpo(r.get("date_posted")), rem, limpo(r.get("description")),
                    ))
                    achadas += 1
                time.sleep(2)
        if achadas:
            status[fonte] = f"{achadas} encontradas"
            if erros:
                status[fonte] += f" · problema: {erros} de {tentativas} buscas falharam"
        elif erros:
            status[fonte] = "bloqueado nesta rodada"
        else:
            status[fonte] = "nada encontrado"
        print(f"{NOMES_FONTES.get(fonte, fonte)}: {status[fonte]} ({tentativas} buscas, {erros} erros)")
    return vagas


# ---------- portal da Gupy ----------

def vaga_gupy(j, empresa_padrao=""):
    local = ", ".join(x for x in [j.get("city"), j.get("state")] if x)
    return nova_vaga(
        j.get("name") or "", j.get("careerPageName") or empresa_padrao,
        local, j.get("jobUrl") or "", "gupy", j.get("publishedDate") or "",
        j.get("workplaceType") == "remote", j.get("description") or "",
    )


def coletar_gupy(status):
    s = sessao()
    vagas, falhas, motivos = [], 0, set()

    for termo in TERMOS:
        params = {"jobName": termo, "limit": RESULTADOS_POR_BUSCA, "offset": 0}
        try:
            r = s.get(GUPY_URL, params=params, timeout=30)
            r.raise_for_status()
            vagas += [vaga_gupy(j) for j in r.json()["data"]]
        except Exception as e:
            falhas += 1
            codigo = getattr(getattr(e, "response", None), "status_code", None)
            motivos.add(f"HTTP {codigo}" if codigo else type(e).__name__)
            print(f"  [gupy] '{termo}' -> {type(e).__name__}: {str(e)[:150]}")
            if falhas >= 2 and not vagas:
                break  # duas falhas sem nenhum resultado: desiste
        time.sleep(1)

    if vagas:
        status["gupy"] = f"{len(vagas)} encontradas"
        if falhas:
            status["gupy"] += f" · problema: {falhas} buscas falharam"
    else:
        status["gupy"] = "bloqueado (" + ", ".join(sorted(motivos)) + ")" if motivos else "nada encontrado"
    print(f"Gupy: {status['gupy']}")
    return vagas


# ---------- repositórios de vagas no GitHub ----------

def vaga_github(j):
    """Converte uma issue em vaga, ou None se não for remota. Ex.: "[Remoto] Dev Júnior na Acme"."""
    colchetes = re.findall(r"\[([^\]]*)\]", j.get("title") or "")
    titulo = re.sub(r"\[[^\]]*\]", " ", j.get("title") or "")
    titulo = re.sub(r"\s+", " ", titulo).strip(" -–—|")
    etiquetas = [x.get("name") or "" for x in j.get("labels") or []]
    corpo = j.get("body") or ""

    cabecalho = norm(" ".join(colchetes + etiquetas + [titulo]))
    if tem(NAO_REMOTO, cabecalho):
        return None
    if not tem(REMOTO, cabecalho) and not descricao_remota(corpo):
        return None

    # o nível costuma vir só na etiqueta ou no colchete, e a classificação olha o título
    e_nivel = lambda x: len(x) <= 20 and (tem(NIVEL_BOM, norm(x)) or tem(NIVEL_RUIM, norm(x)))
    # etiquetas podem trazer emoji ("👨 Pleno") e várias opções ("Júnior" e "Estágio" na mesma vaga)
    for nivel in dict.fromkeys(re.sub(r"[^\w\s/-]", "", x).strip() for x in etiquetas + colchetes if e_nivel(x)):
        if not tem([nivel], norm(titulo)):
            titulo += f" ({nivel})"

    # colchetes com lugar ("Remoto / Portugal") deixam no_brasil cortar vagas de fora
    local = " / ".join(x for x in colchetes if not e_nivel(x)) or "Remoto"
    # a última menção é a empresa: "Java Júnior (Pagamentos via Pix) | Confidencial (via Sylision)"
    empresas = re.findall(r"(?:@|\b(?:na|no|at|via)\b)\s+([A-Z0-9][^|@()–—]{1,40})", titulo)
    return nova_vaga(titulo, empresas[-1].strip(" -") if empresas else "", local, j.get("html_url"),
                     "github", j.get("created_at") or "", True, corpo)


def coletar_github(status):
    s = sessao()
    token = os.environ.get("GITHUB_TOKEN")
    if token:  # sem token, o GitHub limita a 60 consultas por hora
        s.headers["Authorization"] = f"Bearer {token}"
    vagas, falhas = [], []
    for repo in REPOS_VAGAS:
        try:
            r = s.get(f"https://api.github.com/repos/{repo}/issues", timeout=30,
                      params={"state": "open", "sort": "created", "direction": "desc", "per_page": 100})
            r.raise_for_status()
            achadas = [vaga_github(j) for j in r.json() if "pull_request" not in j]
            achadas = [v for v in achadas if v]
            vagas += achadas
            print(f"  [github] {repo}: {len(achadas)} remotas")
        except Exception as e:
            falhas.append(repo)
            print(f"  [github] {repo}: {type(e).__name__}: {str(e)[:150]}")

    texto = f"{len(vagas)} encontradas" if vagas else "nada encontrado"
    if falhas:
        texto += " · problema: " + ", ".join(falhas)
    status["github"] = texto
    print(f"GitHub: {texto}")
    return vagas


# ---------- sites de carreira das empresas ----------

def empresa_gupy(s, nome, sub):
    r = s.get(GUPY_EMPRESA_URL, params={"subdomain": sub}, timeout=25)
    r.raise_for_status()
    vagas = []
    for j in r.json()["data"]:
        local = ", ".join(x for x in [j.get("addressCity"), j.get("addressStateShortName")] if x)
        rem = j.get("workplaceType") == "remote" or bool(j.get("remoteWorking"))
        vagas.append(nova_vaga(j.get("name"), nome, local, f"https://{sub}.gupy.io/jobs/{j['id']}",
                               "empresas", remoto=rem))
    return vagas


def empresa_greenhouse(s, nome, token):
    r = s.get(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs", params={"content": "true"}, timeout=25)
    r.raise_for_status()
    vagas = []
    for j in r.json().get("jobs", []):
        local = (j.get("location") or {}).get("name", "")
        desc = re.sub(r"<[^>]+>", " ", htmllib.unescape(j.get("content") or ""))
        vagas.append(nova_vaga(j.get("title"), nome, local, j.get("absolute_url"), "empresas",
                               j.get("first_published") or j.get("updated_at") or "",
                               tem(REMOTO, norm(local)), desc))
    return vagas


def empresa_lever(s, nome, conta):
    r = s.get(f"https://api.lever.co/v0/postings/{conta}", params={"mode": "json"}, timeout=40)
    r.raise_for_status()
    vagas = []
    for j in r.json():
        cat = j.get("categories") or {}
        local = cat.get("location") or ", ".join(cat.get("allLocations") or [])
        vagas.append(nova_vaga(j.get("text"), nome, local, j.get("hostedUrl"), "empresas",
                               data_de_ms(j.get("createdAt")), j.get("workplaceType") == "remote",
                               j.get("descriptionPlain") or ""))
    return vagas


def empresa_ashby(s, nome, conta):
    r = s.get(f"https://api.ashbyhq.com/posting-api/job-board/{conta}", timeout=25)
    r.raise_for_status()
    return [nova_vaga(j.get("title"), nome, j.get("location") or "", j.get("jobUrl"), "empresas",
                      j.get("publishedAt") or "", bool(j.get("isRemote")), j.get("descriptionPlain") or "")
            for j in r.json().get("jobs", [])]


def empresa_workable(s, nome, conta):
    r = s.get(f"https://apply.workable.com/api/v1/widget/accounts/{conta}", timeout=25)
    r.raise_for_status()
    vagas = []
    for j in r.json().get("jobs", []):
        local = ", ".join(x for x in [j.get("city"), j.get("state"), j.get("country")] if x)
        vagas.append(nova_vaga(j.get("title"), nome, local, j.get("url") or j.get("shortlink"), "empresas",
                               j.get("published_on") or "", bool(j.get("telecommuting"))))
    return vagas


def empresa_smartrecruiters(s, nome, conta):
    r = s.get(f"https://api.smartrecruiters.com/v1/companies/{conta}/postings", params={"limit": 100}, timeout=25)
    r.raise_for_status()
    vagas = []
    for j in r.json().get("content", []):
        loc = j.get("location") or {}
        local = ", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country")] if x)
        vagas.append(nova_vaga(j.get("name"), nome, local,
                               f"https://jobs.smartrecruiters.com/{conta}/{j.get('id')}", "empresas",
                               j.get("releasedDate") or "", bool(loc.get("remote"))))
    return vagas


def empresa_inhire(s, nome, conta):
    r = s.get("https://api.inhire.app/job-posts/public/pages", headers={"X-Tenant": conta}, timeout=25)
    r.raise_for_status()
    vagas = []
    for j in r.json().get("jobsPage", []):
        if j.get("status") != "published":
            continue
        local = re.sub(r"\bBR$", "Brasil", j.get("location") or "")
        vagas.append(nova_vaga(j.get("displayName"), nome, local,
                               f"https://{conta}.inhire.app/vagas/{j.get('jobId')}", "empresas",
                               remoto=j.get("workplaceType") == "Remote"))
    return vagas


PLATAFORMAS = [
    (r"https?://([\w-]+)\.gupy\.io", empresa_gupy),
    (r"https?://([\w-]+)\.inhire\.app", empresa_inhire),
    (r"greenhouse\.io/(?:embed/job_board\?for=)?([\w-]+)", empresa_greenhouse),
    (r"jobs\.lever\.co/([\w.-]+)", empresa_lever),
    (r"jobs\.ashbyhq\.com/([\w.%-]+)", empresa_ashby),
    (r"apply\.workable\.com/([\w-]+)", empresa_workable),
    (r"(?:jobs|careers)\.smartrecruiters\.com/([\w-]+)", empresa_smartrecruiters),
]


def coletar_empresas(status):
    s = sessao()
    vagas, ok, problemas = [], 0, []
    for nome, url in EMPRESAS:
        for padrao, func in PLATAFORMAS:
            m = re.search(padrao, url)
            if m:
                try:
                    achadas = func(s, nome, m.group(1))
                    vagas += achadas
                    ok += 1
                    print(f"  [empresa] {nome}: {len(achadas)} vagas")
                except Exception as e:
                    problemas.append(f"{nome} (erro)")
                    print(f"  [empresa] {nome}: {type(e).__name__}: {str(e)[:150]}")
                break
        else:
            problemas.append(f"{nome} (plataforma não suportada)")
            print(f"  [empresa] {nome}: plataforma não suportada: {url}")
        time.sleep(1)

    texto = f"{len(vagas)} encontradas em {ok} empresas" if vagas else "nada encontrado"
    if problemas:
        texto += " · problema: " + ", ".join(problemas)
    status["empresas"] = texto
    print(f"Sites das empresas: {texto}")
    return vagas


# ---------- tratamento ----------

def perto(local):
    """True se o local é uma das CIDADES_PERTO, sem confundir com homônimas de outros lugares."""
    l = norm(local)
    if not tem(CIDADES_PERTO, l) or re.search(r"santa maria d[aeo]s? ", l):
        return False
    if tem(["rs", "rio grande do sul"], l):
        return True
    resto = l
    for parte in CIDADES_PERTO + ["brasil", "brazil", "greater", "area", "regiao", "de"]:
        resto = resto.replace(parte, " ")
    return not re.search(r"[a-z]", resto)  # sobrou outra sigla ou lugar: é outra cidade


def no_brasil(local):
    """True se o local é no Brasil (ou não diz onde)."""
    l = norm(local)
    if not l or l.strip(" ,-") in ("remoto", "remote", "home office", "hibrido", "hybrid"):
        return True
    if "brasil" in l or "brazil" in l or "latam" in l or "latin america" in l or "america latina" in l:
        return True
    if tem(ESTRANGEIRO, l):
        return False
    if tem(ESTADOS, l) or tem(CIDADES_BR, l) or perto(l):
        return True
    return bool(re.search(r"(?:^|[,\-/(]\s*)(" + "|".join(UFS) + r")\s*(?:$|[,)\-/])", l))


def na_regiao(v):
    if not no_brasil(v["local"]):
        return False
    if v["remoto"]:
        return True
    local = norm(v["local"])
    if not local or tem(REMOTO, local):
        return True
    if perto(local):
        return True
    # presencial em outra cidade: só passa se a descrição deixar claro que é remoto
    return descricao_remota(v["descricao"])


def recente(v):
    if not v["data"]:
        return True
    try:
        return date.fromisoformat(v["data"]) >= date.today() - timedelta(days=DIAS_MAX)
    except ValueError:
        return True


def anos_pedidos(desc):
    numero = r"(\d{1,2})(?:\s*(?:a|ou|to|-|–)\s*\d{1,2})?\s*\+?\s*"  # "3", "3+", "3 a 5"
    padroes = [
        numero + r"anos? de experiencia",
        r"experiencia (?:minima |comprovada )?de " + numero + r"anos?",
        numero + r"years? of (?:\w+ )?experience",
    ]
    empresa_antes = ("empresa", "somos", "temos", "possuimos", "nossa", "nosso", "consultoria",
                     "grupo", "companhia", "we have", "our ")
    empresa_depois = ("mercado", "atuamos", "atuando", "somos", "oferecemos", "historia", "in the market")
    achados = []
    for p in padroes:
        for m in re.finditer(p, desc):
            antes, depois = desc[max(0, m.start() - 40):m.start()], desc[m.end():m.end() + 30]
            if any(x in antes for x in empresa_antes) or any(x in depois for x in empresa_depois):
                continue  # fala da empresa ("há 30 anos de experiência no mercado")
            if int(m.group(1)) <= ANOS_PLAUSIVEIS:
                achados.append(int(m.group(1)))
    # cada número já é o início da sua faixa; requisitos diferentes são cumulativos
    return max(achados) if achados else 0


def classificar(v):
    t = re.sub(r"pl[\s/-]?sql", "plsql", norm(v["titulo"]))
    d = norm(v["descricao"][:6000])

    nivel = tem(NIVEL_BOM, t)
    # em estágio, "N3" ou "Principal" não indicam senioridade
    nivel_acima = tem(NIVEL_RUIM, t) and not tem(ESTAGIO, t)
    if nivel_acima and not nivel:
        return "descartada", "Nível acima do seu (pleno/sênior ou liderança)"

    if tem(CARGO_NAO_TI, t):
        return "descartada", "Fora da área de TI"

    titulo_area = t
    for expressao in TITULO_NAO_TI:
        titulo_area = titulo_area.replace(expressao, " ")
    area_titulo = tem(AREA_TI, titulo_area)
    area_desc = not area_titulo and tem(AREA_TI_DESCRICAO, d)
    if not area_titulo and not area_desc:
        return "descartada", "Fora da área de TI"

    anos = anos_pedidos(d)
    if anos > ANOS_EXPERIENCIA_MAX:
        return "talvez", f"Pede {anos} anos de experiência"
    if nivel_acima:
        return "talvez", "Aceita júnior, mas também cita nível acima"
    if nivel and area_titulo:
        return "encaixa", "Estágio/júnior na área de TI"
    if nivel:
        return "talvez", "Nível certo, mas a área só aparece na descrição"
    return "talvez", "Área de TI, nível não informado no título"


def chave(v):
    empresa = re.sub(r"\b(ltda|s\.?a\.?|me|eireli)\b", "", norm(v["empresa"]))
    return re.sub(r"[^a-z0-9]", "", norm(v["titulo"])) + "|" + re.sub(r"[^a-z0-9]", "", empresa)


def tratar(brutas, vistas, agora):
    unicas, cortes = {}, {"fora do Brasil/região": 0, "antigas": 0}
    for v in brutas:
        if not v["titulo"] or not v["link"]:
            continue
        if not recente(v):
            cortes["antigas"] += 1
            continue
        if not na_regiao(v):
            cortes["fora do Brasil/região"] += 1
            continue
        k = chave(v)
        if k in unicas:
            atual = unicas[k]
            for f in v["fontes"]:
                if f not in atual["fontes"]:
                    atual["fontes"].append(f)
            if not atual["data"] or (v["data"] and v["data"] > atual["data"]):
                atual["data"] = v["data"]
            if len(v["descricao"]) > len(atual["descricao"]):
                atual["descricao"] = v["descricao"]  # a classificação depende dos requisitos
            continue
        unicas[k] = v
    print(f"Cortadas: {cortes}")

    limite_nova = agora - timedelta(hours=24)
    saida = []
    for k, v in unicas.items():
        v["classe"], v["motivo"] = classificar(v)
        # das empresas vem tudo (até vaga de vendedor): só fica o que é de TI
        if v["fontes"] == ["empresas"] and v["classe"] == "descartada":
            continue
        v["favorita"] = any(f in norm(v["empresa"]) for f in EMPRESAS_FAVORITAS)
        primeira = vistas.setdefault(k, agora.isoformat())
        v["nova"] = datetime.fromisoformat(primeira) >= limite_nova
        v["fontes"] = [NOMES_FONTES.get(f, f) for f in v["fontes"]]
        del v["descricao"]  # não vai pra página
        saida.append(v)

    peso = {"encaixa": 2, "talvez": 1, "descartada": 0}
    saida.sort(key=lambda v: (peso[v["classe"]], v["favorita"], v["nova"], v["data"]), reverse=True)

    # esquece vagas vistas há mais de 60 dias que já saíram do ar. Sem isso, uma vaga
    # sem data (as de empresa na Gupy) voltaria a aparecer como "Nova" a cada 60 dias.
    corte = agora - timedelta(days=60)
    for k in [k for k, t in vistas.items() if datetime.fromisoformat(t) < corte and k not in unicas]:
        del vistas[k]
    return saida


# ---------- página ----------

def gerar_pagina(vagas, status, agora, pasta):
    modelo = (BASE / "template.html").read_text(encoding="utf-8")
    dados = {
        "atualizado": agora.isoformat(),
        "fontes": [{"nome": NOMES_FONTES.get(f, f), "status": s} for f, s in status.items()],
        "vagas": vagas,
    }
    js = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "index.html").write_text(modelo.replace('"__DADOS__"', js), encoding="utf-8")


def exemplo():
    """Vagas inventadas pra testar a página sem internet."""
    hoje = date.today()
    d = lambda n: (hoje - timedelta(days=n)).isoformat()
    return [
        nova_vaga("Estágio em Engenharia de Dados", "Indicium", "Remoto", "https://example.com/1", "gupy", d(0), True, "Cursando SI ou Computação. SQL e Python."),
        nova_vaga("Desenvolvedor Júnior Python", "Empresa Exemplo", "Santa Maria, RS", "https://example.com/2", "indeed", d(1), False, "Python, Django."),
        nova_vaga("Desenvolvedor Junior Python", "Empresa Exemplo Ltda", "Santa Maria, RS", "https://example.com/2b", "linkedin", d(1), False, ""),
        nova_vaga("Analista de Dados", "Grupo RBS", "Porto Alegre, RS", "https://example.com/3", "linkedin", d(3), True, "Power BI, SQL. Experiência de 1 ano."),
        nova_vaga("Suporte Técnico N1", "Provedor Sul", "Santa Maria, RS", "https://example.com/4", "indeed", d(2), False, "Atendimento, redes."),
        nova_vaga("Engenheiro de Dados", "Tech Remota", "São Paulo, SP", "https://example.com/5", "glassdoor", d(4), True, "Mínimo 3 anos de experiência com Spark."),
        nova_vaga("Estagiário Administrativo", "Loja Centro", "Santa Maria, RS", "https://example.com/6", "gupy", d(5), False, "Cursando Administração. Excel."),
        nova_vaga("Desenvolvedor Sênior Java", "Banco X", "Remoto", "https://example.com/7", "linkedin", d(1), True, "Java, Spring."),
        nova_vaga("Estágio", "Prefeitura Exemplo", "Santa Maria, RS", "https://example.com/8", "indeed", d(6), False, "Cursando Sistemas de Informação. Suporte técnico aos setores."),
        nova_vaga("Analista de Sistemas Pleno", "Software House", "Curitiba, PR", "https://example.com/9", "indeed", d(2), True, ""),
        nova_vaga("Vendedor Externo", "Atacado Sul", "Santa Maria, RS", "https://example.com/10", "indeed", d(1), False, ""),
        nova_vaga("Desenvolvedor Front-end", "Agência Web", "Porto Alegre, RS", "https://example.com/11", "linkedin", d(3), False, "Presencial."),
        nova_vaga("Software Engineering Intern", "US Corp", "Austin, TX, USA", "https://example.com/12", "linkedin", d(1), True, ""),
        nova_vaga("Junior Data Analyst", "HR Inc", "USA", "https://example.com/13", "linkedin", d(1), True, ""),
        nova_vaga("Estágio em Dados", "CI&T", "Brazil", "https://example.com/14", "empresas", d(2), True, ""),
        nova_vaga("Account Executive", "CI&T", "Brazil", "https://example.com/15", "empresas", d(2), True, ""),
        nova_vaga("Data Intern", "CI&T", "Colombia", "https://example.com/16", "empresas", d(2), True, ""),
    ]


def main():
    demo = "--demo" in sys.argv
    pasta = BASE / ("demo" if demo else "docs")
    arquivo_vistas = pasta / "vistas.json"
    agora = datetime.now(FUSO).replace(microsecond=0)

    try:
        vistas = json.loads(arquivo_vistas.read_text(encoding="utf-8"))
    except Exception:
        vistas = {}

    status = {}
    if demo:
        brutas = exemplo()
        status = {"indeed": "5 encontradas", "linkedin": "4 encontradas", "glassdoor": "nada encontrado",
                  "gupy": "bloqueado (HTTP 403)", "empresas": "3 encontradas em 1 empresas"}
    else:
        brutas = []
        if FONTES_JOBSPY:
            brutas += coletar_jobspy(status)
        if USAR_GUPY:
            brutas += coletar_gupy(status)
        if REPOS_VAGAS:
            brutas += coletar_github(status)
        if EMPRESAS:
            brutas += coletar_empresas(status)

    vagas = tratar(brutas, vistas, agora)
    if not vagas:
        # falha o workflow (o GitHub avisa por e-mail) e mantém a página anterior no ar
        sys.exit(f"Nenhuma vaga nesta rodada, página mantida. Fontes: {status}")
    gerar_pagina(vagas, status, agora, pasta)
    arquivo_vistas.write_text(json.dumps(vistas, ensure_ascii=False, indent=0), encoding="utf-8")

    cont = {c: sum(v["classe"] == c for v in vagas) for c in ("encaixa", "talvez", "descartada")}
    print(f"\n{len(brutas)} coletadas -> {len(vagas)} únicas | "
          f"encaixa {cont['encaixa']}, talvez {cont['talvez']}, descartadas {cont['descartada']}")
    print(f"Página: {pasta / 'index.html'}")


if __name__ == "__main__":
    main()
