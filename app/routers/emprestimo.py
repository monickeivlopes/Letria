from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..models import Usuario, Livro, Emprestimo
from app.routers.dependencies import get_usuario_logado




router = APIRouter(
    prefix="/emprestimo",
    tags=["Emprestimo"]
)

@router.post("/emprestimo")
def criar_emprestimo(
    livro: int,
    data_emprestimo: str,
    data_devolucao: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado)
):
    # Verifica se o livro existe e está disponível
    livro_obj = db.query(Livro).filter_by(id=livro, disponibilidade=True).first()
    if not livro_obj:
        return "Livro indisponível ou não encontrado."

    novo_emprestimo = Emprestimo(
        usuario_id=usuario.id,
        livro_id=livro,
        data_emprestimo=datetime.fromisoformat(data_emprestimo),
        data_devolucao=datetime.fromisoformat(data_devolucao)
    )

    livro_obj.disponibilidade = False  # marca como indisponível
    db.add(novo_emprestimo)
    db.commit()
    db.refresh(novo_emprestimo)
    return "Empréstimo registrado com sucesso!"

@router.get("/emprestimos")
def listar_emprestimos(db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_usuario_logado)):
    emprestimos = db.query(Emprestimo).all()
    resultado = []
    for e in emprestimos:
        resultado.append({
            "id": e.id,
            "livro": {"titulo": e.livro.titulo},
            "usuario": {"nome": e.usuario.nome},
            "data_devolucao": e.data_devolucao.isoformat(),
            "eh_do_usuario_logado": e.usuario.id == usuario_logado.id
        })
    return resultado
