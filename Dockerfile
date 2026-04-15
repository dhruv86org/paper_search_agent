FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    mcp>=1.0.0 \
    google-adk[vertexai]>=1.0.0 \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    httpx>=0.27.0 \
    httpx-sse>=0.4.0 \
    requests>=2.31.0

COPY paper_search_agent/ ./paper_search_agent/
COPY main.py .

ENV PORT=8080

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]