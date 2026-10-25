
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_ollama import OllamaEmbeddings

load_dotenv(Path("chatbot_api/.env"))

PROPS = [
    "physician_name",
    "patient_name",
    "text",
    "hospital_name",
]

BATCH_SIZE = 100

FETCH_QUERY = """
MATCH (n:Review)
WHERE n.embedding IS NULL
  AND any(k IN $props WHERE n[k] IS NOT NULL)
RETURN elementId(n) AS id,
       reduce(s = "", k IN $props |
           s + "\n" + k + ":" + coalesce(n[k], "")
       ) AS text
LIMIT $limit
"""

SAVE_QUERY = """
UNWIND $data AS row
MATCH (n:Review)
WHERE elementId(n) = row.id
CALL db.create.setNodeVectorProperty(
    n, 'embedding', row.embedding
)
RETURN count(*) AS updated
"""

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(
        os.environ["NEO4J_USERNAME"],
        os.environ["NEO4J_PASSWORD"],
    ),
)

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://127.0.0.1:11434",
)

total = 0

try:
    while True:
        result = driver.execute_query(
            FETCH_QUERY,
            parameters_={
                "props": PROPS,
                "limit": BATCH_SIZE,
            },
        )

        records = result.records

        if not records:
            break

        texts = [record["text"] for record in records]
        vectors = embeddings.embed_documents(texts)

        if len(vectors) != len(records):
            raise RuntimeError("Embedding count does not match review count")

        data = [
            {"id": record["id"], "embedding": vector}
            for record, vector in zip(records, vectors)
        ]

        saved = driver.execute_query(
            SAVE_QUERY,
            parameters_={"data": data},
        )

        updated = saved.records[0]["updated"]
        total += updated

        print(
            f"Saved {updated} embeddings "
            f"in this batch. Total saved: {total}"
        )

    print(f"\nFinished. Total embeddings saved: {total}")

finally:
    driver.close()
