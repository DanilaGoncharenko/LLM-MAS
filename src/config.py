import os
from __future__ import annotations

import os
from langchain_openai import ChatOpenAI



MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "qwen3-32b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-fhMGj3XMTsnLDUe__ClMLA")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://10.32.15.89:34000/v1")
NOTES_PATH = os.getenv("NOTES_PATH", "user_notes.json")


print("Model:", MODEL_NAME)
print("Base:", OPENAI_API_BASE)

def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    return ChatOpenAI(model=MODEL_NAME, temperature=temperature, openai_api_key=OPENAI_API_KEY, openai_api_base = OPENAI_API_BASE)