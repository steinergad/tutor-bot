import os
from dotenv import load_dotenv

load_dotenv()
provider = os.getenv('LLM_PROVIDER', 'openai').lower()
print(f'PROVIDER: {provider}')
print(f'OLLAMA_BASE_URL: {os.getenv("OLLAMA_BASE_URL", "NOT SET")}')
print(f'OLLAMA_LLM_MODEL: {os.getenv("OLLAMA_LLM_MODEL", "NOT SET")}')
