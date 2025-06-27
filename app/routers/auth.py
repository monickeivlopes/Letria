from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from .. import models
from ..database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .. import models
from ..database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")



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
