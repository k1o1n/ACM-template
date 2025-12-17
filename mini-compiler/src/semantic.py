from ast_nodes import *
from symbol_table import SymbolTable, Symbol

class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.current_function = None
        self.loop_depth = 0

    def analyze(self, node: ASTNode):
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        pass

    def visit_Program(self, node: Program):
        for decl in node.declarations:
            self.analyze(decl)

    def visit_VarDecl(self, node: VarDecl):
        self.symtab.define(node.name, node.var_type, node.array_size is not None, node.array_size or 0)
        if node.init:
            self.analyze(node.init)

    def visit_FuncDecl(self, node: FuncDecl):
        params = []
        for p in node.params:
            params.append(Symbol(p.name, p.var_type, self.symtab.level + 1))
        self.symtab.define(node.name, node.return_type, is_function=True, params=params)
        self.symtab.enter_scope()
        self.current_function = node.name
        for p in node.params:
            self.symtab.define(p.name, p.var_type)
        self.analyze(node.body)
        self.current_function = None
        self.symtab.exit_scope()

    def visit_Block(self, node: Block):
        self.symtab.enter_scope()
        for stmt in node.statements:
            self.analyze(stmt)
        self.symtab.exit_scope()

    def visit_IfStmt(self, node: IfStmt):
        self.analyze(node.condition)
        self.analyze(node.then_branch)
        if node.else_branch:
            self.analyze(node.else_branch)

    def visit_WhileStmt(self, node: WhileStmt):
        self.analyze(node.condition)
        self.loop_depth += 1
        self.analyze(node.body)
        self.loop_depth -= 1

    def visit_ReturnStmt(self, node: ReturnStmt):
        if node.value:
            self.analyze(node.value)

    def visit_BreakStmt(self, node: BreakStmt):
        if self.loop_depth == 0:
            self.errors.append("'break' outside loop")

    def visit_ContinueStmt(self, node: ContinueStmt):
        if self.loop_depth == 0:
            self.errors.append("'continue' outside loop")

    def visit_ExprStmt(self, node: ExprStmt):
        self.analyze(node.expr)

    def visit_BinaryExpr(self, node: BinaryExpr):
        self.analyze(node.left)
        self.analyze(node.right)

    def visit_UnaryExpr(self, node: UnaryExpr):
        self.analyze(node.operand)

    def visit_AssignExpr(self, node: AssignExpr):
        self.analyze(node.target)
        self.analyze(node.value)

    def visit_CallExpr(self, node: CallExpr):
        sym = self.symtab.lookup(node.callee)
        if not sym:
            self.errors.append(f"Undefined function '{node.callee}'")
        elif not sym.is_function:
            self.errors.append(f"'{node.callee}' is not a function")
        elif len(node.args) != len(sym.params):
            self.errors.append(f"Function '{node.callee}' expects {len(sym.params)} args, got {len(node.args)}")
        for arg in node.args:
            self.analyze(arg)

    def visit_ArrayAccess(self, node: ArrayAccess):
        sym = self.symtab.lookup(node.array)
        if not sym:
            self.errors.append(f"Undefined array '{node.array}'")
        elif not sym.is_array:
            self.errors.append(f"'{node.array}' is not an array")
        self.analyze(node.index)

    def visit_Identifier(self, node: Identifier):
        if not self.symtab.lookup(node.name):
            self.errors.append(f"Undefined variable '{node.name}'")

    def visit_IntLiteral(self, node: IntLiteral):
        pass

    def visit_FloatLiteral(self, node: FloatLiteral):
        pass

    def visit_BoolLiteral(self, node: BoolLiteral):
        pass
