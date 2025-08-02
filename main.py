from fastapi import FastAPI, Request, Form, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from fastapi.middleware.cors import CORSMiddleware

from database import engine, get_db
from models import Livro, Autor, Usuario
from routers import livros, autores, auth
from routers.dependencies import get_usuario_logado

from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import models


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")
router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Rotas 

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

    return RedirectResponse(url="/usuario?sucesso=true", status_code=HTTP_302_FOUND)


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
def dashboard(request: Request, usuario: Usuario = Depends(get_usuario_logado)):
    if not usuario.is_admin:
        return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse("dashboard.html", {"request": request, "usuario": usuario})


@app.get("/cadastro_livro", response_class=HTMLResponse)
def cadastro_livro(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado)
):
    if not usuario.is_admin:
        return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

    autores = db.query(models.Autor).all()
    return templates.TemplateResponse("cadastro_livro.html", {"request": request, "autores": autores})


@app.get("/cadastrar_autor", response_class=HTMLResponse)
def cadastrar_autor(
    request: Request,
    usuario: Usuario = Depends(get_usuario_logado)
):
    if not usuario.is_admin:
        return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse("cadastrar_autor.html", {"request": request})


@router.get("/livros")
def livros(request: Request, db: Session = Depends(get_db)):
    livros = db.query(Livro).all()
    return templates.TemplateResponse("livros.html", {
        "request": request,
        "livros": livros
    })


from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

@router.post("/livros/{livro_id}/deletar")
def deletar_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado")

    livro = db.query(Livro).filter(Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    db.delete(livro)
    db.commit()

    return RedirectResponse(url="/livros?sucesso=true", status_code=HTTP_302_FOUND)


app.include_router(router)