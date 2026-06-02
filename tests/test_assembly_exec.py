# =============================================================================
# PUC-PR — Linguagens Formais e Compiladores
# Fase 3 — Analisador Semântico
#
# Integrantes:
#   Christopher Gabriel Miranda da Cruz  (GitHub: Miiranda45)
#   Mauricio dos Anjos Souza             (GitHub: anjos-404)
# Nome do grupo no Canvas: [RA2-21]
# =============================================================================
# tests/test_assembly_exec.py — Verificação NUMÉRICA do Assembly gerado.
#
# Alvo: ARMv7-A / VFPv3 (Cpulator ARMv7 DE1-SoC v16.1).
#
# O código gerado é bare-metal (sem I/O), então estes testes EXECUTAM o
# Assembly em um simulador do subconjunto de instruções VFP F64 que o gerador
# emite e conferem os resultados nos slots de memória (res_N / mem_X) contra os
# valores esperados.
#
# Fidelidade ao DE1-SoC (ARMv7-A VFPv3):
#   - registradores VFP D0..D15 de 64 bits; S aliasa D (S_{2n}=low, S_{2n+1}=high);
#   - aritmética IEEE-754 binary64 (double) com round-to-nearest — igual ao
#     `float` do Python;
#   - VCVT.S32.F64 (forma sem 'R') converte double->int32 com arredondamento
#     TOWARD-ZERO (truncamento) — base da divisão inteira e do resto;
#   - VCMP.F64 + VMRS APSR_nzcv,FPSCR + branch condicional (BLE/BGE/BLT/BGT/
#     BNE/BEQ) — comparação ordenada de doubles.
#
# Roda com:  python -m unittest tests.test_assembly_exec   (e também via pytest)

import os
import sys
import struct
import math
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic import (
    prepararEntradaSemantica, construirTabelaSimbolos,
    verificarTipos, gerarArvoreAtribuida,
)
from codegen.assembly_gen import gerarAssembly


# ---------------------------------------------------------------------------
# Simulador do subconjunto VFP F64 (ARMv7-A / VFPv3)
# ---------------------------------------------------------------------------
def _regnum(tok: str) -> int:
    return int(tok.strip().strip(",").lstrip("DSRdsr"))


class SimuladorVFP:
    """Executa o subconjunto de instruções ARMv7 VFP F64 que o gerador emite."""

    def __init__(self):
        self.S = [0] * 64          # palavras de 32 bits (S aliasa D)
        self.R = {}                # R0..R3 (inteiro ou label/endereço simbólico)
        self.stack = []            # pilha VFP (VPUSH/VPOP)
        self.cmp = (0.0, 0.0)      # último VCMP.F64 (a, b)
        self.mem = {}              # label -> double

    # D_n  <->  par de palavras S (little-endian, como na DE1-SoC)
    def getD(self, n: int) -> float:
        b = struct.pack("<I", self.S[2 * n] & 0xFFFFFFFF) + \
            struct.pack("<I", self.S[2 * n + 1] & 0xFFFFFFFF)
        return struct.unpack("<d", b)[0]

    def setD(self, n: int, x: float):
        b = struct.pack("<d", x)
        self.S[2 * n]     = struct.unpack("<I", b[0:4])[0]
        self.S[2 * n + 1] = struct.unpack("<I", b[4:8])[0]

    def getSint(self, n: int) -> int:
        v = self.S[n] & 0xFFFFFFFF
        return v - 0x100000000 if v >= 0x80000000 else v   # int32 com sinal

    def setSint(self, n: int, i: int):
        self.S[n] = i & 0xFFFFFFFF


def montar(asm: str):
    """Separa o Assembly em código (.text) e memória (.data)."""
    code, labels, mem_words = [], {}, {}
    section, cur = "text", None
    for raw in asm.split("\n"):
        line = raw.split("@", 1)[0].strip()
        if not line:
            continue
        if line.startswith((".global", ".ltorg", ".align")):
            continue
        if line == ".text":
            section = "text"; continue
        if line == ".data":
            section = "data"; continue
        if line.endswith(":"):
            lab = line[:-1].strip()
            if section == "text":
                labels[lab] = len(code)
            else:
                cur = lab; mem_words[lab] = []
            continue
        if section == "data":
            if line.startswith(".word"):
                mem_words[cur].append(int(line.split()[1], 16))
            continue
        partes = line.split(None, 1)
        code.append((partes[0], partes[1] if len(partes) > 1 else ""))
    mem = {}
    for lab, words in mem_words.items():
        if len(words) >= 2:
            b = struct.pack("<I", words[0]) + struct.pack("<I", words[1])
            mem[lab] = struct.unpack("<d", b)[0]
        else:
            mem[lab] = 0.0
    return code, labels, mem


def executar(asm: str, max_passos: int = 500000) -> dict:
    """Executa o Assembly e devolve o estado final da memória (label -> double)."""
    code, labels, mem = montar(asm)
    v = SimuladorVFP(); v.mem = mem
    pc = labels["_start"]
    passos = 0
    while pc < len(code):
        passos += 1
        if passos > max_passos:
            raise RuntimeError("limite de passos excedido (possível loop infinito)")
        mnem, args = code[pc]
        pc += 1
        a = [x.strip() for x in args.split(",")] if args else []

        if mnem == "MOV":                          # MOV Rd, #imm
            v.R[_regnum(a[0])] = int(a[1].strip().lstrip("#"))
        elif mnem == "LDR":                        # LDR Rd, =label  |  LDR Rd, =int
            alvo = a[1].strip().lstrip("=")
            v.R[_regnum(a[0])] = int(alvo) if alvo.lstrip("-").isdigit() else alvo
        elif mnem == "VLDR.F64":                   # VLDR.F64 Dd, [Rn]
            v.setD(_regnum(a[0]), v.mem.get(v.R[_regnum(a[1].strip("[]"))], 0.0))
        elif mnem == "VSTR.F64":                   # VSTR.F64 Dd, [Rn]
            v.mem[v.R[_regnum(a[1].strip("[]"))]] = v.getD(_regnum(a[0]))
        elif mnem == "VMOV.F64":                   # VMOV.F64 Dd, Dm
            v.setD(_regnum(a[0]), v.getD(_regnum(a[1])))
        elif mnem == "VMOV":                       # VMOV Sn, Rm  (bits inteiros)
            v.S[_regnum(a[0])] = v.R[_regnum(a[1])] & 0xFFFFFFFF
        elif mnem == "VADD.F64":
            v.setD(_regnum(a[0]), v.getD(_regnum(a[1])) + v.getD(_regnum(a[2])))
        elif mnem == "VSUB.F64":
            v.setD(_regnum(a[0]), v.getD(_regnum(a[1])) - v.getD(_regnum(a[2])))
        elif mnem == "VMUL.F64":
            v.setD(_regnum(a[0]), v.getD(_regnum(a[1])) * v.getD(_regnum(a[2])))
        elif mnem == "VDIV.F64":
            v.setD(_regnum(a[0]), v.getD(_regnum(a[1])) / v.getD(_regnum(a[2])))
        elif mnem == "VCVT.S32.F64":               # Sd <- trunc(Dm)  (toward zero)
            v.setSint(_regnum(a[0]), math.trunc(v.getD(_regnum(a[1]))))
        elif mnem == "VCVT.F64.S32":               # Dd <- (double) Sm
            v.setD(_regnum(a[0]), float(v.getSint(_regnum(a[1]))))
        elif mnem == "VCMP.F64":                   # compara doubles (ordenado)
            v.cmp = (v.getD(_regnum(a[0])), v.getD(_regnum(a[1])))
        elif mnem == "VMRS":                        # flags já capturadas no VCMP
            pass
        elif mnem == "VPUSH":
            v.stack.append(v.getD(_regnum(args.strip("{} "))))
        elif mnem == "VPOP":
            v.setD(_regnum(args.strip("{} ")), v.stack.pop())
        elif mnem == "B":
            if args.strip() == "_halt":
                break                               # halt bare-metal
            pc = labels[args.strip()]
        elif mnem in ("BLE", "BGE", "BLT", "BGT", "BNE", "BEQ"):
            x, y = v.cmp
            tomar = {"BLE": x <= y, "BGE": x >= y, "BLT": x < y,
                     "BGT": x > y, "BNE": x != y, "BEQ": x == y}[mnem]
            if tomar:
                pc = labels[args.strip()]
        else:
            raise RuntimeError(f"instrução não suportada pelo simulador: {mnem} {args}")
    return v.mem


# ---------------------------------------------------------------------------
# Ponte: programa-fonte -> Assembly (pipeline completo da Fase 3)
# ---------------------------------------------------------------------------
def compilar_para_asm(src: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False,
                                    encoding="utf-8")
    f.write(src); f.close()
    try:
        ent = prepararEntradaSemantica(f.name)
        assert ent.ok, f"entrada inválida: {ent.erros}"
        tab, e1 = construirTabelaSimbolos(ent.arvore)
        tipos, e2 = verificarTipos(ent.arvore, tab)
        assert not (e1 + e2), f"erros semânticos: {[str(e) for e in e1 + e2]}"
        arv = gerarArvoreAtribuida(ent.arvore, tab, tipos)
        return gerarAssembly(arv.programa)
    finally:
        os.unlink(f.name)


def _prog(corpo: str) -> str:
    return "START\n" + corpo + "\nEND\n"


def _exec_slot(corpo: str, slot: str) -> float:
    """Compila, executa e retorna o valor do slot de memória pedido."""
    return executar(compilar_para_asm(_prog(corpo)))[slot]


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------
class TestAssemblyAritmetica(unittest.TestCase):
    CASOS = [
        # (descrição, corpo, slot, esperado)
        ("soma int",          "(EXPR 10 5 +)",  "res_1", 15),
        ("subtracao int",     "(EXPR 20 8 -)",  "res_1", 12),
        ("multiplicacao int", "(EXPR 6 7 *)",   "res_1", 42),
        ("soma real",         "(EXPR 1.5 2.5 +)", "res_1", 4.0),
        ("sub real",          "(EXPR 2.0 0.5 -)", "res_1", 1.5),
        ("mul real",          "(EXPR 1.5 2.0 *)", "res_1", 3.0),
        ("mista soma 10+2.5", "(EXPR 10 2.5 +)", "res_1", 12.5),
        ("mista mul 3*1.5",   "(EXPR 3 1.5 *)",  "res_1", 4.5),
    ]

    def test_operadores_basicos(self):
        for desc, corpo, slot, esp in self.CASOS:
            with self.subTest(caso=desc):
                self.assertAlmostEqual(_exec_slot(corpo, slot), esp, places=9)


class TestAssemblyDivisaoResto(unittest.TestCase):
    def test_divisao_inteira_trunca_para_zero(self):
        for corpo, esp in [("(EXPR 20 4 /)", 5), ("(EXPR 17 5 /)", 3),
                           ("(EXPR 7 2 /)", 3), ("(EXPR 99 10 /)", 9)]:
            with self.subTest(caso=corpo):
                self.assertAlmostEqual(_exec_slot(corpo, "res_1"), esp, places=9)

    def test_resto(self):
        for corpo, esp in [("(EXPR 17 5 %)", 2), ("(EXPR 20 6 %)", 2),
                           ("(EXPR 10 3 %)", 1)]:
            with self.subTest(caso=corpo):
                self.assertAlmostEqual(_exec_slot(corpo, "res_1"), esp, places=9)

    def test_divisao_real(self):
        for corpo, esp in [("(EXPR 7.5 2.5 |)", 3.0), ("(EXPR 10.0 4.0 |)", 2.5),
                           ("(EXPR 17 5 |)", 3.4)]:
            with self.subTest(caso=corpo):
                self.assertAlmostEqual(_exec_slot(corpo, "res_1"), esp, places=9)


class TestAssemblyPotencia(unittest.TestCase):
    def test_potencia(self):
        for corpo, esp in [("(EXPR 2 5 ^)", 32), ("(EXPR 3 0 ^)", 1),
                           ("(EXPR 5 1 ^)", 5), ("(EXPR 10 3 ^)", 1000),
                           ("(EXPR 1.5 2 ^)", 2.25)]:
            with self.subTest(caso=corpo):
                self.assertAlmostEqual(_exec_slot(corpo, "res_1"), esp, places=9)


class TestAssemblyAninhamento(unittest.TestCase):
    def test_expressoes_aninhadas(self):
        # exercita também o caminho VPUSH/VPOP (operando direito complexo)
        self.assertAlmostEqual(
            _exec_slot("(EXPR (EXPR 3 2 +) (EXPR 4 5 *) +)", "res_1"), 25, places=9)
        self.assertAlmostEqual(
            _exec_slot("(EXPR (EXPR (EXPR 2 3 +) 4 *) 2 ^)", "res_1"), 400, places=9)


class TestAssemblyMemoria(unittest.TestCase):
    def test_store_int(self):
        self.assertAlmostEqual(_exec_slot("(CMD_STORE 123 X)", "mem_X"), 123, places=9)

    def test_store_real(self):
        self.assertAlmostEqual(_exec_slot("(CMD_STORE 3.14 PI)", "mem_PI"), 3.14, places=9)

    def test_load_em_expressao(self):
        # store=res_1; (X+1)=res_2 lendo a memória
        self.assertAlmostEqual(
            _exec_slot("(CMD_STORE 100 X)(EXPR X 1 +)", "res_2"), 101, places=9)

    def test_res(self):
        self.assertAlmostEqual(
            _exec_slot("(EXPR 7 3 +)(CMD_RES 1)", "res_2"), 10, places=9)


class TestAssemblyRelacionais(unittest.TestCase):
    # mem_T = 1 se o ramo "then" foi tomado; 0 se "else" (X vale 5)
    CASOS = [
        ("> verdadeiro", "(X 3 >)", 1), ("> falso", "(X 9 >)", 0),
        ("< verdadeiro", "(X 9 <)", 1), ("< falso", "(X 3 <)", 0),
        (">= igual",     "(X 5 >=)", 1), (">= falso", "(X 6 >=)", 0),
        ("<= igual",     "(X 5 <=)", 1), ("<= falso", "(X 4 <=)", 0),
        ("== verdadeiro","(X 5 ==)", 1), ("== falso", "(X 4 ==)", 0),
        ("!= verdadeiro","(X 4 !=)", 1), ("!= falso", "(X 5 !=)", 0),
    ]

    def test_todos_os_relacionais(self):
        for desc, cond, esp in self.CASOS:
            corpo = (f"(CMD_STORE 5 X)(IFELSE {cond} "
                     f"[(CMD_STORE 1 T)] [(CMD_STORE 0 T)])")
            with self.subTest(caso=desc):
                self.assertAlmostEqual(_exec_slot(corpo, "mem_T"), esp, places=9)


class TestAssemblyWhile(unittest.TestCase):
    def test_contador(self):
        corpo = "(CMD_STORE 0 C)(WHILE (C 3 <) [(CMD_STORE (EXPR C 1 +) C)])"
        self.assertAlmostEqual(_exec_slot(corpo, "mem_C"), 3, places=9)

    def test_somatorio(self):
        corpo = ("(CMD_STORE 0 S)(CMD_STORE 1 N)"
                 "(WHILE (N 3 <=) [(CMD_STORE (EXPR S N +) S)"
                 "(CMD_STORE (EXPR N 1 +) N)])")
        mem = executar(compilar_para_asm(_prog(corpo)))
        self.assertAlmostEqual(mem["mem_S"], 6, places=9)   # 1+2+3
        self.assertAlmostEqual(mem["mem_N"], 4, places=9)


class TestAssemblyArquivosReais(unittest.TestCase):
    """Os arquivos de teste validos devem gerar Assembly que executa ate o halt."""

    def _caminho(self, nome):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), nome)

    def test_teste1_e_teste2_executam(self):
        for nome in ("teste1.txt", "teste2.txt"):
            with self.subTest(arquivo=nome):
                ent = prepararEntradaSemantica(self._caminho(nome))
                self.assertTrue(ent.ok)
                tab, e1 = construirTabelaSimbolos(ent.arvore)
                tipos, e2 = verificarTipos(ent.arvore, tab)
                self.assertEqual(e1 + e2, [])
                arv = gerarArvoreAtribuida(ent.arvore, tab, tipos)
                asm = gerarAssembly(arv.programa)
                # executa por completo sem instrução não suportada nem loop infinito
                mem = executar(asm)
                self.assertIn("res_1", mem)


if __name__ == "__main__":
    unittest.main(verbosity=2)
