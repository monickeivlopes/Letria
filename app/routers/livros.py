from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import Livro
from fastapi.responses import RedirectResponse
from .. import crud, models, schemas
from ..database import get_db
from starlette.status import HTTP_302_FOUND


router = APIRouter(
    prefix="/livros",
    tags=["Livros"]
)

@router.post("/", response_model=schemas.Livro)
def criar_livro(livro: schemas.LivroCreate, db: Session = Depends(get_db)):
    return crud.criar_livro(db=db, livro=livro)

@router.get("/", response_model=List[schemas.Livro])
def listar_livros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.listar_livros(db, skip=skip, limit=limit)

@router.get("/{livro_id}", response_model=schemas.Livro)
def obter_livro(livro_id: int, db: Session = Depends(get_db)):
    db_livro = crud.obter_livro(db, livro_id=livro_id)
    if db_livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return db_livro

@router.post("/livros/{livro_id}/deletar")
def deletar_livro(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(Livro).filter(Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db.delete(livro)
    db.commit()
    
    return RedirectResponse(url="/livros", status_code=HTTP_302_FOUND)
