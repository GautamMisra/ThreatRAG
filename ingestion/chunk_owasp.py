import json
import re
from pathlib import Path


TOP10_FILE = Path(
    "data/raw/owasp/owasp_top_10.md"
)

CHEAT_SHEET_FILE = Path(
    "data/raw/owasp/threat_modeling_cheat_sheet.md"
)

OUTPUT_FILE = Path(
    "data/processed/owasp_chunks.json"
)


def parse_top10(text):
    """
    Parse OWASP Top 10.

    Each A01-A10 category becomes one chunk.
    """

    chunks = []

    # Find every category heading.
    pattern = re.compile(
        r"^(A\d{2}:2025\s*[–-]\s*.+)$",
        re.MULTILINE
    )

    matches = list(pattern.finditer(text))

    for i, match in enumerate(matches):

        title = match.group(1).strip()

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        section_text = text[start:end].strip()

        # Extract category ID
        category_id = title.split(":")[0]

        chunks.append({
            "id": f"owasp-{category_id.lower()}",
            "source": "OWASP",
            "title": title,
            "text": section_text,
            "tags": [
                "OWASP",
                "OWASP Top 10",
                category_id
            ]
        })

    return chunks


def parse_cheat_sheet(text):
    """
    Parse the OWASP Threat Modeling Cheat Sheet.

    Each major section becomes one chunk.
    """

    chunks = []

    # The uploaded file uses ¶ after section headings.
    pattern = re.compile(
        r"^(.+?)¶$",
        re.MULTILINE
    )

    matches = list(pattern.finditer(text))

    for i, match in enumerate(matches):

        title = match.group(1).strip()

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        section_text = text[start:end].strip()

        if not section_text:
            continue

        # Ignore accidental tiny headings if any
        if len(title) < 3:
            continue

        chunks.append({
            "id": (
                "owasp-cheatsheet-"
                + re.sub(
                    r"[^a-z0-9]+",
                    "-",
                    title.lower()
                ).strip("-")
            ),
            "source": "OWASP",
            "title": title,
            "text": section_text,
            "tags": [
                "OWASP",
                "Threat Modeling Cheat Sheet",
                title
            ]
        })

    return chunks


def main():

    # -----------------------------
    # Read OWASP Top 10
    # -----------------------------

    with open(
        TOP10_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        top10_text = f.read()


    # -----------------------------
    # Read Threat Modeling Cheat Sheet
    # -----------------------------

    with open(
        CHEAT_SHEET_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        cheat_sheet_text = f.read()


    # -----------------------------
    # Parse both sources
    # -----------------------------

    top10_chunks = parse_top10(top10_text)

    cheat_sheet_chunks = parse_cheat_sheet(
        cheat_sheet_text
    )


    # Combine everything
    chunks = (
        top10_chunks
        + cheat_sheet_chunks
    )


    # -----------------------------
    # Save processed chunks
    # -----------------------------

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


    # -----------------------------
    # Summary
    # -----------------------------

    print(
        f"Created {len(top10_chunks)} "
        "OWASP Top 10 chunks."
    )

    print(
        f"Created {len(cheat_sheet_chunks)} "
        "Threat Modeling Cheat Sheet chunks."
    )

    print(
        f"Created {len(chunks)} total OWASP chunks."
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()