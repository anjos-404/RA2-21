# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA3-21]
# =============================================================================
# semantic/tipos.py — verificarTipos e Sistema de Regras de Tipos (Aluno 3).
#
# Sistema de tipos ESTÁTICO e FORTE com três tipos:
#   int   — literais inteiros e resultados de operações entre inteiros;
#   real  — literais reais (IEEE 754 double) e operações com pelo menos um real;
#   bool  — produzido EXCLUSIVAMENTE por operadores relacionais (condições).
#
# Compatibilidade (coerção de alargamento):  int ⊑ real
#   - int é compatível com real em operadores numéricos (o int é promovido);
#   - bool NÃO é compatível com operadores numéricos.
#
# Regras dos operadores (ver docs/regras_tipos.md, em cálculo de sequentes):
#   + - * ^ : operandos numéricos        -> int se ambos int, senão real
#   |       : divisão real, numéricos     -> real (sempre)
#   / %     : divisão inteira / resto      -> exigem AMBOS int -> int
#   > < >= <= == != : numéricos compatíveis -> bool
#   condição de IF/IFELSE/WHILE            -> deve ter tipo bool

from parser.ast_nodes import (
    ASTNode, ProgramNode, BinOpNode, NumberNode,
    MemReadNode, MemWriteNode, ResNode,
    ConditionNode, IfNode, WhileNode,
)
from errors.errors import SemanticError


class Tipo:
    INT = "int"
    REAL = "real"
    BOOL = "bool"
    NUMERICOS = frozenset({"int", "real"})


def eh_numerico(t: str | None) -> bool:
    return t in Tipo.NUMERICOS


def compativel_atribuicao(declarado: str, novo: str) -> bool:
    """Regra de atribuição/redefinição: tipo igual, ou alargamento int->real."""
    if declarado == novo:
        return True
    return declarado == Tipo.REAL and novo == Tipo.INT


def tipo_resultado_aritmetico(t1: str, t2: str) -> str:
    """Tipo de + - * ^ : int se ambos int, senão real (promoção)."""
    if t1 == Tipo.INT and t2 == Tipo.INT:
        return Tipo.INT
    return Tipo.REAL


# ---------------------------------------------------------------------------
# Inferência de tipo de uma expressão (anota node.tipo).
#
# `erros`: se for uma lista, incompatibilidades são reportadas como
# SemanticError; se for None, a função apenas infere silenciosamente (usada
# pela construção da tabela de símbolos, que não deve duplicar mensagens).
# ---------------------------------------------------------------------------

def _reportar(erros, msg: str, linha: int):
    if erros is not None:
        erros.append(SemanticError(msg, line=linha))


def _tipo_expr(node: ASTNode, tabela, erros) -> str | None:
    if isinstance(node, NumberNode):
        node.tipo = Tipo.REAL if node.is_real else Tipo.INT
        return node.tipo

    if isinstance(node, MemReadNode):
        simbolo = tabela.get(node.name) if tabela is not None else None
        node.tipo = simbolo.tipo if simbolo else None
        return node.tipo

    if isinstance(node, ResNode):
        # Resultados anteriores são armazenados em precisão dupla (double).
        node.tipo = Tipo.REAL
        return node.tipo

    if isinstance(node, BinOpNode):
        tl = _tipo_expr(node.left, tabela, erros)
        tr = _tipo_expr(node.right, tabela, erros)
        node.tipo = _tipo_binop(node, tl, tr, erros)
        return node.tipo

    return None


def _tipo_binop(node: BinOpNode, tl: str | None, tr: str | None, erros) -> str:
    op = node.op
    indeterminado = tl is None or tr is None  # operando com tipo desconhecido

    if op in ("/", "%"):
        nome = "divisão inteira" if op == "/" else "resto (módulo)"
        if indeterminado:
            return Tipo.INT
        if tl != Tipo.INT or tr != Tipo.INT:
            _reportar(
                erros,
                f"operador '{op}' ({nome}) exige operandos inteiros, "
                f"mas recebeu '{tl}' e '{tr}'",
                node.linha,
            )
        return Tipo.INT

    if op == "|":
        if not indeterminado and not (eh_numerico(tl) and eh_numerico(tr)):
            _reportar(
                erros,
                f"operador '|' (divisão real) exige operandos numéricos, "
                f"mas recebeu '{tl}' e '{tr}'",
                node.linha,
            )
        return Tipo.REAL

    if op in ("+", "-", "*", "^"):
        if indeterminado:
            return tipo_resultado_aritmetico(tl or Tipo.INT, tr or Tipo.INT)
        if not (eh_numerico(tl) and eh_numerico(tr)):
            _reportar(
                erros,
                f"operador '{op}' exige operandos numéricos, "
                f"mas recebeu '{tl}' e '{tr}'",
                node.linha,
            )
            return Tipo.REAL
        return tipo_resultado_aritmetico(tl, tr)

    _reportar(erros, f"operador aritmético desconhecido: '{op}'", node.linha)
    return Tipo.REAL


def _tipo_condicao(cond: ConditionNode, tabela, erros) -> str:
    """Condição relacional sempre produz bool; operandos devem ser numéricos."""
    tl = _tipo_expr(cond.left, tabela, erros)
    tr = _tipo_expr(cond.right, tabela, erros)
    if tl is not None and tr is not None:
        if not (eh_numerico(tl) and eh_numerico(tr)):
            _reportar(
                erros,
                f"operador relacional '{cond.op}' exige operandos numéricos, "
                f"mas recebeu '{tl}' e '{tr}'",
                cond.linha,
            )
    cond.tipo = Tipo.BOOL
    return Tipo.BOOL


def inferir_tipo(node: ASTNode, tabela) -> str | None:
    """Inferência silenciosa (sem reportar erros). Usada pela tabela de símbolos."""
    return _tipo_expr(node, tabela, erros=None)


# ---------------------------------------------------------------------------
# verificarTipos — verificação completa, anota a árvore e reporta erros.
# ---------------------------------------------------------------------------

def verificarTipos(arvore: ProgramNode, tabela) -> tuple[dict, list[SemanticError]]:
    """
    Valida os tipos de expressões, comandos especiais, decisões e laços,
    anotando cada nó relevante com seu tipo inferido/verificado.

    Entrada: árvore sintática inicial e tabela de símbolos.
    Saída: (tipos, erros)
        tipos — dict {id(no): tipo} com os tipos inferidos para os nós;
        erros — lista de SemanticError de incompatibilidade de tipos.
    """
    erros: list[SemanticError] = []

    def visitar_stmt(node: ASTNode):
        if isinstance(node, MemWriteNode):
            node.tipo = _tipo_expr(node.value, tabela, erros)
        elif isinstance(node, (BinOpNode, MemReadNode, ResNode)):
            _tipo_expr(node, tabela, erros)
        elif isinstance(node, IfNode):
            _checar_condicao_logica(node.condition, tabela, erros)
            for s in node.then_block:
                visitar_stmt(s)
            for s in node.else_block:
                visitar_stmt(s)
        elif isinstance(node, WhileNode):
            _checar_condicao_logica(node.condition, tabela, erros)
            for s in node.body:
                visitar_stmt(s)

    for s in arvore.statements:
        visitar_stmt(s)

    tipos: dict[int, str] = {}
    _coletar_tipos(arvore, tipos)
    return tipos, erros


def _checar_condicao_logica(cond: ConditionNode, tabela, erros):
    """Garante que a condição de decisão/repetição tenha tipo lógico (bool)."""
    t = _tipo_condicao(cond, tabela, erros)
    if t != Tipo.BOOL:  # salvaguarda: estruturalmente sempre bool
        _reportar(
            erros,
            f"condição de controle deve ser lógica (bool), mas é '{t}'",
            cond.linha,
        )


def _coletar_tipos(node, tipos: dict):
    """Percorre a árvore preenchendo o dicionário id(no) -> tipo."""
    if node is None:
        return
    if isinstance(node, list):
        for x in node:
            _coletar_tipos(x, tipos)
        return
    t = getattr(node, "tipo", None)
    if t is not None:
        tipos[id(node)] = t
    if isinstance(node, ProgramNode):
        _coletar_tipos(node.statements, tipos)
    elif isinstance(node, BinOpNode):
        _coletar_tipos(node.left, tipos)
        _coletar_tipos(node.right, tipos)
    elif isinstance(node, MemWriteNode):
        _coletar_tipos(node.value, tipos)
    elif isinstance(node, ConditionNode):
        _coletar_tipos(node.left, tipos)
        _coletar_tipos(node.right, tipos)
    elif isinstance(node, IfNode):
        _coletar_tipos(node.condition, tipos)
        _coletar_tipos(node.then_block, tipos)
        _coletar_tipos(node.else_block, tipos)
    elif isinstance(node, WhileNode):
        _coletar_tipos(node.condition, tipos)
        _coletar_tipos(node.body, tipos)
