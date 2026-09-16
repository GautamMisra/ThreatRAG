from generation.ollama_client import OllamaClient


def build_expansion_prompt(component, technology):

    return  f"""
You are a cybersecurity query expansion system for a threat-modeling retrieval system.

Your task is to expand a user's security component description into
retrieval-friendly security terminology.

The expanded queries will be searched against three security knowledge
bases:

1. STRIDE
   Focus on threat concepts such as:
   spoofing, tampering, repudiation, information disclosure,
   denial of service, elevation of privilege, authentication,
   impersonation, credential theft, session hijacking.

2. MITRE ATT&CK
   Focus on adversary techniques and concepts such as:
   token theft, token impersonation, access token manipulation,
   credential theft, session hijacking, web credentials,
   authentication interception, privilege escalation.

3. OWASP
   Focus on application security concepts such as:
   authentication failures, broken access control,
   cryptographic failures, security misconfiguration,
   session management, token validation, authorization.

IMPORTANT RULES:

- Do NOT simply append the name of the knowledge base.
- Do NOT output phrases like "STRIDE analysis", "MITRE ATT&CK techniques",
  or "OWASP top 10" unless they are genuinely useful retrieval terms.
- Extract the actual security risks implied by the component.
- Use concrete cybersecurity terminology.
- Prefer terms likely to appear in security knowledge bases.
- Do not invent technique IDs or vulnerability names.
- Keep the original component technology in the query.
- Generate one focused retrieval query for each knowledge base.
- Be specific rather than generic.
- Return ONLY valid JSON.

Example:

Input:
"API using JWT authentication"

Output:
{{
  "stride": [
    "JWT authentication spoofing token theft impersonation",
    "JWT service session hijacking credential theft privilege escalation"
  ],
  "attack": [
    "JWT token theft token impersonation access token manipulation",
    "JWT web credentials session hijacking credential theft"
  ],
  "owasp": [
    "JWT authentication failures broken access control token validation",
    "JWT cryptographic failures session management security misconfiguration"
  ]
}}

Now expand this component:

"{component}"
"""


def expand_query(component, technology):

    client = OllamaClient()

    prompt = build_expansion_prompt(
        component,
        technology
    )

    result = client.generate_json(
        prompt,
        temperature=0.1
    )

    return result


if __name__ == "__main__":

    component = "auth service"
    technology = "JWT"

    result = expand_query(
        component,
        technology
    )

    print("\n========== QUERY EXPANSION ==========")
    print(result)
    print("=====================================")