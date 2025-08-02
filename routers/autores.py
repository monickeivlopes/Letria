from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/autores",
    tags=["Autores"]
)

@router.post("/", response_model=schemas.Autor)
def criar_autor(autor: schemas.AutorCreate, db: Session = Depends(get_db)):
    return crud.criar_autor(db=db, autor=autor)

@router.get("/", response_model=List[schemas.Autor])
def listar_autores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.listar_autores(db, skip=skip, limit=limit)

@router.get("/{autor_id}", response_model=schemas.Autor)
def obter_autor(autor_id: int, db: Session = Depends(get_db)):
    db_autor = crud.obter_autor(db, autor_id=autor_id)
    if db_autor is None:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return db_autor
