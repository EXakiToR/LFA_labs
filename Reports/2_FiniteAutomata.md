# Laboratory Work 2: Determinism in Finite Automata. Conversion from NDFA to DFA. Chomsky Hierarchy
Course: Formal Languages & Finite Automata  
Author: Cretu Dumitru  
Kudos to: Vasile Drumea and Irina Cojuhari

## Overview

A finite automaton is a mechanism used to represent computational processes through states and transitions.  
The word *finite* reflects that the model has a bounded set of states, including a start state and one or more final states.

In practice, there are automata where for the same input symbol, multiple next states are possible. This is called non-determinism.  
Determinism means that for each state and symbol there is at most one next state, so the evolution of the automaton is fully predictable.

This laboratory focuses on:
- identifying whether a finite automaton is deterministic;
- converting a non-deterministic finite automaton (NDFA/NFA) to a deterministic finite automaton (DFA);
- converting a finite automaton to a regular grammar;
- classifying the resulting grammar in the Chomsky hierarchy.

## Objectives

Continuing the same repository and project, the implemented objectives are:

- Add a function in the grammar class to classify the grammar according to Chomsky hierarchy.
- Use the finite automaton from the variant and implement conversion from finite automaton to regular grammar.
- Determine whether the given finite automaton is deterministic or non-deterministic.
- Implement functionality to convert NDFA to DFA.

Optional graphical representation was not implemented, so it is intentionally not included in this report.

## Implementation Description

The solution is implemented in:
- `grammar.py`
- `finite_automaton.py`
- `main.py`

### 1) Chomsky hierarchy classification

In `grammar.py`, method `classify_chomsky_type()` was added in `Grammar`:

- The grammar representation supports right-linear rules of forms `A -> aB`, `A -> a`, and `A -> ε`.
- Because of this structure, the method classifies the grammar as:
  - `Type-3 regular (right-linear) grammar`

### 2) Finite automaton to regular grammar conversion

In `grammar.py`, function `finite_automaton_to_grammar(automaton)` converts FA to a right-linear grammar:

- Each automaton state becomes a non-terminal.
- Each transition `q --a--> p` becomes production `q -> a p`.
- Each final state receives an epsilon production `q_f -> ε` (stored internally as `("", None)`).
- The start symbol of the grammar is the automaton start state.

### 3) Determinism check

In `finite_automaton.py`, method `is_deterministic()` determines if automaton is DFA:

- It checks all transition destination sets.
- If any transition has more than one destination state, automaton is non-deterministic.

Variant 11 automaton (`build_variant_11_automaton`) includes:
- `δ(q2, c) = {q0, q3}`

Since one `(state, symbol)` pair has 2 destinations, the automaton is NDFA.

### 4) NDFA to DFA conversion

In `finite_automaton.py`, method `to_deterministic()` implements subset construction:

- DFA states are subsets of NDFA states.
- Start subset is `{q0}`.
- For each subset and symbol, destination subset is union of reachable NDFA states.
- Subsets are encoded as named states like `{q0,q2}`.
- A DFA subset state is final if it contains at least one NDFA final state.

The resulting automaton is deterministic and validated using the same class constructor.

### 5) Main client demonstration

`main.py` demonstrates all required functionality:

- builds and uses the regular grammar from previous lab;
- prints the Chomsky type;
- builds Variant 11 finite automaton;
- checks determinism (`False` for variant NDFA);
- converts NDFA to DFA and checks determinism (`True`);
- converts FA to regular grammar and prints its classification.

## Code Snippets

**Chomsky classification (`grammar.py`)**

```python
def classify_chomsky_type(self) -> str:
    """
    Classify this grammar in the Chomsky hierarchy.
    """
    return "Type-3 regular (right-linear) grammar"
```

**FA -> Grammar conversion (`grammar.py`)**

```python
def finite_automaton_to_grammar(automaton: FiniteAutomaton) -> Grammar:
    non_terminals = set(automaton.states)
    terminals = set(automaton.alphabet)

    productions = {state: [] for state in automaton.states}

    for (src, symbol), dests in automaton.transitions.items():
        for dst in dests:
            productions[src].append((symbol, dst))

    for f in automaton.final_states:
        productions.setdefault(f, [])
        productions[f].append(("", None))  # epsilon

    return Grammar(
        non_terminals=non_terminals,
        terminals=terminals,
        productions=productions,
        start_symbol=automaton.start_state,
    )
```

**Determinism + NDFA->DFA (`finite_automaton.py`)**

```python
def is_deterministic(self) -> bool:
    for (_, _), dests in self.transitions.items():
        if len(dests) > 1:
            return False
    return True

def to_deterministic(self) -> "FiniteAutomaton":
    # subset construction over reachable subsets
    ...
```

## Execution / Results

Running `python main.py` produced:

```text
Generating 5 words using the regular grammar:
  1. abaaab
  2. aabccbab
  3. bcaacbab
  4. aabbb
  5. aababbab

Checking if the generated words are accepted by the finite automaton:
  abaaab -> True
  aabccbab -> True
  bcaacbab -> True
  aabbb -> True
  aababbab -> True

Manual tests for membership:
  ab -> False
  bb -> False
  baab -> False
  abab -> True
  ac -> False
  bcbc -> False
  baaab -> False

Chomsky type of the grammar: Type-3 regular (right-linear) grammar

Variant 11 FA is deterministic? False
Converted DFA is deterministic? True
Grammar derived from Variant 11 FA is classified as: Type-3 regular (right-linear) grammar
```

## Conclusions

The implemented code satisfies the required parts of Laboratory Work 2 that are present in the project:

- grammar classification by Chomsky hierarchy is implemented;
- finite automaton to regular grammar conversion is implemented;
- determinism detection is implemented and correctly identifies Variant 11 FA as NDFA;
- NDFA to DFA conversion is implemented and produces a deterministic automaton.

The optional graphical representation was not implemented and is therefore excluded from the report, as requested.

## References

- https://else.fcim.utm.md/pluginfile.php/110457/mod_resource/content/0/Theme_2.pdf
- https://else.fcim.utm.md/pluginfile.php/110457/mod_resource/content/0/Theme_1.pdf
- Python documentation: https://docs.python.org/3/
