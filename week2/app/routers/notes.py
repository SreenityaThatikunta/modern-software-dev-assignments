from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from .. import db
from ..schemas import NoteCreateRequest, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreateRequest) -> NoteResponse:
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=500, detail="created note could not be retrieved")
    return NoteResponse(**note.__dict__)


@router.get("", response_model=list[NoteResponse])
def list_notes() -> list[NoteResponse]:
    return [NoteResponse(**note.__dict__) for note in db.list_notes()]


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse(**note.__dict__)
