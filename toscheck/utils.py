from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.getenv("MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
NUM_CTX = int(os.getenv("NUM_CTX", "8192"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
BANNER = "[bold]TOSCheck[/bold] — local-first TOS flagger."
