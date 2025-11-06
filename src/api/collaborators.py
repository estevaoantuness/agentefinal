"""API endpoints para gerenciar colaboradores."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from src.database.session import get_db
from src.database.models import User


# Pydantic models
class CollaboratorBase(BaseModel):
    phone_number: str
    name: str


class CollaboratorCreate(CollaboratorBase):
    pass


class CollaboratorUpdate(BaseModel):
    name: str = None
    is_active: bool = None


class CollaboratorResponse(CollaboratorBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True


# Router
router = APIRouter(prefix="/api/collaborators", tags=["collaborators"])


@router.get("", response_model=List[CollaboratorResponse])
async def list_collaborators(db: Session = Depends(get_db)):
    """Lista todos os colaboradores."""
    users = db.query(User).all()
    return users


@router.get("/{phone_number}", response_model=CollaboratorResponse)
async def get_collaborator(phone_number: str, db: Session = Depends(get_db)):
    """Obtém um colaborador pelo telefone."""
    user = db.query(User).filter(User.phone_number == phone_number).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    
    return user


@router.post("", response_model=CollaboratorResponse)
async def create_collaborator(collab: CollaboratorCreate, db: Session = Depends(get_db)):
    """Cria um novo colaborador."""
    
    # Check if already exists
    existing = db.query(User).filter(User.phone_number == collab.phone_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Colaborador já existe")
    
    # Create new user
    db_user = User(
        phone_number=collab.phone_number,
        name=collab.name,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.put("/{phone_number}", response_model=CollaboratorResponse)
async def update_collaborator(
    phone_number: str,
    collab: CollaboratorUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um colaborador."""
    
    user = db.query(User).filter(User.phone_number == phone_number).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    
    if collab.name is not None:
        user.name = collab.name
    
    if collab.is_active is not None:
        user.is_active = collab.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{phone_number}")
async def delete_collaborator(phone_number: str, db: Session = Depends(get_db)):
    """Deleta um colaborador (desativa na verdade)."""
    
    user = db.query(User).filter(User.phone_number == phone_number).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    
    # Soft delete - marca como inativo
    user.is_active = False
    db.commit()
    
    return {"message": "Colaborador desativado com sucesso"}


@router.post("/sync/sheets")
async def sync_from_sheets(db: Session = Depends(get_db)):
    """Sincroniza colaboradores do Google Sheets com o banco."""
    
    import csv
    import requests
    
    sheets_url = "https://docs.google.com/spreadsheets/d/1UOo3kKlNCdNJwIVJqMDlnJdtxGLjlGmi9vuctU44324/export?format=csv"
    
    try:
        response = requests.get(sheets_url)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        reader = csv.DictReader(lines)
        
        synced = 0
        for row in reader:
            name = row.get('Nome') or row.get('name') or ''
            phone = row.get('Telefone') or row.get('phone') or row.get('celular') or ''
            
            if name and phone:
                phone = phone.strip().replace(' ', '').replace('-', '').replace('+', '')
                if not phone.startswith('55'):
                    phone = '55' + phone
                
                existing = db.query(User).filter(User.phone_number == phone).first()
                if existing:
                    existing.name = name.strip()
                else:
                    db_user = User(phone_number=phone, name=name.strip(), is_active=True)
                    db.add(db_user)
                
                synced += 1
        
        db.commit()
        return {"synced": synced, "message": "Sincronização concluída"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar: {str(e)}")
