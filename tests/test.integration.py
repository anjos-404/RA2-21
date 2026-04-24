# tests/test_integration.py — Testes End-to-End
# Testa o pipeline completo: tokens → gramática → parser → AST → assembly.

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from lexer.ler_tokens import lerTokens
from grammar.grammar import construirGramatica
from parser.parser import parsear
from codegen.ast_builder import gerarArvore
from codegen.assembly_gen import gerarAssembly
from parser.ast_nodes import *


@pytest.fixture
def gramatica():
    return construirGramatica()


def _get_test_path(nome: str) -> str:
    """Retorna caminho absoluto para arquivo de teste."""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nome)


class TestPipelineCompleto:
    """Testa o pipeline end-to-end com os 3 arquivos de teste."""

    def test_teste1_pipeline(self, gramatica):
        """teste1.txt - tokens - parse - AST - Assembly."""
        path = _get_test_path("teste1.txt")
        tokens = lerTokens(path)
        assert len(tokens) > 10

        derivacao = parsear(tokens, gramatica)
        arvore = gerarArvore(derivacao)

        assert isinstance(arvore, ProgramNode)
        assert len(arvore.statements) > 0

        asm = gerarAssembly(arvore)
        assert ".global _start" in asm
        assert "_start:" in asm

    def test_teste2_pipeline(self, gramatica):
        """teste2.txt - inclui WHILE e IFELSE."""
        path = _get_test_path("teste2.txt")
        tokens = lerTokens(path)
        derivacao = parsear(tokens, gramatica)
        arvore = gerarArvore(derivacao)

        assert isinstance(arvore, ProgramNode)

        # Verificar que existem nós de controle na AST
        tipos = [type(s).__name__ for s in arvore.statements]
        assert "WhileNode" in tipos or "IfNode" in tipos

        asm = gerarAssembly(arvore)
        assert "LOOP_" in asm or "ELSE_" in asm

    def test_teste3_pipeline(self, gramatica):
        """teste3.txt - expressões aninhadas profundas."""
        path = _get_test_path("teste3.txt")
        tokens = lerTokens(path)
        derivacao = parsear(tokens, gramatica)
        arvore = gerarArvore(derivacao)

        assert isinstance(arvore, ProgramNode)
        assert len(arvore.statements) >= 10

        asm = gerarAssembly(arvore)
        assert len(asm) > 100


class TestAST:
    """Testa a geração da AST."""

    def test_binop_node(self, gramatica):
        """Expressão simples gera BinOpNode."""
        import tempfile
        code = "(START)\n(3 4 +)\n(END)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(code)
            path = f.name

        try:
            tokens = lerTokens(path)
            derivacao = parsear(tokens, gramatica)
            arvore = gerarArvore(derivacao)

            assert len(arvore.statements) == 1
            stmt = arvore.statements[0]
            assert isinstance(stmt, BinOpNode)
            assert stmt.op == "+"
            assert isinstance(stmt.left, NumberNode)
            assert stmt.left.value == 3
            assert isinstance(stmt.right, NumberNode)
            assert stmt.right.value == 4
        finally:
            os.unlink(path)

    def test_mem_write_node(self, gramatica):
        """(42 X) gera MemWriteNode."""
        import tempfile
        code = "(START)\n(42 X)\n(END)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(code)
            path = f.name

        try:
            tokens = lerTokens(path)
            derivacao = parsear(tokens, gramatica)
            arvore = gerarArvore(derivacao)

            stmt = arvore.statements[0]
            assert isinstance(stmt, MemWriteNode)
            assert stmt.name == "X"
        finally:
            os.unlink(path)


class TestAssembly:
    """Testa a geração de Assembly."""

    def test_assembly_estrutura(self, gramatica):
        """Assembly gerado tem estrutura correta."""
        import tempfile
        code = "(START)\n(3 4 +)\n(END)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(code)
            path = f.name

        try:
            tokens = lerTokens(path)
            derivacao = parsear(tokens, gramatica)
            arvore = gerarArvore(derivacao)
            asm = gerarAssembly(arvore)

            assert ".global _start" in asm
            assert "_start:" in asm
            assert "_halt:" in asm
        finally:
            os.unlink(path)

    def test_assembly_operacoes(self, gramatica):
        """Assembly contém instruções para operações."""
        import tempfile
        code = "(START)\n(3 4 +)\n(10 3 -)\n(END)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(code)
            path = f.name

        try:
            tokens = lerTokens(path)
            derivacao = parsear(tokens, gramatica)
            arvore = gerarArvore(derivacao)
            asm = gerarAssembly(arvore)

            assert "ADD" in asm
            assert "SUB" in asm
        finally:
            os.unlink(path)

    def test_assembly_mem(self, gramatica):
        """Assembly contém seção .data para memórias."""
        import tempfile
        code = "(START)\n(42 X)\n(X)\n(END)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(code)
            path = f.name

        try:
            tokens = lerTokens(path)
            derivacao = parsear(tokens, gramatica)
            arvore = gerarArvore(derivacao)
            asm = gerarAssembly(arvore)

            assert ".data" in asm
            assert "mem_X" in asm
        finally:
            os.unlink(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
