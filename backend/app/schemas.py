from typing import Literal

from pydantic import BaseModel, Field

Species = Literal["perro", "gato", "otro"]
Sex = Literal["macho", "hembra"]
AgeStage = Literal["cachorro", "adulto", "senior"]
Presence = Literal["siempre", "a_veces", "independiente"]
HungerBehavior = Literal["ladra_pide", "espera_paciente", "sigue_por_todos_lados"]
Contribution = Literal["paz", "alegria", "consuelo", "compania"]


class PetMetadata(BaseModel):
    pet_name: str = ""
    owner_name: str = ""
    species: Species
    sexo: Sex
    age_stage: AgeStage
    traits: list[str] = Field(default_factory=list)
    presence: Presence
    hunger_behavior: HungerBehavior
    contribution: Contribution
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
