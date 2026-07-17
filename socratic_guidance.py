"""
socratic_guidance.py — Generate curriculum-aware Socratic guidance

Replaces generic "think step by step" with references to:
- Specific tutorial examples
- Lecture content
- Recitation problems
- Proven teaching patterns from course materials

This is the key differentiator from generic ChatGPT.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from search_integration import find_relevant_topics

DB_DIR = Path("db")
META_FILE = DB_DIR / "metadata.json"


def load_curriculum() -> Dict:
    """Load tutorial metadata and homework data"""
    if not META_FILE.exists():
        return {}
    return json.loads(META_FILE.read_text(encoding="utf-8"))


def find_related_tutorials(problem_topic: str, num_references: int = 2) -> List[Tuple[str, str, str]]:
    """
    Find related tutorials that cover similar concepts.
    
    Returns:
        List of (tutorial_id, tutorial_name, related_concept) tuples
    """
    curriculum = load_curriculum()
    
    try:
        # Use vector search to find related topics
        related = find_relevant_topics(problem_topic, top_k=5)
        
        results = []
        seen_tutorials = set()
        
        for topic, score, tutorial_id in related:
            if tutorial_id not in seen_tutorials and len(results) < num_references:
                tutorial_name = curriculum.get(tutorial_id, {}).get("display_name", tutorial_id)
                results.append((tutorial_id, tutorial_name, topic))
                seen_tutorials.add(tutorial_id)
        
        return results
    except:
        # Fallback: return empty if vector DB unavailable
        return []


def extract_concepts_from_problem(problem_text: str) -> List[str]:
    """
    Extract key concepts from a homework problem.
    
    Example:
        "Analyze time complexity of nested loops" 
        → ["time complexity", "nested loops", "Big O"]
    """
    # Simple keyword extraction (could be enhanced with NLP)
    keywords = {
        "complexity": ["complexity", "time", "space", "O(", "analyze"],
        "recursion": ["recursion", "recurrence", "recursive", "base case"],
        "sorting": ["sort", "merge", "quick", "heap"],
        "graph": ["graph", "node", "edge", "traverse", "BFS", "DFS"],
        "dynamic": ["dynamic", "DP", "memoization", "optimal"],
        "greedy": ["greedy", "choice", "optimal", "property"],
    }
    
    problem_lower = problem_text.lower()
    extracted = []
    
    for concept, terms in keywords.items():
        if any(term in problem_lower for term in terms):
            extracted.append(concept)
    
    return extracted


def generate_curriculum_reference(hw_problem: str, hw_week: int) -> str:
    """
    Generate a Socratic response that references curriculum.
    
    Instead of:
        "Let's think step by step. Analyze the loops. Consider complexity."
    
    Returns:
        "This involves time complexity analysis—similar to what we covered 
         in Tutorial 1 with the merge-sort example. Let me ask: what do you 
         notice about the nested loop structure?"
    """
    concepts = extract_concepts_from_problem(hw_problem)
    related_tutorials = find_related_tutorials(hw_problem)
    
    # Build response
    response_parts = []
    
    # Part 1: Identify the concept
    if concepts:
        primary_concept = concepts[0].capitalize()
        response_parts.append(
            f"This problem involves **{primary_concept}**—a key concept we've studied."
        )
    
    # Part 2: Reference tutorials
    if related_tutorials:
        response_parts.append("\n**From our course materials:**")
        for tutorial_id, tutorial_name, related_concept in related_tutorials:
            response_parts.append(
                f"- **{tutorial_name}** covered this with the {related_concept.lower()} example"
            )
    
    # Part 3: Socratic question (not hints)
    if concepts:
        concept = concepts[0]
        socratic_questions = {
            "complexity": "What patterns do you notice in how many times the loops execute?",
            "recursion": "How would you express the relationship between successive calls?",
            "sorting": "How does this compare to the merge or quicksort approach we studied?",
            "graph": "What's the order in which you'd visit the nodes?",
            "dynamic": "What overlapping subproblems do you see?",
            "greedy": "Why would choosing this option now lead to the best overall result?",
        }
        
        question = socratic_questions.get(concept, "What patterns or structures do you notice?")
        response_parts.append(f"\n**My question for you**: {question}")
    
    return "\n".join(response_parts)


def validate_homework_query(user_query: str, hw_key: str, all_homework: Dict) -> Tuple[bool, Optional[str]]:
    """
    Check if user's question stays within current homework scope.
    
    Returns:
        (is_valid, error_message)
    """
    hw_data = all_homework.get(hw_key, {})
    current_topics = set(hw_data.get("topics", []))
    current_concepts = set(hw_data.get("key_concepts", []))
    current_week = hw_data.get("week", 1)
    
    # Load allowed concepts from all homework up to current week
    allowed_concepts = set()
    for k, v in all_homework.items():
        if v.get("week", 0) <= current_week:
            allowed_concepts.update(v.get("topics", []))
            allowed_concepts.update(v.get("key_concepts", []))
    
    # Extract user's query topics
    user_topics = extract_concepts_from_problem(user_query)
    user_lower = user_query.lower()
    
    # Check for out-of-scope topics
    future_topics = set()
    for k, v in all_homework.items():
        if v.get("week", 0) > current_week:
            future_topics.update(v.get("topics", []))
            future_topics.update(v.get("key_concepts", []))
    
    # If they mention future topics
    for topic in future_topics:
        if topic.lower() in user_lower:
            return (False, 
                f"That concept (**{topic}**) comes later in the course. "
                f"Let's focus on **{hw_data.get('title', 'this homework')}** for now.")
    
    # If they ask about completely different domains
    if any(word in user_lower for word in ["machine learning", "neural", "AI", "deep learning"]):
        return (False, 
            f"That's outside our current curriculum. "
            f"Let's stay focused on **{hw_data.get('title', 'this assignment')}**.")
    
    return (True, None)


def format_current_problem(problem_text: str, problem_num: int = 1) -> str:
    """Format problem for persistent display in sidebar"""
    # Truncate if too long
    if len(problem_text) > 300:
        problem_text = problem_text[:300] + "…"
    
    return f"""
### 📝 Problem {problem_num}

{problem_text}

---
**Focus on this problem. Use the chat to ask for guidance.**
"""


# Language support
LANGUAGES = {
    "en": {
        "mode_tutorial": "📖 Learn Material",
        "mode_homework": "💪 Solve Homework",
        "select_hw": "Select homework",
        "clear": "🗑 Clear",
        "current_problem": "📝 Current Problem",
        "ask_question": "Ask about this problem…",
        "welcome_tutor": "I'm your Socratic tutor. I'll guide you toward the answer with questions and hints—not give it to you directly.",
        "welcome_hw": "Focus on this problem. Ask questions and I'll guide you through the material.",
        "out_of_scope": "That's outside the current homework scope. Let's focus on this assignment.",
        "future_concept": "That concept comes later. Let's stick with this week's material.",
        "api_key_needed": "Open the sidebar to add your API key…",
        "api_key_info": "👈 Open the sidebar (top-left ▸) and add your OpenAI API key to start chatting.",
    },
    "he": {
        "mode_tutorial": "📖 חומר לימוד",
        "mode_homework": "💪 פתרון שיעורי בית",
        "select_hw": "בחר שיעורי בית",
        "clear": "🗑 נקה",
        "current_problem": "📝 הבעיה הנוכחית",
        "ask_question": "שאל על בעיה זו…",
        "welcome_tutor": "אני המורה שלך בשיטה סוקרטית. אנחיה אתך לכיוון התשובה בשאלות וטיפים—לא אתן לך אותה ישירות.",
        "welcome_hw": "התמקד בבעיה זו. שאל שאלות ואנחיה אותך דרך החומר.",
        "out_of_scope": "זה מחוץ לתחום שיעורי הבית הנוכחיים. בואו נתמקדו בשיעורים אלה.",
        "future_concept": "הקונספט הזה יבוא מאוחר יותר. בואו נדבקים לחומר השבוע.",
        "api_key_needed": "פתח את הסרגל הצידי כדי להוסיף את מפתח ה-API שלך…",
        "api_key_info": "👈 פתח את הסרגל הצידי (למעלה משמאל ▸) והוסף את מפתח OpenAI API שלך כדי להתחיל לשוחח.",
    }
}


def get_text(key: str, language: str = "en") -> str:
    """Get translated text"""
    return LANGUAGES.get(language, LANGUAGES["en"]).get(key, key)
