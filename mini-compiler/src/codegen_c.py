from ast_nodes import *

class CCodeGenerator:
    def __init__(self):
        self.indent = 0
        self.output = []

    def emit(self, text: str):
        self.output.append('    ' * self.indent + text)

    def generate(self, node: ASTNode) -> str:
        method = f'gen_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_gen)
        return visitor(node)

    def generic_gen(self, node: ASTNode):
        return ''

    def gen_Program(self, node: Program) -> str:
        self.emit('#include <stdio.h>')
        self.emit('#include <stdbool.h>')
        self.emit('')
        for decl in node.declarations:
            self.generate(decl)
        return '\n'.join(self.output)

    def gen_VarDecl(self, node: VarDecl):
        if node.array_size:
            line = f'{node.var_type} {node.name}[{node.array_size}];'
        elif node.init:
            init = self.gen_expr(node.init)
            line = f'{node.var_type} {node.name} = {init};'
        else:
            line = f'{node.var_type} {node.name};'
        self.emit(line)

    def gen_FuncDecl(self, node: FuncDecl):
        params = ', '.join([f'{p.var_type} {p.name}' for p in node.params])
        self.emit(f'{node.return_type} {node.name}({params}) {{')
        self.indent += 1
        for stmt in node.body.statements:
            self.generate(stmt)
        self.indent -= 1
        self.emit('}')
        self.emit('')

    def gen_Block(self, node: Block):
        self.emit('{')
        self.indent += 1
        for stmt in node.statements:
            self.generate(stmt)
        self.indent -= 1
        self.emit('}')

    def gen_IfStmt(self, node: IfStmt):
        cond = self.gen_expr(node.condition)
        self.emit(f'if ({cond}) {{')
        self.indent += 1
        self.generate(node.then_branch)
        self.indent -= 1
        if node.else_branch:
            self.emit('} else {')
            self.indent += 1
            self.generate(node.else_branch)
            self.indent -= 1
        self.emit('}')

    def gen_WhileStmt(self, node: WhileStmt):
        cond = self.gen_expr(node.condition)
        self.emit(f'while ({cond}) {{')
        self.indent += 1
        self.generate(node.body)
        self.indent -= 1
        self.emit('}')

    def gen_ReturnStmt(self, node: ReturnStmt):
        if node.value:
            val = self.gen_expr(node.value)
            self.emit(f'return {val};')
        else:
            self.emit('return;')

    def gen_BreakStmt(self, node: BreakStmt):
        self.emit('break;')

    def gen_ContinueStmt(self, node: ContinueStmt):
        self.emit('continue;')

    def gen_ExprStmt(self, node: ExprStmt):
        expr = self.gen_expr(node.expr)
        self.emit(f'{expr};')

    def gen_expr(self, node: ASTNode) -> str:
        method = f'expr_{type(node).__name__}'
        visitor = getattr(self, method, lambda n: '')
        return visitor(node)

    def expr_BinaryExpr(self, node: BinaryExpr) -> str:
        left = self.gen_expr(node.left)
        right = self.gen_expr(node.right)
        return f'({left} {node.op} {right})'

    def expr_UnaryExpr(self, node: UnaryExpr) -> str:
        operand = self.gen_expr(node.operand)
        return f'({node.op}{operand})'

    def expr_AssignExpr(self, node: AssignExpr) -> str:
        target = self.gen_expr(node.target)
        val = self.gen_expr(node.value)
        return f'{target} = {val}'

    def expr_CallExpr(self, node: CallExpr) -> str:
        args = ', '.join([self.gen_expr(a) for a in node.args])
        return f'{node.callee}({args})'

    def expr_ArrayAccess(self, node: ArrayAccess) -> str:
        idx = self.gen_expr(node.index)
        return f'{node.array}[{idx}]'

    def expr_Identifier(self, node: Identifier) -> str:
        return node.name

    def expr_IntLiteral(self, node: IntLiteral) -> str:
        return str(node.value)

    def expr_FloatLiteral(self, node: FloatLiteral) -> str:
        return str(node.value)

    def expr_BoolLiteral(self, node: BoolLiteral) -> str:
        return '1' if node.value else '0'
