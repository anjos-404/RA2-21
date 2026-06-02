# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA2-21]
# =============================================================================
# semantic/ — Pacote do Analisador Semântico (Fase 3).
#
# Funções públicas (conforme a divisão de tarefas do enunciado):
#   prepararEntradaSemantica(arquivo)            -> EntradaSemantica
#   construirTabelaSimbolos(arvore)              -> (TabelaSimbolos, erros)
#   verificarTipos(arvore, tabela)               -> (tipos, erros)
#   gerarArvoreAtribuida(arvore, tabela, tipos)  -> ArvoreAtribuida

from semantic.entrada import prepararEntradaSemantica, EntradaSemantica
from semantic.tabela_simbolos import (
    construirTabelaSimbolos, TabelaSimbolos, Simbolo,
)
from semantic.tipos import verificarTipos, Tipo
from semantic.arvore_atribuida import gerarArvoreAtribuida, ArvoreAtribuida

__all__ = [
    "prepararEntradaSemantica", "EntradaSemantica",
    "construirTabelaSimbolos", "TabelaSimbolos", "Simbolo",
    "verificarTipos", "Tipo",
    "gerarArvoreAtribuida", "ArvoreAtribuida",
]
