import json
from pathlib import Path

# pyrefly: ignore [missing-import]
from rank_bm25 import BM25Okapi


PROCESSED_DIR = Path("data/processed")


def load_chunks():
    chunks = []

    for file in PROCESSED_DIR.glob("*_chunks.json"):
        print(f"Loading {file}...")

        with open(file, "r", encoding="utf-8") as f:
            file_chunks = json.load(f)

        chunks.extend(file_chunks)

    print(f"Loaded {len(chunks)} total chunks.")

    return chunks


def tokenize(text):
    return text.lower().split()


class SparseRetriever:

    def __init__(self):
        print("Building BM25 index...")

        self.chunks = load_chunks()

        documents = [
            tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(documents)

        print("BM25 index built.")


    def search(self, query, top_k=10):

        query_tokens = tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []

        for index in ranked_indices:
            results.append({
                "chunk": self.chunks[index],
                "score": float(scores[index])
            })

        return results


if __name__ == "__main__":

    retriever = SparseRetriever()

    query = "JWT token theft"

    results = retriever.search(query, top_k=5)

    print("\n========== BM25 RESULTS ==========")

    for rank, result in enumerate(results, start=1):

        chunk = result["chunk"]

        print(f"\nRank {rank}")
        print("ID:", chunk["id"])
        print("Source:", chunk["source"])
        print("Title:", chunk["title"])
        print("Score:", result["score"])

    print("\n==================================")