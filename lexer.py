from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Token:
    type: str
    value: Any
    position: int  # index in the original input string


class Lexer:
    """
    A small hand-written lexer (scanner).

    It tokenizes:
      - integers: 123
      - floats:   3.14, 0.5
      - identifiers:
          sin, cos, and any other names as IDENT
      - operators and delimiters:
          + - * / ^ ( )

    This is the "first stage" of a compiler/interpreter: it converts a
    character stream into a stream of tokens.
    """

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def _peek(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def _advance(self) -> Optional[str]:
        ch = self._peek()
        if ch is None:
            return None
        self.pos += 1
        return ch

    def _skip_whitespace(self) -> None:
        while True:
            ch = self._peek()
            if ch is None or not ch.isspace():
                return
            self.pos += 1

    def _lex_number(self) -> Token:
        """
        Maximal munch for numbers:
          - read digits
          - if a '.' followed by a digit exists, read fractional part
        """
        start = self.pos

        # Integer part
        while (ch := self._peek()) is not None and ch.isdigit():
            self.pos += 1

        # Fractional part
        if self._peek() == ".":
            # Lookahead: only treat as float if there is at least one digit after '.'
            if self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit():
                self.pos += 1  # consume '.'
                while (ch := self._peek()) is not None and ch.isdigit():
                    self.pos += 1

                raw = self.text[start:self.pos]
                return Token(type="FLOAT", value=float(raw), position=start)

            # We saw a '.' but it's not a float like "12."
            raise ValueError(f"Invalid number at position {start}: expected digits after '.'")

        raw = self.text[start:self.pos]
        return Token(type="INT", value=int(raw), position=start)

    def _lex_identifier(self) -> Token:
        start = self.pos

        # [a-zA-Z_][a-zA-Z0-9_]*
        while True:
            ch = self._peek()
            if ch is None:
                break
            if ch.isalnum() or ch == "_":
                self.pos += 1
                continue
            break

        raw = self.text[start:self.pos]
        if raw == "sin":
            return Token(type="SIN", value=raw, position=start)
        if raw == "cos":
            return Token(type="COS", value=raw, position=start)
        return Token(type="IDENT", value=raw, position=start)

    def next_token(self) -> Token:
        self._skip_whitespace()
        ch = self._peek()

        if ch is None:
            return Token(type="EOF", value=None, position=self.pos)

        # Numbers
        if ch.isdigit():
            return self._lex_number()

        # Identifiers / keywords
        if ch.isalpha() or ch == "_":
            # identifier starts here, so consume first char in the loop
            return self._lex_identifier()

        # Operators / delimiters
        self.pos += 1  # consume the current character
        if ch == "+":
            return Token(type="PLUS", value=ch, position=self.pos - 1)
        if ch == "-":
            return Token(type="MINUS", value=ch, position=self.pos - 1)
        if ch == "*":
            return Token(type="MUL", value=ch, position=self.pos - 1)
        if ch == "/":
            return Token(type="DIV", value=ch, position=self.pos - 1)
        if ch == "^":
            return Token(type="POW", value=ch, position=self.pos - 1)
        if ch == "(":
            return Token(type="LPAREN", value=ch, position=self.pos - 1)
        if ch == ")":
            return Token(type="RPAREN", value=ch, position=self.pos - 1)

        # Anything else is invalid for this lexer
        raise ValueError(f"Unexpected character {ch!r} at position {self.pos - 1}")

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == "EOF":
                break
        return tokens

