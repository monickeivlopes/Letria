from sqlalchemy.orm import Session
from . import models, schemas


# AUTOR 
def criar_autor(db: Session, autor: schemas.AutorCreate):
    db_autor = models.Autor(nome=autor.nome)
    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

def listar_autores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Autor).offset(skip).limit(limit).all()

def obter_autor(db: Session, autor_id: int):
    return db.query(models.Autor).filter(models.Autor.id == autor_id).first()


#LIVRO
def criar_livro(db: Session, livro: schemas.LivroCreate):
    db_livro = models.Livro(**livro.dict())
    db.add(db_livro)
    db.commit()
    db.refresh(db_livro)
    return db_livro

def listar_livros(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Livro).offset(skip).limit(limit).all()

def obter_livro(db: Session, livro_id: int):
    return db.query(models.Livro).filter(models.Livro.id == livro_id).first()
