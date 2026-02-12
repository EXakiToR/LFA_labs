Laboratory work 1: Regular Grammars and Finite Automata
Course: Formal Languages & Finite Automata
Author: Andrei Elciscev

## Theory

A formal language is a set of strings built from a finite alphabet according to precise rules. The alphabet is the collection of allowed symbols, the vocabulary is the set of all valid words over that alphabet, and the grammar describes how words can be formed using production rules. Regular grammars are a restricted kind of grammar that can be recognized by finite automata, which means their languages can be implemented and checked using a finite number of states and transitions.

Finite automata model computation as movement between states when reading input symbols. If at the end of the input the automaton is in an accepting (final) state, the word belongs to the language; otherwise, it does not. The close relationship between regular grammars and finite automata is important because it gives both a declarative (rules) and an operational (machine) view of the same language.

## Objectives

- Discover what a formal language is and what components it must have (alphabet, vocabulary, grammar).
- Understand how regular grammars relate to finite automata and how to go from one representation to the other.
- Implement a `Grammar` type that encodes the given variant’s regular grammar.
- Implement a method that generates valid strings from the language of the grammar.
- Implement a conversion from `Grammar` to `FiniteAutomaton`.
- Implement a method on the finite automaton that checks whether a given string is accepted.

## Implementation description

The solution is organized around two main Python classes: `Grammar` and `FiniteAutomaton`, plus a small `main.py` script that demonstrates how they work together. The implementation directly encodes the grammar from Variant 11 and then builds an equivalent finite automaton from it.

**Grammar**

The `Grammar` class stores the sets of non-terminals, terminals, the production rules, and the start symbol. The productions are represented in a right-linear form where each rule is a pair consisting of a terminal and an optional next non-terminal (for example `("a", "B")` for `A → aB` and `("b", None)` for `A → b`). The constructor validates that all symbols are consistent with the declared non-terminals and terminals.

The `generate_string` method uses random derivation starting from the start symbol and repeatedly applies one of the available productions for the current non-terminal. At each step it appends the terminal from the chosen rule to a list of output symbols and moves to the next non-terminal until it reaches a rule that does not produce any further non-terminal. A maximum number of steps is enforced to avoid infinite loops in grammars with cycles, and if that limit is exceeded the derivation is restarted.

The `generate_n_strings` method is a simple helper that calls `generate_string` multiple times and returns a list of generated words. The helper function `build_variant_11_grammar` instantiates a `Grammar` object with the exact sets and productions required by Variant 11.

**FiniteAutomaton**

The `FiniteAutomaton` class represents the 5-tuple \{Q, Σ, δ, q₀, F\}. Its constructor receives the states, alphabet, transition function, start state, and final states, and normalizes the transitions so that every transition key `(state, symbol)` maps to a set of possible destination states, supporting a non-deterministic finite automaton (NFA). A private `_validate` method checks that the transitions and states are consistent with the given sets.

The method `string_belongs_to_language` runs an NFA simulation: it keeps track of the current set of possible states, then for each character in the input word it computes the set of next states reachable from any current state using that symbol. If at any point no transitions are possible, the word is rejected early. When the input is fully read, the word is accepted if at least one of the reachable states is a final state.

**Conversion from Grammar to FiniteAutomaton**

The `Grammar.to_finite_automaton` method performs the standard transformation from a right-linear grammar to an equivalent finite automaton. Each non-terminal becomes a state of the automaton and a fresh extra final state is added. For every production of the form `A → aB`, the method creates a transition from state `A` to state `B` on symbol `a`. For productions of the form `A → a` (that do not continue with another non-terminal), the method creates a transition from state `A` to the extra final state on the symbol `a`.

**Main client**

The `main.py` file acts as a client that wires everything together. It builds the variant 11 grammar, generates several words from it, prints them, converts the grammar to a finite automaton, and then checks whether each generated word and several manually chosen test words are accepted by the automaton. This demonstrates that the implementation of the grammar, the conversion, and the automaton are consistent.

## Code snippets

**Grammar constructor and generation**

```python
class Grammar:
    def __init__(
        self,
        non_terminals: Iterable[NonTerminal],
        terminals: Iterable[Terminal],
        productions: Dict[NonTerminal, List[ProductionRHS]],
        start_symbol: NonTerminal,
        max_derivation_steps: int = 20,
    ) -> None:
        self.non_terminals = set(non_terminals)
        self.terminals = set(terminals)
        self.productions: Dict[NonTerminal, List[ProductionRHS]] = productions
        self.start_symbol = start_symbol
        self.max_derivation_steps = max_derivation_steps

    def generate_string(self, rng: Optional[random.Random] = None) -> str:
        if rng is None:
            rng = random

        current_nonterminal: Optional[NonTerminal] = self.start_symbol
        derived_terminals: List[Terminal] = []
        steps = 0

        while current_nonterminal is not None:
            steps += 1
            if steps > self.max_derivation_steps:
                current_nonterminal = self.start_symbol
                derived_terminals = []
                steps = 0
                continue

            options = self.productions.get(current_nonterminal)
            if not options:
                current_nonterminal = self.start_symbol
                derived_terminals = []
                steps = 0
                continue

            terminal, next_nonterminal = rng.choice(options)
            derived_terminals.append(terminal)
            current_nonterminal = next_nonterminal

        return "".join(derived_terminals)
```

**Conversion from Grammar to FiniteAutomaton**

```python
    def to_finite_automaton(self) -> FiniteAutomaton:
        states = set(self.non_terminals)
        alphabet = set(self.terminals)
        start_state = self.start_symbol

        final_state = "F"
        while final_state in states:
            final_state = final_state + "_f"
        states.add(final_state)
        final_states = {final_state}

        from typing import Set, Tuple
        transitions: Dict[Tuple[str, str], Set[str]] = {}

        for head, rhss in self.productions.items():
            for terminal, next_nonterminal in rhss:
                if next_nonterminal is None:
                    src, dst = head, final_state
                else:
                    src, dst = head, next_nonterminal

                key = (src, terminal)
                if key not in transitions:
                    transitions[key] = set()
                transitions[key].add(dst)

        return FiniteAutomaton(
            states=states,
            alphabet=alphabet,
            transitions=transitions,
            start_state=start_state,
            final_states=final_states,
        )
```

**FiniteAutomaton membership check**

```python
class FiniteAutomaton:
    def string_belongs_to_language(self, input_string: str) -> bool:
        current_states: Set[str] = {self.start_state}

        for ch in input_string:
            if ch not in self.alphabet:
                return False

            next_states: Set[str] = set()
            for state in current_states:
                dests = self.transitions.get((state, ch))
                if dests:
                    next_states.update(dests)

            if not next_states:
                return False

            current_states = next_states

        return any(state in self.final_states for state in current_states)
```

**main.py**

```python
from grammar import build_variant_11_grammar


def main() -> None:
    grammar = build_variant_11_grammar()

    print("Generating 5 words using the regular grammar:")
    words = grammar.generate_n_strings(5)
    for i, w in enumerate(words, start=1):
        print(f"  {i}. {w}")

    automaton = grammar.to_finite_automaton()

    print("\nChecking if the generated words are accepted by the finite automaton:")
    for w in words:
        print(f"  {w} -> {automaton.string_belongs_to_language(w)}")

    test_words = ["ab", "bb", "baab", "ac", "bcbc", "baaab"]
    print("\nManual tests for membership:")
    for w in test_words:
        print(f"  {w} -> {automaton.string_belongs_to_language(w)}")


if __name__ == "__main__":
    main()
```

## Conclusions / Results
Running main.py gives the following console output:
```
Generating 5 words using the regular grammar:
  1. abaaaab
  2. babbb
  3. abb
  4. bcaacabcaabaaab
  5. abb

FiniteAutomaton(states={'B', 'S', 'F', 'D'}, alphabet={'b', 'c', 'a'}, start_state=S, final_states={'F'})

Checking if the generated words are accepted by the finite automaton:
  abaaaab -> True
  babbb -> True
  abb -> True
  bcaacabcaabaaab -> True
  abb -> True

Manual tests for membership:
  ab -> False
  bb -> False
  baab -> False
  abab -> True
  ac -> False
  bcbc -> False
  baaab -> False
```
The implemented solution models the given Variant 11 regular grammar and converts it into an equivalent finite automaton. The program can generate valid words from the language and then verify that both randomly generated and manually chosen test words are either accepted or rejected by the automaton according to the formal definition. This exercise showed how theory about grammars and automata can be turned into concrete, testable code.

## References

- https://else.fcim.utm.md/pluginfile.php/110457/mod_resource/content/0/Theme_1.pdf
- Python official documentation: `typing` module and basic data structures.