Trabalho — Linguagens Formais e Compiladores
Informações
Instituição: PUC-PR

Disciplina: Linguagens Formais e Compiladores

Professor: FRANK COELHO DE ALCANTARA

Integrantes:

Christopher Gabriel Miranda da Cruz — GitHub: Miiranda45

Mauricio dos Anjos Souza — GitHub: anjos-404

Objetivo
Implementar um compilador completo para uma linguagem simplificada baseada em Notação Polonesa Reversa (RPN). O projeto engloba desde a Análise Léxica até a Análise Sintática (Parser LL(1) Descendente Recursivo), Geração de Árvore Sintática Abstrata (AST) e, finalmente, a tradução para código Assembly compatível com a arquitetura ARMv7 DEC1-SOC (CPULATOR).

Funcionalidades e Operações Suportadas
O compilador lida nativamente com números de ponto flutuante (IEEE 754 Double Precision) e inteiros, suportando:

Operações Básicas: Adição (+), Subtração (-), Multiplicação (*), Divisão Real (|).

Operações Avançadas: Divisão Inteira (/), Resto da divisão (%) e Potenciação (^).

Suporte a Variáveis Dinâmicas: É possível atribuir e ler variáveis da memória (usando letras 100% maiúsculas, ex: X, CONTADOR).

Histórico de Resultados (RES): O comando N RES recupera o resultado de N operações anteriores.

Estruturas de Controle: Tomada de decisão (IF, IFELSE) e laços de repetição (WHILE), todos mantendo a notação RPN com os blocos delimitados por colchetes [ ].

Exemplo IF: ((X) 5 > [(1 RES)] IF)

Exemplo WHILE: ((CONT) 10 < [((CONT) 1 + CONT)] WHILE)

Arquitetura e Funcionamento
O pipeline do compilador foi arquitetado em etapas modulares:

Analisador Léxico: Lê o arquivo-fonte e converte a string em uma lista de Tokens tipados, ignorando espaços e comentários.

Construção da Gramática: Monta as regras EBNF da linguagem, calcula os conjuntos teóricos FIRST e FOLLOW, e constrói a Tabela de Análise LL(1) garantindo o determinismo.

Análise Sintática (Parser): Utiliza um parser preditivo tabular descendente recursivo com pilha para validar a sequência de tokens contra a tabela LL(1), gerando uma árvore de derivação inicial.

Geração da AST: Transforma a árvore de derivação bruta em uma Árvore Sintática Abstrata (AST) enxuta, mapeando operações matemáticas e blocos lógicos.

Gerador de Código Assembly: Aplica o padrão Visitor para percorrer a AST de baixo para cima. Utiliza uma estratégia avançada de Pool de Registradores (Fila de registradores livres) para resolver expressões altamente aninhadas usando a Unidade de Ponto Flutuante (FPU) do ARMv7, sem sobrescrever valores temporários.

Compilação e Uso
Executando o script Python
Crie um arquivo de texto (ex: teste1.txt) contendo o código RPN, sempre começando com (START) e terminando com (END). Em seguida, execute o arquivo principal passando o teste como argumento:

Bash
python main.py tests/teste1.txt