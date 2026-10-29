# LLM RAG Chatbot With LangChain

A full-stack hospital knowledge assistant that combines a Neo4j graph database, vector search over patient reviews, and a LangChain-powered agent to answer natural-language questions about a synthetic hospital system.

The project includes:
- a Streamlit frontend for conversational Q&A
- a FastAPI backend exposing a hospital RAG agent endpoint
- a Neo4j ETL pipeline that ingests hospital data into a graph
- synthetic hospital datasets used for structured and unstructured retrieval

## Overview

This application demonstrates a multi-source RAG pattern:
- structured hospital data is stored in Neo4j and queried via Cypher
- patient-review text is indexed for semantic retrieval
- a LangChain agent decides which tool to use depending on the question type
- the frontend presents responses and intermediate reasoning steps to the user

It is designed for questions like:
- Which hospitals are in the system?
- What is the current wait time at a specific hospital?
- Which physician has the lowest average visit duration?
- What are patients saying about nursing staff at a hospital?
- Which insurer paid the most in hospital charges for a given period?

## Project Structure

```text
.
├── chatbot_api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/
│       ├── agents/
│       ├── chains/
│       ├── models/
│       ├── tools/
│       ├── utils/
│       ├── entrypoint.sh
│       └── main.py
├── chatbot_frontend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/
│       └── main.py
├── hospital_neo4j_etl/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/
│       ├── entrypoint.sh
│       └── hospital_bulk_csv_write.py
├── data/
│   ├── hospitals.csv
│   ├── patients.csv
│   ├── payers.csv
│   ├── physicians.csv
│   ├── reviews.csv
│   └── visits.csv
├── docker-compose.yml
├── requirements.txt
├── populate_review_embeddings.py
├── test_review_embeddings.py
├── tests/
├── .gitignore
└── README.md
```

## Architecture

### 1. Frontend
`chatbot_frontend/`
- Built with Streamlit
- Sends user prompts to the backend API
- Renders the chatbot response and explanation panel

### 2. Backend API
`chatbot_api/`
- Built with FastAPI
- Hosts a `/hospital-rag-agent` endpoint
- Uses a LangChain agent with tools for:
  - graph-based hospital queries
  - review-based qualitative questions
  - wait time lookup
  - hospital availability checks

### 3. Knowledge Graph ETL
`hospital_neo4j_etl/`
- Loads CSV data into a Neo4j graph
- Creates node uniqueness constraints
- Builds relationships like:
  - `Hospital -> Visit -> Patient`
  - `Physician -> TREATS -> Visit`
  - `Visit -> COVERED_BY -> Payer`
  - `Visit -> WRITES -> Review`

### 4. Data Layer
`data/`
- Synthetic hospital system dataset with records for hospitals, payers, physicians, patients, visits, and reviews
- Used for both graph analytics and semantic search

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangChain
- Neo4j
- Ollama / local LLM model
- Docker + Docker Compose
- Pandas/CSV-based ETL workflow

## Prerequisites

Before running the project, make sure you have:
- Docker
- Docker Compose
- A local or remote LLM endpoint compatible with the project configuration
- Neo4j accessible to the ETL and API services

## Environment Configuration

The app expects environment variables in a `.env` file at the repository root, which is referenced by `docker-compose.yml`.

Example configuration:

```env
# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Optional model settings
HOSPITAL_QA_MODEL=qwen3:8b

# CSV paths used by ETL (adjust as needed for your container setup)
HOSPITALS_CSV_PATH=file:///data/hospitals.csv
PAYERS_CSV_PATH=file:///data/payers.csv
PHYSICIANS_CSV_PATH=file:///data/physicians.csv
PATIENTS_CSV_PATH=file:///data/patients.csv
VISITS_CSV_PATH=file:///data/visits.csv
REVIEWS_CSV_PATH=file:///data/reviews.csv
```

Adjust the values to match your deployment environment and model setup.

## Run with Docker Compose

From the project root:

```bash
docker compose up --build
```

This starts:
- the Neo4j ETL service
- the FastAPI backend on `http://localhost:8000`
- the Streamlit frontend on `http://localhost:8501`

## Manual Run (Optional)

If you want to run individual services manually:

### Backend
```bash
cd chatbot_api
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd chatbot_frontend
streamlit run src/main.py
```

### ETL
```bash
cd hospital_neo4j_etl
python src/hospital_bulk_csv_write.py
```

## How the RAG Agent Works

1. A user asks a question in the Streamlit UI.
2. The frontend sends the message to the FastAPI backend.
3. The LangChain agent routes the request to the appropriate tool:
   - `Graph` for structured queries
   - `Experiences` for patient review / qualitative questions
   - `Waits` for a hospital-specific waiting-time lookup
   - `Availability` for the fastest available hospital
4. The tool executes against the Neo4j graph or review retrieval layer.
5. The final answer is returned to the user with intermediate steps shown in the UI.

## Example Questions

- Which hospitals are in the hospital system?
- What is the current wait time at Wallace-Hamilton Hospital?
- Which hospital has the shortest wait time?
- What are patients saying about the nursing staff at Castaneda-Hardy?
- What was the total billing amount charged to each payer for 2023?
- Which physician has the lowest average visit duration?

## Notes

- The app is designed as a demo / prototype for retrieval-augmented generation over a synthetic hospital domain.
- Some wait-time values may be simulated depending on the implementation used in your environment.
- The datasets are synthetic and intended for experimentation and learning rather than production medical use.

## License

This project does not currently declare a repository license in the root files reviewed here. If you plan to publish or share the project publicly, consider adding an appropriate open-source license such as MIT or Apache 2.0.

## Contributing

Contributions are welcome. Common ways to contribute include:
- improving the agent routing logic
- adding new hospital data sources
- improving UI feedback and explanation clarity
- tuning retrieval and graph queries
- expanding test coverage

## Acknowledgements

This project uses:
- LangChain for orchestration and tool use
- Neo4j for graph storage
- FastAPI and Streamlit for app services
- synthetic dataset generation for a hospital domain use case

