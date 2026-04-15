# Paper Search Agent — Google ADK + MCP

An AI research-assistant agent built with **Google Agent Development Kit (ADK)**
that connects to the **paper-search MCP server** (arXiv, PubMed, Semantic
Scholar, bioRxiv, medRxiv, Google Scholar, CrossRef, IACR) via the
**Model Context Protocol (MCP)** and returns structured academic-paper summaries.

---

## Architecture

```
User (HTTP POST /query)
        │
        ▼
  FastAPI  (main.py)          ← Cloud Run container
        │
        ▼
  Google ADK Runner
        │
        ▼
  LlmAgent  (Gemini 2.5 Flash via Vertex AI)
        │   uses
        ▼
  McpToolset  ──── Streamable HTTP ────►  paper-search MCP server
  (ADK MCP client)                        (arXiv / PubMed / Semantic Scholar
                                           bioRxiv / medRxiv / Scholar / …)
```

**Key design decisions**

| Concern | Choice |
|---|---|
| Framework | Google ADK (`google-adk[vertexai]`) |
| LLM | `gemini-2.5-flash-lite` via Vertex AI with API key |
| Auth | Vertex AI API key (`GOOGLE_API_KEY`) |
| MCP transport | Streamable HTTP (`StreamableHTTPConnectionParams`) |
| MCP auth | Bearer token (Smithery API key) |
| API server | FastAPI + Uvicorn |
| Deployment | Google Cloud Run (fully managed) |

---

## Project layout

```
.
├── paper_search_agent/
│   ├── __init__.py       # makes the directory a Python package
│   └── agent.py          # ADK LlmAgent + McpToolset definition
├── main.py               # FastAPI app + ADK Runner
├── requirements.txt       # Python dependencies
├── Dockerfile            # Multi-stage build for Cloud Run
├── deploy.sh             # one-shot Cloud Build + Cloud Run deploy
├── .env.example          # copy to .env for local dev
├── cloudbuild.yaml       # Cloud Build configuration
└── README.md
```

---

## Deployment Status

✅ **Deployed to Cloud Run:**
- **URL**: https://paper-search-agent-234338064518.us-central1.run.app
- **Region**: us-central1
- **Status**: Fully operational with MCP integration

---

## Local development

### 1. Install dependencies

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Note**: Requires Python 3.10+ (MCP package requirement)

### 2. Set environment variables

Create a `.env` file or set these environment variables:

```bash
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
export GOOGLE_CLOUD_PROJECT="cloudrun-mcp-agent"
export GOOGLE_CLOUD_LOCATION="us-central1"
export MCP_SERVER_URL="https://paper-search-mcp-openai-v2--titansneaker.run.tools/mcp"
export SMITHERY_API_KEY="YOUR_SMITHERY_API_KEY_HERE"
```

### 3. Run locally

```bash
uvicorn main:app --reload --port 8080
```

### 4. Test

```bash
# Health check
curl http://localhost:8080/health

# Service info
curl http://localhost:8080/

# Research query
curl -X POST http://localhost:8080/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the latest papers on transformer architectures?"}'
```

---

## Deploy to Cloud Run

### Prerequisites

- `gcloud` CLI installed and authenticated
- GCP project `cloudrun-mcp-agent` with billing enabled
- Vertex AI API enabled in the project
- The Cloud Run service account has necessary IAM roles

### Option 1: Using Docker (local build)

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/cloudrun-mcp-agent/paper-search/agent:latest .

# Deploy to Cloud Run
gcloud run deploy paper-search-agent \
  --image us-central1-docker.pkg.dev/cloudrun-mcp-agent/paper-search/agent:latest \
  --region us-central1 \
  --project cloudrun-mcp-agent \
  --allow-unauthenticated \
  --min-instances=1 \
  --set-env-vars GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE \
  --set-env-vars GOOGLE_CLOUD_PROJECT=cloudrun-mcp-agent \
  --set-env-vars GOOGLE_CLOUD_LOCATION=us-central1 \
  --set-env-vars MCP_SERVER_URL=https://paper-search-mcp-openai-v2--titansneaker.run.tools/mcp \
  --set-env-vars SMITHERY_API_KEY=YOUR_SMITHERY_API_KEY_HERE
```

### Option 2: Cloud Run source deploy (no Docker needed)

```bash
gcloud run deploy paper-search-agent \
  --source . \
  --region us-central1 \
  --project cloudrun-mcp-agent \
  --allow-unauthenticated
```

### Environment variables for Cloud Run

| Variable | Value | Description |
|---|---|---|
| `GOOGLE_API_KEY` | `YOUR_GOOGLE_API_KEY_HERE` | Vertex AI API key |
| `GOOGLE_CLOUD_PROJECT` | `cloudrun-mcp-agent` | GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Vertex AI region |
| `MCP_SERVER_URL` | (see above) | paper-search MCP endpoint |
| `SMITHERY_API_KEY` | (see above) | Bearer token for MCP server |

---

## API Reference

### `GET /health`
Liveness probe.

```json
{"status": "ok", "agent": "paper_search_agent"}
```

### `GET /`
Service info and endpoint listing.

```json
{
  "service": "Paper Search Agent",
  "description": "AI research assistant powered by Google ADK + MCP"
}
```

### `POST /query`

**Request body**
```json
{
  "query": "What are the latest advances in protein structure prediction?",
  "user_id": "optional-user-id"
}
```

**Response**
```json
{
  "query": "What are the latest advances in protein structure prediction?",
  "answer": "I am searching for papers on protein structure prediction...\n\nHere are the relevant papers:\n\n1. \"AlphaFold...\" [more details]\n\n[additional papers...]",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## MCP Tools Available

The agent has access to all tools exposed by the paper-search MCP server:

| Tool | Description |
|---|---|
| `search` | Aggregate search across all sources |
| `fetch` | Fetch full document content by ID |
| `search_arxiv` | arXiv-specific search |
| `search_pubmed` | PubMed-specific search |
| `search_biorxiv` | bioRxiv-specific search |
| `search_medrxiv` | medRxiv-specific search |
| `search_semantic` | Semantic Scholar search |
| `search_google_scholar` | Google Scholar search |
| `search_iacr` | IACR ePrint Archive search |
| `search_crossref` | CrossRef database search |
| `download_arxiv` | Download arXiv paper PDF |
| `read_arxiv_paper` | Extract text from arXiv paper |

---

## Testing the Deployed Service

### Quick Test

```bash
curl -X POST 'https://paper-search-agent-234338064518.us-central1.run.app/query' \
  -H 'Content-Type: application/json' \
  -d '{"query": "What are the latest papers on transformer architectures?"}'
```

### Expected Response

```json
{
  "query": "What are the latest papers on transformer architectures?",
  "answer": "I am searching for papers on transformer architectures.\nI found 10 papers related to transformer architectures.\n\nHere's a summary of the research landscape and relevant papers:\n\nTransformer architectures have become a cornerstone...\n\n1. \"Attention Is All You Need\" by Ashish Vaswani...\n   Source: arXiv\n   Year: 2017\n   ...\n\n[additional papers with details]",
  "session_id": "[uuid]"
}
```

### Test Other Topics

```bash
# Test with different research topics
curl -X POST 'https://paper-search-agent-234338064518.us-central1.run.app/query' \
  -H 'Content-Type: application/json' \
  -d '{"query": "machine learning healthcare applications"}'

curl -X POST 'https://paper-search-agent-234338064518.us-central1.run.app/query' \
  -H 'Content-Type: application/json' \
  -d '{"query": "quantum computing recent advances"}'

curl -X POST 'https://paper-search-agent-234338064518.us-central1.run.app/query' \
  -H 'Content-Type: application/json' \
  -d '{"query": "CRISPR gene editing papers"}'
```

---

## Troubleshooting

### Container fails to start

If you see "container failed to start" errors:
- Check the Dockerfile has correct Python version (3.11-slim recommended)
- Ensure requirements are installed correctly in the build
- Verify PORT environment variable is set to 8080

### MCP Connection Errors

If the agent fails to connect to the MCP server:
- Verify `MCP_SERVER_URL` is correct
- Check `SMITHERY_API_KEY` is valid
- Ensure the MCP server is accessible from Cloud Run

### Vertex AI API Errors

If you see API key or permission errors:
- Verify `GOOGLE_API_KEY` is set correctly
- Ensure the API key has access to Vertex AI
- Check that the Gemini API is enabled in your GCP project

### Health Check Works but Query Fails

```bash
# Check health first
curl https://paper-search-agent-234338064518.us-central1.run.app/health

# If health is OK but query fails, check logs
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="paper-search-agent"' --project=cloudrun-mcp-agent --limit=50
```

---

## Files Modified During Development

The following files were created/updated during the deployment process:

- `main.py` - FastAPI app with ADK Runner integration
- `paper_search_agent/agent.py` - LlmAgent with MCP toolset
- `requirements.txt` - Python dependencies (mcp, google-adk, fastapi, etc.)
- `Dockerfile` - Multi-stage build configuration
- `cloudbuild.yaml` - Cloud Build configuration (if used)

---

## License

This project is for educational/research purposes.