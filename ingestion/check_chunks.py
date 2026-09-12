import json
from pathlib import Path


FILES = [
    Path("data/processed/stride_chunks.json"),
    Path("data/processed/attack_chunks.json"),
    Path("data/processed/owasp_chunks.json"),
]


def estimate_tokens(text):
    """
    Rough token estimate.

    This is only a sanity check.
    """
    words = text.split()

    return int(len(words) * 1.3)


def main():

    for file in FILES:

        print("\n" + "=" * 60)
        print(file)
        print("=" * 60)

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:
            chunks = json.load(f)

        token_counts = [
            estimate_tokens(chunk["text"])
            for chunk in chunks
        ]

        if not token_counts:
            print("No chunks found.")
            continue

        below_target = sum(
            tokens < 150
            for tokens in token_counts
        )

        within_target = sum(
            150 <= tokens <= 400
            for tokens in token_counts
        )

        above_target = sum(
            tokens > 400
            for tokens in token_counts
        )

        average = (
            sum(token_counts)
            / len(token_counts)
        )

        print(f"Chunks: {len(token_counts)}")
        print(f"Average: {average:.1f} tokens")
        print(f"Smallest: {min(token_counts)}")
        print(f"Largest: {max(token_counts)}")

        print("\nSize distribution:")
        print(f"Below 150:   {below_target}")
        print(f"150 - 400:   {within_target}")
        print(f"Above 400:   {above_target}")


if __name__ == "__main__":
    main()