from __future__ import annotations

import random

from regular_expression_generator import RegexGenerator


def show_examples(pattern: str, title: str, n: int = 5) -> None:
    print(f"\n{title}")
    print(f"Regex: {pattern}")
    generator = RegexGenerator(pattern)
    rng = random.Random(42)
    words = generator.generate_words(n, rng=rng, max_repeat=5)
    print("Generated examples:")
    for w in words:
        print(f"  - {w}")

    explained_word, trace = generator.explain_generation(rng=random.Random(7), max_repeat=5)
    print("One traced generation:")
    print(f"  word = {explained_word}")
    print("  steps:")
    for step in trace:
        print(f"    {step}")


def main() -> None:
    variant_1_regexes = [
        "(a|b)(c|d)E+G?",
        "P(Q|R|S)T(UV|W|X)*Z+",
        "1(0|1)*2(3|4){5}36",
    ]

    for idx, pattern in enumerate(variant_1_regexes, start=1):
        show_examples(pattern, title=f"Variant 1 / Regex #{idx}")


if __name__ == "__main__":
    main()

