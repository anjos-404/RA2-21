# grammar/first_follow.py — Parte 1
# Cálculo dos conjuntos FIRST e FOLLOW por ponto fixo.

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grammar.grammar import Gramatica


def calcularFirst(g: Gramatica) -> dict[str, set[str]]:
    """
    Calcula FIRST para todos os não-terminais.
    Algoritmo padrão com ponto fixo (repete até estabilizar).
    """
    first: dict[str, set[str]] = {nt: set() for nt in g.nao_terminais}
    # terminais: FIRST(t) = {t}
    for t in g.terminais:
        first[t] = {t}

    changed = True
    while changed:
        changed = False
        for prod in g.producoes:
            nt = prod.cabeca
            antes = len(first[nt])

            if not prod.corpo:   # produção epsilon
                first[nt].add("ε")
            else:
                for simbolo in prod.corpo:
                    first[nt] |= (first.get(simbolo, {simbolo}) - {"ε"})
                    if "ε" not in first.get(simbolo, set()):
                        break
                else:
                    first[nt].add("ε")

            if len(first[nt]) != antes:
                changed = True

    return first


def calcularFollow(g: Gramatica) -> dict[str, set[str]]:
    """
    Calcula FOLLOW para todos os não-terminais.
    Algoritmo padrão com ponto fixo.
    """
    follow: dict[str, set[str]] = {nt: set() for nt in g.nao_terminais}
    follow[g.simbolo_inicial].add("EOF")

    changed = True
    while changed:
        changed = False
        for prod in g.producoes:
            trailer = set(follow[prod.cabeca])
            for simbolo in reversed(prod.corpo):
                if simbolo in g.nao_terminais:
                    antes = len(follow[simbolo])
                    follow[simbolo] |= trailer
                    if len(follow[simbolo]) != antes:
                        changed = True
                    if "ε" in g.first.get(simbolo, set()):
                        trailer |= (g.first[simbolo] - {"ε"})
                    else:
                        trailer = set(g.first.get(simbolo, {simbolo}))
                else:
                    trailer = {simbolo}
    return follow


def first_of_sequence(simbolos: list[str], first: dict) -> set[str]:
    """Calcula FIRST de uma sequência de símbolos."""
    result: set[str] = set()
    for s in simbolos:
        result |= (first.get(s, {s}) - {"ε"})
        if "ε" not in first.get(s, set()):
            break
    else:
        result.add("ε")
    return result
