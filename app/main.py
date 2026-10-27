from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import criar_tabelas, get_session
from app.models import Produto


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="Kar.ma Loja", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


def formatar_brl(valor: Decimal) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


templates.env.filters["brl"] = formatar_brl


# ---------- Páginas ----------

@app.get("/")
def pagina_inicio(request: Request, session: Session = Depends(get_session)):
    produtos = session.exec(select(Produto).where(Produto.ativo)).all()
    return templates.TemplateResponse(request, "inicio.html", {"produtos": produtos})


# ---------- API ----------

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