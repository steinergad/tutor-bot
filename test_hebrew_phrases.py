#!/usr/bin/env python3
"""Test Hebrew homework phrase detection"""

from homework_validation import is_in_scope, extract_keywords

print("═" * 70)
print("TESTING HEBREW HOMEWORK PHRASE DETECTION")
print("═" * 70)

# Test the exact Hebrew question from the screenshot
hebrew_question = "איך אני פותר בעיות דינמיות בפיבונאצ'י"

print(f"\n📝 Hebrew Question: {hebrew_question}")
print(f"   Translation: 'How do I solve dynamic fibonacci problems?'")

# Test if it's in scope for hw_3
is_valid, reason = is_in_scope(hebrew_question, "hw_3")

print(f"\n🔍 Validation Result:")
print(f"   Valid: {is_valid}")
if reason:
    print(f"   Reason: {reason}")

# Also extract keywords to see what's found
keywords = extract_keywords(hebrew_question)
print(f"\n🔑 Keywords extracted: {keywords}")

# Test other Hebrew questions
test_questions = [
    ("איך אני פותר בעיות דינמיות בפיבונאצ'י", "How do I solve dynamic fibonacci problems?"),
    ("אני צריך עזור עם בעיות", "I need help with problems"),
    ("איך לפתור את התרגיל", "How to solve the exercise"),
    ("מה זה dynamic programming", "What is dynamic programming"),
]

print("\n" + "═" * 70)
print("TESTING MULTIPLE HEBREW QUESTIONS")
print("═" * 70)

for he_q, en_translation in test_questions:
    is_valid, reason = is_in_scope(he_q, "hw_3")
    status = "✅ PASS" if is_valid else "❌ FAIL"
    print(f"\n{status}")
    print(f"  Hebrew: {he_q}")
    print(f"  English: {en_translation}")
    if reason:
        print(f"  Reason: {reason}")

print("\n" + "═" * 70)
