# ThreatRAG

ThreatRAG is a Hybrid Retrieval-Augmented Generation (RAG) system designed to automate security threat identification and analysis. It combines hybrid retrieval, LLM-based query expansion, and reranking to retrieve relevant security knowledge and generate context-grounded threat assessments.

The system leverages security frameworks such as STRIDE, MITRE ATT&CK, and OWASP to provide structured threat analysis for different system components and technologies.

## Screenshots

### ThreatRAG Interface

<!-- Replace the image path below with your first screenshot -->
![ThreatModel-RAG Interface](docs/images/threatrag-ui.png)

### Threat Analysis Results

<!-- Replace the image path below with your second screenshot -->
![Threat Analysis Results](docs/images/threatrag-results.png)

## Features

### Hybrid Retrieval
- Dense retrieval using Sentence Transformers and vector embeddings.
- Sparse retrieval using BM25 for keyword-based matching.
- Reciprocal Rank Fusion (RRF) to combine retrieval results.
- Cross-encoder reranking to improve the relevance of retrieved chunks.
- Deduplication and merging of results from multiple queries.

### LLM-Based Query Expansion
- Uses Ollama with Phi-4-mini for query expansion.
- Generates multiple security-focused subqueries from a system description.
- Expands queries across STRIDE, MITRE ATT&CK, and OWASP perspectives.
- Improves retrieval coverage by exploring different aspects of a security problem.

### Threat Modeling
- Accepts system components and their associated technologies.
- Retrieves relevant security knowledge from the processed knowledge base.
- Generates structured threat assessments using retrieved context.
- Identifies potential security threats and their implications.
- Produces framework-oriented threat analysis grounded in retrieved information.

### Security Knowledge Base
- Processes security knowledge into searchable chunks.
- Supports knowledge from STRIDE, MITRE ATT&CK, and OWASP.
- Combines semantic similarity with keyword matching.
- Uses PostgreSQL with pgvector for vector-based retrieval.

### REST API
- Built using FastAPI.
- Provides endpoints for health checks and threat analysis.
- Accepts structured system descriptions.
- Returns threat analysis results in JSON format.

### Web Interface
- Provides an interface for entering system components and technologies.
- Sends analysis requests to the backend API.
- Displays generated threat assessments.
- Includes loading states during analysis.

## Architecture

ThreatModel-RAG follows a multi-stage retrieval and generation pipeline.

```text
              System Description
                       |
                       v
                Query Expansion
                 (Ollama LLM)
                       |
                       v
             Security-Focused Queries
                       |
             +---------+---------+
             |                   |
             v                   v
       Dense Retrieval      Sparse Retrieval
       (Embeddings)             (BM25)
             |                   |
             v                   v
        Vector Search       Keyword Search
       (PostgreSQL +        (BM25 Index)
          pgvector)              |
             |                   |
             +---------+---------+
                       |
                       v
          Reciprocal Rank Fusion (RRF)
                       |
                       v
                Cross-Encoder
                  Reranking
                       |
                       v
              Merge and Deduplicate
                       |
                       v
              Retrieved Context
                       |
                       v
              Threat Synthesis
                  (LLM)
                       |
                       v
             Structured Threat Model
                       |
                       v
                 REST API / UI
```

## Tech Stack

### Backend
- Python
- FastAPI
- Pydantic
- Requests

### Retrieval and NLP
- Sentence Transformers
- BAAI/bge-base-en-v1.5
- BM25 (`rank-bm25`)
- Reciprocal Rank Fusion (RRF)
- Cross-encoder reranking

### LLM
- Ollama
- Phi-4-mini (3.8B)

### Database
- PostgreSQL
- pgvector

### Infrastructure and Tools
- Docker
- Docker Compose
- Python virtual environment
- Git and GitHub

### Security Knowledge Sources
- STRIDE
- MITRE ATT&CK
- OWASP

## Retrieval Pipeline

The retrieval pipeline combines semantic search, keyword matching, and reranking to identify relevant security information.

### 1. Query Expansion

The system uses an LLM to transform a system description into multiple security-focused queries.

For example, given:

```text
Component: Auth Service
Technology: JWT
```

The query expansion stage generates queries covering different security perspectives, such as:

- Auth service JWT STRIDE threats
- Auth service JWT MITRE ATT&CK techniques
- Auth service JWT OWASP security guidance

This helps retrieve relevant information that a single query might miss.

### 2. Dense Retrieval

Dense retrieval uses Sentence Transformers to encode queries into vector embeddings.

The embeddings are used to retrieve semantically relevant security knowledge stored in PostgreSQL with pgvector.

**Embedding model:** `BAAI/bge-base-en-v1.5`

### 3. Sparse Retrieval

Sparse retrieval uses BM25 to find relevant knowledge based on keyword overlap between the query and indexed document chunks.

This complements dense retrieval by identifying documents containing important security terms, technologies, and attack techniques.

### 4. Reciprocal Rank Fusion

The results from dense and sparse retrieval are combined using Reciprocal Rank Fusion.

RRF combines rankings from multiple retrieval methods, helping the system leverage both semantic similarity and keyword relevance.

### 5. Cross-Encoder Reranking

The fused candidates are passed through a reranker to improve their ordering based on query-document relevance.

This helps prioritize the most relevant security knowledge before threat synthesis.

### 6. Context Merging

Results from multiple expanded queries are merged and deduplicated.

The system consolidates relevant chunks into a context for the final threat analysis.

### 7. Threat Synthesis

The retrieved context is passed to the LLM to generate a structured threat assessment.

The synthesis stage is designed to ground its output in retrieved security knowledge and reference the associated chunk IDs rather than inventing source references.

## Project Structure

The following illustrates the main logical components of the project. Update the paths to match your actual repository structure.

```text
ThreatModel-RAG/
|
├── backend/
│   ├── api/
│   │   └── main.py
│   │
│   ├── retrieval/
│   │   ├── dense_retriever.py
│   │   ├── sparse_retriever.py
│   │   ├── fusion.py
│   │   └── reranker.py
│   │
│   ├── services/
│   │   ├── query_expansion.py
│   │   └── threat_synthesizer.py
│   │
│   └── requirements.txt
│
├── data/
│   ├── raw/
│   └── processed/
│       └── *_chunks.json
│
├── frontend/
│
├── docker-compose.yml
├── .env.example
└── README.md
```

*Note: This is a representative structure. Adjust directory names and filenames to reflect your actual repository.*

## Local Setup

### Prerequisites

Install the following before running the project:

- Python 3.10 or later
- Docker Desktop with Docker Compose
- Ollama
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/GautamMisra/ThreatModel-RAG.git

cd ThreatModel-RAG
```

Replace the repository URL if your GitHub repository uses a different name.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure that your requirements file includes the dependencies used by your implementation, such as:

```text
sentence-transformers
psycopg2-binary
rank-bm25
python-dotenv
fastapi
uvicorn
pydantic
requests
```

### 4. Configure Ollama

Install and start Ollama, then pull the model:

```bash
ollama pull phi4-mini
```

Verify that the model is available:

```bash
ollama list
```

The query expansion and threat synthesis services use Ollama to generate model responses.

The configured generation endpoint is:

```text
http://localhost:11434/api/generate
```

Ensure the model name in your configuration matches the installed Ollama model.

### 5. Configure PostgreSQL and pgvector

The project uses PostgreSQL with the pgvector extension for vector storage and retrieval.

A Docker Compose configuration can be used to start the database:

```bash
docker compose up -d
```

Configure the database connection using environment variables.

Example configuration:

```env
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=ThreatRAG
DB_USER=ThreatRAG
DB_PASSWORD=your_database_password
```

The example uses port `5433` on the host, mapped to PostgreSQL's default port `5432` inside the container.

Make sure the environment variable names match those expected by your database configuration.

### 6. Prepare the Knowledge Base

Place your processed security knowledge chunks in the configured processed-data directory.

Example:

```text
data/processed/
├── stride_chunks.json
├── mitre_chunks.json
└── owasp_chunks.json
```

The actual filenames should match your preprocessing pipeline.

Ensure the PostgreSQL database, vector extension, tables, and embeddings have been initialized according to your implementation.

### 7. Start the Backend API

From the directory containing your FastAPI application, run:

```bash
uvicorn api.main:app --reload
```

Adjust the module path if your FastAPI application is located elsewhere.

The API will be available at:

```text
http://localhost:8000
```

### 8. Verify the API

Check the health endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "ThreatModel-RAG"
}
```

Open the interactive API documentation at:

```text
http://localhost:8000/docs
```

Use the Swagger interface to test the available endpoints.

### 9. Start the Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

If the frontend requires an API base URL, configure it to point to your running FastAPI backend.

Use the environment variable name expected by your frontend implementation.

## API Overview

### Health Check

```http
GET /health
```

Checks whether the backend service is running.

### Threat Analysis

```http
POST /analyze
```

Accepts a system description and returns a structured threat assessment.

Example request structure:

```json
{
  "components": [
    {
      "component": "Auth Service",
      "technology": "JWT"
    }
  ]
}
```

The exact request schema must match the `SystemDescription` Pydantic model defined in your backend.

The analysis response contains the status, analyzed components, and generated threat model according to the API response schema.

## Example Workflow

Consider an application containing an authentication service that uses JSON Web Tokens (JWT).

1. The user submits the component and its technology through the interface.
2. The backend receives the system description.
3. The query expansion model generates security-focused queries.
4. Dense and sparse retrievers independently retrieve relevant security knowledge.
5. Reciprocal Rank Fusion combines the retrieval rankings.
6. The reranker prioritizes relevant chunks.
7. Duplicate results are removed and the retrieved context is assembled.
8. The threat synthesis model generates a structured threat assessment.
9. The backend returns the results to the interface.

The final output can include identified threats, their descriptions, relevant security framework mappings, and supporting chunk references, depending on the configured response schema.

## Running with Docker

The project uses Docker and Docker Compose for containerized services.

From the repository root:

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

The exact services, port mappings, and environment variables depend on your `docker-compose.yml` configuration.

**Important:** If Ollama runs directly on your host machine while the backend runs inside Docker, `localhost` inside the backend container refers to that container, not your host. Configure the Ollama URL appropriately for your environment.

## Design Considerations

### Hybrid Retrieval

Combining dense and sparse retrieval helps address the limitations of relying on semantic similarity or keyword matching alone.

### Query Expansion

Generating framework-oriented subqueries improves coverage across different security perspectives.

### Reranking

Reranking helps prioritize relevant candidates from the larger set produced by the retrieval stages.

### Grounded Threat Generation

The synthesis stage uses retrieved security knowledge as context and is instructed to avoid unsupported claims and fabricated chunk references.

### Modular Architecture

Separating retrieval, query expansion, reranking, and threat synthesis makes the system easier to test, debug, and improve independently.

## Future Improvements

- Improve retrieval quality through systematic evaluation.
- Compare LLM-generated query expansion against manually designed queries.
- Optimize retrieval latency and model inference time.
- Introduce retrieval evaluation metrics such as Precision@K, Recall@K, and MRR.
- Improve threat prioritization and severity assessment.
- Add support for additional security frameworks and knowledge sources.
- Expand the frontend with threat visualization and architecture diagrams.
- Add automated testing for retrieval and synthesis components.
- Improve citation validation and source traceability.

## Author

**Gautam Misra**

B.Tech Computer Science and Engineering (Cybersecurity)  
Manipal Institute of Technology

---

*ThreatModel-RAG combines retrieval techniques and language models to support context-grounded security threat analysis.*
