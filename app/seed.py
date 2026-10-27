"""Cadastra (ou atualiza) os produtos da loja atual no banco.

Pode rodar quantas vezes quiser: se o produto já existe (mesmo slug), ele é
atualizado em vez de duplicado.

    docker compose exec api python -m app.seed
"""

from decimal import Decimal

from sqlmodel import Session, select

from app.database import criar_tabelas, engine
from app.models import Categoria, Imagem, Produto

# Fotos atuais, hospedadas na Nuvemshop. No painel da artista (Etapa 4), elas
# vão poder ser trocadas por fotos enviadas para o nosso servidor.
CDN = "https://dcdn-us.mitiendanube.com/stores/006/804/689/products/"

CATEGORIAS = [
    {"nome": "Decoração", "slug": "decoracao"},
]

PRODUTOS = [
    {
        "nome": "Porta-vela Butterfly",
        "slug": "porta-vela-butterfly",
        "preco": Decimal("69.90"),
        "estoque": 1,
        "categoria": "decoracao",
        "descricao": "",
        "fotos": [
            "prod-02-frente-743237ee3a292f54ac17930578526393-1024-1024.webp",
            "prod-02-lateral-d078a38c6f1e39ab2c17930578526645-1024-1024.webp",
            "prod-02-costas-57c9a1cdb5b153d75a17930578526544-1024-1024.webp",
        ],
    },
    {
        "nome": "Porta-vela Flor",
        "slug": "porta-vela-flor",
        "preco": Decimal("39.00"),
        "estoque": 1,
        "categoria": "decoracao",
        "descricao": "",
        "fotos": [
            "prod-03-frente-e68f30e29a3d24fe2b17930568908643-1024-1024.webp",
            "prod-03-frente-sem-vela-f2856894c9f8d39e7f17930568908531-1024-1024.webp",
            "prod-03-lateral-80cb60f6a0da5f6ac817930568908595-1024-1024.webp",
        ],
    },
    {
        "nome": "Porta-vela Amarelo",
        "slug": "porta-vela-amarelo",
        "preco": Decimal("49.90"),
        "estoque": 1,
        "cor": "Amarelo",
        "categoria": "decoracao",
        "descricao": "",
        "fotos": [
            "prod-01-lateral-18a871a10e5878ad4817930565189064-1024-1024.webp",
            "prod-01-frente-725f4781166ce3d33e17930558508929-1024-1024.webp",
            "prod-01-costas-3e5abfed6a3e32a73f17930558557125-1024-1024.webp",
        ],
    },
    {
        "nome": "Chaveiro Lovito",
        "slug": "chaveiro-lovito",
        "preco": Decimal("45.00"),
        "estoque": 0,
        "categoria": None,
        "descricao": (
            'Chaveiro Lovito. "love now, cry later"\n'
            "Cada peça do chaveiro é montada manualmente, com atenção e carinho.\n"
            "Duas opções de cores das bolinhas: verde ou branco."
        ),
        "fotos": [
            "chaveiro-lovito-fotos-4-16797fe9f86569af7d17634197733332-1024-1024.webp",
            "chaveiro-lovito-fotos-3-c0a894692e6c0a52b517634197731340-1024-1024.webp",
            "chaveiro-lovito-fotos-2-d7276692891e866e7817634197728554-1024-1024.webp",
            "chaveiro-lovito-fotos-1-47ae545396847d2f2417634197678281-1024-1024.webp",
        ],
    },
]


def buscar_ou_criar_categoria(session: Session, nome: str, slug: str) -> Categoria:
    categoria = session.exec(select(Categoria).where(Categoria.slug == slug)).first()
    if categoria is None:
        categoria = Categoria(nome=nome, slug=slug)
        session.add(categoria)
        session.commit()
        session.refresh(categoria)
    return categoria


def popular():
    with Session(engine) as session:
        categorias = {
            c["slug"]: buscar_ou_criar_categoria(session, c["nome"], c["slug"])
            for c in CATEGORIAS
        }

        for dados in PRODUTOS:
            produto = session.exec(
                select(Produto).where(Produto.slug == dados["slug"])
            ).first()
            if produto is None:
                produto = Produto(nome=dados["nome"], slug=dados["slug"],
                                  preco=dados["preco"])
                acao = "criado"
            else:
                acao = "atualizado"

            produto.nome = dados["nome"]
            produto.preco = dados["preco"]
            produto.estoque = dados["estoque"]
            produto.descricao = dados["descricao"]
            produto.cor = dados.get("cor")
            slug_categoria = dados["categoria"]
            produto.categoria_id = (
                categorias[slug_categoria].id if slug_categoria else None
            )
            fotos = [CDN + arquivo for arquivo in dados["fotos"]]
            produto.imagem = fotos[0] if fotos else None

            # Troca as fotos antigas pelas da lista
            for imagem in list(produto.imagens):
                session.delete(imagem)
            produto.imagens = [
                Imagem(url=url, ordem=posicao) for posicao, url in enumerate(fotos)
            ]

            session.add(produto)
            session.commit()
            print(f"{dados['nome']}: {acao}")


if __name__ == "__main__":
    criar_tabelas()
    popular()
