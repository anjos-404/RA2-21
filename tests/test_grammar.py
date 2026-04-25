# tests/test_grammar.py - Testes da construcao da gramatica LL(1).

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from grammar.grammar import construirGramatica, Gramatica
from grammar.first_follow import first_of_sequence, EPSILON
from errors.errors import GrammarError


@pytest.fixture(scope="module")
def g():
    return construirGramatica()


class TestConstrucao:
    def test_construir_sem_excecao(self, g):
        assert isinstance(g, Gramatica)

    def test_simbolo_inicial(self, g):
        assert g.simbolo_inicial == "programa"

    def test_nao_terminais_essenciais(self, g):
        essenciais = {"programa", "stmts", "statement", "stmt_tail",
                      "operand", "operand_paren_tail", "arith_op",
                      "relational_op", "condition", "block"}
        assert essenciais.issubset(g.nao_terminais)

    def test_terminais_essenciais(self, g):
        essenciais = {"LPAREN", "RPAREN", "LBRACKET", "RBRACKET",
                      "START", "END", "EXPR", "CMD_RES", "CMD_LOAD",
                      "CMD_STORE", "IF", "IFELSE", "WHILE",
                      "INTEGER", "REAL", "MEM_NAME"}
        assert essenciais.issubset(g.terminais)


class TestFirst:
    def test_first_programa(self, g):
        assert g.first["programa"] == {"START"}

    def test_first_statement(self, g):
        assert g.first["statement"] == {"LPAREN"}

    def test_first_stmt_tail(self, g):
        esperado = {"EXPR", "CMD_RES", "CMD_LOAD", "CMD_STORE",
                    "IF", "IFELSE", "WHILE"}
        assert g.first["stmt_tail"] == esperado

    def test_first_operand(self, g):
        esperado = {"INTEGER", "REAL", "MEM_NAME", "LPAREN"}
        assert g.first["operand"] == esperado

    def test_first_operand_paren_tail(self, g):
        assert g.first["operand_paren_tail"] == {"EXPR", "CMD_LOAD"}

    def test_first_arith_op(self, g):
        esperado = {"PLUS", "MINUS", "MUL", "DIV_REAL",
                    "DIV_INT", "MOD", "POW"}
        assert g.first["arith_op"] == esperado

    def test_first_relational_op(self, g):
        esperado = {"GT", "LT", "GTE", "LTE", "EQ", "NEQ"}
        assert g.first["relational_op"] == esperado

    def test_first_stmts_contem_epsilon(self, g):
        assert EPSILON in g.first["stmts"]

    def test_first_block(self, g):
        assert g.first["block"] == {"LBRACKET"}

    def test_first_condition(self, g):
        assert g.first["condition"] == {"LPAREN"}


class TestFollow:
    def test_follow_programa_contem_eof(self, g):
        assert "EOF" in g.follow["programa"]

    def test_follow_stmts_contem_end(self, g):
        # stmts vem antes de END no programa
        assert "END" in g.follow["stmts"]

    def test_follow_stmts_contem_rbracket(self, g):
        # stmts vem antes de ] no block
        assert "RBRACKET" in g.follow["stmts"]

    def test_follow_arith_op_contem_rparen(self, g):
        assert "RPAREN" in g.follow["arith_op"]

    def test_follow_block(self, g):
        # block pode ser seguido de outro block, RPAREN (em stmt_tail)
        assert "RPAREN" in g.follow["block"]


class TestLL1:
    def test_sem_conflitos_firstfirst(self, g):
        """Nenhuma producao da mesma cabeca compartilha FIRST."""
        from collections import defaultdict
        por_nt = defaultdict(list)
        for p in g.producoes:
            por_nt[p.cabeca].append(p)
        for nt, prods in por_nt.items():
            firsts = [first_of_sequence(p.corpo, g.first) for p in prods]
            for i in range(len(firsts)):
                for j in range(i + 1, len(firsts)):
                    inter = (firsts[i] - {EPSILON}) & (firsts[j] - {EPSILON})
                    assert not inter, (
                        f"Conflito FIRST/FIRST em {nt}: "
                        f"'{prods[i]}' vs '{prods[j]}' com {inter}"
                    )

    def test_sem_conflitos_firstfollow(self, g):
        """Se A deriva epsilon, FIRST das outras nao intersecta FOLLOW(A)."""
        from collections import defaultdict
        por_nt = defaultdict(list)
        for p in g.producoes:
            por_nt[p.cabeca].append(p)
        for nt, prods in por_nt.items():
            firsts = [first_of_sequence(p.corpo, g.first) for p in prods]
            for i, fi in enumerate(firsts):
                if EPSILON in fi:
                    for j, fj in enumerate(firsts):
                        if i == j:
                            continue
                        inter = (fj - {EPSILON}) & g.follow[nt]
                        assert not inter, (
                            f"Conflito FIRST/FOLLOW em {nt}: {inter}"
                        )

    def test_tabela_tem_entradas(self, g):
        assert len(g.tabela) > 20

    def test_tabela_statement_lparen(self, g):
        assert ("statement", "LPAREN") in g.tabela

    def test_tabela_stmt_tail_expr(self, g):
        assert ("stmt_tail", "EXPR") in g.tabela

    def test_tabela_stmt_tail_cmd_store(self, g):
        assert ("stmt_tail", "CMD_STORE") in g.tabela

    def test_tabela_operand_integer(self, g):
        assert ("operand", "INTEGER") in g.tabela

    def test_cada_producao_determina_decisao_unica(self, g):
        """Cada entrada na tabela e uma unica producao (determinismo)."""
        for chave, prod in g.tabela.items():
            assert prod is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
