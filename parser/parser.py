# parser/parser.py — Analisador Sintático LL(1) Tabular.


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


class ParserLL1:
    """
    Parser LL(1) tabular preditivo puro.
    Não usa lookahead > 1, não usa backtracking, não tem casos especiais.
    Todas as decisões são tomadas pela tabela M[A, a].
    """

    def __init__(self, tokens: list[Token], gramatica: Gramatica):
        self.tokens = tokens
        self.gramatica = gramatica
        self.pos = 0

    def token_atual(self) -> Token:
        """Retorna o token atual (ou o último, que é EOF)."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def avancar(self):
        """Consome o token atual."""
        self.pos += 1

    def parse(self) -> DerivacaoNode:
        """
        Executa o parsing LL(1) tabular.
        Retorna a raiz da árvore de derivação.
        """
        # Construção da árvore: cada entrada na pilha é (símbolo, nó_da_árvore)
        raiz = DerivacaoNode(self.gramatica.simbolo_inicial)

        # A pilha armazena nós da árvore; o último é o topo.
        # Começa com o símbolo inicial (que é um não-terminal).
        pilha: list[DerivacaoNode] = [raiz]

        while pilha:
            topo = pilha.pop()
            simbolo = topo.simbolo
            token = self.token_atual()
            token_tipo = token.type.name

            if simbolo in self.gramatica.terminais:
                # Terminal: deve casar com o token atual
                if simbolo == token_tipo:
                    topo.token = token
                    topo.linha = token.line
                    if simbolo != "EOF":
                        self.avancar()
                else:
                    raise RPNSyntaxError(
                        f"esperado {simbolo}, encontrado "
                        f"{token_tipo} ('{token.value}')",
                        line=token.line
                    )
            elif simbolo in self.gramatica.nao_terminais:
                # Não-terminal: consulta a tabela M[A, a]
                chave = (simbolo, token_tipo)
                producao = self.gramatica.tabela.get(chave)
                if producao is None:
                    raise RPNSyntaxError(
                        f"token inesperado {token_tipo} ('{token.value}') "
                        f"durante expansão de '{simbolo}'. "
                        f"Não há produção em M[{simbolo}, {token_tipo}].",
                        line=token.line
                    )
                # Cria os nós filhos com os símbolos do corpo da produção
                filhos = [DerivacaoNode(s) for s in producao.corpo]
                topo.filhos = filhos
                # Empilha em ordem reversa para processar da esquerda pra direita
                for filho in reversed(filhos):
                    pilha.append(filho)
            else:
                raise RPNSyntaxError(
                    f"símbolo desconhecido '{simbolo}' na gramática",
                    line=token.line
                )

        # Verifica que todos os tokens foram consumidos (exceto EOF)
        token_final = self.token_atual()
        if token_final.type != TokenType.EOF:
            raise RPNSyntaxError(
                f"tokens extras após o fim do programa: "
                f"{token_final.type.name} ('{token_final.value}')",
                line=token_final.line
            )

        return raiz


def parsear(tokens: list[Token], gramatica: Gramatica) -> DerivacaoNode:
    """
    Executa análise sintática LL(1) preditiva tabular.

    Entrada:
        tokens    — lista de tokens gerada por lerTokens()
        gramatica — objeto Gramatica com tabela LL(1) construída

    Saída:
        DerivacaoNode — raiz da árvore de derivação

    Lança:
        RPNSyntaxError — com linha e descrição do erro sintático
    """
    parser = ParserLL1(tokens, gramatica)
    return parser.parse()


def parsear_com_recuperacao(
    tokens: list[Token], gramatica: Gramatica
) -> tuple[DerivacaoNode | None, list[str]]:
    """Versão que captura o primeiro erro e retorna lista de mensagens."""
    erros = []
    try:
        return parsear(tokens, gramatica), erros
    except RPNSyntaxError as e:
        erros.append(str(e))
        return None, erros
