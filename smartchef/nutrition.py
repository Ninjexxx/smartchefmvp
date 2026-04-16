from __future__ import annotations

from .models import Macros


class NutritionConsultant:
    """Consultor nutricional que formata e apresenta os macros."""

    @staticmethod
    def resumo(macros: Macros) -> str:
        return (
            f"🔥 Calorias: {macros.calorias:.0f} kcal | "
            f"🥩 Proteínas: {macros.proteinas:.1f}g | "
            f"🍚 Carboidratos: {macros.carbo:.1f}g | "
            f"🧈 Gorduras: {macros.gorduras:.1f}g"
        )
