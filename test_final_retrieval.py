from retrieval.multihop_retriever import MultiHopRetriever

retriever = MultiHopRetriever()

results = retriever.retrieve(
    component="Auth Service",
    tech="JWT",
    top_k=15
)

print("\n" + "=" * 80)
print("FINAL MULTIHOP RETRIEVAL RESULTS")
print("=" * 80)

for rank, result in enumerate(results, start=1):
    chunk = result.get("chunk", result)

    print(f"\nRANK: {rank}")
    print("ID:", chunk.get("id", chunk.get("chunk_id")))
    print("SOURCE:", chunk.get("source"))
    print("TITLE:", chunk.get("title"))
    print("SCORE:", result.get("score"))
    print("COMBINED SCORE:", result.get("combined_score"))
    print("HOPS:", result.get("hops", result.get("hop")))
    print("TEXT:", chunk.get("text", "")[:700])
    print("-" * 80)