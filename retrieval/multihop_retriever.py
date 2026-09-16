from retrieval.dense_retriever import DenseRetriever
from retrieval.sparse_retriever import SparseRetriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker

from generation.query_expansion import expand_query


def normalize_scores(results):
    if not results:
        return results

    scores = [result["score"] for result in results]

    min_score = min(scores)
    max_score = max(scores)

    # If all scores are identical
    if max_score == min_score:
        for result in results:
            result["norm_score"] = 1.0
        return results

    for result in results:
        result["norm_score"] = (
            (result["score"] - min_score)
            / (max_score - min_score)
        )

    return results

def combined_score(result, hop_bonus=0.15):
    return (
        result["norm_score"]
        + hop_bonus * (len(result["hops"]) - 1)
    )

def merge_and_dedupe(results):
    merged = {}

    for result in results:
        chunk_id = result["chunk"]["id"]

        if chunk_id not in merged:
            merged[chunk_id] = {
                "chunk": result["chunk"],
                "score": result["score"],
                "hops": [result["hop"]]
            }

        else:
            merged[chunk_id]["hops"].append(result["hop"])

            # Keep the strongest cross-encoder score
            if result["score"] > merged[chunk_id]["score"]:
                merged[chunk_id]["score"] = result["score"]

    merged_results = list(merged.values())

    # Give a small bonus when the same chunk
    # is retrieved by multiple hops
    for result in merged_results:
        result["combined_score"] = (
            result["score"]
            + 0.15 * (len(result["hops"]) - 1)
        )

    merged_results.sort(
        key=lambda x: x["combined_score"],
        reverse=True
    )

    return merged_results

class MultiHopRetriever:

    def __init__(self):
        print("Initializing multi-hop retriever...")

        self.dense = DenseRetriever()
        self.sparse = SparseRetriever()
        self.reranker = Reranker()

        print("Multi-hop retriever ready.")

    def retrieve(self, component, tech, top_k=5):

        expanded_queries = expand_query(component, tech)

        source_map = {
            "stride": "STRIDE",
            "attack": "MITRE_ATT&CK",
            "owasp": "OWASP"
        }

        all_results = []

        for hop, queries in expanded_queries.items():

            source = source_map[hop]

            print(f"\n========== {hop.upper()} HOP ==========")
            print("Source:", source)

            hop_results = []

            for query in queries:

                print("\nSearching for:", query)

                # Dense retrieval
                dense_results = self.dense.search(
                    query,
                    top_k=10,
                    source=source
                )

                # BM25 retrieval
                sparse_results = self.sparse.search(
                    query,
                    top_k=10,
                    source=source
                )

                # RRF
                fused_results = reciprocal_rank_fusion(
                    dense_results,
                    sparse_results
                )

                # Cross-encoder
                reranked_results = self.reranker.rerank(
                    query,
                    fused_results[:10],
                    top_k=top_k
                )

                hop_results.extend(reranked_results)

            # Keep best result for each chunk within this hop
            best_results = {}

            for result in hop_results:

                chunk_id = result["chunk"]["id"]

                if (
                    chunk_id not in best_results
                    or result["score"] > best_results[chunk_id]["score"]
                ):
                    best_results[chunk_id] = result

            for result in best_results.values():
                result["hop"] = hop
                all_results.append(result)

        # Your existing merge_and_dedupe()
        merged_results = merge_and_dedupe(all_results)

        return merged_results[:top_k]


if __name__ == "__main__":

    retriever = MultiHopRetriever()

    results = retriever.retrieve(
        component="web API",
        tech="SQL Injection",
        top_k=5
    )

    print("\n\n========== MERGED MULTI-HOP RESULTS ==========")

    print("Total unique chunks:", len(results))

    for rank, result in enumerate(results, start=1):

        chunk = result["chunk"]

        print(f"\nRank {rank}")
        print("ID:", chunk["id"])
        print("Source:", chunk["source"])
        print("Title:", chunk["title"])
        print("Hops:", ", ".join(result["hops"]))
        print("Raw Score:", result["score"])
       

    print("\n===============================================")