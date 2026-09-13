import os

import psycopg2
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer


load_dotenv()


MODEL_NAME = "BAAI/bge-base-en-v1.5"

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "database": "ThreatRAG",
    "user": "ThreatRAG",
    "password": os.getenv("POSTGRES_PASSWORD"),
}


class DenseRetriever:

    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query, top_k=5):

        print(f"Searching for: {query}")

        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query_sql = """
            SELECT
                id,
                source,
                title,
                text,
                tags,
                1 - (embedding <=> %s::vector) AS similarity
            FROM chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """

        embedding = query_embedding.tolist()

        cursor.execute(
            query_sql,
            (embedding, embedding, top_k)
        )

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        results = []

        for row in rows:
            results.append({
                "id": row[0],
                "source": row[1],
                "title": row[2],
                "text": row[3],
                "tags": row[4],
                "score": float(row[5])
            })

        return results


if __name__ == "__main__":

    retriever = DenseRetriever()

    query = "JWT token theft"

    results = retriever.search(query, top_k=5)

    print("\n========== DENSE RESULTS ==========")

    for rank, result in enumerate(results, start=1):

        print(f"\nRank {rank}")
        print("ID:", result["id"])
        print("Source:", result["source"])
        print("Title:", result["title"])
        print("Similarity:", result["score"])

    print("\n===================================")