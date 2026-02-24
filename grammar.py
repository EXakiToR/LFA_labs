
import random
from typing import Dict, Iterable, List, Optional, Tuple

from finite_automaton import FiniteAutomaton

# Type aliases for readability
Terminal = str
NonTerminal = str
# Each right-hand side is: a single terminal symbol and an optional next non-terminal
ProductionRHS = Tuple[Terminal, Optional[NonTerminal]]


class Grammar:
    """
    Regular grammar model: {V_N, V_T, P, S}.

    This implementation assumes a right-linear grammar where every production
    is of the form A -> aB or A -> a, where:
      - A and B are non-terminals
      - a is a terminal symbol
    """

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

        self._validate()

    def _validate(self) -> None:
        if self.start_symbol not in self.non_terminals:
            raise ValueError("Start symbol must be one of the non-terminals.")

        for head, rhss in self.productions.items():
            if head not in self.non_terminals:
                raise ValueError(f"Production head {head} is not a non-terminal.")
            if not rhss:
                raise ValueError(f"No right-hand sides provided for {head}.")
            for terminal, next_nonterminal in rhss:
                if not terminal:
                    raise ValueError(f"Empty terminal in production for {head}.")
                if any(ch not in self.terminals for ch in terminal):
                    raise ValueError(
                        f"Terminal {terminal} in production {head} "
                        "is not a valid terminal symbol."
                    )
                if next_nonterminal is not None and next_nonterminal not in self.non_terminals:
                    raise ValueError(
                        f"Non-terminal {next_nonterminal} in production for {head} "
                        "is not defined in V_N."
                    )

    def generate_string(self, rng: Optional[random.Random] = None) -> str:
        """
        Generate a single string in the language using random derivation.

        Because regular grammars can have cycles, a maximum number of
        derivation steps is enforced. If this limit is reached, the
        derivation is restarted from the start symbol.
        """
        if rng is None:
            rng = random

        current_nonterminal: Optional[NonTerminal] = self.start_symbol
        derived_terminals: List[Terminal] = []
        steps = 0

        while current_nonterminal is not None:
            steps += 1
            if steps > self.max_derivation_steps:
                # Restart derivation to avoid infinite loops
                current_nonterminal = self.start_symbol
                derived_terminals = []
                steps = 0
                continue

            options = self.productions.get(current_nonterminal)
            if not options:
                # Dead end in the derivation, restart
                current_nonterminal = self.start_symbol
                derived_terminals = []
                steps = 0
                continue

            terminal, next_nonterminal = rng.choice(options)
            derived_terminals.append(terminal)
            current_nonterminal = next_nonterminal

        return "".join(derived_terminals)

    def generate_n_strings(self, n: int, rng: Optional[random.Random] = None) -> List[str]:
        """
        Convenience method to generate multiple strings.
        """
        if n <= 0:
            return []
        return [self.generate_string(rng) for _ in range(n)]

    def to_finite_automaton(self) -> FiniteAutomaton:
        """
        Convert this right-linear grammar to an equivalent finite automaton.

        Standard construction:
          - Each non-terminal becomes a state.
          - Add a fresh final state F.
          - For every production A -> aB, add transition A -a-> B.
          - For every production A -> a, add transition A -a-> F.
        """
        states = set(self.non_terminals)
        alphabet = set(self.terminals)
        start_state = self.start_symbol

        # Choose a fresh name for the synthetic final state
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


def build_variant_11_grammar() -> Grammar:
    """
    Helper to build the concrete grammar for Variant 11:

      V_N = {S, B, D}
      V_T = {a, b, c}
      P   = {
              S -> aB
              S -> bB
              B -> bD
              D -> b
              D -> aD
              B -> cB
              B -> aS
            }
    """
    non_terminals = {"S", "B", "D"}
    terminals = {"a", "b", "c"}

    productions: Dict[NonTerminal, List[ProductionRHS]] = {
        "S": [("a", "B"), ("b", "B")],
        "B": [("b", "D"), ("c", "B"), ("a", "S")],
        "D": [("b", None), ("a", "D")],
    }

    return Grammar(
        non_terminals=non_terminals,
        terminals=terminals,
        productions=productions,
        start_symbol="S",
    )

