# codegen/ast_builder.py — Transformação da árvore de derivação em AST.
#
# A árvore de derivação (DerivacaoNode) segue EXATAMENTE a estrutura das
# produções da gramática. 
# # marcadores (EXPR, CMD_*, IF, etc.) e nós intermediários.

from parser.ast_nodes import (
    ASTNode, ProgramNode, BinOpNode, NumberNode,
    MemReadNode, MemWriteNode, ResNode,
    ConditionNode, IfNode, WhileNode, BlockNode
)
from parser.parser import DerivacaoNode


SIMBOLOS_SINTATICOS = {
    "LPAREN", "RPAREN", "LBRACKET", "RBRACKET",
    "START", "END",
    "EXPR", "CMD_RES", "CMD_LOAD", "CMD_STORE",
    "IF", "IFELSE", "WHILE",
    "EOF",
}


class ASTBuilder:
    """Percorre a árvore de derivação e constrói a AST."""

    def build(self, derivacao: DerivacaoNode) -> ProgramNode:
        # programa → START stmts END
        stmts_node = self._filho(derivacao, "stmts")
        stmts = self._build_stmts(stmts_node)
        return ProgramNode(stmts)

    def _build_stmts(self, node: DerivacaoNode) -> list[ASTNode]:
        """stmts → statement stmts | ε"""
        resultado: list[ASTNode] = []
        while node.filhos:
            # Primeiro filho é statement (caso não-epsilon)
            primeiro = node.filhos[0]
            if primeiro.simbolo == "statement":
                stmt = self._build_statement(primeiro)
                resultado.append(stmt)
                # Segundo filho é stmts (recursivo)
                node = node.filhos[1]
            else:
                break
        return resultado

    def _build_statement(self, node: DerivacaoNode) -> ASTNode:
        """statement → LPAREN stmt_tail"""
        # filhos[0] = LPAREN (descartado)
        # filhos[1] = stmt_tail
        stmt_tail = node.filhos[1]
        return self._build_stmt_tail(stmt_tail)

    def _build_stmt_tail(self, node: DerivacaoNode) -> ASTNode:
        """
        stmt_tail pode ser:
          EXPR operand operand arith_op RPAREN
          CMD_RES INTEGER RPAREN
          CMD_LOAD MEM_NAME RPAREN
          CMD_STORE operand MEM_NAME RPAREN
          IF condition block RPAREN
          IFELSE condition block block RPAREN
          WHILE condition block RPAREN
        """
        primeiro = node.filhos[0].simbolo

        if primeiro == "EXPR":
            # EXPR operand operand arith_op RPAREN
            left  = self._build_operand(node.filhos[1])
            right = self._build_operand(node.filhos[2])
            op    = self._build_arith_op(node.filhos[3])
            return BinOpNode(op=op, left=left, right=right)

        elif primeiro == "CMD_RES":
            # CMD_RES INTEGER RPAREN
            n = int(node.filhos[1].token.value)
            return ResNode(n=n)

        elif primeiro == "CMD_LOAD":
            # CMD_LOAD MEM_NAME RPAREN
            nome = node.filhos[1].token.value
            return MemReadNode(name=nome)

        elif primeiro == "CMD_STORE":
            # CMD_STORE operand MEM_NAME RPAREN
            valor = self._build_operand(node.filhos[1])
            nome  = node.filhos[2].token.value
            return MemWriteNode(name=nome, value=valor)

        elif primeiro == "IF":
            # IF condition block RPAREN
            cond  = self._build_condition(node.filhos[1])
            then_ = self._build_block(node.filhos[2])
            return IfNode(condition=cond, then_block=then_, else_block=[])

        elif primeiro == "IFELSE":
            # IFELSE condition block block RPAREN
            cond  = self._build_condition(node.filhos[1])
            then_ = self._build_block(node.filhos[2])
            else_ = self._build_block(node.filhos[3])
            return IfNode(condition=cond, then_block=then_, else_block=else_)

        elif primeiro == "WHILE":
            # WHILE condition block RPAREN
            cond = self._build_condition(node.filhos[1])
            body = self._build_block(node.filhos[2])
            return WhileNode(condition=cond, body=body)

        raise ValueError(f"stmt_tail desconhecido: começa com {primeiro}")

    def _build_operand(self, node: DerivacaoNode) -> ASTNode:
        """
        operand → INTEGER | REAL | MEM_NAME | LPAREN operand_paren_tail
        """
        filho = node.filhos[0]

        if filho.simbolo == "INTEGER":
            return NumberNode(value=int(filho.token.value), is_real=False)
        if filho.simbolo == "REAL":
            return NumberNode(value=float(filho.token.value), is_real=True)
        if filho.simbolo == "MEM_NAME":
            return MemReadNode(name=filho.token.value)
        if filho.simbolo == "LPAREN":
            # operand → LPAREN operand_paren_tail
            paren_tail = node.filhos[1]
            return self._build_operand_paren_tail(paren_tail)

        raise ValueError(f"operand desconhecido: {filho.simbolo}")

    def _build_operand_paren_tail(self, node: DerivacaoNode) -> ASTNode:
        """
        operand_paren_tail → EXPR operand operand arith_op RPAREN
                           | CMD_LOAD MEM_NAME RPAREN
        """
        primeiro = node.filhos[0].simbolo

        if primeiro == "EXPR":
            left  = self._build_operand(node.filhos[1])
            right = self._build_operand(node.filhos[2])
            op    = self._build_arith_op(node.filhos[3])
            return BinOpNode(op=op, left=left, right=right)

        if primeiro == "CMD_LOAD":
            nome = node.filhos[1].token.value
            return MemReadNode(name=nome)

        raise ValueError(f"operand_paren_tail desconhecido: {primeiro}")

    def _build_arith_op(self, node: DerivacaoNode) -> str:
        """arith_op → PLUS | MINUS | MUL | DIV_REAL | DIV_INT | MOD | POW"""
        return node.filhos[0].token.value

    def _build_relational_op(self, node: DerivacaoNode) -> str:
        """relational_op → GT | LT | GTE | LTE | EQ | NEQ"""
        return node.filhos[0].token.value

    def _build_condition(self, node: DerivacaoNode) -> ConditionNode:
        """condition → LPAREN operand operand relational_op RPAREN"""
        # filhos: [LPAREN, operand, operand, relational_op, RPAREN]
        left  = self._build_operand(node.filhos[1])
        right = self._build_operand(node.filhos[2])
        op    = self._build_relational_op(node.filhos[3])
        return ConditionNode(op=op, left=left, right=right)

    def _build_block(self, node: DerivacaoNode) -> list[ASTNode]:
        """block → LBRACKET stmts RBRACKET"""
        stmts_node = self._filho(node, "stmts")
        return self._build_stmts(stmts_node)

    def _filho(self, node: DerivacaoNode, simbolo: str) -> DerivacaoNode:
        for f in node.filhos:
            if f.simbolo == simbolo:
                return f
        raise ValueError(
            f"filho '{simbolo}' não encontrado em '{node.simbolo}'"
        )


def gerarArvore(derivacao: DerivacaoNode) -> ProgramNode:
    """Transforma a árvore de derivação em AST."""
    return ASTBuilder().build(derivacao)


def imprimir_ast(node: ASTNode, nivel: int = 0):
    """Imprime a AST hierarquicamente no terminal."""
    ind = "  " * nivel
    if isinstance(node, ProgramNode):
        print(f"{ind}Program")
        for s in node.statements:
            imprimir_ast(s, nivel + 1)
    elif isinstance(node, BinOpNode):
        print(f"{ind}BinOp '{node.op}'")
        imprimir_ast(node.left, nivel + 1)
        imprimir_ast(node.right, nivel + 1)
    elif isinstance(node, NumberNode):
        tipo = "REAL" if node.is_real else "INT"
        print(f"{ind}Num({tipo}: {node.value})")
    elif isinstance(node, MemReadNode):
        print(f"{ind}MemRead({node.name})")
    elif isinstance(node, MemWriteNode):
        print(f"{ind}MemWrite({node.name})")
        imprimir_ast(node.value, nivel + 1)
    elif isinstance(node, ResNode):
        print(f"{ind}Res(n={node.n})")
    elif isinstance(node, ConditionNode):
        print(f"{ind}Cond '{node.op}'")
        imprimir_ast(node.left, nivel + 1)
        imprimir_ast(node.right, nivel + 1)
    elif isinstance(node, IfNode):
        print(f"{ind}If")
        print(f"{ind}  [cond]")
        imprimir_ast(node.condition, nivel + 2)
        print(f"{ind}  [then]")
        for s in node.then_block:
            imprimir_ast(s, nivel + 2)
        if node.else_block:
            print(f"{ind}  [else]")
            for s in node.else_block:
                imprimir_ast(s, nivel + 2)
    elif isinstance(node, WhileNode):
        print(f"{ind}While")
        print(f"{ind}  [cond]")
        imprimir_ast(node.condition, nivel + 2)
        print(f"{ind}  [body]")
        for s in node.body:
            imprimir_ast(s, nivel + 2)
