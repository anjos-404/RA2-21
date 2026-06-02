# Árvore Sintática Atribuída

A **árvore sintática atribuída** é a AST da Fase 2 **anotada** com as informações
semânticas necessárias para justificar e dirigir a geração de Assembly. É
produzida por `gerarArvoreAtribuida(arvore, tabelaSimbolos, tipos)`
(`semantic/arvore_atribuida.py`), depois de `verificarTipos`.

## Anotações em cada nó

| Anotação    | Origem                          | Exemplo                          |
|-------------|---------------------------------|----------------------------------|
| `tipo`      | `verificarTipos`                | `int`, `real`, `bool`            |
| `categoria` | `gerarArvoreAtribuida`          | `expressao_aritmetica`, ...      |
| `linha`     | analisador léxico/sintático     | `12`                             |
| `simbolo`   | referência à tabela de símbolos | `{tipo: int, linha_definicao: 12}`|

### Categorias semânticas

| Nó           | Categoria                                  |
|--------------|--------------------------------------------|
| `ProgramNode`| `programa`                                 |
| `BinOpNode`  | `expressao_aritmetica`                     |
| `NumberNode` | `literal_inteiro` \| `literal_real`        |
| `MemReadNode`| `leitura_memoria`                          |
| `MemWriteNode`| `atribuicao_memoria`                      |
| `ResNode`    | `resultado_anterior`                       |
| `ConditionNode`| `condicao_relacional`                    |
| `IfNode`     | `decisao_simples` \| `decisao_composta`    |
| `WhileNode`  | `repeticao`                                |

## Papel na geração de Assembly

- O campo `tipo` informa, por exemplo, se uma divisão é inteira (`int`) ou real,
  e se um literal deve ser carregado como inteiro convertido ou como `double`.
- As `categoria`/`simbolo` ligam cada leitura/escrita de memória à variável
  correspondente na seção `.data`.
- A geração só ocorre se a árvore estiver **livre de erros semânticos**; nesse
  caso `gerarAssembly(arvore_atribuida.programa)` percorre a árvore anotada e
  emite o código ARMv7 (VFP F64).

## Artefato gerado

A cada execução, a árvore atribuída da última execução é gravada em:

- `<arquivo>_arvore_atribuida.md` (árvore aninhada, legível) e
- `<arquivo>_arvore_atribuida.json` (estruturada).

Trecho de exemplo (de `tests/teste1.txt`):

```
- Programa  — categoria=programa
  · statements:
    - BinOp (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=4
      · esquerda:
        - Number (valor=10)  — categoria=literal_inteiro, tipo=int, linha=4
      · direita:
        - Number (valor=5)   — categoria=literal_inteiro, tipo=int, linha=4
```
