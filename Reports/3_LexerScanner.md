Topic: Lexer & Scanner
Course: Formal Languages & Finite Automata
Author: Cretu Dumitru and cudos to the Vasile Drumea with Irina Cojuhari

## Overview
The lexer (also called tokenizer or scanner) is the first stage of lexical analysis. It processes a raw input text and groups it into meaningful lexical units called lexemes, then assigns each lexeme a token category (for example: number, operator, keyword). This creates a stream of tokens that later stages (a parser) can use.

In this lab I implemented a small hand-written lexer in Python that recognizes integers, floating-point numbers, the trigonometric keywords `sin` and `cos`, parentheses, and arithmetic operators. The goal is to demonstrate the “inner workings” of a scanner: reading the input character-by-character and applying maximal-munch rules for tokens.

## Objectives
1. Understand what lexical analysis is and why it is useful.
2. Get familiar with how a lexer/scanner is implemented (stateful, character-by-character).
3. Implement a sample lexer and demonstrate how it tokenizes a more interesting input than a basic calculator.

## Implementation Description
The implementation is split into two parts:

1) `lexer.py` contains the lexer logic.
2) `lexer_demo.py` is a small client that shows the lexer output for a sample input.

### Token stream produced by the lexer
The lexer recognizes:
- `INT`: integer literals (e.g. `12`)
- `FLOAT`: floating-point literals with a decimal point (e.g. `3.14`, `0.5`)
- `SIN` / `COS`: identifiers exactly equal to `sin` or `cos`
- `IDENT`: any other identifier matching `[a-zA-Z_][a-zA-Z0-9_]*`
- Operators/delimiters: `+ - * / ^ ( )`

Whitespace is skipped.

### Maximal munch (longest match) for numbers and identifiers
When the current character starts a token, the lexer consumes as many characters as possible that still match the same token class:
- For numbers: it reads consecutive digits as the integer part; if it then sees a `.` followed by digits, it continues reading the fractional part and returns `FLOAT`. Otherwise it returns `INT`.
- For identifiers: it reads letters/digits/underscore after the first letter/underscore. After extracting the full identifier, it checks whether it is `sin` or `cos` (then returns `SIN`/`COS`), otherwise it returns `IDENT`.

### What is not included
This lab focuses on lexical analysis, so this implementation tokenizes input only. It does not parse or evaluate expressions (computing numeric results).

## Code Snippets
### Lexer (`lexer.py`)
```python
class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def next_token(self) -> Token:
        self._skip_whitespace()
        ch = self._peek()

        if ch is None:
            return Token(type="EOF", value=None, position=self.pos)

        if ch.isdigit():
            return self._lex_number()

        if ch.isalpha() or ch == "_":
            return self._lex_identifier()

        self.pos += 1  # consume the current character
        ...
```

### Demo (`lexer_demo.py`)
```python
def main() -> None:
    text = "sin(0.5) + cos(1.0) * 2"
    lexer = Lexer(text)

    print("Input:")
    print(text)
    print("\nTokens:")
    for tok in lexer.tokenize():
        print(tok)
```

### Demo Output
Running `python -u lexer_demo.py` produced:
```text
Input:
sin(0.5) + cos(1.0) * 2

Tokens:
Token(type='SIN', value='sin', position=0)
Token(type='LPAREN', value='(', position=3)
Token(type='FLOAT', value=0.5, position=4)
Token(type='RPAREN', value=')', position=7)
Token(type='PLUS', value='+', position=9)
Token(type='COS', value='cos', position=11)
Token(type='LPAREN', value='(', position=14)
Token(type='FLOAT', value=1.0, position=15)
Token(type='RPAREN', value=')', position=18)
Token(type='MUL', value='*', position=20)
Token(type='INT', value=2, position=22)
Token(type='EOF', value=None, position=23)
```

## Conclusions / Results
The lexer successfully converts an input expression containing numbers, the `sin`/`cos` keywords, parentheses, and arithmetic operators into a deterministic stream of tokens. This demonstrates the standard pipeline idea from compiler construction: the lexer reduces the complexity of later parsing by operating with a clear token interface (token type + token value).

## References
- [LLVM Kaleidoscope Tutorial - Lexer section](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html)
- [Wikipedia - Lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis)

