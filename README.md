# Compilador RPN — Analisador Sintatico LL(1) + Assembly ARMv7

**Fase 2: Analisador Sintatico LL(1)**

## Informacoes

- **Instituicao:** PUC-PR
- **Disciplina:** Linguagens Formais e Compiladores
- **Professor:** Frank Coelho de Alcantara

### Integrantes

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

## Uso

### Compilacao

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

# Apenas gramatica
pytest tests/test_grammar.py -v

# Apenas parser
pytest tests/test_parser.py -v

# Apenas integracao
pytest tests/test_integration.py -v
```

**99 testes unitarios e de integracao, todos passando.**

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
