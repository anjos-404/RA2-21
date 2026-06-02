# parser/parser.py — Analisador Sintático Descendente Recursivo LL(1).


from dataclasses import dataclass, field
from lexer.token import Token, TokenType
from grammar.grammar import Gramatica, Producao
from errors.errors import RPNSyntaxError


@dataclass
class DerivacaoNode:
    """Nó da árvore de derivação produzida pelo parser."""
    simbolo: str                             # nome do não-terminal ou terminal
    token: Token | None = None               # preenchido apenas para terminais
    filhos: list["DerivacaoNode"] = field(default_factory=list)
    linha: int = 0

    def is_terminal(self) -> bool:
        return self.token is not None

    def __repr__(self):
        if self.is_terminal():
            return f"[{self.simbolo}={self.token.value}]"
        corpo = ", ".join(repr(f) for f in self.filhos)
        return f"({self.simbolo}: [{corpo}])"


class RecursiveDescentParser:
    """
    Parser descendente recursivo LL(1).
    Cada não-terminal é implementado como uma função recursiva.
    """

    def __init__(self, tokens: list[Token], gramatica: Gramatica):
        self.tokens = tokens
        self.gramatica = gramatica
        self.pos = 0

    def current_token(self) -> Token:
        """Retorna o token atual (ou o último, que é EOF)."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def advance(self):
        """Consome o token atual."""
        self.pos += 1

    def match(self, expected_type: str) -> DerivacaoNode:
        """Casa o token esperado e retorna o nó correspondente."""
        token = self.current_token()
        if token.type.name == expected_type:
            node = DerivacaoNode(expected_type, token=token, linha=token.line)
            if expected_type != "EOF":
                self.advance()
            return node
        else:
            raise RPNSyntaxError(
                f"esperado {expected_type}, encontrado "
                f"{token.type.name} ('{token.value}')",
                line=token.line
            )

    def parse(self) -> DerivacaoNode:
        """
        Executa o parsing descendente recursivo LL(1).
        Retorna a raiz da árvore de derivação.
        """
        raiz = self.parse_programa()
        # Verifica que todos os tokens foram consumidos (exceto EOF)
        token_final = self.current_token()
        if token_final.type != TokenType.EOF:
            raise RPNSyntaxError(
                f"tokens extras após o fim do programa: "
                f"{token_final.type.name} ('{token_final.value}')",
                line=token_final.line
            )
        return raiz

    def parse_programa(self) -> DerivacaoNode:
        raiz = DerivacaoNode("programa")
        start_node = self.match("START")
        stmts_node = self.parse_stmts()
        end_node = self.match("END")
        raiz.filhos = [start_node, stmts_node, end_node]
        return raiz

    def parse_stmts(self) -> DerivacaoNode:
        raiz = DerivacaoNode("stmts")
        token = self.current_token()
        if token.type.name == "LPAREN":  # first of statement
            stmt_node = self.parse_statement()
            stmts_node = self.parse_stmts()
            raiz.filhos = [stmt_node, stmts_node]
        else:
            # epsilon
            raiz.filhos = []
        return raiz

    def parse_statement(self) -> DerivacaoNode:
        raiz = DerivacaoNode("statement")
        lparen_node = self.match("LPAREN")
        stmt_tail_node = self.parse_stmt_tail()
        raiz.filhos = [lparen_node, stmt_tail_node]
        return raiz

    def parse_stmt_tail(self) -> DerivacaoNode:
        raiz = DerivacaoNode("stmt_tail")
        token = self.current_token()
        if token.type.name == "EXPR":
            expr_node = self.match("EXPR")
            op1 = self.parse_operand()
            op2 = self.parse_operand()
            arith = self.parse_arith_op()
            rparen = self.match("RPAREN")
            raiz.filhos = [expr_node, op1, op2, arith, rparen]
        elif token.type.name == "CMD_RES":
            cmd = self.match("CMD_RES")
            int_node = self.match("INTEGER")
            rparen = self.match("RPAREN")
            raiz.filhos = [cmd, int_node, rparen]
        elif token.type.name == "CMD_LOAD":
            cmd = self.match("CMD_LOAD")
            mem = self.match("MEM_NAME")
            rparen = self.match("RPAREN")
            raiz.filhos = [cmd, mem, rparen]
        elif token.type.name == "CMD_STORE":
            cmd = self.match("CMD_STORE")
            op = self.parse_operand()
            mem = self.match("MEM_NAME")
            rparen = self.match("RPAREN")
            raiz.filhos = [cmd, op, mem, rparen]
        elif token.type.name == "IF":
            if_node = self.match("IF")
            cond = self.parse_condition()
            blk = self.parse_block()
            rparen = self.match("RPAREN")
            raiz.filhos = [if_node, cond, blk, rparen]
        elif token.type.name == "IFELSE":
            ifelse_node = self.match("IFELSE")
            cond = self.parse_condition()
            blk1 = self.parse_block()
            blk2 = self.parse_block()
            rparen = self.match("RPAREN")
            raiz.filhos = [ifelse_node, cond, blk1, blk2, rparen]
        elif token.type.name == "WHILE":
            while_node = self.match("WHILE")
            cond = self.parse_condition()
            blk = self.parse_block()
            rparen = self.match("RPAREN")
            raiz.filhos = [while_node, cond, blk, rparen]
        else:
            raise RPNSyntaxError(
                f"token inesperado {token.type.name} em stmt_tail",
                line=token.line
            )
        return raiz

    def parse_operand(self) -> DerivacaoNode:
        raiz = DerivacaoNode("operand")
        token = self.current_token()
        if token.type.name == "INTEGER":
            int_node = self.match("INTEGER")
            raiz.filhos = [int_node]
        elif token.type.name == "REAL":
            real_node = self.match("REAL")
            raiz.filhos = [real_node]
        elif token.type.name == "MEM_NAME":
            mem_node = self.match("MEM_NAME")
            raiz.filhos = [mem_node]
        elif token.type.name == "LPAREN":
            lparen = self.match("LPAREN")
            tail = self.parse_operand_paren_tail()
            raiz.filhos = [lparen, tail]
        else:
            raise RPNSyntaxError(
                f"token inesperado {token.type.name} em operand",
                line=token.line
            )
        return raiz

    def parse_operand_paren_tail(self) -> DerivacaoNode:
        raiz = DerivacaoNode("operand_paren_tail")
        token = self.current_token()
        if token.type.name == "EXPR":
            expr = self.match("EXPR")
            op1 = self.parse_operand()
            op2 = self.parse_operand()
            arith = self.parse_arith_op()
            rparen = self.match("RPAREN")
            raiz.filhos = [expr, op1, op2, arith, rparen]
        elif token.type.name == "CMD_LOAD":
            cmd = self.match("CMD_LOAD")
            mem = self.match("MEM_NAME")
            rparen = self.match("RPAREN")
            raiz.filhos = [cmd, mem, rparen]
        else:
            raise RPNSyntaxError(
                f"token inesperado {token.type.name} em operand_paren_tail",
                line=token.line
            )
        return raiz

    def parse_arith_op(self) -> DerivacaoNode:
        raiz = DerivacaoNode("arith_op")
        token = self.current_token()
        if token.type.name in ["PLUS", "MINUS", "MUL", "DIV_REAL", "DIV_INT", "MOD", "POW"]:
            op_node = self.match(token.type.name)
            raiz.filhos = [op_node]
        else:
            raise RPNSyntaxError(
                f"token inesperado {token.type.name} em arith_op",
                line=token.line
            )
        return raiz

    def parse_relational_op(self) -> DerivacaoNode:
        raiz = DerivacaoNode("relational_op")
        token = self.current_token()
        if token.type.name in ["GT", "LT", "GTE", "LTE", "EQ", "NEQ"]:
            op_node = self.match(token.type.name)
            raiz.filhos = [op_node]
        else:
            raise RPNSyntaxError(
                f"token inesperado {token.type.name} em relational_op",
                line=token.line
            )
        return raiz

    def parse_condition(self) -> DerivacaoNode:
        raiz = DerivacaoNode("condition")
        lparen = self.match("LPAREN")
        op1 = self.parse_operand()
        op2 = self.parse_operand()
        rel = self.parse_relational_op()
        rparen = self.match("RPAREN")
        raiz.filhos = [lparen, op1, op2, rel, rparen]
        return raiz

    def parse_block(self) -> DerivacaoNode:
        raiz = DerivacaoNode("block")
        lbracket = self.match("LBRACKET")
        stmts = self.parse_stmts()
        rbracket = self.match("RBRACKET")
        raiz.filhos = [lbracket, stmts, rbracket]
        return raiz

    # ------------------------------------------------------------------
    # Recuperação de erros (modo pânico com sincronização)
    # ------------------------------------------------------------------
    #
    # Conjunto de sincronização para statements:
    #   - LPAREN em nível 0  -> início do próximo statement
    #   - END                -> fim do programa
    #   - EOF                -> fim da entrada
    #
    # Ao encontrar um erro sintático dentro de um statement, o parser
    # registra a mensagem (com linha e tipo) e descarta tokens até um
    # desses pontos seguros, controlando a profundidade de parênteses e
    # colchetes para não sincronizar dentro de um construto aninhado.
    # Assim a análise PROSSEGUE após o erro e todos os erros sintáticos
    # são reportados em uma única passada, em vez de abortar no primeiro.

    def parse_com_recuperacao(self) -> tuple[DerivacaoNode | None, list[str]]:
        erros: list[str] = []
        raiz = DerivacaoNode("programa")

        # START — registra, mas não aborta, se ausente.
        if self.current_token().type.name == "START":
            raiz.filhos.append(self.match("START"))
        else:
            tok = self.current_token()
            erros.append(str(RPNSyntaxError(
                f"esperado START, encontrado {tok.type.name} ('{tok.value}')",
                line=tok.line)))

        stmts = DerivacaoNode("stmts")
        raiz.filhos.append(stmts)

        # Laço de statements com recuperação em modo pânico.
        while True:
            tok = self.current_token()
            name = tok.type.name
            if name in ("END", "EOF"):
                break
            if name == "LPAREN":
                marca = self.pos
                try:
                    stmts.filhos.append(self.parse_statement())
                except RPNSyntaxError as e:
                    erros.append(str(e))
                    self._sincronizar(marca)
            else:
                # Token solto, fora de qualquer statement.
                erros.append(str(RPNSyntaxError(
                    f"token inesperado {name} ('{tok.value}') "
                    f"fora de um statement",
                    line=tok.line)))
                self._sincronizar(self.pos)

        # END — registra, mas não aborta, se ausente.
        if self.current_token().type.name == "END":
            raiz.filhos.append(self.match("END"))
        else:
            tok = self.current_token()
            erros.append(str(RPNSyntaxError(
                f"esperado END, encontrado {tok.type.name} ('{tok.value}')",
                line=tok.line)))

        # Com erros, retorna a árvore PARCIAL (não None) para permitir
        # inspeção; sem erros, retorna a derivação completa e válida.
        return raiz, erros

    def _sincronizar(self, marca: int):
        """Modo pânico: descarta tokens até o próximo ponto de sincronização.

        Garante progresso (consome ao menos um token se a posição não
        avançou desde o início do statement) para nunca entrar em laço
        infinito, e controla a profundidade de ()/[] para parar no início
        do próximo statement, no fechamento do construto quebrado, no END
        ou no EOF.
        """
        if self.pos == marca:
            self.advance()

        depth = 0
        while True:
            name = self.current_token().type.name
            if name == "EOF":
                return
            if name in ("LPAREN", "LBRACKET"):
                if depth == 0 and name == "LPAREN":
                    return  # início do próximo statement
                depth += 1
                self.advance()
            elif name in ("RPAREN", "RBRACKET"):
                if depth == 0:
                    self.advance()  # fecha o construto quebrado; retoma após ele
                    return
                depth -= 1
                self.advance()
            elif name == "END" and depth == 0:
                return
            else:
                self.advance()


def parsear(tokens: list[Token], gramatica: Gramatica) -> DerivacaoNode:
    """
    Executa análise sintática descendente recursiva LL(1).

    Entrada:
        tokens    — lista de tokens gerada por lerTokens()
        gramatica — objeto Gramatica com tabela LL(1) construída

    Saída:
        DerivacaoNode — raiz da árvore de derivação

    Lança:
        RPNSyntaxError — com linha e descrição do erro sintático
    """
    parser = RecursiveDescentParser(tokens, gramatica)
    return parser.parse()


def parsear_com_recuperacao(
    tokens: list[Token], gramatica: Gramatica
) -> tuple[DerivacaoNode | None, list[str]]:
    """Análise sintática com recuperação de erros em modo pânico.

    Diferente de parsear(), NÃO aborta no primeiro erro: registra cada
    erro sintático (com linha e tipo), sincroniza no início do próximo
    statement e continua, de modo a reportar TODOS os erros encontrados
    em uma única passada.

    Saída:
        (raiz, erros) — a árvore de derivação (parcial, se houve erros)
        e a lista de mensagens de erro. Sem erros, `erros` é vazia e a
        árvore é a derivação completa.
    """
    parser = RecursiveDescentParser(tokens, gramatica)
    return parser.parse_com_recuperacao()
