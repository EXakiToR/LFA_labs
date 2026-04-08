from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class TokenType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    SIN = "SIN"
    COS = "COS"
    IDENT = "IDENT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POW = "POW"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    type: TokenType
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

        self._patterns = [
            (TokenType.FLOAT, re.compile(r"\d+\.\d+")),
            (TokenType.INT, re.compile(r"\d+")),
            (TokenType.IDENT, re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")),
            (TokenType.PLUS, re.compile(r"\+")),
            (TokenType.MINUS, re.compile(r"-")),
            (TokenType.MUL, re.compile(r"\*")),
            (TokenType.DIV, re.compile(r"/")),
            (TokenType.POW, re.compile(r"\^")),
            (TokenType.LPAREN, re.compile(r"\(")),
            (TokenType.RPAREN, re.compile(r"\)")),
        ]
        self._ws = re.compile(r"\s+")

    def next_token(self) -> Token:
        ws_match = self._ws.match(self.text, self.pos)
        if ws_match:
            self.pos = ws_match.end()

        if self.pos >= len(self.text):
            return Token(type=TokenType.EOF, value=None, position=self.pos)

        for token_type, pattern in self._patterns:
            match = pattern.match(self.text, self.pos)
            if not match:
                continue
            lexeme = match.group(0)
            start = self.pos
            self.pos = match.end()

            if token_type == TokenType.FLOAT:
                return Token(type=TokenType.FLOAT, value=float(lexeme), position=start)
            if token_type == TokenType.INT:
                return Token(type=TokenType.INT, value=int(lexeme), position=start)
            if token_type == TokenType.IDENT:
                if lexeme == "sin":
                    return Token(type=TokenType.SIN, value=lexeme, position=start)
                if lexeme == "cos":
                    return Token(type=TokenType.COS, value=lexeme, position=start)
                return Token(type=TokenType.IDENT, value=lexeme, position=start)
            return Token(type=token_type, value=lexeme, position=start)

        raise ValueError(f"Unexpected character {self.text[self.pos]!r} at position {self.pos}")

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens

