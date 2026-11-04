#!/usr/bin/env python3
"""
Radar de Vagas
Coleta vagas de várias fontes, classifica pelo seu perfil e gera uma página HTML.

Uso:
    python vagas.py           -> busca de verdade e gera docs/index.html
    python vagas.py --demo    -> gera demo/index.html com vagas de exemplo (sem internet)
"""
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

# O que buscar. Cada termo vira uma busca em cada fonte (local + remoto).
TERMOS = [
    "estágio TI",
    "estágio desenvolvimento",
    "desenvolvedor júnior",
    "analista de dados júnior",
    "engenheiro de dados júnior",
    "suporte técnico TI",
]

# Busca presencial/híbrida perto de você. Vagas remotas do Brasil todo entram sempre.
BUSCA_LOCAL = "Santa Maria, RS"
RAIO_MILHAS = 40  # ~65 km

# Vaga presencial só passa se for numa dessas cidades (sem acento, minúsculo).
CIDADES_PERTO = [
    "santa maria", "restinga seca", "sao joao do polesine", "faxinal do soturno",
    "silveira martins", "itaara", "agudo", "formigueiro", "camobi",
]

# Fontes. Se alguma der problema, é só tirar da lista.
FONTES_JOBSPY = ["indeed", "linkedin", "glassdoor", "google"]
USAR_GUPY = True

RESULTADOS_POR_BUSCA = 25
DIAS_MAX = 14              # ignora vagas publicadas há mais tempo que isso
ANOS_EXPERIENCIA_MAX = 2   # se a vaga pedir mais que isso, cai pra "Talvez"

# Empresas que você quer ver primeiro (ganham estrela).
EMPRESAS_FAVORITAS = ["indicium", "rbs"]

# Palavras que definem o nível (procuradas no título).
NIVEL_BOM = [
    "estagio", "estagiario", "estagiaria", "junior", "jr", "trainee",
    "aprendiz", "assistente", "auxiliar", "iniciante", "nivel 1", "n1",
    "intern", "internship", "entry level",
]
NIVEL_RUIM = [
    "senior", "sr", "pleno", "pl", "especialista", "lead", "lider", "tech lead",
    "coordenador", "coordenadora", "gerente", "head", "principal", "staff",
    "arquiteto", "arquiteta", "manager", "diretor", "diretora", "mid-level", "mid level",
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
REMOTO = ["remoto", "remota", "remote", "home office", "homeoffice", "anywhere"]
GUPY_URLS = [
    "https://portal.api.gupy.io/api/v1/jobs",
    "https://employability-portal.gupy.io/api/v1/jobs",
]
NOMES_FONTES = {
    "indeed": "Indeed", "linkedin": "LinkedIn", "glassdoor": "Glassdoor",
    "google": "Google", "gupy": "Gupy",
}


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


def nova_vaga(titulo, empresa, local, link, fonte, data="", remoto=False, descricao=""):
    return {
        "titulo": titulo.strip(), "empresa": empresa.strip(), "local": local.strip(),
        "link": link.strip(), "fontes": [fonte], "data": data[:10], "remoto": bool(remoto),
        "descricao": descricao or "",
    }


# ---------- coleta ----------

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
                    kw.update(location="Brasil", is_remote=True)
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
                    print(f"  [{fonte}] erro em '{termo}' ({'remoto' if remoto else 'local'}): {str(e)[:120]}")
                    continue
                for _, r in df.iterrows():
                    rem = limpo(r.get("is_remote")).lower() == "true" or remoto
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
        print(f"{NOMES_FONTES[fonte]}: {status[fonte]} ({tentativas} buscas, {erros} erros)")
    return vagas


def coletar_gupy(status):
    import requests

    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 14) RadarDeVagas/1.0"
    vagas, base_ok, erros = [], None, 0

    for termo in TERMOS:
        for pagina in range(5):
            params = {"jobName": termo, "limit": 10, "offset": pagina * 10}
            dados = None
            for url in ([base_ok] if base_ok else GUPY_URLS):
                try:
                    r = s.get(url, params=params, timeout=20)
                    if r.ok and "data" in r.json():
                        dados, base_ok = r.json()["data"], url
                        break
                except Exception as e:
                    print(f"  [gupy] erro em '{termo}': {str(e)[:120]}")
            if dados is None:
                erros += 1
                break
            for j in dados:
                local = ", ".join(x for x in [j.get("city"), j.get("state")] if x)
                rem = j.get("workplaceType") == "remote" or bool(j.get("isRemoteWork"))
                vagas.append(nova_vaga(
                    j.get("name") or "", j.get("careerPageName") or "", local,
                    j.get("jobUrl") or "", "gupy", j.get("publishedDate") or "",
                    rem, j.get("description") or "",
                ))
            if len(dados) < 10:
                break
            time.sleep(1)

    status["gupy"] = f"{len(vagas)} encontradas" if vagas else ("fora do ar" if erros else "nada encontrado")
    print(f"Gupy: {status['gupy']}")
    return vagas


# ---------- tratamento ----------

def na_regiao(v):
    if v["remoto"]:
        return True
    local = norm(v["local"])
    if not local or tem(REMOTO, local):
        return True
    if any(c in local for c in CIDADES_PERTO):
        return True
    # presencial em outra cidade: só passa se a descrição deixar claro que é remoto
    return tem(["100% remoto", "trabalho remoto", "home office"], norm(v["descricao"][:3000]))


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
    unicas = {}
    for v in brutas:
        if not v["titulo"] or not v["link"]:
            continue
        if not recente(v) or not na_regiao(v):
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

    limite_nova = agora - timedelta(hours=24)
    saida = []
    for k, v in unicas.items():
        v["classe"], v["motivo"] = classificar(v)
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
        "fontes": [{"nome": NOMES_FONTES[f], "status": s} for f, s in status.items()],
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
        nova_vaga("Estágio", "Prefeitura Exemplo", "Santa Maria, RS", "https://example.com/8", "google", d(6), False, "Cursando Sistemas de Informação. Suporte técnico aos setores."),
        nova_vaga("Analista de Sistemas Pleno", "Software House", "Curitiba, PR", "https://example.com/9", "indeed", d(2), True, ""),
        nova_vaga("Vendedor Externo", "Atacado Sul", "Santa Maria, RS", "https://example.com/10", "indeed", d(1), False, ""),
        nova_vaga("Desenvolvedor Front-end", "Agência Web", "Porto Alegre, RS", "https://example.com/11", "linkedin", d(3), False, "Presencial."),
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
        status = {"indeed": "4 encontradas", "linkedin": "bloqueado nesta rodada",
                  "glassdoor": "1 encontrada", "google": "1 encontrada", "gupy": "2 encontradas"}
    else:
        brutas = []
        if FONTES_JOBSPY:
            brutas += coletar_jobspy(status)
        if USAR_GUPY:
            brutas += coletar_gupy(status)

    vagas = tratar(brutas, vistas, agora)
    gerar_pagina(vagas, status, agora, pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo_vistas.write_text(json.dumps(vistas, ensure_ascii=False, indent=0), encoding="utf-8")

    cont = {c: sum(v["classe"] == c for v in vagas) for c in ("encaixa", "talvez", "descartada")}
    print(f"\n{len(brutas)} coletadas -> {len(vagas)} únicas | "
          f"encaixa {cont['encaixa']}, talvez {cont['talvez']}, descartadas {cont['descartada']}")
    print(f"Página: {pasta / 'index.html'}")


if __name__ == "__main__":
    main()
