from fastapi import FastAPI

app = FastAPI(title="Kar.ma Loja")


@app.get("/")
def inicio ():
    return {"mensagem": "Ola! A API da Kar.ma esta no ar."}