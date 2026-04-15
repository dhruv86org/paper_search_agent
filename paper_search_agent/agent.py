"""
Paper Search AI Agent using Google ADK + MCP
Full integration with paper-search MCP server
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "cloudrun-mcp-agent")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://paper-search-mcp-openai-v2--titansneaker.run.tools/mcp",
)
SMITHERY_API_KEY = os.getenv(
    "SMITHERY_API_KEY",
    "YOUR_SMITHERY_API_KEY_HERE",
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE")

SYSTEM_INSTRUCTION = """You are a Research Assistant Agent that specializes in
finding and summarizing academic papers.

When a user asks about a research topic, you must:
1. Use the `search` tool (or the most appropriate source-specific tool) to
   retrieve relevant papers from the MCP server.
2. Examine the returned metadata (titles, authors, abstracts, publication
   dates, sources, URLs).
3. Synthesize the findings into a clear, structured summary that includes:
   - A brief overview of the research landscape for the topic.
   - A numbered list of the most relevant papers found, each with:
       * Title and authors
       * Source (e.g. arXiv, PubMed, Semantic Scholar)
       * Publication year
       * A 1-2 sentence plain-English summary of the paper's contribution
       * The paper URL or ID if available
   - Key trends or themes you notice across the papers.
4. If the user asks for papers from a specific source (arXiv, PubMed,
   bioRxiv, medRxiv, Semantic Scholar, Google Scholar, CrossRef, IACR),
   use the corresponding source-specific search tool.
5. If the user asks you to fetch the full text of a specific paper, use
   the `fetch` tool with the paper's ID.

Always be concise, accurate, and cite the data returned by the tools.
Do NOT invent paper titles or results - only use what the tools return.
"""

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def create_agent() -> LlmAgent:
    mcp_toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MCP_SERVER_URL,
            headers={
                "Authorization": f"Bearer {SMITHERY_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
    )

    agent = LlmAgent(
        name="paper_search_agent",
        description=(
            "An AI research assistant that searches academic databases "
            "(arXiv, PubMed, Semantic Scholar, bioRxiv, medRxiv, Google "
            "Scholar, CrossRef, IACR) via MCP and summarizes the results."
        ),
        instruction=SYSTEM_INSTRUCTION,
        tools=[mcp_toolset],
    )
    return agent

root_agent = create_agent()