def build_synthesis_prompt(component, technology, retrieved_chunks):

    context = ""

    for i, result in enumerate(retrieved_chunks, start=1):

        chunk = result["chunk"]

        context += f"""
[CHUNK {i}]
Chunk ID: {chunk["id"]}
Source: {chunk["source"]}
Title: {chunk["title"]}

Content:
{chunk["text"]}

-------------------------
"""

    prompt = f"""
You are a cybersecurity threat-modeling assistant.

Your task is to generate a grounded threat model for the following
system component using ONLY the retrieved security knowledge provided below.

COMPONENT:
{component}

TECHNOLOGY:
{technology}

RETRIEVED SECURITY KNOWLEDGE:
{context}

IMPORTANT GROUNDING RULES:

1. Use ONLY information supported by the retrieved chunks.
2. Do NOT use your own external knowledge to introduce new threats,
   techniques, vulnerabilities, or recommendations.
3. Every threat MUST cite at least one retrieved Chunk ID.
4. Do NOT invent Chunk IDs, source names, technique IDs, or vulnerability IDs.
5. The source citation must correspond exactly to one of the provided chunks.
6. The evidence field must contain information supported by the cited chunk.
7. If the retrieved context does not provide enough evidence for a threat,
   do not include that threat.
8. Likelihood and impact are estimates made by the LLM based on the
   retrieved evidence. Clearly label them as estimates.
9. Keep the answer concise and security-focused.

RETURN ONLY VALID JSON.

Use exactly this structure:

{{
    "summary": "Brief summary of the main security risks supported by the retrieved evidence.",
    "threats": [
        {{
            "stride_category": "One STRIDE category",
            "threat": "Description of the threat",
            "likelihood": "LLM-estimated likelihood",
            "impact": "LLM-estimated impact",
            "mitigation": "Mitigation supported by the retrieved context",
            "source": "Exact source name from the retrieved chunk",
            "source_id": "Exact Chunk ID from the retrieved chunk",
            "evidence": "Relevant evidence from the cited chunk"
        }}
    ],
    "recommendations": [
        "Security recommendation supported by the retrieved context"
    ]
}}

Do not include markdown.
Do not include ```json.
Return only the JSON object.

Now generate the threat model.
"""

    return prompt

if __name__ == "__main__":

    test_chunks = [
        {
            "chunk": {
                "id": "attack-T1134",
                "source": "MITRE_ATT&CK",
                "title": "Access Token Manipulation",
                "text": "Adversaries may modify access tokens to operate under different security contexts."
            }
        },
        {
            "chunk": {
                "id": "owasp-a07",
                "source": "OWASP",
                "title": "Authentication Failures",
                "text": "Authentication failures can occur when authentication mechanisms are improperly implemented."
            }
        }
    ]

    prompt = build_synthesis_prompt(
        component="web API",
        technology="SQL Injection",
        retrieved_chunks=test_chunks
    )

    print(prompt)