from __future__ import annotations

import os
import re
from typing import List

from dotenv import load_dotenv
from ollama import chat
from pydantic import BaseModel

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


class LLMActionItems(BaseModel):
    """The structured response requested from the Ollama model."""

    items: List[str]


# Keep this schema intentionally small: it is easier for compact local models
# such as llama3.2:3b to follow than a schema with generated metadata.
ACTION_ITEMS_SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {"type": "string"}}},
    "required": ["items"],
}


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> List[str]:
    """Extract action items from notes with a locally running Ollama model.

    Set ``OLLAMA_MODEL`` to the name of a model already pulled with Ollama. The
    default, ``llama3.2:3b``, is a small general-purpose model suitable for local use.
    """
    notes = text.strip()
    if not notes:
        return []

    response = chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract every action item as a short string. Return JSON only.\n"
                    f"{notes}"
                ),
            }
        ],
        format=ACTION_ITEMS_SCHEMA,
        options={"temperature": 0},
    )
    parsed = LLMActionItems.model_validate_json(response.message.content)

    # Keep the service contract consistent with the heuristic extractor.
    return _deduplicate_items(parsed.items)


def _deduplicate_items(items: List[str]) -> List[str]:
    """Drop blank and duplicate items while preserving the model's ordering."""
    seen: set[str] = set()
    unique: List[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned.lower() in seen:
            continue
        seen.add(cleaned.lower())
        unique.append(cleaned)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
