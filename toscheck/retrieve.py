import numpy as np
from toscheck.index import _embed_batch

def retrieve(query: str, data: dict, k: int = 6):
    qv = _embed_batch([query])[0]  # (d,)
    M = data["embeddings"]         # (n,d) normalized
    sims = M @ qv                  # cosine via dot
    idx = np.argsort(-sims)[:k]
    return [{"idx": int(i), "score": float(sims[i]), "chunk": data["chunks"][i]} for i in idx]


