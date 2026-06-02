# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA2-21]
# =============================================================================
# tests/test_semantico.py — Testes do Analisador Semântico (Fase 3).
#
# Usa unittest (biblioteca padrão), portanto roda com:
#     python -m unittest tests.test_semantico
# e também é coletado pelo pytest.

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic import (
    prepararEntradaSemantica, construirTabelaSimbolos,
    verificarTipos, gerarArvoreAtribuida,
)
from codegen.assembly_gen import gerarAssembly


def _temp(src: str) -> str:
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    f.write(src)
    f.close()
    return f.name


def analisar(src: str):
    """Roda o pipeline semântico completo sobre um programa-fonte (string)."""
    caminho = _temp(src)
    try:
        entrada = prepararEntradaSemantica(caminho)
        if not entrada.ok:
            return entrada, None, []
        tabela, erros_decl = construirTabelaSimbolos(entrada.arvore)
        tipos, erros_tipo = verificarTipos(entrada.arvore, tabela)
        erros = [str(e) for e in (erros_decl + erros_tipo)]
        return entrada, tabela, erros
    finally:
        os.unlink(caminho)


# ---------------------------------------------------------------------------
# Comentários
# ---------------------------------------------------------------------------
class TestComentarios(unittest.TestCase):
    def test_comentario_linha_inteira(self):
        ent, _, _ = analisar("*{ comentario }*\nSTART\n(EXPR 1 1 +)\nEND\n")
        self.assertTrue(ent.ok)
        self.assertEqual(len(ent.comentarios), 1)

    def test_comentario_fim_de_linha(self):
        ent, _, _ = analisar("START\n(EXPR 1 1 +) *{ fim }*\nEND\n")
        self.assertTrue(ent.ok)
        self.assertEqual(len(ent.comentarios), 1)

    def test_comentario_entre_expressoes_e_multilinha(self):
        src = "START\n(EXPR 1 1 +)\n*{ comentario\n   multilinha }*\n(EXPR 2 2 +)\nEND\n"
        ent, _, _ = analisar(src)
        self.assertTrue(ent.ok)
        self.assertEqual(len(ent.comentarios), 1)
        # comentários não interferem: 2 statements reconhecidos
        self.assertEqual(len(ent.arvore.statements), 2)

    def test_comentario_nao_fechado_eh_erro_lexico(self):
        ent, _, _ = analisar("START *{ sem fim\n(EXPR 1 1 +)\nEND\n")
        self.assertFalse(ent.ok)
        self.assertTrue(ent.erros_lexicos)


# ---------------------------------------------------------------------------
# Tabela de símbolos / declaração e uso
# ---------------------------------------------------------------------------
class TestTabelaSimbolos(unittest.TestCase):
    def test_registra_tipo_e_linhas(self):
        src = "START\n(CMD_STORE 10 X)\n(CMD_STORE 3.14 Y)\n(CMD_LOAD X)\nEND\n"
        _, tab, erros = analisar(src)
        self.assertEqual(erros, [])
        self.assertEqual(tab.get("X").tipo, "int")
        self.assertEqual(tab.get("Y").tipo, "real")
        self.assertEqual(tab.get("X").linha_definicao, 2)
        self.assertIn(4, tab.get("X").linhas_uso)

    def test_uso_antes_da_definicao(self):
        _, _, erros = analisar("START\n(CMD_LOAD Z)\nEND\n")
        self.assertTrue(any("antes de ser definida" in e for e in erros))

    def test_uso_antes_da_definicao_em_expressao(self):
        _, _, erros = analisar("START\n(EXPR Q 1 +)\nEND\n")
        self.assertTrue(any("'Q'" in e and "antes" in e for e in erros))


# ---------------------------------------------------------------------------
# Inferência de tipos
# ---------------------------------------------------------------------------
class TestInferenciaTipos(unittest.TestCase):
    def test_int_e_real(self):
        _, tab, erros = analisar(
            "START\n(CMD_STORE 1 A)\n(CMD_STORE 1.5 B)\nEND\n")
        self.assertEqual(erros, [])
        self.assertEqual(tab.get("A").tipo, "int")
        self.assertEqual(tab.get("B").tipo, "real")

    def test_mistura_int_real_resulta_real(self):
        # B recebe (A + 2.0) com A:int -> real
        _, tab, erros = analisar(
            "START\n(CMD_STORE 2 A)\n(CMD_STORE (EXPR A 2.0 +) B)\nEND\n")
        self.assertEqual(erros, [])
        self.assertEqual(tab.get("B").tipo, "real")

    def test_aninhamento_profundo_valido(self):
        src = "START\n(EXPR (EXPR (EXPR (EXPR 1 2 +) 3 *) 4 -) 5 +)\nEND\n"
        _, _, erros = analisar(src)
        self.assertEqual(erros, [])


# ---------------------------------------------------------------------------
# Erros de tipos
# ---------------------------------------------------------------------------
class TestErrosTipo(unittest.TestCase):
    def test_divisao_inteira_com_real(self):
        _, _, erros = analisar("START\n(EXPR 7.5 2 /)\nEND\n")
        self.assertTrue(any("'/'" in e for e in erros))

    def test_resto_com_real(self):
        _, _, erros = analisar("START\n(EXPR 9.0 2 %)\nEND\n")
        self.assertTrue(any("'%'" in e for e in erros))

    def test_divisao_real_aceita_qualquer_numerico(self):
        _, _, erros = analisar("START\n(EXPR 7.5 2 |)\nEND\n")
        self.assertEqual(erros, [])

    def test_erro_de_tipo_em_expressao_aninhada(self):
        # (3.0 % 2) aninhado dentro de outra expressão
        _, _, erros = analisar("START\n(EXPR (EXPR 3.0 2 %) 4 +)\nEND\n")
        self.assertTrue(any("'%'" in e for e in erros))

    def test_redefinicao_incompativel(self):
        _, _, erros = analisar(
            "START\n(CMD_STORE 1 X)\n(CMD_STORE 2.5 X)\nEND\n")
        self.assertTrue(any("não pode receber" in e for e in erros))

    def test_alargamento_int_para_real_permitido(self):
        _, _, erros = analisar(
            "START\n(CMD_STORE 1.5 R)\n(CMD_STORE 2 R)\nEND\n")
        self.assertEqual(erros, [])


# ---------------------------------------------------------------------------
# Estruturas de controle
# ---------------------------------------------------------------------------
class TestControle(unittest.TestCase):
    def test_if_while_validos(self):
        src = ("START\n(CMD_STORE 0 C)\n"
               "(IF (C 0 >) [(CMD_STORE 1 C)])\n"
               "(WHILE (C 3 <) [(CMD_STORE (EXPR C 1 +) C)])\nEND\n")
        _, _, erros = analisar(src)
        self.assertEqual(erros, [])

    def test_erro_semantico_na_condicao_do_laco(self):
        # variável usada na condição do WHILE antes de definida
        _, _, erros = analisar(
            "START\n(WHILE (M 5 <) [(CMD_STORE 1 M)])\nEND\n")
        self.assertTrue(any("'M'" in e and "antes" in e for e in erros))

    def test_erro_de_tipo_no_corpo_do_laco(self):
        src = ("START\n(CMD_STORE 0 C)\n"
               "(WHILE (C 3 <) [(EXPR 1.5 2 %)])\nEND\n")
        _, _, erros = analisar(src)
        self.assertTrue(any("'%'" in e for e in erros))


# ---------------------------------------------------------------------------
# RES
# ---------------------------------------------------------------------------
class TestRes(unittest.TestCase):
    def test_res_valido(self):
        _, _, erros = analisar("START\n(EXPR 1 1 +)\n(CMD_RES 1)\nEND\n")
        self.assertEqual(erros, [])

    def test_res_fora_do_intervalo(self):
        _, _, erros = analisar("START\n(EXPR 1 1 +)\n(CMD_RES 9)\nEND\n")
        self.assertTrue(any("RES(9)" in e for e in erros))


# ---------------------------------------------------------------------------
# Erros léxicos e sintáticos (antes da etapa semântica)
# ---------------------------------------------------------------------------
class TestLexicoSintatico(unittest.TestCase):
    def test_erro_lexico_caractere_invalido(self):
        ent, _, _ = analisar("START\n(EXPR 1 1 &)\nEND\n")
        self.assertFalse(ent.ok)
        self.assertTrue(ent.erros_lexicos)

    def test_erro_sintatico_expressao_mal_formada(self):
        ent, _, _ = analisar("START\n(EXPR 1 +)\nEND\n")
        self.assertFalse(ent.ok)
        self.assertTrue(ent.erros_sintaticos)

    def test_programa_sem_start(self):
        ent, _, _ = analisar("(EXPR 1 1 +)\nEND\n")
        self.assertFalse(ent.ok)
        self.assertTrue(ent.erros_sintaticos)


# ---------------------------------------------------------------------------
# Casos extremos
# ---------------------------------------------------------------------------
class TestCasosExtremos(unittest.TestCase):
    def test_programa_vazio(self):
        ent, tab, erros = analisar("START\nEND\n")
        self.assertTrue(ent.ok)
        self.assertEqual(len(ent.arvore.statements), 0)
        self.assertEqual(erros, [])

    def test_programa_so_comentarios(self):
        ent, _, erros = analisar("*{ so comentario }*\nSTART\nEND\n")
        self.assertTrue(ent.ok)
        self.assertEqual(erros, [])


# ---------------------------------------------------------------------------
# Integração: Assembly só para programas válidos
# ---------------------------------------------------------------------------
class TestIntegracaoAssembly(unittest.TestCase):
    def test_programa_valido_gera_assembly(self):
        ent, tab, erros = analisar(
            "START\n(CMD_STORE 1 X)\n(EXPR X 2 +)\nEND\n")
        self.assertEqual(erros, [])
        tipos, _ = verificarTipos(ent.arvore, tab)
        atribuida = gerarArvoreAtribuida(ent.arvore, tab, tipos)
        asm = gerarAssembly(atribuida.programa)
        self.assertIn("_start:", asm)
        self.assertIn("VADD.F64", asm)

    def test_arvore_atribuida_tem_anotacoes_de_tipo(self):
        ent, tab, _ = analisar("START\n(EXPR 1 2 +)\nEND\n")
        tipos, _ = verificarTipos(ent.arvore, tab)
        atribuida = gerarArvoreAtribuida(ent.arvore, tab, tipos)
        d = atribuida.to_dict()
        binop = d["statements"][0]
        self.assertEqual(binop["tipo"], "int")
        self.assertEqual(binop["categoria"], "expressao_aritmetica")


if __name__ == "__main__":
    unittest.main(verbosity=2)
