import os
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = "cloudrun-mcp-agent"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

from google import genai

client = genai.Client(vertexai=True, project="cloudrun-mcp-agent", location="us-central1")
response = client.models.generate_content(
    model="gemini-1.5-flash-002",
    contents="Hello"
)
print("Success:", response.text)