from sqlalchemy.orm import Session
from app.models.users import UserDB
from app.models.leads import LeadsDB
from app.models.proposals import ProposalDB
from app.models.activities import ActivityDB
from app.models.companies import CompanyDB
from app.models.users import Roles
from app.core.security import hash_password
from app.db.database import SessionLocal

def criar_usuario_admin():
    # Inicia a sessão com o banco de dados
    db: Session = SessionLocal()
    
    try:
        # Verifica se o admin já existe para evitar erros de duplicidade
        admin_existente = db.query(UserDB).filter(UserDB.username == "admin").first()
        if admin_existente:
            print("O usuário administrador já existe no banco de dados!")
            return

        # Cria a instância do novo usuário
        novo_admin = UserDB(
            username="admin",
            hashed_password=hash_password("admin123"),
            role=Roles.ADMIN, # Use o nome exato da coluna que define o admin no seu modelo
            is_active=True
        )
        
        # Adiciona e salva no banco
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