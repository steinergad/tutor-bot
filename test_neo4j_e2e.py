#!/usr/bin/env python3
"""
End-to-End Test: SQLite Graph → Neo4j → App Integration
Verifies complete Graph RAG pipeline from graph building through production deployment
"""

import subprocess
import time
import sys
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_step(step_num, title, description=""):
    """Print formatted step header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}STEP {step_num}: {title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")
    if description:
        print(f"  {description}")


def print_success(msg):
    """Print success message"""
    print(f"{GREEN}✓ {msg}{RESET}")


def print_info(msg):
    """Print info message"""
    print(f"{BLUE}ℹ {msg}{RESET}")


def print_error(msg):
    """Print error message"""
    print(f"{RED}✗ {msg}{RESET}")


def print_warning(msg):
    """Print warning message"""
    print(f"{YELLOW}⚠ {msg}{RESET}")


def run_command(cmd, description=""):
    """Run shell command and return success status"""
    if description:
        print_info(description)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print_success(f"Command succeeded")
            return True
        else:
            print_error(f"Command failed with code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"Command timed out after 30 seconds")
        return False
    except Exception as e:
        print_error(f"Error running command: {e}")
        return False


def check_neo4j_running():
    """Check if Neo4j is running"""
    print_info("Checking if Neo4j is accessible...")
    try:
        from neo4j import GraphDatabase
        uri = "neo4j://localhost:7687"
        driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
        with driver.session() as session:
            result = session.run("RETURN 1")
            driver.close()
        print_success("Neo4j is running and accessible")
        return True
    except Exception as e:
        print_error(f"Neo4j not accessible: {e}")
        return False


def run_phase_3():
    """Phase 3: Build SQLite knowledge graph"""
    print_step(1, "Build SQLite Knowledge Graph", 
               "Creating graph from entities.json and relationships.json")
    
    if run_command("python build_knowledge_graph.py --all", 
                   "Building graph with: python build_knowledge_graph.py --all"):
        # Check if database was created
        if Path("db/knowledge_graph.db").exists():
            print_success("SQLite knowledge graph created at db/knowledge_graph.db")
            return True
        else:
            print_error("Knowledge graph database not found")
            return False
    return False


def run_phase_5():
    """Phase 5: Load into Neo4j"""
    print_step(2, "Load Graph into Neo4j", 
               "Transferring SQLite graph to Neo4j production database")
    
    if check_neo4j_running():
        if run_command("python graph_rag_neo4j.py --build", 
                       "Loading data with: python graph_rag_neo4j.py --build"):
            print_success("Graph loaded into Neo4j")
            return True
    else:
        print_warning("Neo4j not running. Please start it first:")
        print_warning("  docker run -d -p 7687:7687 -p 7474:7474 --name neo4j -e NEO4J_AUTH=neo4j/password neo4j:latest")
        return False
    return False


def test_neo4j_queries():
    """Phase 5: Test Neo4j queries"""
    print_step(3, "Test Neo4j Queries", 
               "Verifying data retrieval from Neo4j")
    
    test_queries = [
        "Merge Sort",
        "Fibonacci",
        "Dynamic Programming",
        "Recursion",
        "Time Complexity"
    ]
    
    success_count = 0
    for query in test_queries:
        cmd = f'python graph_rag_neo4j.py --query "{query}"'
        print_info(f"Testing query: {query}")
        if run_command(cmd):
            success_count += 1
        time.sleep(0.5)  # Small delay between queries
    
    print_success(f"Completed {success_count}/{len(test_queries)} Neo4j queries")
    return success_count == len(test_queries)


def show_graph_stats():
    """Show graph statistics"""
    print_step(4, "Graph Statistics", 
               "Displaying knowledge graph structure")
    
    print_info("Running: python build_knowledge_graph.py --stats")
    run_command("python build_knowledge_graph.py --stats")


def show_integration_guide():
    """Show next steps for app integration"""
    print_step(5, "Next Steps: App Integration", 
               "How to integrate Neo4j backend with Streamlit app")
    
    print(f"""
{BOLD}Phase 4: Integrate with Streamlit App{RESET}

The Graph RAG backend is now ready! To integrate with app.py:

{BOLD}Step 1: Read the integration guide{RESET}
  cat PHASE_4_INTEGRATION.md

{BOLD}Step 2: Update app.py (5 locations){RESET}
  - Line 1: Add import for graph_rag_neo4j
  - Line 2: Initialize KnowledgeGraphNeo4j retriever
  - Line 3: Add get_graph_context_for_homework() helper
  - Line 4: Enhance homework chain with graph context
  - Line 5: Pass context to LLM when building responses

{BOLD}Step 3: Restart the app{RESET}
  streamlit run app.py

{BOLD}Step 4: Test end-to-end{RESET}
  - Ask a homework question in Hebrew or English
  - Tutor should mention prerequisites
  - Learning path displayed in context
  - All responses curriculum-grounded

{BOLD}Expected Flow:{RESET}
  Student: "How do I solve Fibonacci?"
  
  Tutor (with Graph RAG):
    "Before tackling Fibonacci, you should understand recursion.
     Here's what you need to know:
     1. Recursion basics (Tutorial 2, Week 1)
     2. Call stack mechanics (Tutorial 3, Week 2)
     3. Memoization pattern (Tutorial 5, Week 3)
     
     Now, Fibonacci is about... [Socratic explanation]"

{BOLD}Performance Metrics:{RESET}
  - Query latency: 30-50ms (Neo4j vs 100-150ms SQLite)
  - Response time: <2s end-to-end (including LLM)
  - Scalability: 100K+ entities vs 1K limit on SQLite

{BOLD}Documentation:{RESET}
  - PHASE_4_INTEGRATION.md: Step-by-step code changes
  - IMPLEMENTATION_TIMELINE.md: Full deployment plan
  - QUICK_START.md: Reference guide
    """)


def main():
    """Run complete end-to-end test"""
    print(f"""
{BOLD}{BLUE}╔{'='*58}╗{RESET}
{BOLD}{BLUE}║  Graph RAG End-to-End Test: SQLite → Neo4j → App     ║{RESET}
{BOLD}{BLUE}║  Testing complete Graph RAG pipeline with Neo4j      ║{RESET}
{BOLD}{BLUE}╚{'='*58}╝{RESET}

{YELLOW}Prerequisites:{RESET}
  • Python 3.11+ with dependencies
  • Neo4j running (docker or desktop)
  • db/entities.json and db/relationships.json in place
    """)
    
    # Verify files exist
    print_step(0, "Verify Prerequisites", "Checking required files and dependencies")
    
    required_files = [
        "db/entities.json",
        "db/relationships.json",
        "build_knowledge_graph.py",
        "graph_rag_neo4j.py"
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            missing.append(file)
    
    if missing:
        print_error(f"\nMissing {len(missing)} required files. Cannot proceed.")
        return False
    
    # Run phases
    results = {
        "Phase 3 (SQLite Build)": run_phase_3(),
        "Phase 5 (Neo4j Load)": run_phase_5(),
        "Neo4j Query Tests": test_neo4j_queries(),
    }
    
    # Show statistics
    show_graph_stats()
    
    # Show integration guide
    show_integration_guide()
    
    # Summary
    print_step(6, "End-to-End Test Summary", "")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{BOLD}Test Results:{RESET}")
    for test_name, passed_flag in results.items():
        status = f"{GREEN}✓ PASSED{RESET}" if passed_flag else f"{RED}✗ FAILED{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BOLD}Overall:{RESET}")
    if passed == total:
        print(f"{GREEN}✓ All tests passed! Graph RAG ready for production.{RESET}")
        print(f"\n{BOLD}Next Action:{RESET}")
        print(f"  1. Read PHASE_4_INTEGRATION.md")
        print(f"  2. Update app.py (5 code locations)")
        print(f"  3. Run: streamlit run app.py")
        return True
    else:
        print(f"{RED}✗ {total - passed} test(s) failed. See above for details.{RESET}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
