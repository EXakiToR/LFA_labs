Topic: Regular expressions  
Course: Formal Languages & Finite Automata  
Author: Cretu Dumitru and kudos to the Vasile Drumea with Irina Cojuhari

## Overview

Regular expressions (regex) are a formal notation used to describe sets of strings (languages) using compact symbolic patterns.  
They are widely used for lexical analysis, input validation, text search, filtering, and data extraction.

In this laboratory work, the goal was to interpret regex patterns dynamically and generate valid strings from them, instead of hardcoding string templates.  
Variant 1 contains 3 complex expressions with alternation, concatenation, grouping, and repetition operators.

## Objectives

- Explain what regular expressions are and what they are used for.
- Implement code that dynamically interprets the given regexes and generates valid words.
- Limit unbounded repetition operators (`*`, `+`) to maximum 5 occurrences.
- Bonus: provide a function that shows the sequence of processing/generation steps.
- Write a report covering actions performed and encountered difficulties.

## Variant 1 Regexes

Original assignment expressions:

1. `(a|b)(c|d)E⁺ G?`
2. `P(Q|R|S)T(UV|W|X)* Z⁺`
3. `1(0|1)* 2(3|4)⁵ 36`

Implementation note: due to Windows console encoding limits for superscript symbols, equivalent ASCII input forms were used in demo execution:

1. `(a|b)(c|d)E+G?`
2. `P(Q|R|S)T(UV|W|X)*Z+`
3. `1(0|1)*2(3|4){5}36`

These are semantically equivalent to the required variant.

## Implementation Description

The solution is split into:

- `regular_expression_generator.py` - dynamic parser + generator;
- `regex_demo.py` - client script for Variant 1 demos.

### 1) Dynamic regex interpretation

A recursive-descent parser was implemented to transform input regex text into an AST (abstract syntax tree).  
Supported constructs:

- literals (single characters);
- concatenation (implicit);
- alternation (`|`);
- grouping (`(...)`);
- repetition:
  - `*` as 0..5,
  - `+` as 1..5,
  - `?` as 0..1,
  - superscript exact repetition `⁰..⁹`,
  - exact repetition `{n}`.

This means behavior is not hardcoded per variant; any expression using the supported syntax can be parsed and generated.

### 2) Generation with bounded repetition

Each AST node has a `generate(...)` method:

- `Choice` randomly picks one option;
- `Concat` concatenates generated parts;
- `Repeat` chooses repetition count in allowed range.

For unbounded operators (`*`, `+`), upper limit is set to 5, respecting the assignment requirement.

### 3) Bonus: processing sequence

Function `explain_generation(...)` generates one valid word and returns a step-by-step trace such as:

- entering concatenation;
- choosing branch in alternation;
- repetition count decision;
- emitted literals.

This provides visibility into the exact order of regex processing.

## Code Snippets

### Unary operator handling (`regular_expression_generator.py`)

```python
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
            ...
```

### Variant 1 demo input (`regex_demo.py`)

```python
variant_1_regexes = [
    "(a|b)(c|d)E+G?",
    "P(Q|R|S)T(UV|W|X)*Z+",
    "1(0|1)*2(3|4){5}36",
]
```

## Execution / Results

Running `python regex_demo.py` produced valid strings for all 3 regexes.

Examples from run:

- Regex 1: `acEEE`, `acE`, `bcE`, `acEEEEE`, `adEEG`
- Regex 2: `PSTZ`, `PSTUVUVZZ`, `PSTZZZZZ`, `PQTWUVUVUVZZ`, `PQTXUVXUVZZZZZ`
- Regex 3: `10010023343336`, `123334336`, `110024433436`, `124344436`, `123434436`

All examples respect the specified structure and repetition constraints.

Additionally, one traced generation was printed for each regex to show processing order and decisions.

## Faced Difficulties and Solutions

1. **Superscript symbols in Windows terminal**  
   Printing `⁺` and `⁵` caused a `UnicodeEncodeError` in the default terminal encoding (cp1251).  
   **Solution:** kept parser support for superscripts, but demo input uses ASCII-equivalent operators (`+` and `{5}`), which are semantically identical.

2. **Dynamic parsing without hardcoding patterns**  
   The challenge was to support operator precedence and implicit concatenation correctly.  
   **Solution:** implemented recursive-descent parsing with separate methods for expression (`|`), concatenation, unary operators, and atoms.

3. **Infinite-size language for `*`/`+`**  
   Raw regex languages with these operators can produce unbounded strings.  
   **Solution:** introduced assignment-compliant cap of 5 repeats.

## Conclusions

The lab objectives were achieved:

- Regular expressions were explained and contextualized.
- A dynamic regex interpreter/generator was implemented.
- Generation supports Variant 1 patterns and respects repetition cap.
- Bonus trace functionality was implemented to show generation sequence.

This implementation can be reused for similar regex-generation tasks by simply changing input expressions.

## References

- [Python `re` documentation](https://docs.python.org/3/library/re.html)
- [Regular expression - Wikipedia](https://en.wikipedia.org/wiki/Regular_expression)
