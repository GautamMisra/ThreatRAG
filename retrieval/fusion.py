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

    query = "JWT token theft"

    dense_retriever = DenseRetriever()
    sparse_retriever = SparseRetriever()

    dense_results = dense_retriever.search(query, top_k=5)
    sparse_results = sparse_retriever.search(query, top_k=5)

    fused_results = reciprocal_rank_fusion(
        dense_results,
        sparse_results
    )

    print("\n========== RRF RESULTS ==========")

    for rank, result in enumerate(fused_results[:5], start=1):
        chunk = result["chunk"]

        print(f"\nRank {rank}")
        print("ID:", chunk["id"])
        print("Source:", chunk["source"])
        print("Title:", chunk["title"])
        print("RRF Score:", result["score"])

    print("\n=================================")