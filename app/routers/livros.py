from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db

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
