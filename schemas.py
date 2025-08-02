from pydantic import BaseModel
from typing import Optional

class AutorBase(BaseModel):
    nome: str

class AutorCreate(AutorBase):
    pass

class Autor(AutorBase):
    id: int

    class Config:
        from_attributes = True  


class LivroBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    ano_publicacao: Optional[int] = None
    genero: Optional[str] = None
    capa_url: Optional[str] = None
    autor_id: int
    disponibilidade: bool = True

class LivroCreate(LivroBase):
    pass

class Livro(LivroBase):
    id: int
    autor: Autor

    class Config:
        from_attributes = True  # Atualizado para Pydantic v2
