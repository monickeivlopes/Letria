from fastapi import FastAPI, Request
from . import models
from .database import engine
from .routers import livros, autores
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import auth
from app.models import Livro, Autor, Usuario
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import models
from .database import get_db
from app.routers.dependencies import get_usuario_logado

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catálogo de Livros com Resenhas",
    description="API para gerenciar livros, autores, resenhas e comentários.",
    version="0.1.0"
)

app.include_router(autores.router)
app.include_router(livros.router)
app.include_router(auth.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Liberar CORS para acesso via navegador local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar diretórios de arquivos estáticos e templates
app.mount("/static", StaticFiles(directory="static"), name="static")
router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Rotas para renderizar páginas HTML

@app.get("/")
def homepage(
    request: Request,
    busca_titulo: str = "",
    genero: str = "",
    autor_id: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(Livro)

    if busca_titulo:
        query = query.filter(Livro.titulo.ilike(f"%{busca_titulo}%"))

    if genero:
        query = query.filter(Livro.genero == genero)

    if autor_id:
        query = query.filter(Livro.autor_id == int(autor_id))

    livros = query.order_by(Livro.id.desc()).all()

    # lista distinta de gêneros e autores para os filtros
    generos = [row[0] for row in db.query(Livro.genero).distinct().all()]
    autores = db.query(Autor).all()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "livros": livros,
        "generos": generos,
        "autores": autores,
        "genero": genero,
        "autor_id": autor_id,
        "sucesso": False
    })

@app.get("/usuario", response_class=HTMLResponse)
def usuario(request: Request):
    return templates.TemplateResponse("cadastrar_usuario.html", {"request": request})

@app.get("/emprestimo", response_class=HTMLResponse)
def emprestimo(request: Request):
    return templates.TemplateResponse("emprestimo.html", {"request": request})




# Cadastro de novo usuário
@router.post("/registro")
def registrar_usuario(
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    senha_hash = bcrypt.hash(senha)
    novo_usuario = models.Usuario(nome=nome, email=email, senha_hash=senha_hash)
    db.add(novo_usuario)
    db.commit()

    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)


# Login
@router.post("/login")
def login_usuario(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario or not bcrypt.verify(senha, usuario.senha_hash):
        return templates.TemplateResponse("cadastrar_usuario.html", {
            "request": request,
            "mensagem": "Email ou senha incorretos"
        })

    response = RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
    response.set_cookie(key="usuario_id", value=str(usuario.id))
    return response


# Logout
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("usuario_id")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/usuario")

    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/cadastro_livro", response_class=HTMLResponse)
def cadastro_livro(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/usuario")

    autores = db.query(models.Autor).all()
    return templates.TemplateResponse("cadastro_livro.html", {"request": request, "autores": autores})

@app.get("/cadastrar_autor", response_class=HTMLResponse)
def cadastrar_autor(request: Request):
    return templates.TemplateResponse("cadastrar_autor.html", {"request": request})

@router.get("/livros")
def livros(request: Request, db: Session = Depends(get_db)):
    livros = db.query(Livro).all()
    return templates.TemplateResponse("livros.html", {
        "request": request,
        "livros": livros
    })

@router.post("/livros/{livro_id}/deletar")
def deletar_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado) 
):
    livro = db.query(Livro).filter(Livro.id == livro_id).first()

    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    db.delete(livro)
    db.commit()

    return RedirectResponse(url="/livros", status_code=HTTP_302_FOUND)