import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from neo4j import GraphDatabase

load_dotenv(Path("chatbot_api/.env"))

props = [
    "physician_name",
    "patient_name",
    "text",
    "hospital_name",
]

query = """
MATCH (n:Review)
WHERE n.embedding IS NULL
  AND any(k IN $props WHERE n[k] IS NOT NULL)
RETURN elementId(n) AS id,
       reduce(s = "", k IN $props |
           s + "\n" + k + ":" + coalesce(n[k], "")
       ) AS text
LIMIT 100
"""

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(
        os.environ["NEO4J_USERNAME"],
        os.environ["NEO4J_PASSWORD"],
    ),
)

try:
    result = driver.execute_query(
        query,
        parameters_={"props": props},
    )
    texts = [record["text"] for record in result.records]
finally:
    driver.close()

print("Actual review texts loaded:", len(texts))

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://127.0.0.1:11434",
)

for size in [10, 25, 50, 100]:
    if len(texts) < size:
        continue

    try:
        vectors = embeddings.embed_documents(texts[:size])
        print("PASS:", size, "reviews;", len(vectors), "embeddings")
    except Exception as exc:
        print("FAIL at", size, "reviews")
        print(type(exc).__name__, str(exc))
        break
