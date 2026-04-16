from __future__ import annotations

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class Dificuldade(str, Enum):
    FACIL = "Facil"
    MEDIO = "Medio"
    DIFICIL = "Dificil"

    @classmethod
    def _missing_(cls, value: str):
        lookup = {
            "fácil": cls.FACIL, "facil": cls.FACIL,
            "médio": cls.MEDIO, "medio": cls.MEDIO,
            "difícil": cls.DIFICIL, "dificil": cls.DIFICIL,
        }
        return lookup.get(value.lower() if isinstance(value, str) else value)


class Macros(BaseModel):
    calorias: float
    proteinas: float
    carbo: float
    gorduras: float


class Receita(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    nome_receita: str
    dificuldade: Dificuldade
    macros: Macros
    passos: list[str]
    ingredientes_usados: list[str] = []
    tempo_preparo: int | None = None
    porcoes: int | None = None
    fonte: str = "demo"
    ingredientes_detectados: str | None = None


class CardapioResponse(BaseModel):
    receitas: list[Receita]
    ingredientes_informados: str


class ReceitaRequest(BaseModel):
    ingredientes: str | None = None
    tempo_minutos: int = 30
