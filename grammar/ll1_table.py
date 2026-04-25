# grammar/ll1_table.py — Construção rigorosa da tabela de análise LL(1).
# Esta implementação NÃO permite conflitos. Se a gramática não for LL(1),

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grammar.grammar import Gramatica, Producao

from grammar.first_follow import first_of_sequence, EPSILON
from errors.errors import GrammarError


def construirTabelaLL1(g: "Gramatica") -> dict[tuple, "Producao"]:
    """
    Constrói a tabela de análise preditiva LL(1) M[A, a].

    Regra de preenchimento:
      Para cada produção A → α da gramática:
        (1) Para cada terminal a em FIRST(α) - {ε}:
              M[A, a] := A → α
        (2) Se ε ∈ FIRST(α), então para cada b em FOLLOW(A):
              M[A, b] := A → α

    Se alguma célula receberia duas produções diferentes, a gramática
    NÃO é LL(1) e uma exceção é levantada com detalhes do conflito.
    """
    tabela: dict[tuple, "Producao"] = {}
    conflitos: list[str] = []

    def _definir(nt: str, terminal: str, prod: "Producao"):
        """Define M[nt, terminal] = prod ou detecta conflito."""
        chave = (nt, terminal)
        if chave in tabela:
            existente = tabela[chave]
            if existente.corpo != prod.corpo or existente.cabeca != prod.cabeca:
                conflitos.append(
                    f"  Conflito em M[{nt}, {terminal}]:\n"
                    f"    candidato 1: {existente}\n"
                    f"    candidato 2: {prod}"
                )
        else:
            tabela[chave] = prod

    for prod in g.producoes:
        nt = prod.cabeca
        first_alpha = first_of_sequence(prod.corpo, g.first)

        # (1) FIRST(α) - {ε}
        for terminal in first_alpha - {EPSILON}:
            _definir(nt, terminal, prod)

        # (2) Se α pode derivar ε, usar FOLLOW(A)
        if EPSILON in first_alpha:
            for terminal in g.follow.get(nt, set()):
                _definir(nt, terminal, prod)

    if conflitos:
        raise GrammarError(
            "A gramática não é LL(1). Conflitos detectados:\n"
            + "\n".join(conflitos)
        )

    return tabela


def imprimir_tabela(g: "Gramatica", arquivo=None):
    """Imprime a tabela LL(1) em formato tabular (para debug/documentação)."""
    # Coletar terminais usados como colunas
    terminais_usados = sorted({k[1] for k in g.tabela.keys()})
    nao_terminais = sorted({k[0] for k in g.tabela.keys()})

    def out(msg):
        if arquivo:
            print(msg, file=arquivo)
        else:
            print(msg)

    # Cabeçalho
    out("Tabela LL(1):")
    out("=" * 80)
    for nt in nao_terminais:
        out(f"\n[{nt}]")
        for t in terminais_usados:
            if (nt, t) in g.tabela:
                out(f"  {t:14s}  →  {g.tabela[(nt, t)]}")
    out("\n" + "=" * 80)
    out(f"Total de entradas: {len(g.tabela)}")
