from __future__ import annotations

import httpx

from .config import settings
from .models import Dificuldade, Macros, Receita

BASE_URL = "https://api.spoonacular.com"


class SpoonacularClient:
    """Busca receitas reais na Spoonacular."""

    def __init__(self) -> None:
        self._key = settings.spoonacular_api_key

    async def buscar_receita(self, ingredientes: str, tempo_max: int = 30) -> Receita | None:
        params = {
            "apiKey": self._key,
            "ingredients": ingredientes,
            "number": 5,
            "ranking": 1,
            "ignorePantry": True,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{BASE_URL}/recipes/findByIngredients", params=params)
            if resp.status_code != 200 or not resp.json():
                return None

            # Filtrar: pegar a receita com menos ingredientes faltantes
            resultados = resp.json()
            resultados.sort(key=lambda r: r.get("missedIngredientCount", 99))

            for resultado in resultados:
                if resultado.get("missedIngredientCount", 99) > 2:
                    continue

                recipe_id = resultado["id"]
                receita = await self._detalhar_receita(client, recipe_id, tempo_max)
                if receita:
                    receita.ingredientes_faltantes = [
                        ing["name"] for ing in resultado.get("missedIngredients", [])
                    ]
                    return receita

            return None

    async def _detalhar_receita(self, client: httpx.AsyncClient, recipe_id: int, tempo_max: int) -> Receita | None:
        resp = await client.get(
            f"{BASE_URL}/recipes/{recipe_id}/information",
            params={"apiKey": self._key, "includeNutrition": True},
        )
        if resp.status_code != 200:
            return None

        data = resp.json()

        if data.get("readyInMinutes", 999) > tempo_max:
            return None

        macros = _extrair_macros(data.get("nutrition", {}))

        passos = []
        for section in data.get("analyzedInstructions", []):
            for step in section.get("steps", []):
                passos.append(step["step"])

        if not passos:
            return None

        tempo = data.get("readyInMinutes", 30)
        dificuldade = (
            Dificuldade.FACIL if tempo <= 15
            else Dificuldade.MEDIO if tempo <= 40
            else Dificuldade.DIFICIL
        )

        return Receita(
            nome_receita=data["title"],
            dificuldade=dificuldade,
            macros=macros,
            passos=passos,
            tempo_preparo=tempo,
            porcoes=data.get("servings", 1),
            fonte="spoonacular",
        )


def _extrair_macros(nutrition: dict) -> Macros:
    nutrients = {n["name"]: n["amount"] for n in nutrition.get("nutrients", [])}
    return Macros(
        calorias=nutrients.get("Calories", 0),
        proteinas=nutrients.get("Protein", 0),
        carbo=nutrients.get("Carbohydrates", 0),
        gorduras=nutrients.get("Fat", 0),
    )
