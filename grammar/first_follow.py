# grammar/first_follow.py — Algoritmos de ponto fixo para FIRST e FOLLOW.

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grammar.grammar import Gramatica


EPSILON = "ε"


def calcularFirst(g: "Gramatica") -> dict[str, set[str]]:
    """
    Calcula o conjunto FIRST para todos os símbolos da gramática.
    FIRST(X) é o conjunto de terminais que podem começar uma derivação a partir de X.

    Algoritmo clássico de ponto fixo (Aho, Sethi, Ullman).
    """
    first: dict[str, set[str]] = {nt: set() for nt in g.nao_terminais}
    # Para terminais, FIRST(t) = {t}
    for t in g.terminais:
        first[t] = {t}

    mudou = True
    while mudou:
        mudou = False
        for prod in g.producoes:
            nt = prod.cabeca
            antes = len(first[nt])

            if not prod.corpo:
                # Produção vazia: FIRST inclui ε
                first[nt].add(EPSILON)
            else:
                # FIRST(X1 X2 ... Xn) = FIRST(X1) - {ε} ∪ ... (se X1 derivar ε)
                for simbolo in prod.corpo:
                    first[nt] |= (first.get(simbolo, {simbolo}) - {EPSILON})
                    if EPSILON not in first.get(simbolo, set()):
                        break
                else:
                    # Todos os símbolos da direita podem derivar ε
                    first[nt].add(EPSILON)

            if len(first[nt]) != antes:
                mudou = True

    return first


def calcularFollow(g: "Gramatica") -> dict[str, set[str]]:
    """
    Calcula o conjunto FOLLOW para todos os não-terminais.
    FOLLOW(A) é o conjunto de terminais que podem aparecer imediatamente
    à direita de A em alguma forma sentencial.

    Regras:
      1. FOLLOW(S) contém EOF (onde S é o símbolo inicial).
      2. Se A → α B β, então FIRST(β) - {ε} ⊆ FOLLOW(B).
      3. Se A → α B ou A → α B β onde ε ∈ FIRST(β), então FOLLOW(A) ⊆ FOLLOW(B).
    """
    follow: dict[str, set[str]] = {nt: set() for nt in g.nao_terminais}
    follow[g.simbolo_inicial].add("EOF")

    mudou = True
    while mudou:
        mudou = False
        for prod in g.producoes:
            # 'trailer' acumula o que pode vir depois do símbolo atual
            trailer = set(follow[prod.cabeca])
            for simbolo in reversed(prod.corpo):
                if simbolo in g.nao_terminais:
                    antes = len(follow[simbolo])
                    follow[simbolo] |= trailer
                    if len(follow[simbolo]) != antes:
                        mudou = True
                    if EPSILON in g.first.get(simbolo, set()):
                        trailer |= (g.first[simbolo] - {EPSILON})
                    else:
                        trailer = set(g.first.get(simbolo, {simbolo}))
                else:
                    # Terminal: resetar trailer para FIRST do terminal = {terminal}
                    trailer = {simbolo}
    return follow


def first_of_sequence(simbolos: list[str], first: dict[str, set[str]]) -> set[str]:
    """
    Calcula FIRST de uma sequência arbitrária de símbolos.
    Usado na construção da tabela LL(1).
    """
    resultado: set[str] = set()
    for s in simbolos:
        resultado |= (first.get(s, {s}) - {EPSILON})
        if EPSILON not in first.get(s, set()):
            break
    else:
        # Todos os símbolos derivam ε
        resultado.add(EPSILON)
    return resultado
