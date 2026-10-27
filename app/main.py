from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401 (registra as tabelas)
from app.database import criar_tabelas


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="Kar.ma Loja", lifespan=lifespan)


@app.get("/")
def inicio():
    return {"mensagem": "Olá! A API da Kar.ma está no ar."}