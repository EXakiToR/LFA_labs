Topic (5th): Chomsky Normal Form  
Course: Formal Languages & Finite Automata  
Author: Cretu Dumitru and cudos to the Vasile Drumea with Irina Cojuhari

## Overview

Chomsky Normal Form (CNF) is a restricted form of context-free grammar where each production is one of:

- `A -> BC` (two non-terminals), or
- `A -> a` (one terminal),
- plus optionally `S -> eps` only when epsilon belongs to the language.

CNF is important because it standardizes grammars and is commonly used in parsing algorithms (for example CYK).

This lab implements grammar normalization for Variant 11 and applies the required sequence:

1. eliminate epsilon productions;
2. eliminate renaming/unit productions;
3. eliminate inaccessible symbols;
4. eliminate non-productive symbols;
5. convert to CNF.

## Objectives

- Learn what Chomsky Normal Form is.
- Understand normalization steps for CFGs.
- Implement normalization in a reusable method with clear signature.
- Execute and test the implementation on Variant 11.
- Bonus target: keep the code generic for other grammars.

## Input Grammar (Variant 11)

Given:

- `Vn = {S, A, B, C, D}`
- `Vt = {a, b}`
- Productions:
  - `S -> bA | AC`
  - `A -> bS | BC | AbAa`
  - `B -> BbaA | a | bSa`
  - `C -> eps`
  - `D -> AB`

## Implementation

### Files

- `cnf.py`  
  Contains:
  - `CFG` data model (`non_terminals`, `terminals`, `productions`, `start_symbol`);
  - `CNFNormalizer` class with `normalize(grammar) -> tuple[CFG, List[str]]`.
- `cnf_demo.py`  
  Runs Variant 11 through all normalization steps and prints the transformation log.

### Normalization pipeline

`CNFNormalizer.normalize(...)` performs:

1. `_eliminate_epsilon`
2. `_eliminate_unit`
3. `_remove_inaccessible`
4. `_remove_non_productive`
5. `_to_cnf`

The method returns both:

- the final normalized grammar;
- a textual log after each step, used as execution evidence.

### Generic behavior (bonus)

The implementation is not hardcoded for Variant 11 rules; it works over the generic `CFG` structure and can normalize other grammars that use the same representation.

## Execution / Tested Output

Running:

- `python cnf_demo.py`

produced the expected full step-by-step transformation for Variant 11.

Main observed effects:

- `C -> eps` removed in epsilon-elimination and propagated alternatives.
- Unit productions (e.g., `S -> A`, `A -> B`) removed via unit-closure.
- Inaccessible symbol `D` removed.
- Non-productive `C` removed.
- Long productions and mixed terminal/non-terminal productions transformed using helper non-terminals (`T_a_2`, `T_b_1`, `X...`) and binarization.

Final grammar printed by the program:

```text
Vn = ['A', 'B', 'S', 'T_a_2', 'T_b_1', 'X10', 'X11', 'X12', 'X13', 'X14', 'X15', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9']
Vt = ['a', 'b']
P = {
  A -> AX6 | BX9 | T_b_1S | T_b_1X8 | a
  B -> BX4 | T_b_1X3 | a
  S -> AX11 | BX14 | T_b_1A | T_b_1S | T_b_1X13 | a
  T_a_2 -> a
  T_b_1 -> b
  X10 -> T_a_2A
  X11 -> T_b_1X12
  X12 -> AT_a_2
  X13 -> ST_a_2
  X14 -> T_b_1X15
  X15 -> T_a_2A
  X3 -> ST_a_2
  X4 -> T_b_1X5
  X5 -> T_a_2A
  X6 -> T_b_1X7
  X7 -> AT_a_2
  X8 -> ST_a_2
  X9 -> T_b_1X10
}
Start = S
```

All productions are in CNF shape (`A -> BC` or `A -> a`), so the conversion is successful.

## Faced Difficulties

- **Console encoding issue on Windows** for Greek epsilon character (`ε`) caused output errors.
  - Fixed by printing `eps` in text output.
- **Dictionary mutation during iteration** while creating fresh helper non-terminals in CNF step.
  - Fixed by iterating over snapshot lists (`list(g.productions.items())`).

## Conclusions

The task requirements were completed:

- CNF normalization method implemented in an appropriate class.
- Full required sequence of simplification/normalization steps executed.
- Variant 11 grammar successfully transformed to CNF.
- Implementation is reusable beyond one variant (bonus criterion direction achieved).

## References

- [1] Chomsky Normal Form (Wikipedia): https://en.wikipedia.org/wiki/Chomsky_normal_form
- Formal languages course materials (CNF normalization topics)
