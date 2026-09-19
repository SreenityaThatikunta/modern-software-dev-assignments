from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemDoneRequest,
    ActionItemDoneResponse,
    ActionItemExtractRequest,
    ActionItemResponse,
    ExtractionResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])
logger = logging.getLogger(__name__)


def _persist_extraction(
    payload: ActionItemExtractRequest, items: list[str]
) -> ExtractionResponse:
    """Save an extraction result and optionally associate it with its source note."""
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractionResponse(
        note_id=note_id,
        items=[
            ActionItemResponse(id=item_id, note_id=note_id, text=text)
            for item_id, text in zip(ids, items)
        ],
    )


@router.post("/extract", response_model=ExtractionResponse)
def extract(payload: ActionItemExtractRequest) -> ExtractionResponse:
    items = extract_action_items(payload.text)
    return _persist_extraction(payload, items)


@router.post("/extract/llm", response_model=ExtractionResponse)
def extract_with_llm(payload: ActionItemExtractRequest) -> ExtractionResponse:
    """Extract action items with the configured local Ollama model."""
    try:
        items = extract_action_items_llm(payload.text)
    except Exception as error:
        logger.exception("LLM action item extraction failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "LLM extraction is unavailable. Start Ollama and verify OLLAMA_MODEL is installed."
            ),
        ) from error
    return _persist_extraction(payload, items)


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: Optional[int] = None) -> list[ActionItemResponse]:
    rows = db.list_action_items(note_id=note_id)
    return [ActionItemResponse(**row.__dict__) for row in rows]


@router.post("/{action_item_id}/done", response_model=ActionItemDoneResponse)
def mark_done(action_item_id: int, payload: ActionItemDoneRequest) -> ActionItemDoneResponse:
    if not db.mark_action_item_done(action_item_id, payload.done):
        raise HTTPException(status_code=404, detail="action item not found")
    return ActionItemDoneResponse(id=action_item_id, done=payload.done)
