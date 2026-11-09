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

from vagas import FUSO, norm, sessao, tem

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================

# Estados da busca. RS, SC e PR cobrem até uns 1000 km de Porto Alegre e Santa Maria.
# Pra incluir São Paulo, é só acrescentar "SP".
UFS = ["RS", "SC", "PR"]
INCLUIR_NACIONAIS = True  # concursos federais com vagas no país todo

# Quantos editais novos abrir por rodada (os já abertos ficam guardados).
EDITAIS_POR_RODADA = 200

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


def juntar(pci, cnb):
    """O PCI vem primeiro; do Concursos no Brasil entra o que o PCI não tem (sobretudo estágios)."""
    vistos = {}
    for c in pci:
        vistos.setdefault(c["uf"], set()).update(chaves(c))
    saida, links = [], set()
    for c in pci + cnb:
        if c["link"] in links:
            continue
        if c["fonte"] != "PCI Concursos" and not e_estagio(c) and chaves(c) & vistos.get(c["uf"], set()):
            continue
        links.add(c["link"])
        saida.append(c)
    return saida


# ---------- texto dos editais ----------

def ler_edital(s, link):
    r = s.get(link, headers={"Accept": "text/html"}, timeout=40)
    r.raise_for_status()
    h = r.text
    i, j = h.find("<article"), h.find("</article>")
    corpo = h[i:j] if 0 <= i < j else h
    corpo = re.sub(r'<div class="related-post.*?(?=<p>|<h2|<h3|<ul|$)', " ", corpo, flags=re.S)
    texto = sem_tags(corpo)
    texto = re.sub(r"continua depois da publicidade|Quer se aprofundar\?.*$", " ", texto, flags=re.I | re.S)
    return texto[:8000]


def precisa_ler(c):
    """Concursos que já dá pra decidir pela lista não precisam do edital (só pede fundamental/médio)."""
    if c["fonte"] != "PCI Concursos" or e_estagio(c):
        return True
    esc = norm(c["escolaridade"])
    return "tecnico" in esc or "superior" in esc or "varios cargos" in norm(c["resumo"]) or not esc


# ---------- classificação ----------

def so_basico(c):
    esc = norm(c["escolaridade"])
    return bool(esc) and "tecnico" not in esc and "superior" not in esc and "nao informada" not in esc


def classificar(c, texto, perfil):
    """-> [classe, motivo, cargos que servem]"""
    original = "\n".join([c["titulo"]] + [x.strip() for x in c["resumo"].split(",")] + [texto])
    t = norm_igual(original)

    if e_estagio(c):
        if perfil == "ti":
            cursos = achar(CURSOS_TI, t, original)
            if cursos:
                return ["encaixa", "Estágio pra estudante de TI", cursos]
            if any(re.search(p, t) for p in QUALQUER_CURSO):
                return ["talvez", "Estágio pra vários cursos: confira se TI está incluído", []]
            return ["descartada", "Estágio sem curso de TI", []]
        tem_direito = re.search(r"\bdireito\b|juridic", t)
        if tem_direito and any(re.search(p, t) for p in POS_GRADUACAO):
            return ["talvez", "Estágio de pós em Direito: pede matrícula numa pós-graduação", []]
        if tem_direito:
            return ["descartada", "Estágio de graduação: é pra quem ainda está na faculdade", []]
        return ["descartada", "Estágio sem vaga pra Direito", []]

    if perfil == "ti":
        cargos = achar(CARGOS_TI, t, original)
        if cargos:
            return ["encaixa", "Cargo de TI", cargos]
        for padrao, motivo in CARGOS_TI_TALVEZ:
            cargos = achar([padrao], t, original)
            if cargos:
                return ["talvez", motivo, cargos]
        nome_area = "de TI"
    else:
        # "Analista Judiciário - Especialidade Arquitetura" não serve: só as especialidades jurídicas
        cargos = [x for x in achar(CARGOS_DIREITO, t, original)
                  if not re.search(r"especialidade|apoio especializado", norm(x))
                  or re.search(r"direito|juridic|oficial de justica|area judiciaria", norm(x))]
        if cargos:
            return ["encaixa", "Cargo da área jurídica, sem exigir OAB", cargos]
        for padrao, motivo in CARGOS_DIREITO_TALVEZ:
            cargos = achar([padrao], t, original)
            if cargos:
                return ["talvez", motivo, cargos]
        if not so_basico(c) and any(re.search(p, t) for p in QUALQUER_SUPERIOR):
            return ["talvez", "Tem cargo de nível superior em qualquer área", []]
        for padrao, motivo in CARGOS_DIREITO_FORA:
            cargos = achar([padrao], t, original)
            if cargos:
                return ["descartada", motivo, cargos]
        nome_area = "da área jurídica"

    if so_basico(c):
        return ["descartada", "Só pede ensino fundamental ou médio", []]
    if not texto and "varios cargos" in norm(c["resumo"]):
        return ["talvez", "Não deu pra ler os cargos: confira o edital", []]
    return ["descartada", f"Nenhum cargo {nome_area}", []]


# ---------- juntando tudo ----------

def montar(c, texto, visto, agora):
    """Concurso no formato da página."""
    cidade = (cidade_do_orgao(c["orgao"]) or cidade_do_titulo(c["titulo"])) if c["uf"] else ""
    estagio = e_estagio(c)
    ate = c["ate"] or data_inscricao(texto, agora.date())
    perfis = {}
    for perfil in ("ti", "direito"):
        classe, motivo, cargos = classificar(c, texto, perfil)
        do_cargo = salario_da_linha(cargos)
        perfis[perfil] = [classe, motivo, cargos, do_cargo or None]
    minimo, maximo = faixa_salarial(texto)
    valor = c["salario"] or maximo
    return {
        "orgao": c["orgao"], "titulo": c["titulo"], "link": c["link"], "fonte": c["fonte"],
        "uf": c["uf"], "cidade": cidade, "vagas": c["vagas"], "escolaridade": c["escolaridade"],
        "ate": ate, "estagio": estagio,
        "salario": valor or None, "salarioMin": minimo if minimo and minimo < valor else None,
        "salarioTexto": (reais(valor) + (" por hora" if c["por_hora"] else "")) if valor else "",
        "nova": datetime.fromisoformat(visto) >= agora - timedelta(hours=24),
        "perfis": perfis,
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
    lidos, falhas = 0, 0
    saida, novos_guardados = [], {}
    for c in itens:
        g = guardados.get(c["link"]) or {"visto": agora.isoformat()}
        if "texto" not in g and precisa_ler(c) and lidos < EDITAIS_POR_RODADA and falhas < 5:
            try:
                g["texto"] = ler_edital(s, c["link"])
                lidos += 1
            except Exception as e:
                falhas += 1
                print(f"  [edital] {c['link']}: {type(e).__name__}: {str(e)[:120]}")
            time.sleep(0.7)
        novos_guardados[c["link"]] = g
        item = montar(c, g.get("texto", ""), g["visto"], agora)
        if item["ate"] and item["ate"] < hoje.isoformat():
            continue  # inscrições já fecharam
        saida.append(item)
    if falhas:
        status["Editais"] = f"problema: {falhas} editais não abriram"
    print(f"Concursos: {len(saida)} abertos, {lidos} editais lidos agora, {falhas} falhas")

    # guarda só o que ainda está nas listas
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(novos_guardados, ensure_ascii=False, indent=0), encoding="utf-8")
    saida.sort(key=lambda x: (x["salario"] or 0), reverse=True)
    return saida


def exemplo(agora):
    """Concursos inventados pra testar a página sem internet."""
    hoje = agora.date()
    d = lambda n: (hoje + timedelta(days=n)).isoformat()
    base = {"fonte": "PCI Concursos", "por_hora": False}
    lista = [
        ({**base, "orgao": "Prefeitura de Santa Maria", "titulo": "Prefeitura de Santa Maria - RS abre concurso",
          "link": "https://example.com/c1", "uf": "RS", "ate": d(12), "vagas": "12 vagas", "salario": 7850.40,
          "resumo": "Vários Cargos", "escolaridade": "Médio / Técnico / Superior"},
         "Cargos:\nAnalista de Sistemas (2 vagas) - R$ 7.850,40\nTécnico em Informática (1 vaga) - R$ 4.120,00\nContador\nProcurador Municipal"),
        ({**base, "orgao": "TRT 4 - Tribunal Regional do Trabalho da 4ª Região", "titulo": "TRT4 - RS abre concurso",
          "link": "https://example.com/c2", "uf": "RS", "ate": d(18), "vagas": "Cadastro de reserva", "salario": 16040.88,
          "resumo": "Analista Judiciário, Técnico Judiciário", "escolaridade": "Superior"},
         "Analista Judiciário - Área Judiciária\nAnalista Judiciário - Apoio Especializado - Tecnologia da Informação\nTécnico Judiciário - Área Administrativa"),
        ({**base, "orgao": "BANRISUL", "titulo": "Estágio Banrisul abre 378 vagas em diversas cidades do RS com bolsas de até R$ 2,7 mil",
          "link": "https://example.com/c3", "uf": "RS", "ate": d(5), "vagas": "378 vagas", "salario": 2707.80,
          "resumo": "", "escolaridade": "", "fonte": "Concursos no Brasil"},
         "Grupo I: Administração\nGrupo III: Tecnologia da Informação\nGrupo IX: Estatística"),
        ({**base, "orgao": "PGE", "titulo": "Estágio PGE RS abre 32 vagas para pós-graduação com bolsa de R$ 2,8 mil",
          "link": "https://example.com/c4", "uf": "RS", "ate": d(9), "vagas": "32 vagas", "salario": 2800.0,
          "resumo": "", "escolaridade": "", "fonte": "Concursos no Brasil"},
         "Estudantes de pós-graduação em Direito."),
        ({**base, "orgao": "Prefeitura de Toropi", "titulo": "Câmara de Toropi abre vaga", "link": "https://example.com/c5",
          "uf": "RS", "ate": d(3), "vagas": "1 vaga", "salario": 1654.47,
          "resumo": "Agente de Serviços Complementares", "escolaridade": "Fundamental"}, ""),
        ({**base, "orgao": "TJSC - Tribunal de Justiça do Estado de Santa Catarina", "titulo": "TJSC abre concurso para juiz",
          "link": "https://example.com/c6", "uf": "SC", "ate": d(20), "vagas": "15 vagas", "salario": 35874.14,
          "resumo": "Juiz Substituto", "escolaridade": "Superior"}, "Juiz Substituto"),
    ]
    agora_iso = agora.isoformat()
    itens = [montar(c, texto, agora_iso, agora) for c, texto in lista]
    itens.sort(key=lambda x: (x["salario"] or 0), reverse=True)
    return itens, {"PCI Concursos": "143 encontrados", "Concursos no Brasil": "46 encontrados"}
