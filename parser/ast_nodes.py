# parser/ast_nodes.py — Nós da Árvore Sintática Abstrata (AST).
# A AST é a representação semântica do programa, limpa da derivação gramatical.
#
# Fase 3: cada nó carrega campos de anotação semântica preenchidos pelo
# analisador semântico para formar a ÁRVORE SINTÁTICA ATRIBUÍDA:
#   - linha     : linha do código-fonte (para mensagens de erro);
#   - tipo      : tipo inferido/verificado do nó ('int' | 'real' | 'bool' | None);
#   - categoria : categoria semântica do nó (ex.: 'expressao_aritmetica').

from dataclasses import dataclass, field
from typing import Any


class ASTNode:
    """Classe base de todos os nós da AST."""
    pass


@dataclass
class ProgramNode(ASTNode):
    """Raiz do programa — lista de statements."""
    statements: list[ASTNode]
    linha: int = 0
    categoria: str | None = None


@dataclass
class BinOpNode(ASTNode):
    """Operação binária aritmética."""
    op: str                # '+', '-', '*', '|', '/', '%', '^'
    left: ASTNode
    right: ASTNode
    linha: int = 0
    tipo: str | None = None
    categoria: str | None = None


@dataclass
class NumberNode(ASTNode):
    """Literal numérico."""
    value: int | float
    is_real: bool          # True = REAL (IEEE 754), False = INTEGER
    linha: int = 0
    tipo: str | None = None
    categoria: str | None = None


@dataclass
class MemReadNode(ASTNode):
    """Leitura de memória: (CMD_LOAD NOME)."""
    name: str
    linha: int = 0
    tipo: str | None = None
    categoria: str | None = None


@dataclass
class MemWriteNode(ASTNode):
    """Escrita em memória: (CMD_STORE valor NOME)."""
    name: str
    value: ASTNode
    linha: int = 0
    tipo: str | None = None
    categoria: str | None = None


@dataclass
class ResNode(ASTNode):
    """Comando RES: (CMD_RES N)."""
    n: int
    linha: int = 0
    tipo: str | None = None
    categoria: str | None = None


@dataclass
class ConditionNode(ASTNode):
    """Condição relacional: (A B relop)."""
    op: str                # '>', '<', '>=', '<=', '==', '!='
    left: ASTNode
    right: ASTNode
    linha: int = 0
    tipo: str | None = None
    categoria: str | None = None


@dataclass
class IfNode(ASTNode):
    """Estrutura IF ou IFELSE."""
    condition: ConditionNode
    then_block: list[ASTNode]
    else_block: list[ASTNode] = field(default_factory=list)
    linha: int = 0
    categoria: str | None = None


@dataclass
class WhileNode(ASTNode):
    """Estrutura WHILE."""
    condition: ConditionNode
    body: list[ASTNode]
    linha: int = 0
    categoria: str | None = None


@dataclass
class BlockNode(ASTNode):
    """Bloco de statements entre [ ]."""
    statements: list[ASTNode]
    linha: int = 0
    categoria: str | None = None
