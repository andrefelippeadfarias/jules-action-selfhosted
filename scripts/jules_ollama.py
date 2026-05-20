#!/usr/bin/env python3
import os, sys, json, pathlib, subprocess, requests

# Configurable host (default local Ollama)
OLLAMA_URL = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
# Choose a model that exists locally; adjust if needed
MODEL = os.getenv('OLLAMA_MODEL', 'deepseek-v4-flash')

def generate_code(prompt: str) -> str:
    payload = {
        'model': MODEL,
        'prompt': prompt,
        'stream': False,
        'max_tokens': 2048,
        'temperature': 0.2,
    }
    resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get('response', '')

def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: jules_ollama.py <prompt_file>')
    prompt_path = pathlib.Path(sys.argv[1])
    prompt = prompt_path.read_text()
    code = generate_code(prompt)
    # Write generated code for debugging
    Path('jules_output.txt').write_text(code)
    # Create a temporary branch for the changes (GitHub Action will handle PR creation later)
    # Here we just stage the generated file so the downstream step can create a diff/PR.
    pathlib.Path('generated_code.txt').write_text(code)
    subprocess.run(['git', 'add', 'generated_code.txt'], check=True)
    # Create a simple diff file (optional, for later steps)
    diff = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True).stdout
    pathlib.Path('jules_diff.patch').write_text(diff)

if __name__ == '__main__':
    main()
