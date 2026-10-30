import getpass
import os
import sys

from sqlalchemy.orm import Session

from app.models.users import UserDB
from app.models.users import Roles
from app.core.security import hash_password
from app.db.database import SessionLocal

TAMANHO_MINIMO_SENHA = 12

def _obter_credenciais() -> tuple[str, str]:
    """Le ADMIN_USERNAME/ADMIN_PASSWORD do ambiente ou pede via getpass."""
    username = os.environ.get("ADMIN_USERNAME") or input("Username do admin: ").strip()
    password = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Senha do admin: ")

    if not username:
        print("Erro: username nao informado.")
        sys.exit(1)

    if len(password) < TAMANHO_MINIMO_SENHA:
        print(f"Erro: a senha deve ter no minimo {TAMANHO_MINIMO_SENHA} caracteres.")
        sys.exit(1)

    return username, password

def criar_usuario_admin() -> None:
    username, password = _obter_credenciais()

    db: Session = SessionLocal()

    try:

        admin_existente = db.query(UserDB).filter(UserDB.username == username).first()
        if admin_existente:
            print("O usuário administrador já existe no banco de dados!")
            return

        novo_admin = UserDB(
            username=username,
            hashed_password=hash_password(password),
            role=Roles.ADMIN,
            is_active=True
        )

        db.add(novo_admin)
        db.commit()
        db.refresh(novo_admin)
        print(f"Usuário administrador criado com sucesso! ID: {novo_admin.id}")

    except Exception as e:
        db.rollback()
        print(f"Ocorreu um erro ao criar o usuário: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando a criação do admin...")
    criar_usuario_admin()