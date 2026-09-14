def reciprocal_rank_fusion(dense_results, sparse_results, k=60):
    scores = {}
    chunks = {}

    # Add dense retrieval rankings
    for rank, result in enumerate(dense_results, start=1):
        chunk_id = result["id"]

        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank)
        chunks[chunk_id] = result

    # Add BM25 retrieval rankings
    for rank, result in enumerate(sparse_results, start=1):
        chunk_id = result["chunk"]["id"]

        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank)
        chunks[chunk_id] = result["chunk"]

    # Sort chunks by their RRF score
    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    results = []

    for chunk_id in ranked_ids:
        results.append({
            "chunk": chunks[chunk_id],
            "score": scores[chunk_id]
        })

    return results


if __name__ == "__main__":
    from dense_retriever import DenseRetriever
    from sparse_retriever import SparseRetriever
    from reranker import Reranker

    query = "SQL injection"

    # -----------------------------
    # 1. Initialize retrievers
    # -----------------------------

    dense_retriever = DenseRetriever()
    sparse_retriever = SparseRetriever()

    # -----------------------------
    # 2. Retrieve candidates
    # -----------------------------

    dense_results = dense_retriever.search(
        query,
        top_k=10
    )

    sparse_results = sparse_retriever.search(
        query,
        top_k=10
    )

    # -----------------------------
    # 3. Fuse using RRF
    # -----------------------------

    fused_results = reciprocal_rank_fusion(
        dense_results,
        sparse_results
    )

    print("\n========== RRF RESULTS ==========")

    for rank, result in enumerate(
        fused_results[:10],
        start=1
    ):
        chunk = result["chunk"]

        print(f"\nRank {rank}")
        print("ID:", chunk["id"])
        print("Title:", chunk["title"])
        print("RRF Score:", result["score"])

    # -----------------------------
    # 4. Rerank using cross-encoder
    # -----------------------------

    reranker = Reranker()

    reranked_results = reranker.rerank(
        query,
        fused_results[:10],
        top_k=5
    )

print("\n====== RERANKED RESULTS ======")

for rank, result in enumerate(reranked_results, start=1):
    chunk = result["chunk"]

    print(
        f"{rank}. {chunk['id']} | "
        f"{chunk['title']} | "
        f"Score: {result['score']:.4f}"
    )

print("\n==============================")