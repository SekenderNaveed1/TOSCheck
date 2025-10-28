import os, json, math
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
_client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)
EMB_MODEL = os.environ.get("OLLAMA_EMB_MODEL", "nomic-embed-text")

def _embed_batch(texts: list[str]) -> np.ndarray:
    # simple loop; Ollama embeddings emulate OpenAI endpoint one-by-one
    out = []
    for t in tqdm(texts, desc=f"Embedding ({EMB_MODEL})"):
        resp = _client.embeddings.create(model=EMB_MODEL, input=t)
        out.append(resp.data[0].embedding)
    arr = np.array(out, dtype=np.float32)
    arr /= (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12)
    return arr

def build_and_save(chunks: list[str], out_dir: str = ".ragcache"):
    os.makedirs(out_dir, exist_ok=True)
    vecs = _embed_batch(chunks)
    np.save(os.path.join(out_dir, "embeddings.npy"), vecs)
    with open(os.path.join(out_dir, "chunks.json"), "w") as f:
        json.dump(chunks, f)

def load_index(out_dir: str = ".ragcache"):
    vecs = np.load(os.path.join(out_dir, "embeddings.npy"))
    with open(os.path.join(out_dir, "chunks.json")) as f:
        chunks = json.load(f)
    return {"embeddings": vecs, "chunks": chunks}


