from __future__ import annotations

from .models import Dificuldade, Macros, Receita

DEMO_RECIPES = {
    "rapida": Receita(
        nome_receita="Salada Mediterrânea Express",
        dificuldade=Dificuldade.FACIL,
        macros=Macros(calorias=320, proteinas=12.5, carbo=28.0, gorduras=18.3),
        passos=[
            "Lave e pique os tomates em cubos medios.",
            "Corte o pepino em rodelas finas.",
            "Misture tudo em uma tigela com azeite e sal.",
            "Adicione queijo feta esfarelado por cima.",
            "Finalize com oregano e sirva imediatamente.",
        ],
        fonte="demo",
    ),
    "media": Receita(
        nome_receita="Frango Grelhado com Legumes",
        dificuldade=Dificuldade.MEDIO,
        macros=Macros(calorias=480, proteinas=42.0, carbo=22.0, gorduras=24.5),
        passos=[
            "Tempere o frango com sal, pimenta e alho.",
            "Aqueça a frigideira em fogo alto com um fio de azeite.",
            "Grelhe o frango por 5 minutos de cada lado.",
            "Enquanto isso, corte os legumes em tiras.",
            "Refogue os legumes na mesma frigideira por 4 minutos.",
            "Monte o prato com o frango fatiado sobre os legumes.",
            "Finalize com um fio de azeite e ervas frescas.",
        ],
        fonte="demo",
    ),
    "longa": Receita(
        nome_receita="Risoto Cremoso de Cogumelos",
        dificuldade=Dificuldade.DIFICIL,
        macros=Macros(calorias=620, proteinas=18.0, carbo=72.0, gorduras=28.0),
        passos=[
            "Aqueça o caldo de legumes e mantenha em fogo baixo.",
            "Refogue a cebola picada em manteiga até dourar.",
            "Adicione o arroz arbóreo e mexa por 2 minutos.",
            "Acrescente uma concha de caldo e mexa até absorver.",
            "Repita o processo por 18 minutos, adicionando caldo aos poucos.",
            "Em outra panela, salteie os cogumelos com alho.",
            "Misture os cogumelos ao risoto.",
            "Finalize com parmesão ralado e manteiga gelada.",
            "Tampe e deixe descansar por 2 minutos antes de servir.",
        ],
        fonte="demo",
    ),
}


def receita_demo(tempo_minutos: int) -> Receita:
    if tempo_minutos < 15:
        return DEMO_RECIPES["rapida"].model_copy()
    if tempo_minutos <= 30:
        return DEMO_RECIPES["media"].model_copy()
    return DEMO_RECIPES["longa"].model_copy()
