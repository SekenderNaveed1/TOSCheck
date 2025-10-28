import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

GEN_MODEL = os.environ.get("OLLAMA_GEN_MODEL", "llama3.1:8b")
_client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)

def answer_with_rag(query: str, retrieved: list[dict], temperature: float = 0.0) -> str:
    context = "\n\n---\n\n".join(f"[{r['idx']}] {r['chunk']}" for r in retrieved)
    prompt = f"""You are analyzing Terms of Service. Use ONLY the context and cite by [chunk_id].
Question: {query}

Context:
{context}

Answer with:
- 3–8 concise bullets of findings
- exact short quotes (<= 25 words) with [chunk_id]
- a final 1–2 sentence summary
If the answer is not in the context, say: "Not found in provided context."
"""
    resp = _client.chat.completions.create(
        model=GEN_MODEL,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()



