#!/bin/bash
echo "🚀 Starting UTelcom Evaluation Environment..."

# 1. Spin up the orchestrator
docker-compose up -d --build

echo "⏳ Waiting for Ollama server to initialize..."
sleep 5

# 2. Pull the model inside the Ollama container
echo "🧠 Downloading llama3.2 model (this may take a minute)..."
docker exec utelcom_ollama ollama pull llama3.2

# 3. Execute the Agentic Workflow
echo "✅ Environment Ready. Executing Task 1 Agent..."
docker exec utelcom_agent python task1/solution.py

echo "🏁 Evaluation run complete."