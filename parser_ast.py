from __future__ import annotations

from dataclasses import dataclass
from typing import List

from lexer import Lexer, Token, TokenType


@dataclass(frozen=True)
class ASTNode:
    pass


@dataclass(frozen=True)
class NumberNode(ASTNode):
    value: float


@dataclass(frozen=True)
class IdentifierNode(ASTNode):
    name: str


@dataclass(frozen=True)
class UnaryOpNode(ASTNode):
    op: TokenType
    operand: ASTNode


@dataclass(frozen=True)
class BinaryOpNode(ASTNode):
    left: ASTNode
    op: TokenType
    right: ASTNode


@dataclass(frozen=True)
class FunctionCallNode(ASTNode):
    name: str
    argument: ASTNode


class ParserError(ValueError):
    pass


class Parser:
    """
    Recursive-descent parser for arithmetic expressions.

    Grammar (with precedence and right-associative power):
      expr   := term (('+' | '-') term)*
      term   := power (('*' | '/') power)*
      power  := unary ('^' power)?
      unary  := '-' unary | primary
      primary:= INT | FLOAT | IDENT | ('sin'|'cos') '(' expr ')' | '(' expr ')'
    """

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.i = 0

    @classmethod
    def from_text(cls, text: str) -> "Parser":
        lexer = Lexer(text)
        return cls(lexer.tokenize())

    def _current(self) -> Token:
        return self.tokens[self.i]

    def _consume(self, expected: TokenType | None = None) -> Token:
        tok = self._current()
        if expected is not None and tok.type != expected:
            raise ParserError(f"Expected {expected.value}, got {tok.type.value} at position {tok.position}.")
        self.i += 1
        return tok

    def parse(self) -> ASTNode:
        node = self._parse_expr()
        if self._current().type != TokenType.EOF:
            tok = self._current()
            raise ParserError(f"Unexpected token {tok.type.value} at position {tok.position}.")
        return node

    def _parse_expr(self) -> ASTNode:
        node = self._parse_term()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._consume().type
            right = self._parse_term()
            node = BinaryOpNode(left=node, op=op, right=right)
        return node

    def _parse_term(self) -> ASTNode:
        node = self._parse_power()
        while self._current().type in (TokenType.MUL, TokenType.DIV):
            op = self._consume().type
            right = self._parse_power()
            node = BinaryOpNode(left=node, op=op, right=right)
        return node

    def _parse_power(self) -> ASTNode:
        node = self._parse_unary()
        if self._current().type == TokenType.POW:
            op = self._consume().type
            right = self._parse_power()
            node = BinaryOpNode(left=node, op=op, right=right)
        return node

    def _parse_unary(self) -> ASTNode:
        if self._current().type == TokenType.MINUS:
            op = self._consume().type
            return UnaryOpNode(op=op, operand=self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        tok = self._current()

        if tok.type == TokenType.INT:
            self._consume(TokenType.INT)
            return NumberNode(value=float(tok.value))

        if tok.type == TokenType.FLOAT:
            self._consume(TokenType.FLOAT)
            return NumberNode(value=float(tok.value))

        if tok.type == TokenType.IDENT:
            self._consume(TokenType.IDENT)
            return IdentifierNode(name=str(tok.value))

        if tok.type in (TokenType.SIN, TokenType.COS):
            func_name = str(tok.value)
            self._consume(tok.type)
            self._consume(TokenType.LPAREN)
            arg = self._parse_expr()
            self._consume(TokenType.RPAREN)
            return FunctionCallNode(name=func_name, argument=arg)

        if tok.type == TokenType.LPAREN:
            self._consume(TokenType.LPAREN)
            node = self._parse_expr()
            self._consume(TokenType.RPAREN)
            return node

        raise ParserError(f"Unexpected token {tok.type.value} at position {tok.position}.")


def ast_to_pretty_lines(node: ASTNode, indent: int = 0) -> List[str]:
    pad = "  " * indent
    if isinstance(node, NumberNode):
        return [f"{pad}Number({node.value})"]
    if isinstance(node, IdentifierNode):
        return [f"{pad}Identifier({node.name})"]
    if isinstance(node, UnaryOpNode):
        lines = [f"{pad}UnaryOp({node.op.value})"]
        lines.extend(ast_to_pretty_lines(node.operand, indent + 1))
        return lines
    if isinstance(node, BinaryOpNode):
        lines = [f"{pad}BinaryOp({node.op.value})"]
        lines.extend(ast_to_pretty_lines(node.left, indent + 1))
        lines.extend(ast_to_pretty_lines(node.right, indent + 1))
        return lines
    if isinstance(node, FunctionCallNode):
        lines = [f"{pad}Call({node.name})"]
        lines.extend(ast_to_pretty_lines(node.argument, indent + 1))
        return lines
    return [f"{pad}<unknown node>"]

