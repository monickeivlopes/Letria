from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)

    resenhas = relationship("Resenha", back_populates="usuario")
    comentarios = relationship("Comentario", back_populates="usuario")


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

    autor = relationship("Autor", back_populates="livros")
    resenhas = relationship("Resenha", back_populates="livro")


class Resenha(Base):
    __tablename__ = "resenhas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    livro_id = Column(Integer, ForeignKey("livros.id"))
    titulo_resenha = Column(String, nullable=False)
    conteudo_resenha = Column(Text)
    avaliacao = Column(Integer)
    data_publicacao = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="resenhas")
    livro = relationship("Livro", back_populates="resenhas")
    comentarios = relationship("Comentario", back_populates="resenha")


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    resenha_id = Column(Integer, ForeignKey("resenhas.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    conteudo_comentario = Column(Text)
    data_comentario = Column(DateTime, default=datetime.utcnow)

    resenha = relationship("Resenha", back_populates="comentarios")
    usuario = relationship("Usuario", back_populates="comentarios")
