#!/bin/bash

echo "🤖 Starting Ollama and checking for ${OLLAMA_MODEL} model..."

# Start ollama in background
ollama serve &
OLLAMA_PID=$!

# Wait for ollama to be ready
echo "⏳ Waiting for Ollama to start..."
while ! ollama list &> /dev/null; do
    sleep 1
done

echo "✅ Ollama is ready!"

# Check if qwen3:4b model exists
if ! ollama list | grep -q "${OLLAMA_MODEL}"; then
    echo "📥 Model ${OLLAMA_MODEL} not found. Downloading..."
    ollama pull ${OLLAMA_MODEL}
    echo "✅ Model ${OLLAMA_MODEL} downloaded successfully!"
else
    echo "✅ Model ${OLLAMA_MODEL} already exists."
fi

echo "🚀 Ollama setup complete!"

# Keep the process running
wait $OLLAMA_PID
