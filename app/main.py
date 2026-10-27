from contextlib import asynccontextmanager
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import BANNERS, CARROSSEL, DESCONTO_PIX, LOJA, PEDIDO_MINIMO
from app.database import criar_tabelas, engine, get_session
from app.models import Assinante, Categoria, Mensagem, Produto


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="Kar.ma Loja", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


# ---------- Filtros usados nos modelos HTML ----------

def formatar_brl(valor: Decimal) -> str:
    """49.9 -> 'R$49,90' (padrão brasileiro, escrito igual à loja atual)."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R${texto}"


templates.env.filters["brl"] = formatar_brl


# ---------- Ajudantes ----------

def pagina(request: Request, modelo: str, status_code: int = 200, **contexto):
    """Monta uma página com as informações que TODAS as páginas usam
    (dados da loja e categorias do menu) mais as que a página passar."""
    with Session(engine) as session:
        categorias = session.exec(select(Categoria).order_by(Categoria.nome)).all()
    contexto_completo = {
        "loja": LOJA,
        "categorias_menu": categorias,
        "pedido_minimo": PEDIDO_MINIMO,
        "desconto_pix": DESCONTO_PIX,
        **contexto,
    }
    return templates.TemplateResponse(
        request, modelo, contexto_completo, status_code=status_code
    )


def para_decimal(texto: str | None) -> Decimal | None:
    """Converte '45,90' ou '45.90' em Decimal. Texto vazio ou inválido -> None."""
    if not texto:
        return None
    try:
        return Decimal(texto.replace(",", "."))
    except InvalidOperation:
        return None


# Opções de ordenação: nome no endereço -> (texto no menu, regra de ordem)
ORDENACOES = {
    "novos": ("Mais novos", Produto.criado_em.desc()),
    "antigos": ("Mais antigos", Produto.criado_em.asc()),
    "menor-preco": ("Menor preço", Produto.preco.asc()),
    "maior-preco": ("Maior preço", Produto.preco.desc()),
    "a-z": ("A - Z", Produto.nome.asc()),
    "z-a": ("Z - A", Produto.nome.desc()),
}


# ---------- Páginas ----------

@app.get("/")
def pagina_inicio(request: Request, session: Session = Depends(get_session)):
    # Na vitrine da página inicial aparecem só os produtos com estoque
    consulta = (
        select(Produto)
        .where(Produto.ativo, Produto.estoque > 0)
        .order_by(Produto.criado_em.desc())
    )
    produtos = session.exec(consulta).all()
    return pagina(request, "inicio.html", produtos=produtos,
                  carrossel=CARROSSEL, banners=BANNERS)


@app.get("/produtos")
def pagina_produtos(
    request: Request,
    cor: str | None = None,
    preco_min: str | None = None,
    preco_max: str | None = None,
    ordem: str = "novos",
    busca: str | None = None,
    session: Session = Depends(get_session),
):
    titulo = f'Resultados para "{busca}"' if busca else "Produtos"
    return listar(request, session, titulo=titulo, cor=cor,
                  preco_min=preco_min, preco_max=preco_max, ordem=ordem,
                  busca=busca)


@app.get("/categoria/{slug}")
def pagina_categoria(
    request: Request,
    slug: str,
    cor: str | None = None,
    preco_min: str | None = None,
    preco_max: str | None = None,
    ordem: str = "novos",
    session: Session = Depends(get_session),
):
    categoria = session.exec(select(Categoria).where(Categoria.slug == slug)).first()
    if categoria is None:
        raise HTTPException(status_code=404)
    return listar(request, session, titulo=categoria.nome, categoria=categoria,
                  cor=cor, preco_min=preco_min, preco_max=preco_max, ordem=ordem)


def listar(request, session, titulo, cor, preco_min, preco_max, ordem,
           categoria=None, busca=None):
    """Lista de produtos com filtros. Usada por /produtos e /categoria/..."""
    consulta = select(Produto).where(Produto.ativo)
    if categoria:
        consulta = consulta.where(Produto.categoria_id == categoria.id)
    if busca:
        # ilike = "contém", sem diferenciar maiúsculas de minúsculas
        consulta = consulta.where(Produto.nome.ilike(f"%{busca.strip()}%"))

    # Cores disponíveis para o filtro (antes de filtrar por cor)
    cores = sorted({p.cor for p in session.exec(consulta).all() if p.cor})

    if cor:
        consulta = consulta.where(Produto.cor == cor)
    minimo = para_decimal(preco_min)
    maximo = para_decimal(preco_max)
    if minimo is not None:
        consulta = consulta.where(Produto.preco >= minimo)
    if maximo is not None:
        consulta = consulta.where(Produto.preco <= maximo)

    if ordem not in ORDENACOES:
        ordem = "novos"
    # Esgotados sempre por último; depois, a ordem escolhida
    consulta = consulta.order_by(Produto.estoque == 0, ORDENACOES[ordem][1])

    return pagina(
        request,
        "produtos.html",
        titulo=titulo,
        categoria=categoria,
        produtos=session.exec(consulta).all(),
        cores=cores,
        filtro={"cor": cor or "", "preco_min": preco_min or "",
                "preco_max": preco_max or "", "ordem": ordem,
                "busca": busca or ""},
        ordenacoes={chave: texto for chave, (texto, _) in ORDENACOES.items()},
    )


@app.get("/produtos/{slug}")
def pagina_produto(request: Request, slug: str,
                   session: Session = Depends(get_session)):
    produto = session.exec(
        select(Produto).where(Produto.slug == slug, Produto.ativo)
    ).first()
    if produto is None:
        raise HTTPException(status_code=404)

    relacionados = session.exec(
        select(Produto)
        .where(Produto.ativo, Produto.id != produto.id)
        .order_by(Produto.estoque == 0, Produto.criado_em.desc())
        .limit(4)
    ).all()
    return pagina(request, "produto.html", produto=produto,
                  relacionados=relacionados)


@app.get("/sobre")
def pagina_sobre(request: Request):
    return pagina(request, "sobre.html")


@app.get("/carrinho")
def pagina_carrinho(request: Request):
    return pagina(request, "carrinho.html")


@app.get("/contato")
def pagina_contato(request: Request, enviado: bool = False):
    return pagina(request, "contato.html", enviado=enviado, erro=None, dados={})


@app.post("/contato")
def enviar_contato(
    request: Request,
    nome: str = Form(""),
    email: str = Form(""),
    telefone: str = Form(""),
    mensagem: str = Form(""),
    site: str = Form(""),  # campo escondido "armadilha" para robôs de spam
    session: Session = Depends(get_session),
):
    # Pessoas não veem o campo "site"; robôs preenchem tudo. Se veio
    # preenchido, fingimos que deu certo e não salvamos nada.
    if site:
        return RedirectResponse("/contato?enviado=true", status_code=303)

    dados = {"nome": nome, "email": email, "telefone": telefone,
             "mensagem": mensagem}
    if not nome.strip() or not email.strip() or not mensagem.strip():
        return pagina(request, "contato.html", status_code=400, enviado=False,
                      erro="Preencha nome, e-mail e mensagem.", dados=dados)

    session.add(Mensagem(nome=nome.strip(), email=email.strip(),
                         telefone=telefone.strip(), texto=mensagem.strip()))
    session.commit()
    # Redireciona depois de salvar (assim, apertar F5 não envia de novo)
    return RedirectResponse("/contato?enviado=true", status_code=303)


@app.post("/newsletter")
def assinar_newsletter(request: Request, email: str = Form(""),
                       session: Session = Depends(get_session)):
    email = email.strip().lower()
    # Volta para a página onde a pessoa estava. Usa só o "caminho" (/produtos,
    # por exemplo), nunca um endereço de outro site.
    voltar = urlparse(request.headers.get("referer") or "").path or "/"
    if "@" not in email:
        return RedirectResponse(f"{voltar}?newsletter=erro", status_code=303)
    ja_existe = session.exec(select(Assinante).where(Assinante.email == email)).first()
    if not ja_existe:
        session.add(Assinante(email=email))
        session.commit()
    return RedirectResponse(f"{voltar}?newsletter=ok", status_code=303)


# ---------- API (JSON) ----------

@app.get("/api/produtos")
def api_listar_produtos(session: Session = Depends(get_session)):
    consulta = select(Produto).where(Produto.ativo)
    return session.exec(consulta).all()


@app.get("/api/produtos/{slug}")
def api_ver_produto(slug: str, session: Session = Depends(get_session)):
    consulta = select(Produto).where(Produto.slug == slug)
    produto = session.exec(consulta).first()
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


# ---------- Página de erro 404 ----------

@app.exception_handler(StarletteHTTPException)
async def tratar_erro_http(request: Request, erro: StarletteHTTPException):
    # Na API, o erro continua em JSON. Nas páginas, mostra uma página bonita.
    if request.url.path.startswith("/api") or erro.status_code != 404:
        return JSONResponse({"detail": erro.detail}, status_code=erro.status_code)
    return pagina(request, "404.html", status_code=404)
