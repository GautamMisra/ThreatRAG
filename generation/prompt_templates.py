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
10. The "stride_category" field MUST be exactly one of these six values:
    Spoofing
    Tampering
    Repudiation
    Information Disclosure
    Denial of Service
    Elevation of Privilege

    Do NOT use MITRE ATT&CK tactics such as Credential Access,
    Lateral Movement, Execution, Persistence, Defense Evasion,
    Discovery, or Privilege Escalation as STRIDE categories.
11. The "source_id" field MUST exactly match the complete "Chunk ID"
    shown in the retrieved context.

    For example:
    If the retrieved chunk says:
    Chunk ID: attack-T1134

    You MUST output:
    "source_id": "attack-T1134"

    NOT:
    "source_id": "T1134"

    Similarly:
    "attack-T1563.002" must remain exactly "attack-T1563.002".

    Never remove prefixes such as "attack-", "owasp-", or "stride-".
12. The source_id, source, and source_title MUST all refer to the SAME
    retrieved chunk.

    For example, if the retrieved context contains:

    Chunk ID: attack-T1134
    Source: MITRE_ATT&CK
    Title: Access Token Manipulation

    then a threat about Access Token Manipulation MUST use:

    "source": "MITRE_ATT&CK",
    "source_id": "attack-T1134",
    "source_title": "Access Token Manipulation"

    Do NOT use a Chunk ID belonging to a different threat or technique.

13. The evidence field MUST be derived from the Content of the cited
    chunk. Do not use evidence from another retrieved chunk.
14. Do NOT generate a mitigation or recommendation unless it is explicitly
    supported by the retrieved chunk(s). If the retrieved evidence does
    not contain a mitigation, write:
    "No mitigation supported by retrieved evidence."

15. Do NOT infer or add cybersecurity knowledge from the model's own
    knowledge, even if the recommendation is generally considered good
    security practice.

16. The stride_category MUST be one of:
    Spoofing, Tampering, Repudiation, Information Disclosure,
    Denial of Service, Elevation of Privilege.

    If a retrieved threat does not clearly map to one of these categories,
    do not include that threat.

RETURN ONLY VALID JSON.

Use exactly this structure:

{{
    "summary": "Brief summary of the main security risks supported by the retrieved evidence.",
    "threats": [
        {{
            "stride_category": "One of: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege",
            "threat": "Description of the threat",
            "likelihood": "LLM-estimated likelihood",
            "impact": "LLM-estimated impact",
            "mitigation": "Mitigation supported by the retrieved context",
            "source": "MITRE_ATT&CK, STRIDE, or OWASP",
            "source_id": "Exact Chunk ID from the retrieved chunk",
            "source_title": "Exact Title from the cited chunk",
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