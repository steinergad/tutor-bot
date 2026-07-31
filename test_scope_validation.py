#!/usr/bin/env python3
"""Test scope validation fixes"""

from homework_validation import is_in_scope, get_homework_scope, extract_keywords

print("═" * 70)
print("TESTING HOMEWORK SCOPE VALIDATION FIX")
print("═" * 70)

# Test Homework 3 scope
hw_key = "hw_3"
scope = get_homework_scope(hw_key)

print(f"\n📚 Homework: {scope['title']}")
print(f"   Topics: {', '.join(scope['topics'])}")
print(f"   Description: {scope['description'][:60]}...")
print(f"   Problem Preview: {scope['problem_preview'][:100]}...")

# Extract keywords from scope
scope_keywords = set()
for text in [scope['description'], scope['problem_preview']]:
    if text:
        scope_keywords.update(extract_keywords(text))

print(f"\n🔑 Scope keywords extracted: {sorted(scope_keywords)}")

# Test questions
test_questions = [
    "How do I solve Fibonacci?",
    "how to find fibonacci sequence in o(n)",
    "hello how to do merge sort",
    "what is dynamic programming?",
    "explain memoization",
    "I don't understand anything",  # Should be OK (help phrase)
    "Is this related to homework 4?",  # Should fail (graph algorithms, not DP)
]

print("\n" + "═" * 70)
print("TESTING QUESTIONS")
print("═" * 70)

for question in test_questions:
    is_valid, reason = is_in_scope(question, hw_key)
    q_keywords = extract_keywords(question)
    
    status = "✅ PASS" if is_valid else "❌ FAIL"
    print(f"\n{status}")
    print(f"  Question: {question}")
    print(f"  Keywords: {q_keywords}")
    if reason:
        print(f"  Reason: {reason}")

print("\n" + "═" * 70)
print("END OF TESTS")
print("═" * 70)
