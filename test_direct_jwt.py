
from retrieval.dense_retriever import DenseRetriever
from retrieval.sparse_retriever import SparseRetriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker

queries = [
    ("JWT token validation", "OWASP"),
    ("JWT authentication token signature verification", "OWASP"),
    ("JWT token theft", "MITRE_ATT&CK"),
]

dense = DenseRetriever()
sparse = SparseRetriever()
reranker = Reranker()


def print_results(label, results):
    print(f"\n{label}:")

    if not results:
        print("  No results")
        return

    for r in results:
        print("  Result keys:", list(r.keys()))

        # Support either a nested chunk or a flat result
        c = r.get("chunk", r)

        print(
            "  ID:", c.get("id", c.get("chunk_id", "N/A")),
            "| Title:", c.get("title", "N/A"),
            "| Score:", r.get("score", "N/A")
        )


for query, source in queries:
    print("\n" + "=" * 65)
    print("QUERY:", query)
    print("SOURCE:", source)

    d = dense.search(query, top_k=5, source=source)
    s = sparse.search(query, top_k=5, source=source)

    print_results("DENSE", d)
    print_results("BM25", s)

    fused = reciprocal_rank_fusion(d, s)
    print_results("FUSED", fused)

    reranked = reranker.rerank(query, fused[:10], top_k=5)
    print_results("RERANKED", reranked)


