# Gramatica Formal — Linguagem RPN Estendida (LL(1) Pura)

## Notacao

- **minusculas** = nao-terminais
- **MAIUSCULAS** / `simbolos` = terminais
- `epsilon` = producao vazia
- `|` = alternativa

---

## Visao Geral

Esta gramatica define uma linguagem baseada em Notacao Polonesa Reversa (RPN)
com marcadores desambiguadores que garantem que cada producao tenha um
conjunto FIRST unico. **A gramatica e LL(1) no sentido estrito**: zero
conflitos FIRST/FIRST e zero conflitos FIRST/FOLLOW.

### Marcadores desambiguadores

- `EXPR`      — marca expressao aritmetica
- `CMD_RES`   — marca comando de resultado anterior
- `CMD_LOAD`  — marca leitura de memoria
- `CMD_STORE` — marca escrita em memoria
- `IF`, `IFELSE`, `WHILE` — marcadores de estruturas de controle

### Sintaxe

```
Programa:    START <stmts> END

Expressao:   (EXPR a b op)
RES:         (CMD_RES N)
Leitura:     (CMD_LOAD NOME)
Escrita:     (CMD_STORE V NOME)
IF:          (IF (cond) [bloco])
IFELSE:      (IFELSE (cond) [then] [else])
WHILE:       (WHILE (cond) [corpo])
```

---

## Gramatica em EBNF

```ebnf
programa           ::= START stmts END

stmts              ::= statement stmts
                     | epsilon

statement          ::= '(' stmt_tail

stmt_tail          ::= EXPR operand operand arith_op ')'
                     | CMD_RES INTEGER ')'
                     | CMD_LOAD MEM_NAME ')'
                     | CMD_STORE operand MEM_NAME ')'
                     | IF condition block ')'
                     | IFELSE condition block block ')'
                     | WHILE condition block ')'

operand            ::= INTEGER
                     | REAL
                     | MEM_NAME
                     | '(' operand_paren_tail

operand_paren_tail ::= EXPR operand operand arith_op ')'
                     | CMD_LOAD MEM_NAME ')'

arith_op           ::= '+' | '-' | '*' | '|' | '/' | '%' | '^'

relational_op      ::= '>' | '<' | '>=' | '<=' | '==' | '!='

condition          ::= '(' operand operand relational_op ')'

block              ::= '[' stmts ']'
```

---

## Producoes Numeradas (para Tabela LL(1))

```
 P1  programa           -> START stmts END
 P2  stmts              -> statement stmts
 P3  stmts              -> epsilon
 P4  statement          -> ( stmt_tail
 P5  stmt_tail          -> EXPR operand operand arith_op )
 P6  stmt_tail          -> CMD_RES INTEGER )
 P7  stmt_tail          -> CMD_LOAD MEM_NAME )
 P8  stmt_tail          -> CMD_STORE operand MEM_NAME )
 P9  stmt_tail          -> IF condition block )
 P10 stmt_tail          -> IFELSE condition block block )
 P11 stmt_tail          -> WHILE condition block )
 P12 operand            -> INTEGER
 P13 operand            -> REAL
 P14 operand            -> MEM_NAME
 P15 operand            -> ( operand_paren_tail
 P16 operand_paren_tail -> EXPR operand operand arith_op )
 P17 operand_paren_tail -> CMD_LOAD MEM_NAME )
 P18 arith_op           -> +
 P19 arith_op           -> -
 P20 arith_op           -> *
 P21 arith_op           -> |
 P22 arith_op           -> /
 P23 arith_op           -> %
 P24 arith_op           -> ^
 P25 relational_op      -> >
 P26 relational_op      -> <
 P27 relational_op      -> >=
 P28 relational_op      -> <=
 P29 relational_op      -> ==
 P30 relational_op      -> !=
 P31 condition          -> ( operand operand relational_op )
 P32 block              -> [ stmts ]
```

---

## Conjuntos FIRST

```
FIRST(programa)           = { START }
FIRST(stmts)              = { (, epsilon }
FIRST(statement)          = { ( }
FIRST(stmt_tail)          = { EXPR, CMD_RES, CMD_LOAD, CMD_STORE, IF, IFELSE, WHILE }
FIRST(operand)            = { INTEGER, REAL, MEM_NAME, ( }
FIRST(operand_paren_tail) = { EXPR, CMD_LOAD }
FIRST(arith_op)           = { +, -, *, |, /, %, ^ }
FIRST(relational_op)      = { >, <, >=, <=, ==, != }
FIRST(condition)          = { ( }
FIRST(block)              = { [ }
```

---

## Conjuntos FOLLOW

```
FOLLOW(programa)           = { EOF }
FOLLOW(stmts)              = { END, ] }
FOLLOW(statement)          = { (, END, ] }
FOLLOW(stmt_tail)          = FOLLOW(statement)
FOLLOW(operand)            = { +, -, *, |, /, %, ^,
                               >, <, >=, <=, ==, !=,
                               INTEGER, REAL, MEM_NAME, (, MEM_NAME }
FOLLOW(operand_paren_tail) = FOLLOW(operand)
FOLLOW(arith_op)           = { ) }
FOLLOW(relational_op)      = { ) }
FOLLOW(condition)          = { [ }
FOLLOW(block)              = { ), [ }
```

---

## Analise de Conflitos

### FIRST/FIRST

Para todas as producoes `A -> alpha_1 | alpha_2 | ... | alpha_n`:

| Nao-Terminal       | Alternativas                                                 | Intersecao FIRST |
|--------------------|--------------------------------------------------------------|------------------|
| stmts              | `statement stmts` vs `epsilon`                               | vazio            |
| stmt_tail          | EXPR/CMD_RES/CMD_LOAD/CMD_STORE/IF/IFELSE/WHILE (7 alt.)     | vazio            |
| operand            | INTEGER/REAL/MEM_NAME/`(`                                    | vazio            |
| operand_paren_tail | EXPR vs CMD_LOAD                                             | vazio            |
| arith_op           | +/-/\*/\|//%/^                                               | vazio            |
| relational_op      | >/</>=/<=/==/!=                                              | vazio            |

**Zero conflitos FIRST/FIRST.**

### FIRST/FOLLOW

Para producoes que podem derivar epsilon:

| Nao-Terminal | FIRST das outras     | FOLLOW    | Intersecao |
|--------------|----------------------|-----------|------------|
| stmts        | FIRST(statement)={(} | {END, ]}  | vazio      |

**Zero conflitos FIRST/FOLLOW.**

---

## Tabela LL(1)

A tabela foi construida pelo algoritmo classico:

- Para cada producao `A -> alpha`:
  - Para todo `a` em `FIRST(alpha) - {epsilon}`: `M[A, a] = A -> alpha`
  - Se `epsilon` em `FIRST(alpha)`: para todo `b` em `FOLLOW(A)`: `M[A, b] = A -> alpha`

A tabela resultante tem **33 entradas** e e **deterministica** (cada celula
contem no maximo uma producao).

---

## Parser

O parser (`parser/parser.py`) e uma implementacao direta do algoritmo
LL(1) preditivo tabular com pilha:

```
pilha = [EOF, simbolo_inicial]
enquanto topo(pilha) != EOF:
    X = topo(pilha)
    a = token_atual
    se X e terminal:
        se X == a: consome token e pop
        senao: erro
    senao (X e nao-terminal):
        consulta M[X, a]
        se existe producao X -> Y1 Y2 ... Yn:
            pop X, empilha Yn, Yn-1, ..., Y1
        senao: erro
```

**Nao usa lookahead > 1. Nao faz backtracking. Nao usa scan forward.**
Todas as decisoes sao tomadas pela tabela.
