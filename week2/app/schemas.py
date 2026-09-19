from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class NoteCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("content must not be blank")
        return content


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemExtractRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)
    save_note: bool = False

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("text must not be blank")
        return text


class ActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool = False
    created_at: Optional[str] = None


class ExtractionResponse(BaseModel):
    note_id: Optional[int]
    items: list[ActionItemResponse]


class ActionItemDoneRequest(BaseModel):
    done: bool = True


class ActionItemDoneResponse(BaseModel):
    id: int
    done: bool
