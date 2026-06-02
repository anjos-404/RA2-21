# Relatório de Erros Semânticos

Arquivo de teste: `tests/teste3.txt`

- Linha 10: variável 'CONTADOR' usada antes de ser definida
- Linha 23: operador '/' (divisão inteira) exige operandos inteiros, mas recebeu 'real' e 'int'
- Linha 26: operador '%' (resto (módulo)) exige operandos inteiros, mas recebeu 'real' e 'int'
- Linha 30: variável 'K' foi definida como 'int' e não pode receber valor 'real' (tipagem estática e forte)
- Linha 40: RES(99) referencia um resultado inexistente — há 16 resultado(s) anterior(es) disponível(is)
