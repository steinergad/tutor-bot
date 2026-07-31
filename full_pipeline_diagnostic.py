#!/usr/bin/env python3
"""
Complete Pipeline Diagnostic
Systematically checks every component
"""

import os
import sys
from pathlib import Path

print("╔" + "═" * 70 + "╗")
print("║" + " COMPLETE PIPELINE DIAGNOSTIC ".center(70) + "║")
print("╚" + "═" * 70 + "╝\n")

# ════════════════════════════════════════════════════════════════════════════
# 1. ENVIRONMENT & DEPENDENCIES
# ════════════════════════════════════════════════════════════════════════════

print("1️⃣  CHECKING ENVIRONMENT & DEPENDENCIES")
print("─" * 70)

issues = []

# Check Python version
py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print(f"   Python: {py_version} ✓")

# Check required packages
required_packages = {
    "streamlit": "Streamlit UI",
    "langchain": "LLM chains",
    "langchain_core": "LangChain core",
    "langchain_openai": "OpenAI integration",
    "dotenv": "Env config",
    "networkx": "Graph algorithms",
}

for pkg, desc in required_packages.items():
    try:
        __import__(pkg)
        print(f"   {pkg}: ✓ ({desc})")
    except ImportError:
        print(f"   {pkg}: ✗ MISSING ({desc})")
        issues.append(f"Missing package: {pkg}")

# Check API keys
print(f"\n   API Keys:")
openai_key = os.getenv("OPENAI_API_KEY", "")
github_token = os.getenv("GITHUB_TOKEN", "")
ollama_url = os.getenv("OLLAMA_BASE_URL", "")

if openai_key.startswith("sk-"):
    print(f"      OPENAI_API_KEY: ✓ (found)")
else:
    print(f"      OPENAI_API_KEY: ✗ NOT SET or invalid")
    issues.append("OPENAI_API_KEY not configured")

if github_token.startswith("github_pat_") or github_token.startswith("ghp_"):
    print(f"      GITHUB_TOKEN: ✓ (found)")
else:
    print(f"      GITHUB_TOKEN: ✗ NOT SET or invalid")

if ollama_url:
    print(f"      OLLAMA_BASE_URL: ✓ ({ollama_url})")
else:
    print(f"      OLLAMA_BASE_URL: ✗ Not configured (using OpenAI)")

# ════════════════════════════════════════════════════════════════════════════
# 2. DATA FILES & DATABASES
# ════════════════════════════════════════════════════════════════════════════

print("\n2️⃣  CHECKING DATA FILES & DATABASES")
print("─" * 70)

db_dir = Path("db")
required_files = {
    "db/homework.json": "Homework definitions",
    "db/metadata.json": "Tutorial metadata",
    "db/knowledge_graph.db": "Graph RAG database",
    "db/entities.json": "Entity definitions",
    "db/relationships.json": "Relationship mappings",
}

for file_path, desc in required_files.items():
    path = Path(file_path)
    if path.exists():
        size = path.stat().st_size
        print(f"   {file_path}: ✓ ({size:,} bytes) - {desc}")
    else:
        print(f"   {file_path}: ✗ MISSING - {desc}")
        if "db/" in file_path:
            issues.append(f"Missing: {file_path}")

# ════════════════════════════════════════════════════════════════════════════
# 3. KNOWLEDGE GRAPH
# ════════════════════════════════════════════════════════════════════════════

print("\n3️⃣  CHECKING KNOWLEDGE GRAPH")
print("─" * 70)

try:
    from graph_rag_starter import LightweightKnowledgeGraph
    
    kg = LightweightKnowledgeGraph("db/knowledge_graph.db")
    stats = kg.stats()
    
    print(f"   Graph loaded: ✓")
    print(f"   Entities: {stats['num_entities']}")
    print(f"   Relationships: {stats['num_relationships']}")
    print(f"   Density: {stats['density']:.4f}")
    
    # Test entity retrieval
    test_entity = kg.find_entity_by_name("Recursion")
    if test_entity:
        print(f"   Entity lookup (Recursion): ✓")
    else:
        print(f"   Entity lookup (Recursion): ✗ NOT FOUND")
        issues.append("Cannot find 'Recursion' entity in graph")
        
    kg.conn.close()
    
except Exception as e:
    print(f"   Graph loading: ✗ ERROR")
    print(f"   Error: {e}")
    issues.append(f"Knowledge graph error: {e}")

# ════════════════════════════════════════════════════════════════════════════
# 4. PROMPT SYSTEM
# ════════════════════════════════════════════════════════════════════════════

print("\n4️⃣  CHECKING PROMPT SYSTEM")
print("─" * 70)

try:
    from prompts.prompt_builder import build_tutorial_prompt, build_homework_prompt
    
    # Test tutorial prompt
    test_tutorial = build_tutorial_prompt(
        topics_list="• Topic 1\n• Topic 2",
        tutorial_label="Tutorial 1",
        topic_context="Some context"
    )
    if "Socratic" in test_tutorial or "tutor" in test_tutorial.lower():
        print(f"   build_tutorial_prompt: ✓")
    else:
        print(f"   build_tutorial_prompt: ⚠️  Output seems incomplete")
        
    # Test homework prompt
    test_homework = build_homework_prompt(
        concepts_list="• Concept 1\n• Concept 2",
        hw_title="Homework 1",
        hw_description="Test",
        key_concepts="• Key 1"
    )
    if "Socratic" in test_homework or "student" in test_homework.lower():
        print(f"   build_homework_prompt: ✓")
    else:
        print(f"   build_homework_prompt: ⚠️  Output seems incomplete")
        
except Exception as e:
    print(f"   Prompt system: ✗ ERROR")
    print(f"   Error: {e}")
    issues.append(f"Prompt system error: {e}")

# ════════════════════════════════════════════════════════════════════════════
# 5. HOMEWORK VALIDATION
# ════════════════════════════════════════════════════════════════════════════

print("\n5️⃣  CHECKING HOMEWORK VALIDATION")
print("─" * 70)

try:
    from homework_validation import is_in_scope, get_homework_scope
    
    # Test scope retrieval
    scope = get_homework_scope("hw_3")
    if scope.get("topics"):
        print(f"   get_homework_scope: ✓ (found {len(scope['topics'])} topics)")
    else:
        print(f"   get_homework_scope: ✗ No topics found")
        issues.append("Homework scope retrieval failed")
    
    # Test in-scope validation (English)
    is_valid, reason = is_in_scope("How do I solve Fibonacci?", "hw_3")
    print(f"   is_in_scope (English): {'✓' if is_valid else '✗'} (Fibonacci)")
    
    # Test in-scope validation (Hebrew)
    is_valid, reason = is_in_scope("איך אני פותר בעיות דינמיות?", "hw_3")
    print(f"   is_in_scope (Hebrew): {'✓' if is_valid else '✗'} (Dynamic Programming)")
    
except Exception as e:
    print(f"   Homework validation: ✗ ERROR")
    print(f"   Error: {e}")
    issues.append(f"Homework validation error: {e}")

# ════════════════════════════════════════════════════════════════════════════
# 6. LANGUAGE SUPPORT
# ════════════════════════════════════════════════════════════════════════════

print("\n6️⃣  CHECKING LANGUAGE SUPPORT")
print("─" * 70)

try:
    from language_config import get_text, LANGUAGES
    
    print(f"   Supported languages: {list(LANGUAGES.keys())}")
    
    # Test English text
    en_text = get_text("en", "select_mode")
    if en_text:
        print(f"   get_text('en'): ✓")
    else:
        print(f"   get_text('en'): ✗ No text found")
        
    # Test Hebrew text
    he_text = get_text("he", "select_mode")
    if he_text:
        print(f"   get_text('he'): ✓")
    else:
        print(f"   get_text('he'): ✗ No text found")
        
except Exception as e:
    print(f"   Language support: ✗ ERROR")
    print(f"   Error: {e}")
    issues.append(f"Language support error: {e}")

# ════════════════════════════════════════════════════════════════════════════
# 7. LLM CONNECTIVITY TEST
# ════════════════════════════════════════════════════════════════════════════

print("\n7️⃣  CHECKING LLM CONNECTIVITY")
print("─" * 70)

def test_llm_connection():
    """Test if LLM is accessible without making actual API calls"""
    try:
        # Check for OpenAI
        if openai_key.startswith("sk-"):
            print(f"   OpenAI: ✓ (API key configured)")
            return True
            
        # Check for GitHub Models
        if github_token and (github_token.startswith("github_pat_") or github_token.startswith("ghp_")):
            print(f"   GitHub Models: ✓ (Token configured)")
            return True
            
        # Check for Ollama
        if ollama_url:
            print(f"   Ollama: ✓ (URL configured at {ollama_url})")
            return True
            
        print(f"   ✗ NO LLM CONFIGURED")
        return False
        
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False

llm_ok = test_llm_connection()
if not llm_ok:
    issues.append("No LLM provider configured (need OPENAI_API_KEY, GITHUB_TOKEN, or OLLAMA_BASE_URL)")

# ════════════════════════════════════════════════════════════════════════════
# 8. SEARCH SYSTEM
# ════════════════════════════════════════════════════════════════════════════

print("\n8️⃣  CHECKING SEARCH SYSTEM")
print("─" * 70)

try:
    from search_integration import init_search, find_relevant_topics
    
    # Don't actually initialize (would create resources), just check if importable
    print(f"   search_integration: ✓")
    
except Exception as e:
    print(f"   search_integration: ⚠️  Import warning: {str(e)[:50]}...")

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("DIAGNOSTIC SUMMARY")
print("═" * 70)

if not issues:
    print("\n✅ ALL SYSTEMS OPERATIONAL\n")
    print("The pipeline is fully configured and ready to run!")
    print("\nTo start the app:")
    print("  streamlit run app.py\n")
    sys.exit(0)
else:
    print(f"\n⚠️  FOUND {len(issues)} ISSUE(S):\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    print("\n" + "─" * 70)
    print("REQUIRED FIXES:")
    print("─" * 70)
    
    if any("API_KEY" in issue for issue in issues):
        print("\n🔑 API KEY CONFIGURATION")
        print("   Set one of:")
        print("     export OPENAI_API_KEY=sk-...")
        print("     export GITHUB_TOKEN=github_pat_...")
        print("     export OLLAMA_BASE_URL=http://localhost:11434")
    
    if any("Missing package" in issue for issue in issues):
        print("\n📦 INSTALL MISSING PACKAGES")
        print("   pip install streamlit langchain langchain-openai")
    
    if any("Missing:" in issue for issue in issues):
        print("\n📁 REBUILD MISSING DATA FILES")
        print("   python build_knowledge_graph.py --all")
    
    print("\n")
    sys.exit(1)
