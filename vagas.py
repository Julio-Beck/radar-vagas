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
# Se o link for de outra plataforma, a página avisa em "Fontes".
# Dica: abra uma vaga da empresa no LinkedIn/Indeed e veja pra onde o botão "Candidatar" leva.
EMPRESAS = [
    ("CI&T", "https://jobs.lever.co/ciandt"),
    ("Zenvia", "https://job-boards.greenhouse.io/zenvia"),
    # ("Indicium", "COLE AQUI O LINK DE CARREIRAS"),
    # ("Grupo RBS", "COLE AQUI O LINK DE CARREIRAS"),
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

RESULTADOS_POR_BUSCA = 50
DIAS_MAX = 14              # ignora vagas publicadas há mais tempo que isso
ANOS_EXPERIENCIA_MAX = 2   # se a vaga pedir mais que isso, cai pra "Talvez"

# Empresas que você quer ver primeiro (ganham estrela), venham de onde vierem.
EMPRESAS_FAVORITAS = ["indicium", "rbs"]

# Palavras que definem o nível (procuradas no título).
NIVEL_BOM = [
    "estagio", "estagiario", "estagiaria", "junior", "jr", "trainee",
    "aprendiz", "assistente", "auxiliar", "iniciante", "nivel 1", "n1",
    "intern", "internship", "entry level", "entry-level",
]
NIVEL_RUIM = [
    "senior", "sr", "pleno", "pl", "especialista", "lead", "lider", "tech lead",
    "coordenador", "coordenadora", "gerente", "head", "principal", "staff",
    "arquiteto", "arquiteta", "manager", "diretor", "diretora", "director",
    "mid-level", "mid level", "mid",
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
    "engineer", "engenheiro de dados", "engenharia de dados", "it",
]

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
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/142.0 Safari/537.36")
REMOTO = ["remoto", "remota", "remote", "home office", "homeoffice", "anywhere"]
GUPY_URLS = [
    "https://portal.api.gupy.io/api/v1/jobs",
    "https://employability-portal.gupy.io/api/v1/jobs",
]
NOMES_FONTES = {
    "indeed": "Indeed", "linkedin": "LinkedIn", "glassdoor": "Glassdoor",
    "google": "Google", "gupy": "Gupy", "empresas": "Sites das empresas",
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
]
ESTRANGEIRO = [
    "usa", "us", "united states", "eua", "estados unidos", "canada", "mexico", "colombia",
    "argentina", "chile", "peru", "uruguay", "uruguai", "paraguay", "portugal", "spain",
    "espanha", "united kingdom", "uk", "england", "london", "ireland", "germany", "alemanha",
    "france", "india", "emea", "europe", "europa", "apac", "area",
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


def sessao():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
                      "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    return s


# ---------- sites de vagas (JobSpy) ----------

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
                    country_indeed="Brazil", verbose=0,
                )
                if remoto:
                    kw.update(location="Brazil", is_remote=True)
                else:
                    kw.update(location=BUSCA_LOCAL, distance=RAIO_MILHAS, hours_old=24 * DIAS_MAX)
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
                for _, r in df.iterrows():
                    flag = limpo(r.get("is_remote")).lower()
                    rem = flag == "true" or (flag == "" and remoto)
                    vagas.append(nova_vaga(
                        limpo(r.get("title")), limpo(r.get("company")),
                        limpo(r.get("location")),
                        limpo(r.get("job_url")) or limpo(r.get("job_url_direct")),
                        fonte, limpo(r.get("date_posted")), rem, limpo(r.get("description")),
                    ))
                    achadas += 1
                time.sleep(2)
        if achadas:
            status[fonte] = f"{achadas} encontradas"
        elif erros:
            status[fonte] = "bloqueado nesta rodada"
        else:
            status[fonte] = "nada encontrado"
        print(f"{NOMES_FONTES.get(fonte, fonte)}: {status[fonte]} ({tentativas} buscas, {erros} erros)")
    return vagas


# ---------- portal da Gupy ----------

def vaga_gupy(j, empresa_padrao=""):
    local = ", ".join(x for x in [j.get("city"), j.get("state")] if x)
    rem = j.get("workplaceType") == "remote" or bool(j.get("isRemoteWork"))
    return nova_vaga(
        j.get("name") or j.get("title") or "", j.get("careerPageName") or empresa_padrao,
        local, j.get("jobUrl") or "", "gupy", j.get("publishedDate") or "",
        rem, j.get("description") or "",
    )


def coletar_gupy(status):
    s = sessao()
    s.headers.update({"Origin": "https://portal.gupy.io", "Referer": "https://portal.gupy.io/"})
    vagas, base_ok, motivos = [], None, set()

    for termo in TERMOS:
        for pagina in range(5):
            params = {"jobName": termo, "limit": 10, "offset": pagina * 10}
            dados = None
            for url in ([base_ok] if base_ok else GUPY_URLS):
                try:
                    r = s.get(url, params=params, timeout=20)
                    if not r.ok:
                        motivos.add(f"HTTP {r.status_code}")
                        print(f"  [gupy] {url} -> HTTP {r.status_code}: {r.text[:120]!r}")
                        continue
                    corpo = r.json()
                    if isinstance(corpo, dict) and isinstance(corpo.get("data"), list):
                        dados, base_ok = corpo["data"], url
                        break
                    motivos.add("resposta inesperada")
                    print(f"  [gupy] {url} -> formato inesperado: {str(corpo)[:120]}")
                except Exception as e:
                    motivos.add(type(e).__name__)
                    print(f"  [gupy] {url} -> {type(e).__name__}: {str(e)[:120]}")
            if dados is None:
                break
            vagas += [vaga_gupy(j) for j in dados]
            if len(dados) < 10:
                break
            time.sleep(1)
        if base_ok is None and len(motivos) and termo == TERMOS[1]:
            break  # duas buscas seguidas falharam nos dois endereços: desiste

    if vagas:
        status["gupy"] = f"{len(vagas)} encontradas"
    else:
        status["gupy"] = "bloqueado (" + ", ".join(sorted(motivos)) + ")" if motivos else "nada encontrado"
    print(f"Gupy: {status['gupy']}")
    return vagas


# ---------- sites de carreira das empresas ----------

def achar_listas(obj, achadas):
    """Procura, dentro de um JSON qualquer, listas de dicionários com cara de vaga."""
    if isinstance(obj, list):
        if obj and all(isinstance(x, dict) for x in obj) and \
                sum(1 for x in obj if "id" in x and ("title" in x or "name" in x)) >= max(1, len(obj) // 2):
            achadas.append(obj)
        for x in obj:
            achar_listas(x, achadas)
    elif isinstance(obj, dict):
        for x in obj.values():
            achar_listas(x, achadas)


def procurar_chave(obj, chaves):
    """Primeiro valor de texto encontrado para alguma das chaves, em qualquer profundidade."""
    if isinstance(obj, dict):
        for k in chaves:
            if isinstance(obj.get(k), str) and obj[k]:
                return obj[k]
        for v in obj.values():
            achado = procurar_chave(v, chaves)
            if achado:
                return achado
    elif isinstance(obj, list):
        for v in obj:
            achado = procurar_chave(v, chaves)
            if achado:
                return achado
    return ""


def empresa_gupy(s, nome, sub):
    base = f"https://{sub}.gupy.io"
    html = s.get(base + "/", timeout=25).text
    vagas = []
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        listas = []
        achar_listas(json.loads(m.group(1)), listas)
        for j in max(listas, key=len, default=[]):
            titulo = j.get("title") or j.get("name") or ""
            cidade = procurar_chave(j, ["city", "addressCity"])
            estado = procurar_chave(j, ["state", "stateShortName", "addressState"])
            tipo = norm(json.dumps(j.get("workplaceType") or j.get("workplace") or "", ensure_ascii=False))
            rem = "remote" in tipo or bool(j.get("isRemoteWork"))
            data = procurar_chave(j, ["publishedDate", "publishedAt", "createdAt"])
            vagas.append(nova_vaga(titulo, nome, ", ".join(x for x in [cidade, estado] if x),
                                   f"{base}/jobs/{j['id']}", "empresas", data, rem))
    if not vagas:  # plano B: links /jobs/123 do HTML
        for href, texto in re.findall(r'<a[^>]+href="(/jobs/\d+[^"]*)"[^>]*>(.*?)</a>', html, re.S):
            texto = re.sub(r"<[^>]+>", " ", texto)
            texto = re.sub(r"\s+", " ", texto).strip()
            texto = re.sub(r"^Vaga para\s*", "", texto)
            vagas.append(nova_vaga(texto, nome, "", base + href.split("?")[0], "empresas",
                                   remoto="remot" in norm(texto)))
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


PLATAFORMAS = [
    (r"https?://([\w-]+)\.gupy\.io", empresa_gupy),
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

def no_brasil(local):
    """True se o local é no Brasil (ou não diz onde)."""
    l = norm(local)
    if not l or l.strip(" ,-") in ("remoto", "remote", "home office", "hibrido", "hybrid"):
        return True
    if "brasil" in l or "brazil" in l or "latam" in l or "latin america" in l or "america latina" in l:
        return True
    if tem(ESTRANGEIRO, l):
        return False
    if tem(ESTADOS, l) or tem(CIDADES_BR, l) or any(c in l for c in CIDADES_PERTO):
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
    if any(c in local for c in CIDADES_PERTO):
        return True
    # presencial em outra cidade: só passa se a descrição deixar claro que é remoto
    return tem(["100% remoto", "trabalho remoto", "home office", "fully remote"], norm(v["descricao"][:3000]))


def recente(v):
    if not v["data"]:
        return True
    try:
        return date.fromisoformat(v["data"]) >= date.today() - timedelta(days=DIAS_MAX)
    except ValueError:
        return True


def anos_pedidos(desc):
    padroes = [
        r"(\d{1,2})\s*\+?\s*anos? de experiencia",
        r"experiencia (?:minima |comprovada )?de (\d{1,2})\s*\+?\s*anos?",
        r"(\d{1,2})\s*\+?\s*years? of (?:professional )?experience",
    ]
    achados = [int(n) for p in padroes for n in re.findall(p, desc)]
    return min(achados) if achados else 0


def classificar(v):
    t = norm(v["titulo"]).replace("pl/sql", "plsql")
    d = norm(v["descricao"][:6000])

    if tem(NIVEL_RUIM, t):
        return "descartada", "Nível acima do seu (pleno/sênior ou liderança)"

    area_titulo = tem(AREA_TI, t)
    area_desc = not area_titulo and tem(AREA_TI_DESCRICAO, d)
    if not area_titulo and not area_desc:
        return "descartada", "Fora da área de TI"

    nivel = tem(NIVEL_BOM, t)
    anos = anos_pedidos(d)
    if anos > ANOS_EXPERIENCIA_MAX:
        return "talvez", f"Pede {anos} anos de experiência"
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

    # esquece vagas vistas há mais de 60 dias
    corte = agora - timedelta(days=60)
    for k in [k for k, t in vistas.items() if datetime.fromisoformat(t) < corte]:
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
        if EMPRESAS:
            brutas += coletar_empresas(status)

    vagas = tratar(brutas, vistas, agora)
    gerar_pagina(vagas, status, agora, pasta)
    arquivo_vistas.write_text(json.dumps(vistas, ensure_ascii=False, indent=0), encoding="utf-8")

    cont = {c: sum(v["classe"] == c for v in vagas) for c in ("encaixa", "talvez", "descartada")}
    print(f"\n{len(brutas)} coletadas -> {len(vagas)} únicas | "
          f"encaixa {cont['encaixa']}, talvez {cont['talvez']}, descartadas {cont['descartada']}")
    print(f"Página: {pasta / 'index.html'}")


if __name__ == "__main__":
    main()
