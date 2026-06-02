# Sistema de Regras de Tipos — Cálculo de Sequentes

Linguagem do grupo **RA2-21**. O sistema de tipos é **estático** (o tipo de cada
variável é fixado na definição) e **forte** (não há conversões implícitas além do
alargamento `int ⊑ real`; operações entre tipos incompatíveis são erros).

## Tipos

```
τ ::= int | real | bool
```

- `int`  — literais inteiros e operações entre inteiros;
- `real` — literais reais (IEEE 754, double) e operações com ao menos um `real`;
- `bool` — produzido **exclusivamente** por operadores relacionais. A linguagem
  não possui literais booleanos: valores lógicos surgem apenas em condições e são
  consumidos por `IF`/`IFELSE`/`WHILE`. Logo, variáveis são sempre numéricas.

## Ambiente

`Γ` é a **tabela de símbolos**: um conjunto de associações `x : τ` (escopo global
por arquivo). O julgamento de tipos é o sequente:

```
Γ ⊢ e : τ        "no ambiente Γ, a expressão e tem tipo τ"
```

## Subtipagem / coerção (`⊑`)

```
────────  (S-Refl)            ───────────  (S-Widen)
 τ ⊑ τ                          int ⊑ real
```

`int ⊑ real` modela a promoção de inteiro para real (alargamento sem perda).

---

## Regras de tipos

### Literais

```
─────────────────  (T-Int)            ──────────────  (T-Real)
 Γ ⊢ INTEGER : int                     Γ ⊢ REAL : real
```

### Variáveis (uso após definição)

```
 (x : τ) ∈ Γ
─────────────  (T-Var / T-Load)
 Γ ⊢ x : τ
```

> Se `x ∉ Γ` no ponto de uso ⇒ **erro semântico**: *variável usada antes de ser
> definida*.

### Operadores aritméticos `+`, `-`, `*`, `^`

```
 Γ ⊢ a : τ₁    Γ ⊢ b : τ₂    τ₁ ∈ {int,real}    τ₂ ∈ {int,real}
──────────────────────────────────────────────────────────────────  (T-Arith)
 Γ ⊢ (EXPR a b op) : ( int  se τ₁ = τ₂ = int ;  real  caso contrário )

                              op ∈ { +, -, *, ^ }
```

### Divisão real `|`

```
 Γ ⊢ a : τ₁    Γ ⊢ b : τ₂    τ₁ ∈ {int,real}    τ₂ ∈ {int,real}
──────────────────────────────────────────────────────────────────  (T-DivReal)
 Γ ⊢ (EXPR a b |) : real
```

### Divisão inteira `/` e resto `%`

```
 Γ ⊢ a : int    Γ ⊢ b : int
─────────────────────────────  (T-DivInt, T-Mod)
 Γ ⊢ (EXPR a b op) : int            op ∈ { /, % }
```

> Se `τ₁ ≠ int` ou `τ₂ ≠ int` ⇒ **erro semântico**: *divisão inteira/resto exige
> operandos inteiros*.

### Operadores relacionais `>`, `<`, `>=`, `<=`, `==`, `!=`

```
 Γ ⊢ a : τ₁    Γ ⊢ b : τ₂    τ₁ ∈ {int,real}    τ₂ ∈ {int,real}
──────────────────────────────────────────────────────────────────  (T-Rel)
 Γ ⊢ (a b relop) : bool
```

### Definição e atribuição de memória (`CMD_STORE`)

```
 Γ ⊢ v : τ        x ∉ dom(Γ)
──────────────────────────────────  (T-Decl)
 Γ, x:τ ⊢ (CMD_STORE v x) : τ
```

```
 Γ ⊢ v : τ'      (x : τ) ∈ Γ      τ' ⊑ τ
─────────────────────────────────────────  (T-Assign)
 Γ ⊢ (CMD_STORE v x) : τ
```

> Se `(x : τ) ∈ Γ` mas `τ' ⋢ τ` ⇒ **erro semântico**: *redefinição incompatível*
> (a variável foi definida como `τ` e não pode receber `τ'`).

### Resultado anterior (`CMD_RES`)

```
 1 ≤ n ≤ k          (k = nº de resultados de topo anteriores)
──────────────────────────────────────────────────────────────  (T-Res)
 Γ ⊢ (CMD_RES n) : real
```

> Se `n < 1` ou `n > k` ⇒ **erro semântico**: *RES referencia resultado
> inexistente*.

### Estruturas de controle (boa-formação do bloco: `Γ ⊢ s ok`)

```
 Γ ⊢ c : bool      Γ ⊢ s ok  (para cada s no bloco)
─────────────────────────────────────────────────────  (T-If)
 Γ ⊢ (IF c [bloco]) ok
```

```
 Γ ⊢ c : bool    Γ ⊢ s ok (then)    Γ ⊢ s ok (else)
──────────────────────────────────────────────────────  (T-IfElse)
 Γ ⊢ (IFELSE c [then] [else]) ok
```

```
 Γ ⊢ c : bool      Γ ⊢ s ok  (corpo)
──────────────────────────────────────  (T-While)
 Γ ⊢ (WHILE c [corpo]) ok
```

> A condição `c` precisa ter tipo `bool`. Como a única condição possível é uma
> comparação relacional (regra **T-Rel**), isso é garantido estruturalmente.

---

## Resumo das incompatibilidades detectadas

| Situação                                            | Regra violada | Erro semântico                          |
|-----------------------------------------------------|---------------|-----------------------------------------|
| `x` usada sem `(CMD_STORE _ x)` anterior            | T-Var         | variável usada antes de ser definida    |
| `/` ou `%` com operando `real`                      | T-DivInt/Mod  | exige operandos inteiros                |
| `(CMD_STORE real x)` com `x : int` já definida      | T-Assign      | redefinição incompatível                |
| `(CMD_RES n)` com `n` fora de `[1, k]`              | T-Res         | resultado inexistente                   |
| condição não-lógica em IF/IFELSE/WHILE              | T-If/While    | condição deve ser lógica                |
