import json
from pathlib import Path


INPUT_FILE = Path("data/raw/stride/stride_reference.md")
OUTPUT_FILE = Path("data/processed/stride_chunks.json")


def parse_stride_sections(text):
    sections = []

    current_title = None
    current_content = []

    for line in text.splitlines():

        # A markdown H2 represents a STRIDE category
        if line.startswith("## "):

            # Save previous section
            if current_title is not None:
                sections.append({
                    "title": current_title,
                    "text": "\n".join(current_content).strip()
                })

            current_title = line.replace("## ", "").strip()
            current_content = []

        else:
            if current_title is not None:
                current_content.append(line)

    # Save final section
    if current_title is not None:
        sections.append({
            "title": current_title,
            "text": "\n".join(current_content).strip()
        })

    return sections


def build_chunks(sections):
    chunks = []

    for section in sections:

        title = section["title"]

        chunk = {
            "id": f"stride-{title.lower().replace(' ', '-')}",
            "source": "STRIDE",
            "title": title,
            "text": section["text"],
            "tags": [
                "STRIDE",
                title
            ]
        }

        chunks.append(chunk)

    return chunks


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    sections = parse_stride_sections(text)

    chunks = build_chunks(sections)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Created {len(chunks)} STRIDE chunks.")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()