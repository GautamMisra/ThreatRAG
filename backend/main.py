# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import SystemDescription
from generation.threat_synthesizer import ThreatSynthesizer


app = FastAPI(
    title="ThreatModel-RAG API",
    description="Hybrid RAG Threat Modeling Assistant",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize the threat synthesizer once when the API starts.
# This loads the retrievers, reranker, and Ollama client.
print("\n========================================")
print("INITIALIZING THREATMODEL-RAG API")
print("========================================")

synthesizer = ThreatSynthesizer()

print("========================================")
print("THREATMODEL-RAG API READY")
print("========================================\n")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ThreatModel-RAG"
    }


@app.post("/analyze")
def analyze_system(system: SystemDescription):

    print("\n========================================")
    print("RECEIVED SYSTEM ANALYSIS REQUEST")
    print("========================================")

    print("Components:", len(system.components))
    print("Data flows:", len(system.data_flows))
    print("Trust boundaries:", len(system.trust_boundaries))

    results = []

    try:

        # Analyze every component using the existing
        # Day 6 threat synthesis pipeline.
        for component in system.components:

            print("\n----------------------------------------")
            print("ANALYZING COMPONENT")
            print("----------------------------------------")
            print("Component:", component.name)
            print("Technology:", component.technology)

            threat_model = synthesizer.synthesize(
                component=component.name,
                technology=component.technology,
                top_k=5
            )

            results.append({
                "component": component.name,
                "technology": component.technology,
                "threat_model": threat_model
            })

        return {
            "status": "success",
            "components": results,
            "data_flows": [
                flow.model_dump()
                for flow in system.data_flows
            ],
            "trust_boundaries": system.trust_boundaries
        }

    except Exception as e:

        print("\nERROR DURING SYSTEM ANALYSIS:")
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Threat model generation failed: {str(e)}"
        )