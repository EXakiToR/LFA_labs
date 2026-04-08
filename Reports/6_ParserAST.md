Topic: Parser & Building an Abstract Syntax Tree  
Course: Formal Languages & Finite Automata  
Author: Cretu Dumitru and cudos to the Vasile Drumea with Irina Cojuhari

## Overview

Parsing is the process of extracting syntactic structure from a stream of tokens according to grammar rules.  
In compiler-like pipelines, lexical analysis is followed by parsing, and parsing usually produces a structural representation such as a parse tree or an Abstract Syntax Tree (AST).

An AST is a simplified tree representation of source text: it keeps the semantic/syntactic constructs (operations, literals, function calls) while omitting unnecessary concrete syntax details.  
This lab extends the lexer from Lab 3 by adding a token type enum, regex-based token classification, and a recursive-descent parser that builds an AST.

## Objectives

- Get familiar with parsing and how it is programmed.
- Get familiar with AST and why it is useful.
- Add a `TokenType` type for lexical categories.
- Use regular expressions in lexical analysis to identify token types.
- Implement AST data structures for the processed text.
- Implement a simple parser that extracts syntactic information from input.
- Execute and test the functionality.

## Implementation Description

The implementation is split into:

- `lexer.py` (updated)
- `parser_ast.py` (new)
- `parser_demo.py` (new)

### 1) TokenType and regex-based lexical analysis

`lexer.py` now defines:

- `TokenType` as an enum (`INT`, `FLOAT`, `SIN`, `COS`, `IDENT`, `PLUS`, `MINUS`, `MUL`, `DIV`, `POW`, `LPAREN`, `RPAREN`, `EOF`);
- `Token` using `type: TokenType`.

Token detection uses compiled regular expressions, matched from the current position with priority order:

- float, int, identifier, operators, parentheses.

Keyword mapping is done after identifier match:

- `sin` -> `TokenType.SIN`
- `cos` -> `TokenType.COS`
- otherwise -> `TokenType.IDENT`.

### 2) AST data structures

In `parser_ast.py`, these AST nodes were implemented:

- `NumberNode`
- `IdentifierNode`
- `UnaryOpNode`
- `BinaryOpNode`
- `FunctionCallNode`

This structure is enough for arithmetic expressions with function calls and precedence.

### 3) Parser

A recursive-descent parser (`Parser`) was implemented with grammar:

- `expr   := term (('+' | '-') term)*`
- `term   := power (('*' | '/') power)*`
- `power  := unary ('^' power)?` (right-associative)
- `unary  := '-' unary | primary`
- `primary:= INT | FLOAT | IDENT | ('sin'|'cos') '(' expr ')' | '(' expr ')'`

The parser consumes tokens from the lexer and builds AST nodes incrementally.

### 4) AST visualization

Helper `ast_to_pretty_lines(...)` prints a readable tree-like structure, useful for report evidence and debugging.

## Code Snippets

### TokenType enum (`lexer.py`)

```python
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
```

### Parser entry point (`parser_ast.py`)

```python
def parse(self) -> ASTNode:
    node = self._parse_expr()
    if self._current().type != TokenType.EOF:
        tok = self._current()
        raise ParserError(f"Unexpected token {tok.type.value} at position {tok.position}.")
    return node
```

### Demo (`parser_demo.py`)

```python
text = "sin(0.5) + cos(1.0) * 2 ^ (3 - 1)"
lexer = Lexer(text)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
```

## Execution / Results

### 1) Lexer validation

Running `python lexer_demo.py` now returns tokens with enum types:

```text
Token(type=<TokenType.SIN: 'SIN'>, value='sin', position=0)
Token(type=<TokenType.LPAREN: 'LPAREN'>, value='(', position=3)
Token(type=<TokenType.FLOAT: 'FLOAT'>, value=0.5, position=4)
...
Token(type=<TokenType.EOF: 'EOF'>, value=None, position=23)
```

### 2) Parser + AST

Running `python parser_demo.py`:

Input:

```text
sin(0.5) + cos(1.0) * 2 ^ (3 - 1)
```

Produced AST:

```text
BinaryOp(PLUS)
  Call(sin)
    Number(0.5)
  BinaryOp(MUL)
    Call(cos)
      Number(1.0)
    BinaryOp(POW)
      Number(2.0)
      BinaryOp(MINUS)
        Number(3.0)
        Number(1.0)
```

This confirms syntactic structure extraction with operator precedence and hierarchy.

## Faced Difficulties

- **Preserving precedence and associativity**  
  Implemented layered recursive-descent methods (`expr`, `term`, `power`, `unary`, `primary`) and right-associative handling for `^`.

- **Migrating from string token types to enum-based types**  
  Updated lexer flow and stop condition to compare against `TokenType.EOF`, keeping behavior consistent with previous labs.

## Conclusions

All requested tasks were completed:

- `TokenType` introduced;
- regex-based token identification implemented;
- AST structures implemented;
- parser implemented and tested;
- practical run output confirms correct syntactic extraction.

The resulting mini front-end now contains a complete flow:

`input text -> lexer tokens -> parser -> AST`.

## References

- [1] https://en.wikipedia.org/wiki/Parsing
- [2] https://en.wikipedia.org/wiki/Abstract_syntax_tree
