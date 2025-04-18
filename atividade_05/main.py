# // GRUPO:
# // - ARTHUR MIRANDA TAVARES
# // - LUCAS FARIAS DE MEDEIROS
# // - MICHAEL DA CUNHA PINHO
# // - RENAN GONDIM DIAS DE ALBUQUERQUE

import os
from typing import List

# Definição das classes de token
class TokenType:
    NUMERO = "Numero"
    PAREN_ESQ = "ParenEsq"
    PAREN_DIR = "ParenDir"
    SOMA = "Soma"
    SUBTRACAO = "Sub"
    MULTIPLICACAO = "Mult"
    DIVISAO = "Div"
    EOF = "EOF"

# Classe do Token
class Token:
    def __init__(self, tipo: str, lexema: str, posicao: int):
        self.tipo = tipo
        self.lexema = lexema
        self.posicao = posicao
    
    def __repr__(self):
        return f"<{self.tipo}, '{self.lexema}', {self.posicao}>"

# Analisador léxico
class Lexer:
    def __init__(self, entrada: str):
        self.entrada = entrada
        self.posicao = 0
        self.tamanho = len(entrada)

    def proximo_token(self) -> Token:
        while self.posicao < self.tamanho:
            char = self.entrada[self.posicao]
            
            if char.isspace():
                self.posicao += 1
                continue
            
            if char.isdigit():
                return self._extrair_numero()
            
            if char == '(': 
                return self._criar_token(TokenType.PAREN_ESQ, "(")
            if char == ')': 
                return self._criar_token(TokenType.PAREN_DIR, ")")
            if char == '+': 
                return self._criar_token(TokenType.SOMA, "+")
            if char == '-': 
                return self._criar_token(TokenType.SUBTRACAO, "-")
            if char == '*': 
                return self._criar_token(TokenType.MULTIPLICACAO, "*")
            if char == '/': 
                return self._criar_token(TokenType.DIVISAO, "/")
            
            raise ValueError(f"Erro léxico: caractere inesperado '{char}' na posição {self.posicao}")
        
        return Token(TokenType.EOF, "", self.posicao)
    
    def _extrair_numero(self) -> Token:
        inicio = self.posicao
        while self.posicao < self.tamanho and self.entrada[self.posicao].isdigit():
            self.posicao += 1
        lexema = self.entrada[inicio:self.posicao]
        return Token(TokenType.NUMERO, lexema, inicio)
    
    def _criar_token(self, tipo: str, lexema: str) -> Token:
        token = Token(tipo, lexema, self.posicao)
        self.posicao += 1
        return token
    
    def todos_tokens(self) -> List[Token]:
        tokens = []
        while True:
            token = self.proximo_token()
            tokens.append(token)
            if token.tipo == TokenType.EOF:
                break
        return tokens

# Representação da árvore sintática
class Expressao:
    def avaliar(self):
        raise NotImplementedError()

class Numero(Expressao):
    def __init__(self, valor: int):
        self.valor = valor

    def avaliar(self):
        return self.valor

    def __repr__(self):
        return str(self.valor)

class OperacaoBinaria(Expressao):
    def __init__(self, operador: str, esquerda: Expressao, direita: Expressao):
        self.operador = operador
        self.esquerda = esquerda
        self.direita = direita
    
    def avaliar(self):
        esq = self.esquerda.avaliar()
        dir = self.direita.avaliar()
        if self.operador == '+':
            return esq + dir
        elif self.operador == '-':
            return esq - dir
        elif self.operador == '*':
            return esq * dir
        elif self.operador == '/':
            if dir == 0:
                raise ZeroDivisionError("Erro: Segundo operando da divisão é zero.")
            return esq / dir

    def __repr__(self):
        return f"({self.operador} {self.esquerda} {self.direita})"

# Implementação do Parser
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicao = 0

    def _token_atual(self) -> Token:
        return self.tokens[self.posicao]
    
    def _consumir(self) -> Token:
        token = self.tokens[self.posicao]
        self.posicao += 1
        return token
    
    def analisar_expressao(self) -> Expressao:
        expressao = self._analisar_expressao()
        if self._token_atual().tipo != TokenType.EOF:
            raise SyntaxError("Erro: Tokens extras ao final da expressão.")
        return expressao
    
    def _analisar_expressao(self) -> Expressao:
        token = self._token_atual()
        if token.tipo == TokenType.NUMERO:
            self._consumir()
            return Numero(int(token.lexema))
        elif token.tipo == TokenType.PAREN_ESQ:
            self._consumir()
            esquerda = self._analisar_expressao()
            operador = self._token_atual()
            if operador.tipo not in {TokenType.SOMA, TokenType.SUBTRACAO, TokenType.MULTIPLICACAO, TokenType.DIVISAO}:
                raise SyntaxError(f"Erro: Operador ou parêntese direito esperado, mas encontrado {operador.tipo}.")
            self._consumir()
            if self._token_atual().tipo == TokenType.PAREN_DIR:
                raise SyntaxError(f"Erro: Segundo operando da {operador.lexema} está faltando.")
            direita = self._analisar_expressao()
            if self._token_atual().tipo != TokenType.PAREN_DIR:
                raise SyntaxError("Erro: Parêntese direito esperado.")
            self._consumir()
            return OperacaoBinaria(operador.lexema, esquerda, direita)
        else:
            raise SyntaxError(f"Erro: Token inesperado: {token.lexema}")

def processar_expressao(expressao: str):
    lexer = Lexer(expressao)
    tokens = lexer.todos_tokens()
    parser = Parser(tokens)
    arvore = parser.analisar_expressao()
    return arvore


def imprimir_arvore(no, prefixo="", is_left=True):
    if isinstance(no, OperacaoBinaria):
        imprimir_arvore(no.direita, prefixo + ("│   " if is_left else "    "), False)
        print(prefixo + ("├── " if is_left else "└── ") + no.operador)
        imprimir_arvore(no.esquerda, prefixo + ("│   " if is_left else "    "), True)
    elif isinstance(no, Numero):
        print(prefixo + ("├── " if is_left else "└── ") + str(no.valor))
        
def executar_testes(diretorio):
    for arquivo in sorted(os.listdir(diretorio)):
        caminho = os.path.join(diretorio, arquivo)
        with open(caminho, 'r') as f:
            expressao = f.read().strip()
        print(f"Expressão de entrada ({arquivo}): {expressao}")
        try:
            resultado = processar_expressao(expressao)
            avaliacao = resultado.avaliar()
            print("\nÁrvore Sintática:")
            imprimir_arvore(resultado)
            print("\nResultado da avaliação:", avaliacao)
        except Exception as e:
            print("Erro:", e)
        print("=" * 40)

if __name__ == "__main__":
    print("=== TESTES VÁLIDOS ===")
    executar_testes("valid_tests")
    print("=== TESTES INVÁLIDOS ===")
    executar_testes("invalid_tests")
