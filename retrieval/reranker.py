
# pyrefly: ignore [missing-import]
from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:

    def __init__(self):
        print("Loading cross-encoder model...")
        self.model = CrossEncoder(MODEL_NAME)
        print("Cross-encoder loaded.")

    def rerank(self, query, results, top_k=5):

        pairs = []

        for result in results:
            chunk = result["chunk"]

            pairs.append([
                query,
                chunk["text"]
            ])

        scores = self.model.predict(pairs)

        reranked = []

        for result, score in zip(results, scores):
            reranked.append({
                "chunk": result["chunk"],
                "score": float(score)
            })

        reranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return reranked[:top_k]


if __name__ == "__main__":

    reranker = Reranker()

    print("\nReranker loaded successfully.")