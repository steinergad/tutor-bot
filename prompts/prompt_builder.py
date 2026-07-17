"""
prompt_builder.py — Load and construct system prompts from structured files

This module loads prompt templates from the `prompts/` folder and builds
complete system messages with proper formatting and variable substitution.

Usage:
  from prompts.prompt_builder import build_tutorial_prompt, build_homework_prompt
  
  sys_msg = build_tutorial_prompt(
    topics_list="Topic 1\\nTopic 2",
    tutorial_label="Tutorial 1",
    topic_context="..."
  )
"""

import json
from pathlib import Path
from typing import Dict, Any, List

PROMPTS_DIR = Path(__file__).parent


def load_prompt_template(template_name: str) -> Dict[str, Any]:
    """Load a prompt template from JSON file."""
    path = PROMPTS_DIR / f"{template_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_tutorial_prompt(
    topics_list: str,
    tutorial_label: str,
    topic_context: str = ""
) -> str:
    """
    Build complete system prompt for tutorial mode.
    
    Args:
        topics_list: Formatted list of allowed topics (newline-separated)
        tutorial_label: Display name for current tutorial
        topic_context: Optional course material reference
    
    Returns:
        Complete system message as string
    """
    template = load_prompt_template("tutorial_prompt")
    msg = template["system_message_template"]
    
    # Build the system message
    sys_msg = (
        f"{msg['role']}\n\n"
        f"The student has learned the following topics so far:\n\n"
        f"{topics_list}\n\n"
        f"Current topic: {tutorial_label}\n\n"
        f"Guidelines:\n"
    )
    
    # Add curriculum boundary rules
    sys_msg += f"- {msg['curriculum_boundary']['allowed']}\n"
    sys_msg += f"- {msg['curriculum_boundary']['out_of_scope']}\n"
    
    # Add teaching guidelines
    for guideline in msg['teaching_guidelines']:
        sys_msg += f"- {guideline}\n"
    
    # Add course material if provided
    if topic_context.strip():
        # Escape {{ }} so LangChain doesn't treat math notation like {1..k} as template vars
        safe_context = topic_context.replace("{", "{{").replace("}", "}}")
        sys_msg += f"\nCourse material reference:\n{safe_context}\n"
    
    # Add math formatting instructions
    sys_msg += (
        f"\nFormat all math using Markdown/KaTeX:\n"
        f"- Inline math: {msg['math_formatting']['inline']}\n"
        f"- Block math: {msg['math_formatting']['block']}\n"
        f"Use only $...$ and $$...$$ delimiters.\n"
    )
    
    return sys_msg


def build_homework_prompt(
    concepts_list: str,
    hw_title: str,
    hw_description: str = "",
    key_concepts: str = ""
) -> str:
    """
    Build complete system prompt for homework/Socratic mode.
    
    IMPORTANT: This prompt enforces curriculum-grounding and strict Socratic method.
    The tutor MUST reference specific tutorials/lectures, not give generic hints.
    
    Args:
        concepts_list: Formatted list of learned concepts (newline-separated)
        hw_title: Title of homework assignment
        hw_description: Optional description of the problem
        key_concepts: Optional list of key concepts to focus on
    
    Returns:
        Complete system message as string
    """
    template = load_prompt_template("homework_prompt")
    msg = template["system_message_template"]
    
    # Build the system message
    sys_msg = (
        f"{msg['role']}\n\n"
        f"**CURRICULUM GROUNDING**: {msg['core_principle']}\n\n"
        f"The student has learned these concepts:\n{concepts_list}\n\n"
    )
    
    if hw_description:
        sys_msg += f"**Problem Context**: {hw_description}\n\n"
    
    if key_concepts:
        sys_msg += f"**Key Concepts for This Assignment**:\n{key_concepts}\n\n"
    
    # Add Socratic method philosophy
    sys_msg += f"**PHILOSOPHY**: {msg['socratic_method']['philosophy']}\n\n"
    
    sys_msg += "**What You MUST Do**:\n"
    for do in msg['socratic_method']['dos']:
        sys_msg += f"- {do}\n"
    
    sys_msg += "\n**What You MUST NOT Do**:\n"
    for dont in msg['socratic_method']['donts']:
        sys_msg += f"- {dont}\n"
    
    sys_msg += f"\n**Curriculum Grounding Rules**:\n"
    sys_msg += f"- Every question should reference a specific tutorial, week, or concept from the curriculum\n"
    sys_msg += f"- Generic advice is BANNED (no 'consider the loops', 'think step by step', etc.)\n"
    sys_msg += f"- Examples of GOOD guidance: 'In Tutorial 2, we analyzed merge sort...', 'Week 1 homework had a similar pattern...'\n"
    sys_msg += f"- Examples of BAD guidance: 'Think about complexity', 'Consider the nested loops', 'Let's analyze this step by step'\n"
    
    # Add anti-generic response section
    anti_generic = msg.get('anti_generic_responses', {})
    if anti_generic:
        sys_msg += f"\n**CRITICAL: DO NOT RESPOND LIKE ChatGPT**:\n"
        sys_msg += f"BAD example (NEVER do this):\n"
        sys_msg += f"  '{anti_generic.get('when_student_asks_for_help', {}).get('bad_response', '')}'\n"
        sys_msg += f"GOOD example (do this instead):\n"
        sys_msg += f"  '{anti_generic.get('when_student_asks_for_help', {}).get('good_response', '')}'\n"
        sys_msg += f"\nBanned phrases (never use these):\n"
        for phrase in anti_generic.get('examples_of_banned_phrases', []):
            sys_msg += f"  • '{phrase}'\n"
    
    sys_msg += f"\n**Scope Rule**: Stay focused on {hw_title}. Redirect off-topic questions.\n"
    
    # Add explicit anti-ChatGPT enforcement
    sys_msg += (
        f"\n**⚠️ CRITICAL - ANTI-CHATGPT PROTOCOL ⚠️**:\n"
        f"RULE: When student says 'Help' or 'Help me' WITHOUT a specific question:\n"
        f"1. ASK: 'What specific problem or question are you working on?'\n"
        f"2. DO NOT end with 'Is there something related to...' or 'Are you working on...'\n"
        f"3. DO NOT suggest any concepts, topics, or ideas\n"
        f"4. DO NOT add follow-up questions about what they might want to discuss\n"
        f"5. WAIT - just ask for the specific question/problem, nothing else\n"
        f"\n"
        f"ZERO TOLERANCE:\n"
        f"- NO phrases like: 'we can discuss', 'we can explore', 'something related to', 'perhaps', 'maybe'\n"
        f"- NO concept suggestions: 'asymptotic', 'Big O', 'complexity', 'algorithm', 'analysis'\n"
        f"- NO topic hints or ideas - just ask for their specific question\n"
        f"\n"
        f"This is NOT ChatGPT. This is STRICT Socratic tutoring:\n"
        f"- Student states specific question FIRST\n"
        f"- ONLY THEN you reference tutorials and ask Socratic questions\n"
        f"- No suggestions. No hints. Just guidance toward their answer.\n"
    )
    
    # Add math formatting instructions
    sys_msg += (
        f"\nFormat all math using Markdown/KaTeX:\n"
        f"- Inline math: {msg['math_formatting']['inline']}\n"
        f"- Block math: {msg['math_formatting']['block']}\n"
        f"Use only $...$ and $$...$$ delimiters.\n"
    )
    
    return sys_msg


def get_prompt_metadata(template_name: str) -> Dict[str, Any]:
    """Get metadata about a prompt template."""
    return load_prompt_template(template_name)
