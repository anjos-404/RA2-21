
class CompilerError(Exception):
    """Classe base para todos os erros do compilador RPN."""

    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"Linha {line}: {message}" if line else message)


class LexicalError(CompilerError):
    """Erro léxico — token inválido ou formato de arquivo incorreto."""
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
