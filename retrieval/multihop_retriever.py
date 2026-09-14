from dense_retriever import DenseRetriever
from sparse_retriever import SparseRetriever
from fusion import reciprocal_rank_fusion
from reranker import Reranker


def build_subqueries(component, tech):
    return {
        "stride": {
            "query": f"{component} {tech} threats attacks risks",
            "source": "STRIDE"
        },

        "attack": {
            "query": f"{component} {tech} attacks adversary techniques",
            "source": "MITRE_ATT&CK"
        },

        "owasp": {
            "query": f"{component} {tech} vulnerabilities security risks",
            "source": "OWASP"
        }
    }

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

        subqueries = build_subqueries(component, tech)

        all_results = []

        for hop, hop_info in subqueries.items():

            query = hop_info["query"]
            source = hop_info["source"]

            print(f"\n========== {hop.upper()} HOP ==========")
            print("Query:", query)
            print("Source:", source)

            # 1. Dense retrieval
            dense_results = self.dense.search(
                query,
                top_k=10,
                source=source
            )

            # 2. BM25 retrieval
            sparse_results = self.sparse.search(
                query,
                top_k=10,
                source=source
            )

            print("\n----- DENSE RESULTS -----")

            for rank, result in enumerate(dense_results, start=1):
                print(
                    f"Rank {rank} | "
                    f"ID: {result['id']} | "
                    f"Title: {result['title']} | "
                    f"Dense Score: {result['score']}"
                )

            print("\n----- BM25 RESULTS -----")

            for rank, result in enumerate(sparse_results, start=1):
                chunk = result["chunk"]

                print(
                    f"Rank {rank} | "
                    f"ID: {chunk['id']} | "
                    f"Title: {chunk['title']} | "
                    f"BM25 Score: {result['score']}"
                )

            # 3. RRF fusion
            fused_results = reciprocal_rank_fusion(
                dense_results,
                sparse_results
            )

            print("\n----- RRF RESULTS -----")

            for rank, result in enumerate(fused_results[:10], start=1):
                chunk = result["chunk"]

                print(
                    f"Rank {rank} | "
                    f"ID: {chunk['id']} | "
                    f"Title: {chunk['title']} | "
                    f"RRF Score: {result['score']}"
                )

            print("-----------------------")

            # 4. Cross-encoder reranking
            reranked_results = self.reranker.rerank(
                query,
                fused_results[:10],
                top_k=top_k
            )

        

            # Store hop information
            for result in reranked_results:
                result["hop"] = hop
                all_results.append(result)

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