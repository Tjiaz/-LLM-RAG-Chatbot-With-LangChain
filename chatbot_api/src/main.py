from fastapi import FastAPI

from agents.hospital_rag_agent import hospital_rag_agent_executor
from models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput
from utils.async_utils import async_retry

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital system graph RAG chatbot",
)


@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query: str):
    """Retry the agent if a tool fails to run."""
    return await hospital_rag_agent_executor.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )


@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/hospital-rag-agent")
async def query_hospital_agent(
    query: HospitalQueryInput,
) -> HospitalQueryOutput:
    query_response = await invoke_agent_with_retry(query.text)

    messages = query_response.get("messages", [])

    # Find the final assistant message.
    assistant_messages = [
        message
        for message in messages
        if getattr(message, "type", None) == "ai"
    ]

    if not assistant_messages:
        raise ValueError("The agent returned no assistant response.")

    final_message = assistant_messages[-1]

    final_content = final_message.content

    if isinstance(final_content, str):
            answer = final_content
    else:
            answer = str(final_content)

    return HospitalQueryOutput(
            input=query.text,
            output=answer,
            intermediate_steps=[
                str(message.tool_calls)
                for message in messages
                if getattr(message, "tool_calls", None)
            ],
        )
