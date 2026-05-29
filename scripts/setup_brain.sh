#!/bin/bash
set -e

echo "Creating models/llm/ directory..."
mkdir -p models/llm/

echo "Installing huggingface_hub and CPU-optimized llama-cpp-python..."
pip install huggingface_hub
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

echo "Downloading Qwen2.5-1.5B-Instruct-GGUF model..."
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct-GGUF qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir models/llm/ --local-dir-use-symlinks False

echo "Brain setup complete!"
