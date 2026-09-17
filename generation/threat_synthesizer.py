from retrieval.multihop_retriever import MultiHopRetriever
from generation.ollama_client import OllamaClient
from generation.prompt_templates import build_synthesis_prompt
from generation.grounding import validate_grounding


class ThreatSynthesizer:

    def __init__(self):

        print("Initializing threat synthesizer...")

        self.retriever = MultiHopRetriever()
        self.ollama = OllamaClient()

        print("Threat synthesizer ready.")

    def synthesize(self, component, technology, top_k=5):

        print("\n========================================")
        print("STARTING THREAT SYNTHESIS")
        print("========================================")

        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.retriever.retrieve(
            component=component,
            tech=technology,
            top_k=top_k
        )

        print("\n========== RETRIEVED CONTEXT ==========")

        for rank, result in enumerate(retrieved_chunks, start=1):

            chunk = result["chunk"]

            print(f"\nRank {rank}")
            print("ID:", chunk["id"])
            print("Source:", chunk["source"])
            print("Title:", chunk["title"])

        # Step 2: Build grounded synthesis prompt
        prompt = build_synthesis_prompt(
            component=component,
            technology=technology,
            retrieved_chunks=retrieved_chunks
        )

        print("\n========== GENERATING THREAT MODEL ==========")

        # Step 3: Ask Ollama to generate structured JSON
        result = self.ollama.generate_json(
            prompt,
            temperature=0.2
        )

        # Validate generated citations against retrieved chunks
        validated_result, rejected_threats = validate_grounding(
            result,
            retrieved_chunks
        )

        # Display rejected threats for debugging
        if rejected_threats:

            print("\n========== REJECTED UNGROUNDED THREATS ==========")

            for threat in rejected_threats:

                print("Rejected:", threat.get("threat"))
                print("Source ID:", threat.get("source_id"))
                print("Source:", threat.get("source"))
                print("Source Title:", threat.get("source_title"))
                print("Reason:", threat.get("grounding_reason"))
                print()

            print("==================================================")

        return validated_result


if __name__ == "__main__":

    synthesizer = ThreatSynthesizer()

    result = synthesizer.synthesize(
        component="web API",
        technology="SQL Injection",
        top_k=5
    )

    print("\n\n========== FINAL THREAT MODEL ==========")

    print(result)

    print("\n========================================")