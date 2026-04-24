# grammar/grammar.py — Parte 1
# Definição da gramática RPN, produções e função construirGramatica().

from dataclasses import dataclass, field
from grammar.first_follow import calcularFirst, calcularFollow
from grammar.ll1_table import construirTabelaLL1


@dataclass
class Producao:
    """Uma produção da gramática: cabeça → corpo."""
    cabeca: str          # não-terminal 
    corpo: list[str]     # lista de símbolos

    def __repr__(self):
        corpo_str = ' '.join(self.corpo) if self.corpo else 'ε'
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
    Retorna a gramática completa com FIRST, FOLLOW e tabela LL(1) calculados.
    Entrada: Nenhuma (gramática é fixa).
    Saída: objeto Gramatica pronto para ser consumido por parsear().
    """
    producoes = [
        # Programa
        Producao("programa",    ["LPAREN", "START", "RPAREN", "stmts", "LPAREN", "END", "RPAREN"]),

        # Lista de statements (com epsilon)
        Producao("stmts",       ["statement", "stmts"]),
        Producao("stmts",       []),   # produção epsilon

        # Statement → expression | special_cmd | control_struct
        Producao("statement",   ["expression"]),
        Producao("statement",   ["special_cmd"]),
        Producao("statement",   ["control_struct"]),

        # Expressão binária: (operand operand arith_op)
        Producao("expression",  ["LPAREN", "operand", "operand", "arith_op", "RPAREN"]),

        # Operandos
        Producao("operand",     ["INTEGER"]),
        Producao("operand",     ["REAL"]),
        Producao("operand",     ["MEM_NAME"]),
        Producao("operand",     ["expression"]),

        # Operadores aritméticos
        Producao("arith_op",    ["PLUS"]),
        Producao("arith_op",    ["MINUS"]),
        Producao("arith_op",    ["MUL"]),
        Producao("arith_op",    ["DIV_REAL"]),
        Producao("arith_op",    ["DIV_INT"]),
        Producao("arith_op",    ["MOD"]),
        Producao("arith_op",    ["POW"]),

        # Operadores relacionais
        Producao("relational_op", ["GT"]),
        Producao("relational_op", ["LT"]),
        Producao("relational_op", ["GTE"]),
        Producao("relational_op", ["LTE"]),
        Producao("relational_op", ["EQ"]),
        Producao("relational_op", ["NEQ"]),

        # Comandos especiais
        Producao("special_cmd",   ["LPAREN", "INTEGER", "RES", "RPAREN"]),
        Producao("special_cmd",   ["LPAREN", "operand", "MEM_NAME", "RPAREN"]),
        Producao("special_cmd",   ["LPAREN", "MEM_NAME", "RPAREN"]),

        # Estruturas de controle
        Producao("control_struct", ["if_stmt"]),
        Producao("control_struct", ["while_stmt"]),

        # IF e IFELSE
        Producao("if_stmt",     ["LPAREN", "condition", "block", "IF", "RPAREN"]),
        Producao("if_stmt",     ["LPAREN", "condition", "block", "block", "IFELSE", "RPAREN"]),

        # WHILE
        Producao("while_stmt",  ["LPAREN", "condition", "block", "WHILE", "RPAREN"]),

        # Condição: (operand operand relational_op)
        Producao("condition",   ["LPAREN", "operand", "operand", "relational_op", "RPAREN"]),

        # Bloco: [stmts]
        Producao("block",       ["LBRACKET", "stmts", "RBRACKET"]),
    ]

    nao_terminais = {p.cabeca for p in producoes}
    terminais = {
        "LPAREN", "RPAREN", "LBRACKET", "RBRACKET",
        "START", "END", "INTEGER", "REAL", "MEM_NAME", "RES",
        "PLUS", "MINUS", "MUL", "DIV_REAL", "DIV_INT", "MOD", "POW",
        "GT", "LT", "GTE", "LTE", "EQ", "NEQ",
        "IF", "IFELSE", "WHILE", "EOF"
    }

    g = Gramatica(producoes, nao_terminais, terminais)
    g.first  = calcularFirst(g)
    g.follow = calcularFollow(g)
    g.tabela = construirTabelaLL1(g)
    return g
