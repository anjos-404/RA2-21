# tests/test_parser.py — Testes da Parte 2
# Testa parsear() com entradas válidas e inválidas.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from lexer.ler_tokens import lerTokens
from grammar.grammar import construirGramatica
from parser.parser import parsear, parsear_com_recuperacao, DerivacaoNode


@pytest.fixture
def gramatica():
    return construirGramatica()


def _tokens_from_string(code: str) -> list:
    """Helper: cria um arquivo temporário com o código e gera tokens."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(code)
        f.flush()
        path = f.name
    try:
        return lerTokens(path)
    finally:
        os.unlink(path)


class TestEntradasValidas:
    """Testes com entradas sintaticamente válidas."""

    def test_expressao_simples(self, gramatica):
        """(START) (3.14 2.0 +) (END) → sem erro."""
        tokens = _tokens_from_string("(START)\n(3.14 2.0 +)\n(END)")
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)
        assert resultado.simbolo == "programa"

    def test_expressao_aninhada(self, gramatica):
        """Expressão aninhada válida."""
        tokens = _tokens_from_string("(START)\n((3 4 +) (2 3 *) |)\n(END)")
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_comando_res(self, gramatica):
        """(1 RES) válido."""
        tokens = _tokens_from_string("(START)\n(3 4 +)\n(1 RES)\n(END)")
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_mem_escrita(self, gramatica):
        """(10 X) - escrita em memória."""
        tokens = _tokens_from_string("(START)\n(10 X)\n(END)")
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_mem_leitura(self, gramatica):
        """(X) - leitura de memória."""
        tokens = _tokens_from_string("(START)\n(42 X)\n(X)\n(END)")
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_if_simples(self, gramatica):
        """IF simples válido."""
        code = "(START)\n(42 X)\n((X) 0 > [(1 RES)] IF)\n(END)"
        tokens = _tokens_from_string(code)
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_ifelse(self, gramatica):
        """IFELSE válido."""
        code = "(START)\n(5 X)\n((X) 10 < [(X)] [(0 Y)] IFELSE)\n(END)"
        tokens = _tokens_from_string(code)
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_while(self, gramatica):
        """WHILE válido."""
        code = "(START)\n(0 CONT)\n((CONT) 5 < [((CONT) 1 + CONT)] WHILE)\n(END)"
        tokens = _tokens_from_string(code)
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_programa_vazio(self, gramatica):
        """(START) (END) sem statements — válido."""
        tokens = _tokens_from_string("(START)\n(END)")
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)

    def test_todos_operadores(self, gramatica):
        """Todos os operadores aritméticos."""
        code = "(START)\n(3 4 +)\n(10 3 -)\n(2 5 *)\n(7.5 2.0 |)\n(10 3 /)\n(10 3 %)\n(2 8 ^)\n(END)"
        tokens = _tokens_from_string(code)
        resultado = parsear(tokens, gramatica)
        assert isinstance(resultado, DerivacaoNode)


class TestEntradasInvalidas:
    """Testes com entradas sintaticamente inválidas."""

    def test_sem_start(self, gramatica):
        """Sem (START) - erro."""
        with pytest.raises(SyntaxError):
            tokens = _tokens_from_string("(3.14 2.0 +)\n(END)")
            parsear(tokens, gramatica)

    def test_sem_end(self, gramatica):
        """Sem (END) - erro."""
        with pytest.raises(SyntaxError):
            tokens = _tokens_from_string("(START)\n(3.14 2.0 +)")
            parsear(tokens, gramatica)


class TestRecuperacaoErros:
    """Testes da recuperação de erros."""

    def test_recuperacao_erro_basico(self, gramatica):
        """Recuperação de erro retorna lista de erros."""
        tokens = _tokens_from_string("(3.14 2.0 +)\n(END)")
        resultado, erros = parsear_com_recuperacao(tokens, gramatica)
        assert len(erros) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
