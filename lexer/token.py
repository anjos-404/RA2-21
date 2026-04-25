# lexer/token.py — Definições de Token para gramática LL(1) pura.
# Tipos de token usados por todo o compilador.

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # ----- Literais -----
    INTEGER     = auto()   # ex: 42
    REAL        = auto()   # ex: 3.14
    MEM_NAME    = auto()   # ex: X, CONTADOR (letras maiúsculas)

    # ----- Marcadores desambiguadores -----
    EXPR        = auto()   # marca expressão aritmética: (EXPR a b op)
    CMD_RES     = auto()   # marca comando RES:          (CMD_RES N)
    CMD_LOAD    = auto()   # marca leitura de memória:   (CMD_LOAD X)
    CMD_STORE   = auto()   # marca escrita em memória:   (CMD_STORE V X)

    # ----- Estruturas de controle -----
    IF          = auto()   # (IF cond block)
    IFELSE      = auto()   # (IFELSE cond then else)
    WHILE       = auto()   # (WHILE cond block)

    # ----- Operadores aritméticos -----
    PLUS        = auto()   # +
    MINUS       = auto()   # -
    MUL         = auto()   # *
    DIV_REAL    = auto()   # |
    DIV_INT     = auto()   # /
    MOD         = auto()   # %
    POW         = auto()   # ^

    # ----- Operadores relacionais -----
    GT          = auto()   # >
    LT          = auto()   # <
    GTE         = auto()   # >=
    LTE         = auto()   # <=
    EQ          = auto()   # ==
    NEQ         = auto()   # !=

    # ----- Delimitadores -----
    LPAREN      = auto()   # (
    RPAREN      = auto()   # )
    LBRACKET    = auto()   # [
    RBRACKET    = auto()   # ]

    # ----- Marcadores de programa -----
    START       = auto()   # keyword START (início de programa)
    END         = auto()   # keyword END (fim de programa)

    # ----- Especial -----
    EOF         = auto()


@dataclass
class Token:
    """Token: unidade léxica produzida pelo analisador léxico."""
    type: TokenType
    value: str | int | float
    line: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, L{self.line})"
