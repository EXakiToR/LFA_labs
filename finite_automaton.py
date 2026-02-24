
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

    def is_deterministic(self) -> bool:
        """
        An automaton is deterministic if for every (state, symbol) pair
        there is at most one destination state.
        """
        for (_, _), dests in self.transitions.items():
            if len(dests) > 1:
                return False
        return True

    def to_deterministic(self) -> "FiniteAutomaton":
        """
        Convert this (ε-free) NFA to an equivalent DFA using the
        standard subset construction.
        """
        from collections import deque

        # Each DFA state is a subset of NFA states, encoded as a string.
        def subset_name(subset) -> str:
            subset = sorted(subset)
            if not subset:
                return "{}"
            return "{" + ",".join(subset) + "}"

        start_subset = frozenset({self.start_state})
        subset_to_name: Dict[frozenset, str] = {
            start_subset: subset_name(start_subset)
        }

        queue = deque([start_subset])
        dfa_transitions: Dict[Tuple[str, str], Set[str]] = {}

        while queue:
            subset = queue.popleft()
            src_name = subset_to_name[subset]

            for symbol in self.alphabet:
                dest_subset = set()
                for state in subset:
                    dests = self.transitions.get((state, symbol))
                    if dests:
                        dest_subset.update(dests)

                if not dest_subset:
                    continue

                dest_frozen = frozenset(dest_subset)
                if dest_frozen not in subset_to_name:
                    subset_to_name[dest_frozen] = subset_name(dest_subset)
                    queue.append(dest_frozen)

                dst_name = subset_to_name[dest_frozen]
                dfa_transitions.setdefault((src_name, symbol), set()).add(dst_name)

        dfa_states = set(subset_to_name.values())
        dfa_start_state = subset_to_name[start_subset]
        dfa_final_states = {
            subset_to_name[s]
            for s in subset_to_name
            if any(state in self.final_states for state in s)
        }

        return FiniteAutomaton(
            states=dfa_states,
            alphabet=self.alphabet,
            transitions=dfa_transitions,
            start_state=dfa_start_state,
            final_states=dfa_final_states,
        )


def build_variant_11_automaton() -> FiniteAutomaton:
    """
    Build the finite automaton for Variant 11:

      Q = {q0, q1, q2, q3}
      Σ = {a, b, c}
      F = {q3}
      δ(q0, a) = q1
      δ(q1, b) = q2
      δ(q2, c) = q0
      δ(q1, a) = q3
      δ(q0, b) = q2
      δ(q2, c) = q3

    Note that δ(q2, c) has two destinations (q0, q3), which makes this
    automaton non-deterministic.
    """
    states = {"q0", "q1", "q2", "q3"}
    alphabet = {"a", "b", "c"}
    transitions: Dict[Tuple[str, str], Set[str]] = {
        ("q0", "a"): {"q1"},
        ("q1", "b"): {"q2"},
        ("q2", "c"): {"q0", "q3"},
        ("q1", "a"): {"q3"},
        ("q0", "b"): {"q2"},
    }
    start_state = "q0"
    final_states = {"q3"}

    return FiniteAutomaton(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state=start_state,
        final_states=final_states,
    )

