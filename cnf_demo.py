from __future__ import annotations

from cnf import CNFNormalizer, build_variant_11_cfg


def main() -> None:
    grammar = build_variant_11_cfg()
    normalizer = CNFNormalizer()

    print("Initial grammar (Variant 11):")
    print(grammar.pretty())

    cnf_grammar, log = normalizer.normalize(grammar)

    print("\nNormalization log:")
    for chunk in log:
        print("\n" + chunk)

    print("\nFinal CNF grammar:")
    print(cnf_grammar.pretty())


if __name__ == "__main__":
    main()

