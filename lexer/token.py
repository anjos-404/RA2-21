# lexer/token.py — INTERFACE ACORDADA ENTRE TODOS
# Define TokenType (enum) e Token (dataclass) usados em todo o compilador.

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Literais
    INTEGER     = auto()   # ex: 42
    REAL        = auto()   # ex: 3.14
    # Memórias e keywords
    MEM_NAME    = auto()   # ex: X, CONTADOR (letras maiúsculas)
    RES         = auto()   # keyword RES
    # Operadores aritméticos
    PLUS        = auto()   # +
    MINUS       = auto()   # -
    MUL         = auto()   # *
    DIV_REAL    = auto()   # |
    DIV_INT     = auto()   # /
    MOD         = auto()   # %
    POW         = auto()   # ^
    # Operadores relacionais (Parte 3)
    GT          = auto()   # >
    LT          = auto()   # <
    GTE         = auto()   # >=
    LTE         = auto()   # <=
    EQ          = auto()   # ==
    NEQ         = auto()   # !=
    # Estruturas de controle (Parte 3)
    IF          = auto()   # IF
    IFELSE      = auto()   # IFELSE
    WHILE       = auto()   # WHILE
    # Delimitadores
    LPAREN      = auto()   # (
    RPAREN      = auto()   # )
    LBRACKET    = auto()   # [
    RBRACKET    = auto()   # ]
    # Programa
    START       = auto()   # START (dentro de parênteses)
    END         = auto()   # END (dentro de parênteses)
    # Especial
    EOF         = auto()


@dataclass
class Token:
    type: TokenType
    value: str | int | float
    line: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, L{self.line})"
