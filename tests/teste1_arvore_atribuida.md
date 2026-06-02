<!-- Arquivo de teste usado: tests/teste1.txt -->

# Árvore Sintática Atribuída

- **Programa**  — categoria=programa
  · statements:
    - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=10
      · esquerda:
        - **Number** (valor=10)  — categoria=literal_inteiro, tipo=int, linha=10
      · direita:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=10
    - **BinOp** (op='-')  — categoria=expressao_aritmetica, tipo=int, linha=11
      · esquerda:
        - **Number** (valor=20)  — categoria=literal_inteiro, tipo=int, linha=11
      · direita:
        - **Number** (valor=8)  — categoria=literal_inteiro, tipo=int, linha=11
    - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=int, linha=12
      · esquerda:
        - **Number** (valor=6)  — categoria=literal_inteiro, tipo=int, linha=12
      · direita:
        - **Number** (valor=7)  — categoria=literal_inteiro, tipo=int, linha=12
    - **BinOp** (op='|')  — categoria=expressao_aritmetica, tipo=real, linha=13
      · esquerda:
        - **Number** (valor=7.5)  — categoria=literal_real, tipo=real, linha=13
      · direita:
        - **Number** (valor=2.5)  — categoria=literal_real, tipo=real, linha=13
    - **BinOp** (op='/')  — categoria=expressao_aritmetica, tipo=int, linha=14
      · esquerda:
        - **Number** (valor=20)  — categoria=literal_inteiro, tipo=int, linha=14
      · direita:
        - **Number** (valor=4)  — categoria=literal_inteiro, tipo=int, linha=14
    - **BinOp** (op='%')  — categoria=expressao_aritmetica, tipo=int, linha=15
      · esquerda:
        - **Number** (valor=17)  — categoria=literal_inteiro, tipo=int, linha=15
      · direita:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=15
    - **BinOp** (op='^')  — categoria=expressao_aritmetica, tipo=int, linha=16
      · esquerda:
        - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=16
      · direita:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=16
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 19, 'valor': 100, 'is_real': False}, mem=VALOR)  — categoria=atribuicao_memoria, tipo=int, linha=19, símbolo→int@L19
      · valor:
        - **Number** (valor=100)  — categoria=literal_inteiro, tipo=int, linha=19
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_real', 'tipo': 'real', 'linha': 20, 'valor': 3.14, 'is_real': True}, mem=PI)  — categoria=atribuicao_memoria, tipo=real, linha=20, símbolo→real@L20
      · valor:
        - **Number** (valor=3.14)  — categoria=literal_real, tipo=real, linha=20
    - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=real, linha=21
      · esquerda:
        - **MemRead** (mem=PI)  — categoria=leitura_memoria, tipo=real, linha=21, símbolo→real@L20
      · direita:
        - **Number** (valor=2.0)  — categoria=literal_real, tipo=real, linha=21
    - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=real, linha=22
      · esquerda:
        - **MemRead** (mem=VALOR)  — categoria=leitura_memoria, tipo=int, linha=22, símbolo→int@L19
      · direita:
        - **MemRead** (mem=PI)  — categoria=leitura_memoria, tipo=real, linha=22, símbolo→real@L20
    - **MemRead** (mem=VALOR)  — categoria=leitura_memoria, tipo=int, linha=23, símbolo→int@L19
    - **Res** (n=1)  — categoria=resultado_anterior, tipo=real, linha=24
    - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=27
      · esquerda:
        - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=27
          · esquerda:
            - **Number** (valor=3)  — categoria=literal_inteiro, tipo=int, linha=27
          · direita:
            - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=27
      · direita:
        - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=int, linha=27
          · esquerda:
            - **Number** (valor=4)  — categoria=literal_inteiro, tipo=int, linha=27
          · direita:
            - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=27
    - **BinOp** (op='^')  — categoria=expressao_aritmetica, tipo=int, linha=28
      · esquerda:
        - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=int, linha=28
          · esquerda:
            - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=28
              · esquerda:
                - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=28
              · direita:
                - **Number** (valor=3)  — categoria=literal_inteiro, tipo=int, linha=28
          · direita:
            - **Number** (valor=4)  — categoria=literal_inteiro, tipo=int, linha=28
      · direita:
        - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=28
    - **If**  — categoria=decisao_composta, linha=31
      · condicao:
        - **Condition** (op='>')  — categoria=condicao_relacional, tipo=bool, linha=31
          · esquerda:
            - **MemRead** (mem=VALOR)  — categoria=leitura_memoria, tipo=int, linha=31, símbolo→int@L19
          · direita:
            - **Number** (valor=50)  — categoria=literal_inteiro, tipo=int, linha=31
      · then:
        - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 31, 'valor': 1, 'is_real': False}, mem=FLAG)  — categoria=atribuicao_memoria, tipo=int, linha=31, símbolo→int@L31
          · valor:
            - **Number** (valor=1)  — categoria=literal_inteiro, tipo=int, linha=31
      · else:
        - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 31, 'valor': 0, 'is_real': False}, mem=FLAG)  — categoria=atribuicao_memoria, tipo=int, linha=31, símbolo→int@L31
          · valor:
            - **Number** (valor=0)  — categoria=literal_inteiro, tipo=int, linha=31
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 32, 'valor': 0, 'is_real': False}, mem=CONT)  — categoria=atribuicao_memoria, tipo=int, linha=32, símbolo→int@L32
      · valor:
        - **Number** (valor=0)  — categoria=literal_inteiro, tipo=int, linha=32
    - **While**  — categoria=repeticao, linha=33
      · condicao:
        - **Condition** (op='<')  — categoria=condicao_relacional, tipo=bool, linha=33
          · esquerda:
            - **MemRead** (mem=CONT)  — categoria=leitura_memoria, tipo=int, linha=33, símbolo→int@L32
          · direita:
            - **Number** (valor=3)  — categoria=literal_inteiro, tipo=int, linha=33
      · corpo:
        - **MemWrite** (valor={'no': 'BinOp', 'categoria': 'expressao_aritmetica', 'tipo': 'int', 'linha': 33, 'op': '+', 'esquerda': {'no': 'MemRead', 'categoria': 'leitura_memoria', 'tipo': 'int', 'linha': 33, 'nome': 'CONT', 'simbolo': {'tipo': 'int', 'linha_definicao': 32}}, 'direita': {'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 33, 'valor': 1, 'is_real': False}}, mem=CONT)  — categoria=atribuicao_memoria, tipo=int, linha=33, símbolo→int@L32
          · valor:
            - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=33
              · esquerda:
                - **MemRead** (mem=CONT)  — categoria=leitura_memoria, tipo=int, linha=33, símbolo→int@L32
              · direita:
                - **Number** (valor=1)  — categoria=literal_inteiro, tipo=int, linha=33
    - **MemRead** (mem=CONT)  — categoria=leitura_memoria, tipo=int, linha=34, símbolo→int@L32
