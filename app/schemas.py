from pydantic import BaseModel
from typing import Optional, List

class AutorBase(BaseModel):
    nome: str

class AutorCreate(AutorBase):
    pass

class Autor(AutorBase):
    id: int

    class Config:
        orm_mode = True


class LivroBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    ano: Optional[int] = None
    autor_id: int

class LivroCreate(LivroBase):
    pass

class Livro(LivroBase):
    id: int
    autor: Autor

    class Config:
        orm_mode = True
