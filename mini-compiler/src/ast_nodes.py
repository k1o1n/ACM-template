from dataclasses import dataclass, field
from typing import List, Optional, Any
import json

class ASTNode:
    def to_dict(self) -> dict:
        raise NotImplementedError

@dataclass
class Program(ASTNode):
    declarations: List[ASTNode]
    def to_dict(self):
        return {"type": "Program", "declarations": [d.to_dict() for d in self.declarations]}

@dataclass
class VarDecl(ASTNode):
    var_type: str
    name: str
    array_size: Optional[int] = None
    init: Optional[ASTNode] = None
    def to_dict(self):
        return {"type": "VarDecl", "var_type": self.var_type, "name": self.name, 
                "array_size": self.array_size, "init": self.init.to_dict() if self.init else None}

@dataclass
class FuncDecl(ASTNode):
    return_type: str
    name: str
    params: List['VarDecl']
    body: 'Block'
    def to_dict(self):
        return {"type": "FuncDecl", "return_type": self.return_type, "name": self.name,
                "params": [p.to_dict() for p in self.params], "body": self.body.to_dict()}

@dataclass
class Block(ASTNode):
    statements: List[ASTNode]
    def to_dict(self):
        return {"type": "Block", "statements": [s.to_dict() for s in self.statements]}

@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode] = None
    def to_dict(self):
        return {"type": "IfStmt", "condition": self.condition.to_dict(),
                "then_branch": self.then_branch.to_dict(),
                "else_branch": self.else_branch.to_dict() if self.else_branch else None}

@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: ASTNode
    def to_dict(self):
        return {"type": "WhileStmt", "condition": self.condition.to_dict(), "body": self.body.to_dict()}

@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode] = None
    def to_dict(self):
        return {"type": "ReturnStmt", "value": self.value.to_dict() if self.value else None}

@dataclass
class BreakStmt(ASTNode):
    def to_dict(self):
        return {"type": "BreakStmt"}

@dataclass
class ContinueStmt(ASTNode):
    def to_dict(self):
        return {"type": "ContinueStmt"}

@dataclass
class ExprStmt(ASTNode):
    expr: ASTNode
    def to_dict(self):
        return {"type": "ExprStmt", "expr": self.expr.to_dict()}

@dataclass
class BinaryExpr(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode
    def to_dict(self):
        return {"type": "BinaryExpr", "left": self.left.to_dict(), "op": self.op, "right": self.right.to_dict()}

@dataclass
class UnaryExpr(ASTNode):
    op: str
    operand: ASTNode
    def to_dict(self):
        return {"type": "UnaryExpr", "op": self.op, "operand": self.operand.to_dict()}

@dataclass
class AssignExpr(ASTNode):
    target: ASTNode
    value: ASTNode
    def to_dict(self):
        return {"type": "AssignExpr", "target": self.target.to_dict(), "value": self.value.to_dict()}

@dataclass
class CallExpr(ASTNode):
    callee: str
    args: List[ASTNode]
    def to_dict(self):
        return {"type": "CallExpr", "callee": self.callee, "args": [a.to_dict() for a in self.args]}

@dataclass
class ArrayAccess(ASTNode):
    array: str
    index: ASTNode
    def to_dict(self):
        return {"type": "ArrayAccess", "array": self.array, "index": self.index.to_dict()}

@dataclass
class Identifier(ASTNode):
    name: str
    def to_dict(self):
        return {"type": "Identifier", "name": self.name}

@dataclass
class IntLiteral(ASTNode):
    value: int
    def to_dict(self):
        return {"type": "IntLiteral", "value": self.value}

@dataclass
class FloatLiteral(ASTNode):
    value: float
    def to_dict(self):
        return {"type": "FloatLiteral", "value": self.value}

@dataclass
class BoolLiteral(ASTNode):
    value: bool
    def to_dict(self):
        return {"type": "BoolLiteral", "value": self.value}

def ast_to_json(node: ASTNode) -> str:
    return json.dumps(node.to_dict(), indent=2)
