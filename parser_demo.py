from __future__ import annotations

from lexer import Lexer
from parser_ast import Parser, ast_to_pretty_lines


def main() -> None:
    text = "sin(0.5) + cos(1.0) * 2 ^ (3 - 1)"
    lexer = Lexer(text)
    tokens = lexer.tokenize()

    print("Input:")
    print(text)

    print("\nTokens:")
    for tok in tokens:
        print(f"{tok.type.value:<6} value={tok.value!r} pos={tok.position}")

    parser = Parser(tokens)
    ast = parser.parse()

    print("\nAST:")
    for line in ast_to_pretty_lines(ast):
        print(line)


if __name__ == "__main__":
    main()

