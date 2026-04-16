from __future__ import annotations

import base64
import json
import mimetypes
import re
import traceback
from pathlib import Path

from .config import settings
from .models import CardapioResponse, Receita

VISION_PROMPT = """\
Voce e um chef profissional brasileiro analisando uma foto de ingredientes.

## INSTRUCOES RIGOROSAS
1. Liste SOMENTE o que voce ve com CERTEZA ABSOLUTA na imagem.
2. NUNCA adivinhe. Se nao tem 100% de certeza, NAO inclua.
3. Seja ESPECIFICO:
   - Carne: identifique o tipo (bovina, frango, suina, peixe) pela cor e textura.
     Carne vermelha escura = bovina. Carne rosa clara = suina. Carne branca/amarelada = frango.
     Salmao = cor alaranjada/rosada caracteristica.
   - Ervas: alecrim (folhas finas como agulhas), salsinha (folhas largas planas),
     coentro (similar a salsinha mas com aroma), manjericao (folhas largas ovais).
   - Alho: bulbo branco com dentes, NAO confunda com cogumelos.
   - Cogumelos: chapeu arredondado com haste, muito maiores que dentes de alho.
   - Manteiga: bloco amarelo, geralmente em embalagem.
   - Pimentas: identifique o tipo se possivel (dedo-de-moca, pimenta-do-reino moida, etc.)

Responda APENAS com a lista separada por virgula em portugues. Nada mais.
"""

CARDAPIO_PROMPT = """\
Voce e o SmartChef, um chef profissional brasileiro com 20 anos de experiencia \
em restaurantes premiados. Voce ensina como se o aluno estivesse do seu lado na cozinha.

O usuario vai te dar uma lista de ingredientes. Crie um CARDAPIO COMPLETO \
que APROVEITE TODOS os ingredientes.

## REGRAS INVIOLAVEIS
1. TODOS os ingredientes devem ser usados em pelo menos uma receita.
2. Numero de receitas conforme variedade:
   - 1-3 ingredientes: 1 receita
   - 4-6 ingredientes: 1 a 2 receitas
   - 7+ ingredientes: 2 a 3 receitas
3. Combinacoes devem fazer sentido culinario.
4. Itens basicos permitidos: sal, agua, azeite, pimenta-do-reino.
5. NUNCA adicione ingredientes principais nao mencionados.

## DETALHAMENTO DOS PASSOS (CRITICO)
Cada receita deve ter no MINIMO 6 passos e no MAXIMO 12 passos.
Cada passo deve ser DETALHADO como um professor ensinando um iniciante:

- PREPARACAO: "Corte o salmao em cubos de 2cm, retire a pele e as espinhas. \
Seque bem com papel toalha — a umidade impede a selagem."
- TEMPO EXATO: "Refogue o alho picado fino por 1 minuto em fogo medio, \
mexendo sempre para nao queimar."
- TEMPERATURA: "Aqueca a frigideira antiaderente em fogo alto por 2 minutos \
antes de adicionar o azeite — a panela quente sela melhor."
- PONTO CERTO: "Cozinhe o arroz por 18 minutos em fogo baixo com tampa, \
ate a agua secar e aparecerem furinhos na superficie."
- TECNICA: "Adicione o creme de leite fora do fogo e mexa delicadamente — \
se ferver, o creme talha."
- FINALIZACAO: "Prove e ajuste o sal. Sirva imediatamente com o salmao \
por cima do arroz, finalizando com cebolinha picada."

NUNCA escreva passos genericos como "tempere a gosto" ou "cozinhe ate ficar pronto".
Sempre diga QUANTO tempo, QUAL fogo, QUAL ponto.

## MACROS
Estime de forma REALISTA para 1 porcao individual.

## FORMATO — JSON valido (sem markdown, sem ```):
{
  "receitas": [
    {
      "nome_receita": "string",
      "dificuldade": "Facil" | "Medio" | "Dificil",
      "tempo_preparo": number,
      "porcoes": number,
      "ingredientes_usados": ["ingrediente1", "ingrediente2"],
      "macros": {"calorias": number, "proteinas": number, "carbo": number, "gorduras": number},
      "passos": ["passo 1", "passo 2", "passo 3", "passo 4", "passo 5", "passo 6", ...]
    }
  ]
}
"""


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("A IA nao retornou um JSON valido.")
    return json.loads(match.group())


def _image_to_base64(path: str) -> tuple[str, str]:
    data = Path(path).read_bytes()
    media_type = mimetypes.guess_type(path)[0] or "image/jpeg"
    return base64.standard_b64encode(data).decode(), media_type


class ChefEngine:
    """Motor principal — Claude Sonnet como cerebro."""

    def __init__(self) -> None:
        self._claude = None
        if settings.has_anthropic:
            import anthropic
            self._claude = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def gerar_cardapio(
        self,
        ingredientes: str | None = None,
        imagem_path: str | None = None,
        tempo_minutos: int = 30,
    ) -> CardapioResponse:
        veio_da_imagem = False

        if imagem_path and self._claude:
            try:
                ingredientes = self._identificar_ingredientes(imagem_path)
                veio_da_imagem = True
            except Exception as e:
                print(f"[ERRO] Visao: {e}")
                traceback.print_exc()

        if not ingredientes:
            from .demo import receita_demo
            r = receita_demo(tempo_minutos)
            return CardapioResponse(receitas=[r], ingredientes_informados="")

        if self._claude:
            try:
                print(f"[INFO] Gerando cardapio para: {ingredientes}")
                receitas = self._gerar_cardapio_claude(ingredientes, tempo_minutos)
                for r in receitas:
                    r.fonte = "claude"
                    if veio_da_imagem:
                        r.ingredientes_detectados = ingredientes
                return CardapioResponse(
                    receitas=receitas,
                    ingredientes_informados=ingredientes,
                )
            except Exception as e:
                print(f"[ERRO] Claude: {e}")
                traceback.print_exc()

        from .demo import receita_demo
        r = receita_demo(tempo_minutos)
        return CardapioResponse(receitas=[r], ingredientes_informados=ingredientes or "")

    # Mantém compatibilidade com endpoint antigo
    async def gerar_receita(
        self,
        ingredientes: str | None = None,
        imagem_path: str | None = None,
        tempo_minutos: int = 30,
    ) -> Receita:
        cardapio = await self.gerar_cardapio(ingredientes, imagem_path, tempo_minutos)
        return cardapio.receitas[0]

    def _identificar_ingredientes(self, imagem_path: str) -> str:
        b64, media_type = _image_to_base64(imagem_path)

        response = self._claude.messages.create(
            model=settings.anthropic_model,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                    {"type": "text", "text": VISION_PROMPT},
                ],
            }],
        )
        resultado = response.content[0].text
        print(f"[VISAO] Ingredientes identificados: {resultado}")
        return resultado

    def _gerar_cardapio_claude(self, ingredientes: str, tempo_minutos: int) -> list[Receita]:
        user_msg = (
            f"Ingredientes disponiveis: {ingredientes}\n"
            f"Tempo maximo por receita: {tempo_minutos} minutos\n"
            f"Crie o melhor cardapio possivel aproveitando TODOS esses ingredientes."
        )

        response = self._claude.messages.create(
            model=settings.anthropic_model,
            max_tokens=4096,
            system=CARDAPIO_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )

        data = _extract_json(response.content[0].text)
        receitas = []
        for r in data["receitas"]:
            receitas.append(Receita.model_validate(r))

        print(f"[OK] {len(receitas)} receita(s) gerada(s)")
        return receitas
