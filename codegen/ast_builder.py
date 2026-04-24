# codegen/ast_builder.py — Parte 4
# Transformação da árvore de derivação (DerivacaoNode) em AST compacta.

from parser.ast_nodes import *
from parser.parser import DerivacaoNode


class ASTBuilder:
    """
    Transforma a DerivacaoNode (parse tree) em AST compacta.
    Percorre a árvore de derivação recursivamente, coletando apenas os nós semânticos.
    """

    def build(self, derivacao: DerivacaoNode) -> ProgramNode:
        return self._build_programa(derivacao)

    def _build_programa(self, node: DerivacaoNode) -> ProgramNode:
        # node.simbolo == "programa"
        # filhos: LPAREN START RPAREN stmts LPAREN END RPAREN
        stmts_node = self._find_child(node, "stmts")
        stmts = self._build_stmts(stmts_node)
        return ProgramNode(stmts)

    def _build_stmts(self, node: DerivacaoNode) -> list[ASTNode]:
        if not node.filhos:
            return []
        resultado = []
        for filho in node.filhos:
            if filho.simbolo == "statement":
                stmt = self._build_statement(filho)
                if stmt is not None:
                    resultado.append(stmt)
            elif filho.simbolo == "stmts":
                resultado.extend(self._build_stmts(filho))
        return resultado

    def _build_statement(self, node: DerivacaoNode) -> ASTNode:
        if not node.filhos:
            return None
        filho = node.filhos[0]
        if filho.simbolo == "expression":
            return self._build_expression(filho)
        elif filho.simbolo == "special_cmd":
            return self._build_special(filho)
        elif filho.simbolo == "control_struct":
            return self._build_control(filho)
        raise ValueError(f"Statement desconhecido: {filho.simbolo}")

    def _build_expression(self, node: DerivacaoNode) -> ASTNode:
        # filhos: LPAREN operand operand arith_op [MEM_NAME] RPAREN
        left = self._build_operand(node.filhos[1])
        right = self._build_operand(node.filhos[2])
        op = node.filhos[3].filhos[0].token.value  # arith_op → terminal
        binop = BinOpNode(op=op, left=left, right=right)

        # Verificar se há MEM_NAME (expressão + store)
        mem_nodes = [f for f in node.filhos if f.simbolo == "MEM_NAME"]
        if mem_nodes:
            return MemWriteNode(name=mem_nodes[0].token.value, value=binop)
        return binop

    def _build_operand(self, node: DerivacaoNode) -> ASTNode:
        if not node.filhos:
            raise ValueError("Operando sem filhos")
        filho = node.filhos[0]
        if filho.simbolo == "INTEGER":
            return NumberNode(value=int(filho.token.value), is_real=False)
        elif filho.simbolo == "REAL":
            return NumberNode(value=float(filho.token.value), is_real=True)
        elif filho.simbolo == "MEM_NAME":
            return MemReadNode(name=filho.token.value)
        elif filho.simbolo == "expression":
            return self._build_expression(filho)
        elif filho.simbolo == "special_cmd":
            # (MEM_NAME) usado como operand — leitura de memória
            return self._build_special(filho)
        raise ValueError(f"Operando desconhecido: {filho.simbolo}")

    def _build_special(self, node: DerivacaoNode) -> ASTNode:
        # Distinguir pelos filhos:
        # (N RES)   → filhos: LPAREN INTEGER RES RPAREN
        # (V MEM)   → filhos: LPAREN operand MEM_NAME RPAREN
        # (MEM)     → filhos: LPAREN MEM_NAME RPAREN

        # Filtrar filhos significativos (sem LPAREN/RPAREN)
        filhos_sig = [f for f in node.filhos if f.simbolo not in ("LPAREN", "RPAREN")]

        if len(filhos_sig) == 1 and filhos_sig[0].simbolo == "MEM_NAME":
            # Leitura de memória: (MEM)
            return MemReadNode(name=filhos_sig[0].token.value)

        if len(filhos_sig) == 2:
            if filhos_sig[1].simbolo == "RES":
                # (N RES)
                n = int(filhos_sig[0].token.value)
                return ResNode(n=n)
            elif filhos_sig[1].simbolo == "MEM_NAME":
                # (V MEM) — escrita
                name = filhos_sig[1].token.value
                
                value = self._build_operand(filhos_sig[0])
                return MemWriteNode(name=name, value=value)

        raise ValueError(f"Comando especial inválido com {len(filhos_sig)} filhos significativos")

    def _build_control(self, node: DerivacaoNode) -> ASTNode:
        filho = node.filhos[0]
        if filho.simbolo == "if_stmt":
            return self._build_if(filho)
        elif filho.simbolo == "while_stmt":
            return self._build_while(filho)
        raise ValueError(f"Controle desconhecido: {filho.simbolo}")

    def _build_if(self, node: DerivacaoNode) -> IfNode:
        cond = self._build_condition(self._find_child(node, "condition"))
        blocks = [f for f in node.filhos if f.simbolo == "block"]
        then_b = self._build_block(blocks[0])
        else_b = self._build_block(blocks[1]) if len(blocks) > 1 else []
        return IfNode(condition=cond, then_block=then_b, else_block=else_b)

    def _build_while(self, node: DerivacaoNode) -> WhileNode:
        cond = self._build_condition(self._find_child(node, "condition"))
        body = self._build_block(self._find_child(node, "block"))
        return WhileNode(condition=cond, body=body)

    def _build_condition(self, node: DerivacaoNode) -> ConditionNode:
        # filhos: operand operand relational_op (sem LPAREN/RPAREN)
        left = self._build_operand(node.filhos[0])
        right = self._build_operand(node.filhos[1])
        op = node.filhos[2].filhos[0].token.value
        return ConditionNode(op=op, left=left, right=right)

    def _build_block(self, node: DerivacaoNode) -> list[ASTNode]:
        # block: LBRACKET stmts RBRACKET
        stmts_node = self._find_child(node, "stmts")
        return self._build_stmts(stmts_node)

    def _find_child(self, node: DerivacaoNode, simbolo: str) -> DerivacaoNode:
        for f in node.filhos:
            if f.simbolo == simbolo:
                return f
        raise ValueError(f"Filho '{simbolo}' não encontrado em '{node.simbolo}'")


def gerarArvore(derivacao: DerivacaoNode) -> ProgramNode:
    """Transforma a árvore de derivação em AST."""
    return ASTBuilder().build(derivacao)


def imprimir_ast(node: ASTNode, nivel: int = 0):
    """Imprime a AST de forma hierárquica no terminal."""
    indent = "  " * nivel
    if isinstance(node, ProgramNode):
        print(f"{indent}Program")
        for s in node.statements:
            imprimir_ast(s, nivel + 1)
    elif isinstance(node, BinOpNode):
        print(f"{indent}BinOp '{node.op}'")
        imprimir_ast(node.left, nivel + 1)
        imprimir_ast(node.right, nivel + 1)
    elif isinstance(node, NumberNode):
        tipo = "REAL" if node.is_real else "INT"
        print(f"{indent}Num({tipo}: {node.value})")
    elif isinstance(node, MemReadNode):
        print(f"{indent}MemRead({node.name})")
    elif isinstance(node, MemWriteNode):
        print(f"{indent}MemWrite({node.name})")
        imprimir_ast(node.value, nivel + 1)
    elif isinstance(node, ResNode):
        print(f"{indent}Res(n={node.n})")
    elif isinstance(node, ConditionNode):
        print(f"{indent}Cond '{node.op}'")
        imprimir_ast(node.left, nivel + 1)
        imprimir_ast(node.right, nivel + 1)
    elif isinstance(node, IfNode):
        print(f"{indent}If")
        print(f"{indent}  [cond]")
        imprimir_ast(node.condition, nivel + 2)
        print(f"{indent}  [then]")
        for s in node.then_block:
            imprimir_ast(s, nivel + 2)
        if node.else_block:
            print(f"{indent}  [else]")
            for s in node.else_block:
                imprimir_ast(s, nivel + 2)
    elif isinstance(node, WhileNode):
        print(f"{indent}While")
        print(f"{indent}  [cond]")
        imprimir_ast(node.condition, nivel + 2)
        print(f"{indent}  [body]")
        for s in node.body:
            imprimir_ast(s, nivel + 2)
