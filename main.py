"""
Paper Search AI Agent - FastAPI with ADK + MCP
Full integration with Vertex AI and paper-search MCP server
"""

import os
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "cloudrun-mcp-agent")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

import vertexai
vertexai.init(project=PROJECT_ID, location=LOCATION)

from paper_search_agent.agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Paper Search Agent")

session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="paper_search_app",
    session_service=session_service,
)

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"

class QueryResponse(BaseModel):
    query: str
    answer: str
    session_id: str

@app.get("/health")
def health():
    return {"status": "ok", "agent": root_agent.name}

@app.get("/")
def index():
    return {
        "service": "Paper Search Agent",
        "description": "AI research assistant powered by Google ADK + MCP",
    }

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    import uuid
    session_id = str(uuid.uuid4())
    user_id = request.user_id
    
    logger.info(f"Query: {request.query}")
    
    await session_service.create_session(
        app_name="paper_search_app",
        user_id=user_id,
        session_id=session_id,
    )
    
    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=request.query)],
    )
    
    answer_parts = []
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        answer_parts.append(part.text)
    except Exception as exc:
        logger.exception(f"Agent run failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}")
    
    answer = "".join(answer_parts).strip()
    if not answer:
        answer = "The agent did not return a response. Please try again."
    
    return QueryResponse(
        query=request.query,
        answer=answer,
        session_id=session_id
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)