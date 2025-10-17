#!/usr/bin/env python3
import sys
from lexer import Lexer
from parser_ll import Parser
from interpreter import Interpreter

def main():
    if len(sys.argv) != 2:
        print("Kullanım: python main.py <ffling_dosya>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Dosya bulunamadı: {filename}")
        sys.exit(1)

    # Lexer, Parser, Interpreter kullanarak kodu çalıştır
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    interpreter.execute(ast)

if __name__ == "__main__":
    main()
