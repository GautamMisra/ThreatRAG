from retrieval.dense_retriever import DenseRetriever
from retrieval.sparse_retriever import SparseRetriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker
from generation.query_expansion import expand_query


COMPONENT = "Auth Service"
TECHNOLOGY = "JWT"
TARGET_IDS = {
    "attack-T1528",
    "attack-T1550.001",
    "attack-T1134",
    "attack-T1134.001",
    "owasp-cheatsheet-threat-identification",
    "owasp-a07",
}


def get_chunk(result):
    return result.get("chunk", result)


def get_chunk_id(result):
    chunk = get_chunk(result)
    return chunk.get("id", chunk.get("chunk_id"))


def main():
    print("Initializing retrievers...")

    dense = DenseRetriever()
    sparse = SparseRetriever()
    reranker = Reranker()

    expanded_queries = expand_query(COMPONENT, TECHNOLOGY)

    # Track how often each target appears after reranking.
    target_stats = {
        chunk_id: {"appearances": 0, "best_rank": None, "queries": []}
        for chunk_id in TARGET_IDS
    }

    for hop, queries in expanded_queries.items():
        source_map = {
            "stride": "STRIDE",
            "attack": "MITRE_ATT&CK",
            "owasp": "OWASP",
        }

        source = source_map.get(hop)

        if source is None:
            continue

        print(f"\n{'#' * 80}")
        print(f"HOP: {hop.upper()} | SOURCE: {source}")
        print(f"{'#' * 80}")

        for query in queries:
            print(f"\nQUERY: {query}")

            dense_results = dense.search(
                query, top_k=10, source=source
            )

            sparse_results = sparse.search(
                query, top_k=10, source=source
            )

            fused_results = reciprocal_rank_fusion(
                dense_results, sparse_results
            )

            reranked_results = reranker.rerank(
                query, fused_results[:10], top_k=10
            )

            print("RERANKED RESULTS:")

            for rank, result in enumerate(reranked_results, start=1):
                chunk = get_chunk(result)
                chunk_id = get_chunk_id(result)

                print(
                    f"{rank:02}. {chunk_id} | "
                    f"{chunk.get('title')} | "
                    f"score={result.get('score')}"
                )

                if chunk_id in target_stats:
                    stats = target_stats[chunk_id]
                    stats["appearances"] += 1
                    stats["queries"].append(
                        f"{query} (rank {rank})"
                    )

                    if (
                        stats["best_rank"] is None
                        or rank < stats["best_rank"]
                    ):
                        stats["best_rank"] = rank

    print(f"\n{'=' * 80}")
    print("TARGET CHUNK SUMMARY")
    print("=" * 80)

    for chunk_id, stats in target_stats.items():
        print(f"\n{chunk_id}")
        print(f"Appearances: {stats['appearances']}")
        print(f"Best rank: {stats['best_rank']}")
        for query in stats["queries"]:
            print(f"  - {query}")


if __name__ == "__main__":
    main()