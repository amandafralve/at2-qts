from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PorteCachorro(str, Enum):
    PEQUENO = "Pequeno"
    MEDIO = "Médio"
    GRANDE = "Grande"


class RacaCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    porte: PorteCachorro
    expectativa_vida_anos: int = Field(ge=1, le=25)
    temperamento: str = Field(min_length=3, max_length=200)
    origem: str | None = Field(default=None, max_length=100)

    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("O nome não pode conter apenas espaços.")
        return normalized

    @field_validator("origem")
    @classmethod
    def normalizar_origem(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("temperamento")
    @classmethod
    def normalizar_temperamento(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("O temperamento não pode conter apenas espaços.")
        return normalized


class RacaResponse(RacaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
