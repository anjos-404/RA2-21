# Tabela de Símbolos

A tabela de símbolos é construída por `construirTabelaSimbolos(arvore)`
(`semantic/tabela_simbolos.py`) em uma passagem **em ordem de programa** sobre a
árvore sintática. Ela é a base para a verificação de declarações e para a
inferência de tipos.

## Estrutura

Cada símbolo (`semantic.tabela_simbolos.Simbolo`) registra:

| Campo             | Descrição                                                        |
|-------------------|------------------------------------------------------------------|
| `nome`            | identificador da variável (ex.: `VALOR`, `CONT`)                 |
| `tipo`            | tipo inferido **na definição** (`int` ou `real`)                 |
| `categoria`       | `variavel`                                                       |
| `escopo`          | `global` — cada arquivo é um escopo de memória independente      |
| `linha_definicao` | linha do primeiro `(CMD_STORE _ nome)`                           |
| `linhas_uso`      | linhas em que a variável é lida (`MEM_NAME`/`CMD_LOAD`)          |

## Regras aplicadas durante a construção

1. **Definição** — `(CMD_STORE v NOME)`: se `NOME` ainda não existe, é declarada
   com o tipo de `v` (inferido por `semantic.tipos.inferir_tipo`). O valor `v` é
   avaliado **antes** de a variável ser (re)definida.
2. **Uso antes da definição** — toda leitura de variável (`MEM_NAME` em operandos
   ou condições, `CMD_LOAD`) é verificada: se a variável não foi definida até
   aquele ponto, gera-se o erro *variável usada antes de ser definida*.
3. **Redefinição incompatível** — reatribuir uma variável `int` com um valor
   `real` viola a tipagem estática/forte e gera erro. O alargamento `int → real`
   (variável `real` recebendo `int`) é permitido (ver `regras_tipos.md`).
4. **Validação de RES** — `(CMD_RES n)` é validado contra o número de resultados
   de topo emitidos antes daquele ponto; `n` fora de `[1, k]` gera erro.

## Significado dos comandos especiais

| Comando             | Papel na tabela de símbolos                                  |
|---------------------|-------------------------------------------------------------|
| `(CMD_STORE v NOME)`| **define/atribui** `NOME` (declara na 1ª vez)               |
| `(CMD_LOAD NOME)`   | **usa** `NOME` (exige definição prévia)                     |
| `MEM_NAME` (operando)| **usa** a variável dentro de uma expressão/condição        |
| `(CMD_RES n)`       | referencia um **resultado anterior** (não é variável)       |

## Artefato gerado

A cada execução, o analisador grava a tabela da última execução em:

- `<arquivo>_tabela_simbolos.md` (legível) e
- `<arquivo>_tabela_simbolos.json` (estruturado).

Exemplo (de `tests/teste1.txt`):

| Nome  | Tipo | Categoria | Escopo | Linha de definição | Linhas de uso |
|-------|------|-----------|--------|--------------------|---------------|
| VALOR | int  | variavel  | global | 12                 | 13, 14, 18    |
| FLAG  | int  | variavel  | global | 14                 | —             |
| CONT  | int  | variavel  | global | 15                 | 16, 17        |
