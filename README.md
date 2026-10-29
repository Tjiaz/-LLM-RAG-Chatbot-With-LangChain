# LLM RAG Chatbot With LangChain

A full-stack hospital knowledge assistant that combines a Neo4j graph database, semantic review search, and a LangChain agent to answer natural-language questions about a synthetic hospital ecosystem.

This project demonstrates a practical retrieval-augmented generation workflow over both structured and unstructured data:
- structured hospital data is stored in Neo4j and queried with Cypher
- patient reviews are used for qualitative, experience-based questions
- a LangChain agent routes questions to the correct tool
- a Streamlit frontend presents answers and traceable reasoning

## Features

- Natural-language questions over hospital, patient, physician, payer, and visit data
- Graph-based reasoning with Neo4j for structured analytics
- Semantic search over patient reviews for experiential questions
- FastAPI backend exposing a chatbot endpoint
- Streamlit frontend for conversational interaction
- Docker Compose setup for running the full stack locally
- Synthetic hospital data for experimentation and demos

## Architecture

```text
User
  |
  v
Streamlit Frontend (chatbot_frontend)
  |
  v
FastAPI Backend (chatbot_api)
  |\
  | \__ Graph tool -> Neo4j hospital knowledge graph
  |
  \__ Experiences tool -> review vector retrieval / semantic search
      
      +-- Waits / Availability tools -> simulated hospital wait-time lookup
```

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangChain
- Neo4j
- Ollama / local LLM model
- Docker + Docker Compose

## Repository Structure

```text
.
├── README.md
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── populate_review_embeddings.py
├── test_review_embeddings.py
├── tests/
├── data/
│   ├── hospitals.csv
│   ├── patients.csv
│   ├── payers.csv
│   ├── physicians.csv
│   ├── reviews.csv
│   └── visits.csv
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
└──
```

## Project Components

### 1) Frontend
The Streamlit app in `chatbot_frontend/src/main.py` serves as the chatbot UI. It sends user queries to the backend and displays the response and intermediate tool steps.

### 2) Backend API
The FastAPI service in `chatbot_api/src/main.py` exposes a `POST /hospital-rag-agent` endpoint. It invokes the LangChain agent and returns:
- the final answer
- the user prompt
- intermediate tool traces

### 3) Agent Logic
The LangChain agent in `chatbot_api/src/agents/hospital_rag_agent.py` uses multiple tools:
- `Graph` for structured hospital, payer, physician, and visit questions
- `Experiences` for patient-review and sentiment-based questions
- `Waits` to retrieve a hospital wait-time value
- `Availability` to determine the hospital with the shortest wait time

### 4) ETL Pipeline
The Neo4j ETL component in `hospital_neo4j_etl/src/hospital_bulk_csv_write.py` loads CSV data into a graph with nodes and relationships such as:
- `Hospital`
- `Patient`
- `Physician`
- `Payer`
- `Visit`
- `Review`

Examples of relationships include:
- `(:Patient)-[:HAS]->(:Visit)`
- `(:Physician)-[:TREATS]->(:Visit)`
- `(:Visit)-[:AT]->(:Hospital)`
- `(:Visit)-[:COVERED_BY]->(:Payer)`
- `(:Visit)-[:WRITES]->(:Review)`

### 5) Data
The `data/` directory contains synthetic CSV files used to model a healthcare/hospital system. These files support both graph queries and review-based retrieval.

## Prerequisites

Before running the project locally, install:
- Docker
- Docker Compose
- Python 3.10+
- A local LLM runtime such as Ollama if you plan to run the model locally

## Environment Setup

The Docker services reference a root-level `.env` file.

Example:

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
HOSPITAL_QA_MODEL=qwen3:8b

HOSPITALS_CSV_PATH=file:///data/hospitals.csv
PAYERS_CSV_PATH=file:///data/payers.csv
PHYSICIANS_CSV_PATH=file:///data/physicians.csv
PATIENTS_CSV_PATH=file:///data/patients.csv
VISITS_CSV_PATH=file:///data/visits.csv
REVIEWS_CSV_PATH=file:///data/reviews.csv
```

You may need to adjust these values based on your local or container setup.

## Quick Start

From the repository root, run:

```bash
docker compose up --build
```

This will start:
- the ETL service
- the FastAPI backend on `http://localhost:8000`
- the Streamlit frontend on `http://localhost:8501`

## Manual Run

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

### ETL Pipeline

```bash
cd hospital_neo4j_etl
python src/hospital_bulk_csv_write.py
```

## Example Questions

- Which hospitals are in the system?
- What is the current wait time at Wallace-Hamilton Hospital?
- Which hospital has the shortest wait time?
- What are patients saying about the nursing staff at Castaneda-Hardy?
- What was the total billing amount charged to each payer for 2023?
- Which physician has the lowest average visit duration?
- How much was billed for patient 789's stay?

## Notes

- This project is best viewed as a demo / prototype for graph + vector-based RAG patterns.
- The synthetic dataset is not intended for real medical or clinical decision making.
- Some wait-time values may be simulated depending on the runtime environment and model configuration.

## License

No explicit license file was present in the project files reviewed here. If you intend to publish or distribute the project more broadly, consider adding an open-source license such as MIT or Apache 2.0.

## Contributing

Contributions are welcome. Good areas for improvement include:
- better prompt routing and tool selection
- richer graph queries and analytics
- improved frontend UX
- additional tests and validation
- more robust deployment configuration

## Acknowledgements

This project uses:
- LangChain for orchestration and agent tooling
- Neo4j for graph storage and query processing
- FastAPI and Streamlit for application services
- synthetic hospital data for demonstration purposes
