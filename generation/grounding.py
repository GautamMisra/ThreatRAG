def validate_grounding(threat_model, retrieved_chunks):

    # Build a mapping:
    # chunk_id -> source + title
    retrieved_map = {}

    for result in retrieved_chunks:

        chunk = result["chunk"]

        chunk_id = chunk["id"]

        retrieved_map[chunk_id] = {
            "source": chunk["source"],
            "title": chunk["title"]
        }

    grounded_threats = []
    rejected_threats = []

    for threat in threat_model.get("threats", []):

        source_id = threat.get("source_id")
        source = threat.get("source")
        source_title = threat.get("source_title")

        # Check that the source_id exists
        if source_id not in retrieved_map:

            threat["grounded"] = False
            threat["grounding_reason"] = "source_id not found in retrieved chunks"

            rejected_threats.append(threat)
            continue

        retrieved_chunk = retrieved_map[source_id]

        # Check source matches the cited chunk
        if source != retrieved_chunk["source"]:

            threat["grounded"] = False
            threat["grounding_reason"] = "source does not match source_id"

            rejected_threats.append(threat)
            continue

        # Check title matches the cited chunk
        if source_title != retrieved_chunk["title"]:

            threat["grounded"] = False
            threat["grounding_reason"] = "source_title does not match source_id"

            rejected_threats.append(threat)
            continue

        # All provenance checks passed
        threat["grounded"] = True

        grounded_threats.append(threat)

    # Only return grounded threats
    threat_model["threats"] = grounded_threats

    threat_model["grounding"] = {
        "total_threats_generated": (
            len(grounded_threats) + len(rejected_threats)
        ),
        "grounded_threats": len(grounded_threats),
        "rejected_threats": len(rejected_threats)
    }

    return threat_model, rejected_threats