# codegen/assembly_gen.py — Parte 4

from parser.ast_nodes import *
import struct


class AssemblyGenerator:
    """
        D0:    operando esquerdo / resultado temporário
        D1:    operando direito
        D2:    resultado da operação / acumulador
        D3–D5: temporários para expressões aninhadas
        R0–R3: registradores ARM auxiliares (endereços, contadores)
    Variáveis de memória armazenadas como .double (8 bytes, alinhadas).
    """

    def __init__(self):
        self.linhas_asm: list[str] = []
        self.label_count: int = 0
        self.mem_map: dict[str, str] = {}       # MEM_NAME → label
        self.const_pool: dict[str, float] = {}   # label → valor double
        self.historico_resultados: list[str] = []  # para RES (labels dos slots)
        self.res_count: int = 0                  # contador de slots de resultado
        self._rastrear_historico: bool = True    # False dentro de IF/WHILE bodies

    def novo_label(self, prefixo: str = "L") -> str:
        """Gera um label único."""
        self.label_count += 1
        return f"{prefixo}{self.label_count}"

    def emit(self, instrucao: str):
        """Emite uma instrução Assembly."""
        self.linhas_asm.append(instrucao)

    def _double_to_words(self, val: float) -> tuple[int, int]:
        """Converte um double IEEE 754 para dois words (little-endian ARM)."""
        packed = struct.pack('<d', val)
        lo = struct.unpack('<I', packed[0:4])[0]
        hi = struct.unpack('<I', packed[4:8])[0]
        return lo, hi

    def _add_const(self, val: float) -> str:
        """Adiciona uma constante double ao pool e retorna o label."""
        # Reusar label se valor já existe
        for label, existing_val in self.const_pool.items():
            if existing_val == val:
                return label
        label = self.novo_label("const_")
        self.const_pool[label] = val
        return label

    def gerar(self, arvore: ProgramNode) -> str:
        """
        Gera código Assembly completo a partir da AST.
        Retorna string com o código Assembly.
        """
        # Cabeçalho
        self.emit("@ ============================================")
        self.emit("@ Compilador RPN -> Assembly ARMv7 (CPulator)")
        self.emit("@ IEEE 754 Double Precision (64-bit)")
        self.emit("@ Target: DEC1-SOC (v16.1) - VFPv3")
        self.emit("@ ============================================")
        self.emit("")
        self.emit(".global _start")
        self.emit(".text")
        self.emit("")
        self.emit("_start:")

        for stmt in arvore.statements:
            self.emit(f"    @ --- Statement ---")
            self._gerar_stmt(stmt)
            self.emit("")

        # Fim do programa (bare-metal halt)
        self.emit("    @ Fim do programa")
        self.emit("_halt:")
        self.emit("    B _halt          @ loop infinito (halt)")
        self.emit("")
        # Forçar literal pool antes da seção de dados
        self.emit(".ltorg")
        self.emit("")

        # Seção de dados
        self._gerar_secao_dados()

        return "\n".join(self.linhas_asm)

    def _salvar_resultado(self, dreg: str):
        """Salva o resultado do statement atual em um slot de memória (res_N)."""
        self.res_count += 1
        label = f"res_{self.res_count}"
        if self._rastrear_historico:
            self.historico_resultados.append(label)
        self.emit(f"    LDR R0, ={label}")
        self.emit(f"    VSTR.F64 {dreg}, [R0]    @ salvar resultado #{self.res_count}")

    def _gerar_stmt(self, node: ASTNode):
        """Gera Assembly para um statement. """
        if isinstance(node, BinOpNode):
            dreg = self._gerar_binop(node)

            self._salvar_resultado(dreg)
        elif isinstance(node, MemWriteNode):
            self._gerar_mem_write(node)
           
            self.emit(f"    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)")
            self._salvar_resultado("D2")
        elif isinstance(node, MemReadNode):
            self._gerar_mem_read(node, "D0")
            # Valor lido fica em D0 — copiar para D2 (acumulador)
            self.emit(f"    VMOV.F64 D2, D0          @ resultado em D2 (acumulador)")
            self._salvar_resultado("D2")
        elif isinstance(node, ResNode):
            self._gerar_res(node)
        elif isinstance(node, IfNode):
            self._gerar_if(node)

        elif isinstance(node, WhileNode):
            self._gerar_while(node)

    # ==================================================================
    # Operações Aritméticas 
    # ==================================================================

    def _operand_is_complex(self, node: ASTNode) -> bool:
        """Verifica se um operando pode gerar código que clobber D0/D1."""
        return isinstance(node, BinOpNode)

    def _gerar_binop(self, node: BinOpNode, dest: str = "D2") -> str:
        """Gera código VFP para operação binária aritmética (IEEE 754 F64)."""
        dreg_l = self._gerar_operand(node.left, "D0")

        # Se o operando direito é complexo (ex: expressão aninhada),
        # ele pode gerar código que sobrescreve D0. Salvamos D0 na pilha.
        needs_save = self._operand_is_complex(node.right)
        if needs_save:
            self.emit(f"    VPUSH {{D0}}              @ salvar operando esquerdo")

        dreg_r = self._gerar_operand(node.right, "D1")

        if needs_save:
            self.emit(f"    VPOP {{D0}}               @ restaurar operando esquerdo")

        if node.op == "+":
            self.emit(f"    VADD.F64 {dest}, {dreg_l}, {dreg_r}  @ soma IEEE 754")
        elif node.op == "-":
            self.emit(f"    VSUB.F64 {dest}, {dreg_l}, {dreg_r}  @ subtracao IEEE 754")
        elif node.op == "*":
            self.emit(f"    VMUL.F64 {dest}, {dreg_l}, {dreg_r}  @ multiplicacao IEEE 754")
        elif node.op == "/":
            # Divisão inteira: VDIV + truncar para inteiro + converter de volta
            self.emit(f"    @ Divisao inteira IEEE 754")
            self.emit(f"    VDIV.F64 {dest}, {dreg_l}, {dreg_r}  @ divisao")
            self.emit(f"    VCVT.S32.F64 S14, {dest}             @ truncar para int32")
            self.emit(f"    VCVT.F64.S32 {dest}, S14             @ converter de volta para double")
        elif node.op == "%":
            # Resto: A % B = A - trunc(A/B) * B
            self.emit(f"    @ Resto (modulo) IEEE 754")
            self.emit(f"    VDIV.F64 D3, {dreg_l}, {dreg_r}      @ D3 = A / B")
            self.emit(f"    VCVT.S32.F64 S14, D3                 @ truncar para int32")
            self.emit(f"    VCVT.F64.S32 D3, S14                 @ D3 = trunc(A/B)")
            self.emit(f"    VMUL.F64 D3, D3, {dreg_r}            @ D3 = trunc(A/B) * B")
            self.emit(f"    VSUB.F64 {dest}, {dreg_l}, D3        @ resultado = A - trunc(A/B)*B")
        elif node.op == "|":
            # Divisão real (resultado double, sem truncar)
            self.emit(f"    @ Divisao real IEEE 754")
            self.emit(f"    VDIV.F64 {dest}, {dreg_l}, {dreg_r}  @ divisao real")
        elif node.op == "^":
            # Potenciação: base^exp via loop de VMUL.F64 (100% VFP F64)
            label_loop = self.novo_label("POW_LOOP_")
            label_fim = self.novo_label("POW_FIM_")
            const_1 = self._add_const(1.0)
            const_0 = self._add_const(0.0)
            self.emit(f"    @ Potenciacao IEEE 754 (loop F64)")
            # Carregar 1.0 no resultado
            self.emit(f"    LDR R0, ={const_1}")
            self.emit(f"    VLDR.F64 {dest}, [R0]    @ resultado = 1.0")
            # D4 = contador (expoente), D3 = base, D5 = 1.0 (decremento)
            self.emit(f"    VMOV.F64 D4, {dreg_r}    @ D4 = expoente (contador)")
            self.emit(f"    VMOV.F64 D3, {dreg_l}    @ D3 = base")
            self.emit(f"    LDR R0, ={const_1}")
            self.emit(f"    VLDR.F64 D5, [R0]        @ D5 = 1.0 (decremento)")
            # Carregar 0.0 para comparação
            self.emit(f"    LDR R0, ={const_0}")
            self.emit(f"    VLDR.F64 D6, [R0]        @ D6 = 0.0 (limite)")
            self.emit(f"{label_loop}:")
            self.emit(f"    VCMP.F64 D4, D6")
            self.emit(f"    VMRS APSR_nzcv, FPSCR    @ flags VFP -> APSR")
            self.emit(f"    BLE {label_fim}           @ sair se contador <= 0")
            self.emit(f"    VMUL.F64 {dest}, {dest}, D3  @ resultado *= base")
            self.emit(f"    VSUB.F64 D4, D4, D5      @ contador -= 1.0")
            self.emit(f"    B {label_loop}")
            self.emit(f"{label_fim}:")
        else:
            self.emit(f"    @ Operacao desconhecida: {node.op}")

        return dest

    # ==================================================================
    # Carregamento de Operandos — para registradores VFP D
    # ==================================================================

    def _dreg_to_sreg(self, dreg: str) -> str:
        """Retorna o registrador S correspondente ao D (S = D*2).
        D0 -> S0, D1 -> S2, D2 -> S4, etc.
        """
        d_num = int(dreg[1:])
        return f"S{d_num * 2}"

    def _gerar_operand(self, node: ASTNode, dreg: str) -> str:
        """Gera código para carregar um operando em um registrador VFP D (F64)."""
        if isinstance(node, NumberNode):
            if node.is_real:
                # Valor real → armazenar como double no pool de constantes
                const_label = self._add_const(node.value)
                self.emit(f"    LDR R0, ={const_label}")
                self.emit(f"    VLDR.F64 {dreg}, [R0]    @ carregar {node.value} (double)")
            else:
                # Valor inteiro → MOV para R, VMOV para S, VCVT para D
                s_reg = self._dreg_to_sreg(dreg)
                if -256 <= node.value <= 255:
                    self.emit(f"    MOV R0, #{node.value}")
                else:
                    self.emit(f"    LDR R0, ={node.value}")
                self.emit(f"    VMOV {s_reg}, R0               @ int para VFP (via {s_reg})")
                self.emit(f"    VCVT.F64.S32 {dreg}, {s_reg}   @ converter int32 para F64")
            return dreg
        elif isinstance(node, MemReadNode):
            return self._gerar_mem_read(node, dreg)
        elif isinstance(node, BinOpNode):
            resultado = self._gerar_binop(node, dreg)
            return resultado
        return dreg

    # ==================================================================
    # Memória — Load/Store de doubles (8 bytes)
    # ==================================================================

    def _gerar_mem_read(self, node: MemReadNode, dreg: str) -> str:
        """Gera código para ler uma variável de memória (double)."""
        label = self._get_mem_label(node.name)
        self.emit(f"    LDR R0, ={label}")
        self.emit(f"    VLDR.F64 {dreg}, [R0]    @ ler memoria {node.name}")
        return dreg

    def _gerar_mem_write(self, node: MemWriteNode):
        """Gera código para escrever em uma variável de memória (double)."""
        label = self._get_mem_label(node.name)
        dreg_val = self._gerar_operand(node.value, "D0")
        self.emit(f"    LDR R0, ={label}")
        self.emit(f"    VSTR.F64 {dreg_val}, [R0]    @ escrever {node.name}")

    # ==================================================================
    # Comandos Especiais
    # ==================================================================

    def _gerar_res(self, node: ResNode):
        """Gera código para carregar resultado de N statements atrás em D2."""
        idx = len(self.historico_resultados) - node.n
        if idx < 0 or idx >= len(self.historico_resultados):
            self.emit(f"    @ RES({node.n}): fora do historico -> 0.0")
            const_0 = self._add_const(0.0)
            self.emit(f"    LDR R0, ={const_0}")
            self.emit(f"    VLDR.F64 D2, [R0]        @ D2 = 0.0")
        else:
            res_label = self.historico_resultados[idx]
            self.emit(f"    @ RES({node.n}): carregar resultado #{idx+1}")
            self.emit(f"    LDR R0, ={res_label}")
            self.emit(f"    VLDR.F64 D2, [R0]        @ D2 = resultado de {node.n} stmt atras")
        # RES também é um statement que produz resultado
        self._salvar_resultado("D2")


    # ==================================================================
    # Estruturas de Controle — Comparação com VCMP.F64
    # ==================================================================

    def _gerar_if(self, node: IfNode):
        """Gera código para estrutura IF/IFELSE."""
        label_else = self.novo_label("ELSE_")
        label_fim = self.novo_label("FIM_IF_")

        self.emit(f"    @ IF")
        self._gerar_condicao(node.condition, label_else)

        # Bloco then — resultados internos não entram no histórico de CMD_RES
        self.emit(f"    @ [then]")
        old_rastrear = self._rastrear_historico
        self._rastrear_historico = False
        for stmt in node.then_block:
            self._gerar_stmt(stmt)
        self._rastrear_historico = old_rastrear
        self.emit(f"    B {label_fim}")

        # Bloco else (pode ser vazio)
        self.emit(f"{label_else}:")
        if node.else_block:
            self.emit(f"    @ [else]")
            old_rastrear = self._rastrear_historico
            self._rastrear_historico = False
            for stmt in node.else_block:
                self._gerar_stmt(stmt)
            self._rastrear_historico = old_rastrear

        self.emit(f"{label_fim}:")

    def _gerar_while(self, node: WhileNode):
        """Gera código para estrutura WHILE."""
        label_inicio = self.novo_label("LOOP_")
        label_fim = self.novo_label("FIM_LOOP_")

        self.emit(f"    @ WHILE")
        self.emit(f"{label_inicio}:")
        self._gerar_condicao(node.condition, label_fim)

        # Corpo do loop — resultados internos não entram no histórico individualmente
        self.emit(f"    @ [body]")
        old_rastrear = self._rastrear_historico
        self._rastrear_historico = False
        res_antes = self.res_count
        for stmt in node.body:
            self._gerar_stmt(stmt)
        self._rastrear_historico = old_rastrear

        if self.res_count > res_antes:
            self.historico_resultados.append(f"res_{self.res_count}")

        self.emit(f"    B {label_inicio}")
        self.emit(f"{label_fim}:")

    def _gerar_condicao(self, cond: ConditionNode, label_falso: str):
        """Gera código de comparação VFP e branch condicional (IEEE 754)."""
        dreg_l = self._gerar_operand(cond.left, "D0")

        # Salvar D0 se operando direito pode clobber
        needs_save = self._operand_is_complex(cond.right)
        if needs_save:
            self.emit(f"    VPUSH {{D0}}              @ salvar operando esquerdo da condicao")

        dreg_r = self._gerar_operand(cond.right, "D1")

        if needs_save:
            self.emit(f"    VPOP {{D0}}               @ restaurar operando esquerdo da condicao")

        # Comparação VFP double precision
        self.emit(f"    VCMP.F64 {dreg_l}, {dreg_r}")
        self.emit(f"    VMRS APSR_nzcv, FPSCR    @ copiar flags VFP para APSR")

        # Branch para label_falso se condição é FALSA
        branch_falso = {
            ">":  "BLE",
            "<":  "BGE",
            ">=": "BLT",
            "<=": "BGT",
            "==": "BNE",
            "!=": "BEQ",
        }
        inst = branch_falso.get(cond.op, "B")
        self.emit(f"    {inst} {label_falso}        @ pular se NAO({cond.op})")

    # ==================================================================
    # Seção de Dados — variáveis e constantes
    # ==================================================================

    def _get_mem_label(self, name: str) -> str:
        """Retorna o label Assembly para uma variável de memória."""
        if name not in self.mem_map:
            self.mem_map[name] = f"mem_{name}"
        return self.mem_map[name]

    def _gerar_secao_dados(self):
        """Gera a seção .data com variáveis, slots de resultado e constantes."""
        self.emit("@ ============================================")
        self.emit("@ Secao de dados")
        self.emit("@ ============================================")
        self.emit(".data")
        self.emit("")

        # Slots de resultado para RES (cada um 8 bytes = 1 double)
        if self.res_count > 0:
            self.emit("@ --- Slots de resultado para RES (double, 8 bytes) ---")
            for i in range(1, self.res_count + 1):
                self.emit(f".align 3")
                self.emit(f"res_{i}:")
                self.emit(f"    .word 0x00000000  @ double 0.0 (low)")
                self.emit(f"    .word 0x00000000  @ double 0.0 (high) - resultado #{i}")
            self.emit("")

        # Variáveis de memória (inicializadas com 0.0)
        if self.mem_map:
            self.emit("@ --- Variaveis de memoria (double, 8 bytes) ---")
            for name, label in self.mem_map.items():
                self.emit(f".align 3")
                lo, hi = self._double_to_words(0.0)
                self.emit(f"{label}:")
                self.emit(f"    .word 0x{lo:08X}  @ double 0.0 (low)")
                self.emit(f"    .word 0x{hi:08X}  @ double 0.0 (high) - {name}")
            self.emit("")

        # Pool de constantes double
        if self.const_pool:
            self.emit("@ --- Constantes IEEE 754 double ---")
            for label, val in self.const_pool.items():
                lo, hi = self._double_to_words(val)
                self.emit(f".align 3")
                self.emit(f"{label}:")
                self.emit(f"    .word 0x{lo:08X}  @ double {val} (low)")
                self.emit(f"    .word 0x{hi:08X}  @ double {val} (high)")


def gerarAssembly(arvore: ProgramNode) -> str:
    """Gera código Assembly ARMv7 a partir da AST."""
    return AssemblyGenerator().gerar(arvore)
