<!-- Arquivo de teste usado: tests/teste3.txt -->

# Árvore Sintática Atribuída

- **Programa**  — categoria=programa
  · statements:
    - **MemRead** (mem=CONTADOR)  — categoria=leitura_memoria, linha=10
    - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=13
      · esquerda:
        - **Number** (valor=8)  — categoria=literal_inteiro, tipo=int, linha=13
      · direita:
        - **Number** (valor=3)  — categoria=literal_inteiro, tipo=int, linha=13
    - **BinOp** (op='-')  — categoria=expressao_aritmetica, tipo=int, linha=14
      · esquerda:
        - **Number** (valor=9)  — categoria=literal_inteiro, tipo=int, linha=14
      · direita:
        - **Number** (valor=4)  — categoria=literal_inteiro, tipo=int, linha=14
    - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=int, linha=15
      · esquerda:
        - **Number** (valor=6)  — categoria=literal_inteiro, tipo=int, linha=15
      · direita:
        - **Number** (valor=7)  — categoria=literal_inteiro, tipo=int, linha=15
    - **BinOp** (op='|')  — categoria=expressao_aritmetica, tipo=real, linha=16
      · esquerda:
        - **Number** (valor=10.0)  — categoria=literal_real, tipo=real, linha=16
      · direita:
        - **Number** (valor=4.0)  — categoria=literal_real, tipo=real, linha=16
    - **BinOp** (op='/')  — categoria=expressao_aritmetica, tipo=int, linha=17
      · esquerda:
        - **Number** (valor=20)  — categoria=literal_inteiro, tipo=int, linha=17
      · direita:
        - **Number** (valor=6)  — categoria=literal_inteiro, tipo=int, linha=17
    - **BinOp** (op='%')  — categoria=expressao_aritmetica, tipo=int, linha=18
      · esquerda:
        - **Number** (valor=17)  — categoria=literal_inteiro, tipo=int, linha=18
      · direita:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=18
    - **BinOp** (op='^')  — categoria=expressao_aritmetica, tipo=int, linha=19
      · esquerda:
        - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=19
      · direita:
        - **Number** (valor=6)  — categoria=literal_inteiro, tipo=int, linha=19
    - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=20
      · esquerda:
        - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=20
          · esquerda:
            - **Number** (valor=3)  — categoria=literal_inteiro, tipo=int, linha=20
          · direita:
            - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=20
      · direita:
        - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=int, linha=20
          · esquerda:
            - **Number** (valor=4)  — categoria=literal_inteiro, tipo=int, linha=20
          · direita:
            - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=20
    - **BinOp** (op='/')  — categoria=expressao_aritmetica, tipo=int, linha=23
      · esquerda:
        - **Number** (valor=7.5)  — categoria=literal_real, tipo=real, linha=23
      · direita:
        - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=23
    - **BinOp** (op='%')  — categoria=expressao_aritmetica, tipo=int, linha=26
      · esquerda:
        - **Number** (valor=9.0)  — categoria=literal_real, tipo=real, linha=26
      · direita:
        - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=26
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 29, 'valor': 5, 'is_real': False}, mem=K)  — categoria=atribuicao_memoria, tipo=int, linha=29, símbolo→int@L29
      · valor:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=29
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_real', 'tipo': 'real', 'linha': 30, 'valor': 2.5, 'is_real': True}, mem=K)  — categoria=atribuicao_memoria, tipo=real, linha=30, símbolo→int@L29
      · valor:
        - **Number** (valor=2.5)  — categoria=literal_real, tipo=real, linha=30
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 33, 'valor': 0, 'is_real': False}, mem=SOMA)  — categoria=atribuicao_memoria, tipo=int, linha=33, símbolo→int@L33
      · valor:
        - **Number** (valor=0)  — categoria=literal_inteiro, tipo=int, linha=33
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 34, 'valor': 1, 'is_real': False}, mem=N)  — categoria=atribuicao_memoria, tipo=int, linha=34, símbolo→int@L34
      · valor:
        - **Number** (valor=1)  — categoria=literal_inteiro, tipo=int, linha=34
    - **While**  — categoria=repeticao, linha=35
      · condicao:
        - **Condition** (op='<=')  — categoria=condicao_relacional, tipo=bool, linha=35
          · esquerda:
            - **MemRead** (mem=N)  — categoria=leitura_memoria, tipo=int, linha=35, símbolo→int@L34
          · direita:
            - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=35
      · corpo:
        - **MemWrite** (valor={'no': 'BinOp', 'categoria': 'expressao_aritmetica', 'tipo': 'int', 'linha': 35, 'op': '+', 'esquerda': {'no': 'MemRead', 'categoria': 'leitura_memoria', 'tipo': 'int', 'linha': 35, 'nome': 'SOMA', 'simbolo': {'tipo': 'int', 'linha_definicao': 33}}, 'direita': {'no': 'MemRead', 'categoria': 'leitura_memoria', 'tipo': 'int', 'linha': 35, 'nome': 'N', 'simbolo': {'tipo': 'int', 'linha_definicao': 34}}}, mem=SOMA)  — categoria=atribuicao_memoria, tipo=int, linha=35, símbolo→int@L33
          · valor:
            - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=35
              · esquerda:
                - **MemRead** (mem=SOMA)  — categoria=leitura_memoria, tipo=int, linha=35, símbolo→int@L33
              · direita:
                - **MemRead** (mem=N)  — categoria=leitura_memoria, tipo=int, linha=35, símbolo→int@L34
        - **MemWrite** (valor={'no': 'BinOp', 'categoria': 'expressao_aritmetica', 'tipo': 'int', 'linha': 35, 'op': '+', 'esquerda': {'no': 'MemRead', 'categoria': 'leitura_memoria', 'tipo': 'int', 'linha': 35, 'nome': 'N', 'simbolo': {'tipo': 'int', 'linha_definicao': 34}}, 'direita': {'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 35, 'valor': 1, 'is_real': False}}, mem=N)  — categoria=atribuicao_memoria, tipo=int, linha=35, símbolo→int@L34
          · valor:
            - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=35
              · esquerda:
                - **MemRead** (mem=N)  — categoria=leitura_memoria, tipo=int, linha=35, símbolo→int@L34
              · direita:
                - **Number** (valor=1)  — categoria=literal_inteiro, tipo=int, linha=35
    - **If**  — categoria=decisao_composta, linha=36
      · condicao:
        - **Condition** (op='>')  — categoria=condicao_relacional, tipo=bool, linha=36
          · esquerda:
            - **MemRead** (mem=SOMA)  — categoria=leitura_memoria, tipo=int, linha=36, símbolo→int@L33
          · direita:
            - **Number** (valor=10)  — categoria=literal_inteiro, tipo=int, linha=36
      · then:
        - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 36, 'valor': 1, 'is_real': False}, mem=OK)  — categoria=atribuicao_memoria, tipo=int, linha=36, símbolo→int@L36
          · valor:
            - **Number** (valor=1)  — categoria=literal_inteiro, tipo=int, linha=36
      · else:
        - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 36, 'valor': 0, 'is_real': False}, mem=OK)  — categoria=atribuicao_memoria, tipo=int, linha=36, símbolo→int@L36
          · valor:
            - **Number** (valor=0)  — categoria=literal_inteiro, tipo=int, linha=36
    - **MemRead** (mem=OK)  — categoria=leitura_memoria, tipo=int, linha=37, símbolo→int@L36
    - **Res** (n=99)  — categoria=resultado_anterior, tipo=real, linha=40
