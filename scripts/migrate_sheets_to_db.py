"""
Script para migrar colaboradores do Google Sheets para PostgreSQL.

Uso:
    python scripts/migrate_sheets_to_db.py
"""

import os
import csv
import requests
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Base, User


def get_collaborators_from_sheets():
    """Fetch colaboradores from Google Sheets CSV export."""
    
    sheets_url = "https://docs.google.com/spreadsheets/d/1UOo3kKlNCdNJwIVJqMDlnJdtxGLjlGmi9vuctU44324/export?format=csv"
    
    print(f"📥 Baixando dados do Google Sheets...")
    
    try:
        response = requests.get(sheets_url)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        reader = csv.DictReader(lines)
        
        collaborators = []
        for row in reader:
            # Esperado: Nome, Telefone (ou columns similares)
            name = row.get('Nome') or row.get('name') or ''
            phone = row.get('Telefone') or row.get('phone') or row.get('celular') or ''
            
            if name and phone:
                # Normaliza telefone
                phone = phone.strip().replace(' ', '').replace('-', '').replace('+', '')
                if not phone.startswith('55'):
                    phone = '55' + phone
                
                collaborators.append({
                    'name': name.strip(),
                    'phone_number': phone
                })
        
        print(f"✅ {len(collaborators)} colaboradores encontrados")
        return collaborators
    
    except Exception as e:
        print(f"❌ Erro ao baixar Google Sheets: {e}")
        return []


def migrate_to_database(collaborators):
    """Migrate colaboradores to PostgreSQL."""
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL não configurada")
        return False
    
    print(f"🔗 Conectando ao banco de dados...")
    
    try:
        # Create engine and session
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/atualizadas")
        
        # Migrate data
        session = SessionLocal()
        
        try:
            # Clear existing users (opcional - descomente se quiser limpar)
            # session.query(User).delete()
            # session.commit()
            
            added = 0
            updated = 0
            
            for collab in collaborators:
                # Check if user already exists
                existing = session.query(User).filter(
                    User.phone_number == collab['phone_number']
                ).first()
                
                if existing:
                    existing.name = collab['name']
                    updated += 1
                    print(f"  ♻️  Atualizado: {collab['name']} ({collab['phone_number']})")
                else:
                    user = User(
                        phone_number=collab['phone_number'],
                        name=collab['name'],
                        is_active=True
                    )
                    session.add(user)
                    added += 1
                    print(f"  ➕ Adicionado: {collab['name']} ({collab['phone_number']})")
            
            session.commit()
            session.close()
            
            print(f"\n✅ Migração concluída!")
            print(f"   ➕ Novos: {added}")
            print(f"   ♻️  Atualizados: {updated}")
            
            return True
        
        except Exception as e:
            session.rollback()
            session.close()
            print(f"❌ Erro ao migrar: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("🔄 Migração: Google Sheets → PostgreSQL")
    print("=" * 60 + "\n")
    
    # Get colaboradores from sheets
    collaborators = get_collaborators_from_sheets()
    
    if not collaborators:
        print("⚠️  Nenhum colaborador encontrado")
        return False
    
    # Migrate to database
    success = migrate_to_database(collaborators)
    
    if success:
        print("\n✅ Migração bem-sucedida!")
        return True
    else:
        print("\n❌ Falha na migração")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
