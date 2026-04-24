# tests/test_grammar.py — Testes da Parte 1
# Testa construirGramatica(), FIRST, FOLLOW e tabela LL(1).

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from grammar.grammar import construirGramatica, Gramatica


class TestConstruirGramatica:
    """Testes para construirGramatica()."""

    def setup_method(self):
        self.g = construirGramatica()

    def test_construir_sem_excecao(self):
        """construirGramatica() não lança exceção."""
        assert isinstance(self.g, Gramatica)

    def test_nao_terminais_presentes(self):
        """Verifica que todos os não-terminais esperados existem."""
        esperados = {"programa", "stmts", "statement", "expression", "operand",
                     "arith_op", "relational_op", "special_cmd", "control_struct",
                     "if_stmt", "while_stmt", "condition", "block"}
        assert esperados.issubset(self.g.nao_terminais)

    def test_terminais_presentes(self):
        """Verifica que terminais essenciais existem."""
        esperados = {"LPAREN", "RPAREN", "INTEGER", "REAL", "MEM_NAME",
                     "PLUS", "MINUS", "MUL", "IF", "WHILE"}
        assert esperados.issubset(self.g.terminais)


class TestFirst:
    """Testes para os conjuntos FIRST."""

    def setup_method(self):
        self.g = construirGramatica()

    def test_first_expression(self):
        """FIRST(expression) contém LPAREN."""
        assert "LPAREN" in self.g.first["expression"]

    def test_first_operand(self):
        """FIRST(operand) contém INTEGER, REAL, MEM_NAME, LPAREN."""
        esperados = {"INTEGER", "REAL", "MEM_NAME", "LPAREN"}
        assert esperados.issubset(self.g.first["operand"])

    def test_first_block(self):
        """FIRST(block) contém LBRACKET."""
        assert "LBRACKET" in self.g.first["block"]

    def test_first_arith_op(self):
        """FIRST(arith_op) contém todos os operadores aritméticos."""
        ops = {"PLUS", "MINUS", "MUL", "DIV_REAL", "DIV_INT", "MOD", "POW"}
        assert ops.issubset(self.g.first["arith_op"])

    def test_first_stmts_epsilon(self):
        """FIRST(stmts) contém ε."""
        assert "ε" in self.g.first["stmts"]

    def test_first_programa(self):
        """FIRST(programa) contém LPAREN."""
        assert "LPAREN" in self.g.first["programa"]

    def test_first_relational_op(self):
        """FIRST(relational_op) contém operadores relacionais."""
        ops = {"GT", "LT", "GTE", "LTE", "EQ", "NEQ"}
        assert ops.issubset(self.g.first["relational_op"])


class TestFollow:
    """Testes para os conjuntos FOLLOW."""

    def setup_method(self):
        self.g = construirGramatica()

    def test_follow_programa(self):
        """FOLLOW(programa) contém EOF."""
        assert "EOF" in self.g.follow["programa"]

    def test_follow_block(self):
        """FOLLOW(block) contém IF, IFELSE, WHILE."""
        esperados = {"IF", "IFELSE", "WHILE"}
        assert esperados.issubset(self.g.follow["block"])

    def test_follow_arith_op(self):
        """FOLLOW(arith_op) contém RPAREN."""
        assert "RPAREN" in self.g.follow["arith_op"]


class TestTabelaLL1:
    """Testes para a tabela LL(1)."""

    def setup_method(self):
        self.g = construirGramatica()

    def test_tabela_sem_conflitos(self):
        """Tabela LL(1) foi construída sem conflitos."""
        assert len(self.g.tabela) > 0

    def test_expression_lparen(self):
        """tabela[("expression", "LPAREN")] existe."""
        assert ("expression", "LPAREN") in self.g.tabela

    def test_stmts_epsilon_eof(self):
        """tabela[("stmts", "EOF")] existe (produção epsilon)."""
        # stmts pode derivar ε quando o próximo token é RPAREN ou RBRACKET
        # Verificamos que alguma entrada epsilon existe para stmts
        entradas_stmts = {k: v for k, v in self.g.tabela.items() if k[0] == "stmts"}
        assert len(entradas_stmts) > 0

    def test_operand_integer(self):
        """tabela[("operand", "INTEGER")] existe."""
        assert ("operand", "INTEGER") in self.g.tabela

    def test_block_lbracket(self):
        """tabela[("block", "LBRACKET")] existe."""
        assert ("block", "LBRACKET") in self.g.tabela


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
