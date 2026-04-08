from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional


SUPERSCRIPT_MAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


class RegexParseError(ValueError):
    pass


@dataclass(frozen=True)
class Node:
    def generate(self, rng: random.Random, max_repeat: int, trace: Optional[List[str]] = None) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Literal(Node):
    value: str

    def generate(self, rng: random.Random, max_repeat: int, trace: Optional[List[str]] = None) -> str:
        if trace is not None:
            trace.append(f"LITERAL('{self.value}')")
        return self.value


@dataclass(frozen=True)
class Concat(Node):
    parts: List[Node]

    def generate(self, rng: random.Random, max_repeat: int, trace: Optional[List[str]] = None) -> str:
        if trace is not None:
            trace.append("CONCAT(")
        out = "".join(part.generate(rng, max_repeat, trace) for part in self.parts)
        if trace is not None:
            trace.append(")")
        return out


@dataclass(frozen=True)
class Choice(Node):
    options: List[Node]

    def generate(self, rng: random.Random, max_repeat: int, trace: Optional[List[str]] = None) -> str:
        idx = rng.randrange(len(self.options))
        if trace is not None:
            trace.append(f"CHOICE(option={idx + 1}/{len(self.options)})")
        return self.options[idx].generate(rng, max_repeat, trace)


@dataclass(frozen=True)
class Repeat(Node):
    expr: Node
    min_times: int
    max_times: int

    def generate(self, rng: random.Random, max_repeat: int, trace: Optional[List[str]] = None) -> str:
        local_max = min(self.max_times, max_repeat)
        if local_max < self.min_times:
            local_max = self.min_times
        times = rng.randint(self.min_times, local_max)
        if trace is not None:
            trace.append(f"REPEAT(times={times}, min={self.min_times}, max={self.max_times})")
        return "".join(self.expr.generate(rng, max_repeat, trace) for _ in range(times))


class RegexGenerator:
    """
    Dynamic generator for a small regex language:
      - literals (any non-meta character)
      - concatenation (implicit)
      - alternation: |
      - grouping: (...)
      - unary operators: *, +, ?
      - superscript + and ? (⁺, ⁇ equivalent if present in text)
      - exact superscript repeat: ⁰..⁹ (e.g., (3|4)⁵)
      - exact repeat with braces: {n} (e.g., (3|4){5})
    """

    def __init__(self, pattern: str) -> None:
        self.original_pattern = pattern
        self.pattern = self._normalize(pattern)
        self.i = 0
        self.ast = self._parse_expression()
        if self.i != len(self.pattern):
            raise RegexParseError(f"Unexpected trailing input at index {self.i}: {self.pattern[self.i:]!r}")

    @staticmethod
    def _normalize(pattern: str) -> str:
        return "".join(ch for ch in pattern if not ch.isspace())

    def _peek(self) -> Optional[str]:
        if self.i >= len(self.pattern):
            return None
        return self.pattern[self.i]

    def _consume(self) -> Optional[str]:
        ch = self._peek()
        if ch is not None:
            self.i += 1
        return ch

    def _parse_expression(self) -> Node:
        options = [self._parse_concatenation()]
        while self._peek() == "|":
            self._consume()
            options.append(self._parse_concatenation())
        if len(options) == 1:
            return options[0]
        return Choice(options)

    def _parse_concatenation(self) -> Node:
        parts: List[Node] = []
        while True:
            ch = self._peek()
            if ch is None or ch in ")|":
                break
            parts.append(self._parse_unary())
        if not parts:
            return Literal("")
        if len(parts) == 1:
            return parts[0]
        return Concat(parts)

    def _parse_unary(self) -> Node:
        base = self._parse_atom()
        while True:
            ch = self._peek()
            if ch == "*":
                self._consume()
                base = Repeat(base, 0, 5)
            elif ch in {"+", "⁺"}:
                self._consume()
                base = Repeat(base, 1, 5)
            elif ch in {"?", "⁇"}:
                self._consume()
                base = Repeat(base, 0, 1)
            elif ch is not None and ch.translate(SUPERSCRIPT_MAP).isdigit() and ch in "⁰¹²³⁴⁵⁶⁷⁸⁹":
                n = int(ch.translate(SUPERSCRIPT_MAP))
                self._consume()
                base = Repeat(base, n, n)
            elif ch == "{":
                self._consume()
                digits: List[str] = []
                while (cur := self._peek()) is not None and cur.isdigit():
                    digits.append(cur)
                    self._consume()
                if not digits:
                    raise RegexParseError("Expected integer inside repetition braces, e.g. {5}.")
                if self._consume() != "}":
                    raise RegexParseError("Unclosed repetition braces: expected '}'.")
                n = int("".join(digits))
                base = Repeat(base, n, n)
            else:
                break
        return base

    def _parse_atom(self) -> Node:
        ch = self._peek()
        if ch is None:
            raise RegexParseError("Unexpected end of input while parsing atom.")
        if ch == "(":
            self._consume()
            expr = self._parse_expression()
            if self._consume() != ")":
                raise RegexParseError("Unclosed group: expected ')'.")
            return expr
        if ch in {"|", ")", "*", "+", "?", "⁺", "⁇"}:
            raise RegexParseError(f"Unexpected token {ch!r} at index {self.i}.")
        self._consume()
        return Literal(ch)

    def generate_word(self, rng: Optional[random.Random] = None, max_repeat: int = 5) -> str:
        if rng is None:
            rng = random.Random()
        return self.ast.generate(rng, max_repeat=max_repeat)

    def generate_words(
        self,
        count: int,
        rng: Optional[random.Random] = None,
        max_repeat: int = 5,
    ) -> List[str]:
        if count <= 0:
            return []
        if rng is None:
            rng = random.Random()
        return [self.generate_word(rng=rng, max_repeat=max_repeat) for _ in range(count)]

    def explain_generation(self, rng: Optional[random.Random] = None, max_repeat: int = 5) -> tuple[str, List[str]]:
        if rng is None:
            rng = random.Random()
        trace: List[str] = []
        word = self.ast.generate(rng, max_repeat=max_repeat, trace=trace)
        return word, trace

