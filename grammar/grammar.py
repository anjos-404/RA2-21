# grammar/grammar.py — Gramática LL(1) pura para a linguagem RPN estendida.

# Exemplo de tradução da sintaxe original para a sintaxe LL(1):
#   Original: (3 4 +)             →  LL(1): (EXPR 3 4 +)
#   Original: (5 RES)             →  LL(1): (CMD_RES 5)
#   Original: (42 X)              →  LL(1): (CMD_STORE 42 X)
#   Original: (X)                 →  LL(1): (CMD_LOAD X)
#   Original: (cond [then] IF)    →  LL(1): (IF cond [then])
#   Original: (cond [t] [e] IFELSE) → LL(1): (IFELSE cond [t] [e])
#   Original: (cond [body] WHILE) →  LL(1): (WHILE cond [body])

from dataclasses import dataclass, field
from grammar.first_follow import calcularFirst, calcularFollow
from grammar.ll1_table import construirTabelaLL1


@dataclass
class Producao:
    """Uma produção da gramática: cabeca → corpo."""
    cabeca: str          # não-terminal
    corpo: list[str]     # sequência de símbolos (vazia = ε)

    def __repr__(self):
        corpo_str = " ".join(self.corpo) if self.corpo else "ε"
        return f"{self.cabeca} → {corpo_str}"


@dataclass
class Gramatica:
    """Gramática completa com produções, FIRST, FOLLOW e tabela LL(1)."""
    producoes: list[Producao]
    nao_terminais: set[str]
    terminais: set[str]
    simbolo_inicial: str = "programa"
    first: dict[str, set[str]] = field(default_factory=dict)
    follow: dict[str, set[str]] = field(default_factory=dict)
    tabela: dict[tuple, Producao] = field(default_factory=dict)


def construirGramatica() -> Gramatica:
    """
    Retorna a gramática LL(1) pura com FIRST, FOLLOW e tabela LL(1) calculados.

    A gramática é fixa — essa função é idempotente.
    A tabela LL(1) é construída sem conflitos.
    """
    producoes = [
        # ---- Programa: START <stmts> END ----
        Producao("programa", ["START", "stmts", "END"]),

        # ---- Lista de statements (pode ser vazia) ----
        Producao("stmts", ["statement", "stmts"]),
        Producao("stmts", []),                          # ε

        # ---- Statement: sempre '(' seguido de marcador ----
        Producao("statement", ["LPAREN", "stmt_tail"]),

        # ---- stmt_tail: escolha determinada pelo marcador ----
        Producao("stmt_tail", ["EXPR", "operand", "operand", "arith_op", "RPAREN"]),
        Producao("stmt_tail", ["CMD_RES", "INTEGER", "RPAREN"]),
        Producao("stmt_tail", ["CMD_LOAD", "MEM_NAME", "RPAREN"]),
        Producao("stmt_tail", ["CMD_STORE", "operand", "MEM_NAME", "RPAREN"]),
        Producao("stmt_tail", ["IF", "condition", "block", "RPAREN"]),
        Producao("stmt_tail", ["IFELSE", "condition", "block", "block", "RPAREN"]),
        Producao("stmt_tail", ["WHILE", "condition", "block", "RPAREN"]),

        # ---- Operando: escolha determinada pelo primeiro token ----
        Producao("operand", ["INTEGER"]),
        Producao("operand", ["REAL"]),
        Producao("operand", ["MEM_NAME"]),
        Producao("operand", ["LPAREN", "operand_paren_tail"]),

        # ---- operand_paren_tail: sub-expressão dentro de operand ----
        Producao("operand_paren_tail", ["EXPR", "operand", "operand", "arith_op", "RPAREN"]),
        Producao("operand_paren_tail", ["CMD_LOAD", "MEM_NAME", "RPAREN"]),

        # ---- Operadores aritméticos ----
        Producao("arith_op", ["PLUS"]),
        Producao("arith_op", ["MINUS"]),
        Producao("arith_op", ["MUL"]),
        Producao("arith_op", ["DIV_REAL"]),
        Producao("arith_op", ["DIV_INT"]),
        Producao("arith_op", ["MOD"]),
        Producao("arith_op", ["POW"]),

        # ---- Operadores relacionais ----
        Producao("relational_op", ["GT"]),
        Producao("relational_op", ["LT"]),
        Producao("relational_op", ["GTE"]),
        Producao("relational_op", ["LTE"]),
        Producao("relational_op", ["EQ"]),
        Producao("relational_op", ["NEQ"]),

        # ---- Condição: (operand operand relop) ----
        Producao("condition", ["LPAREN", "operand", "operand", "relational_op", "RPAREN"]),

        # ---- Bloco: [ stmts ] ----
        Producao("block", ["LBRACKET", "stmts", "RBRACKET"]),
    ]

    nao_terminais = {p.cabeca for p in producoes}
    terminais = {
        "LPAREN", "RPAREN", "LBRACKET", "RBRACKET",
        "START", "END", "INTEGER", "REAL", "MEM_NAME",
        "EXPR", "CMD_RES", "CMD_LOAD", "CMD_STORE",
        "IF", "IFELSE", "WHILE",
        "PLUS", "MINUS", "MUL", "DIV_REAL", "DIV_INT", "MOD", "POW",
        "GT", "LT", "GTE", "LTE", "EQ", "NEQ",
        "EOF",
    }

    g = Gramatica(producoes, nao_terminais, terminais)
    g.first = calcularFirst(g)
    g.follow = calcularFollow(g)
    g.tabela = construirTabelaLL1(g)
    return g
