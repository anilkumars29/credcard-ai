# CODE ARTIFACT: ai_engine.py
# SYSTEM MODULE: OLLAMA NETWORK INTERACTION HOOK

import requests
import json
from ai_training import TRAINING_PROMPT_TEMPLATE

def query_qwen_underwriter(context_metrics, user_query):
    """
    Formulates context wrappers and posts payload payloads directly to the Ollama server.
    """
    url = "http://127.0.0.1:11434/api/chat"
    
    payload = {
        "model": "llama3.2:latest", 
        "messages": [
            {
                "role": "system",
                "content": TRAINING_PROMPT_TEMPLATE
            },
            {
                "role": "user",
                "content": f"Applicant Dossier Profile Parameters:\n{json.dumps(context_metrics, indent=2)}\n\nInquiry Directive: {user_query}"
            }
        ],
        "stream": False
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"⚠️ Ollama Core Fault: Received status registration flag {response.status_code}"
    except Exception as e:
        return f"🚨 Loopback connection failed. Trace: {str(e)}"