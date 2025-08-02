from database import engine, SessionLocal
from models import Usuario
from passlib.hash import bcrypt

db = SessionLocal()

admin = Usuario(
    nome="Administrador",
    email="admin@letria.com",
    senha_hash=bcrypt.hash("admin123"),
    is_admin=True
)

db.add(admin)
db.commit()
db.close()

print("Administrador criado com sucesso.")
