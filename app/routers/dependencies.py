from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario

def get_usuario_logado(request: Request, db: Session = Depends(get_db)) -> Usuario:
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return usuario
