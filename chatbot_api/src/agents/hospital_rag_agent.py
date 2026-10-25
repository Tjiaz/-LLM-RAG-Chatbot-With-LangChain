import os

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from chains.hospital_cypher_chain import hospital_cypher_chain
from chains.hospital_review_chain import reviews_vector_chain
from tools.wait_times import (
    get_current_wait_times,
    get_most_available_hospital,
)

# Use the same local Ollama model as the review chain.
HOSPITAL_AGENT_MODEL = os.getenv(
    "HOSPITAL_QA_MODEL",
    "qwen3:8b",
)


@tool("Experiences")
def experiences(question: str) -> str:
    """Answer qualitative questions about patient experiences,
    feelings, satisfaction, treatment, and communication using
    semantic search over patient reviews.
    """
    result = reviews_vector_chain.invoke({"query": question})
    return str(result.get("result", result))


@tool("Graph")
def graph(question: str) -> str:
    """Answer structured questions about hospitals, patients,
    physicians, insurance payers, visit details, counts, and
    review statistics using the hospital knowledge graph.
    """
    result = hospital_cypher_chain.invoke({"query": question})

    if isinstance(result, dict):
        return str(result.get("result", result.get("answer", result)))

    return str(result)


@tool("Waits")
def waits(hospital: str) -> str:
    """Look up the wait time for a specific hospital.
    Supply the hospital name without the word 'hospital'
    when possible.
    """
    return get_current_wait_times(hospital)


@tool("Availability")
def availability(request: str) -> str:
    """Find the hospital with the shortest wait time.
    Use this when the user asks which hospital has the
    shortest current wait.
    """
    result = get_most_available_hospital(request)
    return str(result)


tools = [experiences, graph, waits, availability]

chat_model = ChatOllama(
    model=HOSPITAL_AGENT_MODEL,
    temperature=0,
    base_url="http://host.docker.internal:11434",
)

hospital_rag_agent = create_agent(
    model=chat_model,
    tools=tools,
    system_prompt=(
        "You are a hospital information assistant. "
        "Use the Experiences tool for qualitative patient-review "
        "questions. Use the Graph tool for structured questions "
        "about hospital data, counts, and statistics. Use the "
        "Waits tool for a specific hospital's wait time, and the "
        "Availability tool to find the hospital with the shortest "
        "wait. Do not invent tool results. Explain when information "
        "is unavailable. Wait-time results from the current demo "
        "implementation may be simulated rather than real."
    ),
)

# Keep the existing exported name for code that imports it.
# Note: create_agent uses the modern messages-based invoke interface.
hospital_rag_agent_executor = hospital_rag_agent
