from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from app.database import criar_tabelas, get_session
from app.models import Produto


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="Kar.ma Loja", lifespan=lifespan)


@app.get("/")
def inicio():
    return {"mensagem": "Olá! A API da Kar.ma está no ar."}


@app.get("/api/produtos")
def listar_produtos(session: Session = Depends(get_session)):
    consulta = select(Produto).where(Produto.ativo)
    return session.exec(consulta).all()


@app.get("/api/produtos/{slug}")
def ver_produto(slug: str, session: Session = Depends(get_session)):
    consulta = select(Produto).where(Produto.slug == slug)
    produto = session.exec(consulta).first()
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto