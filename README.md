# Compilador RPN — Analisador Semantico + LL(1) + Assembly ARMv7

**Fase 3: Analisador Semantico** (sobre o Analisador Lexico da Fase 1 e o
Analisador Sintatico LL(1) da Fase 2)

## Informacoes

- **Instituicao:** PUC-PR
- **Ano:** 2026 (semestre 2026/1)
- **Disciplina:** Linguagens Formais e Compiladores
- **Professor:** Frank Coelho de Alcantara
- **Linguagem de implementacao:** Python
- **Nome do grupo no Canvas:** RA2-21

### Integrantes (ordem alfabetica)

- Christopher Gabriel Miranda da Cruz — GitHub: Miiranda45
- Mauricio dos Anjos Souza — GitHub: anjos-404

---

## Sobre o Projeto

Implementacao completa de um compilador para uma linguagem baseada em
Notacao Polonesa Reversa (RPN). O projeto cobre desde a analise lexica
ate a geracao de codigo Assembly para a arquitetura ARMv7 (CPUlator
DE1-SoC).

### Caracteristicas Principais

- **Gramatica LL(1) pura**: FIRST/FIRST e FIRST/FOLLOW
- **Parser LL(1) tabular**: (pilha + tabela M[A, a])
- **Nao usa** lookahead > 1, backtracking, ou scan forward
- **Validacao automatica**: construcao da tabela falha com excecao
  se a gramatica nao for LL(1)
- **IEEE 754** double precision (64 bits) para todos os numeros reais
- **Assembly ARMv7** com VFP (instrucoes F64) para o CPUlator DE1-SoC

### Arquitetura Modular

```
compilador/
├── lexer/            # Analisador lexico
│   ├── token.py      # Definicao de Token e TokenType
│   └── ler_tokens.py # Funcao lerTokens()
├── grammar/          # Construcao da gramatica
│   ├── first_follow.py # Calculo de FIRST/FOLLOW
│   ├── ll1_table.py    # Construcao rigorosa da tabela
│   └── grammar.py      # Producoes e construirGramatica()
├── parser/           # Analisador sintatico
│   ├── parser.py     # Parser LL(1) tabular
│   └── ast_nodes.py  # Nos da AST
├── codegen/          # Geracao de codigo
│   ├── ast_builder.py  # Derivacao -> AST
│   └── assembly_gen.py # AST -> Assembly ARMv7
├── errors/           # Hierarquia de erros
│   └── errors.py
├── tests/            # Testes unitarios e de integracao
├── docs/             # Documentacao da gramatica
└── main.py           # Ponto de entrada
```

---

## Sintaxe da Linguagem

### Marcadores Desambiguadores

A linguagem usa marcadores explicitos para garantir que cada construcao
seja identificavel por 1 token apos o `(`. Isso e o que permite a
gramatica ser LL(1) pura.

| Construcao              | Sintaxe LL(1)                            |
|-------------------------|------------------------------------------|
| Inicio de programa      | `START`                                  |
| Fim de programa         | `END`                                    |
| Expressao aritmetica    | `(EXPR a b op)`                          |
| Resultado anterior      | `(CMD_RES N)`                            |
| Leitura de memoria      | `(CMD_LOAD NOME)`                        |
| Escrita em memoria      | `(CMD_STORE V NOME)`                     |
| IF                      | `(IF (cond) [bloco])`                    |
| IFELSE                  | `(IFELSE (cond) [then] [else])`          |
| WHILE                   | `(WHILE (cond) [corpo])`                 |

### Operadores

- **Aritmeticos:** `+` `-` `*` `|` (divisao real) `/` (divisao inteira) `%` `^`
- **Relacionais:** `>` `<` `>=` `<=` `==` `!=`

### Exemplo

```
START

(CMD_STORE 100 VALOR)
(CMD_STORE 0 CONT)

(WHILE (CONT 3 <) [
    (CMD_STORE (EXPR CONT 1 +) CONT)
])

(IFELSE (VALOR 50 >)
    [(CMD_STORE 1 FLAG)]
    [(CMD_STORE 0 FLAG)])

(CMD_LOAD VALOR)
(CMD_RES 1)

END
```

---

## Analise Semantica (Fase 3)

A Fase 3 adiciona o **analisador semantico** sobre as fases anteriores. Ele
constroi a **arvore sintatica atribuida**, mantem uma **tabela de simbolos**,
faz **inferencia e verificacao de tipos** e so gera Assembly para programas
**semanticamente validos**.

### Comentarios

A linguagem aceita comentarios no formato `*{ ... }*` (e tambem `#` ate o fim da
linha). Podem ocupar linhas inteiras, aparecer no fim de uma linha de codigo ou
entre expressoes, e podem se estender por varias linhas. O analisador lexico os
reconhece como tokens de *comentario* e os **descarta** antes da analise
sintatica, de modo que nao interferem nas demais fases.

```
*{ comentario de linha inteira }*
START
(EXPR 10 5 +)   *{ comentario no fim de uma linha }*
END
```

### Tipos suportados

| Tipo   | Origem                                                              |
|--------|--------------------------------------------------------------------|
| `int`  | literais inteiros e operacoes entre inteiros                       |
| `real` | literais reais (IEEE 754, double) e operacoes com ao menos um real |
| `bool` | produzido **somente** por operadores relacionais (condicoes)       |

Os tipos sao **estaticos e fortes**: o tipo de cada variavel e fixado na
definicao e nao pode mudar. A unica coercao permitida e o alargamento
`int ⊑ real`. Regras formais (em **calculo de sequentes**):
[`docs/regras_tipos.md`](docs/regras_tipos.md).

Regras dos operadores:
- `+ - * ^` → `int` se ambos inteiros, senao `real`;
- `|` (divisao real) → sempre `real`;
- `/` (divisao inteira) e `%` (resto) → **exigem ambos `int`**;
- `> < >= <= == !=` → `bool`.

### Definicao e uso de variaveis

- **Definir/atribuir:** `(CMD_STORE valor NOME)` — a variavel e declarada na
  primeira escrita, com o tipo inferido do valor.
- **Usar/ler:** `(CMD_LOAD NOME)` ou `NOME` dentro de uma expressao/condicao —
  a variavel **deve ter sido definida antes**.
- Reatribuir com tipo incompativel (ex.: `int` recebendo `real`) e **erro
  semantico**.

### Exemplos

**Programa semanticamente valido:**
```
START
(CMD_STORE 10 X)            *{ X : int }*
(EXPR X 5 +)                *{ int + int -> int }*
(IF (X 0 >) [(CMD_STORE 1 POS)])
END
```

**Erros semanticos (rejeitados, sem gerar Assembly):**
```
START
(CMD_LOAD Y)               *{ ERRO: Y usada antes de ser definida }*
(CMD_STORE 3.14 P)
(EXPR P 2 /)              *{ ERRO: divisao inteira exige operandos int }*
(CMD_STORE 10 N)
(CMD_STORE 2.5 N)         *{ ERRO: N e int, nao pode receber real }*
(CMD_RES 99)              *{ ERRO: RES referencia resultado inexistente }*
END
```

### Tabela de simbolos e arvore atribuida

- Tabela de simbolos: [`docs/tabela_simbolos.md`](docs/tabela_simbolos.md)
- Arvore sintatica atribuida: [`docs/arvore_atribuida.md`](docs/arvore_atribuida.md)
- Gramatica atribuida (EBNF): [`docs/gramatica_atribuida.md`](docs/gramatica_atribuida.md)

### Arquivos de saida gerados pelo analisador

Para um arquivo `tests/testeN.txt`, a execucao gera:

| Arquivo                              | Conteudo                                   |
|--------------------------------------|--------------------------------------------|
| `testeN_ast.json`                    | AST inicial (com anotacoes)                |
| `testeN_tabela_simbolos.md` / `.json`| tabela de simbolos da execucao             |
| `testeN_arvore_atribuida.md` / `.json`| arvore sintatica atribuida                |
| `testeN_erros_semanticos.md`         | relatorio de erros (mesmo que vazio)       |
| `testeN.s`                           | Assembly ARMv7 (**so se nao houver erros**)|

---

## Uso

### Execucao (Fase 3 — Analisador Semantico)

```bash
python AnalisadorSemantico.py tests/teste1.txt
```

A execucao apresenta: arquivo analisado, resultado da analise lexica, sintatica
e semantica, lista de erros (se houver) e os caminhos dos arquivos de saida.

### Compilacao (Fase 2 — pipeline ate Assembly)

```bash
python main.py tests/teste1.txt
```

Saidas geradas:
- `tests/teste1_ast.json` — AST em formato JSON
- `tests/teste1.s` — Codigo Assembly ARMv7

### Testes

```bash
# Todos os testes
pytest tests/ -v

# Apenas o analisador semantico (Fase 3)
pytest tests/test_semantico.py -v

# Verificacao numerica do Assembly gerado (executa o codigo ARMv7)
pytest tests/test_assembly_exec.py -v
```

Os testes da Fase 3 (`test_semantico.py` e `test_assembly_exec.py`) usam a
biblioteca padrao `unittest`, entao tambem rodam sem o pytest instalado:

```bash
python -m unittest tests.test_semantico tests.test_assembly_exec
```

**Cobertura de testes:**
- Fase 1/2 (lexer, gramatica, parser, integracao): testes unitarios e e2e.
- Fase 3 (semantico): comentarios, tabela de simbolos, declaracao/uso,
  inferencia e erros de tipo, condicoes, RES e casos extremos.
- **Execucao do Assembly** (`test_assembly_exec.py`): um simulador do
  subconjunto VFP F64 do **ARMv7-A DE1-SoC** executa o codigo gerado e confere
  os resultados numericos de TODAS as operacoes (aritmeticas com int/real/
  mista, divisao inteira com truncamento toward-zero, resto, potenciacao,
  divisao real, aninhamento, memoria, RES, os 6 relacionais e lacos WHILE).

### Depuracao

O compilador expoe cada etapa do pipeline para inspecao, o que permite
depurar isoladamente o lexer, a gramatica, o parser, a AST e o assembly.

**1. Inspecionar os tokens (saida do lexer):**

```bash
python -c "from lexer.ler_tokens import lerTokens; [print(t) for t in lerTokens('tests/teste1.txt')]"
```

**2. Inspecionar a tabela LL(1), FIRST e FOLLOW:**

```bash
python -c "from grammar.grammar import construirGramatica; from grammar.ll1_table import imprimir_tabela; imprimir_tabela(construirGramatica())"
```

**3. Inspecionar a AST gerada:**

Cada execucao imprime a AST no console e grava `tests/<nome>_ast.json`.
Abra o `.json` para ver a arvore completa em formato legivel:

```bash
python main.py tests/teste1.txt      # imprime a AST e gera o .json
cat tests/teste1_ast.json
```

**4. Depuracao passo a passo com o pdb (debugger do Python):**

```bash
python -m pdb main.py tests/teste1.txt
# comandos uteis: b parser/parser.py:100  (breakpoint)
#                 n (next)  s (step)  c (continue)  p <var> (print)
```

Para parar num ponto especifico, insira `breakpoint()` no codigo (por
exemplo, dentro de `parse_stmt_tail`) e execute normalmente.

**5. Mensagens de erro com linha e tipo:**

Erros lexicos (`LexicalError`) e sintaticos (`RPNSyntaxError`) ja
informam o numero da linha e a descricao do problema. Para listar
*todos* os erros sintaticos de uma vez (em vez de abortar no primeiro),
use a analise com recuperacao em modo panico:

```bash
python -c "from lexer.ler_tokens import lerTokens; from grammar.grammar import construirGramatica; from parser.parser import parsear_com_recuperacao; _, erros = parsear_com_recuperacao(lerTokens('tests/teste1.txt'), construirGramatica()); [print(e) for e in erros]"
```

---

## Pipeline do Compilador

```
Arquivo .txt
    |
    v
[Lexer]  lerTokens() -> Lista de Tokens
    |
    v
[Gramatica]  construirGramatica() -> FIRST, FOLLOW, Tabela LL(1)
    |
    v
[Parser]  parsear() -> Arvore de Derivacao
    |
    v
[AST Builder]  gerarArvore() -> AST
    |
    v
[CodeGen]  gerarAssembly() -> Codigo ARMv7
    |
    v
Arquivo .s + .json
```

---

## Garantia de LL(1)

O projeto **garante** que a gramatica e o parser sao genuinamente LL(1):

1. A construcao da tabela em `grammar/ll1_table.py` **levanta excecao**
   se qualquer celula receberia duas producoes distintas (ou seja, se
   houvesse qualquer conflito FIRST/FIRST ou FIRST/FOLLOW).

2. O parser em `parser/parser.py` consulta **apenas** `M[A, a]` com
   o topo da pilha e o token atual — nao ha lookahead adicional,
   backtracking, ou logica ad-hoc.

3. Os testes em `tests/test_grammar.py` verificam explicitamente
   que nao ha conflitos FIRST/FIRST nem FIRST/FOLLOW em nenhuma
   producao.

Para inspecionar a tabela:

```python
from grammar.grammar import construirGramatica
from grammar.ll1_table import imprimir_tabela

g = construirGramatica()
imprimir_tabela(g)
```

---

## Documentacao da Gramatica

Ver `docs/gramatica.txt` para a especificacao formal completa em EBNF,
com producoes numeradas, conjuntos FIRST e FOLLOW calculados, e analise
de conflitos.

---

## Detalhes do Assembly Gerado

- Target: **ARMv7 DE1-SoC (CPUlator v16.1)**
- Ponto flutuante: **IEEE 754 double-precision (64 bits)**
- Extensao: **VFPv3** (instrucoes `VADD.F64`, `VSUB.F64`, etc.)
- Memoria: variaveis alocadas como `.double` (8 bytes, alinhadas)
- Historico de resultados (`CMD_RES`): armazenado em slots `res_N`
- Halt: loop infinito ao final (bare-metal)
