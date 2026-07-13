"""
prompts package — System prompts and policies for the tutoring bot

Provides structured prompt templates and builders for both tutorial
and homework modes, ensuring consistent teaching approaches across
different LLM backends.
"""

from .prompt_builder import (
    build_tutorial_prompt,
    build_homework_prompt,
    load_prompt_template,
    get_prompt_metadata,
)

__all__ = [
    "build_tutorial_prompt",
    "build_homework_prompt", 
    "load_prompt_template",
    "get_prompt_metadata",
]
