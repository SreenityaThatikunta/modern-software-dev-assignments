from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_tags_deduplicates_and_normalizes_tags():
    tags = extract_tags("Plan #Release with #backend, then revisit #RELEASE and #not-a-tag.")
    assert tags == ["release", "backend", "not-a-tag"]
