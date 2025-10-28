from __future__ import annotations
import os

# Model selection
# Honor environment variable first; fall back to a sane small default for CPU
MODEL = os.environ.get("TOSCHECK_MODEL") or "llama3.2:1b"

# Generation defaults (kept conservative for classification tasks)
NUM_CTX = int(os.environ.get("TOSCHECK_NUM_CTX", "2048"))
TEMPERATURE = float(os.environ.get("TOSCHECK_TEMPERATURE", "0.0"))
TOP_P = float(os.environ.get("TOSCHECK_TOP_P", "0.9"))

# Embedding model for RAG (Ollama embedding)
EMBED_MODEL = os.environ.get("TOSCHECK_EMBED_MODEL") or "nomic-embed-text:latest"

# Small utility to expose effective config (optional)
def effective_model():
    return MODEL
