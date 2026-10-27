from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Field, SQLModel


class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    slug: str = Field(unique=True, index=True)


class Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    slug: str = Field(unique=True, index=True)
    descricao: str = ""
    preco: Decimal = Field(max_digits=10, decimal_places=2)
    estoque: int = 0
    ativo: bool = True
    cor: str | None = None
    frete_gratis: bool = True
    imagem: str | None = None
    categoria_id: int | None = Field(default=None, foreign_key="categoria.id")
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))