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
    
    # Build the system message with STRICT scope restrictions
    sys_msg = f"{msg['role']}\n\n"
    
    # Add CRITICAL scope enforcement first
    sys_msg += f"⚠️ CRITICAL SCOPE RESTRICTION:\n"
    if msg.get('scope_restrictions'):
        sys_msg += f"- {msg['scope_restrictions']['critical']}\n"
        sys_msg += f"- ONLY answer questions about: **{hw_title}**\n"
        sys_msg += f"- If question is out of scope, redirect with: 'That's not part of this assignment. Let's focus on {hw_title}.'\n\n"
    
    # Add concepts learned so far
    sys_msg += f"The student has learned these concepts:\n{concepts_list}\n\n"
    
    if hw_description:
        sys_msg += f"**Problem Context**: {hw_description}\n\n"
    
    if key_concepts:
        sys_msg += f"**Key Concepts for This Assignment**:\n{key_concepts}\n\n"
    
    # Add Socratic method with strict enforcement
    sys_msg += f"**Your Teaching Role**: {msg['socratic_method']['core_principle']}\n\n"
    
    sys_msg += "**MUST DOs (Reference Curriculum):**\n"
    for do in msg['socratic_method']['dos']:
        sys_msg += f"- {do}\n"
    
    sys_msg += "\n**MUST NOT DOs (Never Do These):**\n"
    for dont in msg['socratic_method']['donts']:
        sys_msg += f"- {dont}\n"
    
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
