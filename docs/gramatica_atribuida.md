# Gramática Atribuída — Fase 3 (Analisador Semântico)

Esta é a gramática **LL(1)** da linguagem do grupo RA2-21, **aumentada** com as
regras semânticas (ações de atribuição de tipos, tabela de símbolos e geração de
Assembly). Notação:

- **não-terminais** em letras minúsculas;
- **TERMINAIS** em letras MAIÚSCULAS;
- `::=` separa cabeça e corpo; `|` separa alternativas; `ε` é a produção vazia;
- atributos sintetizados são indicados com `.tipo`, `.cat` (categoria semântica);
- `Γ` é a tabela de símbolos (ambiente); `⊢` é o julgamento de tipos definido
  em [`regras_tipos.md`](regras_tipos.md).

> Comentários `*{ ... }*` (e `#` de linha) são reconhecidos pelo **analisador
> léxico** como tokens de categoria *comentário* e **descartados** antes da
> análise sintática. Por isso não aparecem na gramática.

## 1. Produções (EBNF)

```ebnf
programa            ::= START stmts END

stmts               ::= statement stmts
                      |  ε

statement           ::= LPAREN stmt_tail

stmt_tail           ::= EXPR operand operand arith_op RPAREN
                      |  CMD_RES INTEGER RPAREN
                      |  CMD_LOAD MEM_NAME RPAREN
                      |  CMD_STORE operand MEM_NAME RPAREN
                      |  IF condition block RPAREN
                      |  IFELSE condition block block RPAREN
                      |  WHILE condition block RPAREN

operand             ::= INTEGER
                      |  REAL
                      |  MEM_NAME
                      |  LPAREN operand_paren_tail

operand_paren_tail  ::= EXPR operand operand arith_op RPAREN
                      |  CMD_LOAD MEM_NAME RPAREN

arith_op            ::= PLUS | MINUS | MUL | DIV_REAL | DIV_INT | MOD | POW

relational_op       ::= GT | LT | GTE | LTE | EQ | NEQ

condition           ::= LPAREN operand operand relational_op RPAREN

block               ::= LBRACKET stmts RBRACKET
```

## 2. Atributos semânticos

| Símbolo            | Atributo  | Significado                                            |
|--------------------|-----------|--------------------------------------------------------|
| `operand`          | `.tipo`   | `int` \| `real` (tipo sintetizado do operando)         |
| `stmt_tail` (EXPR) | `.tipo`   | tipo do resultado da expressão aritmética              |
| `condition`        | `.tipo`   | sempre `bool`                                          |
| qualquer nó        | `.cat`    | categoria semântica (ex.: `expressao_aritmetica`)      |
| qualquer nó        | `.linha`  | linha-fonte (para mensagens de erro)                   |

## 3. Regras semânticas por produção

As regras abaixo são aplicadas pelo analisador semântico sobre a árvore. A
formalização completa do sistema de tipos está em
[`regras_tipos.md`](regras_tipos.md).

### 3.1 Expressões aritméticas
```
stmt_tail ::= EXPR operand₁ operand₂ arith_op RPAREN
operand_paren_tail ::= EXPR operand₁ operand₂ arith_op RPAREN
```
- `operand₁`, `operand₂` devem ser **numéricos** (`int`/`real`).
- Tipo sintetizado, conforme `arith_op`:
  - `+ - * ^` → `int` se ambos `int`, senão `real`;
  - `|` (DIV_REAL) → sempre `real`;
  - `/ %` (DIV_INT, MOD) → **exigem ambos `int`** e resultam em `int`; caso
    contrário, **erro semântico**.

### 3.2 Comando RES
```
stmt_tail ::= CMD_RES INTEGER RPAREN
```
- `INTEGER` = `n` deve satisfazer `1 ≤ n ≤ (nº de resultados anteriores)`;
  fora desse intervalo → **erro semântico** (resultado inexistente).
- Tipo sintetizado: `real` (resultados são armazenados em precisão dupla).

### 3.3 Escrita e leitura de memória
```
stmt_tail ::= CMD_STORE operand MEM_NAME RPAREN      (definição/atribuição)
operand   ::= MEM_NAME                                (uso)
operand_paren_tail / stmt_tail ::= CMD_LOAD MEM_NAME RPAREN   (uso)
```
- **CMD_STORE**: se `MEM_NAME ∉ Γ`, **declara** a variável com o tipo de
  `operand`; se já existe com tipo `τ`, só aceita valor `τ'` tal que `τ' ⊑ τ`
  (igual ou alargamento `int ⊑ real`), senão **erro semântico** (redefinição
  incompatível — tipagem estática e forte).
- **MEM_NAME / CMD_LOAD**: a variável deve ter sido **definida antes do uso**;
  caso contrário → **erro semântico**. O tipo sintetizado é o tipo registrado
  em `Γ`.

### 3.4 Condições e estruturas de controle
```
condition ::= LPAREN operand operand relational_op RPAREN
stmt_tail ::= IF condition block RPAREN
            | IFELSE condition block block RPAREN
            | WHILE condition block RPAREN
```
- Os dois `operand` da `condition` devem ser numéricos e compatíveis.
- `condition.tipo = bool` (sempre). As estruturas IF/IFELSE/WHILE **exigem
  condição de tipo `bool`** — o que é garantido estruturalmente, pois a única
  forma de condição é uma comparação relacional.

### 3.5 Geração de Assembly
A geração de código ARMv7 é dirigida pela árvore atribuída e só ocorre quando o
programa **não possui** erros léxicos, sintáticos nem semânticos.
```
programa ::= START stmts END     ⇒  emite .text/_start, código de stmts, halt e .data
```
