from __future__ import annotations

from lexer import Lexer


def main() -> None:
    text = "sin(0.5) + cos(1.0) * 2"
    lexer = Lexer(text)

    print("Input:")
    print(text)
    print("\nTokens:")
    for tok in lexer.tokenize():
        print(tok)


if __name__ == "__main__":
    main()

