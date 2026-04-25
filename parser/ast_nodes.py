# parser/ast_nodes.py — Nós da Árvore Sintática Abstrata (AST).
# A AST é a representação semântica do programa, limpa da derivação gramatical.

from dataclasses import dataclass, field
from typing import Any


class ASTNode:
    """Classe base de todos os nós da AST."""
    pass


@dataclass
class ProgramNode(ASTNode):
    """Raiz do programa — lista de statements."""
    statements: list[ASTNode]


@dataclass
class BinOpNode(ASTNode):
    """Operação binária aritmética."""
    op: str                # '+', '-', '*', '|', '/', '%', '^'
    left: ASTNode
    right: ASTNode


@dataclass
class NumberNode(ASTNode):
    """Literal numérico."""
    value: int | float
    is_real: bool          # True = REAL (IEEE 754), False = INTEGER


@dataclass
class MemReadNode(ASTNode):
    """Leitura de memória: (CMD_LOAD NOME)."""
    name: str


@dataclass
class MemWriteNode(ASTNode):
    """Escrita em memória: (CMD_STORE valor NOME)."""
    name: str
    value: ASTNode


@dataclass
class ResNode(ASTNode):
    """Comando RES: (CMD_RES N)."""
    n: int


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
