from __future__ import annotations
import os, hashlib
from typing import List, Dict, Tuple
import numpy as np
import ollama
import yaml
from .utils import EMBED_MODEL

# --------- tiny filesystem cache (no sqlite) ----------
# per-text vector stored as ~/.toscheck_cache/emb/<model>/<sha1>.npy
def _cache_dir() -> str:
    base = os.path.join(os.path.expanduser("~"), ".toscheck_cache", "emb", EMBED_MODEL.replace("/", "_"))
    os.makedirs(base, exist_ok=True)
    return base

def _key(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8", errors="ignore")).hexdigest()

def _load_cached(text: str) -> np.ndarray | None:
    path = os.path.join(_cache_dir(), _key(text) + ".npy")
    if os.path.exists(path):
        try:
            v = np.load(path)
            # normalize
            v = v.astype(np.float32)
            n = np.linalg.norm(v) + 1e-12
            return v / n
        except Exception:
            return None
    return None

def _save_cached(text: str, vec: np.ndarray) -> None:
    path = os.path.join(_cache_dir(), _key(text) + ".npy")
    try:
        np.save(path, vec.astype(np.float32))
    except Exception:
        pass

def _embed_one(text: str) -> np.ndarray:
    cached = _load_cached(text)
    if cached is not None:
        return cached
    r = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    v = np.array(r["embedding"], dtype=np.float32)
    n = np.linalg.norm(v) + 1e-12
    v = v / n
    _save_cached(text, v)
    return v

def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 768), dtype=np.float32)
    vecs = [_embed_one(t) for t in texts]
    return np.vstack(vecs)

def cosine_sim(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    # A: n x d, B: m x d (both normalized) -> n x m
    return A @ B.T

def load_seeds(path: str) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    out = {}
    for k, v in data.items():
        if isinstance(v, list):
            out[k] = [str(x).strip() for x in v if isinstance(x, (str, int, float))]
    return out

def rag_flag(sentences: List[str], seeds: Dict[str, List[str]], threshold: float = 0.75) -> List[Dict]:
    sents = [s.strip() for s in sentences if s.strip()]
    if not sents:
        return []
    S = embed_texts(sents)

    flags: List[Dict] = []
    for cat, examples in seeds.items():
        if not examples:
            continue
        E = embed_texts(examples)
        sims = cosine_sim(S, E)                 # n_sent x n_ex
        best = sims.max(axis=1)                 # best seed similarity per sentence
        hits = np.where(best >= threshold)[0].tolist()
        if not hits:
            continue
        flags.append({
            "category": cat,
            "sentence_indexes": hits,
            "rationale": f"Semantic match to exemplars ≥{threshold}.",
        })
    return flags
