# errors/errors.py — Hierarquia de erros do compilador.


class CompilerError(Exception):
    """Classe base para todos os erros do compilador."""

    def __init__(self, message: str, line: int = 0):
        self.line = line
        msg = f"Linha {line}: {message}" if line else message
        super().__init__(msg)


class LexicalError(CompilerError):
    """Erro léxico — caractere ou token inválido."""
    pass


class RPNSyntaxError(CompilerError):
    """Erro sintático — estrutura do programa inválida."""
    pass


class SemanticError(CompilerError):
    """Erro semântico — uso inválido de memória, RES fora do intervalo, etc."""
    pass


class CodeGenError(CompilerError):
    """Erro na geração de código Assembly."""
    pass


class GrammarError(Exception):
    """Erro na definição/construção da gramática."""
    pass
