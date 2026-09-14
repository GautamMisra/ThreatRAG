from pathlib import Path
import json

sources = set()

for file in Path("data/processed").glob("*_chunks.json"):
    with open(file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    for chunk in chunks:
        sources.add(chunk["source"])

print("Sources found:")
for source in sorted(sources):
    print(source)