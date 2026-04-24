# lexer/ler_tokens.py — Parte 3

from lexer.token import Token, TokenType
from errors.errors import LexicalError


def lerTokens(arquivo: str) -> list[Token]:
    """
    Entrada: caminho do arquivo-fonte (.txt)
    Saída: list[Token] pronto para parsear()
    Levanta: LexicalError se token desconhecido ou formato inválido
    """
    tokens = []

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: '{arquivo}'")

    # Mapa de keywords
    keywords = {
        "START": TokenType.START,
        "END":   TokenType.END,
        "RES":   TokenType.RES,
        "IF":    TokenType.IF,
        "IFELSE": TokenType.IFELSE,
        "WHILE": TokenType.WHILE,
    }

    # Operadores de dois caracteres (verificar antes dos de um caractere)
    ops_duplos = {
        ">=": TokenType.GTE,
        "<=": TokenType.LTE,
        "==": TokenType.EQ,
        "!=": TokenType.NEQ,
    }

    # Operadores de um caractere
    ops_simples = {
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

    linha_atual = 1
    i = 0
    n = len(conteudo)

    while i < n:
        c = conteudo[i]

        # Newline — atualizar contagem de linhas
        if c == "\n":
            linha_atual += 1
            i += 1
            continue

        # Espaços e tabs — ignorar
        if c in (" ", "\t", "\r"):
            i += 1
            continue

        # Comentários: # até fim da linha
        if c == "#":
            while i < n and conteudo[i] != "\n":
                i += 1
            continue

        # Operadores de dois caracteres
        if i + 1 < n:
            par = conteudo[i:i+2]
            if par in ops_duplos:
                tokens.append(Token(type=ops_duplos[par], value=par, line=linha_atual))
                i += 2
                continue

        # Operadores e delimitadores de um caractere
        if c in ops_simples:
            tokens.append(Token(type=ops_simples[c], value=c, line=linha_atual))
            i += 1
            continue

        # Números (inteiros e reais)
        if c.isdigit() or (c == '.' and i + 1 < n and conteudo[i+1].isdigit()):
            inicio = i
            tem_ponto = False
            while i < n and (conteudo[i].isdigit() or conteudo[i] == '.'):
                if conteudo[i] == '.':
                    if tem_ponto:
                        break  # Segundo ponto — parar
                    tem_ponto = True
                i += 1
            valor_str = conteudo[inicio:i]
            if tem_ponto:
                tokens.append(Token(type=TokenType.REAL, value=float(valor_str), line=linha_atual))
            else:
                tokens.append(Token(type=TokenType.INTEGER, value=int(valor_str), line=linha_atual))
            continue

        # Identificadores e keywords (letras maiúsculas)
        if c.isalpha():
            inicio = i
            while i < n and (conteudo[i].isalpha() or conteudo[i] == '_'):
                i += 1
            palavra = conteudo[inicio:i]

            if palavra in keywords:
                tokens.append(Token(type=keywords[palavra], value=palavra, line=linha_atual))
            elif palavra.isupper():
                tokens.append(Token(type=TokenType.MEM_NAME, value=palavra, line=linha_atual))
            else:
                raise LexicalError(
                    f"Identificador inválido: '{palavra}' (use apenas letras MAIÚSCULAS para memórias)",
                    line=linha_atual
                )
            continue

        # Caractere desconhecido
        raise LexicalError(f"Caractere inesperado: '{c}'", line=linha_atual)

    # Adicionar token EOF
    tokens.append(Token(type=TokenType.EOF, value="$", line=linha_atual))
    return tokens
