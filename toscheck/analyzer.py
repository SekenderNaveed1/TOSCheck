import subprocess
import json


def analyze_tos(text, model="llama3"):
    prompt = f"Analyze the following Terms of Service and flag sections that involve arbitration, data sharing, unilateral changes, or vague permissions. Respond in JSON: {{'flags': [{{'type': '', 'excerpt': ''}}]}}.\n\n{text}"
    
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True
    )
    return result.stdout.decode("utf-8")