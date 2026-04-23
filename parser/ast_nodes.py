# parser/ast_nodes.py — Parte 4
# Definição dos nós da AST (Abstract Syntax Tree) do compilador RPN.

from dataclasses import dataclass, field
from typing import Any


class ASTNode:
    """Classe base para todos os nós da AST."""
    pass


@dataclass
class ProgramNode(ASTNode):
    """Nó raiz do programa — contém lista de statements."""
    statements: list[ASTNode]


@dataclass
class BinOpNode(ASTNode):
    """Operação binária aritmética."""
    op: str                # '+', '-', '*', '|', '/', '%', '^'
    left: ASTNode
    right: ASTNode


@dataclass
class NumberNode(ASTNode):
    """Literal numérico (inteiro ou real)."""
    value: int | float
    is_real: bool          # True = REAL (IEEE 754 double), False = INTEGER


@dataclass
class MemReadNode(ASTNode):
    """Leitura de memória: (MEM_NAME)."""
    name: str              # nome da memória (ex: "X", "CONTADOR")


@dataclass
class MemWriteNode(ASTNode):
    """Escrita em memória: (V MEM_NAME)."""
    name: str
    value: ASTNode


@dataclass
class ResNode(ASTNode):
    """Referência a resultado anterior: (N RES)."""
    n: int                 # N linhas anteriores


@dataclass
class PrintNode(ASTNode):
    """Comando PRINT: (V PRINT)."""
    value: ASTNode


@dataclass
class ConditionNode(ASTNode):
    """Condição relacional: (A B relop)."""
    op: str                # '>', '<', '>=', '<=', '==', '!='
    left: ASTNode
    right: ASTNode


@dataclass
class IfNode(ASTNode):
    """Estrutura IF ou IFELSE."""
    condition: ConditionNode
    then_block: list[ASTNode]
    else_block: list[ASTNode] = field(default_factory=list)


@dataclass
class WhileNode(ASTNode):
    """Estrutura WHILE."""
    condition: ConditionNode
    body: list[ASTNode]


@dataclass
class BlockNode(ASTNode):
    """Bloco de statements entre [ ]."""
    statements: list[ASTNode]
