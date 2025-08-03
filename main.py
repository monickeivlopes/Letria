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
        return RedirectResponse(url="/dashboard_usuario", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse("dashboard.html", {"request": request, "usuario": usuario})

@app.get("/dashboard_usuario", response_class=HTMLResponse)
def dashboard_usuario(
    request: Request,
    usuario: Usuario = Depends(get_usuario_logado)
):
    return templates.TemplateResponse("dashboard_usuario.html", {
        "request": request,
        "usuario": usuario
    })



@app.get("/cadastro_livro", response_class=HTMLResponse)
def cadastro_livro(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado)
):
    if not usuario.is_admin:
        return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

    autores = db.query(models.Autor).all()
    return templates.TemplateResponse("cadastro_livro.html", {
        "request": request,
        "autores": autores,
        "usuario": usuario
    })



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

@app.get("/livros_usuario", response_class=HTMLResponse)
def livros_para_usuario(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado)
):
    livros = db.query(Livro).all()
    return templates.TemplateResponse("livros_usuario.html", {
        "request": request,
        "livros": livros,
        "usuario": usuario
    })

from fastapi import Body
from datetime import datetime

@app.get("/emprestimo", response_class=HTMLResponse)
def pagina_emprestimo(request: Request, usuario: Usuario = Depends(get_usuario_logado)):
    return templates.TemplateResponse("emprestimo.html", {"request": request, "usuario": usuario})


@app.get("/livros_usuario_json")
def livros_usuario_json(db: Session = Depends(get_db)):
    livros = db.query(models.Livro).filter(models.Livro.disponibilidade == True).all()
    return [{"id": l.id, "titulo": l.titulo} for l in livros]


@app.get("/emprestimos")
def listar_emprestimos(db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_logado)):
    emprestimos = db.query(models.Emprestimo).all()
    return [
        {
            "id": e.id,
            "usuario": {"id": e.usuario.id, "nome": e.usuario.nome},
            "livro": {"id": e.livro.id, "titulo": e.livro.titulo},
            "data_emprestimo": e.data_emprestimo,
            "data_devolucao": e.data_devolucao,
            "eh_do_usuario_logado": e.usuario_id == usuario.id
        }
        for e in emprestimos
    ]

#EMPRESTIMO ----------------------------------

@app.post("/emprestimo")
def criar_emprestimo(
    livro: int,
    data_emprestimo: str,
    data_devolucao: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado)
):
    livro_obj = db.query(models.Livro).filter(models.Livro.id == livro).first()
    if not livro_obj or not livro_obj.disponibilidade:
        raise HTTPException(status_code=400, detail="Livro não disponível")

    novo = models.Emprestimo(
        usuario_id=usuario.id,
        livro_id=livro,
        data_emprestimo=datetime.strptime(data_emprestimo, "%Y-%m-%d"),
        data_devolucao=datetime.strptime(data_devolucao, "%Y-%m-%d")
    )

    livro_obj.disponibilidade = False
    db.add(novo)
    db.commit()

    return "Empréstimo realizado com sucesso!"


@app.delete("/emprestimo/{emprestimo_id}")
def cancelar_emprestimo(emprestimo_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_logado)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    if emprestimo.usuario_id != usuario.id and not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado")

    livro = emprestimo.livro
    livro.disponibilidade = True
    db.delete(emprestimo)
    db.commit()
    return {"detail": "Empréstimo cancelado com sucesso"}


@app.put("/emprestimo/{emprestimo_id}")
def editar_emprestimo(emprestimo_id: int, payload: dict = Body(...), db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_logado)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    if emprestimo.usuario_id != usuario.id and not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado")

    nova_data = payload.get("nova_data_devolucao")
    if not nova_data:
        raise HTTPException(status_code=400, detail="Nova data inválida")

    emprestimo.data_devolucao = datetime.strptime(nova_data, "%Y-%m-%d")
    db.commit()
    return {"detail": "Data de devolução atualizada"}


app.include_router(router)