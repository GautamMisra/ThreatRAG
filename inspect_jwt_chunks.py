from retrieval.dense_retriever import DenseRetriever
from retrieval.sparse_retriever import SparseRetriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker

tests = [
    ("JWT token validation", "OWASP"),
    ("JWT authentication token signature verification", "OWASP"),
    ("JWT token theft", "MITRE_ATT&CK"),
]

dense = DenseRetriever()
sparse = SparseRetriever()
reranker = Reranker()

for query, source in tests:
    print("\n" + "=" * 80)
    print("QUERY:", query, "| SOURCE:", source)

    d = dense.search(query, top_k=5, source=source)
    s = sparse.search(query, top_k=5, source=source)

    fused = reciprocal_rank_fusion(d, s)
    reranked = reranker.rerank(query, fused[:10], top_k=3)

    for result in reranked:
        chunk = result.get("chunk", result)

        print("\nID:", chunk.get("id", chunk.get("chunk_id")))
        print("TITLE:", chunk.get("title"))
        print("SOURCE:", chunk.get("source"))
        print("SCORE:", result.get("score"))
        print("TEXT:")
        print(chunk.get("text", "NO TEXT FIELD FOUND")[:1800])
        print("-" * 80)