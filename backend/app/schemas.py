from typing import Literal

from pydantic import BaseModel, Field

Species = Literal["perro", "gato", "otro"]
Sex = Literal["macho", "hembra"]


class PetMetadata(BaseModel):
    pet_name: str = ""
    species: Species
    sexo: Sex
    traits: list[str] = Field(default_factory=list)
    anecdote: str = ""


class MonologueResponse(BaseModel):
    titulo: str
    monologo: str


class GenerateResponse(BaseModel):
    id: str
    title: str
    monologue: str
    illustration_url: str
    card_url: str
    audio_url: str
    video_url: str


class ErrorResponse(BaseModel):
    detail: str
