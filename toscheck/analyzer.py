"""
analyzer.py — core logic for analyzing Terms of Service text using a local Llama model.
"""

from transformers import pipeline
import json

def load_llama(model_name="meta-llama/Llama-3.1-8B-Instruct"):
    """
    Loads a local Llama model for text generation.
    Uses 4-bit quantization automatically if bitsandbytes is installed.
    """
    print(f"🔧 Loading model: {model_name} ... this may take a minute the first time.")
    pipe = pipeline(
        "text-generation",
        model=model_name,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=True,
    )
    print("✅ Model ready.")
    return pipe


def build_prompt(text: str, mode="outline") -> str:
    """
    Builds a prompt for the model depending on mode:
    - 'outline': summarize main sections.
    - 'full': flag risky clauses.
    """
    if mode == "outline":
        return (
            "You are a legal analysis assistant. Read the following Terms of Service "
            "and produce a concise JSON outline of the main sections. "
            "Use the format:\n"
            "{ 'outline': [ {'title': '...', 'summary': '...'} ] }\n\n"
            f"Text:\n{text}\n\nReturn JSON only."
        )
    elif mode == "full":
        return (
            "You are a compliance assistant. Identify clauses that involve arbitration, "
            "data sharing, unilateral changes, vague permissions, or opt-outs. "
            "Return JSON:\n"
            "{ 'flags': [ {'type': '', 'evidence': '', 'why': ''} ] }\n\n"
            f"Text:\n{text}\n\nReturn JSON only."
        )
    else:
        raise ValueError("Invalid mode. Use 'outline' or 'full'.")


def run_llama(pipe, prompt: str, max_new_tokens=512):
    """
    Sends the prompt to the model and returns decoded text.
    """
    output = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=0.0,
        eos_token_id=pipe.tokenizer.eos_token_id,
    )
    return output[0]["generated_text"]


def safe_parse_json(output: str):
    """
    Tries to safely parse JSON from the model output.
    """
    try:
        return json.loads(output)
    except Exception:
        start = output.find("{")
        end = output.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(output[start:end + 1])
            except Exception:
                pass
        return {"error": "Invalid JSON", "raw_output": output}


def analyze_tos(text: str, model_name="meta-llama/Llama-3.1-8B-Instruct", mode="outline"):
    """
    Main function: load model, build prompt, run inference, parse JSON.
    """
    pipe = load_llama(model_name)
    prompt = build_prompt(text, mode)
    output = run_llama(pipe, prompt)
    return safe_parse_json(output)
