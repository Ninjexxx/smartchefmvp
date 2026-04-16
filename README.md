# SmartChef MVP

Assistente de culinária inteligente que gera receitas detalhadas a partir de ingredientes por texto ou foto.

## Como funciona

1. Você informa os ingredientes (digitando ou tirando foto)
2. **Claude Sonnet** identifica os ingredientes na foto e gera um cardápio completo
3. Cada receita vem com passos detalhados: tempos, temperaturas, técnicas e dicas de chef

## Stack

- **Backend**: Python + FastAPI
- **IA**: Claude Sonnet 4 (Anthropic) — visão + geração de receitas
- **Dados**: Spoonacular API (receitas reais como referência)
- **Frontend**: HTML/JS (PWA)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Preencha as API keys no .env
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

## API Keys necessárias

| Serviço | Onde obter | Obrigatório |
|---|---|---|
| Anthropic (Claude) | [console.anthropic.com](https://console.anthropic.com) | Sim |
| Spoonacular | [spoonacular.com/food-api](https://spoonacular.com/food-api) | Opcional |

## Endpoints

- `POST /api/cardapio` — gera cardápio completo (múltiplas receitas)
- `POST /api/receita` — gera uma receita
- `POST /api/cardapio/imagem` — gera cardápio a partir de foto
- `GET /api/status` — status das integrações
