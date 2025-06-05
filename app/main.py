from fastapi import FastAPI
from . import models
from .database import engine
from .routers import livros, autores

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catálogo de Livros com Resenhas",
    description="API para gerenciar livros, autores, resenhas e comentários.",
    version="0.1.0"
)

app.include_router(autores.router)
app.include_router(livros.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Catálogo de Livros 📚"}
