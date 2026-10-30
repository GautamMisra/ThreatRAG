
from generation.query_expansion import expand_query
from retrieval.dense_retriever import DenseRetriever
from retrieval.sparse_retriever import SparseRetriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker

COMPONENT = "Auth Service"
TECHNOLOGY = "JWT"

SOURCE_MAP = {
    "stride": "STRIDE",
    "attack": "MITRE_ATT&CK",
    "owasp": "OWASP",
}


def show_results(label, results):
    print(f"\n--- {label} ---")

    if not results:
        print("No results returned.")
        return

    for rank, result in enumerate(results, start=1):
        chunk = result.get("chunk", result)

        print(f"\nRank: {rank}")
        print("ID:", chunk.get("id"))
        print("Source:", chunk.get("source"))
        print("Title:", chunk.get("title"))
        print("Score:", result.get("score", "N/A"))
        print(
            "Text:",
            (
                chunk.get("text")
                or chunk.get("content")
                or chunk.get("chunk_text")
                or ""
            )[:500],
        )


def main():
    print("Initializing retrievers...")
    dense = DenseRetriever()
    sparse = SparseRetriever()
    reranker = Reranker()

    expanded = expand_query(COMPONENT, TECHNOLOGY)

    for hop, queries in expanded.items():
        source = SOURCE_MAP.get(hop)

        if source is None:
            print(f"Skipping unknown hop: {hop}")
            continue

        for query in queries:
            print("\n" + "=" * 70)
            print("HOP:", hop)
            print("SOURCE FILTER:", source)
            print("QUERY:", query)
            print("=" * 70)

            # 1. Dense retrieval alone
            dense_results = dense.search(
                query,
                top_k=5,
                source=source,
            )
            show_results("DENSE RESULTS", dense_results)

            # 2. Sparse retrieval alone
            sparse_results = sparse.search(
                query,
                top_k=5,
                source=source,
            )
            show_results("BM25 RESULTS", sparse_results)

            # 3. Fusion
            fused = reciprocal_rank_fusion(
                dense_results,
                sparse_results,
            )
            show_results("FUSED RESULTS", fused[:5])

            # 4. Reranking
            reranked = reranker.rerank(
                query,
                fused[:10],
                top_k=5,
            )
            show_results("RERANKED RESULTS", reranked)


if __name__ == "__main__":
    main()
