from ast_nodes import *

class TACGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = []

    def new_temp(self) -> str:
        self.temp_count += 1
        return f't{self.temp_count}'

    def new_label(self) -> str:
        self.label_count += 1
        return f'L{self.label_count}'

    def emit(self, op: str, arg1='', arg2='', result=''):
        self.code.append((op, arg1, arg2, result))

    def generate(self, node: ASTNode) -> str:
        method = f'gen_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_gen)
        return visitor(node)

    def generic_gen(self, node: ASTNode):
        return ''

    def gen_Program(self, node: Program):
        for decl in node.declarations:
            self.generate(decl)
        return self.dump()

    def gen_VarDecl(self, node: VarDecl):
        if node.init:
            val = self.generate(node.init)
            self.emit('=', val, '', node.name)

    def gen_FuncDecl(self, node: FuncDecl):
        self.emit('FUNC', node.name)
        for p in node.params:
            self.emit('PARAM', p.name)
        self.generate(node.body)
        self.emit('ENDFUNC', node.name)

    def gen_Block(self, node: Block):
        for stmt in node.statements:
            self.generate(stmt)

    def gen_IfStmt(self, node: IfStmt):
        cond = self.generate(node.condition)
        else_label = self.new_label()
        end_label = self.new_label()
        self.emit('IFFALSE', cond, '', else_label)
        self.generate(node.then_branch)
        if node.else_branch:
            self.emit('GOTO', '', '', end_label)
        self.emit('LABEL', else_label)
        if node.else_branch:
            self.generate(node.else_branch)
            self.emit('LABEL', end_label)

    def gen_WhileStmt(self, node: WhileStmt):
        start_label = self.new_label()
        end_label = self.new_label()
        self.emit('LABEL', start_label)
        cond = self.generate(node.condition)
        self.emit('IFFALSE', cond, '', end_label)
        self.generate(node.body)
        self.emit('GOTO', '', '', start_label)
        self.emit('LABEL', end_label)

    def gen_ReturnStmt(self, node: ReturnStmt):
        if node.value:
            val = self.generate(node.value)
            self.emit('RETURN', val)
        else:
            self.emit('RETURN')

    def gen_BreakStmt(self, node: BreakStmt):
        self.emit('BREAK')

    def gen_ContinueStmt(self, node: ContinueStmt):
        self.emit('CONTINUE')

    def gen_ExprStmt(self, node: ExprStmt):
        self.generate(node.expr)

    def gen_BinaryExpr(self, node: BinaryExpr) -> str:
        left = self.generate(node.left)
        right = self.generate(node.right)
        result = self.new_temp()
        self.emit(node.op, left, right, result)
        return result

    def gen_UnaryExpr(self, node: UnaryExpr) -> str:
        operand = self.generate(node.operand)
        result = self.new_temp()
        self.emit(f'UNARY{node.op}', operand, '', result)
        return result

    def gen_AssignExpr(self, node: AssignExpr) -> str:
        val = self.generate(node.value)
        if isinstance(node.target, Identifier):
            self.emit('=', val, '', node.target.name)
            return node.target.name
        elif isinstance(node.target, ArrayAccess):
            idx = self.generate(node.target.index)
            self.emit('[]=', val, idx, node.target.array)
            return val
        return val

    def gen_CallExpr(self, node: CallExpr) -> str:
        for arg in node.args:
            val = self.generate(arg)
            self.emit('ARG', val)
        result = self.new_temp()
        self.emit('CALL', node.callee, str(len(node.args)), result)
        return result

    def gen_ArrayAccess(self, node: ArrayAccess) -> str:
        idx = self.generate(node.index)
        result = self.new_temp()
        self.emit('=[]', node.array, idx, result)
        return result

    def gen_Identifier(self, node: Identifier) -> str:
        return node.name

    def gen_IntLiteral(self, node: IntLiteral) -> str:
        return str(node.value)

    def gen_FloatLiteral(self, node: FloatLiteral) -> str:
        return str(node.value)

    def gen_BoolLiteral(self, node: BoolLiteral) -> str:
        return '1' if node.value else '0'

    def dump(self) -> str:
        lines = []
        for op, arg1, arg2, result in self.code:
            if op == 'FUNC':
                lines.append(f'FUNC {arg1}:')
            elif op == 'ENDFUNC':
                lines.append(f'ENDFUNC {arg1}')
            elif op == 'PARAM':
                lines.append(f'  PARAM {arg1}')
            elif op == 'LABEL':
                lines.append(f'{arg1}:')
            elif op == 'GOTO':
                lines.append(f'  GOTO {result}')
            elif op == 'IFFALSE':
                lines.append(f'  IFFALSE {arg1} GOTO {result}')
            elif op == 'RETURN':
                lines.append(f'  RETURN {arg1}' if arg1 else '  RETURN')
            elif op == 'BREAK':
                lines.append(f'  BREAK')
            elif op == 'CONTINUE':
                lines.append(f'  CONTINUE')
            elif op == 'ARG':
                lines.append(f'  ARG {arg1}')
            elif op == 'CALL':
                lines.append(f'  {result} = CALL {arg1}, {arg2}')
            elif op == '=':
                lines.append(f'  {result} = {arg1}')
            elif op == '[]=':
                lines.append(f'  {result}[{arg2}] = {arg1}')
            elif op == '=[]':
                lines.append(f'  {result} = {arg1}[{arg2}]')
            elif op.startswith('UNARY'):
                lines.append(f'  {result} = {op[5:]}{arg1}')
            else:
                lines.append(f'  {result} = {arg1} {op} {arg2}')
        return '\n'.join(lines)
