
import re


def normalize_source(source):
    """Normalize source labels so harmless formatting differences are ignored."""
    value = str(source or "").strip().lower()
    value = value.replace("_", "").replace(" ", "").replace("-", "")

    aliases = {
        "mitreatt&ck": "mitre",
        "mitreattck": "mitre",
        "mitre": "mitre",
        "stride": "stride",
        "owasp": "owasp",
    }

    return aliases.get(value, value)


def resolve_source_id(source_id, retrieved_map):
    """
    Resolve a source ID to exactly one retrieved chunk.
    Supports omitted 'attack-' prefixes when the match is unambiguous.
    """
    source_id = str(source_id or "").strip()

    if source_id in retrieved_map:
        return source_id

    candidates = {
        f"attack-{source_id}",
        source_id.removeprefix("attack-"),
    }

    matches = {
        candidate
        for candidate in candidates
        if candidate in retrieved_map
    }

    if len(matches) == 1:
        return next(iter(matches))

    return None


def normalize_text(text):
    """Normalize text for simple evidence-overlap checks."""
    return re.findall(r"[a-z0-9]+", str(text or "").lower())


def validate_grounding(threat_model, retrieved_chunks):
    """
    Validate threat citations against retrieved chunks.

    Checks:
    - source_id resolves to a retrieved chunk
    - source identifies the corpus or matches the resolved chunk's title
    - source_title matches the resolved chunk's title
    - evidence overlaps with the retrieved text
    - duplicate threats are removed
    """
    retrieved_map = {}

    for result in retrieved_chunks:
        chunk = result.get("chunk", result)

        chunk_id = str(chunk.get("id", "")).strip()
        if not chunk_id:
            continue

        retrieved_map[chunk_id] = {
            "source": chunk.get("source", ""),
            "title": chunk.get("title", ""),
            "text": (
                chunk.get("text")
                or chunk.get("content")
                or chunk.get("chunk_text")
                or ""
            ),
        }

    validated_model = dict(threat_model)
    accepted_threats = []
    rejected_threats = []
    seen_threats = set()

    for original_threat in threat_model.get("threats", []):
        threat = dict(original_threat)

        source_id = threat.get("source_id", "")
        source = threat.get("source", "")
        source_title = threat.get("source_title", "")
        evidence = threat.get("evidence", "")

        # 1. Resolve the citation to a retrieved chunk.
        resolved_id = resolve_source_id(source_id, retrieved_map)

        if resolved_id is None:
            threat["grounded"] = False
            threat["grounding_reason"] = (
                "source_id does not uniquely match a retrieved chunk"
            )
            rejected_threats.append(threat)
            continue

        retrieved_chunk = retrieved_map[resolved_id]
        canonical_source = str(
            retrieved_chunk["source"] or ""
        ).strip()
        canonical_title = str(
            retrieved_chunk["title"] or ""
        ).strip()

        # 2. Accept the canonical corpus name OR the exact title
        # of the already-resolved chunk in the source field.
        source_matches_corpus = (
            normalize_source(source)
            == normalize_source(canonical_source)
        )

        source_matches_title = (
            str(source or "").strip().casefold()
            == canonical_title.casefold()
        )

        if not (source_matches_corpus or source_matches_title):
            threat["grounded"] = False
            threat["grounding_reason"] = (
                "source matches neither the chunk's corpus nor its title"
            )
            rejected_threats.append(threat)
            continue

        # 3. Validate source_title against the exact resolved chunk.
        if (
            str(source_title or "").strip().casefold()
            != canonical_title.casefold()
        ):
            threat["grounded"] = False
            threat["grounding_reason"] = (
                "source_title does not match the resolved chunk"
            )
            rejected_threats.append(threat)
            continue

        # 4. Check meaningful word overlap with retrieved evidence.
        chunk_words = set(normalize_text(retrieved_chunk["text"]))
        evidence_words = set(normalize_text(evidence))

        stop_words = {
            "the", "and", "for", "with", "from", "that", "this",
            "into", "are", "can", "may", "could", "would", "their",
            "when", "which", "using", "used", "such", "have", "has",
            "been", "being", "its", "via", "about", "system",
        }

        meaningful_evidence = evidence_words - stop_words
        overlap = meaningful_evidence & chunk_words

        if meaningful_evidence and not overlap:
            threat["grounded"] = False
            threat["grounding_reason"] = (
                "evidence has no meaningful word overlap "
                "with the retrieved chunk"
            )
            rejected_threats.append(threat)
            continue

        # 5. Store canonical provenance from the retrieved chunk.
        threat["source_id"] = resolved_id
        threat["source"] = canonical_source
        threat["source_title"] = canonical_title
        threat["grounded"] = True
        threat.pop("grounding_reason", None)

        # 6. Deduplicate accepted threats.
        dedupe_key = (
            str(threat.get("stride_category", "")).strip().lower(),
            " ".join(normalize_text(threat.get("threat", ""))),
            resolved_id,
        )

        if dedupe_key in seen_threats:
            continue

        seen_threats.add(dedupe_key)
        accepted_threats.append(threat)

    validated_model["threats"] = accepted_threats

    return validated_model, rejected_threats

