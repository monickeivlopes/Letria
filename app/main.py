from fastapi import FastAPI, Request
from . import models
from .database import engine
from .routers import livros, autores
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catálogo de Livros com Resenhas",
    description="API para gerenciar livros, autores, resenhas e comentários.",
    version="0.1.0"
)

app.include_router(autores.router)
app.include_router(livros.router)


# Liberar CORS para acesso via navegador local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar diretórios de arquivos estáticos e templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Rotas para renderizar páginas HTML

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/listar", response_class=HTMLResponse)
def listar(request: Request):
    return templates.TemplateResponse("listar_livros.html", {"request": request})

@app.get("/cadastrar", response_class=HTMLResponse)
def cadastrar(request: Request):
    return templates.TemplateResponse("cadastrar_livro.html", {"request": request})

@app.get("/buscar", response_class=HTMLResponse)
def buscar(request: Request):
    return templates.TemplateResponse("buscar_livro.html", {"request": request})

