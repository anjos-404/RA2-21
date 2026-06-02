# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA3-21]
# =============================================================================
# AnalisadorSemantico.py — Ponto de entrada da Fase 3 (Aluno 4: integração).
#
# Uso:
#   python AnalisadorSemantico.py tests/teste1.txt
#
# Pipeline:
#   prepararEntradaSemantica -> construirTabelaSimbolos -> verificarTipos
#   -> gerarArvoreAtribuida -> gerarAssembly (apenas se NÃO houver erros).
#
# A execução apresenta: arquivo analisado, resultado das análises léxica,
# sintática e semântica, lista de erros (se houver) e os caminhos dos
# arquivos de saída gerados.

import sys
import os
import json

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from semantic import (
    prepararEntradaSemantica,
    construirTabelaSimbolos,
    verificarTipos,
    gerarArvoreAtribuida,
)
from codegen.assembly_gen import gerarAssembly
from codegen.ast_builder import imprimir_ast


BANNER = """\
============================================================
  Analisador Semântico RPN  —  Fase 3 (LL(1) + Assembly)
  Grupo RA2-21  —  PUC-PR / Linguagens Formais e Compiladores
============================================================
"""


def _salvar(caminho: str, conteudo: str, gerados: list[str]):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    gerados.append(caminho)


def _ast_to_dict(node):
    """Serializa a AST (inclui anotações de tipo/categoria/linha)."""
    if node is None or isinstance(node, (str, int, float, bool)):
        return node
    if isinstance(node, list):
        return [_ast_to_dict(v) for v in node]
    if not hasattr(node, "__dict__"):
        return node
    d = {"tipo_no": type(node).__name__}
    for campo, valor in node.__dict__.items():
        d[campo] = _ast_to_dict(valor)
    return d


def main(argv: list[str]) -> int:
    print(BANNER)

    if len(argv) != 2:
        print("Uso: python AnalisadorSemantico.py <arquivo.txt>")
        return 1

    arquivo = argv[1]
    base = arquivo.rsplit(".", 1)[0]
    gerados: list[str] = []

    print(f"Arquivo analisado: {arquivo}\n")

    # ===================== Análise Léxica + Sintática =====================
    entrada = prepararEntradaSemantica(arquivo)

    print("[1] Análise Léxica")
    if entrada.erros_lexicos:
        print("    RESULTADO: FALHA")
        for e in entrada.erros_lexicos:
            print(f"      - {e}")
        print("\nGeração de Assembly NÃO realizada (há erros léxicos).")
        return 1
    print(f"    Tokens (sem comentários): {len(entrada.tokens)}")
    print(f"    Comentários reconhecidos e descartados: {len(entrada.comentarios)}")
    print("    RESULTADO: OK\n")

    print("[2] Análise Sintática (LL(1))")
    if entrada.erros_sintaticos:
        print("    RESULTADO: FALHA")
        for e in entrada.erros_sintaticos:
            print(f"      - {e}")
        print("\nGeração de Assembly NÃO realizada (há erros sintáticos).")
        return 1
    print(f"    Statements no programa: {len(entrada.arvore.statements)}")
    print("    RESULTADO: OK\n")

    # ===================== Análise Semântica =====================
    print("[3] Análise Semântica")
    tabela, erros_decl = construirTabelaSimbolos(entrada.arvore)
    tipos, erros_tipo = verificarTipos(entrada.arvore, tabela)
    erros_sem = sorted(erros_decl + erros_tipo, key=lambda e: getattr(e, "line", 0))

    arvore_atribuida = gerarArvoreAtribuida(entrada.arvore, tabela, tipos)

    print(f"    Variáveis na tabela de símbolos: {len(tabela)}")
    for s in tabela.itens():
        print(f"      · {s.nome}: {s.tipo} (def. L{s.linha_definicao})")
    if erros_sem:
        print(f"    RESULTADO: FALHA — {len(erros_sem)} erro(s) semântico(s):")
        for e in erros_sem:
            print(f"      - {e}")
    else:
        print("    RESULTADO: OK — nenhum erro semântico")
    print()

    # ===================== Artefatos =====================
    cabecalho = f"<!-- Arquivo de teste usado: {arquivo} -->\n\n"

    # AST inicial (JSON)
    _salvar(f"{base}_ast.json",
            json.dumps(_ast_to_dict(entrada.arvore), indent=2, ensure_ascii=False),
            gerados)

    # Tabela de símbolos (Markdown + JSON)
    _salvar(f"{base}_tabela_simbolos.md", cabecalho + tabela.to_markdown(), gerados)
    _salvar(f"{base}_tabela_simbolos.json", tabela.to_json_str(), gerados)

    # Árvore sintática atribuída (Markdown + JSON)
    _salvar(f"{base}_arvore_atribuida.md",
            cabecalho + arvore_atribuida.to_markdown(), gerados)
    _salvar(f"{base}_arvore_atribuida.json", arvore_atribuida.to_json_str(), gerados)

    # Relatório de erros semânticos (sempre, mesmo que vazio)
    rel = [f"# Relatório de Erros Semânticos", "",
           f"Arquivo de teste: `{arquivo}`", ""]
    if erros_sem:
        for e in erros_sem:
            rel.append(f"- {e}")
    else:
        rel.append("_Nenhum erro semântico encontrado nesta execução._")
    _salvar(f"{base}_erros_semanticos.md", "\n".join(rel) + "\n", gerados)

    # ===================== Geração de Assembly =====================
    print("[4] Geração de Assembly ARMv7 (CPulator DE1-SoC v16.1)")
    if erros_sem:
        print("    RESULTADO: NÃO GERADO")
        print("    O Assembly só é gerado para programas sem erros léxicos,")
        print("    sintáticos ou semânticos. Corrija os erros acima.")
    else:
        codigo = gerarAssembly(arvore_atribuida.programa)
        asm_path = f"{base}.s"
        _salvar(asm_path, codigo, gerados)
        n_linhas = len([l for l in codigo.split("\n")
                        if l.strip() and not l.strip().startswith("@")])
        print(f"    Assembly gerado: {asm_path} ({n_linhas} linhas)")
        print("    RESULTADO: OK")
    print()

    # ===================== Saídas geradas =====================
    print("Arquivos de saída gerados:")
    for g in gerados:
        print(f"    - {g}")
    print()

    if erros_sem:
        print("Concluído COM erros semânticos (Assembly não gerado).")
        return 2
    print("Concluído com sucesso (programa semanticamente válido).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
