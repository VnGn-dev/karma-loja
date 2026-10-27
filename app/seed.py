from decimal import Decimal

from sqlmodel import Session, select

from app.database import criar_tabelas, engine
from app.models import Categoria, Produto


def popular():
    with Session(engine) as session:
        # Se já tiver produto no banco, não cadastra de novo
        if session.exec(select(Produto)).first():
            print("Já existem produtos. Nada a fazer.")
            return

        decoracao = Categoria(nome="Decoração", slug="decoracao")
        session.add(decoracao)
        session.commit()
        session.refresh(decoracao)

        produtos = [
            Produto(nome="Porta-vela Butterfly", slug="porta-vela-butterfly",
                    preco=Decimal("69.90"), estoque=5, categoria_id=decoracao.id),
            Produto(nome="Porta-vela Flor", slug="porta-vela-flor",
                    preco=Decimal("39.00"), estoque=5, categoria_id=decoracao.id),
            Produto(nome="Porta-vela Amarelo", slug="porta-vela-amarelo",
                    preco=Decimal("49.90"), estoque=5, cor="Amarelo",
                    categoria_id=decoracao.id),
            Produto(nome="Chaveiro Lovito", slug="chaveiro-lovito",
                    preco=Decimal("45.00"), estoque=0),
        ]
        session.add_all(produtos)
        session.commit()
        print(f"{len(produtos)} produtos cadastrados!")


if __name__ == "__main__":
    criar_tabelas()
    popular()