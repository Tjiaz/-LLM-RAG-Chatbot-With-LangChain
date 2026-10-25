import os
from pathlib import Path

from dotenv import load_dotenv

# Load chatbot_api/.env regardless of the working directory
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import (
   ChatPromptTemplate,
   HumanMessagePromptTemplate,
   PromptTemplate,
   SystemMessagePromptTemplate,
)
from langchain_neo4j import Neo4jVector
from langchain_ollama import ChatOllama, OllamaEmbeddings

HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL", "qwen3:8b")
EMBEDDING_MODEL = "nomic-embed-text"

# Embedding model: replaces OpenAIEmbeddings()
embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url="http://host.docker.internal:11434",
)

neo4j_vector_index = Neo4jVector.from_existing_graph(
    embedding=embeddings,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="reviews",
    node_label="Review",
    text_node_properties=[
        "physician_name",
        "patient_name",
        "text",
        "hospital_name",
    ],
    embedding_node_property="embedding",

)

review_template = """Your job is to use patient
reviews to answer questions about their experience at
a hospital. Use the following context to answer questions.
Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer,
say you don't know.
{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=review_template
    )
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [review_system_prompt, review_human_prompt]

review_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

# Local Ollama chat model: replaces ChatOpenAI()
llm = ChatOllama(
    model=HOSPITAL_QA_MODEL,
    temperature=0,
    base_url="http://127.0.0.1:11434",
)


reviews_vector_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=neo4j_vector_index.as_retriever( search_kwargs={"k": 12}),

    chain_type_kwargs={
           "prompt": review_prompt,
       },
       return_source_documents=True,
)

if __name__ == "__main__":
   question = "What do patients say about communication with hospital staff?"

   result = reviews_vector_chain.invoke({
       "query": question,
   })

   print("\nAnswer:\n")
   print(result["result"])

   print("\nRetrieved review count:", len(result["source_documents"]))
