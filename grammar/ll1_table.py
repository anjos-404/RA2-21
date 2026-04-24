# grammar/ll1_table.py — Parte 1
# Construção da tabela de análise LL(1).

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grammar.grammar import Gramatica, Producao

from grammar.first_follow import first_of_sequence


# Conflitos conhecidos e esperados na gramática RPN
CONFLITOS_PERMITIDOS = {
    ("statement", "LPAREN"),       # expression vs special_cmd vs control_struct
    ("control_struct", "LPAREN"),  # if_stmt vs while_stmt
    ("stmts", "LPAREN"),           # statement stmts vs ε (pode acontecer via FOLLOW)
    ("special_cmd", "LPAREN"),     # (N RES) vs (V MEM) vs (MEM)
    ("if_stmt", "LPAREN"),         # IF vs IFELSE
    ("operand", "LPAREN"),         # expression como operand
}


def construirTabelaLL1(g: "Gramatica") -> dict[tuple, "Producao"]:
    """
    Constrói tabela M[A, a] para parser LL(1).
    Chave: (nao_terminal, terminal)
    Valor: Producao a aplicar

    Para conflitos conhecidos (e.g., statement + LPAREN), a tabela armazena
    a PRIMEIRA produção encontrada. O parser descendente recursivo resolve
    esses conflitos com lookahead.

    Levanta ValueError apenas para conflitos INESPERADOS.
    """
    tabela: dict[tuple, "Producao"] = {}
    conflitos_registrados: list[str] = []

    for prod in g.producoes:
        nt = prod.cabeca
        first_alpha = first_of_sequence(prod.corpo, g.first)

        for terminal in first_alpha - {"ε"}:
            chave = (nt, terminal)
            if chave in tabela:
                if chave in CONFLITOS_PERMITIDOS:
                    # Conflito esperado — manter a primeira produção
                    conflitos_registrados.append(
                        f"  [tolerado] M[{nt}, {terminal}]: "
                        f"'{tabela[chave]}' mantida (ignorando '{prod}')"
                    )
                else:
                    # Resolver por tamanho do corpo
                    existente = tabela[chave]
                    if len(prod.corpo) > len(existente.corpo):
                        tabela[chave] = prod
                    elif len(prod.corpo) == len(existente.corpo) and prod.corpo != existente.corpo:
                        raise ValueError(
                            f"Conflito LL(1) inesperado em M[{nt}, {terminal}]: "
                            f"'{existente}' vs '{prod}'"
                        )
            else:
                tabela[chave] = prod

        if "ε" in first_alpha:
            for terminal in g.follow.get(nt, set()):
                chave = (nt, terminal)
                if chave in tabela:
                    existente = tabela[chave]
                    if existente.corpo:
                        # Produção não-epsilon tem prioridade
                        continue
                    if chave in CONFLITOS_PERMITIDOS:
                        continue
                    raise ValueError(
                        f"Conflito LL(1) inesperado em M[{nt}, {terminal}]: "
                        f"'{existente}' vs '{prod}'"
                    )
                tabela[chave] = prod

    return tabela
