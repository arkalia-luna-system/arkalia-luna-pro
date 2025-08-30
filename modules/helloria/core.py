"""
Module core.

Ce module fait partie du système Arkalia Luna Pro.
"""

# modules/helloria/core.py

import os
import sys

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

# === ZeroIA router désactivé (module core n'existe pas) ===
zeroia_router = None

router = APIRouter()


@router.get("/", tags=["Root"])
async def root():
    return {"message": "Arkalia-LUNA API active"}


@router.get("/status", tags=["Status"])
async def status():
    return {"status": "Helloria est opérationnel"}


app = FastAPI()
app.include_router(router)

# === Inclusion du routeur ZeroIA ===
if zeroia_router is not None:
    app.include_router(zeroia_router, prefix="/zeroia")


@app.post("/echo", tags=["Test"])
async def echo(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()

        if not message:
            return JSONResponse(status_code=400, content={"error": "Message vide."})

        return {"echo": message}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur : {str(e)}"})
