"""
test_search_comparison.py — Test suite for comparing metadata.json search vs RAG (vector DB)

This script evaluates both search methods against a fixed set of 10-15 questions
to determine which approach is more accurate and efficient for the tutoring bot.

Usage:
  python test_search_comparison.py

This is a standard ML project evaluation methodology: create a test set,
run both methods, compare metrics (accuracy, latency, resource usage).
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Any
import re


# Test questions designed to evaluate search quality
TEST_QUESTIONS = [
    {
        "id": "q1",
        "question": "What is Big O notation?",
        "expected_topics": ["Big O notation", "Asymptotic analysis"],
        "tutorial": "tutorial_1",
        "difficulty": "basic"
    },
    {
        "id": "q2",
        "question": "Explain the difference between O(n) and O(n²) complexity",
        "expected_topics": ["Asymptotic analysis", "Time complexity"],
        "tutorial": "tutorial_1",
        "difficulty": "basic"
    },
    {
        "id": "q3",
        "question": "What is dynamic programming and when do you use it?",
        "expected_topics": ["Dynamic Programming", "Overlapping subproblems"],
        "tutorial": "tutorial_3",
        "difficulty": "intermediate"
    },
    {
        "id": "q4",
        "question": "How does Dijkstra's algorithm work?",
        "expected_topics": ["Shortest paths", "Graph algorithms"],
        "tutorial": "tutorial_8",
        "difficulty": "intermediate"
    },
    {
        "id": "q5",
        "question": "What is memoization?",
        "expected_topics": ["Dynamic Programming", "Memoization"],
        "tutorial": "tutorial_3",
        "difficulty": "basic"
    },
    {
        "id": "q6",
        "question": "Explain greedy algorithms and when they work",
        "expected_topics": ["Greedy Algorithms", "Greedy choice property"],
        "tutorial": "tutorial_2",
        "difficulty": "intermediate"
    },
    {
        "id": "q7",
        "question": "What is the master theorem?",
        "expected_topics": ["Divide-and-Conquer", "Master Theorem"],
        "tutorial": "tutorial_2",
        "difficulty": "advanced"
    },
    {
        "id": "q8",
        "question": "How do you analyze recursive algorithms?",
        "expected_topics": ["Recursion", "Recurrence relations"],
        "tutorial": "tutorial_1",
        "difficulty": "intermediate"
    },
    {
        "id": "q9",
        "question": "What is a minimum spanning tree and how do you find one?",
        "expected_topics": ["Graph algorithms", "MST algorithms"],
        "tutorial": "tutorial_4",
        "difficulty": "intermediate"
    },
    {
        "id": "q10",
        "question": "Explain the difference between BFS and DFS",
        "expected_topics": ["Graph traversal", "Search algorithms"],
        "tutorial": "tutorial_4",
        "difficulty": "basic"
    },
    {
        "id": "q11",
        "question": "What is NP-completeness?",
        "expected_topics": ["NP-completeness", "Computational complexity"],
        "tutorial": "tutorial_5",
        "difficulty": "advanced"
    },
    {
        "id": "q12",
        "question": "How does quicksort work and what's its time complexity?",
        "expected_topics": ["Sorting algorithms", "Divide-and-Conquer"],
        "tutorial": "tutorial_2",
        "difficulty": "intermediate"
    },
    {
        "id": "q13",
        "question": "What is maximum flow and how does it relate to minimum cut?",
        "expected_topics": ["Flow networks", "Max flow"],
        "tutorial": "tutorial_5",
        "difficulty": "advanced"
    },
    {
        "id": "q14",
        "question": "Explain polynomial time reduction",
        "expected_topics": ["Computational complexity", "NP-completeness"],
        "tutorial": "tutorial_5",
        "difficulty": "advanced"
    },
    {
        "id": "q15",
        "question": "What is backtracking and where is it used?",
        "expected_topics": ["Backtracking", "Search algorithms"],
        "tutorial": "tutorial_3",
        "difficulty": "intermediate"
    },
]


class MetadataSearcher:
    """Search using metadata.json (baseline/simple method)"""
    
    def __init__(self, metadata_path: str):
        self.metadata = json.loads(Path(metadata_path).read_text(encoding='utf-8'))
        self.name = "Metadata Search"
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Simple search: Find topics matching keywords in query
        """
        start_time = time.time()
        
        keywords = set(query.lower().split())
        matched_topics = []
        relevant_tutorials = set()
        
        # Search through all tutorials for keyword matches
        for tutorial_id, tutorial_data in self.metadata.items():
            topics = tutorial_data.get("topics", [])
            for topic in topics:
                if any(kw in topic.lower() for kw in keywords):
                    matched_topics.append(topic)
                    relevant_tutorials.add(tutorial_id)
        
        elapsed = time.time() - start_time
        
        return {
            "matched_topics": list(set(matched_topics)),  # Dedupe
            "relevant_tutorials": list(relevant_tutorials),
            "latency_ms": elapsed * 1000,
            "method": "metadata_search"
        }


class VectorDBSearcher:
    """Search using vector embeddings (RAG method) - placeholder for future"""
    
    def __init__(self, metadata_path: str, chroma_dir: str = "db"):
        self.metadata = json.loads(Path(metadata_path).read_text(encoding='utf-8'))
        self.chroma_dir = Path(chroma_dir)
        self.name = "Vector DB (RAG)"
        # TODO: Initialize Chroma/vector DB client here
        self.available = False
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Vector DB search: Convert query to embedding, find similar content
        """
        if not self.available:
            return {
                "error": "Vector DB not initialized yet",
                "matched_topics": [],
                "relevant_tutorials": [],
                "latency_ms": None,
                "method": "vector_db_search"
            }
        
        # TODO: Implement actual vector search
        start_time = time.time()
        elapsed = time.time() - start_time
        
        return {
            "matched_topics": [],
            "relevant_tutorials": [],
            "latency_ms": elapsed * 1000,
            "method": "vector_db_search"
        }


def evaluate_search(searcher: Any, question: str, expected_topics: List[str]) -> Dict[str, float]:
    """
    Evaluate search results against expected answer
    
    Metrics:
    - Precision: Of found topics, how many were expected? 
    - Recall: Of expected topics, how many were found?
    - F1: Harmonic mean of precision and recall
    """
    result = searcher.search(question)
    found = set(t.lower() for t in result.get("matched_topics", []))
    expected = set(t.lower() for t in expected_topics)
    
    if not expected:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "latency_ms": result.get("latency_ms", 0)}
    
    if not found:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "latency_ms": result.get("latency_ms", 0)}
    
    # Calculate metrics
    tp = len(found & expected)
    fp = len(found - expected)
    fn = len(expected - found)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "latency_ms": result.get("latency_ms", 0),
        "found_topics": list(found),
        "expected_topics": list(expected),
        "matched_count": tp
    }


def run_comparison():
    """Run comparison between both search methods"""
    
    metadata_path = Path(__file__).parent / "db" / "metadata.json"
    
    if not metadata_path.exists():
        print(f"ERROR: metadata.json not found at {metadata_path}")
        print("Run the pipeline first: python process_with_llm.py && python transform_to_metadata.py")
        return
    
    print("=" * 80)
    print("🧪 SEARCH METHOD COMPARISON")
    print("=" * 80)
    print(f"\nTest set size: {len(TEST_QUESTIONS)} questions")
    print(f"Metadata file: {metadata_path}")
    
    # Initialize searchers
    metadata_searcher = MetadataSearcher(str(metadata_path))
    vector_searcher = VectorDBSearcher(str(metadata_path))
    
    searchers = [metadata_searcher, vector_searcher if vector_searcher.available else None]
    searchers = [s for s in searchers if s]  # Filter out None
    
    results = {s.name: [] for s in searchers}
    
    # Run tests
    print("\n" + "-" * 80)
    print("Running tests...")
    print("-" * 80)
    
    for test in TEST_QUESTIONS:
        q_id = test["id"]
        question = test["question"]
        expected_topics = test["expected_topics"]
        
        for searcher in searchers:
            eval_result = evaluate_search(searcher, question, expected_topics)
            results[searcher.name].append({
                "question_id": q_id,
                "question": question,
                "difficulty": test["difficulty"],
                **eval_result
            })
            
            print(f"\n{q_id}: {question[:50]}...")
            print(f"  {searcher.name}:")
            print(f"    F1: {eval_result['f1']:.3f} | Precision: {eval_result['precision']:.3f} | Recall: {eval_result['recall']:.3f}")
            if eval_result.get('latency_ms'):
                print(f"    Latency: {eval_result['latency_ms']:.2f}ms")
    
    # Compute aggregate metrics
    print("\n" + "=" * 80)
    print("📊 AGGREGATE RESULTS")
    print("=" * 80)
    
    for searcher_name, test_results in results.items():
        if not test_results:
            print(f"\n{searcher_name}: NOT AVAILABLE")
            continue
        
        avg_f1 = sum(r["f1"] for r in test_results) / len(test_results)
        avg_precision = sum(r["precision"] for r in test_results) / len(test_results)
        avg_recall = sum(r["recall"] for r in test_results) / len(test_results)
        avg_latency = sum(r.get("latency_ms", 0) for r in test_results) / len(test_results)
        
        print(f"\n{searcher_name}:")
        print(f"  Average F1: {avg_f1:.3f}")
        print(f"  Average Precision: {avg_precision:.3f}")
        print(f"  Average Recall: {avg_recall:.3f}")
        print(f"  Average Latency: {avg_latency:.2f}ms")
        
        # Breakdown by difficulty
        by_difficulty = {}
        for result in test_results:
            diff = result["difficulty"]
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append(result["f1"])
        
        print(f"\n  By Difficulty:")
        for diff in ["basic", "intermediate", "advanced"]:
            if diff in by_difficulty:
                f1_scores = by_difficulty[diff]
                avg = sum(f1_scores) / len(f1_scores)
                print(f"    {diff}: {avg:.3f} ({len(f1_scores)} questions)")
    
    # Recommendation
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATION")
    print("=" * 80)
    
    if len(results) >= 2:
        # Compare F1 scores
        searcher_names = list(results.keys())
        f1_scores = {
            name: sum(r["f1"] for r in results[name]) / len(results[name])
            for name in searcher_names
        }
        
        best = max(f1_scores, key=f1_scores.get)
        print(f"\nBetter method: {best} (F1: {f1_scores[best]:.3f})")
        
        for name, score in f1_scores.items():
            if name != best:
                improvement = ((f1_scores[best] - score) / score * 100) if score > 0 else 0
                print(f"  {best} is {improvement:.1f}% better than {name}")
    else:
        print("\nOnly metadata search is available. Vector DB not initialized.")
        print("To enable RAG evaluation, set up Chroma and uncomment in VectorDBSearcher.__init__")
    
    # Save results
    output_file = Path(__file__).parent / "test_results.json"
    output_file.write_text(
        json.dumps(
            {
                "test_set_size": len(TEST_QUESTIONS),
                "test_questions": TEST_QUESTIONS,
                "results": results,
                "timestamp": time.time(),
            },
            indent=2
        )
    )
    print(f"\n✅ Results saved to {output_file}")


if __name__ == "__main__":
    run_comparison()
