# tests/test_lexer.py - Testes do analisador lexico.

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from lexer.ler_tokens import lerTokens
from lexer.token import TokenType
from errors.errors import LexicalError


def _tokenize(code: str):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        path = f.name
    try:
        return lerTokens(path)
    finally:
        os.unlink(path)


class TestLexerBasico:
    def test_parenteses(self):
        tokens = _tokenize("()")
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN

    def test_colchetes(self):
        tokens = _tokenize("[]")
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET

    def test_inteiro(self):
        tokens = _tokenize("42")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 42

    def test_real(self):
        tokens = _tokenize("3.14")
        assert tokens[0].type == TokenType.REAL
        assert tokens[0].value == 3.14

    def test_mem_name(self):
        tokens = _tokenize("VALOR")
        assert tokens[0].type == TokenType.MEM_NAME
        assert tokens[0].value == "VALOR"


class TestKeywords:
    @pytest.mark.parametrize("palavra,tipo", [
        ("START",     TokenType.START),
        ("END",       TokenType.END),
        ("EXPR",      TokenType.EXPR),
        ("CMD_RES",   TokenType.CMD_RES),
        ("CMD_LOAD",  TokenType.CMD_LOAD),
        ("CMD_STORE", TokenType.CMD_STORE),
        ("IF",        TokenType.IF),
        ("IFELSE",    TokenType.IFELSE),
        ("WHILE",     TokenType.WHILE),
    ])
    def test_keyword(self, palavra, tipo):
        tokens = _tokenize(palavra)
        assert tokens[0].type == tipo


class TestOperadores:
    @pytest.mark.parametrize("op,tipo", [
        ("+",  TokenType.PLUS),
        ("-",  TokenType.MINUS),
        ("*",  TokenType.MUL),
        ("|",  TokenType.DIV_REAL),
        ("/",  TokenType.DIV_INT),
        ("%",  TokenType.MOD),
        ("^",  TokenType.POW),
        (">",  TokenType.GT),
        ("<",  TokenType.LT),
        (">=", TokenType.GTE),
        ("<=", TokenType.LTE),
        ("==", TokenType.EQ),
        ("!=", TokenType.NEQ),
    ])
    def test_operador(self, op, tipo):
        tokens = _tokenize(op)
        assert tokens[0].type == tipo


class TestErros:
    def test_caractere_invalido(self):
        with pytest.raises(LexicalError):
            _tokenize("&")

    def test_numero_malformado(self):
        with pytest.raises(LexicalError):
            _tokenize("3.14.5")

    def test_identificador_minusculo(self):
        with pytest.raises(LexicalError):
            _tokenize("variavel")


class TestProgramaCompleto:
    def test_tokenizacao_programa_valido(self):
        code = "START\n(EXPR 3 4 +)\nEND\n"
        tokens = _tokenize(code)
        # START, LPAREN, EXPR, INTEGER, INTEGER, PLUS, RPAREN, END, EOF
        tipos = [t.type for t in tokens]
        assert tipos == [
            TokenType.START, TokenType.LPAREN, TokenType.EXPR,
            TokenType.INTEGER, TokenType.INTEGER, TokenType.PLUS,
            TokenType.RPAREN, TokenType.END, TokenType.EOF
        ]

    def test_comentarios_ignorados(self):
        tokens = _tokenize("# comentario\nSTART\nEND\n")
        assert tokens[0].type == TokenType.START

    def test_eof_sempre_presente(self):
        tokens = _tokenize("")
        assert tokens[-1].type == TokenType.EOF


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
