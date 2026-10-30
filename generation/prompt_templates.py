
import json


def build_synthesis_prompt(component, technology, retrieved_chunks):
    """
    Build a grounded threat-synthesis prompt that prioritizes relevance
    to the specified component and technology.
    """

    context_chunks = []

    for result in retrieved_chunks:
        chunk = result.get("chunk", result)

        context_chunks.append({
            "id": chunk.get("id", ""),
            "source": chunk.get("source", ""),
            "title": chunk.get("title", ""),
            "text": (
                chunk.get("text")
                or chunk.get("content")
                or chunk.get("chunk_text")
                or ""
            ),
        })

    context_json = json.dumps(context_chunks, indent=2)

    prompt = f"""
You are a cybersecurity threat-modeling assistant.

Your task is to generate a threat model for ONE specific system component
using only the retrieved reference material as evidence.

TARGET COMPONENT:
{component}

TARGET TECHNOLOGY:
{technology}

RETRIEVED REFERENCE CHUNKS:
{context_json}

==================================================
1. COMPONENT AND TECHNOLOGY RELEVANCE
==================================================

Every threat must apply to the TARGET COMPONENT and its stated TECHNOLOGY.

Before including a threat, internally check:
- Does this threat apply to this component?
- Does it apply to the stated technology or an explicitly described interaction?
- Does the retrieved evidence actually support the threat?
- Is the threat relevant to this component's role in the system?

If any answer is no or cannot be established, DO NOT include that threat.

Do not assume technologies, operating systems, infrastructure, or deployment
details that the user has not provided.

IMPORTANT TECHNOLOGY DISTINCTION:
A JWT application token is not the same thing as a Windows operating-system
access token.

For example, MITRE ATT&CK techniques concerning Windows access-token
manipulation, process-token duplication, or Windows privilege escalation
must NOT automatically be treated as JWT vulnerabilities.

Only include such techniques if the supplied architecture explicitly makes
them relevant and the retrieved evidence supports that connection.

Do not force every retrieved chunk into the output. It is acceptable to
return fewer threats, including zero threats, when the evidence is irrelevant.

==================================================
2. EVIDENCE AND GROUNDING
==================================================

Use ONLY the supplied retrieved chunks as evidence.

- Do not invent vulnerabilities, attack details, or source references.
- Every threat must cite one retrieved chunk using its exact ID.
- Copy the source and title exactly from the same cited chunk.
- The evidence field must accurately reflect information in that chunk.
- Do not claim that a chunk proves something it does not discuss.
- Do not combine multiple sources into one citation.
- Do not invent chunk IDs or alter their prefixes.
- If a threat is plausible but the retrieved material does not support it,
  omit it rather than presenting it as a confirmed, grounded threat.

The target component and technology help determine relevance; they are not
themselves evidence that a vulnerability exists.

==================================================
3. THREAT QUALITY
==================================================

Each threat must:
- Describe a concrete attack or security failure.
- Explain the potential consequence for the target component.
- Use the most appropriate STRIDE category:
  Spoofing, Tampering, Repudiation, Information Disclosure,
  Denial of Service, or Elevation of Privilege.
- Avoid duplicating another threat with different wording.
- Avoid generic claims such as "hackers may attack the system" without
  a specific, evidence-supported attack scenario.

Prefer a small number of relevant, evidence-supported threats over a long
list of weak or unrelated threats.

==================================================
4. MITIGATIONS
==================================================

Each mitigation must address the specific threat.

- Prefer actionable controls over generic advice.
- Do not claim that a control completely prevents an attack unless the
  evidence supports that claim.
- Do not recommend unrelated controls just to fill the field.
- Do not present general best practices as if they were stated in the
  retrieved source.
- If the source describes an attack but does not provide a mitigation,
  provide a conservative, technically appropriate recommendation only
  when it directly addresses the described attack. Do not falsely attribute
  that recommendation to the source.

==================================================
5. OUTPUT FORMAT
==================================================

Return ONLY valid JSON. Do not use Markdown fences or additional prose.

Use exactly this structure:

{{
  "summary": "Short summary of the relevant threats, or that no relevant threats could be established from the retrieved evidence.",
  "threats": [
    {{
      "stride_category": "One valid STRIDE category",
      "threat": "Specific threat description",
      "likelihood": "Low, Medium, or High",
      "impact": "Low, Medium, or High",
      "mitigation": "Specific mitigation",
      "source": "Exact source value from the cited chunk",
      "source_id": "Exact chunk ID from the cited chunk",
      "source_title": "Exact title from the cited chunk",
      "evidence": "Accurate supporting evidence from the cited chunk"
    }}
  ],
  "recommendations": [
    "Actionable recommendation relevant to the target component"
  ]
}}

Additional output rules:
- Use an empty threats array if no relevant threats are supported.
- Recommendations must be relevant to the target component.
- Do not include threats merely to populate every STRIDE category.
- Do not include a grounded field; the grounding validator adds it.
- Ensure the JSON is syntactically valid.
"""

    return prompt



if __name__ == "__main__":

    test_chunks = [
        {
            "chunk": {
                "id": "attack-T1134",
                "source": "MITRE_ATT&CK",
                "title": "Access Token Manipulation",
                "text": (
                    "Adversaries may modify access tokens to operate "
                    "under different security contexts."
                )
            }
        },
        {
            "chunk": {
                "id": "owasp-a07",
                "source": "OWASP",
                "title": "Authentication Failures",
                "text": (
                    "Authentication failures can occur when "
                    "authentication mechanisms are improperly implemented."
                )
            }
        }
    ]

    print(
        build_synthesis_prompt(
            component="Auth Service",
            technology="JWT",
            retrieved_chunks=test_chunks
        )
    )
