
from typing import Dict, Iterable, Set, Tuple


class FiniteAutomaton:
    """
    Finite automaton model: {Q, Sigma, delta, q0, F}.

    This implementation supports non-deterministic transition functions,
    but there are no ε-transitions, which is enough for regular grammars.
    """

    def __init__(
        self,
        states: Iterable[str],
        alphabet: Iterable[str],
        transitions: Dict[Tuple[str, str], Set[str]],
        start_state: str,
        final_states: Iterable[str],
    ) -> None:
        self.states: Set[str] = set(states)
        self.alphabet: Set[str] = set(alphabet)
        # Normalize transitions to use sets for destinations
        self.transitions: Dict[Tuple[str, str], Set[str]] = {
            (src, symbol): set(dests)
            for (src, symbol), dests in transitions.items()
        }
        self.start_state: str = start_state
        self.final_states: Set[str] = set(final_states)

        self._validate()

    def _validate(self) -> None:
        if self.start_state not in self.states:
            raise ValueError("Start state must be one of the states.")

        if not self.final_states.issubset(self.states):
            raise ValueError("All final states must be included in the set of states.")

        for (src, symbol), dests in self.transitions.items():
            if src not in self.states:
                raise ValueError(f"Transition from unknown state {src}.")
            if symbol not in self.alphabet:
                raise ValueError(f"Transition uses symbol {symbol} not in alphabet.")
            if not dests:
                raise ValueError("Transition must have at least one destination state.")
            if not dests.issubset(self.states):
                raise ValueError(
                    f"Transition from {src} with {symbol} "
                    "has destinations not included in the set of states."
                )

    def string_belongs_to_language(self, input_string: str) -> bool:
        """
        Check if the given input string is accepted by the automaton.
        Uses standard NFA simulation (set of current states, no ε-moves).
        """
        current_states: Set[str] = {self.start_state}

        for ch in input_string:
            if ch not in self.alphabet:
                # Contains a symbol that is not in the language alphabet
                return False

            next_states: Set[str] = set()
            for state in current_states:
                dests = self.transitions.get((state, ch))
                if dests:
                    next_states.update(dests)

            if not next_states:
                # No valid transitions for this symbol
                return False

            current_states = next_states

        # Accepted if any of the possible end states is final
        return any(state in self.final_states for state in current_states)

    def __repr__(self) -> str:
        return (
            f"FiniteAutomaton(states={self.states}, "
            f"alphabet={self.alphabet}, "
            f"start_state={self.start_state}, "
            f"final_states={self.final_states})"
        )

