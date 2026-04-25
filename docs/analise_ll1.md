# Analise LL(1) — Compilador RPN

> **PUC-PR — Linguagens Formais e Compiladores**
> Fase 2 — Analisador Sintatico LL(1)
>
> Integrantes:
> - Christopher Gabriel Miranda da Cruz (GitHub: Miiranda45)
> - Mauricio dos Anjos Souza (GitHub: anjos-404)

---

## 1. Regras de Producao

A gramatica define uma linguagem baseada em Notacao Polonesa Reversa (RPN) com marcadores
desambiguadores. Os marcadores (`EXPR`, `CMD_RES`, `CMD_LOAD`, `CMD_STORE`, `IF`, `IFELSE`, `WHILE`)
garantem que cada alternativa tenha um conjunto FIRST unico, tornando a gramatica LL(1) pura.

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

### Producoes Numeradas

| N   | Producao |
|-----|----------|
| P1  | `programa → START stmts END` |
| P2  | `stmts → statement stmts` |
| P3  | `stmts → ε` |
| P4  | `statement → ( stmt_tail` |
| P5  | `stmt_tail → EXPR operand operand arith_op )` |
| P6  | `stmt_tail → CMD_RES INTEGER )` |
| P7  | `stmt_tail → CMD_LOAD MEM_NAME )` |
| P8  | `stmt_tail → CMD_STORE operand MEM_NAME )` |
| P9  | `stmt_tail → IF condition block )` |
| P10 | `stmt_tail → IFELSE condition block block )` |
| P11 | `stmt_tail → WHILE condition block )` |
| P12 | `operand → INTEGER` |
| P13 | `operand → REAL` |
| P14 | `operand → MEM_NAME` |
| P15 | `operand → ( operand_paren_tail` |
| P16 | `operand_paren_tail → EXPR operand operand arith_op )` |
| P17 | `operand_paren_tail → CMD_LOAD MEM_NAME )` |
| P18 | `arith_op → +` |
| P19 | `arith_op → -` |
| P20 | `arith_op → *` |
| P21 | `arith_op → \|` |
| P22 | `arith_op → /` |
| P23 | `arith_op → %` |
| P24 | `arith_op → ^` |
| P25 | `relational_op → >` |
| P26 | `relational_op → <` |
| P27 | `relational_op → >=` |
| P28 | `relational_op → <=` |
| P29 | `relational_op → ==` |
| P30 | `relational_op → !=` |
| P31 | `condition → ( operand operand relational_op )` |
| P32 | `block → [ stmts ]` |

---

## 2. Conjuntos FIRST e FOLLOW

### Conjuntos FIRST

| Nao-Terminal | FIRST |
|---|---|
| `programa` | `{ START }` |
| `stmts` | `{ (, ε }` |
| `statement` | `{ ( }` |
| `stmt_tail` | `{ EXPR, CMD_RES, CMD_LOAD, CMD_STORE, IF, IFELSE, WHILE }` |
| `operand` | `{ INTEGER, REAL, MEM_NAME, ( }` |
| `operand_paren_tail` | `{ EXPR, CMD_LOAD }` |
| `arith_op` | `{ +, -, *, \|, /, %, ^ }` |
| `relational_op` | `{ >, <, >=, <=, ==, != }` |
| `condition` | `{ ( }` |
| `block` | `{ [ }` |

### Conjuntos FOLLOW

| Nao-Terminal | FOLLOW |
|---|---|
| `programa` | `{ EOF }` |
| `stmts` | `{ END, ] }` |
| `statement` | `{ (, END, ] }` |
| `stmt_tail` | `{ (, END, ] }` |
| `operand` | `{ +, -, *, \|, /, %, ^, >, <, >=, <=, ==, !=, INTEGER, REAL, MEM_NAME, ( }` |
| `operand_paren_tail` | `{ +, -, *, \|, /, %, ^, >, <, >=, <=, ==, !=, INTEGER, REAL, MEM_NAME, ( }` |
| `arith_op` | `{ ) }` |
| `relational_op` | `{ ) }` |
| `condition` | `{ [ }` |
| `block` | `{ ), [ }` |

### Analise de Conflitos

**Zero conflitos FIRST/FIRST** — para todo nao-terminal com multiplas alternativas, a interseccao dos FIRST de cada alternativa e vazia.

**Zero conflitos FIRST/FOLLOW** — o unico nao-terminal com producao epsilon e `stmts`. FIRST(statement) = `{(}` e FOLLOW(stmts) = `{END, ]}`. Interseccao vazia.

A gramatica e **LL(1) pura**.

---

## 3. Tabela de Analise LL(1)

A tabela mapeia pares `(nao-terminal, terminal)` para producoes. Total: **33 entradas**.

### [programa]

| Terminal | Producao |
|---|---|
| `START` | `programa → START stmts END` |

### [stmts]

| Terminal | Producao |
|---|---|
| `(` | `stmts → statement stmts` |
| `END` | `stmts → ε` |
| `]` | `stmts → ε` |

### [statement]

| Terminal | Producao |
|---|---|
| `(` | `statement → ( stmt_tail` |

### [stmt_tail]

| Terminal | Producao |
|---|---|
| `EXPR` | `stmt_tail → EXPR operand operand arith_op )` |
| `CMD_RES` | `stmt_tail → CMD_RES INTEGER )` |
| `CMD_LOAD` | `stmt_tail → CMD_LOAD MEM_NAME )` |
| `CMD_STORE` | `stmt_tail → CMD_STORE operand MEM_NAME )` |
| `IF` | `stmt_tail → IF condition block )` |
| `IFELSE` | `stmt_tail → IFELSE condition block block )` |
| `WHILE` | `stmt_tail → WHILE condition block )` |

### [operand]

| Terminal | Producao |
|---|---|
| `INTEGER` | `operand → INTEGER` |
| `REAL` | `operand → REAL` |
| `MEM_NAME` | `operand → MEM_NAME` |
| `(` | `operand → ( operand_paren_tail` |

### [operand_paren_tail]

| Terminal | Producao |
|---|---|
| `EXPR` | `operand_paren_tail → EXPR operand operand arith_op )` |
| `CMD_LOAD` | `operand_paren_tail → CMD_LOAD MEM_NAME )` |

### [arith_op]

| Terminal | Producao |
|---|---|
| `+` | `arith_op → +` |
| `-` | `arith_op → -` |
| `*` | `arith_op → *` |
| `\|` | `arith_op → \|` |
| `/` | `arith_op → /` |
| `%` | `arith_op → %` |
| `^` | `arith_op → ^` |

### [relational_op]

| Terminal | Producao |
|---|---|
| `>` | `relational_op → >` |
| `<` | `relational_op → <` |
| `>=` | `relational_op → >=` |
| `<=` | `relational_op → <=` |
| `==` | `relational_op → ==` |
| `!=` | `relational_op → !=` |

### [condition]

| Terminal | Producao |
|---|---|
| `(` | `condition → ( operand operand relational_op )` |

### [block]

| Terminal | Producao |
|---|---|
| `[` | `block → [ stmts ]` |

---

## 4. Arvore Sintatica Abstrata — teste1.txt

Codigo-fonte compilado (`tests/teste1.txt`):

```
START
(EXPR 10 5 +)
(EXPR 20 8 -)
(EXPR 6 7 *)
(EXPR 20 4 /)
(EXPR 17 5 %)
(EXPR 7.5 2.5 |)
(EXPR 2 5 ^)
(CMD_RES 1)
(CMD_STORE 100 VALOR)
(CMD_LOAD VALOR)
(IF (VALOR 50 >) [(CMD_STORE 1 FLAG)])
(CMD_STORE 0 CONT)
(WHILE (CONT 3 <) [(CMD_STORE (EXPR CONT 1 +) CONT)])
(CMD_LOAD CONT)
(CMD_LOAD VALOR)
END
```

### Arvore Sintatica Abstrata (AST)

```
Program
├── BinOp '+'
│   ├── Num(INT: 10)
│   └── Num(INT: 5)
├── BinOp '-'
│   ├── Num(INT: 20)
│   └── Num(INT: 8)
├── BinOp '*'
│   ├── Num(INT: 6)
│   └── Num(INT: 7)
├── BinOp '/'
│   ├── Num(INT: 20)
│   └── Num(INT: 4)
├── BinOp '%'
│   ├── Num(INT: 17)
│   └── Num(INT: 5)
├── BinOp '|'
│   ├── Num(REAL: 7.5)
│   └── Num(REAL: 2.5)
├── BinOp '^'
│   ├── Num(INT: 2)
│   └── Num(INT: 5)
├── Res(n=1)
├── MemWrite(VALOR)
│   └── Num(INT: 100)
├── MemRead(VALOR)
├── If
│   ├── [cond] Cond '>'
│   │   ├── MemRead(VALOR)
│   │   └── Num(INT: 50)
│   └── [then] MemWrite(FLAG)
│           └── Num(INT: 1)
├── MemWrite(CONT)
│   └── Num(INT: 0)
├── While
│   ├── [cond] Cond '<'
│   │   ├── MemRead(CONT)
│   │   └── Num(INT: 3)
│   └── [body] MemWrite(CONT)
│           └── BinOp '+'
│               ├── MemRead(CONT)
│               └── Num(INT: 1)
├── MemRead(CONT)
└── MemRead(VALOR)
```

### Legenda dos nos

| No | Descricao |
|---|---|
| `Program` | Raiz — lista de statements do programa |
| `BinOp 'op'` | Expressao aritmetica binaria em RPN |
| `Num(INT: v)` | Literal inteiro |
| `Num(REAL: v)` | Literal real (double IEEE 754) |
| `MemRead(X)` | Leitura da variavel X da memoria |
| `MemWrite(X)` | Escrita de valor na variavel X |
| `Res(n=N)` | Resultado da expressao N posicoes atras |
| `If` | Condicional (com ou sem else) |
| `Cond 'op'` | Condicao com operador relacional |
| `While` | Laco de repeticao |
