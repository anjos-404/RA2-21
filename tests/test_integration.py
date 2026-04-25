# tests/test_integration.py - Testes de integracao end-to-end.

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from lexer.ler_tokens import lerTokens
from grammar.grammar import construirGramatica
from parser.parser import parsear
from codegen.ast_builder import gerarArvore
from codegen.assembly_gen import gerarAssembly
from parser.ast_nodes import (
    ProgramNode, BinOpNode, NumberNode,
    MemReadNode, MemWriteNode, ResNode,
    IfNode, WhileNode, ConditionNode
)


@pytest.fixture(scope="module")
def gramatica():
    return construirGramatica()


def compilar(code: str, gramatica) -> tuple:
    """Pipeline completo: codigo -> (AST, assembly)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        path = f.name
    try:
        tokens = lerTokens(path)
        derivacao = parsear(tokens, gramatica)
        ast = gerarArvore(derivacao)
        asm = gerarAssembly(ast)
        return ast, asm
    finally:
        os.unlink(path)


class TestPipelineCompleto:
    def test_soma_simples(self, gramatica):
        ast, asm = compilar("START\n(EXPR 3 4 +)\nEND\n", gramatica)
        assert isinstance(ast, ProgramNode)
        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, BinOpNode)
        assert stmt.op == "+"
        assert isinstance(stmt.left, NumberNode)
        assert stmt.left.value == 3

    def test_todas_operacoes_geram_ast(self, gramatica):
        code = """START
(EXPR 1 2 +)
(EXPR 1 2 -)
(EXPR 1 2 *)
(EXPR 1 2 /)
(EXPR 1 2 %)
(EXPR 1.0 2.0 |)
(EXPR 2 3 ^)
END
"""
        ast, asm = compilar(code, gramatica)
        assert len(ast.statements) == 7
        ops = [s.op for s in ast.statements if isinstance(s, BinOpNode)]
        assert ops == ["+", "-", "*", "/", "%", "|", "^"]

    def test_aninhamento(self, gramatica):
        ast, asm = compilar(
            "START\n(EXPR (EXPR 1 2 +) (EXPR 3 4 *) -)\nEND\n", gramatica
        )
        top = ast.statements[0]
        assert isinstance(top, BinOpNode)
        assert top.op == "-"
        assert isinstance(top.left, BinOpNode)
        assert top.left.op == "+"
        assert isinstance(top.right, BinOpNode)
        assert top.right.op == "*"

    def test_mem_store_load(self, gramatica):
        code = """START
(CMD_STORE 42 X)
(CMD_LOAD X)
END
"""
        ast, asm = compilar(code, gramatica)
        assert len(ast.statements) == 2
        assert isinstance(ast.statements[0], MemWriteNode)
        assert ast.statements[0].name == "X"
        assert isinstance(ast.statements[1], MemReadNode)
        assert ast.statements[1].name == "X"

    def test_cmd_res(self, gramatica):
        code = "START\n(EXPR 1 2 +)\n(CMD_RES 1)\nEND\n"
        ast, asm = compilar(code, gramatica)
        res_node = ast.statements[1]
        assert isinstance(res_node, ResNode)
        assert res_node.n == 1

    def test_if_gera_ifnode_com_else_vazio(self, gramatica):
        code = """START
(CMD_STORE 1 X)
(IF (X 0 >) [(CMD_STORE 2 Y)])
END
"""
        ast, asm = compilar(code, gramatica)
        if_node = ast.statements[1]
        assert isinstance(if_node, IfNode)
        assert if_node.else_block == []
        assert len(if_node.then_block) == 1

    def test_ifelse_gera_else_preenchido(self, gramatica):
        code = """START
(CMD_STORE 1 X)
(IFELSE (X 0 >) [(CMD_STORE 2 Y)] [(CMD_STORE 3 Y)])
END
"""
        ast, asm = compilar(code, gramatica)
        if_node = ast.statements[1]
        assert isinstance(if_node, IfNode)
        assert len(if_node.then_block) == 1
        assert len(if_node.else_block) == 1

    def test_while_gera_whilenode(self, gramatica):
        code = """START
(CMD_STORE 0 I)
(WHILE (I 5 <) [(CMD_STORE (EXPR I 1 +) I)])
END
"""
        ast, asm = compilar(code, gramatica)
        w = ast.statements[1]
        assert isinstance(w, WhileNode)
        assert isinstance(w.condition, ConditionNode)
        assert w.condition.op == "<"

    def test_asm_contem_header(self, gramatica):
        ast, asm = compilar("START\n(EXPR 1 2 +)\nEND\n", gramatica)
        assert "_start:" in asm
        assert ".text" in asm

    def test_asm_usa_vfp(self, gramatica):
        ast, asm = compilar("START\n(EXPR 1.5 2.5 +)\nEND\n", gramatica)
        assert "VADD.F64" in asm

    def test_asm_gera_mem_label(self, gramatica):
        ast, asm = compilar("START\n(CMD_STORE 1 X)\nEND\n", gramatica)
        assert "mem_X" in asm


class TestArquivosDeTeste:
    """Testes que compilam os arquivos .txt em tests/."""

    @pytest.mark.parametrize("arquivo", ["teste1.txt", "teste2.txt", "teste3.txt"])
    def test_compila_sem_erros(self, gramatica, arquivo):
        caminho = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), arquivo
        )
        tokens = lerTokens(caminho)
        derivacao = parsear(tokens, gramatica)
        ast = gerarArvore(derivacao)
        asm = gerarAssembly(ast)
        assert isinstance(ast, ProgramNode)
        assert len(ast.statements) > 0
        assert "_start:" in asm


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
