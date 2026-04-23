# parser/parser.py — Parte 2

from dataclasses import dataclass, field
from lexer.token import Token, TokenType
from grammar.grammar import Gramatica, Producao
from parser.ast_nodes import *


@dataclass
class DerivacaoNode:
    """
    Nó na árvore de derivação (parse tree).
    Diferente da AST — representa a derivação gramatical completa.
    """
    simbolo: str                          # nome do não-terminal ou terminal
    token: Token | None = None            # preenchido apenas para terminais
    filhos: list["DerivacaoNode"] = field(default_factory=list)
    linha: int = 0

    def is_terminal(self) -> bool:
        return self.token is not None

    def __repr__(self):
        if self.is_terminal():
            return f"[{self.simbolo}={self.token.value}]"
        return f"({self.simbolo}: {self.filhos})"


class ParserRecursivo:
    """
    Parser descendente recursivo para a linguagem RPN.
    Resolve ambiguidades (expression vs special_cmd vs control_struct)
    por lookahead de profundidade variável.
    """

    def __init__(self, tokens: list[Token], gramatica: Gramatica):
        self.tokens = tokens
        self.gramatica = gramatica
        self.pos = 0
        self.derivacao_log: list[str] = []

    def atual(self) -> Token:
        """Retorna o token na posição atual."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF

    def peek(self, offset: int = 0) -> Token:
        """Olha N tokens à frente sem consumir."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def consumir(self, tipo: TokenType) -> Token:
        """Consome e retorna o token atual se for do tipo esperado."""
        t = self.atual()
        if t.type != tipo:
            raise SyntaxError(
                f"Linha {t.line}: esperado {tipo.name}, encontrado '{t.value}' ({t.type.name})"
            )
        self.pos += 1
        return t

    def parse_programa(self) -> DerivacaoNode:
        """programa ::= '(' START ')' { statement } '(' END ')'"""
        raiz = DerivacaoNode("programa")

        lp1 = self.consumir(TokenType.LPAREN)
        raiz.filhos.append(DerivacaoNode("LPAREN", token=lp1, linha=lp1.line))

        start = self.consumir(TokenType.START)
        raiz.filhos.append(DerivacaoNode("START", token=start, linha=start.line))

        rp1 = self.consumir(TokenType.RPAREN)
        raiz.filhos.append(DerivacaoNode("RPAREN", token=rp1, linha=rp1.line))

        # Parse stmts
        stmts_node = DerivacaoNode("stmts")
        self._parse_stmts(stmts_node)
        raiz.filhos.append(stmts_node)

        lp2 = self.consumir(TokenType.LPAREN)
        raiz.filhos.append(DerivacaoNode("LPAREN", token=lp2, linha=lp2.line))

        end = self.consumir(TokenType.END)
        raiz.filhos.append(DerivacaoNode("END", token=end, linha=end.line))

        rp2 = self.consumir(TokenType.RPAREN)
        raiz.filhos.append(DerivacaoNode("RPAREN", token=rp2, linha=rp2.line))

        return raiz

    def _parse_stmts(self, stmts_node: DerivacaoNode):
        """stmts ::= statement stmts | ε"""
        while self.atual().type not in (TokenType.EOF, TokenType.RBRACKET):
            # Verifica se os próximos tokens são '(' END ')'
            if self._proximo_e_end():
                break
            stmt_node = DerivacaoNode("statement")
            self._parse_statement(stmt_node)
            stmts_node.filhos.append(stmt_node)

            # Cria stmts recursivo
            next_stmts = DerivacaoNode("stmts")
            stmts_node.filhos.append(next_stmts)
            stmts_node = next_stmts

    def _proximo_e_end(self) -> bool:
        """Lookahead: verifica se os próximos tokens são '(' END ')'."""
        if self.pos + 1 >= len(self.tokens):
            return False
        return (self.tokens[self.pos].type == TokenType.LPAREN and
                self.tokens[self.pos + 1].type == TokenType.END)

    def _parse_statement(self, stmt_node: DerivacaoNode):
        """
        statement ::= expression | special_cmd | control_struct
        Usa lookahead para distinguir.
        """
        if self.atual().type != TokenType.LPAREN:
            raise SyntaxError(
                f"Linha {self.atual().line}: esperado '(' no início do statement, "
                f"encontrado '{self.atual().value}'"
            )

        # Determinar qual tipo de statement temos por lookahead
        tipo = self._classificar_statement()

        if tipo == "special_res":
            node = self._parse_special_res()
            stmt_node.filhos.append(node)
        elif tipo == "special_mem_read":
            node = self._parse_special_mem_read()
            stmt_node.filhos.append(node)
        elif tipo == "special_mem_write":
            node = self._parse_special_mem_write()
            stmt_node.filhos.append(node)
        elif tipo == "control":
            node = self._parse_control_struct()
            stmt_node.filhos.append(node)
        else:
            node = self._parse_expression()
            stmt_node.filhos.append(node)

    def _classificar_statement(self) -> str:
        """
        Classifica o statement usando lookahead para resolver ambiguidades.
        Retorna: 'special_res', 'special_mem_read', 'special_mem_write', 'control', 'expression'

        Regras de classificação:
        1. (INTEGER RES )          → special_res
        2. (MEM_NAME )             → special_mem_read
        3. (operand MEM_NAME )     → special_mem_write
        4. (condição [bloco] ...)  → control (IF/IFELSE/WHILE)
        5. (operand operand op )   → expression
        """
        prox1 = self.peek(1)

        # 1. (INTEGER RES) → special_res
        if prox1.type == TokenType.INTEGER:
            prox2 = self.peek(2)
            if prox2.type == TokenType.RES:
                return "special_res"

        # 2. (MEM_NAME ')') → special_mem_read
        if prox1.type == TokenType.MEM_NAME:
            prox2 = self.peek(2)
            if prox2.type == TokenType.RPAREN:
                return "special_mem_read"

        # 4. Verificar se é estrutura de controle (tem '[' no nível 1)
        if self._e_controle():
            return "control"

        # 3. Verificar se é escrita em memória: (operand MEM_NAME )
        # O operand pode ser: INTEGER, REAL, MEM_NAME, ou expressão aninhada (...)
        if self._e_mem_write():
            return "special_mem_write"

        # 5. Caso padrão: expressão aritmética
        return "expression"

    def _e_mem_write(self) -> bool:
        """
        Verifica se o statement é uma escrita em memória: (operand MEM_NAME )
        Faz scan forward para pular o operand e verificar se o próximo é MEM_NAME.
        """
        prox1 = self.peek(1)

        # Determinar onde termina o primeiro operand
        if prox1.type in (TokenType.INTEGER, TokenType.REAL, TokenType.MEM_NAME):
            # Operand simples: próximo token após ele
            token_apos_operand = self.peek(2)
        elif prox1.type == TokenType.LPAREN:
            # Operand é uma sub-expressão: precisamos encontrar o ) correspondente
            nivel = 0
            idx = self.pos + 1
            while idx < len(self.tokens):
                t = self.tokens[idx]
                if t.type == TokenType.LPAREN:
                    nivel += 1
                elif t.type == TokenType.RPAREN:
                    nivel -= 1
                    if nivel == 0:
                        idx += 1
                        break
                elif t.type == TokenType.EOF:
                    return False
                idx += 1
            if idx >= len(self.tokens):
                return False
            token_apos_operand = self.tokens[idx]
        else:
            return False

        # O token após o operand deve ser MEM_NAME, e o seguinte ')'
        if token_apos_operand.type == TokenType.MEM_NAME:
            return True
        return False

    def _e_controle(self) -> bool:
        """
        Verifica se o statement atual é uma estrutura de controle.
        Faz scan forward para encontrar '[' antes de ')' no nível correto.
        """
        nivel = 0
        idx = self.pos

        while idx < len(self.tokens):
            t = self.tokens[idx]
            if t.type == TokenType.LPAREN:
                nivel += 1
            elif t.type == TokenType.RPAREN:
                nivel -= 1
                if nivel == 0:
                    break
            elif t.type == TokenType.LBRACKET and nivel == 1:
                return True
            elif t.type == TokenType.EOF:
                break
            idx += 1

        return False

    def _parse_expression(self) -> DerivacaoNode:
        """
        expression ::= '(' operand operand arith_op ')'
                     | '(' operand operand arith_op MEM_NAME ')'  (expression+store)
        O segundo formato é uma extensão: calcula a expressão e armazena em MEM_NAME.
        """
        node = DerivacaoNode("expression")

        lp = self.consumir(TokenType.LPAREN)
        node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))

        left = self._parse_operand()
        node.filhos.append(left)

        right = self._parse_operand()
        node.filhos.append(right)

        op_node = self._parse_arith_op()
        node.filhos.append(op_node)

        # Verificar se há MEM_NAME após o operador (expressão + store)
        if self.atual().type == TokenType.MEM_NAME:
            mem = self.consumir(TokenType.MEM_NAME)
            node.filhos.append(DerivacaoNode("MEM_NAME", token=mem, linha=mem.line))

        rp = self.consumir(TokenType.RPAREN)
        node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))

        return node

    def _parse_operand(self) -> DerivacaoNode:
        """
        operand ::= INTEGER | REAL | MEM_NAME | expression | '(' MEM_NAME ')'
        Nota: (MEM_NAME) é tratado como leitura de memória quando usado como operand.
        """
        node = DerivacaoNode("operand")
        t = self.atual()

        if t.type == TokenType.INTEGER:
            self.pos += 1
            node.filhos.append(DerivacaoNode("INTEGER", token=t, linha=t.line))
        elif t.type == TokenType.REAL:
            self.pos += 1
            node.filhos.append(DerivacaoNode("REAL", token=t, linha=t.line))
        elif t.type == TokenType.MEM_NAME:
            self.pos += 1
            node.filhos.append(DerivacaoNode("MEM_NAME", token=t, linha=t.line))
        elif t.type == TokenType.LPAREN:
            # Verificar se é (MEM_NAME) — leitura de memória como operand
            prox = self.peek(1)
            prox2 = self.peek(2)
            if prox.type == TokenType.MEM_NAME and prox2.type == TokenType.RPAREN:
                # (MEM_NAME) — leitura de memória embutida como operand
                # Criamos um nó special_cmd dentro do operand
                mem_read_node = DerivacaoNode("special_cmd")
                lp = self.consumir(TokenType.LPAREN)
                mem_read_node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))
                mem = self.consumir(TokenType.MEM_NAME)
                mem_read_node.filhos.append(DerivacaoNode("MEM_NAME", token=mem, linha=mem.line))
                rp = self.consumir(TokenType.RPAREN)
                mem_read_node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))
                node.filhos.append(mem_read_node)
            else:
                # Sub-expressão aninhada: (operand operand arith_op)
                expr = self._parse_expression()
                node.filhos.append(expr)
        else:
            raise SyntaxError(
                f"Linha {t.line}: operando inválido '{t.value}' ({t.type.name})"
            )

        return node

    def _parse_arith_op(self) -> DerivacaoNode:
        """arith_op ::= '+' | '-' | '*' | '|' | '/' | '%' | '^'"""
        node = DerivacaoNode("arith_op")
        t = self.atual()
        ops = {
            TokenType.PLUS, TokenType.MINUS, TokenType.MUL,
            TokenType.DIV_REAL, TokenType.DIV_INT, TokenType.MOD, TokenType.POW
        }
        if t.type in ops:
            self.pos += 1
            node.filhos.append(DerivacaoNode(t.type.name, token=t, linha=t.line))
            return node
        raise SyntaxError(
            f"Linha {t.line}: operador aritmético esperado, encontrado '{t.value}' ({t.type.name})"
        )

    def _parse_relational_op(self) -> DerivacaoNode:
        """relational_op ::= '>' | '<' | '>=' | '<=' | '==' | '!='"""
        node = DerivacaoNode("relational_op")
        t = self.atual()
        ops = {
            TokenType.GT, TokenType.LT, TokenType.GTE,
            TokenType.LTE, TokenType.EQ, TokenType.NEQ
        }
        if t.type in ops:
            self.pos += 1
            node.filhos.append(DerivacaoNode(t.type.name, token=t, linha=t.line))
            return node
        raise SyntaxError(
            f"Linha {t.line}: operador relacional esperado, encontrado '{t.value}' ({t.type.name})"
        )

    def _parse_condition(self) -> DerivacaoNode:
        """
        condition ::= operand operand relational_op
        a condição é parseada SEM parênteses próprios —
        os parênteses externos pertencem ao if_stmt/while_stmt.
        """
        node = DerivacaoNode("condition")

        left = self._parse_operand()
        node.filhos.append(left)

        right = self._parse_operand()
        node.filhos.append(right)

        relop = self._parse_relational_op()
        node.filhos.append(relop)

        return node

    def _parse_block(self) -> DerivacaoNode:
        """block ::= '[' stmts ']'"""
        node = DerivacaoNode("block")

        lb = self.consumir(TokenType.LBRACKET)
        node.filhos.append(DerivacaoNode("LBRACKET", token=lb, linha=lb.line))

        stmts_node = DerivacaoNode("stmts")
        self._parse_stmts(stmts_node)
        node.filhos.append(stmts_node)

        rb = self.consumir(TokenType.RBRACKET)
        node.filhos.append(DerivacaoNode("RBRACKET", token=rb, linha=rb.line))

        return node

    def _parse_control_struct(self) -> DerivacaoNode:
        """control_struct ::= if_stmt | while_stmt"""
        node = DerivacaoNode("control_struct")

        lp = self.consumir(TokenType.LPAREN)

        cond = self._parse_condition()
        block_then = self._parse_block()

        if self.atual().type == TokenType.LBRACKET:
            # IFELSE: (condition [bloco_then] [bloco_else] IFELSE)
            block_else = self._parse_block()
            kw = self.consumir(TokenType.IFELSE)
            rp = self.consumir(TokenType.RPAREN)

            if_node = DerivacaoNode("if_stmt")
            if_node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))
            if_node.filhos.append(cond)
            if_node.filhos.append(block_then)
            if_node.filhos.append(block_else)
            if_node.filhos.append(DerivacaoNode("IFELSE", token=kw, linha=kw.line))
            if_node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))
            node.filhos.append(if_node)

        elif self.atual().type == TokenType.IF:
            # IF: (condition [bloco_then] IF)
            kw = self.consumir(TokenType.IF)
            rp = self.consumir(TokenType.RPAREN)

            if_node = DerivacaoNode("if_stmt")
            if_node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))
            if_node.filhos.append(cond)
            if_node.filhos.append(block_then)
            if_node.filhos.append(DerivacaoNode("IF", token=kw, linha=kw.line))
            if_node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))
            node.filhos.append(if_node)

        elif self.atual().type == TokenType.WHILE:
            # WHILE: (condition [bloco] WHILE)
            kw = self.consumir(TokenType.WHILE)
            rp = self.consumir(TokenType.RPAREN)

            while_node = DerivacaoNode("while_stmt")
            while_node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))
            while_node.filhos.append(cond)
            while_node.filhos.append(block_then)
            while_node.filhos.append(DerivacaoNode("WHILE", token=kw, linha=kw.line))
            while_node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))
            node.filhos.append(while_node)

        else:
            raise SyntaxError(
                f"Linha {self.atual().line}: esperado IF, IFELSE ou WHILE, "
                f"encontrado '{self.atual().value}' ({self.atual().type.name})"
            )

        return node

    def _parse_special_res(self) -> DerivacaoNode:
        """special_cmd ::= '(' INTEGER RES ')'"""
        node = DerivacaoNode("special_cmd")

        lp = self.consumir(TokenType.LPAREN)
        node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))

        n = self.consumir(TokenType.INTEGER)
        node.filhos.append(DerivacaoNode("INTEGER", token=n, linha=n.line))

        res = self.consumir(TokenType.RES)
        node.filhos.append(DerivacaoNode("RES", token=res, linha=res.line))

        rp = self.consumir(TokenType.RPAREN)
        node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))

        return node

    def _parse_special_mem_read(self) -> DerivacaoNode:
        """special_cmd ::= '(' MEM_NAME ')'"""
        node = DerivacaoNode("special_cmd")

        lp = self.consumir(TokenType.LPAREN)
        node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))

        mem = self.consumir(TokenType.MEM_NAME)
        node.filhos.append(DerivacaoNode("MEM_NAME", token=mem, linha=mem.line))

        rp = self.consumir(TokenType.RPAREN)
        node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))

        return node

    def _parse_special_mem_write(self) -> DerivacaoNode:
        """special_cmd ::= '(' operand MEM_NAME ')'"""
        node = DerivacaoNode("special_cmd")

        lp = self.consumir(TokenType.LPAREN)
        node.filhos.append(DerivacaoNode("LPAREN", token=lp, linha=lp.line))

        operand = self._parse_operand()
        node.filhos.append(operand)

        mem = self.consumir(TokenType.MEM_NAME)
        node.filhos.append(DerivacaoNode("MEM_NAME", token=mem, linha=mem.line))

        rp = self.consumir(TokenType.RPAREN)
        node.filhos.append(DerivacaoNode("RPAREN", token=rp, linha=rp.line))

        return node


def parsear(tokens: list[Token], gramatica: Gramatica) -> DerivacaoNode:
    """
    Realiza análise sintática usando parser descendente recursivo com lookahead.

    Entrada:
        tokens    — lista de tokens gerada por lerTokens()
        gramatica — objeto Gramatica com tabela LL(1) (gerado por construirGramatica())

    Saída:
        DerivacaoNode — raiz da estrutura de derivação (para gerarArvore())

    Levanta:
        SyntaxError — com número de linha e descrição do erro
    """
    parser = ParserRecursivo(tokens, gramatica)
    return parser.parse_programa()


def parsear_com_recuperacao(tokens: list[Token], gramatica: Gramatica) -> tuple[DerivacaoNode | None, list[str]]:

    erros = []
    try:
        parser = ParserRecursivo(tokens, gramatica)
        arvore = parser.parse_programa()
        return arvore, erros
    except SyntaxError as e:
        erros.append(str(e))
        return None, erros
