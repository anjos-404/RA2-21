<!-- Arquivo de teste usado: tests/teste2.txt -->

# Árvore Sintática Atribuída

- **Programa**  — categoria=programa
  · statements:
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 9, 'valor': 42, 'is_real': False}, mem=X)  — categoria=atribuicao_memoria, tipo=int, linha=9, símbolo→int@L9
      · valor:
        - **Number** (valor=42)  — categoria=literal_inteiro, tipo=int, linha=9
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_real', 'tipo': 'real', 'linha': 10, 'valor': 3.14, 'is_real': True}, mem=PI)  — categoria=atribuicao_memoria, tipo=real, linha=10, símbolo→real@L10
      · valor:
        - **Number** (valor=3.14)  — categoria=literal_real, tipo=real, linha=10
    - **MemRead** (mem=X)  — categoria=leitura_memoria, tipo=int, linha=11, símbolo→int@L9
    - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=14
      · esquerda:
        - **MemRead** (mem=X)  — categoria=leitura_memoria, tipo=int, linha=14, símbolo→int@L9
      · direita:
        - **Number** (valor=8)  — categoria=literal_inteiro, tipo=int, linha=14
    - **BinOp** (op='-')  — categoria=expressao_aritmetica, tipo=int, linha=15
      · esquerda:
        - **MemRead** (mem=X)  — categoria=leitura_memoria, tipo=int, linha=15, símbolo→int@L9
      · direita:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=15
    - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=real, linha=16
      · esquerda:
        - **MemRead** (mem=PI)  — categoria=leitura_memoria, tipo=real, linha=16, símbolo→real@L10
      · direita:
        - **Number** (valor=2.0)  — categoria=literal_real, tipo=real, linha=16
    - **BinOp** (op='|')  — categoria=expressao_aritmetica, tipo=real, linha=17
      · esquerda:
        - **Number** (valor=10.0)  — categoria=literal_real, tipo=real, linha=17
      · direita:
        - **Number** (valor=4.0)  — categoria=literal_real, tipo=real, linha=17
    - **BinOp** (op='/')  — categoria=expressao_aritmetica, tipo=int, linha=18
      · esquerda:
        - **Number** (valor=17)  — categoria=literal_inteiro, tipo=int, linha=18
      · direita:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=18
    - **BinOp** (op='%')  — categoria=expressao_aritmetica, tipo=int, linha=19
      · esquerda:
        - **Number** (valor=17)  — categoria=literal_inteiro, tipo=int, linha=19
      · direita:
        - **Number** (valor=5)  — categoria=literal_inteiro, tipo=int, linha=19
    - **BinOp** (op='^')  — categoria=expressao_aritmetica, tipo=int, linha=20
      · esquerda:
        - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=20
      · direita:
        - **Number** (valor=8)  — categoria=literal_inteiro, tipo=int, linha=20
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 23, 'valor': 50, 'is_real': False}, mem=Y)  — categoria=atribuicao_memoria, tipo=int, linha=23, símbolo→int@L23
      · valor:
        - **Number** (valor=50)  — categoria=literal_inteiro, tipo=int, linha=23
    - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=int, linha=24
      · esquerda:
        - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=24
          · esquerda:
            - **MemRead** (mem=X)  — categoria=leitura_memoria, tipo=int, linha=24, símbolo→int@L9
          · direita:
            - **MemRead** (mem=Y)  — categoria=leitura_memoria, tipo=int, linha=24, símbolo→int@L23
      · direita:
        - **BinOp** (op='-')  — categoria=expressao_aritmetica, tipo=int, linha=24
          · esquerda:
            - **MemRead** (mem=X)  — categoria=leitura_memoria, tipo=int, linha=24, símbolo→int@L9
          · direita:
            - **MemRead** (mem=Y)  — categoria=leitura_memoria, tipo=int, linha=24, símbolo→int@L23
    - **BinOp** (op='|')  — categoria=expressao_aritmetica, tipo=real, linha=25
      · esquerda:
        - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=real, linha=25
          · esquerda:
            - **MemRead** (mem=PI)  — categoria=leitura_memoria, tipo=real, linha=25, símbolo→real@L10
          · direita:
            - **Number** (valor=1.0)  — categoria=literal_real, tipo=real, linha=25
      · direita:
        - **BinOp** (op='*')  — categoria=expressao_aritmetica, tipo=int, linha=25
          · esquerda:
            - **MemRead** (mem=X)  — categoria=leitura_memoria, tipo=int, linha=25, símbolo→int@L9
          · direita:
            - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=25
    - **Res** (n=1)  — categoria=resultado_anterior, tipo=real, linha=26
    - **If**  — categoria=decisao_composta, linha=29
      · condicao:
        - **Condition** (op='>')  — categoria=condicao_relacional, tipo=bool, linha=29
          · esquerda:
            - **MemRead** (mem=X)  — categoria=leitura_memoria, tipo=int, linha=29, símbolo→int@L9
          · direita:
            - **Number** (valor=0)  — categoria=literal_inteiro, tipo=int, linha=29
      · then:
        - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 29, 'valor': 1, 'is_real': False}, mem=POS)  — categoria=atribuicao_memoria, tipo=int, linha=29, símbolo→int@L29
          · valor:
            - **Number** (valor=1)  — categoria=literal_inteiro, tipo=int, linha=29
      · else:
        - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 29, 'valor': 0, 'is_real': False}, mem=POS)  — categoria=atribuicao_memoria, tipo=int, linha=29, símbolo→int@L29
          · valor:
            - **Number** (valor=0)  — categoria=literal_inteiro, tipo=int, linha=29
    - **MemWrite** (valor={'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 30, 'valor': 0, 'is_real': False}, mem=I)  — categoria=atribuicao_memoria, tipo=int, linha=30, símbolo→int@L30
      · valor:
        - **Number** (valor=0)  — categoria=literal_inteiro, tipo=int, linha=30
    - **While**  — categoria=repeticao, linha=31
      · condicao:
        - **Condition** (op='<')  — categoria=condicao_relacional, tipo=bool, linha=31
          · esquerda:
            - **MemRead** (mem=I)  — categoria=leitura_memoria, tipo=int, linha=31, símbolo→int@L30
          · direita:
            - **Number** (valor=2)  — categoria=literal_inteiro, tipo=int, linha=31
      · corpo:
        - **MemWrite** (valor={'no': 'BinOp', 'categoria': 'expressao_aritmetica', 'tipo': 'int', 'linha': 31, 'op': '+', 'esquerda': {'no': 'MemRead', 'categoria': 'leitura_memoria', 'tipo': 'int', 'linha': 31, 'nome': 'I', 'simbolo': {'tipo': 'int', 'linha_definicao': 30}}, 'direita': {'no': 'Number', 'categoria': 'literal_inteiro', 'tipo': 'int', 'linha': 31, 'valor': 1, 'is_real': False}}, mem=I)  — categoria=atribuicao_memoria, tipo=int, linha=31, símbolo→int@L30
          · valor:
            - **BinOp** (op='+')  — categoria=expressao_aritmetica, tipo=int, linha=31
              · esquerda:
                - **MemRead** (mem=I)  — categoria=leitura_memoria, tipo=int, linha=31, símbolo→int@L30
              · direita:
                - **Number** (valor=1)  — categoria=literal_inteiro, tipo=int, linha=31
    - **MemRead** (mem=I)  — categoria=leitura_memoria, tipo=int, linha=32, símbolo→int@L30
