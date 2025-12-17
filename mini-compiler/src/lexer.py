import re
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

KEYWORDS = {
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'bool': TokenType.BOOL,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'return': TokenType.RETURN,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
}

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def peek(self, offset=0):
        pos = self.pos + offset
        return self.source[pos] if pos < len(self.source) else '\0'

    def advance(self):
        ch = self.peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def skip_whitespace(self):
        while self.peek().isspace():
            self.advance()

    def skip_comment(self):
        if self.peek() == '/' and self.peek(1) == '/':
            while self.peek() != '\n' and self.peek() != '\0':
                self.advance()
            return True
        if self.peek() == '/' and self.peek(1) == '*':
            self.advance()
            self.advance()
            while not (self.peek() == '*' and self.peek(1) == '/'):
                if self.peek() == '\0':
                    break
                self.advance()
            self.advance()
            self.advance()
            return True
        return False

    def read_number(self):
        start_col = self.column
        num = ''
        while self.peek().isdigit():
            num += self.advance()
        if self.peek() == '.' and self.peek(1).isdigit():
            num += self.advance()
            while self.peek().isdigit():
                num += self.advance()
            return Token(TokenType.FLOAT_LITERAL, num, self.line, start_col)
        return Token(TokenType.INT_LITERAL, num, self.line, start_col)

    def read_identifier(self):
        start_col = self.column
        ident = ''
        while self.peek().isalnum() or self.peek() == '_':
            ident += self.advance()
        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, self.line, start_col)

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.skip_comment():
                continue
            if self.pos >= len(self.source):
                break

            ch = self.peek()
            start_col = self.column

            if ch.isdigit():
                self.tokens.append(self.read_number())
            elif ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier())
            elif ch == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', self.line, start_col))
            elif ch == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', self.line, start_col))
            elif ch == '*':
                self.advance()
                self.tokens.append(Token(TokenType.STAR, '*', self.line, start_col))
            elif ch == '/':
                self.advance()
                self.tokens.append(Token(TokenType.SLASH, '/', self.line, start_col))
            elif ch == '%':
                self.advance()
                self.tokens.append(Token(TokenType.PERCENT, '%', self.line, start_col))
            elif ch == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', self.line, start_col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', self.line, start_col))
            elif ch == '!':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, '!=', self.line, start_col))
                else:
                    self.tokens.append(Token(TokenType.NOT, '!', self.line, start_col))
            elif ch == '<':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LE, '<=', self.line, start_col))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', self.line, start_col))
            elif ch == '>':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GE, '>=', self.line, start_col))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', self.line, start_col))
            elif ch == '&' and self.peek(1) == '&':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.AND, '&&', self.line, start_col))
            elif ch == '|' and self.peek(1) == '|':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.OR, '||', self.line, start_col))
            elif ch == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, start_col))
            elif ch == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, start_col))
            elif ch == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', self.line, start_col))
            elif ch == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', self.line, start_col))
            elif ch == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', self.line, start_col))
            elif ch == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', self.line, start_col))
            elif ch == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', self.line, start_col))
            elif ch == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, start_col))
            elif ch == '\0':
                break
            else:
                self.advance()

        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
