"""Regras de classificação, região e leitura de issues. Não acessa a internet."""
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vagas as m  # noqa: E402


def vaga(titulo, local="Santa Maria, RS", remoto=False, descricao=""):
    return m.nova_vaga(titulo, "X", local, "http://x", "indeed", "", remoto, descricao)


def issue(titulo, etiquetas=(), corpo=""):
    return m.vaga_github({
        "title": titulo, "labels": [{"name": e} for e in etiquetas], "body": corpo,
        "html_url": "http://x", "created_at": "2026-11-01T00:00:00Z",
    })


class Classificar(unittest.TestCase):
    CASOS = [
        ("Estágio em Redes Sociais", "", "descartada"),
        ("Estágio em Desenvolvimento de Negócios", "", "descartada"),
        ("Estágio em Programa de Suporte ao Paciente, 2026", "", "descartada"),
        ("Assistente de Suporte ao Cliente", "", "descartada"),
        ("Auxiliar de Sistemas de Irrigação", "", "descartada"),
        ("Civil Engineer Intern", "", "descartada"),
        ("Sales Account Executive - Data & AI", "", "descartada"),
        ("Vendedor Externo", "", "descartada"),
        ("Estágio", "", "descartada"),
        ("Analista de Suporte N2", "", "descartada"),
        ("Analista de Sistemas III", "", "descartada"),
        ("Data Architect (Databricks), Brazil", "", "descartada"),
        ("Java Backend Specialist, Brazil", "", "descartada"),
        ("Master AWS .Net Developer, Brazil", "", "descartada"),
        ("Desenvolvedor Sênior Java", "", "descartada"),
        ("Desenvolvedor Júnior/Pleno", "", "talvez"),
        ("RPA e Automação Junior, Pleno e Senior | Remoto", "", "talvez"),
        ("Business Intelligence Associate", "", "talvez"),
        ("Estágio", "Cursando Sistemas de Informação. Python.", "talvez"),
        ("Desenvolvedor PL SQL Júnior", "", "encaixa"),
        ("Desenvolvedor PL/SQL Júnior", "", "encaixa"),
        ("Estagiários de TI", "", "encaixa"),
        ("Estagiário(a) em Suporte Técnico N3", "", "encaixa"),
        ("Infosec Intern", "", "encaixa"),
        ("Estágio em AI Engineering", "", "encaixa"),
        ("Analista de Suporte Júnior", "", "encaixa"),
    ]

    def test_classes(self):
        for titulo, descricao, esperado in self.CASOS:
            with self.subTest(titulo=titulo, descricao=descricao):
                self.assertEqual(m.classificar(vaga(titulo, descricao=descricao))[0], esperado)


class AnosDeExperiencia(unittest.TestCase):
    CASOS = [
        ("Somos uma empresa com 30 anos de experiência no mercado.", 0),
        ("Com mais de 16 anos de experiência, atuamos com tecnologia", 0),
        ("Requisitos: de 3 a 5 anos de experiência", 3),
        ("Experiência de 3 a 5 anos com Java", 3),
        ("Mínimo 3 anos de experiência", 3),
        ("3-5 years of experience", 3),
        ("1 ano de experiência", 1),
        ("Sem exigência", 0),
    ]

    def test_anos(self):
        for descricao, esperado in self.CASOS:
            with self.subTest(descricao=descricao):
                self.assertEqual(m.anos_pedidos(m.norm(descricao)), esperado)

    def test_vaga_que_pede_demais_vai_para_talvez(self):
        self.assertEqual(m.classificar(vaga("Desenvolvedor Júnior", descricao="Mínimo 3 anos de experiência"))[0], "talvez")


class Regiao(unittest.TestCase):
    CASOS = [
        ("Greater São Paulo Area", True, True),
        ("Greater Porto Alegre Area", True, True),
        ("Canoas", True, True),
        ("Remoto, Brazil", True, True),
        ("Santa Maria, RS", False, True),
        ("Santa Maria, RS, Brazil", False, True),
        ("Santa Maria, Rio Grande do Sul, Brazil", False, True),
        ("Santa Maria", False, True),
        ("Agudo, RS", False, True),
        ("San Francisco Bay Area", True, False),
        ("Warsaw, Poland", True, False),
        ("Remote - Poland", True, False),
        ("Santa Maria, CA", True, False),
        ("Santa Maria, CA", False, False),
        ("Agudos, SP", False, False),
        ("Agudos, São Paulo, Brazil", False, False),
        ("Santa Maria da Vitória, BA", False, False),
        ("Santa Maria de Jetibá, ES", False, False),
        ("Porto Alegre, RS", False, False),
    ]

    def test_na_regiao(self):
        for local, remoto, esperado in self.CASOS:
            with self.subTest(local=local, remoto=remoto):
                self.assertEqual(m.na_regiao(vaga("Dev Jr", local, remoto)), esperado)

    def test_auxilio_home_office_nao_libera_presencial(self):
        self.assertFalse(m.na_regiao(vaga("Dev", "São Paulo, SP", descricao="VR, auxílio home office.")))

    def test_descricao_100_remoto_libera(self):
        self.assertTrue(m.na_regiao(vaga("Dev", "São Paulo, SP", descricao="Trabalho 100% remoto.")))


class Remota(unittest.TestCase):
    CASOS = [
        (("false", "Desenvolvedor Júnior - Remoto", "São Paulo, Brazil", True), True),
        (("false", "Data Engineer - Remote Work", "Goiânia, Brazil", True), True),
        (("false", "Desenvolvedor Júnior", "São Paulo, Brazil", True), False),
        (("true", "Fullstack Jr (Híbrido - Manaus)", "Manaus, AM", True), False),
        (("true", "Dev Jr", "Recife, PE", True), True),
        (("", "Dev Jr", "", True), True),
        (("", "Dev Jr", "", False), False),
    ]

    def test_e_remota(self):
        for args, esperado in self.CASOS:
            with self.subTest(args=args):
                self.assertEqual(m.e_remota(*args), esperado)


class IssuesDoGitHub(unittest.TestCase):
    def test_empresa_e_a_ultima_mencao(self):
        v = issue("[Remoto] Desenvolvedor(a) Java Júnior (Pagamentos via Pix) | Confidencial (vaga via Sylision)",
                  ["Júnior", "Estágio", "Remoto"])
        self.assertEqual(v["empresa"], "Sylision")
        self.assertTrue(v["titulo"].startswith("Desenvolvedor"))
        self.assertEqual(m.classificar(v)[0], "encaixa")

    def test_emoji_da_etiqueta_nao_vai_para_o_titulo(self):
        v = issue("Mobile Developer React Native (Pleno) na Coodesh", ["👨 Pleno", "Remoto"])
        self.assertEqual(v["titulo"], "Mobile Developer React Native (Pleno) na Coodesh")
        self.assertEqual(v["empresa"], "Coodesh")
        self.assertEqual(m.classificar(v)[0], "descartada")

    def test_nivel_vem_da_etiqueta(self):
        v = issue("[Remoto] Analista de Dados", ["Júnior"])
        self.assertEqual(v["titulo"], "Analista de Dados (Júnior)")
        self.assertEqual(m.classificar(v)[0], "encaixa")

    def test_colchete_de_nivel_nao_vira_local(self):
        v = issue("[Remoto] [Júnior] Dev Python @ Acme")
        self.assertEqual(v["local"], "Remoto")
        self.assertEqual(v["empresa"], "Acme")

    def test_so_entram_remotas(self):
        self.assertIsNone(issue("[Híbrido] Dev Jr"))
        self.assertIsNone(issue("Dev Jr", ["Híbrido"], "trabalho remoto"))
        self.assertIsNone(issue("[Joinville/SC] Dev Jr"))
        self.assertTrue(issue("Dev Jr", [], "Vaga 100% remoto")["remoto"])

    def test_remota_de_outro_pais_e_cortada(self):
        self.assertFalse(m.na_regiao(issue("[Remoto / Portugal] Dev Jr")))
        self.assertTrue(m.na_regiao(issue("[Remoto / Brasil] Dev Jr")))
        self.assertTrue(m.na_regiao(issue("[Remoto] Dev Jr")))


class ApontamentosDoCodex(unittest.TestCase):
    def test_duplicata_preserva_a_descricao_mais_completa(self):
        agora = datetime(2026, 11, 4, 12, tzinfo=m.FUSO)
        sem_descricao = vaga("Desenvolvedor Júnior", "Santa Maria, RS")
        com_requisitos = vaga("Desenvolvedor Júnior", "Santa Maria, RS", descricao="Mínimo 5 anos de experiência")
        saida = m.tratar([sem_descricao, com_requisitos], {}, agora)
        self.assertEqual(len(saida), 1)
        self.assertEqual(saida[0]["classe"], "talvez")

    def test_requisitos_cumulativos_contam_o_maior(self):
        desc = m.norm("1 ano de experiência com SQL e 5 anos de experiência com Python")
        self.assertEqual(m.anos_pedidos(desc), 5)

    def test_faixa_continua_contando_o_minimo(self):
        self.assertEqual(m.anos_pedidos(m.norm("de 1 a 5 anos de experiência")), 1)

    def test_hibrido_na_descricao_nao_libera_vaga_de_fora(self):
        desc = "Modelo híbrido, com dois dias de trabalho remoto por semana"
        self.assertFalse(m.na_regiao(vaga("Dev Jr", "São Paulo, SP", descricao=desc)))
        self.assertIsNone(issue("Dev Jr", [], desc))


if __name__ == "__main__":
    unittest.main()
