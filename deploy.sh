#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID=cloudrun-mcp-agent
REGION=us-central1
SERVICE_NAME=paper-search-agent
IMAGE=us-central1-docker.pkg.dev/${PROJECT_ID}/paper-search/agent:latest

MCP_SERVER_URL=https://paper-search-mcp-openai-v2--titansneaker.run.tools/mcp
SMITHERY_API_KEY=YOUR_SMITHERY_API_KEY_HERE

gcloud config set project ${PROJECT_ID}

gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com --project=${PROJECT_ID}

gcloud builds submit --tag ${IMAGE} --project=${PROJECT_ID} .

gcloud run deploy ${SERVICE_NAME} --image ${IMAGE} --region ${REGION} --platform managed --allow-unauthenticated --memory 1Gi --cpu 1 --concurrency 80 --timeout 300 --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID} --set-env-vars GOOGLE_CLOUD_LOCATION=${REGION} --set-env-vars MCP_SERVER_URL=${MCP_SERVER_URL} --set-env-vars SMITHERY_API_KEY=${SMITHERY_API_KEY} --project=${PROJECT_ID}

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID} --format value(status.url))
echo Service URL: ${SERVICE_URL}
echo Test: curl -X POST ${SERVICE_URL}/query -H 'Content-Type: application/json' -d '{}'