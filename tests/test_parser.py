# tests/test_parser.py - Testes do parser LL(1) tabular.

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from lexer.ler_tokens import lerTokens
from grammar.grammar import construirGramatica
from parser.parser import parsear, parsear_com_recuperacao, DerivacaoNode
from errors.errors import RPNSyntaxError


@pytest.fixture(scope="module")
def gramatica():
    return construirGramatica()


def _parse_string(code: str, gramatica):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        path = f.name
    try:
        tokens = lerTokens(path)
        return parsear(tokens, gramatica)
    finally:
        os.unlink(path)


class TestEntradasValidas:
    def test_programa_vazio(self, gramatica):
        r = _parse_string("START\nEND\n", gramatica)
        assert isinstance(r, DerivacaoNode)
        assert r.simbolo == "programa"

    def test_expressao_simples(self, gramatica):
        r = _parse_string("START\n(EXPR 3.14 2.0 +)\nEND\n", gramatica)
        assert r.simbolo == "programa"

    def test_todas_operacoes_aritmeticas(self, gramatica):
        code = """START
(EXPR 3 2 +)
(EXPR 5 1 -)
(EXPR 4 2 *)
(EXPR 10 3 /)
(EXPR 10 3 %)
(EXPR 10.0 4.0 |)
(EXPR 2 8 ^)
END
"""
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_expressao_aninhada(self, gramatica):
        code = "START\n(EXPR (EXPR 3 4 +) (EXPR 2 3 *) |)\nEND\n"
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_aninhamento_profundo(self, gramatica):
        code = "START\n(EXPR (EXPR (EXPR 1 2 +) 3 *) 4 -)\nEND\n"
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_cmd_res(self, gramatica):
        code = "START\n(EXPR 1 2 +)\n(CMD_RES 1)\nEND\n"
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_cmd_store(self, gramatica):
        r = _parse_string("START\n(CMD_STORE 42 X)\nEND\n", gramatica)
        assert r.simbolo == "programa"

    def test_cmd_load(self, gramatica):
        code = "START\n(CMD_STORE 42 X)\n(CMD_LOAD X)\nEND\n"
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_cmd_store_com_expressao(self, gramatica):
        code = "START\n(CMD_STORE (EXPR 3 4 +) X)\nEND\n"
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_if_simples(self, gramatica):
        code = "START\n(CMD_STORE 5 X)\n(IF (X 0 >) [(CMD_STORE 1 Y)])\nEND\n"
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_ifelse(self, gramatica):
        code = """START
(CMD_STORE 5 X)
(IFELSE (X 0 >) [(CMD_STORE 1 Y)] [(CMD_STORE 0 Y)])
END
"""
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_while(self, gramatica):
        code = """START
(CMD_STORE 0 I)
(WHILE (I 5 <) [(CMD_STORE (EXPR I 1 +) I)])
END
"""
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_while_com_multiplos_statements_corpo(self, gramatica):
        code = """START
(CMD_STORE 0 A)
(CMD_STORE 0 B)
(WHILE (A 3 <) [(CMD_STORE (EXPR A 1 +) A) (CMD_STORE (EXPR B 2 +) B)])
END
"""
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_bloco_vazio_nao_permitido(self, gramatica):
        # Bloco vazio [] nao faz sentido semantico mas eh sintaticamente valido
        # pela regra: block -> LBRACKET stmts RBRACKET com stmts -> epsilon
        code = "START\n(CMD_STORE 1 X)\n(IF (X 0 >) [])\nEND\n"
        r = _parse_string(code, gramatica)
        assert r.simbolo == "programa"

    def test_todos_operadores_relacionais(self, gramatica):
        for op in [">", "<", ">=", "<=", "==", "!="]:
            code = f"START\n(CMD_STORE 1 X)\n(IF (X 0 {op}) [(CMD_STORE 2 Y)])\nEND\n"
            r = _parse_string(code, gramatica)
            assert r.simbolo == "programa"


class TestEntradasInvalidas:
    def test_falta_start(self, gramatica):
        with pytest.raises(RPNSyntaxError):
            _parse_string("(EXPR 3 4 +)\nEND\n", gramatica)

    def test_falta_end(self, gramatica):
        with pytest.raises(RPNSyntaxError):
            _parse_string("START\n(EXPR 3 4 +)\n", gramatica)

    def test_sintaxe_antiga_sem_marcador(self, gramatica):
        """A sintaxe antiga sem marcador deve falhar no parser LL(1)."""
        with pytest.raises(RPNSyntaxError):
            _parse_string("START\n(3 4 +)\nEND\n", gramatica)

    def test_operador_invalido_no_expr(self, gramatica):
        with pytest.raises(RPNSyntaxError):
            _parse_string("START\n(EXPR 3 4 >)\nEND\n", gramatica)

    def test_parenteses_nao_fechados(self, gramatica):
        with pytest.raises(RPNSyntaxError):
            _parse_string("START\n(EXPR 3 4 +\nEND\n", gramatica)

    def test_falta_operando(self, gramatica):
        with pytest.raises(RPNSyntaxError):
            _parse_string("START\n(EXPR 3 +)\nEND\n", gramatica)

    def test_if_sem_condicao(self, gramatica):
        with pytest.raises(RPNSyntaxError):
            _parse_string("START\n(IF [(CMD_STORE 1 X)])\nEND\n", gramatica)

    def test_tokens_apos_end(self, gramatica):
        with pytest.raises(RPNSyntaxError):
            _parse_string("START\nEND\n(EXPR 1 1 +)\n", gramatica)


class TestRecuperacao:
    def test_parsear_com_recuperacao_valida(self, gramatica):
        r, erros = parsear_com_recuperacao(
            lerTokens_from_string("START\nEND\n"), gramatica
        )
        assert r is not None
        assert erros == []

    def test_parsear_com_recuperacao_invalida(self, gramatica):
        r, erros = parsear_com_recuperacao(
            lerTokens_from_string("START\n(3 4 +)\nEND\n"), gramatica
        )
        assert r is None
        assert len(erros) == 1


def lerTokens_from_string(s: str):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(s)
        path = f.name
    try:
        return lerTokens(path)
    finally:
        os.unlink(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
