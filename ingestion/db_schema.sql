CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    tags JSONB,
    embedding VECTOR(768)
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
ON chunks
USING hnsw (embedding vector_cosine_ops);