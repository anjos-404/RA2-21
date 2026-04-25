# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 2 — Analisador Sintatico LL(1) + Geracao de Assembly ARMv7
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA2-21]
# =============================================================================
# main.py — Ponto de entrada do compilador RPN.
# Pipeline: lerTokens -> construirGramatica -> parsear -> gerarArvore -> gerarAssembly

import sys
import json
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer.ler_tokens import lerTokens
from grammar.grammar import construirGramatica
from parser.parser import parsear
from codegen.ast_builder import gerarArvore, imprimir_ast
from codegen.assembly_gen import gerarAssembly
from errors.errors import LexicalError, RPNSyntaxError, GrammarError


BANNER = """\
============================================
  Compilador RPN -> Assembly ARMv7 (LL(1))
============================================
"""


def main():
    if len(sys.argv) != 2:
        print(BANNER)
        print("Uso: python main.py <arquivo.txt>")
        sys.exit(1)

    arquivo = sys.argv[1]
    print(BANNER)

    # ---- Fase 1: Analise Lexica ----
    print("[Fase 1] Analise Lexica")
    try:
        tokens = lerTokens(arquivo)
        print(f"    Tokens lidos: {len(tokens)}")
        print(f"    Tipos distintos: {len({t.type for t in tokens})}")
        print("    OK\n")
    except (LexicalError, FileNotFoundError) as e:
        print(f"    ERRO: {e}")
        sys.exit(1)

    # ---- Fase 2: Construcao da Gramatica ----
    print("[Fase 2] Construcao da Gramatica")
    try:
        gramatica = construirGramatica()
        print(f"    Nao-terminais: {len(gramatica.nao_terminais)}")
        print(f"    Terminais: {len(gramatica.terminais)}")
        print(f"    Producoes: {len(gramatica.producoes)}")
        print(f"    Entradas na tabela LL(1): {len(gramatica.tabela)}")
        print("    OK\n")
    except GrammarError as e:
        print(f"    ERRO: {e}")
        sys.exit(1)

    # ---- Fase 3: Analise Sintatica (LL(1)) ----
    print("[Fase 3] Analise Sintatica LL(1)")
    try:
        derivacao = parsear(tokens, gramatica)
        print(f"    Arvore de derivacao construida")
        print(f"    Simbolo raiz: '{derivacao.simbolo}'")
        print("    OK\n")
    except RPNSyntaxError as e:
        print(f"    ERRO SINTATICO: {e}")
        sys.exit(1)

    # ---- Fase 4: Geracao da AST ----
    print("[Fase 4] Geracao da AST")
    try:
        arvore = gerarArvore(derivacao)
        print(f"    AST gerada com {len(arvore.statements)} statements")
        print("    OK\n")
    except Exception as e:
        print(f"    ERRO: {e}")
        sys.exit(1)

    # ---- Exibe a AST ----
    print("[AST] Arvore Sintatica Abstrata:")
    print("-" * 44)
    imprimir_ast(arvore)
    print("-" * 44)
    print()

    # ---- Salva AST em JSON ----
    nome_base = arquivo.rsplit(".", 1)[0]
    try:
        json_path = f"{nome_base}_ast.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(_ast_to_dict(arvore), f, indent=2, ensure_ascii=False)
        print(f"    AST salva em: {json_path}")
    except Exception as e:
        print(f"    Erro ao salvar AST: {e}")

    # ---- Fase 5: Geracao de Assembly ----
    try:
        codigo_asm = gerarAssembly(arvore)
        asm_path = f"{nome_base}.s"
        with open(asm_path, "w", encoding="utf-8") as f:
            f.write(codigo_asm)
        linhas_asm = [
            l for l in codigo_asm.split("\n")
            if l.strip() and not l.strip().startswith("@")
        ]
        print(f"    Assembly salvo em: {asm_path} ({len(linhas_asm)} linhas)")
    except Exception as e:
        print(f"    Erro na geracao de Assembly: {e}")
        sys.exit(1)


    print()
    print("============================================")
    print("  Compilacao concluida com sucesso!")
    print("============================================")


def _ast_to_dict(node) -> dict:
    """Serializa AST para JSON recursivamente."""
    if node is None:
        return None
    if isinstance(node, list):
        return [_ast_to_dict(v) for v in node]
    if not hasattr(node, "__dict__"):
        return node
    d = {"tipo": type(node).__name__}
    for campo, valor in node.__dict__.items():
        if isinstance(valor, list):
            d[campo] = [
                _ast_to_dict(v) if hasattr(v, "__dict__") else v
                for v in valor
            ]
        elif hasattr(valor, "__dict__"):
            d[campo] = _ast_to_dict(valor)
        else:
            d[campo] = valor
    return d


if __name__ == "__main__":
    main()
