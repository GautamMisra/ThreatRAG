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
        print("Building BM25 indexes...")

        self.chunks = load_chunks()

        self.source_chunks = {
            "STRIDE": [],
            "OWASP": [],
            "MITRE_ATT&CK": []
        }

        for chunk in self.chunks:
            self.source_chunks[chunk["source"]].append(chunk)

        self.bm25_indexes = {}

        for source, chunks in self.source_chunks.items():
            documents = [
                tokenize(chunk["text"])
                for chunk in chunks
            ]

            self.bm25_indexes[source] = BM25Okapi(documents)

        print("BM25 indexes built.")


    def search(self, query, top_k=10, source=None):

        query_tokens = tokenize(query)

        if source:
            chunks = self.source_chunks[source]
            bm25 = self.bm25_indexes[source]
        else:
            chunks = self.chunks

            documents = [
                tokenize(chunk["text"])
                for chunk in chunks
            ]

            bm25 = BM25Okapi(documents)

        scores = bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []

        for index in ranked_indices:
            if scores[index] <= 0:
                continue

            results.append({
                "chunk": chunks[index],
                "score": float(scores[index])
            })

            if len(results) >= top_k:
                break

        return results


if __name__ == "__main__":

    retriever = SparseRetriever()

    query = "JWT token theft auth service"

    results = retriever.search(query, top_k=5, source="MITRE_ATT&CK")

    print("\n========== BM25 RESULTS ==========")

    for rank, result in enumerate(results, start=1):

        chunk = result["chunk"]

        print(f"\nRank {rank}")
        print("ID:", chunk["id"])
        print("Source:", chunk["source"])
        print("Title:", chunk["title"])
        print("Score:", result["score"])

    print("\n==================================")