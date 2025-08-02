from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)

    emprestimos = relationship("Emprestimo", back_populates="usuario")


class Autor(Base):
    __tablename__ = "autores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    biografia = Column(Text)

    livros = relationship("Livro", back_populates="autor")

class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    ano_publicacao = Column(Integer)
    genero = Column(String)
    capa_url = Column(String)
    autor_id = Column(Integer, ForeignKey("autores.id"))
    disponibilidade = Column(Boolean, default=True)  

    autor = relationship("Autor", back_populates="livros")
    emprestimos = relationship("Emprestimo", back_populates="livro")


class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    livro_id = Column(Integer, ForeignKey("livros.id"))
    data_emprestimo = Column(DateTime, default=datetime.utcnow)
    data_devolucao = Column(DateTime)
    devolvido = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="emprestimos")
    livro = relationship("Livro", back_populates="emprestimos")


