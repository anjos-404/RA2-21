# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA3-21]
# =============================================================================
# semantic/entrada.py — prepararEntradaSemantica (Tarefa do Aluno 1).
#
# Integra as fases anteriores: lê o arquivo-fonte, aciona o analisador léxico
# (reconhecendo e DESCARTANDO comentários *{ ... }*), valida que o programa
# começa com START e termina com END, aciona o analisador sintático LL(1) da
# Fase 2 e produz a árvore sintática inicial usada pelo analisador semântico.
#
# Reporta erros léxicos e sintáticos ANTES da etapa semântica.

from dataclasses import dataclass, field

from lexer.token import Token, TokenType
from lexer.ler_tokens import lerTokens
from grammar.grammar import construirGramatica
from parser.parser import parsear, parsear_com_recuperacao
from codegen.ast_builder import gerarArvore
from parser.ast_nodes import ProgramNode
from errors.errors import LexicalError, RPNSyntaxError


@dataclass
class EntradaSemantica:
    """Resultado de prepararEntradaSemantica()."""
    arquivo: str
    tokens: list[Token] = field(default_factory=list)          # sem comentários
    comentarios: list[Token] = field(default_factory=list)     # descartados
    arvore: ProgramNode | None = None                          # AST inicial
    erros_lexicos: list[str] = field(default_factory=list)
    erros_sintaticos: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True se não houve erro léxico nem sintático e a AST foi construída."""
        return (
            not self.erros_lexicos
            and not self.erros_sintaticos
            and self.arvore is not None
        )

    @property
    def erros(self) -> list[str]:
        return self.erros_lexicos + self.erros_sintaticos


def prepararEntradaSemantica(arquivo: str) -> EntradaSemantica:
    """
    Prepara a entrada para o analisador semântico.

    Etapas:
      1. Lê o arquivo e produz o vetor de tokens, reconhecendo os comentários
         *{ ... }* como tokens de tipo COMMENT e descartando-os do vetor que
         alimenta o parser.
      2. Valida que o programa começa com START e termina com END.
      3. Aciona o analisador sintático LL(1) (com recuperação de erros, para
         reportar todos os erros sintáticos de uma vez).
      4. Constrói a árvore sintática inicial (AST) para uso pelo analisador
         semântico — apenas se não houver erros sintáticos.

    Saída: EntradaSemantica com tokens, comentários, árvore e listas de erros.
           Fornece a árvore para construirTabelaSimbolos() e gerarArvoreAtribuida().
    """
    resultado = EntradaSemantica(arquivo=arquivo)

    # ---- 1. Análise léxica (com extração de comentários) ----
    try:
        todos = lerTokens(arquivo, incluir_comentarios=True)
    except (LexicalError, FileNotFoundError) as e:
        resultado.erros_lexicos.append(str(e))
        return resultado

    resultado.comentarios = [t for t in todos if t.type == TokenType.COMMENT]
    tokens = [t for t in todos if t.type != TokenType.COMMENT]
    resultado.tokens = tokens

    # ---- 2. Validação START ... END (mensagem clara antes do parser) ----
    uteis = [t for t in tokens if t.type != TokenType.EOF]
    if not uteis or uteis[0].type != TokenType.START:
        linha = uteis[0].line if uteis else 1
        resultado.erros_sintaticos.append(
            f"Linha {linha}: o programa deve começar com START"
        )
    if not uteis or uteis[-1].type != TokenType.END:
        linha = uteis[-1].line if uteis else 1
        resultado.erros_sintaticos.append(
            f"Linha {linha}: o programa deve terminar com END"
        )

    # Se a estrutura START..END já está quebrada, não vale parsear.
    if resultado.erros_sintaticos:
        return resultado

    # ---- 3. Análise sintática LL(1) ----
    # Usa o parser estrito para obter a árvore de derivação canônica (usada
    # pela construção da AST). Em caso de erro sintático, aciona o parser com
    # recuperação em modo pânico para reportar TODOS os erros de uma só vez.
    gramatica = construirGramatica()
    try:
        derivacao = parsear(tokens, gramatica)
    except RPNSyntaxError:
        _, erros_sint = parsear_com_recuperacao(tokens, gramatica)
        for e in erros_sint:
            if e not in resultado.erros_sintaticos:
                resultado.erros_sintaticos.append(e)
        return resultado

    # ---- 4. Construção da AST (sintaticamente válido) ----
    try:
        resultado.arvore = gerarArvore(derivacao)
    except Exception as e:  # pragma: no cover - salvaguarda
        resultado.erros_sintaticos.append(f"Erro ao construir a AST: {e}")

    return resultado
