from grammar import (
    build_variant_11_grammar,
    finite_automaton_to_grammar,
)
from finite_automaton import build_variant_11_automaton


def main():
    grammar = build_variant_11_grammar()

    print("Generating 5 words using the regular grammar:")
    words = grammar.generate_n_strings(5)
    for i, w in enumerate(words, start=1):
        print(f"  {i}. {w}")

    automaton = grammar.to_finite_automaton()

    print("\nChecking if the generated words are accepted by the finite automaton:")
    for w in words:
        print(f"  {w} -> {automaton.string_belongs_to_language(w)}")

    # Some additional manual tests
    test_words = ["ab", "bb", "baab", "abab", "ac", "bcbc", "baaab"]
    print("\nManual tests for membership:")
    for w in test_words:
        print(f"  {w} -> {automaton.string_belongs_to_language(w)}")

    print("\nChomsky type of the grammar:", grammar.classify_chomsky_type())

    # Variant 11 finite automaton from the second lab
    variant_fa = build_variant_11_automaton()
    print("\nVariant 11 FA is deterministic?", variant_fa.is_deterministic())

    dfa = variant_fa.to_deterministic()
    print("Converted DFA is deterministic?", dfa.is_deterministic())

    rg_from_fa = finite_automaton_to_grammar(variant_fa)
    print("Grammar derived from Variant 11 FA is classified as:",
          rg_from_fa.classify_chomsky_type())


if __name__ == "__main__":
    main()

