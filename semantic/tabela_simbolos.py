# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA3-21]
# =============================================================================
# semantic/tabela_simbolos.py — construirTabelaSimbolos e Validação de
# Declarações (Aluno 2).
#
# Percorre a árvore sintática em ORDEM DE PROGRAMA e:
#   - registra cada variável (nome, tipo inferido na definição, categoria,
#     escopo, linha de definição e linhas de uso);
#   - verifica se toda variável foi DEFINIDA ANTES de ser usada;
#   - impede redefinição com tipo incompatível (tipagem estática e forte);
#   - controla o significado dos comandos especiais (V MEM)/CMD_STORE,
#     (MEM)/CMD_LOAD e (N RES)/CMD_RES;
#   - valida referências a resultados anteriores feitas com RES.
#
# Escopo: cada arquivo-fonte representa um único escopo de memória global
# ("global"); as estruturas de controle não criam novos escopos de memória.

from dataclasses import dataclass, field
import json

from parser.ast_nodes import (
    ASTNode, ProgramNode, BinOpNode, NumberNode,
    MemReadNode, MemWriteNode, ResNode,
    ConditionNode, IfNode, WhileNode,
)
from errors.errors import SemanticError
from semantic.tipos import inferir_tipo, compativel_atribuicao, Tipo


@dataclass
class Simbolo:
    """Entrada da tabela de símbolos."""
    nome: str
    tipo: str                       # 'int' | 'real'
    linha_definicao: int
    categoria: str = "variavel"
    escopo: str = "global"
    linhas_uso: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "escopo": self.escopo,
            "linha_definicao": self.linha_definicao,
            "linhas_uso": list(self.linhas_uso),
        }


class TabelaSimbolos:
    """Tabela de símbolos: nome -> Simbolo (escopo global por arquivo)."""

    def __init__(self):
        self._simbolos: dict[str, Simbolo] = {}

    def definida(self, nome: str) -> bool:
        return nome in self._simbolos

    def get(self, nome: str) -> Simbolo | None:
        return self._simbolos.get(nome)

    def declarar(self, nome: str, tipo: str, linha: int,
                 categoria: str = "variavel") -> Simbolo:
        simbolo = Simbolo(
            nome=nome, tipo=tipo, linha_definicao=linha, categoria=categoria
        )
        self._simbolos[nome] = simbolo
        return simbolo

    def registrar_uso(self, nome: str, linha: int):
        simbolo = self._simbolos.get(nome)
        if simbolo is not None and linha not in simbolo.linhas_uso:
            simbolo.linhas_uso.append(linha)

    def itens(self) -> list[Simbolo]:
        return list(self._simbolos.values())

    def __len__(self) -> int:
        return len(self._simbolos)

    # ----- Serialização (artefatos) -----

    def to_dict(self) -> dict:
        return {nome: s.to_dict() for nome, s in self._simbolos.items()}

    def to_json_str(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        linhas = [
            "# Tabela de Símbolos",
            "",
            "| Nome | Tipo | Categoria | Escopo | Linha de definição | Linhas de uso |",
            "|------|------|-----------|--------|--------------------|---------------|",
        ]
        if not self._simbolos:
            linhas.append("| _(nenhuma variável)_ | | | | | |")
        for s in self._simbolos.values():
            usos = ", ".join(str(u) for u in s.linhas_uso) if s.linhas_uso else "—"
            linhas.append(
                f"| {s.nome} | {s.tipo} | {s.categoria} | {s.escopo} "
                f"| {s.linha_definicao} | {usos} |"
            )
        return "\n".join(linhas) + "\n"


def construirTabelaSimbolos(
    arvore: ProgramNode,
) -> tuple[TabelaSimbolos, list[SemanticError]]:
    """
    Constrói a tabela de símbolos e retorna a lista de erros semânticos
    relacionados a declarações:
      - uso de variável não definida;
      - redefinição com tipo incompatível;
      - referência inválida a resultado anterior (RES).
    """
    tabela = TabelaSimbolos()
    erros: list[SemanticError] = []
    # nº de resultados de TOPO emitidos até o ponto atual (para validar RES)
    estado = {"resultados": 0}

    def usar_variavel(nome: str, linha: int):
        if tabela.definida(nome):
            tabela.registrar_uso(nome, linha)
        else:
            erros.append(SemanticError(
                f"variável '{nome}' usada antes de ser definida", line=linha))

    def registrar_usos_expr(node: ASTNode):
        """Registra usos de variáveis dentro de uma expressão/condição."""
        if isinstance(node, BinOpNode):
            registrar_usos_expr(node.left)
            registrar_usos_expr(node.right)
        elif isinstance(node, MemReadNode):
            usar_variavel(node.name, node.linha)
        # NumberNode e ResNode não referenciam variáveis

    def validar_res(node: ResNode):
        disponiveis = estado["resultados"]
        if node.n < 1 or node.n > disponiveis:
            erros.append(SemanticError(
                f"RES({node.n}) referencia um resultado inexistente — há "
                f"{disponiveis} resultado(s) anterior(es) disponível(is)",
                line=node.linha))

    def visitar_stmt(node: ASTNode, topo: bool):
        if isinstance(node, MemWriteNode):
            # (V MEM): o valor é avaliado ANTES de a variável ser (re)definida.
            registrar_usos_expr(node.value)
            tipo_valor = inferir_tipo(node.value, tabela) or Tipo.REAL
            if tabela.definida(node.name):
                decl = tabela.get(node.name)
                if not compativel_atribuicao(decl.tipo, tipo_valor):
                    erros.append(SemanticError(
                        f"variável '{node.name}' foi definida como "
                        f"'{decl.tipo}' e não pode receber valor '{tipo_valor}' "
                        f"(tipagem estática e forte)", line=node.linha))
            else:
                tabela.declarar(node.name, tipo_valor, node.linha)
            if topo:
                estado["resultados"] += 1

        elif isinstance(node, MemReadNode):
            usar_variavel(node.name, node.linha)
            if topo:
                estado["resultados"] += 1

        elif isinstance(node, BinOpNode):
            registrar_usos_expr(node)
            if topo:
                estado["resultados"] += 1

        elif isinstance(node, ResNode):
            validar_res(node)          # valida ANTES de contar este resultado
            if topo:
                estado["resultados"] += 1

        elif isinstance(node, IfNode):
            registrar_usos_expr(node.condition.left)
            registrar_usos_expr(node.condition.right)
            for s in node.then_block:
                visitar_stmt(s, topo=False)
            for s in node.else_block:
                visitar_stmt(s, topo=False)

        elif isinstance(node, WhileNode):
            registrar_usos_expr(node.condition.left)
            registrar_usos_expr(node.condition.right)
            for s in node.body:
                visitar_stmt(s, topo=False)

    for s in arvore.statements:
        visitar_stmt(s, topo=True)

    return tabela, erros
