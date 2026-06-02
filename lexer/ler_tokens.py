# lexer/ler_tokens.py — Analisador Léxico.
# Lê o arquivo-fonte e produz a lista de Tokens.

from lexer.token import Token, TokenType
from errors.errors import LexicalError


# Keywords reconhecidas (palavras reservadas da linguagem)
KEYWORDS = {
    "START":     TokenType.START,
    "END":       TokenType.END,
    "EXPR":      TokenType.EXPR,
    "CMD_RES":   TokenType.CMD_RES,
    "CMD_LOAD":  TokenType.CMD_LOAD,
    "CMD_STORE": TokenType.CMD_STORE,
    "IF":        TokenType.IF,
    "IFELSE":    TokenType.IFELSE,
    "WHILE":     TokenType.WHILE,
}

# Operadores de 2 caracteres (verificar antes dos de 1)
OPS_DUPLOS = {
    ">=": TokenType.GTE,
    "<=": TokenType.LTE,
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
}

# Operadores e delimitadores de 1 caractere
OPS_SIMPLES = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MUL,
    "|": TokenType.DIV_REAL,
    "/": TokenType.DIV_INT,
    "%": TokenType.MOD,
    "^": TokenType.POW,
    ">": TokenType.GT,
    "<": TokenType.LT,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
}


def lerTokens(arquivo: str, incluir_comentarios: bool = False) -> list[Token]:
    """
    Entrada:
        arquivo               — caminho do arquivo-fonte (.txt).
        incluir_comentarios   — se True, emite tokens TokenType.COMMENT para os
                                comentários; se False (padrão), eles são apenas
                                reconhecidos e descartados, sem chegar ao parser.
    Saída: list[Token] pronto para ser consumido pelo parser.
    Lança: LexicalError se encontrar token desconhecido ou comentário não fechado.

    Comentários (Fase 3): a linguagem usa *{ para iniciar e }* para encerrar um
    comentário. Comentários podem ocupar linhas inteiras, aparecer no fim de uma
    linha de código ou entre expressões, e podem se estender por várias linhas.
    O analisador léxico os reconhece como tokens de tipo "comentário" e os
    descarta durante a geração do vetor de tokens, de modo que não interferem nas
    análises sintática e semântica. (O comentário de linha '#' também é aceito.)
    """
    tokens: list[Token] = []

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: '{arquivo}'")

    linha = 1
    i = 0
    n = len(conteudo)

    while i < n:
        c = conteudo[i]

        # Quebra de linha
        if c == "\n":
            linha += 1
            i += 1
            continue

        # Espaços em branco
        if c in (" ", "\t", "\r"):
            i += 1
            continue

        # Comentário de bloco: *{ ... }* (pode ser multilinha)
        # Precede o operador '*' (MUL): '*{' é sempre início de comentário.
        if c == "*" and i + 1 < n and conteudo[i + 1] == "{":
            linha_inicio = linha
            i += 2
            inicio_txt = i
            fechado = False
            while i < n:
                if conteudo[i] == "}" and i + 1 < n and conteudo[i + 1] == "*":
                    fechado = True
                    break
                if conteudo[i] == "\n":
                    linha += 1
                i += 1
            if not fechado:
                raise LexicalError(
                    "Comentário não terminado (esperado '}*')",
                    line=linha_inicio,
                )
            if incluir_comentarios:
                texto = conteudo[inicio_txt:i]
                tokens.append(Token(TokenType.COMMENT, texto, linha_inicio))
            i += 2  # consome o '}*'
            continue

        # Comentário: # até fim da linha
        if c == "#":
            inicio_txt = i + 1
            while i < n and conteudo[i] != "\n":
                i += 1
            if incluir_comentarios:
                tokens.append(
                    Token(TokenType.COMMENT, conteudo[inicio_txt:i], linha)
                )
            continue

        # Operadores duplos (>=, <=, ==, !=)
        if i + 1 < n:
            par = conteudo[i:i+2]
            if par in OPS_DUPLOS:
                tokens.append(Token(OPS_DUPLOS[par], par, linha))
                i += 2
                continue

        # Operadores / delimitadores simples
        if c in OPS_SIMPLES:
            tokens.append(Token(OPS_SIMPLES[c], c, linha))
            i += 1
            continue

        # Números (inteiros ou reais)
        if c.isdigit() or (c == "." and i + 1 < n and conteudo[i+1].isdigit()):
            inicio = i
            tem_ponto = False
            while i < n and (conteudo[i].isdigit() or conteudo[i] == "."):
                if conteudo[i] == ".":
                    if tem_ponto:
                        raise LexicalError(
                            f"Número malformado: '{conteudo[inicio:i+1]}'",
                            line=linha
                        )
                    tem_ponto = True
                i += 1
            valor_str = conteudo[inicio:i]
            if tem_ponto:
                tokens.append(Token(TokenType.REAL, float(valor_str), linha))
            else:
                tokens.append(Token(TokenType.INTEGER, int(valor_str), linha))
            continue

        # Identificadores (letras) e keywords
        if c.isalpha() or c == "_":
            inicio = i
            while i < n and (conteudo[i].isalpha() or conteudo[i].isdigit() or conteudo[i] == "_"):
                i += 1
            palavra = conteudo[inicio:i]

            if palavra in KEYWORDS:
                tokens.append(Token(KEYWORDS[palavra], palavra, linha))
            elif palavra.isupper() and "_" not in palavra and all(ch.isalpha() for ch in palavra):
                # Identificador de memória: só letras maiúsculas, sem underscore
                tokens.append(Token(TokenType.MEM_NAME, palavra, linha))
            else:
                raise LexicalError(
                    f"Identificador inválido: '{palavra}' "
                    "(use apenas letras MAIÚSCULAS para nomes de memória)",
                    line=linha
                )
            continue

        # Caractere não reconhecido
        raise LexicalError(f"Caractere inesperado: '{c}'", line=linha)

    # Token EOF marca o final do fluxo
    tokens.append(Token(TokenType.EOF, "$", linha))
    return tokens
