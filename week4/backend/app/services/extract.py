import re

TAG_PATTERN = re.compile(r"(?<!\w)#([a-zA-Z0-9][a-zA-Z0-9_-]*)")


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    """Return unique hash-tags in first-seen order, without the leading '#'."""
    return list(dict.fromkeys(match.group(1).lower() for match in TAG_PATTERN.finditer(text)))
