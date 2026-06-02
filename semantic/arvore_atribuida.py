# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA3-21]
# =============================================================================
# semantic/arvore_atribuida.py — gerarArvoreAtribuida (Aluno 4).
#
# Produz a ÁRVORE SINTÁTICA ATRIBUÍDA: a AST anotada com, no mínimo, o tipo
# inferido/verificado de cada nó relevante, a categoria semântica do nó, a
# linha de origem e as referências à tabela de símbolos. Essas informações
# justificam e alimentam a geração do código Assembly.

from dataclasses import dataclass
import json

from parser.ast_nodes import (
    ASTNode, ProgramNode, BinOpNode, NumberNode,
    MemReadNode, MemWriteNode, ResNode,
    ConditionNode, IfNode, WhileNode,
)
from semantic.tabela_simbolos import TabelaSimbolos


# Categoria semântica de cada tipo de nó.
def _categoria(node: ASTNode) -> str:
    if isinstance(node, ProgramNode):
        return "programa"
    if isinstance(node, BinOpNode):
        return "expressao_aritmetica"
    if isinstance(node, NumberNode):
        return "literal_real" if node.is_real else "literal_inteiro"
    if isinstance(node, MemReadNode):
        return "leitura_memoria"
    if isinstance(node, MemWriteNode):
        return "atribuicao_memoria"
    if isinstance(node, ResNode):
        return "resultado_anterior"
    if isinstance(node, ConditionNode):
        return "condicao_relacional"
    if isinstance(node, IfNode):
        return "decisao_composta" if node.else_block else "decisao_simples"
    if isinstance(node, WhileNode):
        return "repeticao"
    return "desconhecido"


def _atribuir_categorias(node: ASTNode):
    """Anota node.categoria recursivamente em toda a árvore."""
    if node is None:
        return
    if isinstance(node, list):
        for x in node:
            _atribuir_categorias(x)
        return
    if hasattr(node, "categoria"):
        node.categoria = _categoria(node)
    if isinstance(node, ProgramNode):
        _atribuir_categorias(node.statements)
    elif isinstance(node, BinOpNode):
        _atribuir_categorias(node.left)
        _atribuir_categorias(node.right)
    elif isinstance(node, MemWriteNode):
        _atribuir_categorias(node.value)
    elif isinstance(node, ConditionNode):
        _atribuir_categorias(node.left)
        _atribuir_categorias(node.right)
    elif isinstance(node, IfNode):
        _atribuir_categorias(node.condition)
        _atribuir_categorias(node.then_block)
        _atribuir_categorias(node.else_block)
    elif isinstance(node, WhileNode):
        _atribuir_categorias(node.condition)
        _atribuir_categorias(node.body)


def _ref_simbolo(tabela: TabelaSimbolos, nome: str) -> dict | None:
    s = tabela.get(nome) if tabela else None
    if s is None:
        return None
    return {"tipo": s.tipo, "linha_definicao": s.linha_definicao}


def _no_to_dict(node: ASTNode, tabela: TabelaSimbolos):
    if node is None:
        return None
    if isinstance(node, ProgramNode):
        return {
            "no": "Programa",
            "categoria": node.categoria,
            "statements": [_no_to_dict(s, tabela) for s in node.statements],
        }
    if isinstance(node, NumberNode):
        return {
            "no": "Number", "categoria": node.categoria, "tipo": node.tipo,
            "linha": node.linha, "valor": node.value, "is_real": node.is_real,
        }
    if isinstance(node, MemReadNode):
        return {
            "no": "MemRead", "categoria": node.categoria, "tipo": node.tipo,
            "linha": node.linha, "nome": node.name,
            "simbolo": _ref_simbolo(tabela, node.name),
        }
    if isinstance(node, MemWriteNode):
        return {
            "no": "MemWrite", "categoria": node.categoria, "tipo": node.tipo,
            "linha": node.linha, "nome": node.name,
            "simbolo": _ref_simbolo(tabela, node.name),
            "valor": _no_to_dict(node.value, tabela),
        }
    if isinstance(node, ResNode):
        return {
            "no": "Res", "categoria": node.categoria, "tipo": node.tipo,
            "linha": node.linha, "n": node.n,
        }
    if isinstance(node, BinOpNode):
        return {
            "no": "BinOp", "categoria": node.categoria, "tipo": node.tipo,
            "linha": node.linha, "op": node.op,
            "esquerda": _no_to_dict(node.left, tabela),
            "direita": _no_to_dict(node.right, tabela),
        }
    if isinstance(node, ConditionNode):
        return {
            "no": "Condition", "categoria": node.categoria, "tipo": node.tipo,
            "linha": node.linha, "op": node.op,
            "esquerda": _no_to_dict(node.left, tabela),
            "direita": _no_to_dict(node.right, tabela),
        }
    if isinstance(node, IfNode):
        return {
            "no": "If", "categoria": node.categoria, "linha": node.linha,
            "condicao": _no_to_dict(node.condition, tabela),
            "then": [_no_to_dict(s, tabela) for s in node.then_block],
            "else": [_no_to_dict(s, tabela) for s in node.else_block],
        }
    if isinstance(node, WhileNode):
        return {
            "no": "While", "categoria": node.categoria, "linha": node.linha,
            "condicao": _no_to_dict(node.condition, tabela),
            "corpo": [_no_to_dict(s, tabela) for s in node.body],
        }
    return {"no": type(node).__name__}


def _no_to_markdown(d: dict, nivel: int = 0) -> list[str]:
    """Renderiza o dicionário da árvore atribuída como lista aninhada."""
    ind = "  " * nivel
    if d is None:
        return [f"{ind}- ø"]
    linhas = []
    nome = d.get("no", "?")
    tipo = d.get("tipo")
    cat = d.get("categoria", "")
    linha_src = d.get("linha")
    rotulo = nome
    detalhe = []
    if "op" in d:
        detalhe.append(f"op='{d['op']}'")
    if "valor" in d:
        detalhe.append(f"valor={d['valor']}")
    if "nome" in d:
        detalhe.append(f"mem={d['nome']}")
    if "n" in d:
        detalhe.append(f"n={d['n']}")
    cab = f"{ind}- **{rotulo}**"
    if detalhe:
        cab += " (" + ", ".join(detalhe) + ")"
    anot = [f"categoria={cat}"]
    if tipo is not None:
        anot.append(f"tipo={tipo}")
    if linha_src is not None:
        anot.append(f"linha={linha_src}")
    if d.get("simbolo"):
        anot.append(f"símbolo→{d['simbolo']['tipo']}@L{d['simbolo']['linha_definicao']}")
    cab += "  — " + ", ".join(anot)
    linhas.append(cab)

    for chave in ("esquerda", "direita", "valor", "condicao"):
        if chave in d and isinstance(d[chave], dict):
            linhas.append(f"{ind}  · {chave}:")
            linhas += _no_to_markdown(d[chave], nivel + 2)
    for chave in ("statements", "then", "else", "corpo"):
        if chave in d and d[chave]:
            linhas.append(f"{ind}  · {chave}:")
            for filho in d[chave]:
                linhas += _no_to_markdown(filho, nivel + 2)
    return linhas


@dataclass
class ArvoreAtribuida:
    """Árvore sintática atribuída + acesso à AST anotada para o gerador."""
    programa: ProgramNode            # AST anotada — entrada de gerarAssembly()
    tabela: TabelaSimbolos
    tipos: dict

    def to_dict(self) -> dict:
        return _no_to_dict(self.programa, self.tabela)

    def to_json_str(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        corpo = _no_to_markdown(self.to_dict(), 0)
        return "# Árvore Sintática Atribuída\n\n" + "\n".join(corpo) + "\n"


def gerarArvoreAtribuida(
    arvore: ProgramNode, tabelaSimbolos: TabelaSimbolos, tipos: dict
) -> ArvoreAtribuida:
    """
    Produz a árvore sintática atribuída a partir da árvore inicial, da tabela
    de símbolos e dos tipos inferidos por verificarTipos().

    A AST já vem anotada com os tipos (campo .tipo); aqui anotamos também a
    categoria semântica de cada nó e empacotamos tudo em ArvoreAtribuida, que
    expõe `.programa` (AST anotada) para gerarAssembly() e serializa a árvore
    para Markdown/JSON.
    """
    _atribuir_categorias(arvore)
    return ArvoreAtribuida(programa=arvore, tabela=tabelaSimbolos, tipos=tipos)
