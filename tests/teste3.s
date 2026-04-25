@ ============================================
@ Compilador RPN -> Assembly ARMv7 (CPulator)
@ IEEE 754 Double Precision (64-bit)
@ Target: DEC1-SOC (v16.1) - VFPv3
@ ============================================

.global _start
.text

_start:
    @ --- Statement ---
    MOV R0, #3
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #2
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VADD.F64 D0, D0, D1  @ soma IEEE 754
    VPUSH {D0}              @ salvar operando esquerdo
    MOV R0, #4
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #5
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VMUL.F64 D1, D0, D1  @ multiplicacao IEEE 754
    VPOP {D0}               @ restaurar operando esquerdo
    VADD.F64 D2, D0, D1  @ soma IEEE 754
    LDR R0, =res_1
    VSTR.F64 D2, [R0]    @ salvar resultado #1

    @ --- Statement ---
    MOV R0, #7
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #3
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    @ Resto (modulo) IEEE 754
    VDIV.F64 D3, D0, D1      @ D3 = A / B
    VCVT.S32.F64 S14, D3                 @ truncar para int32
    VCVT.F64.S32 D3, S14                 @ D3 = trunc(A/B)
    VMUL.F64 D3, D3, D1            @ D3 = trunc(A/B) * B
    VSUB.F64 D0, D0, D3        @ resultado = A - trunc(A/B)*B
    VPUSH {D0}              @ salvar operando esquerdo
    MOV R0, #2
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #4
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VMUL.F64 D1, D0, D1  @ multiplicacao IEEE 754
    VPOP {D0}               @ restaurar operando esquerdo
    @ Divisao real IEEE 754
    VDIV.F64 D2, D0, D1  @ divisao real
    LDR R0, =res_2
    VSTR.F64 D2, [R0]    @ salvar resultado #2

    @ --- Statement ---
    MOV R0, #2
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #3
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VADD.F64 D0, D0, D1  @ soma IEEE 754
    VPUSH {D0}              @ salvar operando esquerdo
    MOV R0, #4
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #5
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VMUL.F64 D1, D0, D1  @ multiplicacao IEEE 754
    VPOP {D0}               @ restaurar operando esquerdo
    VSUB.F64 D0, D0, D1  @ subtracao IEEE 754
    MOV R0, #2
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    @ Potenciacao IEEE 754 (loop F64)
    LDR R0, =const_3
    VLDR.F64 D2, [R0]    @ resultado = 1.0
    VMOV.F64 D4, D1    @ D4 = expoente (contador)
    VMOV.F64 D3, D0    @ D3 = base
    LDR R0, =const_3
    VLDR.F64 D5, [R0]        @ D5 = 1.0 (decremento)
    LDR R0, =const_4
    VLDR.F64 D6, [R0]        @ D6 = 0.0 (limite)
POW_LOOP_1:
    VCMP.F64 D4, D6
    VMRS APSR_nzcv, FPSCR    @ flags VFP -> APSR
    BLE POW_FIM_2           @ sair se contador <= 0
    VMUL.F64 D2, D2, D3  @ resultado *= base
    VSUB.F64 D4, D4, D5      @ contador -= 1.0
    B POW_LOOP_1
POW_FIM_2:
    LDR R0, =res_3
    VSTR.F64 D2, [R0]    @ salvar resultado #3

    @ --- Statement ---
    MOV R0, #3
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #2
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VADD.F64 D0, D0, D1  @ soma IEEE 754
    VPUSH {D0}              @ salvar operando esquerdo
    MOV R0, #4
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #5
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VMUL.F64 D1, D0, D1  @ multiplicacao IEEE 754
    VPOP {D0}               @ restaurar operando esquerdo
    VSUB.F64 D0, D0, D1  @ subtracao IEEE 754
    LDR R0, =mem_MEURES
    VSTR.F64 D0, [R0]    @ escrever MEURES
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_4
    VSTR.F64 D2, [R0]    @ salvar resultado #4

    @ --- Statement ---
    MOV R0, #20
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    MOV R0, #6
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    @ Divisao inteira IEEE 754
    VDIV.F64 D2, D0, D1  @ divisao
    VCVT.S32.F64 S14, D2             @ truncar para int32
    VCVT.F64.S32 D2, S14             @ converter de volta para double
    LDR R0, =res_5
    VSTR.F64 D2, [R0]    @ salvar resultado #5

    @ --- Statement ---
    MOV R0, #0
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    LDR R0, =mem_SOMA
    VSTR.F64 D0, [R0]    @ escrever SOMA
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_6
    VSTR.F64 D2, [R0]    @ salvar resultado #6

    @ --- Statement ---
    MOV R0, #1
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    LDR R0, =mem_N
    VSTR.F64 D0, [R0]    @ escrever N
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_7
    VSTR.F64 D2, [R0]    @ salvar resultado #7

    @ --- Statement ---
    @ WHILE
LOOP_5:
    LDR R0, =mem_N
    VLDR.F64 D0, [R0]    @ ler memoria N
    MOV R0, #5
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VCMP.F64 D0, D1
    VMRS APSR_nzcv, FPSCR    @ copiar flags VFP para APSR
    BGT FIM_LOOP_6        @ pular se NAO(<=)
    @ [body]
    LDR R0, =mem_SOMA
    VLDR.F64 D0, [R0]    @ ler memoria SOMA
    LDR R0, =mem_N
    VLDR.F64 D1, [R0]    @ ler memoria N
    VADD.F64 D0, D0, D1  @ soma IEEE 754
    LDR R0, =mem_SOMA
    VSTR.F64 D0, [R0]    @ escrever SOMA
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_8
    VSTR.F64 D2, [R0]    @ salvar resultado #8
    LDR R0, =mem_N
    VLDR.F64 D0, [R0]    @ ler memoria N
    MOV R0, #1
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VADD.F64 D0, D0, D1  @ soma IEEE 754
    LDR R0, =mem_N
    VSTR.F64 D0, [R0]    @ escrever N
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_9
    VSTR.F64 D2, [R0]    @ salvar resultado #9
    B LOOP_5
FIM_LOOP_6:

    @ --- Statement ---
    @ RES(1): carregar resultado #8
    LDR R0, =res_9
    VLDR.F64 D2, [R0]        @ D2 = resultado de 1 stmt atras
    LDR R0, =res_10
    VSTR.F64 D2, [R0]    @ salvar resultado #10

    @ --- Statement ---
    LDR R0, =mem_SOMA
    VLDR.F64 D0, [R0]    @ ler memoria SOMA
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_11
    VSTR.F64 D2, [R0]    @ salvar resultado #11

    @ --- Statement ---
    @ IF
    LDR R0, =mem_SOMA
    VLDR.F64 D0, [R0]    @ ler memoria SOMA
    MOV R0, #10
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VCMP.F64 D0, D1
    VMRS APSR_nzcv, FPSCR    @ copiar flags VFP para APSR
    BLE ELSE_7        @ pular se NAO(>)
    @ [then]
    MOV R0, #1
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    LDR R0, =mem_OK
    VSTR.F64 D0, [R0]    @ escrever OK
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_12
    VSTR.F64 D2, [R0]    @ salvar resultado #12
    B FIM_IF_8
ELSE_7:
    @ [else]
    MOV R0, #0
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    LDR R0, =mem_OK
    VSTR.F64 D0, [R0]    @ escrever OK
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_13
    VSTR.F64 D2, [R0]    @ salvar resultado #13
FIM_IF_8:

    @ --- Statement ---
    LDR R0, =mem_OK
    VLDR.F64 D0, [R0]    @ ler memoria OK
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_14
    VSTR.F64 D2, [R0]    @ salvar resultado #14

    @ --- Statement ---
    MOV R0, #100
    VMOV S0, R0               @ int para VFP (via S0)
    VCVT.F64.S32 D0, S0   @ converter int32 para F64
    LDR R0, =mem_X
    VSTR.F64 D0, [R0]    @ escrever X
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_15
    VSTR.F64 D2, [R0]    @ salvar resultado #15

    @ --- Statement ---
    @ IF
    LDR R0, =mem_X
    VLDR.F64 D0, [R0]    @ ler memoria X
    MOV R0, #50
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VCMP.F64 D0, D1
    VMRS APSR_nzcv, FPSCR    @ copiar flags VFP para APSR
    BLT ELSE_9        @ pular se NAO(>=)
    @ [then]
    LDR R0, =mem_X
    VLDR.F64 D0, [R0]    @ ler memoria X
    MOV R0, #2
    VMOV S2, R0               @ int para VFP (via S2)
    VCVT.F64.S32 D1, S2   @ converter int32 para F64
    VMUL.F64 D0, D0, D1  @ multiplicacao IEEE 754
    LDR R0, =mem_X
    VSTR.F64 D0, [R0]    @ escrever X
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_16
    VSTR.F64 D2, [R0]    @ salvar resultado #16
    B FIM_IF_10
ELSE_9:
FIM_IF_10:

    @ --- Statement ---
    LDR R0, =mem_MEURES
    VLDR.F64 D0, [R0]    @ ler memoria MEURES
    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)
    LDR R0, =res_17
    VSTR.F64 D2, [R0]    @ salvar resultado #17

    @ --- Statement ---
    @ RES(1): carregar resultado #13
    LDR R0, =res_17
    VLDR.F64 D2, [R0]        @ D2 = resultado de 1 stmt atras
    LDR R0, =res_18
    VSTR.F64 D2, [R0]    @ salvar resultado #18

    @ Fim do programa
_halt:
    B _halt          @ loop infinito (halt)

.ltorg

@ ============================================
@ Secao de dados
@ ============================================
.data

@ --- Slots de resultado para RES (double, 8 bytes) ---
.align 3
res_1:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #1
.align 3
res_2:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #2
.align 3
res_3:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #3
.align 3
res_4:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #4
.align 3
res_5:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #5
.align 3
res_6:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #6
.align 3
res_7:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #7
.align 3
res_8:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #8
.align 3
res_9:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #9
.align 3
res_10:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #10
.align 3
res_11:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #11
.align 3
res_12:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #12
.align 3
res_13:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #13
.align 3
res_14:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #14
.align 3
res_15:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #15
.align 3
res_16:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #16
.align 3
res_17:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #17
.align 3
res_18:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - resultado #18

@ --- Variaveis de memoria (double, 8 bytes) ---
.align 3
mem_MEURES:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - MEURES
.align 3
mem_SOMA:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - SOMA
.align 3
mem_N:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - N
.align 3
mem_OK:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - OK
.align 3
mem_X:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high) - X

@ --- Constantes IEEE 754 double ---
.align 3
const_3:
    .word 0x00000000  @ double 1.0 (low)
    .word 0x3FF00000  @ double 1.0 (high)
.align 3
const_4:
    .word 0x00000000  @ double 0.0 (low)
    .word 0x00000000  @ double 0.0 (high)