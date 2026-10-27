from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from sqlmodel import Field, Relationship, SQLModel


def agora():
    """Data e hora atual, com fuso horário (UTC)."""
    return datetime.now(timezone.utc)


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda para 2 casas, do jeito da escola: 66,405 -> 66,41."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    slug: str = Field(unique=True, index=True)

    produtos: list["Produto"] = Relationship(back_populates="categoria")


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
    imagem: str | None = None  # foto principal (aparece na vitrine)
    categoria_id: int | None = Field(default=None, foreign_key="categoria.id")
    criado_em: datetime = Field(default_factory=agora)

    # Relacionamentos: não são colunas, são "atalhos" para outras tabelas.
    # produto.categoria -> a Categoria deste produto
    # produto.imagens   -> lista de fotos, na ordem certa
    categoria: Categoria | None = Relationship(back_populates="produtos")
    imagens: list["Imagem"] = Relationship(
        back_populates="produto",
        sa_relationship_kwargs={"order_by": "Imagem.ordem"},
    )

    # ----- Valores calculados (não ficam guardados no banco) -----

    @property
    def preco_pix(self) -> Decimal:
        """5% de desconto pagando com Pix."""
        return arredondar(self.preco * Decimal("0.95"))

    @property
    def parcela_2x(self) -> Decimal:
        """Valor de cada parcela em 2x sem juros."""
        return arredondar(self.preco / 2)

    @property
    def esgotado(self) -> bool:
        return self.estoque <= 0

    @property
    def ultima_peca(self) -> bool:
        return self.estoque == 1


class Imagem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    produto_id: int = Field(foreign_key="produto.id", index=True)
    url: str
    ordem: int = 0

    produto: Produto | None = Relationship(back_populates="imagens")


class Mensagem(SQLModel, table=True):
    """Mensagens enviadas pelo formulário de contato."""

    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str
    telefone: str = ""
    texto: str
    lida: bool = False
    criado_em: datetime = Field(default_factory=agora)
