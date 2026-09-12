import json
from pathlib import Path


INPUT_FILE = Path(
    "data/raw/attack/enterprise-attack.json"
)

OUTPUT_FILE = Path(
    "data/processed/attack_chunks.json"
)


def extract_attack_id(obj):
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")

    return None


def extract_tactics(obj):
    tactics = []

    for phase in obj.get("kill_chain_phases", []):

        if phase.get("kill_chain_name") == "mitre-attack":
            phase_name = phase.get("phase_name")

            if phase_name:
                tactics.append(phase_name)

    return tactics


def build_chunks(objects):

    chunks = []

    for obj in objects:

        # Only process ATT&CK techniques
        if obj.get("type") != "attack-pattern":
            continue

        attack_id = extract_attack_id(obj)

        if not attack_id:
            continue

        name = obj.get("name", "")
        description = obj.get("description", "")
        tactics = extract_tactics(obj)

        text_parts = [
            f"Technique: {name}",
            f"ATT&CK ID: {attack_id}",
            f"Description: {description}"
        ]

        if tactics:
            text_parts.append(
                "Tactics: " + ", ".join(tactics)
            )

        chunk = {
            "id": f"attack-{attack_id}",
            "source": "MITRE_ATT&CK",
            "title": name,
            "text": "\n".join(text_parts),
            "tags": [
                "ATT&CK",
                attack_id,
                *tactics
            ]
        }

        chunks.append(chunk)

    return chunks


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    objects = data["objects"]

    chunks = build_chunks(objects)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            chunks,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Created {len(chunks)} ATT&CK chunks."
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()