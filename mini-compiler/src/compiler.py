#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from tac_generator import TACGenerator
from codegen_c import CCodeGenerator
from ast_nodes import ast_to_json

def main():
    if len(sys.argv) < 2:
        print("Usage: compiler.py <source_file> [options]")
        print("Options:")
        print("  -emit-ast      Print AST as JSON")
        print("  -emit-tac      Print Three-Address Code")
        print("  -dump-symtab   Dump symbol table")
        print("  -o <file>      Output file")
        return

    source_file = sys.argv[1]
    options = sys.argv[2:]

    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    if '-emit-ast' in options:
        print(ast_to_json(ast))
        return

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    if '-dump-symtab' in options:
        print(analyzer.symtab.dump())
        return

    if analyzer.errors:
        for err in analyzer.errors:
            print(f"Error: {err}", file=sys.stderr)
        return

    if '-emit-tac' in options:
        tac = TACGenerator()
        print(tac.generate(ast))
        return

    codegen = CCodeGenerator()
    c_code = codegen.generate(ast)

    output_file = None
    for i, opt in enumerate(options):
        if opt == '-o' and i + 1 < len(options):
            output_file = options[i + 1]
            break

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        print(f"Generated: {output_file}")
    else:
        print(c_code)

if __name__ == '__main__':
    main()
