from dense_retriever import DenseRetriever
from sparse_retriever import SparseRetriever
from fusion import reciprocal_rank_fusion
from reranker import Reranker


def build_subqueries(component, tech):
    return {
        "stride": f"{component} {tech} STRIDE threats",
        "attack": f"{component} {tech} MITRE ATT&CK techniques",
        "owasp": f"{component} {tech} OWASP security guidance"
    }


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

        for hop, query in subqueries.items():

            print(f"\n========== {hop.upper()} HOP ==========")
            print("Query:", query)

            # 1. Dense retrieval
            dense_results = self.dense.search(
                query,
                top_k=10
            )

            # 2. BM25 retrieval
            sparse_results = self.sparse.search(
                query,
                top_k=10
            )

            # 3. RRF fusion
            fused_results = reciprocal_rank_fusion(
                dense_results,
                sparse_results
            )

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

        return all_results


if __name__ == "__main__":

    retriever = MultiHopRetriever()

    results = retriever.retrieve(
        component="auth service",
        tech="JWT",
        top_k=5
    )

    print("\n\n========== ALL MULTI-HOP RESULTS ==========")

    for rank, result in enumerate(results, start=1):

        chunk = result["chunk"]

        print(f"\nRank {rank}")
        print("Hop:", result["hop"])
        print("ID:", chunk["id"])
        print("Source:", chunk["source"])
        print("Title:", chunk["title"])
        print("Score:", result["score"])

    print("\n===========================================")