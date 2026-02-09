from grammar import build_variant_11_grammar


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


if __name__ == "__main__":
    main()

