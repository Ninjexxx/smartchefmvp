"""SmartChef MVP — API REST com FastAPI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from smartchef.config import settings
from smartchef.engine import ChefEngine
from smartchef.models import CardapioResponse, Receita, ReceitaRequest

app = FastAPI(title="SmartChef MVP", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_engine = ChefEngine()


@app.post("/api/cardapio", response_model=CardapioResponse)
async def gerar_cardapio(req: ReceitaRequest):
    """Gera cardapio completo (multiplas receitas) a partir de ingredientes."""
    try:
        return await _engine.gerar_cardapio(
            ingredientes=req.ingredientes,
            tempo_minutos=req.tempo_minutos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/receita", response_model=Receita)
async def gerar_receita(req: ReceitaRequest):
    """Gera uma receita (compatibilidade)."""
    try:
        return await _engine.gerar_receita(
            ingredientes=req.ingredientes,
            tempo_minutos=req.tempo_minutos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cardapio/imagem", response_model=CardapioResponse)
async def gerar_cardapio_imagem(
    imagem: UploadFile = File(...),
    tempo_minutos: int = Form(30),
):
    """Gera cardapio a partir de foto de ingredientes."""
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    dest = upload_dir / imagem.filename
    dest.write_bytes(await imagem.read())

    try:
        return await _engine.gerar_cardapio(
            imagem_path=str(dest),
            tempo_minutos=tempo_minutos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        dest.unlink(missing_ok=True)


@app.get("/api/status")
async def status():
    return {
        "anthropic": settings.has_anthropic,
        "spoonacular": settings.has_spoonacular,
        "demo_mode": settings.demo_mode,
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
