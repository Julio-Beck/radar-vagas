#!/usr/bin/env python3
"""
Concursos e estágios públicos da região, pra aba "Concursos" do Radar de Vagas.
Quem chama é o vagas.py; este arquivo não precisa rodar sozinho.

De onde vem:
  - PCI Concursos (pciconcursos.com.br): concursos abertos, por região.
  - Concursos no Brasil (concursosnobrasil.com): traz também os estágios públicos.
Cada edital é aberto uma vez só; o texto fica guardado em docs/concursos.json.
"""
import html as htmllib
import json
import re
import time
import unicodedata
from datetime import date, datetime, timedelta

from vagas import norm, sessao, tem

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================

# Estados da busca. RS, SC e PR cobrem até uns 1000 km de Porto Alegre e Santa Maria.
# Pra incluir São Paulo, é só acrescentar "SP".
UFS = ["RS", "SC", "PR"]
INCLUIR_NACIONAIS = True  # concursos federais com vagas no país todo

# Quantos editais novos procurar por rodada e por quanto tempo (os já lidos ficam guardados;
# o que não der tempo fica pra próxima rodada).
EDITAIS_POR_RODADA = 200
MINUTOS_PROCURANDO_EDITAIS = 20
VERSAO_EDITAL = 1  # aumente pra reler todos os editais depois de mudar as listas abaixo

# As listas abaixo são procuradas no edital (minúsculo, sem acento) e aceitam
# expressões regulares: [oa] = "o" ou "a", (de|em) = "de" ou "em", ? = opcional.

# --- Perfil TI: cargos de técnico ou de nível superior em TI ---
CARGOS_TI = [
    r"tecnic[oa]s? (em|de) (informatica|tecnologia da informacao|ti|processamento de dados"
    r"|redes de computadores|redes|manutencao de computadores|desenvolvimento de sistemas)\b",
    r"tecnolog[oa] em (analise e desenvolvimento de sistemas|redes de computadores|informatica"
    r"|sistemas para internet|tecnologia da informacao|gestao da tecnologia da informacao)",
    r"(assistente|agente|auxiliar tecnico) (em|de) (informatica|tecnologia da informacao|ti)\b",
    r"analista (de |em )?(sistemas?|tecnologia da informacao|ti|informatica|suporte|redes|dados"
    r"|banco de dados|seguranca da informacao)\b",
    r"analista (programador|desenvolvedor)",
    r"\bprogramador(a)?\b",
    r"\bdesenvolvedor(a)?\b",
    r"engenheir[oa] (de software|da computacao|de computacao)",
    r"cientista de dados",
    r"administrador(a)? de (banco de dados|redes|sistemas)",
    r"(especialidade|area|especialista em)[: -]+(tecnologia da informacao|informatica|analise de sistemas"
    r"|desenvolvimento de sistemas|suporte tecnico|infraestrutura de ti|ciencia de dados)",
    r"suporte (tecnico )?(em|de) (ti|informatica)",
]
# Cargos de informática que talvez sirvam, e por quê.
CARGOS_TI_TALVEZ = [
    (r"professor(a)?( de| -| –| em)? (informatica|computacao|tecnologia)", "Professor: costuma pedir licenciatura"),
    (r"instrutor(a)? de informatica", "Instrutor de informática: confira a escolaridade"),
    (r"(monitor|auxiliar|operador)(a)? de (informatica|computador)|\bdigitador", "Cargo de nível médio em informática"),
]
# Cursos que um estágio precisa citar pra servir pro perfil TI.
CURSOS_TI = [
    r"tecnologia da informacao", r"ciencias? da computacao", r"sistemas de informacao",
    r"analise e desenvolvimento de sistemas", r"engenharia (de software|da computacao|de computacao)",
    r"\binformatica\b", r"redes de computadores", r"sistemas para internet", r"ciencia de dados",
    r"seguranca da informacao", r"jogos digitais", r"\bcomputacao\b",
]

# --- Perfil Direito: formado, sem OAB ---
CARGOS_DIREITO = [
    r"analista judiciari[oa]", r"tecnic[oa] judiciari[oa]", r"oficial de justica",
    r"oficial (de )?escrevente", r"\bescrevente", r"analista (juridic[oa]|processual)",
    r"(assistente|auxiliar|agente|tecnic[oa]) juridic[oa]",
    r"(analista|tecnic[oa]|oficial) (do|de) (ministerio publico|mp)\b",
    r"\bconciliador(a)?\b", r"mediador(a)? judicial", r"residen(cia|te)s? juridic[oa]",
    r"analista de controle externo[^\n]{0,40}direito",
]
CARGOS_DIREITO_TALVEZ = [
    (r"assessor(a)? juridic[oa]", "Assessor jurídico: às vezes pede OAB"),
    (r"delegad[oa] de policia", "Delegado: alguns estados pedem anos de prática jurídica"),
    (r"\bescrivao|inspetor(a)? de policia|agente de policia|policial civil|investigador(a)? de policia"
     r"|policial penal|agente penitenciari", "Carreira policial: nível superior e teste físico"),
    (r"analista legislativo|tecnic[oa] legislativo|consultor(a)? legislativ", "Cargo legislativo: confira se a área é Direito"),
    (r"controlador(a)? intern[oa]|auditor(a)? de controle|analista de controle", "Controle interno: costuma aceitar Direito"),
    (r"agente fiscal|fiscal de tributos|auditor(a)? fiscal", "Fiscal: costuma aceitar qualquer curso superior"),
]
CARGOS_DIREITO_FORA = [
    (r"\badvogad[oa]s?\b", "Advogado: pede OAB"),
    (r"\bprocurador(a|es)?\b", "Procurador: pede OAB"),
    (r"juiz(a)? leigo", "Juiz leigo: pede 2 anos de advocacia"),
    (r"\bjuiz(a|es)?\b|magistratura|promotor(a)? de justica|defensor(a)? public", "Pede 3 anos de atividade jurídica"),
]

# Expressões que dizem que o edital aceita qualquer formação.
QUALQUER_CURSO = [r"diversos cursos", r"diversas areas", r"todos os cursos", r"qualquer curso", r"todas as areas"]
QUALQUER_SUPERIOR = [r"(nivel|ensino|curso) superior (completo )?(em )?qualquer (area|curso|formacao)",
                     r"graduacao em qualquer (area|curso)", r"qualquer (curso|formacao) (de nivel )?superior"]
POS_GRADUACAO = [r"pos-? ?graduac", r"pos-? ?graduand", r"residencia juridica"]

# =====================================================================

PCI = "https://www.pciconcursos.com.br/concursos/"
CNB = "https://concursosnobrasil.com/concursos/"
REGIAO_PCI = {
    "RS": "sul", "SC": "sul", "PR": "sul", "SP": "sudeste", "RJ": "sudeste", "MG": "sudeste", "ES": "sudeste",
    "MS": "centrooeste", "MT": "centrooeste", "GO": "centrooeste", "DF": "centrooeste",
}
MESES = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]


# ---------- utilidades ----------

def norm_igual(texto):
    """Como norm(), mas mantém o tamanho do texto: assim dá pra recortar o trecho original."""
    return "".join((unicodedata.normalize("NFKD", c)[:1] or c).lower()[:1] for c in texto)


def sem_tags(trecho):
    trecho = re.sub(r"<(script|style)\b.*?</\1>", " ", trecho, flags=re.S)
    trecho = re.sub(r"<(br|/p|/li|/tr|/h\d|/td|/div)\b[^>]*>", "\n", trecho)
    trecho = htmllib.unescape(re.sub(r"<[^>]+>", " ", trecho))
    linhas = (re.sub(r"[ \t\xa0]+", " ", x).strip() for x in trecho.split("\n"))
    return "\n".join(x for x in linhas if x)


def dinheiro(texto):
    """'R$ 13.844,56' -> 13844.56; 'R$ 2,7 mil' -> 2700.0; nada -> 0."""
    m = re.search(r"R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?)\s*(mil\b)?", texto or "")
    if not m:
        return 0.0
    valor = float(m.group(1).replace(".", "").replace(",", "."))
    return valor * 1000 if m.group(2) else valor


def reais(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def achar(padroes, t, original):
    """Nomes de cargo (como estão no edital) que batem com algum padrão."""
    achados = []
    for p in padroes:
        for m in re.finditer(p, t):
            inicio = original.rfind("\n", 0, m.start()) + 1
            fim = original.find("\n", m.end())
            linha = original[inicio:fim if fim >= 0 else len(original)]
            if len(linha) > 90:  # é uma frase: fica só o pedaço que bateu
                linha = original[m.start():m.end()]
                linha = linha[:1].upper() + linha[1:]
            linha = re.sub(r"\s*\(\s*\d+\s*vagas?[^)]*\)|\s*[-–]?\s*\d+\s*vagas?\b.*$", "", linha, flags=re.I)
            linha = linha.strip(" -–:;,.")
            if linha and norm(linha) not in (norm(x) for x in achados):
                achados.append(linha)
    return achados[:6]


def salario_da_linha(cargos):
    """Se a linha do cargo traz o salário ("Técnico em Informática - R$ 4.200,00"), usa ele."""
    valores = [dinheiro(c) for c in cargos]
    valores = [v for v in valores if v]
    return max(valores) if valores else 0.0


def faixa_salarial(texto):
    """'remuneração inicial vai de R$ 2.339,27 a R$ 19.089,94' -> (2339.27, 19089.94)."""
    m = re.search(r"de R\$\s*([\d.]+,\d{2}) a(?:té)? R\$\s*([\d.]+,\d{2})", texto or "")
    if not m:
        return 0.0, 0.0
    return dinheiro("R$ " + m.group(1)), dinheiro("R$ " + m.group(2))


def data_inscricao(texto, hoje):
    """Último dia de inscrição que aparece nas frases sobre inscrição."""
    datas = []
    for frase in re.split(r"(?<=[.;])\s+|\n", texto):
        f = norm(frase)
        if "inscri" not in f:
            continue
        for d, m, a in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", f):
            datas.append((int(a), int(m), int(d)))
        for d, mes, a in re.findall(r"\b(\d{1,2})o? de (" + "|".join(MESES) + r")(?: de (\d{4}))?", f):
            mes = MESES.index(mes) + 1
            ano = int(a) if a else (hoje.year + 1 if mes < hoje.month - 6 else hoje.year)
            datas.append((ano, mes, int(d)))
    validas = []
    for a, m, d in datas:
        try:
            validas.append(date(a, m, d))
        except ValueError:
            pass
    return max(validas).isoformat() if validas else ""


def cidade_do_orgao(orgao):
    """'Câmara de Vereadores de Erval Velho' -> 'Erval Velho'. Só pra prefeituras e câmaras."""
    if not re.match(r"(prefeitura|c[aâ]mara|munic[ií]pio)", orgao, re.I):
        return ""
    for parte in (re.split(r"\s+[-–]\s+|,|/|\s+e\s+(?=[A-ZÁÉÍÓÚ])", orgao)[0], orgao):
        m = re.search(r"\b(?:de|do|da|dos|das)\s+((?!Vereadores\b|Munic[ií]pio\b)[A-ZÁÉÍÓÚÂÊÔÃÕÇ][^,(]*)$", parte)
        if m:
            return m.group(1).strip(" -–")
    return ""


def cidade_do_titulo(titulo):
    """'... seletivo em Sapucaia do Sul' ou '... no campus Jacarezinho' -> nome da cidade."""
    m = re.search(r"\b(?:em|campus)\s+([A-ZÁÉÍÓÚ][\wÀ-ú]+(?:\s+(?:d[aeo]s?\s+)?[A-ZÁÉÍÓÚ][\wÀ-ú]+)*)\s*$", titulo.strip())
    return m.group(1) if m else ""


def nucleo(orgao):
    """Nome do órgão sem "Prefeitura de", pontuação e espaços: "TRT 4ª Região" -> "trt4"."""
    n = re.sub(r"(\d+)[ao]\b", r"\1", norm(orgao))
    n = re.sub(r"\b(concurso|prefeitura|municipal|municipio|camara|de|do|da|dos|das|vereadores|regiao"
               r"|s\.?a\.?|ltda)\b", " ", n)
    return re.sub(r"[^a-z0-9]+", "", n)


def chaves(c):
    """Jeitos de reconhecer o mesmo órgão nas duas fontes (nome, sigla, cidade)."""
    nomes = {nucleo(c["orgao"]), nucleo(re.split(r"\s+[-–]\s+", c["orgao"])[0])}
    nomes |= {re.sub(r"(rs|sc|pr|sp)$", "", n) for n in nomes}
    cidade = cidade_do_orgao(c["orgao"])
    if cidade:
        nomes.add("cidade:" + nucleo(cidade))
    return {n for n in nomes if len(n) >= 2}


# ---------- edital (PDF) ----------

BLOQUEIO = ("cf-mitigated", "x-amzn-waf-action")


class Bloqueado(Exception):
    """O site da banca tem proteção contra robôs (Cloudflare, AWS WAF, captcha)."""


def links_da_pagina(html, base):
    """[(url absoluta, texto do link + o texto logo antes dele)] de uma página."""
    from urllib.parse import urljoin
    saida = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', html, re.S | re.I):
        href = htmllib.unescape(m.group(1).strip())
        if href.startswith(("javascript:", "mailto:", "tel:")):
            continue
        antes = sem_tags(html[max(0, m.start() - 400):m.start()]).replace("\n", " ")[-120:]
        texto = sem_tags(m.group(2)).replace("\n", " ")[:150]
        saida.append((urljoin(base, href), f"{antes} {texto}"))
    return saida


def nota_pdf(url, texto):
    """Quanto mais alto, mais cara de edital de abertura o link tem."""
    t = norm(url + " " + texto)
    nota = 0
    if re.search(r"\.pdf\b|arquivo|download|anexo", t):
        nota += 1
    if "edital" in t:
        nota += 3
    if re.search(r"abertura|\b0*1/20\d\d\b|edital de concurso|edital de processo|edital completo", t):
        nota += 3
    if "consolidad" in t:
        nota += 1
    if re.search(r"concurso|processo seletivo|selecao publica", t):
        nota += 2
    if re.search(r"retific|resultado|homolog|gabarito|convoca|classifica|recurso|deferid|prova|errata|aviso|"
                 r"termo|politica|privacidade|manual|cronograma|requerimento|formulario|ficha|lgpd|cookies", t):
        nota -= 4
    return nota


def parece_arquivo(url):
    return bool(re.search(r"\.pdf\b|arquivo|download|/files?/|anexo", url.lower()))


def baixar(s, url, limite=25_000_000):
    r = s.get(url, timeout=(8, 30), stream=True, headers={"Accept": "text/html,application/pdf,*/*"})
    if any(h in r.headers for h in BLOQUEIO) or r.status_code in (202, 403, 429, 503):
        r.close()
        raise Bloqueado(f"HTTP {r.status_code}")
    r.raise_for_status()
    corpo = b""
    for parte in r.iter_content(65536):
        corpo += parte
        if len(corpo) > limite:
            break
    r.close()
    return corpo, r.headers.get("content-type", ""), r.url


def parece_edital(texto):
    t = norm(texto[:60000])
    return (len(texto) > 4000 and "edital" in t and "cargo" in t
            and bool(re.search(r"requisito|escolaridade|vencimento|remuneracao|salario", t)))


def do_orgao(texto, alvo):
    """O edital fala do órgão certo? (evita pegar o edital de outra cidade)"""
    return not alvo or alvo in norm(texto[:15000]).replace("-", " ")


def achar_edital(s, links, alvo, max_buscas=12):
    """Segue os links (notícias, banca, prefeitura) até o edital.
    -> (url, texto, situacao); situacao: lido, bloqueado, sem pdf, pdf escaneado."""
    bloqueado = escaneado = False
    vistos = set()
    fila = [(u, 0) for u in links]
    while fila and len(vistos) < max_buscas:
        url, nivel = fila.pop(0)
        if url in vistos:
            continue
        vistos.add(url)
        try:
            corpo, tipo, final = baixar(s, url)
        except Bloqueado:
            bloqueado = True
            continue
        except Exception:
            continue
        if corpo[:5] == b"%PDF-":
            try:
                texto = texto_do_pdf(corpo)
            except Exception:
                continue
            if len(texto.strip()) < 800:
                escaneado = True
                continue
            if do_orgao(texto, alvo):
                return final, texto, "lido"
            continue
        if "html" not in tipo.lower():
            continue
        html = corpo.decode("utf-8", "replace")
        texto = sem_tags(re.sub(r"<(nav|header|footer)\b.*?</\1>", " ", html, flags=re.S | re.I))
        if parece_edital(texto) and do_orgao(texto, alvo):
            return final, texto, "lido"  # edital publicado como página (Diário Oficial da União, por exemplo)
        if nivel >= 2:
            continue
        candidatos = sorted(((nota_pdf(u, t), i, u) for i, (u, t) in enumerate(links_da_pagina(html, final))),
                            key=lambda x: (-x[0], x[1]))
        # primeiro os arquivos com cara de edital (até um link só com ícone serve), depois as páginas
        arquivos = [(u, nivel + 1) for n, _, u in candidatos if n >= 1 and parece_arquivo(u)][:3]
        paginas = [(u, nivel + 1) for n, _, u in candidatos if n >= 2 and not parece_arquivo(u)][:3]
        fila = arquivos + paginas + fila
    if bloqueado:
        return "", "", "bloqueado"
    return "", "", "pdf escaneado" if escaneado else "sem pdf"


def texto_do_pdf(corpo, paginas=45):
    import io
    from pypdf import PdfReader
    leitor = PdfReader(io.BytesIO(corpo))
    partes = []
    for pagina in leitor.pages[:paginas]:
        try:
            partes.append(pagina.extract_text() or "")
        except Exception:
            partes.append("")
    return "\n".join(partes)


DINHEIRO = r"(?<![\d.,])\d{1,3}(?:\.\d{3})*,\d{2}(?![\d,])"


def frouxo(padrao):
    """Padrão que aceita palavras grudadas, como sai às vezes do PDF ("TécnicoemInformática")."""
    return padrao.replace(" ", " ?")


def linhas_de_cargo(texto):
    """Lê a tabela de cargos do edital: [{cargo, req, salario}] dos cargos que interessam a algum perfil."""
    original = re.sub(r"\s+", " ", texto)
    t = norm_igual(original)
    padroes = (CARGOS_TI + [p for p, _ in CARGOS_TI_TALVEZ] + CARGOS_DIREITO
               + [p for p, _ in CARGOS_DIREITO_TALVEZ] + [p for p, _ in CARGOS_DIREITO_FORA])
    achados = {}
    for p in padroes:
        for m in re.finditer(frouxo(p), t):
            janela = original[m.end():m.end() + 700]
            valores = [(v.start(), dinheiro("R$ " + v.group())) for v in re.finditer(DINHEIRO, janela)]
            valores = [(i, v) for i, v in valores if v >= 600]
            nome = re.sub(r"\s+", " ", original[m.start():m.end()]).strip()
            chave = norm(nome).replace(" ", "")
            if chave in achados and achados[chave]["salario"]:
                continue
            if valores:
                i, v = valores[0]
                req = janela[:i]
            else:
                v, req = 0.0, janela[:300]
            req = re.sub(r"^[\s\-–:]*(\d{1,3}|cr|cadastro reserva)?\s*(\d{2} ?h(oras)?)?", "", req, flags=re.I)
            if chave not in achados or v:
                achados[chave] = {"cargo": nome, "req": req.strip()[:400], "salario": v}
    return list(achados.values())[:15]


def trechos_estagio(texto):
    """Linhas do edital de estágio que falam de curso, semestre e formatura."""
    linhas = [x.strip() for x in texto.split("\n") if x.strip()]
    pega = [x for x in linhas if re.search(r"curso|semestre|formatura|conclus|matriculad|direito|informatica|"
                                            r"computacao|sistemas|tecnologia", norm(x))]
    return "\n".join(pega)[:3000]


def trechos_lotacao(texto):
    """Pedaços do edital que dizem onde é o trabalho."""
    original = re.sub(r"\s+", " ", texto)
    t = norm(original)
    pedacos = [original[max(0, m.start() - 80):m.end() + 300]
               for m in re.finditer(r"lotac|local de trabalho|locais de trabalho|cidade de|municipio de|campus|unidade de", t)]
    return " | ".join(pedacos[:12])[:3000]


def ler_edital_pdf(s, links, alvo):
    """-> dict guardado em concursos.json com o que interessa do edital."""
    info = {"versao": VERSAO_EDITAL, "url": "", "situacao": "sem link", "cargos": [], "estagio": "", "lotacao": ""}
    if not links:
        return info
    url, texto, situacao = achar_edital(s, links, alvo)
    info.update(url=url, situacao=situacao)
    if texto:
        info["cargos"] = linhas_de_cargo(texto)
        info["estagio"] = trechos_estagio(texto)
        info["lotacao"] = trechos_lotacao(texto)
    return info


def juntar(pci, cnb):
    """O PCI vem primeiro. Do Concursos no Brasil entra o que o PCI não tem (sobretudo estágios);
    quando os dois têm o mesmo concurso, a notícia do Concursos no Brasil fica guardada pra achar o edital."""
    def perto_no_salario(a, b):
        if not a["salario"] or not b["salario"]:
            return 1.0
        return abs(a["salario"] - b["salario"]) / max(a["salario"], b["salario"])

    usados, links, saida = set(), set(), []
    for c in pci:
        if c["link"] in links:
            continue
        links.add(c["link"])
        ks, est = chaves(c), e_estagio(c)
        pares = [o for o in cnb if o["uf"] == c["uf"] and o["link"] not in usados
                 and e_estagio(o) == est and chaves(o) & ks]
        if pares:
            o = min(pares, key=lambda o: perto_no_salario(c, o))
            c["artigos"] = [o["link"]]
            usados.add(o["link"])
        saida.append(c)
    for c in cnb:
        if c["link"] in usados or c["link"] in links:
            continue
        if not e_estagio(c) and any(chaves(c) & chaves(p) for p in pci if p["uf"] == c["uf"]):
            continue  # outro edital do mesmo órgão que o PCI já tem
        c["artigos"] = [c["link"]]
        links.add(c["link"])
        saida.append(c)
    return saida


# ---------- notícia e outras fontes do mesmo concurso ----------

FONTES_WP = [  # sites de notícias de concursos com busca aberta (WordPress)
    "https://concursosnobrasil.com",
    "https://blog.grancursosonline.com.br",
    "https://concursos.estrategia.com/portal",
]
NAO_SAO_EDITAL = re.compile(
    r"facebook|instagram|twitter|x\.com/|whatsapp|t\.me/|youtube|google|bit\.ly|linktr|spotify|tiktok|linkedin"
    r"|concursosnobrasil|grancursos|estrategia|pciconcursos|qconcursos|apostila|cdn-cgi|wp-content/uploads/20\d\d/\d\d/.*\.(jpe?g|png|webp)")


def ler_noticia(s, link):
    r = s.get(link, headers={"Accept": "text/html"}, timeout=40)
    r.raise_for_status()
    h = r.text
    i, j = h.find("<article"), h.find("</article>")
    corpo = h[i:j] if 0 <= i < j else h
    corpo = re.sub(r'<div class="related-post.*?(?=<p>|<h2|<h3|<ul|$)', " ", corpo, flags=re.S)
    texto = sem_tags(corpo)
    texto = re.sub(r"continua depois da publicidade|Quer se aprofundar\?.*$", " ", texto, flags=re.I | re.S)
    return texto[:8000], links_externos(corpo)


def links_externos(html):
    vistos, saida = set(), []
    for u in re.findall(r'href=["\'](https?://[^"\']+)["\']', html):
        u = htmllib.unescape(u)
        if NAO_SAO_EDITAL.search(u.lower()) or u in vistos:
            continue
        vistos.add(u)
        saida.append(u)
    return saida


def nome_de_busca(c):
    """O que procurar nos outros sites: a cidade (prefeituras e câmaras) ou a sigla/nome do órgão."""
    cidade = cidade_do_orgao(c["orgao"])
    if cidade:
        return cidade
    return re.split(r"\s+[-–]\s+|\(", c["orgao"])[0].strip()


def outras_noticias(s, c, hoje):
    """Links (banca, PDF, prefeitura, diário oficial) citados por outras notícias do mesmo concurso."""
    nome = nome_de_busca(c)
    alvo = norm(nome)
    est = e_estagio(c)
    links = []
    for base in FONTES_WP:
        try:
            r = s.get(base + "/wp-json/wp/v2/posts", timeout=(8, 25),
                      params={"search": nome, "per_page": 8, "_fields": "link,title,date,content"})
            r.raise_for_status()
            posts = r.json()
        except Exception:
            continue
        bons = []
        for p in posts if isinstance(posts, list) else []:
            titulo = norm(sem_tags((p.get("title") or {}).get("rendered", "")))
            data = (p.get("date") or "")[:10]
            if alvo not in titulo or (data and data < (hoje - timedelta(days=150)).isoformat()):
                continue
            # o mesmo tipo de seleção primeiro (estágio com estágio) e o salário mais parecido
            nota = (tem(["estagio", "estagiarios"], titulo) == est) * 2
            if c["salario"] and abs(dinheiro(titulo) - c["salario"]) <= c["salario"] * 0.1:
                nota += 1
            bons.append((nota, data, p))
        for _, _, p in sorted(bons, key=lambda x: (x[0], x[1]), reverse=True)[:3]:
            links += links_externos((p.get("content") or {}).get("rendered", ""))
        time.sleep(0.3)
    return links


def site_da_prefeitura(c):
    """Prefeituras e câmaras do Sul quase sempre ficam em cidade.uf.gov.br."""
    cidade = cidade_do_orgao(c["orgao"])
    if not cidade or not c["uf"]:
        return []
    slug = re.sub(r"[^a-z0-9]+", "", norm(cidade))
    uf = c["uf"].lower()
    if re.match(r"c[aâ]mara", c["orgao"], re.I):
        return [f"https://www.camara{slug}.{uf}.gov.br/", f"https://{slug}.{uf}.leg.br/"]
    return [f"https://{slug}.{uf}.gov.br/", f"https://www.{slug}.{uf}.gov.br/"]


# ---------- listas de concursos ----------

def listar_pci(s, hoje):
    paginas = sorted({REGIAO_PCI[uf] for uf in UFS if uf in REGIAO_PCI})
    if INCLUIR_NACIONAIS:
        paginas.append("nacional")
    itens = []
    for pagina in paginas:
        r = s.get(PCI + pagina + "/", headers={"Accept": "text/html"}, timeout=40)
        r.raise_for_status()
        blocos = r.text.split('onclick="myClick(event)" data-url="')[1:]
        for b in blocos:
            link = b[:b.index('"')]
            a = re.search(r'<div class="ca"><a[^>]*title="([^"]*)"[^>]*>(.*?)</a>', b, re.S)
            uf = re.search(r'<div class="cc">(.*?)</div>', b, re.S)
            cd = re.search(r'<div class="cd">(.*?)</div>', b, re.S)
            ce = re.search(r'<div class="ce">(.*?)</div>', b, re.S)
            if not (a and cd):
                continue
            uf = sem_tags(uf.group(1)).strip().upper() if uf else ""
            if pagina == "nacional":
                uf = ""
            elif uf not in UFS:
                continue
            partes = [x.strip() for x in sem_tags(cd.group(1).replace("<br>", "\n")).split("\n") if x.strip()]
            fim = re.findall(r"(\d{2})/(\d{2})/(\d{4})", sem_tags(ce.group(1)) if ce else "")
            ate = f"{fim[-1][2]}-{fim[-1][1]}-{fim[-1][0]}" if fim else ""
            if ate and ate < hoje.isoformat():
                continue
            vagas_salario = partes[0] if partes else ""
            itens.append({
                "orgao": sem_tags(a.group(2)), "titulo": htmllib.unescape(a.group(1)), "link": link,
                "fonte": "PCI Concursos", "uf": uf, "ate": ate,
                "vagas": re.split(r"\s+até\s+R\$", vagas_salario)[0].strip(),
                "salario": dinheiro(vagas_salario), "por_hora": "por hora" in vagas_salario,
                "resumo": partes[1] if len(partes) > 1 else "",
                "escolaridade": partes[2] if len(partes) > 2 else "",
            })
    return itens


def listar_cnb(s):
    itens = []
    for uf in UFS:
        r = s.get(CNB + uf.lower() + "/", headers={"Accept": "text/html"}, timeout=40)
        r.raise_for_status()
        linhas = re.findall(r'<tr[^>]*>\s*<td>\s*<a href="([^"]+)" title="([^"]+)">(.*?)</a>\s*</td>\s*'
                            r'<td[^>]*>(.*?)</td>', r.text, re.S)
        for link, titulo, orgao, vagas in linhas:
            titulo, vagas = htmllib.unescape(titulo), sem_tags(vagas).strip()
            itens.append({
                "orgao": sem_tags(orgao), "titulo": titulo, "link": link, "fonte": "Concursos no Brasil",
                "uf": uf, "ate": "", "salario": dinheiro(titulo), "por_hora": False,
                "vagas": "1 vaga" if vagas == "1" else f"{vagas} vagas" if vagas else "",
                "resumo": "", "escolaridade": "",
            })
    return itens


def e_estagio(c):
    return tem(["estagio", "estagios", "estagiario", "estagiarios", "estagiaria", "residencia juridica"],
               norm(c["titulo"] + " " + c["resumo"]))


# ---------- quais cargos servem pra você ----------

FORMATURA_DIREITO = "jan/2027"

NIVEIS = [("superior", r"superior|graduac|bachar|licenciat|tecnolog"), ("tecnico", r"tecnic"),
          ("medio", r"medio|2o grau|segundo grau"), ("fundamental", r"fundamental|alfabetiz")]


def niveis_da_noticia(texto):
    """A notícia costuma agrupar os cargos por escolaridade ("Nível técnico: Técnico de Informática")."""
    nivel, saida = "", {}
    for linha in texto.split("\n"):
        l = norm(linha).strip(" :-–")
        if len(l) <= 45 and re.match(r"^(cargos? de )?(nivel|ensino|escolaridade|formacao)?\s*"
                                      r"(fundamental|medio|tecnico|superior)\b", l):
            nivel = next(n for n, p in NIVEIS if re.search(p, l))
            continue
        if len(l) > 120:
            nivel = ""
        elif nivel:
            saida[l] = nivel
    return saida


def nivel_do_texto(req):
    r = norm(req)
    for nivel, padrao in NIVEIS:
        if re.search(padrao, r):
            return nivel
    return ""


def avaliar_ti(nome, req, nivel):
    """Você: técnico em informática, cursando Sistemas de Informação."""
    n, r = norm(nome), norm(req)
    if re.search(r"licenciatura", r) and not re.search(r"bacharel|tecnolog|tecnico em", r):
        return "descartada", "Pede licenciatura"
    if re.search(r"tecnic[oa] (em|de) (informatica|ti|tecnologia da informacao|redes|manutencao|processamento)"
                 r"|curso tecnico", r):
        return "encaixa", "Pede curso técnico: você é técnico em informática"
    if re.search(r"cursando|em andamento|matriculad|estudante", r):
        return "encaixa", "Aceita quem está cursando"
    if re.search(r"superior|graduac|bachar|tecnolog|diploma", r):
        return "talvez", "Pede faculdade concluída: você ainda está cursando SI"
    if re.search(r"ensino medio|nivel medio|medio completo|2o grau|fundamental", r):
        return "encaixa", "Pede ensino médio"
    nivel = nivel or ("tecnico" if re.search(r"tecnic[oa] (em|de)", n) else
                      "medio" if re.search(r"(auxiliar|assistente|agente|monitor|operador)", n) else
                      "superior" if re.search(r"analista|engenheir|cientista|administrador|especialista", n) else "")
    if re.search(r"professor|instrutor", n):
        return "talvez", "Professor/instrutor: costuma pedir licenciatura"
    if nivel in ("tecnico", "medio", "fundamental"):
        return "encaixa", f"Cargo de nível {'técnico' if nivel == 'tecnico' else nivel}"
    if nivel == "superior":
        return "talvez", "Costuma pedir faculdade concluída: você ainda está cursando SI"
    return "talvez", "Confira a escolaridade no edital"


def avaliar_direito(nome, req, nivel):
    """Você: cursando Direito, formatura em FORMATURA_DIREITO, sem OAB."""
    n, r = norm(nome), norm(req)
    for padrao, motivo in CARGOS_DIREITO_FORA:
        if re.search(padrao, n):
            return "descartada", motivo
    if re.search(r"\boab\b", r):
        return "descartada", "Pede OAB"
    if re.search(r"cursando|em andamento|matriculad|estudante|academico", r):
        return "encaixa", "Aceita quem está cursando Direito"
    if re.search(r"superior|graduac|bachar|diploma", r):
        return "talvez", f"Pede faculdade concluída: você se forma em {FORMATURA_DIREITO} e o diploma é cobrado na posse"
    if re.search(r"ensino medio|nivel medio|medio completo|2o grau|fundamental|tecnico", r):
        return "encaixa", "Pede ensino médio"
    if nivel in ("medio", "tecnico", "fundamental"):
        return "encaixa", "Cargo de nível médio"
    if nivel == "superior" or re.search(r"analista|oficial de justica|assessor|delegad|escrivao|inspetor|"
                                        r"controlador|auditor|fiscal|consultor", n):
        return "talvez", f"Costuma pedir faculdade concluída: você se forma em {FORMATURA_DIREITO}"
    return "talvez", "Confira a escolaridade: alguns pedem só ensino médio"


def candidatos(perfil, original, t):
    """Cargos do perfil citados num texto: [(nome, padrão)]."""
    if perfil == "ti":
        padroes = CARGOS_TI + [p for p, _ in CARGOS_TI_TALVEZ]
    else:
        padroes = CARGOS_DIREITO + [p for p, _ in CARGOS_DIREITO_TALVEZ] + [p for p, _ in CARGOS_DIREITO_FORA]
    return achar(padroes, t, original)


def nivel_da_lista(c):
    esc = [n for n, p in NIVEIS if re.search(p, norm(c["escolaridade"]))]
    return esc[0] if len(esc) == 1 else ""


def classificar(c, noticia, edital, perfil):
    """-> [classe, motivo, cargos ("Nome · R$ x"), salário do cargo, de onde veio o salário]"""
    avaliar = avaliar_ti if perfil == "ti" else avaliar_direito
    texto_est = (edital.get("estagio") or "") + "\n" + noticia + "\n" + c["titulo"]
    t_est = norm(texto_est)

    if e_estagio(c):
        if perfil == "ti":
            if any(re.search(p, t_est) for p in CURSOS_TI):
                return ["encaixa", "Estágio pra estudante de TI (você cursa SI)", [], None, None]
            if any(re.search(p, t_est) for p in QUALQUER_CURSO):
                return ["talvez", "Estágio pra vários cursos: confira se SI está incluído", [], None, None]
            return ["descartada", "Estágio sem curso de TI", [], None, None]
        if not re.search(r"\bdireito\b|juridic", t_est):
            return ["descartada", "Estágio sem vaga pra Direito", [], None, None]
        if any(re.search(p, t_est) for p in POS_GRADUACAO) and not re.search(r"graduacao em direito|cursando direito", t_est):
            return ["descartada", "Estágio de pós: é pra quem já se formou", [], None, None]
        if re.search(r"ultimo semestre|ultimos semestres|semestres? restantes|minimo de \d+ semestres? (a|para) cursar"
                     r"|50% da carga|formatura[^.]{0,40}20(2[89]|3\d)", t_est):
            return ["talvez", f"Confira o tempo que falta pra formatura: você se forma em {FORMATURA_DIREITO}", [], None, None]
        return ["encaixa", "Estágio pra estudante de Direito", [], None, None]

    resultados = []  # (classe, motivo, nome, salário, origem)
    linhas = edital.get("cargos") or []
    padroes_perfil = (CARGOS_TI + [p for p, _ in CARGOS_TI_TALVEZ] if perfil == "ti" else
                      CARGOS_DIREITO + [p for p, _ in CARGOS_DIREITO_TALVEZ] + [p for p, _ in CARGOS_DIREITO_FORA])
    for l in linhas:  # o edital manda: escolaridade e salário de cada cargo
        if any(re.search(p, norm(l["cargo"])) for p in padroes_perfil):
            classe, motivo = avaliar(l["cargo"], l["req"], nivel_do_texto(l["req"]))
            resultados.append((classe, motivo, l["cargo"], l["salario"] or None, "edital" if l["salario"] else None))
    if not resultados:  # sem edital: o que a notícia diz
        original = "\n".join([c["titulo"]] + [x.strip() for x in c["resumo"].split(",")] + [noticia])
        niveis = niveis_da_noticia(noticia)
        for nome in candidatos(perfil, original, norm_igual(original)):
            nivel = niveis.get(norm(nome).strip(" :-–")) or next(
                (v for k, v in niveis.items() if norm(nome) in k), "") or nivel_da_lista(c)
            classe, motivo = avaliar(nome, "", nivel)
            valor = dinheiro(nome)
            resultados.append((classe, motivo, nome, valor or None, "noticia" if valor else None))
    if resultados:
        peso = {"encaixa": 2, "talvez": 1, "descartada": 0}
        melhor = max(peso[r[0]] for r in resultados)
        escolhidos = [r for r in resultados if peso[r[0]] == melhor]
        valores = [r[3] for r in escolhidos if r[3]]
        cargos = [r[2] + (f" · {reais(r[3])}" if r[3] else "") for r in escolhidos][:6]
        origem = next((r[4] for r in escolhidos if r[3] == max(valores)), None) if valores else None
        return [escolhidos[0][0], escolhidos[0][1], cargos, max(valores) if valores else None, origem]

    if perfil == "direito" and nivel_da_lista(c) != "fundamental" and any(
            re.search(p, norm(noticia)) for p in QUALQUER_SUPERIOR):
        return ["talvez", f"Tem cargo de nível superior em qualquer área (você se forma em {FORMATURA_DIREITO})", [], None, None]
    esc = norm(c["escolaridade"])
    if esc and "tecnico" not in esc and "superior" not in esc and "nao informada" not in esc and perfil == "ti":
        return ["descartada", "Só pede ensino fundamental ou médio, sem cargo de TI", [], None, None]
    if not noticia and not linhas and "varios cargos" in norm(c["resumo"]):
        return ["talvez", "Não deu pra ler os cargos: confira o edital", [], None, None]
    return ["descartada", "Nenhum cargo " + ("de TI" if perfil == "ti" else "da área jurídica"), [], None, None]


# ---------- cidade ----------

COMUNS = {"Vitória", "Esperança", "Progresso", "Liberdade", "Paraíso", "Independência", "Harmonia", "União",
          "Salvador", "Planalto", "Cristal", "Formosa", "Palmeira", "Sertão", "Cruzeiro", "Bandeirantes", "Pinhal",
          "Machado", "Saudade", "Campina", "Colorado", "Nova", "Jardim", "Tupã", "Itapuã", "Barracão", "Alvorada",
          "Mariana", "Bom Jesus", "Esteio", "Feliz", "Imbé", "Ivoti", "Riozinho", "Serafina Corrêa", "Paraná",
          "Cerro Azul", "Rio Negro", "Prudentópolis"}
PREFERIDAS = ["Santa Maria", "Porto Alegre"]  # aparecem primeiro quando o concurso tem vaga nelas


def carregar_municipios():
    from pathlib import Path
    try:
        return json.loads((Path(__file__).resolve().parent / "municipios.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


MUNICIPIOS = carregar_municipios()


def cidades_no_texto(texto, uf):
    contagem = {}
    for nome in MUNICIPIOS.get(uf, []):
        if nome in COMUNS or len(nome) < 4:
            continue
        n = len(re.findall(r"(?<![\wÀ-ú])" + re.escape(nome) + r"(?![\wÀ-ú])", texto))
        if n:
            contagem[nome] = n
    # "Santa Maria do Herval" não conta como "Santa Maria"
    for a in list(contagem):
        for b in contagem:
            if a != b and a in b:
                contagem[a] -= contagem[b]
    nomes = [n for n, q in sorted(contagem.items(), key=lambda x: -x[1]) if q > 0]
    return sorted(nomes, key=lambda n: PREFERIDAS.index(n) if n in PREFERIDAS else len(PREFERIDAS))


def cidades(c, noticia, edital):
    """Onde é o trabalho: a cidade da prefeitura/câmara, ou as cidades de lotação do edital/notícia."""
    if not c["uf"]:
        return []
    propria = cidade_do_orgao(c["orgao"])
    if propria:
        return [propria]
    achadas = cidades_no_texto(edital.get("lotacao") or "", c["uf"])
    if not achadas:
        achadas = cidades_no_texto(c["titulo"] + "\n" + noticia, c["uf"])
    return achadas[:12]


def texto_cidades(lista):
    if not lista:
        return ""
    if len(lista) <= 3:
        return ", ".join(lista[:-1]) + (" e " if len(lista) > 1 else "") + lista[-1]
    return f"{', '.join(lista[:3])} e mais {len(lista) - 3}"


# ---------- juntando tudo ----------

def montar(c, g, agora):
    """Concurso no formato da página. g: o que está guardado em concursos.json pra ele."""
    noticia, edital = g.get("texto", ""), g.get("edital") or {}
    estagio = e_estagio(c)
    ate = c["ate"] or data_inscricao(noticia, agora.date())
    minimo, maximo = faixa_salarial(noticia)
    valor = c["salario"] or maximo
    lugar = cidades(c, noticia, edital)
    return {
        "orgao": c["orgao"], "titulo": c["titulo"], "link": c["link"], "fonte": c["fonte"],
        "uf": c["uf"], "cidade": texto_cidades(lugar), "cidades": lugar, "vagas": c["vagas"],
        "escolaridade": c["escolaridade"], "ate": ate, "estagio": estagio,
        "salario": valor or None, "salarioMin": minimo if minimo and minimo < valor else None,
        "salarioTexto": (reais(valor) + (" por hora" if c["por_hora"] else "")) if valor else "",
        "edital": edital.get("situacao", "sem link"), "editalUrl": edital.get("url", ""),
        "nova": datetime.fromisoformat(g["visto"]) >= agora - timedelta(hours=24),
        "perfis": {p: classificar(c, noticia, edital, p) for p in ("ti", "direito")},
    }


def coletar(status, agora, pasta):
    s = sessao()
    s.headers["User-Agent"] = "Mozilla/5.0 (compatible; radar-vagas/1.0)"
    hoje = agora.date()
    arquivo = pasta / "concursos.json"
    try:
        guardados = json.loads(arquivo.read_text(encoding="utf-8"))
    except Exception:
        guardados = {}

    pci, cnb = [], []
    try:
        pci = listar_pci(s, hoje)
        status["PCI Concursos"] = f"{len(pci)} encontrados" if pci else "nada encontrado"
    except Exception as e:
        status["PCI Concursos"] = f"bloqueado ({type(e).__name__})"
        print(f"  [pci] {type(e).__name__}: {str(e)[:150]}")
    try:
        cnb = listar_cnb(s)
        status["Concursos no Brasil"] = f"{len(cnb)} encontrados" if cnb else "nada encontrado"
    except Exception as e:
        status["Concursos no Brasil"] = f"bloqueado ({type(e).__name__})"
        print(f"  [concursosnobrasil] {type(e).__name__}: {str(e)[:150]}")
    print(f"Concursos: PCI {len(pci)}, Concursos no Brasil {len(cnb)}")

    itens = juntar(pci, cnb)
    abertos = [c for c in itens if not (c["ate"] and c["ate"] < hoje.isoformat())]
    lidos, novos = 0, {}
    situacoes = {}
    limite = time.monotonic() + MINUTOS_PROCURANDO_EDITAIS * 60
    for c in abertos:
        g = guardados.get(c["link"]) or {"visto": agora.isoformat()}
        if "texto" not in g:
            try:
                g["texto"], links = ler_noticia(s, c["link"])
                g["links"] = links if c["fonte"] != "PCI Concursos" else []
            except Exception as e:
                print(f"  [notícia] {c['link']}: {type(e).__name__}")
            time.sleep(0.5)
        edital = g.get("edital") or {}
        if edital.get("versao") != VERSAO_EDITAL and lidos < EDITAIS_POR_RODADA and time.monotonic() < limite:
            links = list(g.get("links") or [])
            for artigo in c.get("artigos", []):
                if artigo != c["link"]:
                    try:
                        links += ler_noticia(s, artigo)[1]
                    except Exception:
                        pass
            links += [u for u in outras_noticias(s, c, hoje) if u not in links]
            links += site_da_prefeitura(c)
            alvo = norm(nome_de_busca(c)) if c["uf"] else ""
            g["edital"] = ler_edital_pdf(s, links, alvo)
            lidos += 1
        situacao = (g.get("edital") or {}).get("situacao", "sem link")
        situacoes[situacao] = situacoes.get(situacao, 0) + 1
        novos[c["link"]] = g
    saida = []
    for c in abertos:
        item = montar(c, novos[c["link"]], agora)
        if item["ate"] and item["ate"] < hoje.isoformat():
            continue  # inscrições já fecharam
        saida.append(item)
    resumo = ", ".join(f"{q} {n}" for n, q in sorted(situacoes.items(), key=lambda x: -x[1]))
    status["Editais"] = f"{situacoes.get('lido', 0)} encontrados de {len(abertos)} ({resumo})"
    print(f"Concursos: {len(saida)} abertos, {lidos} editais procurados agora. Editais: {resumo}")

    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(novos, ensure_ascii=False, indent=0), encoding="utf-8")
    saida.sort(key=lambda x: (x["salario"] or 0), reverse=True)
    return saida


def exemplo(agora):
    """Concursos inventados pra testar a página sem internet."""
    hoje = agora.date()
    d = lambda n: (hoje + timedelta(days=n)).isoformat()
    base = {"fonte": "PCI Concursos", "por_hora": False, "resumo": "", "escolaridade": ""}
    lido = lambda cargos, estagio="", lotacao="": {"versao": VERSAO_EDITAL, "url": "https://example.com/edital.pdf",
                                                   "situacao": "lido", "cargos": cargos, "estagio": estagio,
                                                   "lotacao": lotacao}
    lista = [
        ({**base, "orgao": "Prefeitura de Santa Maria", "titulo": "Prefeitura de Santa Maria - RS abre concurso",
          "link": "https://example.com/c1", "uf": "RS", "ate": d(12), "vagas": "12 vagas", "salario": 7850.40,
          "resumo": "Vários Cargos", "escolaridade": "Médio / Técnico / Superior"},
         {"texto": "", "edital": lido([
             {"cargo": "Analista de Sistemas", "req": "Curso superior completo em Sistemas de Informação", "salario": 7850.40},
             {"cargo": "Técnico em Informática", "req": "Ensino médio completo e curso técnico em informática", "salario": 4120.00},
             {"cargo": "Procurador Municipal", "req": "Bacharel em Direito e inscrição na OAB", "salario": 12000.00}])}),
        ({**base, "orgao": "TRT 4 - Tribunal Regional do Trabalho da 4ª Região", "titulo": "TRT4 - RS abre concurso",
          "link": "https://example.com/c2", "uf": "RS", "ate": d(18), "vagas": "Cadastro de reserva", "salario": 16040.88,
          "resumo": "Analista Judiciário, Técnico Judiciário", "escolaridade": "Superior"},
         {"texto": "", "edital": lido([
             {"cargo": "Analista Judiciário - Área Judiciária", "req": "Curso superior em Direito", "salario": 16040.88},
             {"cargo": "Técnico Judiciário - Área Administrativa", "req": "Curso superior completo", "salario": 9780.00}],
             lotacao="Lotação: Porto Alegre, Santa Maria, Caxias do Sul, Pelotas e Passo Fundo")}),
        ({**base, "orgao": "BANRISUL", "titulo": "Estágio Banrisul abre 378 vagas em diversas cidades do RS com bolsas de até R$ 2,7 mil",
          "link": "https://example.com/c3", "uf": "RS", "ate": d(5), "vagas": "378 vagas", "salario": 2707.80,
          "fonte": "Concursos no Brasil"},
         {"texto": "Grupo I: Administração\nGrupo III: Tecnologia da Informação\nVagas em Porto Alegre, Santa Maria e Ijuí.",
          "edital": {"versao": VERSAO_EDITAL, "situacao": "sem pdf"}}),
        ({**base, "orgao": "TJRS", "titulo": "Estágio TJRS em Santa Maria seleciona estudantes de Direito",
          "link": "https://example.com/c4", "uf": "RS", "ate": d(9), "vagas": "10 vagas", "salario": 1200.0,
          "fonte": "Concursos no Brasil"},
         {"texto": "Estudantes de graduação em Direito. Vagas no Foro de Santa Maria.",
          "edital": {"versao": VERSAO_EDITAL, "situacao": "bloqueado"}}),
        ({**base, "orgao": "Prefeitura de Florestópolis", "titulo": "Prefeitura de Florestópolis - PR abre concurso",
          "link": "https://example.com/c5", "uf": "PR", "ate": d(3), "vagas": "46 vagas", "salario": 15389.87,
          "resumo": "Vários Cargos", "escolaridade": "Médio / Técnico / Superior"},
         {"texto": "Nível médio\nAssistente Administrativo (CR)\nNível técnico\nTécnico de Informática (1 vaga + CR)\n"
                   "Nível superior\nPsicólogo (1 vaga + CR)\nA remuneração varia de R$ 2.117,00 a R$ 15.389,87.",
          "edital": {"versao": VERSAO_EDITAL, "situacao": "bloqueado"}}),
    ]
    agora_iso = agora.isoformat()
    itens = [montar(c, {"visto": agora_iso, **g}, agora) for c, g in lista]
    itens.sort(key=lambda x: (x["salario"] or 0), reverse=True)
    return itens, {"PCI Concursos": "152 encontrados", "Concursos no Brasil": "135 encontrados",
                   "Editais": "3 encontrados de 5 (3 lido, 2 bloqueado)"}
