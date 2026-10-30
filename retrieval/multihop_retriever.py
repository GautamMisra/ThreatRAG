from retrieval.dense_retriever import DenseRetriever
from retrieval.sparse_retriever import SparseRetriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker
from generation.query_expansion import expand_query


class MultiHopRetriever:
    def __init__(self):
        self.dense = DenseRetriever()
        self.sparse = SparseRetriever()
        self.reranker = Reranker()

    def _get_relevance_adjustment(self, chunk, component, tech):
        text = " ".join([
            str(chunk.get("title", "")),
            str(chunk.get("text", "")),
            str(chunk.get("content", "")),
            str(chunk.get("description", "")),
        ]).lower()

        tech_lower = str(tech).lower().strip()

        if tech_lower not in {"jwt", "json web token", "json web tokens"}:
            return 0.0

        chunk_id = str(chunk.get("id", "")).lower()

        adjustment = 0.0

        # 1. Stronger evidence for application-token and web-credential threats.
        strong_attack_terms = [
            "steal application access token",
            "stolen application access token",
            "application access tokens",
            "forge web credentials",
            "forged web credentials",
        ]

        if any(term in text for term in strong_attack_terms):
            adjustment += 0.003

        # 2. Relevant authentication and authorization evidence.
        auth_terms = [
            "authentication failures",
            "authentication failure",
            "session token",
            "session hijacking",
            "token validation",
            "signature validation",
            "broken access control",
        ]

        if any(term in text for term in auth_terms):
            adjustment += 0.002

        # 3. Penalize Windows OS token manipulation for a JWT component.
        # T1134 describes OS-level access-token manipulation, not JWT handling.
        windows_token_terms = [
            "windows access token",
            "windows uses access tokens",
            "windows security context",
            "security context associated with",
            "running process",
            "make and impersonate token",
            "rdp hijacking",
            "built-in windows api",
        ]

        is_windows_token_technique = (
            "attack-t1134" in chunk_id
            or any(term in text for term in windows_token_terms)
        )

        if is_windows_token_technique:
            adjustment -= 0.005

        # 4. Reduce the priority of generic threat-modeling guidance.
        generic_terms = [
            "threat identification",
            "threat modeling technique",
            "threat modeling methodology",
        ]

        if any(term in text for term in generic_terms):
            adjustment -= 0.004

        return adjustment

    def retrieve(self, component, tech, top_k=5):
        expanded_queries = expand_query(component, tech)

        source_map = {
            "stride": "STRIDE",
            "attack": "MITRE_ATT&CK",
            "owasp": "OWASP",
        }

        candidates = {}
        rrf_k = 60

        # --------------------------------------------------
        # 1. Retrieve and rerank candidates for each hop.
        # --------------------------------------------------
        for hop, queries in expanded_queries.items():
            source = source_map.get(hop)

            if source is None:
                print(f"Skipping unknown retrieval hop: {hop}")
                continue

            print(f"\n========== {hop.upper()} HOP ==========")
            print(f"Source: {source}")

            for query in queries:
                dense_results = self.dense.search(
                    query,
                    top_k=10,
                    source=source,
                )

                sparse_results = self.sparse.search(
                    query,
                    top_k=10,
                    source=source,
                )

                fused_results = reciprocal_rank_fusion(
                    dense_results,
                    sparse_results,
                )

                reranked_results = self.reranker.rerank(
                    query,
                    fused_results[:10],
                    top_k=10,
                )

                seen_in_query = set()

                for rank, result in enumerate(
                    reranked_results,
                    start=1,
                ):
                    chunk = result.get("chunk", result)

                    chunk_id = chunk.get(
                        "id",
                        chunk.get("chunk_id"),
                    )

                    if chunk_id is None:
                        continue

                    if chunk_id in seen_in_query:
                        continue

                    seen_in_query.add(chunk_id)

                    if chunk_id not in candidates:
                        candidates[chunk_id] = {
                            "chunk": chunk,
                            "hop_scores": {},
                            "appearances": 0,
                            "hops": set(),
                            "queries": [],
                            "scores": [],
                        }

                    entry = candidates[chunk_id]

                    # RRF contribution from this query.
                    query_rrf_score = 1.0 / (rrf_k + rank)

                    # Retain contributions separately by hop.
                    entry["hop_scores"].setdefault(
                        hop, []
                    ).append(query_rrf_score)

                    entry["appearances"] += 1
                    entry["hops"].add(hop)
                    entry["queries"].append(query)

                    if result.get("score") is not None:
                        entry["scores"].append(result["score"])

        # --------------------------------------------------
        # 2. Aggregate scores across retrieval hops.
        # --------------------------------------------------
        merged_results = []

        for entry in candidates.values():
            combined_score = 0.0

            for hop_scores in entry["hop_scores"].values():
                ranked_scores = sorted(
                    hop_scores,
                    reverse=True,
                )

                if ranked_scores:
                    # Full credit for the strongest query.
                    combined_score += ranked_scores[0]

                if len(ranked_scores) > 1:
                    # Limited credit for the second strongest.
                    combined_score += 0.25 * ranked_scores[1]

            chunk = entry["chunk"]

            # --------------------------------------------------
            # 3. Apply technology-aware relevance adjustment.
            # --------------------------------------------------
            relevance_adjustment = self._get_relevance_adjustment(
                chunk,
                component,
                tech,
            )

            adjusted_score = combined_score + relevance_adjustment

            merged_results.append({
                "chunk": chunk,
                "score": (
                    max(entry["scores"])
                    if entry["scores"]
                    else None
                ),
                "combined_score": combined_score,
                "relevance_adjustment": relevance_adjustment,
                "adjusted_score": adjusted_score,
                "appearances": entry["appearances"],
                "hops": sorted(entry["hops"]),
                "queries": entry["queries"],
            })

        # --------------------------------------------------
        # 4. Rank using the adjusted score.
        # --------------------------------------------------
        merged_results.sort(
            key=lambda result: result["adjusted_score"],
            reverse=True,
        )

        # --------------------------------------------------
        # 5. Display final ranking and score breakdown.
        # --------------------------------------------------
        print("\n========== FINAL AGGREGATED RESULTS ==========")
        print(f"Component: {component}")
        print(f"Technology: {tech}")

        for rank, result in enumerate(
            merged_results[:top_k],
            start=1,
        ):
            chunk = result["chunk"]

            print(
                f"{rank:02}. "
                f"{chunk.get('id', chunk.get('chunk_id'))} | "
                f"{chunk.get('title')} | "
                f"base={result['combined_score']:.6f} | "
                f"adjustment="
                f"{result['relevance_adjustment']:+.6f} | "
                f"adjusted={result['adjusted_score']:.6f} | "
                f"appearances={result['appearances']} | "
                f"hops={result['hops']}"
            )

        return merged_results[:top_k]

