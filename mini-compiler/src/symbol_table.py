from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Symbol:
    name: str
    sym_type: str
    scope_level: int
    is_array: bool = False
    array_size: int = 0
    is_function: bool = False
    params: List['Symbol'] = field(default_factory=list)

class SymbolTable:
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.level = 0

    def enter_scope(self):
        self.level += 1
        self.scopes.append({})

    def exit_scope(self):
        if self.level > 0:
            self.scopes.pop()
            self.level -= 1

    def define(self, name: str, sym_type: str, is_array=False, array_size=0, is_function=False, params=None) -> Symbol:
        if name in self.scopes[-1]:
            raise Exception(f"Redefinition of '{name}'")
        sym = Symbol(name, sym_type, self.level, is_array, array_size, is_function, params or [])
        self.scopes[-1][name] = sym
        return sym

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current(self, name: str) -> Optional[Symbol]:
        return self.scopes[-1].get(name)

    def dump(self) -> str:
        lines = []
        for i, scope in enumerate(self.scopes):
            lines.append(f"Scope Level {i}:")
            for name, sym in scope.items():
                if sym.is_function:
                    params = ', '.join([f"{p.sym_type} {p.name}" for p in sym.params])
                    lines.append(f"  {sym.sym_type} {name}({params})")
                elif sym.is_array:
                    lines.append(f"  {sym.sym_type} {name}[{sym.array_size}]")
                else:
                    lines.append(f"  {sym.sym_type} {name}")
        return '\n'.join(lines)
