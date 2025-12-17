from typing import List, Optional
from lexer import Token, TokenType
from ast_nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def peek(self, offset=0) -> Token:
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        token = self.current()
        self.pos += 1
        return token

    def match(self, *types: TokenType) -> bool:
        return self.current().type in types

    def consume(self, token_type: TokenType, msg: str) -> Token:
        if self.current().type == token_type:
            return self.advance()
        raise SyntaxError(f"{msg} at line {self.current().line}")

    def parse(self) -> Program:
        declarations = []
        while not self.match(TokenType.EOF):
            declarations.append(self.declaration())
        return Program(declarations)

    def declaration(self) -> ASTNode:
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.BOOL):
            return self.var_or_func_decl()
        return self.statement()

    def var_or_func_decl(self) -> ASTNode:
        type_token = self.advance()
        var_type = type_token.value
        name = self.consume(TokenType.IDENTIFIER, "Expected identifier").value
        
        if self.match(TokenType.LPAREN):
            return self.func_decl(var_type, name)
        
        array_size = None
        if self.match(TokenType.LBRACKET):
            self.advance()
            array_size = int(self.consume(TokenType.INT_LITERAL, "Expected array size").value)
            self.consume(TokenType.RBRACKET, "Expected ']'")

        init = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            init = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return VarDecl(var_type, name, array_size, init)

    def func_decl(self, return_type: str, name: str) -> FuncDecl:
        self.consume(TokenType.LPAREN, "Expected '('")
        params = []
        if not self.match(TokenType.RPAREN):
            params = self.param_list()
        self.consume(TokenType.RPAREN, "Expected ')'")
        body = self.block()
        return FuncDecl(return_type, name, params, body)

    def param_list(self) -> List[VarDecl]:
        params = [self.param()]
        while self.match(TokenType.COMMA):
            self.advance()
            params.append(self.param())
        return params

    def param(self) -> VarDecl:
        type_token = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
        return VarDecl(type_token.value, name)

    def block(self) -> Block:
        self.consume(TokenType.LBRACE, "Expected '{'")
        stmts = []
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.declaration())
        self.consume(TokenType.RBRACE, "Expected '}'")
        return Block(stmts)

    def statement(self) -> ASTNode:
        if self.match(TokenType.IF):
            return self.if_stmt()
        if self.match(TokenType.WHILE):
            return self.while_stmt()
        if self.match(TokenType.RETURN):
            return self.return_stmt()
        if self.match(TokenType.BREAK):
            self.advance()
            self.consume(TokenType.SEMICOLON, "Expected ';'")
            return BreakStmt()
        if self.match(TokenType.CONTINUE):
            self.advance()
            self.consume(TokenType.SEMICOLON, "Expected ';'")
            return ContinueStmt()
        if self.match(TokenType.LBRACE):
            return self.block()
        return self.expr_stmt()

    def if_stmt(self) -> IfStmt:
        self.consume(TokenType.IF, "Expected 'if'")
        self.consume(TokenType.LPAREN, "Expected '('")
        cond = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')'")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_branch = self.statement()
        return IfStmt(cond, then_branch, else_branch)

    def while_stmt(self) -> WhileStmt:
        self.consume(TokenType.WHILE, "Expected 'while'")
        self.consume(TokenType.LPAREN, "Expected '('")
        cond = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')'")
        body = self.statement()
        return WhileStmt(cond, body)

    def return_stmt(self) -> ReturnStmt:
        self.consume(TokenType.RETURN, "Expected 'return'")
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return ReturnStmt(value)

    def expr_stmt(self) -> ExprStmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return ExprStmt(expr)

    def expression(self) -> ASTNode:
        return self.assignment()

    def assignment(self) -> ASTNode:
        expr = self.or_expr()
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.assignment()
            return AssignExpr(expr, value)
        return expr

    def or_expr(self) -> ASTNode:
        left = self.and_expr()
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.and_expr()
            left = BinaryExpr(left, op, right)
        return left

    def and_expr(self) -> ASTNode:
        left = self.equality()
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.equality()
            left = BinaryExpr(left, op, right)
        return left

    def equality(self) -> ASTNode:
        left = self.comparison()
        while self.match(TokenType.EQ, TokenType.NE):
            op = self.advance().value
            right = self.comparison()
            left = BinaryExpr(left, op, right)
        return left

    def comparison(self) -> ASTNode:
        left = self.additive()
        while self.match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.advance().value
            right = self.additive()
            left = BinaryExpr(left, op, right)
        return left

    def additive(self) -> ASTNode:
        left = self.multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.multiplicative()
            left = BinaryExpr(left, op, right)
        return left

    def multiplicative(self) -> ASTNode:
        left = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance().value
            right = self.unary()
            left = BinaryExpr(left, op, right)
        return left

    def unary(self) -> ASTNode:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance().value
            operand = self.unary()
            return UnaryExpr(op, operand)
        return self.primary()

    def primary(self) -> ASTNode:
        if self.match(TokenType.INT_LITERAL):
            return IntLiteral(int(self.advance().value))
        if self.match(TokenType.FLOAT_LITERAL):
            return FloatLiteral(float(self.advance().value))
        if self.match(TokenType.TRUE):
            self.advance()
            return BoolLiteral(True)
        if self.match(TokenType.FALSE):
            self.advance()
            return BoolLiteral(False)
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            if self.match(TokenType.LPAREN):
                return self.call_expr(name)
            if self.match(TokenType.LBRACKET):
                self.advance()
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Expected ']'")
                return ArrayAccess(name, index)
            return Identifier(name)
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')'")
            return expr
        raise SyntaxError(f"Unexpected token at line {self.current().line}")

    def call_expr(self, callee: str) -> CallExpr:
        self.consume(TokenType.LPAREN, "Expected '('")
        args = []
        if not self.match(TokenType.RPAREN):
            args.append(self.expression())
            while self.match(TokenType.COMMA):
                self.advance()
                args.append(self.expression())
        self.consume(TokenType.RPAREN, "Expected ')'")
        return CallExpr(callee, args)
