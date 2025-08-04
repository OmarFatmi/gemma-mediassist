import json
from pathlib import Path
import ollama

def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def load_prompt(filename):
    return Path(f"prompts/{filename}").read_text(encoding="utf-8")

def query_gemma(prompt_template, **kwargs):
    full_prompt = prompt_template
    for k, v in kwargs.items():
        full_prompt = full_prompt.replace(f"{{{{{k}}}}}", v)
    response = ollama.chat(model="gemma:2b", messages=[{"role": "user", "content": full_prompt}])
    return response['message']['content'].strip()
def call_gemma(*args, prompt=None, **kwargs):
    """
    Wrapper to accept either:
      call_gemma(prompt=..., input=...)
    or
      call_gemma(prompt_template, input=...)
    """
    if prompt is not None:
        # prompt passed as keyword
        return query_gemma(prompt, **kwargs)
    # positional style: first arg is prompt_template
    return query_gemma(*args, **kwargs)