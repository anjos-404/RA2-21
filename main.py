# main.py — Parte 4
# Ponto de entrada do compilador RPN.
# Integra: lerTokens (Parte 3) - construirGramatica (Parte 1) - parsear (Parte 2) -
#          gerarArvore + gerarAssembly (Parte 4)

import sys
import json
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Adiciona diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer.ler_tokens import lerTokens
from grammar.grammar import construirGramatica
from parser.parser import parsear, parsear_com_recuperacao
from codegen.ast_builder import gerarArvore, imprimir_ast
from codegen.assembly_gen import gerarAssembly
from errors.errors import LexicalError, RPNSyntaxError


def main():
    if len(sys.argv) != 2:
        print("╔══════════════════════════════════════════╗")
        print("║     Compilador RPN - Assembly ARMv7      ║")
        print("╚══════════════════════════════════════════╝")
        print()
        print("Uso: python main.py <arquivo.txt>")
        print()
        sys.exit(1)

    arquivo = sys.argv[1]

    print("╔══════════════════════════════════════════╗")
    print("║     Compilador RPN - Assembly ARMv7      ║")
    print("╚══════════════════════════════════════════╝")
    print()

   
    # 1. Análise Léxica — lerTokens()
   
    print("┌─ Fase 1: Análise Léxica")
    try:
        tokens = lerTokens(arquivo)
        print(f"│   Tokens carregados: {len(tokens)}")
        print(f"│   Tipos encontrados: {len({t.type for t in tokens})}")
        print(" OK")
    except (LexicalError, FileNotFoundError) as e:
        print(f"│   ERRO: {e}")
        print(" FALHOU")
        sys.exit(1)
    print()

    
    # 2. Construção da Gramática — construirGramatica()
    
    print("┌─ Fase 2: Construção da Gramática")
    try:
        gramatica = construirGramatica()
        print(f"│   Gramática construída")
        print(f"│   Não-terminais: {len(gramatica.nao_terminais)}")
        print(f"│   Terminais: {len(gramatica.terminais)}")
        print(f"│   Produções: {len(gramatica.producoes)}")
        print(f"│   Entradas na tabela LL(1): {len(gramatica.tabela)}")
        print(" OK")
    except ValueError as e:
        print(f"│   ERRO na gramática: {e}")
        print(" FALHOU")
        sys.exit(1)
    print()

   
    # 3. Análise Sintática — parsear()
   
    print("─ Fase 3: Análise Sintática (Parser)")
    try:
        derivacao = parsear(tokens, gramatica)
        print("│   Parsing concluído sem erros")
        print("│   Programa válido")
        print(" OK")
    except SyntaxError as e:
        print(f"│   ERRO SINTÁTICO: {e}")
        print(" FALHOU")
        sys.exit(1)
    print()

   
    # 4. Geração da AST — gerarArvore()
    
    print("─ Fase 4: Geração da AST")
    try:
        arvore = gerarArvore(derivacao)
        num_stmts = len(arvore.statements)
        print(f"│   AST gerada com {num_stmts} statements")
        print(" OK")
    except Exception as e:
        print(f"│   ERRO na geração da AST: {e}")
        print(" FALHOU")
        sys.exit(1)
    print()

    # Imprimir AST
    print("─ Árvore Sintática Abstrata (AST)")
    print("│")
    imprimir_ast(arvore)
    print("│")
    print("─ FIM")
    print()

    # 5. Salvar AST em JSON
  
    nome_base = arquivo.rsplit(".", 1)[0]
    try:
        json_path = f"{nome_base}_ast.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(_ast_to_dict(arvore), f, indent=2, ensure_ascii=False)
        print(f"✓ AST salva em: {json_path}")
    except Exception as e:
        print(f"✗ Erro ao salvar AST: {e}")

   
    # 6. Geração de Assembly — gerarAssembly()
    
    try:
        codigo_asm = gerarAssembly(arvore)
        asm_path = f"{nome_base}.s"
        with open(asm_path, "w", encoding="utf-8") as f:
            f.write(codigo_asm)
        print(f" Assembly gerado em: {asm_path}")

        # Contar linhas de Assembly
        linhas_asm = [l for l in codigo_asm.split("\n") if l.strip() and not l.strip().startswith("@")]
        print(f"  ({len(linhas_asm)} linhas de instrução)")
    except Exception as e:
        print(f" Erro na geração de Assembly: {e}")
        sys.exit(1)

    print()
    print("═══════════════════════════════════════════")
    print("  Compilação concluída com sucesso! ")
    print("═══════════════════════════════════════════")


def _ast_to_dict(node) -> dict:
    """Serializa AST para JSON recursivamente."""
    if node is None:
        return None
    d = {"tipo": type(node).__name__}
    for campo, valor in node.__dict__.items():
        if isinstance(valor, list):
            d[campo] = [_ast_to_dict(v) if hasattr(v, "__dict__") else v for v in valor]
        elif hasattr(valor, "__dict__"):
            d[campo] = _ast_to_dict(valor)
        else:
            d[campo] = valor
    return d


if __name__ == "__main__":
    main()
