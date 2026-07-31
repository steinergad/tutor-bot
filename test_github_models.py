#!/usr/bin/env python
"""Test GitHub Models LLM connection"""

import os
import sys

# Load .env
from pathlib import Path
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().split('\n'):
        if '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip()

print("\n" + "="*60)
print("GITHUB MODELS LLM TEST")
print("="*60 + "\n")

# Check token
gh_token = os.getenv("GITHUB_TOKEN", "")
print(f"✓ GITHUB_TOKEN set: {bool(gh_token)}")
if gh_token:
    print(f"  Token length: {len(gh_token)} chars")
    print(f"  Token starts with: {gh_token[:10]}...")
    print(f"  Token ends with: ...{gh_token[-10:]}")
else:
    print("✗ NO GITHUB_TOKEN FOUND")
    sys.exit(1)

print("\n" + "-"*60)
print("Testing GitHub Models connection...")
print("-"*60 + "\n")

try:
    from langchain_openai import ChatOpenAI
    print("✓ langchain_openai imported")
except Exception as e:
    print(f"✗ Failed to import langchain_openai: {e}")
    sys.exit(1)

try:
    print("\nInitializing ChatOpenAI with GitHub Models...")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=gh_token,
        base_url="https://models.inference.ai.azure.com",
        temperature=0,
        streaming=True,
    )
    print("✓ LLM initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize LLM: {e}")
    sys.exit(1)

try:
    print("\nSending test message...")
    from langchain_core.messages import HumanMessage
    
    messages = [HumanMessage(content="Hello! Respond with just 'OK' to confirm.")]
    
    print("Waiting for response (this may take 10-30 seconds)...")
    response = llm.invoke(messages)
    print(f"✓ Got response: {response.content}")
    
except Exception as e:
    print(f"✗ Failed to get response: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✓ GitHub Models is working correctly!")
print("="*60 + "\n")
