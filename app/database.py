import os

from sqlmodel import Session, SQLModel, create_engine

USUARIO = os.environ["POSTGRES_USER"]
SENHA = os.environ["POSTGRES_PASSWORD"]
BANCO = os.environ["POSTGRES_DB"]

DATABASE_URL = f"postgresql+psycopg://{USUARIO}:{SENHA}@db:5432/{BANCO}"

engine = create_engine(DATABASE_URL)


def criar_tabelas():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session