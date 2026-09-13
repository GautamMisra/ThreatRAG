import json
import os
from pathlib import Path

import psycopg2


# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer


# Load variables from .env
load_dotenv()


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROCESSED_DIR = Path("data/processed")

MODEL_NAME = "BAAI/bge-base-en-v1.5"

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "database": "ThreatRAG",
    "user": "ThreatRAG",
    "password": os.getenv("POSTGRES_PASSWORD").strip(),
}


# --------------------------------------------------
# Load chunks
# --------------------------------------------------

def load_chunks():
    chunks = []

    for file in PROCESSED_DIR.glob("*_chunks.json"):
        print(f"Loading {file}...")

        with open(file, "r", encoding="utf-8") as f:
            file_chunks = json.load(f)

        chunks.extend(file_chunks)

    print(f"Loaded {len(chunks)} total chunks.")

    return chunks


# --------------------------------------------------
# Generate embeddings
# --------------------------------------------------

def generate_embeddings(chunks, model):
    texts = [chunk["text"] for chunk in chunks]

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    print("Embeddings generated.")

    return embeddings


# --------------------------------------------------
# Insert into PostgreSQL
# --------------------------------------------------

def insert_chunks(chunks, embeddings):
    print("Connecting to PostgreSQL...")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    print("Connected.")

    insert_query = """
        INSERT INTO chunks (
            id,
            source,
            title,
            text,
            tags,
            embedding
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (id)
        DO UPDATE SET
            source = EXCLUDED.source,
            title = EXCLUDED.title,
            text = EXCLUDED.text,
            tags = EXCLUDED.tags,
            embedding = EXCLUDED.embedding;
    """

    for chunk, embedding in zip(chunks, embeddings):

        cursor.execute(
            insert_query,
            (
                chunk["id"],
                chunk["source"],
                chunk["title"],
                chunk["text"],
                json.dumps(chunk["tags"]),
                embedding.tolist(),
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Inserted {len(chunks)} chunks into PostgreSQL.")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    if not DB_CONFIG["password"]:
        raise ValueError(
            "POSTGRES_PASSWORD is not set in the .env file."
        )

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    chunks = load_chunks()

    embeddings = generate_embeddings(chunks, model)

    insert_chunks(chunks, embeddings)

    print("\nIndex building complete!")


if __name__ == "__main__":
    main()